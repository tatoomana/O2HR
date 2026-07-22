# plan.md (Updated)

## 1) Objectives
- Deliver a **first-try working** `docker-compose.yml` running **OpenHands + Headroom** together.
- Enforce hard constraints: **no host 3000/4000 binds**; expose **OpenHands on 5000**, **Headroom on 5001**; both on `ai-stack-network`.
- Implement and *prove* the two critical reliability fixes:
  - **Docker socket permissions** via `group_add` using host **DOCKER_GID** computed by `init.sh` (secure alternative to `chmod 666`).
  - **DinD/sibling-container workspace correctness** via **absolute host** `WORKSPACE_MOUNT_PATH` (written into `.env` by `init.sh`) + `extra_hosts: host.docker.internal:host-gateway` + **OpenHands app/runtime version sync**.
- Provide production-ready deliverables in `/app/deliverables/`:
  - `docker-compose.yml`, `.env.example`, `init.sh`, `README.md`, plus `.gitignore` and `validate_stack.py`.
- Provide a previewable **web dashboard** (FastAPI + React) to view/copy/download files + zip, and show a **live validation report**.
- Validate and regression-test the solution via the **testing_agent** (required), including post-fix re-testing.

---

## 2) Implementation Steps

### Phase 1 — Core POC (isolation): compose reliability + invariants (COMPLETED)
**Goal:** Prove the compose config + init script solve the two historical failure modes (Docker socket permissions + DinD workspace/networking) **before** building the dashboard.

User stories:
1. As a user, I want `init.sh` to generate a correct `.env` so I don’t have to debug env wiring.
2. As a user, I want Docker socket permissions handled safely (no `chmod 666`).
3. As a user, I want OpenHands to create sandbox sibling containers that can see the workspace reliably.
4. As a user, I want the stack to respect forbidden ports and always bind 5000/5001.
5. As a user, I want the compose file to be valid with modern `docker compose`.

Steps completed:
1. Web research confirmed:
   - OpenHands registry + port + socket/runtime requirements.
   - Headroom image + default port + persistence path.
2. Created deliverables in `/app/deliverables/`:
   - `docker-compose.yml`
     - Custom network `ai-stack-network`.
     - Port bindings: **5000→3000** (OpenHands), **5001→8787** (Headroom).
     - Restart policy: `unless-stopped`.
     - OpenHands mounts `/var/run/docker.sock`.
     - Workspace bind mount to `/opt/workspace_base`.
     - `extra_hosts: host.docker.internal:host-gateway`.
     - `group_add: ["${DOCKER_GID}"]`.
     - App/runtime version sync via `OPENHANDS_VERSION` → runtime image tag.
   - `.env.example` with GLM (Z.AI) defaults: `LLM_MODEL=zai/glm-4.6`, `LLM_BASE_URL=https://api.z.ai/api/paas/v4`, `LLM_API_KEY` placeholder.
   - `init.sh`:
     - Creates `./workspace`.
     - Computes absolute host workspace path.
     - Computes `SANDBOX_USER_ID=$(id -u)`.
     - Computes `DOCKER_GID` from the docker socket when available, with safe fallback messaging.
     - Writes/upserts `.env` without clobbering secrets.
   - `README.md` emphasizing the two fixes and first-try reliability.
   - `.gitignore` + `validate_stack.py`.
3. Validation completed:
   - Static validator `validate_stack.py`: **42/42** checks passed.
   - Authoritative Compose validation: `docker compose config` (downloaded correct arch binary) passed.
   - `init.sh` end-to-end run verified.
   - Fail-fast behavior verified (missing required env triggers explicit error).

Gate result:
- ✅ POC validations passed and invariants are enforced.

---

### Phase 2 — V1 App Development (dashboard MVP) (COMPLETED)
**Goal:** Build the previewable dashboard that surfaces the deliverables with great UX.

User stories:
1. As a user, I want to view each generated file with syntax highlighting.
2. As a user, I want one-click copy for each file.
3. As a user, I want to download individual files.
4. As a user, I want a “download all as zip” button.
5. As a user, I want a clear “Fixes Applied” section explaining why this stack won’t fail like before.
6. As a user, I want proof via a CI-like validation report.

Steps completed:
1. Backend (FastAPI):
   - Implemented endpoints:
     - `/api/overview`, `/api/files`, `/api/files/{filename}`, `/api/files/{filename}/download`, `/api/download-all`, `/api/validate`.
   - Zip bundling includes all 6 deliverables under `ai-stack/`.
   - Live validation report parses `docker-compose.yml` and produces grouped pass/fail checks.
2. Frontend (React + shadcn/ui):
   - Dark-first “AI Stack Console” dashboard with sticky nav anchors.
   - Architecture diagram (inline SVG), ports table, “Fixes Applied” cards.
   - File browser + syntax-highlighted code panel with copy/download.
   - Validation panel with grouped checklist and refresh.
   - Quick start section.
3. Testing (required):
   - **testing_agent iteration_1:** 99.5% overall; identified a low-priority traversal-related edge-case.

---

### Phase 3 — Hardening + quality improvements (COMPLETED)
**Goal:** Remove the remaining minor issue found by tests; ensure regression-proof API behavior.

Steps completed:
1. Added defense-in-depth API hardening:
   - Explicit filename whitelist guard (`_is_safe_name`).
   - Resolved-path containment check to ensure reads stay inside `/app/deliverables`.
2. Re-tested:
   - **testing_agent iteration_2:** **100% (33/33)** regression pass; traversal attempts that reach API return 404; no regressions.

---

## 3) Next Actions
All planned work is complete and verified.

Optional future enhancements (not required for delivery):
1. Add an optional “Route OpenHands via Headroom” toggle/demo (set `LLM_BASE_URL=http://headroom:8787`).
2. Add a `Makefile` alternative to `init.sh`.
3. Add OS-specific helpers (WSL2/macOS detection) to `init.sh` for improved messaging.
4. Add a “Generate .env” UI wizard in the dashboard.

---

## 4) Success Criteria
- ✅ Compose hard constraints met: host ports **5000/5001 only**, no 3000/4000 binds; both services on `ai-stack-network`.
- ✅ OpenHands reliability fixes present and validated:
  - `group_add` with computed `DOCKER_GID` (secure socket permission fix).
  - `WORKSPACE_MOUNT_PATH` driven by `.env` (absolute host path via `init.sh`) + `extra_hosts` host-gateway.
  - App/runtime version kept in sync via a single `OPENHANDS_VERSION` variable.
- ✅ `init.sh` is idempotent and produces a correct `.env`.
- ✅ Static validation passed (42/42) + authoritative `docker compose config` passed.
- ✅ Dashboard can view/copy/download each file and download zip-all.
- ✅ **testing_agent reports** confirm:
  - iteration_1: full E2E coverage of dashboard and API; critical fixes verified.
  - iteration_2: hardening regression suite 100% pass.
