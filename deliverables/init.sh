#!/usr/bin/env bash
# ==============================================================================
# init.sh — prepares the host for the OpenHands + Headroom stack.
# Idempotent: safe to run repeatedly.
#
#   1. Creates ./workspace with sane permissions.
#   2. Computes the host-specific values that make the stack work FIRST TRY:
#        • WORKSPACE_BASE / WORKSPACE_MOUNT_PATH  (absolute host path — DinD fix)
#        • DOCKER_GID                             (owner group of docker.sock)
#        • SANDBOX_USER_ID                         (so workspace files are yours)
#   3. Writes/updates .env WITHOUT clobbering your LLM_API_KEY.
#
# Usage:   ./init.sh   then   docker compose up -d
# ==============================================================================
set -euo pipefail

# Always operate from this script's own directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE=".env"
ENV_EXAMPLE=".env.example"
WORKSPACE_DIR="./workspace"
SOCK="/var/run/docker.sock"

log()  { printf '\033[0;36m[init]\033[0m %s\n' "$*"; }
ok()   { printf '\033[0;32m[ ok ]\033[0m %s\n' "$*"; }
warn() { printf '\033[0;33m[warn]\033[0m %s\n' "$*"; }
err()  { printf '\033[0;31m[fail]\033[0m %s\n' "$*" >&2; }

# ---- 1. workspace -----------------------------------------------------------
log "Ensuring workspace directory exists..."
mkdir -p "$WORKSPACE_DIR"
chmod 0775 "$WORKSPACE_DIR"
HOST_WORKSPACE_PATH="$(cd "$WORKSPACE_DIR" && pwd)"
ok "Workspace ready at: $HOST_WORKSPACE_PATH"

# ---- 2. .env bootstrap ------------------------------------------------------
if [[ ! -f "$ENV_FILE" ]]; then
  if [[ -f "$ENV_EXAMPLE" ]]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    ok "Created $ENV_FILE from $ENV_EXAMPLE"
  else
    : > "$ENV_FILE"
    warn "$ENV_EXAMPLE not found; created empty $ENV_FILE"
  fi
fi

# Upsert KEY=VALUE into .env (replaces any existing/commented definition).
set_env() {
  local key="$1" value="$2"
  if grep -qE "^[#[:space:]]*${key}=" "$ENV_FILE" 2>/dev/null; then
    grep -vE "^[#[:space:]]*${key}=" "$ENV_FILE" > "${ENV_FILE}.tmp"
    mv "${ENV_FILE}.tmp" "$ENV_FILE"
  fi
  printf '%s=%s\n' "$key" "$value" >> "$ENV_FILE"
}

# ---- 3. docker socket + GID (secure socket-permission fix) ------------------
if [[ -S "$SOCK" ]]; then
  if stat -c '%g' "$SOCK" >/dev/null 2>&1; then
    DOCKER_GID="$(stat -c '%g' "$SOCK")"     # GNU / Linux
  else
    DOCKER_GID="$(stat -f '%g' "$SOCK")"     # BSD / macOS
  fi
  ok "Docker socket found; group id (GID) = $DOCKER_GID"
else
  warn "Docker socket not found at $SOCK."
  warn "On Docker Desktop (macOS/Windows) this is expected; defaulting DOCKER_GID=999."
  DOCKER_GID="999"
fi

# ---- 4. host identity -------------------------------------------------------
SANDBOX_USER_ID="$(id -u)"

# ---- 5. persist computed values --------------------------------------------
log "Writing host-specific values into $ENV_FILE ..."
set_env "WORKSPACE_BASE"       "$HOST_WORKSPACE_PATH"
set_env "WORKSPACE_MOUNT_PATH" "$HOST_WORKSPACE_PATH"
set_env "DOCKER_GID"           "$DOCKER_GID"
set_env "SANDBOX_USER_ID"      "$SANDBOX_USER_ID"
ok "Environment prepared."

# ---- 6. secret sanity check -------------------------------------------------
if grep -qE '^LLM_API_KEY=(your_zai_glm_api_key_here)?[[:space:]]*$' "$ENV_FILE"; then
  warn "LLM_API_KEY is not set yet — edit .env and add your GLM/Z.AI key before starting."
fi

# ---- 7. next steps ----------------------------------------------------------
OH_PORT="$(grep -E '^OPENHANDS_HOST_PORT=' "$ENV_FILE" | tail -n1 | cut -d= -f2)"
HR_PORT="$(grep -E '^HEADROOM_HOST_PORT=' "$ENV_FILE" | tail -n1 | cut -d= -f2)"
OH_PORT="${OH_PORT:-5000}"
HR_PORT="${HR_PORT:-5001}"

printf '\n'
ok "Setup complete."
cat <<EOF
Next steps:
  1) Add your GLM/Z.AI key to .env      ->  LLM_API_KEY=...
  2) Start the stack                    ->  docker compose up -d
  3) Open the UIs:
       OpenHands  ->  http://localhost:${OH_PORT}
       Headroom   ->  http://localhost:${HR_PORT}
  4) Tail logs                          ->  docker compose logs -f
EOF
