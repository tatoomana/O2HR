#!/usr/bin/env python3
"""
Static validation for the OpenHands + Headroom Compose stack.

Docker is not required to run this. It parses docker-compose.yml and asserts the
hard constraints and the two reliability fixes are present, validates .env.example
keys, and syntax-checks init.sh (bash -n).

Usage:  python3 validate_stack.py
Exit code 0 on success, 1 on any failure.
"""
import os
import re
import sys
import subprocess

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
COMPOSE = os.path.join(HERE, "docker-compose.yml")
ENV_EXAMPLE = os.path.join(HERE, ".env.example")
INIT_SH = os.path.join(HERE, "init.sh")

FORBIDDEN_HOST_PORTS = {3000, 4000}

passed, failed = [], []


def check(name, condition, detail=""):
    if condition:
        passed.append(name)
        print(f"  [PASS] {name}")
    else:
        failed.append((name, detail))
        print(f"  [FAIL] {name}  {('- ' + detail) if detail else ''}")


def parse_port(p):
    """Return (host_port, container_port) resolving ${VAR:-default} host specs."""
    p = str(p).strip().strip('"')
    host_spec, cont = p.rsplit(":", 1)
    m = re.search(r":-(\d+)", host_spec)          # ${VAR:-5000}
    if m:
        host = int(m.group(1))
    else:
        m2 = re.search(r"(\d+)", host_spec)
        host = int(m2.group(1)) if m2 else None
    cm = re.search(r"(\d+)", cont)
    return host, (int(cm.group(1)) if cm else None)


def env_list_has_prefix(env_list, prefix):
    return any(str(e).strip().strip('"').startswith(prefix) for e in env_list)


def main():
    print("== Validating docker-compose.yml ==")
    with open(COMPOSE) as f:
        raw = f.read()
        data = yaml.safe_load(raw)

    # No obsolete top-level version key
    check("No deprecated top-level 'version:' key", "version" not in data)

    services = data.get("services", {})
    check("Service 'openhands' exists", "openhands" in services)
    check("Service 'headroom' exists", "headroom" in services)

    oh = services.get("openhands", {})
    hr = services.get("headroom", {})

    # ---- Ports / forbidden host ports ----
    all_host_ports = []
    for svc_name, svc in services.items():
        for p in svc.get("ports", []):
            host, cont = parse_port(p)
            all_host_ports.append(host)
    check("No forbidden host port (3000/4000) is bound",
          all(h not in FORBIDDEN_HOST_PORTS for h in all_host_ports),
          f"host ports = {all_host_ports}")

    oh_ports = [parse_port(p) for p in oh.get("ports", [])]
    hr_ports = [parse_port(p) for p in hr.get("ports", [])]
    check("OpenHands maps host 5000 -> container 3000", (5000, 3000) in oh_ports,
          str(oh_ports))
    check("Headroom maps host 5001 -> container 8787", (5001, 8787) in hr_ports,
          str(hr_ports))

    # ---- Restart policy ----
    check("OpenHands restart: unless-stopped", oh.get("restart") == "unless-stopped")
    check("Headroom restart: unless-stopped", hr.get("restart") == "unless-stopped")

    # ---- Container names ----
    check("OpenHands has container_name", bool(oh.get("container_name")))
    check("Headroom has container_name", bool(hr.get("container_name")))

    # ---- Socket mount ----
    oh_vols = [str(v) for v in oh.get("volumes", [])]
    check("OpenHands mounts the docker socket",
          any("/var/run/docker.sock:/var/run/docker.sock" in v for v in oh_vols))
    check("OpenHands bind-mounts workspace -> /opt/workspace_base",
          any(v.endswith(":/opt/workspace_base") for v in oh_vols))

    # ---- FIX #1: socket permissions via group_add ----
    ga = [str(g) for g in oh.get("group_add", [])]
    check("FIX#1 socket perms: group_add uses DOCKER_GID",
          any("DOCKER_GID" in g for g in ga), str(ga))

    # ---- FIX #2: DinD networking + absolute host workspace ----
    eh = [str(h) for h in oh.get("extra_hosts", [])]
    check("FIX#2 networking: extra_hosts host.docker.internal:host-gateway",
          any("host.docker.internal:host-gateway" in h for h in eh), str(eh))

    oh_env = oh.get("environment", [])
    check("OpenHands env sets WORKSPACE_BASE", env_list_has_prefix(oh_env, "WORKSPACE_BASE="))
    check("OpenHands env sets WORKSPACE_MOUNT_PATH",
          env_list_has_prefix(oh_env, "WORKSPACE_MOUNT_PATH="))
    check("WORKSPACE_MOUNT_PATH is driven by env (absolute host path via init.sh)",
          any("WORKSPACE_MOUNT_PATH=${WORKSPACE_MOUNT_PATH" in str(e) for e in oh_env))
    check("OpenHands env sets SANDBOX_RUNTIME_CONTAINER_IMAGE",
          env_list_has_prefix(oh_env, "SANDBOX_RUNTIME_CONTAINER_IMAGE="))
    check("Runtime image tag tied to OPENHANDS_VERSION (app/runtime in sync)",
          any("SANDBOX_RUNTIME_CONTAINER_IMAGE" in str(e) and "OPENHANDS_VERSION" in str(e)
              for e in oh_env))
    check("OpenHands env sets SANDBOX_USER_ID", env_list_has_prefix(oh_env, "SANDBOX_USER_ID="))
    check("OpenHands LLM_MODEL present", env_list_has_prefix(oh_env, "LLM_MODEL="))
    check("OpenHands LLM_API_KEY present", env_list_has_prefix(oh_env, "LLM_API_KEY="))

    # ---- Headroom persistence + bind ----
    hr_vols = [str(v) for v in hr.get("volumes", [])]
    check("Headroom has a persistence volume", len(hr_vols) >= 1, str(hr_vols))
    check("Headroom binds to 0.0.0.0",
          any("0.0.0.0" in str(c) for c in hr.get("command", [])), str(hr.get("command")))

    # ---- Custom network ----
    nets = data.get("networks", {})
    check("ai-stack-network defined", "ai-stack-network" in nets)
    check("ai-stack-network is a bridge",
          nets.get("ai-stack-network", {}).get("driver") == "bridge")
    check("OpenHands attached to ai-stack-network",
          "ai-stack-network" in oh.get("networks", []))
    check("Headroom attached to ai-stack-network",
          "ai-stack-network" in hr.get("networks", []))

    # ---- Named volumes ----
    vols = data.get("volumes", {})
    check("openhands-state volume defined", "openhands-state" in vols)
    check("headroom-data volume defined", "headroom-data" in vols)

    # ---- .env.example ----
    print("\n== Validating .env.example ==")
    with open(ENV_EXAMPLE) as f:
        env_text = f.read()
    for key in ["LLM_API_KEY", "LLM_MODEL", "LLM_BASE_URL", "OPENHANDS_VERSION",
                "OPENHANDS_HOST_PORT", "HEADROOM_HOST_PORT", "HEADROOM_VERSION"]:
        check(f".env.example documents {key}", re.search(rf"(?m)^#?\s*{key}=", env_text) is not None)

    # ---- init.sh ----
    print("\n== Validating init.sh ==")
    with open(INIT_SH) as f:
        init_text = f.read()
    check("init.sh creates the workspace dir", "mkdir -p" in init_text)
    check("init.sh computes DOCKER_GID from the socket", "stat -c '%g'" in init_text)
    check("init.sh sets absolute WORKSPACE_MOUNT_PATH", "WORKSPACE_MOUNT_PATH" in init_text)
    check("init.sh sets SANDBOX_USER_ID from id -u", "id -u" in init_text)
    r = subprocess.run(["bash", "-n", INIT_SH], capture_output=True, text=True)
    check("init.sh passes bash -n syntax check", r.returncode == 0, r.stderr.strip())

    # ---- summary ----
    print("\n" + "=" * 60)
    print(f"RESULT: {len(passed)} passed, {len(failed)} failed")
    if failed:
        print("\nFailures:")
        for n, d in failed:
            print(f"  - {n}: {d}")
        return 1
    print("All checks passed — stack invariants and both fixes verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
