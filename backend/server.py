from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import io
import re
import zipfile
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

import yaml


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Directory that holds the generated DevOps deliverables
DELIVERABLES_DIR = Path(
    os.environ.get('DELIVERABLES_DIR', str(ROOT_DIR.parent / 'deliverables'))
).resolve()

# Ordered, whitelisted catalogue of files we surface in the dashboard.
FILE_CATALOG = [
    {
        "name": "docker-compose.yml",
        "language": "yaml",
        "title": "Compose Stack",
        "description": "The two-service stack (OpenHands + Headroom) with the socket-permission and DinD fixes baked in.",
        "primary": True,
    },
    {
        "name": ".env.example",
        "language": "bash",
        "title": "Environment Template",
        "description": "All environment variables for both services. Copy to .env; init.sh fills host-specific values.",
        "primary": False,
    },
    {
        "name": "init.sh",
        "language": "bash",
        "title": "Host Bootstrap Script",
        "description": "Idempotent setup: creates ./workspace, detects the docker GID, writes absolute host paths into .env.",
        "primary": False,
    },
    {
        "name": "README.md",
        "language": "markdown",
        "title": "Documentation",
        "description": "Quick start, port map, the two critical fixes explained, and troubleshooting.",
        "primary": False,
    },
    {
        "name": ".gitignore",
        "language": "bash",
        "title": "Git Ignore",
        "description": "Keeps secrets (.env) and the local workspace out of version control.",
        "primary": False,
    },
    {
        "name": "validate_stack.py",
        "language": "python",
        "title": "Static Validator",
        "description": "Docker-free validation of the compose invariants and both reliability fixes.",
        "primary": False,
    },
]
CATALOG_BY_NAME = {f["name"]: f for f in FILE_CATALOG}

# Create the main app without a prefix
app = FastAPI(title="AI Stack Console")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ----------------------------- Models -----------------------------
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


# ----------------------------- Helpers -----------------------------
def _read_file(name: str) -> str:
    if name not in CATALOG_BY_NAME:
        raise HTTPException(status_code=404, detail=f"Unknown file: {name}")
    path = DELIVERABLES_DIR / name
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found on disk: {name}")
    return path.read_text(encoding="utf-8")


def _parse_ports(port_val):
    """Return (host_port, container_port) resolving ${VAR:-default} host specs."""
    p = str(port_val).strip().strip('"')
    if ":" not in p:
        return None, None
    host_spec, cont = p.rsplit(":", 1)
    m = re.search(r":-(\d+)", host_spec)
    if m:
        host = int(m.group(1))
    else:
        m2 = re.search(r"(\d+)", host_spec)
        host = int(m2.group(1)) if m2 else None
    cm = re.search(r"(\d+)", cont)
    return host, (int(cm.group(1)) if cm else None)


def _env_has(env_list, prefix):
    return any(str(e).strip().strip('"').startswith(prefix) for e in (env_list or []))


def build_validation_report():
    """Parse docker-compose.yml and evaluate the stack invariants + fixes."""
    compose_path = DELIVERABLES_DIR / "docker-compose.yml"
    data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = data.get("services", {})
    oh = services.get("openhands", {})
    hr = services.get("headroom", {})

    oh_env = oh.get("environment", [])
    oh_vols = [str(v) for v in oh.get("volumes", [])]
    hr_vols = [str(v) for v in hr.get("volumes", [])]
    oh_ports = [_parse_ports(p) for p in oh.get("ports", [])]
    hr_ports = [_parse_ports(p) for p in hr.get("ports", [])]
    all_host_ports = [h for (h, _) in oh_ports + hr_ports]
    extra_hosts = [str(h) for h in oh.get("extra_hosts", [])]
    group_add = [str(g) for g in oh.get("group_add", [])]
    networks = data.get("networks", {})
    volumes = data.get("volumes", {})

    def chk(name, ok, detail="", why="", status=None):
        return {
            "name": name,
            "status": status or ("pass" if ok else "fail"),
            "detail": detail,
            "why": why,
        }

    groups = [
        {
            "name": "Ports & Constraints",
            "icon": "plug",
            "checks": [
                chk("Host ports 3000 & 4000 are never bound",
                    all(h not in (3000, 4000) for h in all_host_ports),
                    f"host ports = {sorted(set(all_host_ports))}",
                    "3000/4000 are reserved on your machine."),
                chk("OpenHands UI mapped host 5000 → container 3000",
                    (5000, 3000) in oh_ports, str(oh_ports),
                    "Required exposure for the OpenHands GUI."),
                chk("Headroom mapped host 5001 → container 8787",
                    (5001, 8787) in hr_ports, str(hr_ports),
                    "Headroom proxy default internal port is 8787."),
            ],
        },
        {
            "name": "Networking (DinD fix)",
            "icon": "network",
            "checks": [
                chk("extra_hosts sets host.docker.internal:host-gateway",
                    any("host.docker.internal:host-gateway" in h for h in extra_hosts),
                    str(extra_hosts),
                    "Lets the app reach the host and its spawned sandbox on Linux."),
                chk("WORKSPACE_MOUNT_PATH is an absolute HOST path (via env)",
                    any("WORKSPACE_MOUNT_PATH=${WORKSPACE_MOUNT_PATH" in str(e) for e in oh_env),
                    "",
                    "The sandbox is a sibling container; it can only mount host paths."),
                chk("Runtime image tag tied to OPENHANDS_VERSION (app/runtime sync)",
                    any("SANDBOX_RUNTIME_CONTAINER_IMAGE" in str(e) and "OPENHANDS_VERSION" in str(e)
                        for e in oh_env),
                    "",
                    "A version mismatch between app and runtime breaks the sandbox."),
                chk("Both services share ai-stack-network",
                    "ai-stack-network" in oh.get("networks", []) and
                    "ai-stack-network" in hr.get("networks", []),
                    "",
                    "Enables service-to-service communication by name."),
            ],
        },
        {
            "name": "Security (socket fix)",
            "icon": "shield",
            "checks": [
                chk("group_add uses detected DOCKER_GID (no chmod 666)",
                    any("DOCKER_GID" in g for g in group_add), str(group_add),
                    "Grants socket access securely via the owning group."),
                chk("Docker socket mounted read/write",
                    any("/var/run/docker.sock:/var/run/docker.sock" in v for v in oh_vols),
                    "",
                    "OpenHands needs it to spawn sandbox containers."),
                chk("Privileged mode disabled by default",
                    oh.get("privileged") in (None, False),
                    "",
                    "Not required for the docker-outside-of-docker model."),
                chk("Secrets sourced from .env (LLM_API_KEY interpolated)",
                    _env_has(oh_env, "LLM_API_KEY="),
                    "",
                    "No secrets are hardcoded in the compose file."),
            ],
        },
        {
            "name": "Persistence & Volumes",
            "icon": "database",
            "checks": [
                chk("Workspace bind mount → /opt/workspace_base",
                    any(v.endswith(":/opt/workspace_base") for v in oh_vols), "",
                    "Per spec: the OpenHands workspace path."),
                chk("OpenHands state volume defined",
                    "openhands-state" in volumes, "",
                    "Persists settings/conversations across restarts."),
                chk("Headroom data volume defined",
                    "headroom-data" in volumes, "",
                    "Persists Headroom config + local DB."),
            ],
        },
        {
            "name": "Compose Hygiene",
            "icon": "check",
            "checks": [
                chk("No obsolete top-level 'version:' key",
                    "version" not in data, "",
                    "Removed in the modern Compose Spec."),
                chk("restart: unless-stopped on both services",
                    oh.get("restart") == "unless-stopped" and hr.get("restart") == "unless-stopped",
                    "",
                    "Production-grade restart policy."),
                chk("Explicit container_name on both services",
                    bool(oh.get("container_name")) and bool(hr.get("container_name")),
                    f"{oh.get('container_name')}, {hr.get('container_name')}",
                    "Predictable naming convention."),
                chk("ai-stack-network is a custom bridge",
                    networks.get("ai-stack-network", {}).get("driver") == "bridge",
                    "",
                    "Isolated, named network for the stack."),
            ],
        },
    ]

    passed = sum(1 for g in groups for c in g["checks"] if c["status"] == "pass")
    failed = sum(1 for g in groups for c in g["checks"] if c["status"] == "fail")
    warn = sum(1 for g in groups for c in g["checks"] if c["status"] == "warn")
    total = passed + failed + warn

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {"passed": passed, "failed": failed, "warn": warn, "total": total},
        "groups": groups,
    }


# ----------------------------- Routes -----------------------------
@api_router.get("/")
async def root():
    return {"message": "AI Stack Console API"}


@api_router.get("/overview")
async def overview():
    """High-level summary for the hero + architecture sections."""
    return {
        "title": "AI Stack",
        "subtitle": "OpenHands + Headroom, orchestrated with Docker Compose",
        "quick_start": "./init.sh && docker compose up -d",
        "services": [
            {
                "id": "openhands",
                "name": "OpenHands",
                "role": "Autonomous AI software engineer",
                "image": "docker.all-hands.dev/all-hands-ai/openhands",
                "host_port": 5000,
                "container_port": 3000,
                "url": "http://localhost:5000",
                "highlights": [
                    "Spawns sandboxed sibling containers via the host Docker socket",
                    "Workspace bind-mounted at /opt/workspace_base",
                    "GLM (Z.AI) via LiteLLM",
                ],
            },
            {
                "id": "headroom",
                "name": "Headroom",
                "role": "LLM proxy · caching & cost optimization",
                "image": "ghcr.io/chopratejas/headroom",
                "host_port": 5001,
                "container_port": 8787,
                "url": "http://localhost:5001",
                "highlights": [
                    "Binds 0.0.0.0:8787 inside the container",
                    "Persists config + local DB to a named volume",
                    "Reachable by OpenHands over ai-stack-network",
                ],
            },
        ],
        "network": "ai-stack-network",
        "forbidden_ports": [3000, 4000],
        "fixes": [
            {
                "id": "socket",
                "icon": "shield",
                "title": "Docker Socket Permissions",
                "summary": "init.sh detects the GID that owns /var/run/docker.sock and adds the container to that group via group_add — the secure alternative to chmod 666.",
                "snippet": "group_add:\n  - \"${DOCKER_GID}\"   # auto-detected by init.sh",
            },
            {
                "id": "dind",
                "icon": "network",
                "title": "Docker-in-Docker Networking",
                "summary": "OpenHands spawns its sandbox as a sibling container on the host, so WORKSPACE_MOUNT_PATH must be an absolute host path. We also map the host gateway and keep app/runtime versions in sync.",
                "snippet": "extra_hosts:\n  - \"host.docker.internal:host-gateway\"\nenvironment:\n  - \"WORKSPACE_MOUNT_PATH=${WORKSPACE_MOUNT_PATH}\"  # absolute host path",
            },
        ],
    }


@api_router.get("/files")
async def list_files():
    """Return catalogue metadata (no content) for the file browser."""
    out = []
    for meta in FILE_CATALOG:
        path = DELIVERABLES_DIR / meta["name"]
        exists = path.is_file()
        text = path.read_text(encoding="utf-8") if exists else ""
        out.append({
            **meta,
            "exists": exists,
            "size": path.stat().st_size if exists else 0,
            "lines": text.count("\n") + 1 if text else 0,
        })
    return {"files": out}


@api_router.get("/files/{filename}")
async def get_file(filename: str):
    """Return a single file's content + metadata."""
    meta = CATALOG_BY_NAME.get(filename)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Unknown file: {filename}")
    content = _read_file(filename)
    return {
        **meta,
        "content": content,
        "lines": content.count("\n") + 1,
        "size": len(content.encode("utf-8")),
    }


@api_router.get("/files/{filename}/download")
async def download_file(filename: str):
    content = _read_file(filename)
    # best-effort download log
    try:
        await db.download_logs.insert_one({
            "file": filename,
            "kind": "single",
            "at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@api_router.get("/download-all")
async def download_all():
    """Bundle every deliverable into a zip named ai-stack.zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for meta in FILE_CATALOG:
            path = DELIVERABLES_DIR / meta["name"]
            if path.is_file():
                zf.write(path, arcname=f"ai-stack/{meta['name']}")
    buf.seek(0)
    try:
        await db.download_logs.insert_one({
            "file": "ai-stack.zip",
            "kind": "zip",
            "at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="ai-stack.zip"'},
    )


@api_router.get("/validate")
async def validate():
    try:
        return build_validation_report()
    except Exception as e:  # pragma: no cover
        logging.exception("validation failed")
        raise HTTPException(status_code=500, detail=f"Validation error: {e}")


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.model_dump())
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
