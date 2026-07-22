# plan.md

## 1) Objectives
- Deliver a **first-try working** `docker-compose.yml` running **OpenHands + Headroom** together.
- Enforce hard constraints: **no host 3000/4000 binds**; expose **OpenHands on 5000**, **Headroom on 5001**; both on `ai-stack-network`.
- Implement the two critical reliability fixes:
  - **Docker socket permissions** via `group_add` using host **DOCKER_GID** computed by `init.sh`.
  - **DinD/sibling-container workspace correctness** by setting `WORKSPACE_MOUNT_PATH` to the **absolute host path** (written into `.env` by `init.sh`) + `extra_hosts: host.docker.internal:host-gateway`.
- Provide production-ready deliverables: `docker-compose.yml`, `.env.example`, `init.sh`, `README.md`.
- Provide a previewable **web dashboard** (FastAPI + React) to view/copy/download files + zip, with a “Fixes Applied” explainer.

---

## 2) Implementation Steps

### Phase 1 — Core POC (isolation): compose reliability + invariants
**Goal:** Prove the core workflow (compose config + init script + invariants for the two failure modes) is correct **before** building the dashboard.

User stories:
1. As a user, I want `init.sh` to generate a correct `.env` so I don’t have to debug env wiring.
2. As a user, I want Docker socket permissions handled safely (no `chmod 666`).
3. As a user, I want OpenHands to create sandbox sibling containers that can see the workspace reliably.
4. As a user, I want the stack to respect forbidden ports and always bind 5000/5001.
5. As a user, I want the compose file to be valid with modern `docker compose`.

Steps:
1. Web research pass for latest OpenHands/Headroom run requirements (image names, internal ports, required env vars, known gotchas).
2. Create initial deliverables in `/app/deliverables/`:
   - `docker-compose.yml` with `ai-stack-network`, ports 5000→3000, 5001→8787, `restart: unless-stopped`, socket + workspace + state mounts.
   - Ensure OpenHands app+runtime stay in sync via a single `OPENHANDS_VERSION` variable (document “latest” option).
   - Ensure OpenHands includes `extra_hosts: ["host.docker.internal:host-gateway"]`.
   - Add `group_add: ["${DOCKER_GID}"]` for OpenHands.
   - Add Headroom persistence volume to `~/.headroom` (container path per docs).
3. Implement `init.sh` (robust, idempotent):
   - Create `./workspace`.
   - Compute `HOST_WORKSPACE_PATH` as absolute path.
   - Compute `SANDBOX_USER_ID=$(id -u)`.
   - Compute `DOCKER_GID` from `/var/run/docker.sock` (fail with actionable message if missing).
   - Write `.env` (or update) with `WORKSPACE_MOUNT_PATH=$HOST_WORKSPACE_PATH`, `WORKSPACE_BASE=/opt/workspace_base`, `DOCKER_GID`, `SANDBOX_USER_ID`, ports, OpenHands version/runtime image.
4. Add `.env.example` covering both services (Z.AI GLM defaults):
   - `LLM_MODEL` (default to `zai/glm-4.6`; document mapping to user “glm 5.2”).
   - `LLM_BASE_URL` default `https://api.z.ai/api/paas/v4`.
   - `LLM_API_KEY` placeholder.
5. Add `README.md` quickstart + troubleshooting focused on the two failure modes.
6. Static validation scripts (since Docker daemon not available):
   - Python: parse YAML + assert invariants (ports, network, mounts, env keys, extra_hosts, group_add).
   - `bash -n init.sh`.
   - If feasible, install compose v2 binary and run `docker compose config` (schema validation without daemon).

Gate to proceed: POC validations pass and invariants are enforced.

---

### Phase 2 — V1 App Development (dashboard MVP)
**Goal:** Build the previewable dashboard that surfaces the deliverables with great UX.

User stories:
1. As a user, I want to view each generated file with syntax highlighting.
2. As a user, I want one-click copy for each file.
3. As a user, I want to download individual files.
4. As a user, I want a “download all as zip” button.
5. As a user, I want a clear “Fixes Applied” section explaining why this stack won’t fail like before.

Steps:
1. Backend (FastAPI):
   - Serve file list and file contents from `/app/deliverables/`.
   - Provide endpoints to download individual files and a zip bundle.
   - (Optional) log downloads to MongoDB.
2. Frontend (React + shadcn/ui):
   - Landing page: architecture diagram (simple SVG), ports table, start instructions.
   - Tabs/cards per file with highlighted view + copy/download.
   - “Fixes Applied” section summarizing socket GID + absolute host workspace path + host-gateway.
3. Wire FE↔BE; ensure correct base URLs.
4. Run and verify preview behavior.
5. **Call `testing_agent`** for 1 full E2E pass of the dashboard and download flows.

---

### Phase 3 — Hardening + quality improvements
User stories:
1. As a user, I want validation errors to be actionable (exact fix steps).
2. As a user, I want the zip to always include `.env.example` and README.
3. As a user, I want the dashboard to warn me if I bind forbidden ports.
4. As a user, I want OS-specific notes (Linux vs macOS/WSL) clearly separated.
5. As a user, I want the stack to support switching OpenHands version safely.

Steps:
1. Add a backend “self-check” endpoint that runs the static validations and returns a report.
2. Add frontend display of the self-check report.
3. Improve README troubleshooting (WSL2/macOS notes; Docker Desktop socket path notes).
4. Re-run **testing_agent** E2E.

---

## 3) Next Actions
1. Implement Phase 1 deliverables (`docker-compose.yml`, `.env.example`, `init.sh`, `README.md`) + static validation script.
2. Run static validations locally in this environment.
3. Implement Phase 2 dashboard (FastAPI + React) reading from `/app/deliverables/`.
4. Invoke **testing_agent** to verify dashboard E2E and that the two critical fixes are present/visible.

---

## 4) Success Criteria
- Compose hard constraints met: host ports **5000/5001 only**, no 3000/4000 binds; both services on `ai-stack-network`.
- OpenHands reliability fixes present:
  - `group_add` with computed `DOCKER_GID`.
  - `WORKSPACE_MOUNT_PATH` equals **absolute host workspace path** (from `init.sh`), and `extra_hosts` includes `host.docker.internal:host-gateway`.
  - App/runtime version kept in sync via single variable.
- `init.sh` is idempotent and fails fast with clear messages if prerequisites missing.
- Dashboard can view/copy/download each file and download zip-all.
- **testing_agent report** confirms dashboard flows work and deliverables are accessible.