#!/usr/bin/env bash
# ==============================================================================
# Test script for push_to_github.sh hardening
# ==============================================================================
# Note: Not using set -e so test failures don't exit the script
set -uo pipefail

TEST_ROOT="/tmp/git_push_test_$$"
BARE_REPO="$TEST_ROOT/bare_remote.git"
WORK_DIR="$TEST_ROOT/working_copy"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log()  { printf "${CYAN}[TEST]${NC} %s\n" "$*"; }
ok()   { printf "${GREEN}[PASS]${NC} %s\n" "$*"; }
fail() { printf "${RED}[FAIL]${NC} %s\n" "$*" >&2; }
warn() { printf "${YELLOW}[WARN]${NC} %s\n" "$*"; }

cleanup() {
  log "Cleaning up test directory: $TEST_ROOT"
  rm -rf "$TEST_ROOT"
}
# Removed trap - will cleanup manually at end

# ==============================================================================
# TEST 1: Verify init.sh is staged and pushed correctly
# ==============================================================================
test_init_sh_pushed() {
  log "TEST 1: Verify init.sh is staged and pushed"
  
  # Setup
  mkdir -p "$TEST_ROOT"
  git init --bare -q "$BARE_REPO"
  mkdir -p "$WORK_DIR"
  # Copy all files including hidden ones
  cp -r /app/deliverables/. "$WORK_DIR/"
  cd "$WORK_DIR"
  
  # Run init.sh
  log "Running init.sh..."
  bash ./init.sh > /dev/null 2>&1 || true
  
  # Run push_to_github.sh
  log "Running push_to_github.sh..."
  if bash ./push_to_github.sh "$BARE_REPO" > /dev/null 2>&1; then
    log "push_to_github.sh completed successfully"
  else
    fail "push_to_github.sh failed"
    return 1
  fi
  
  # Verify init.sh is in the pushed tree
  log "Checking if init.sh is in the pushed tree..."
  if git --git-dir="$BARE_REPO" ls-tree --name-only main | grep -x "init.sh" > /dev/null; then
    ok "init.sh is present in the pushed tree"
    return 0
  else
    fail "init.sh is NOT in the pushed tree"
    git --git-dir="$BARE_REPO" ls-tree --name-only main
    return 1
  fi
}

# ==============================================================================
# TEST 2: Verify .gitignore does NOT ignore init.sh
# ==============================================================================
test_gitignore_allows_init_sh() {
  log "TEST 2: Verify .gitignore does NOT ignore init.sh"
  
  cd "$WORK_DIR"
  
  # git check-ignore returns 0 if file IS ignored, non-zero if NOT ignored
  if git check-ignore -v init.sh > /dev/null 2>&1; then
    fail "init.sh is IGNORED by .gitignore (should NOT be)"
    git check-ignore -v init.sh
    return 1
  else
    ok "init.sh is NOT ignored by .gitignore"
    return 0
  fi
}

# ==============================================================================
# TEST 3: Verify safety guard - script aborts if init.sh is missing
# ==============================================================================
test_safety_guard_missing_init_sh() {
  log "TEST 3: Verify safety guard when init.sh is missing"
  
  # Create fresh test environment
  GUARD_TEST_DIR="$TEST_ROOT/guard_test"
  GUARD_BARE="$TEST_ROOT/guard_bare.git"
  git init --bare -q "$GUARD_BARE"
  mkdir -p "$GUARD_TEST_DIR"
  # Copy all files including hidden ones
  cp -r /app/deliverables/. "$GUARD_TEST_DIR/"
  cd "$GUARD_TEST_DIR"
  
  # Remove init.sh
  log "Removing init.sh to trigger safety guard..."
  rm -f init.sh
  
  # Run push_to_github.sh and capture output and exit code
  log "Running push_to_github.sh (should abort)..."
  set +e
  output=$(bash ./push_to_github.sh "$GUARD_BARE" 2>&1)
  exit_code=$?
  set -e
  
  log "Exit code: $exit_code"
  log "Output: $output"
  
  # Verify script aborted (non-zero exit)
  if [[ $exit_code -ne 0 ]]; then
    ok "Script aborted with non-zero exit code ($exit_code)"
  else
    fail "Script did NOT abort (exit code: $exit_code)"
    return 1
  fi
  
  # Verify error message mentions init.sh
  if echo "$output" | grep -i "init.sh" > /dev/null; then
    ok "Error message mentions init.sh"
  else
    fail "Error message does NOT mention init.sh"
    echo "Output was: $output"
    return 1
  fi
  
  # Verify nothing was pushed
  if git --git-dir="$GUARD_BARE" rev-parse main > /dev/null 2>&1; then
    fail "Branch 'main' exists in remote (should NOT have been pushed)"
    return 1
  else
    ok "Nothing was pushed to remote (as expected)"
  fi
  
  return 0
}

# ==============================================================================
# TEST 4: Verify secret safety - .env NOT pushed, .env.example IS pushed
# ==============================================================================
test_secret_safety() {
  log "TEST 4: Verify secret safety (.env vs .env.example)"
  
  cd "$WORK_DIR"
  
  # Check .env is NOT in the tree
  if git --git-dir="$BARE_REPO" ls-tree --name-only main | grep -x ".env" > /dev/null; then
    fail ".env is present in the pushed tree (SECURITY ISSUE)"
    return 1
  else
    ok ".env is NOT in the pushed tree (secure)"
  fi
  
  # Check .env.example IS in the tree
  if git --git-dir="$BARE_REPO" ls-tree --name-only main | grep -x ".env.example" > /dev/null; then
    ok ".env.example is present in the pushed tree"
    return 0
  else
    fail ".env.example is NOT in the pushed tree"
    return 1
  fi
}

# ==============================================================================
# TEST 5: Verify commit message
# ==============================================================================
test_commit_message() {
  log "TEST 5: Verify commit message"
  
  expected_msg="feat: initial OpenHands + Headroom Docker stack"
  actual_msg=$(git --git-dir="$BARE_REPO" log --format=%s -n 1 main)
  
  log "Expected: '$expected_msg'"
  log "Actual:   '$actual_msg'"
  
  if [[ "$actual_msg" == "$expected_msg" ]]; then
    ok "Commit message is correct"
    return 0
  else
    fail "Commit message mismatch"
    return 1
  fi
}

# ==============================================================================
# Run all tests
# ==============================================================================
main() {
  log "Starting push_to_github.sh test suite"
  log "Test root: $TEST_ROOT"
  echo ""
  
  PASSED=0
  FAILED=0
  
  # Test 1
  if test_init_sh_pushed; then
    ((PASSED++))
  else
    ((FAILED++))
  fi
  echo ""
  
  # Test 2
  if test_gitignore_allows_init_sh; then
    ((PASSED++))
  else
    ((FAILED++))
  fi
  echo ""
  
  # Test 3
  if test_safety_guard_missing_init_sh; then
    ((PASSED++))
  else
    ((FAILED++))
  fi
  echo ""
  
  # Test 4
  if test_secret_safety; then
    ((PASSED++))
  else
    ((FAILED++))
  fi
  echo ""
  
  # Test 5
  if test_commit_message; then
    ((PASSED++))
  else
    ((FAILED++))
  fi
  echo ""
  
  # Summary
  log "=========================================="
  log "Test Summary"
  log "=========================================="
  ok "Passed: $PASSED"
  if [[ $FAILED -gt 0 ]]; then
    fail "Failed: $FAILED"
    return 1
  else
    log "Failed: $FAILED"
  fi
  log "=========================================="
  
  if [[ $FAILED -eq 0 ]]; then
    ok "All tests passed!"
    cleanup
    return 0
  else
    fail "Some tests failed"
    cleanup
    return 1
  fi
}

main
