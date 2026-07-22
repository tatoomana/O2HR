# AI Stack — OpenHands + Headroom (Docker Compose)

A production-ready, **first-try-working** Docker Compose stack that runs two AI
apps side by side on a shared network:

| Service   | What it does                                             | UI URL                  | Container port |
|-----------|----------------------------------------------------------|-------------------------|----------------|
| OpenHands | Autonomous AI software engineer (spawns dev sandboxes)   | http://localhost:5000   | `3000`         |
| Headroom  | LLM proxy (caching + cost/latency optimization)          | http://localhost:5001   | `8787`         |

> Host ports **3000** and **4000** are intentionally **not** used (reserved on your machine).

---

## Prerequisites

- Docker Engine 20.10+ with the **Compose v2 plugin** (`docker compose`, not `docker-compose`).
- Linux host recommended (Docker Desktop on macOS/Windows works — see notes below).
- A **GLM / Z.AI API key** (https://z.ai).

---

## Quick start (3 commands)

```bash
# 1. Prepare the host (creates ./workspace, detects docker GID, writes .env)
./init.sh

# 2. Add your GLM/Z.AI key to the generated .env
#    LLM_API_KEY=sk-...

# 3. Launch
docker compose up -d
```

Then open:
- **OpenHands** → http://localhost:5000
- **Headroom**  → http://localhost:5001

Stop / view logs:
```bash
docker compose logs -f          # follow logs
docker compose down             # stop (keeps named volumes)
docker compose down -v          # stop and delete persisted data
```

---

## Files in this bundle

| File                 | Purpose                                                                 |
|----------------------|-------------------------------------------------------------------------|
| `docker-compose.yml` | The stack definition (Compose Spec, no obsolete `version:` key).        |
| `.env.example`       | All environment variables. Copy to `.env` (done for you by `init.sh`).  |
| `init.sh`            | Idempotent host prep: workspace, docker GID, host paths → writes `.env`. |
| `.gitignore`         | Keeps `.env` and `./workspace` out of version control.                  |
| `README.md`          | This file.                                                              |

---

## The two fixes that make this work first try

These two issues are why the stack usually fails. Both are handled here.

### 1. Docker socket permissions (secure fix)
OpenHands needs `/var/run/docker.sock` to spawn its sandbox. Instead of the
insecure `chmod 666`, `init.sh` detects the **group id that owns the socket**
(`stat -c '%g' /var/run/docker.sock`) and writes it as `DOCKER_GID`. Compose
then adds the container to that group:

```yaml
group_add:
  - "${DOCKER_GID}"
```

### 2. Docker-in-Docker networking / workspace mount (the #1 killer)
OpenHands runs **docker-outside-of-docker**: it uses the host daemon to create
its sandbox as a **sibling container on the host**. That sandbox can only mount
a path that exists **on the host filesystem** — not a path inside the OpenHands
container. So `WORKSPACE_MOUNT_PATH` **must be an absolute host path**.
`init.sh` computes it and writes it to `.env`. We also map the host gateway:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

And we keep the **app image and runtime image versions in sync** via a single
`OPENHANDS_VERSION` variable (a mismatch is another common failure).

---

## Configuration

All config lives in `.env`. Key variables:

| Variable                 | Default                             | Notes                                                   |
|--------------------------|-------------------------------------|---------------------------------------------------------|
| `LLM_API_KEY`            | _(required)_                        | Your GLM / Z.AI key.                                    |
| `LLM_MODEL`              | `zai/glm-4.6`                       | LiteLLM model string (you asked for "GLM 5.2").         |
| `LLM_BASE_URL`           | `https://api.z.ai/api/paas/v4`      | Use the China endpoint if applicable.                   |
| `OPENHANDS_VERSION`      | `0.53`                              | Drives both app + runtime image tags.                   |
| `OPENHANDS_HOST_PORT`    | `5000`                              | Host port for OpenHands UI.                             |
| `HEADROOM_HOST_PORT`     | `5001`                              | Host port for Headroom.                                 |
| `WORKSPACE_MOUNT_PATH`   | _(set by init.sh)_                  | Absolute host workspace path.                           |
| `DOCKER_GID`             | _(set by init.sh)_                  | Group owning `docker.sock`.                             |
| `SANDBOX_USER_ID`        | _(set by init.sh)_                  | Your host uid, so workspace files are owned by you.     |

### GLM model note
You requested **"GLM 5.2"**. The currently available Z.AI coding model through
LiteLLM is `zai/glm-4.6`, used as the default. Change `LLM_MODEL` in `.env` to
your exact model id when it is available on your plan.

---

## Optional: route OpenHands through Headroom

Both services share the `ai-stack-network` bridge, so they can reach each other
by name. To send OpenHands' LLM traffic through the Headroom proxy (for caching
/ cost savings), set in `.env`:

```bash
LLM_BASE_URL=http://headroom:8787
```

(Then configure Headroom with your upstream provider as per its docs.)

---

## Troubleshooting

**`permission denied ... /var/run/docker.sock`**
- Re-run `./init.sh` (it recomputes `DOCKER_GID`).
- Confirm `docker ps` works as your user on the host.
- Do **not** `chmod 666` the socket; `group_add` is the correct fix.

**Sandbox starts but the workspace is empty / runtime fails to mount**
- This is the sibling-container path issue. Ensure `WORKSPACE_MOUNT_PATH` in
  `.env` is an **absolute host path** (it will be, if you ran `./init.sh`).

**`runtime image ... not found` / sandbox won't start**
- App and runtime versions must match. Keep them driven by `OPENHANDS_VERSION`,
  or set `SANDBOX_RUNTIME_CONTAINER_IMAGE` explicitly to the matching tag.

**Port already in use**
- Change `OPENHANDS_HOST_PORT` / `HEADROOM_HOST_PORT` in `.env` (never 3000/4000).

**macOS / Windows (Docker Desktop)**
- The socket path is provided by Docker Desktop; `init.sh` falls back to
  `DOCKER_GID=999`, which is correct for Docker Desktop VMs.

**WSL2**
- Run everything inside the WSL2 distro (not Windows paths) so the absolute
  host workspace path resolves correctly.

---

## Security notes
- Secrets live only in `.env` (git-ignored). Never commit real keys.
- Mounting the Docker socket grants root-equivalent host access to OpenHands —
  run this stack only on machines you trust.
- Privileged mode is **disabled** by default (not needed for the socket model).
