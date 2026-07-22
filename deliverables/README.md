# AI Stack - OpenHands + Headroom (Docker Compose)

A production-ready, **first-try-working** Docker Compose stack that runs two AI
apps side by side on a shared network. This repository is pure Infrastructure as
Code - no application/build steps required.

| Service   | What it does                                             | UI URL                  | Container port |
|-----------|----------------------------------------------------------|-------------------------|----------------|
| OpenHands | Autonomous AI software engineer (spawns dev sandboxes)   | http://localhost:5000   | `3000`         |
| Headroom  | LLM proxy (caching + cost/latency optimization)          | http://localhost:5001   | `8787`         |

> Host ports **3000** and **4000** are intentionally **not** used (reserved on your machine).

---

## Repository contents

| File                 | Purpose                                                                 |
|----------------------|-------------------------------------------------------------------------|
| `docker-compose.yml` | The stack definition (Compose Spec, no obsolete `version:` key).        |
| `.env.example`       | All environment variables. Copy to `.env` (done for you by `init.sh`).  |
| `init.sh`            | Idempotent host prep: workspace, docker GID, host paths -> writes `.env`.|
| `.gitignore`         | Keeps `.env` and generated state (`workspace/`, `.openhands-state/`) out of git. |
| `push_to_github.sh`  | One-command publish of this stack to your own GitHub repo.              |
| `README.md`          | This file.                                                              |

---

## Prerequisites

- Docker Engine 20.10+ with the **Compose v2 plugin** (`docker compose`).
- Linux host recommended (Docker Desktop on macOS/Windows works - see notes below).
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
- **OpenHands** -> http://localhost:5000
- **Headroom**  -> http://localhost:5001

Manage the stack:
```bash
docker compose logs -f          # follow logs
docker compose down             # stop (keeps named volumes)
docker compose down -v          # stop and delete persisted data
```

---

## Publish to your own GitHub repository

1. Create a new **empty** repository on GitHub (no README/license), and copy its URL.
2. Run:

```bash
./push_to_github.sh https://github.com/<you>/ai-stack.git
```

The script runs `git init`, stages the core files, commits
`feat: initial OpenHands + Headroom Docker stack`, and pushes to the `main`
branch. Your secret `.env` is git-ignored and never pushed.

> Uses HTTPS or SSH URLs. For HTTPS you may be prompted for a GitHub Personal
> Access Token; for SSH ensure your key is added to GitHub.

---

## The two fixes that make this work first try

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
a path that exists **on the host filesystem** - not a path inside the OpenHands
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
| `LLM_MODEL`              | `zai/glm-4.6`                       | LiteLLM model string (set to your exact GLM model).     |
| `LLM_BASE_URL`           | `https://api.z.ai/api/paas/v4`      | Use the China endpoint if applicable.                   |
| `OPENHANDS_VERSION`      | `0.53`                              | Drives both app + runtime image tags.                   |
| `OPENHANDS_HOST_PORT`    | `5000`                              | Host port for OpenHands UI.                             |
| `HEADROOM_HOST_PORT`     | `5001`                              | Host port for Headroom.                                 |
| `WORKSPACE_MOUNT_PATH`   | _(set by init.sh)_                  | Absolute host workspace path.                           |
| `DOCKER_GID`             | _(set by init.sh)_                  | Group owning `docker.sock`.                             |
| `SANDBOX_USER_ID`        | _(set by init.sh)_                  | Your host uid, so workspace files are owned by you.     |

---

## Optional: route OpenHands through Headroom

Both services share the `ai-stack-network` bridge, so they can reach each other
by name. To send OpenHands' LLM traffic through the Headroom proxy, set in `.env`:

```bash
LLM_BASE_URL=http://headroom:8787
```

---

## Troubleshooting

**`permission denied ... /var/run/docker.sock`** - re-run `./init.sh` (it
recomputes `DOCKER_GID`). Confirm `docker ps` works as your user. Do not
`chmod 666` the socket.

**Sandbox starts but workspace is empty** - ensure `WORKSPACE_MOUNT_PATH` in
`.env` is an absolute host path (it will be, if you ran `./init.sh`).

**`runtime image ... not found`** - app and runtime versions must match; keep
them driven by `OPENHANDS_VERSION`.

**Port already in use** - change `OPENHANDS_HOST_PORT` / `HEADROOM_HOST_PORT`
in `.env` (never 3000/4000).

**macOS / Windows (Docker Desktop)** - `init.sh` falls back to `DOCKER_GID=999`,
which is correct for Docker Desktop VMs.

**WSL2** - run everything inside the WSL2 distro so the absolute host workspace
path resolves correctly.

---

## Security notes
- Secrets live only in `.env` (git-ignored). Never commit real keys.
- Mounting the Docker socket grants root-equivalent host access to OpenHands -
  run this stack only on machines you trust.
- Privileged mode is disabled by default (not needed for the socket model).
