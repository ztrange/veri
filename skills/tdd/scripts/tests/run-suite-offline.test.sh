#!/usr/bin/env bash
# Unit tests for run-suite.sh's environment.
#
# Contract under test:
#   run-suite.sh runs a suite under make test's offline git: a case that starts `git fetch`
#   against an unreachable https origin is refused by git's transport allowlist.
#
# Run: skills/tdd/scripts/tests/run-suite-offline.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
source "$HERE/lib/harness.sh"

RUNNER="$ROOT/skills/tdd/scripts/run-suite.sh"

name="run-suite.sh refuses a suite's git fetch against an unreachable https origin by the transport allowlist, as make test does (#1468)"
problems=()

probe_runner_applies_offline_git() {
  local tree out code
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory, so the question went unasked")
    return 1
  }
  new_repo "$tree/repo" && git -C "$tree/repo" remote add origin https://127.0.0.1:9/nowhere.git || {
    problems+=("could not make the repository the suite fetches from, so the question went unasked")
    return 1
  }
  cat > "$tree/fetches.test.sh" <<'SUITE'
#!/usr/bin/env bash
set -uo pipefail
err="$(git -C "$FETCH_REPO" fetch origin 2>&1)"
if [[ "$err" == *"transport 'https' not allowed"* ]]; then
  echo "1 passed, 0 failed"
else
  echo "FAIL - fetch was not refused by the allowlist: $err"
  echo "0 passed, 1 failed"
  exit 1
fi
SUITE
  chmod +x "$tree/fetches.test.sh"
  out="$(env -u GIT_CONFIG_KEY_0 -u GIT_CONFIG_VALUE_0 -u GIT_CONFIG_KEY_1 -u GIT_CONFIG_VALUE_1 \
    -u GIT_CONFIG_KEY_2 -u GIT_CONFIG_VALUE_2 -u GIT_CONFIG_KEY_3 -u GIT_CONFIG_VALUE_3 \
    GIT_CONFIG_COUNT=0 FETCH_REPO="$tree/repo" "$RUNNER" "$tree/fetches.test.sh" 2>&1 < /dev/null)" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("want exit 0, the allowlist refusing the fetch under the runner; it exited $code and said: $(printf '%s' "$out" | tr '\n' '/')")
}

probe_runner_applies_offline_git

report "$name"

name="run-suite.sh gives a suite make test's dead HTTP and HTTPS proxy with NO_PROXY=127.0.0.1,localhost (#1468)"
problems=()

probe_runner_applies_dead_proxy() {
  local tree out code
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory, so the question went unasked")
    return 1
  }
  cat > "$tree/proxies.test.sh" <<'SUITE'
#!/usr/bin/env bash
set -uo pipefail
echo "HTTP_PROXY=${HTTP_PROXY-unset} HTTPS_PROXY=${HTTPS_PROXY-unset} NO_PROXY=${NO_PROXY-unset}"
echo "1 passed, 0 failed"
SUITE
  chmod +x "$tree/proxies.test.sh"
  out="$(env -u HTTP_PROXY -u HTTPS_PROXY -u NO_PROXY -u http_proxy -u https_proxy -u no_proxy \
    "$RUNNER" "$tree/proxies.test.sh" 2>&1 < /dev/null)" && code=0 || code=$?
  expect_eq "the suite's proxy environment under the runner" \
    "HTTP_PROXY=http://127.0.0.1:1 HTTPS_PROXY=http://127.0.0.1:1 NO_PROXY=127.0.0.1,localhost" \
    "$(printf '%s\n' "$out" | head -n 1)"
}

probe_runner_applies_dead_proxy

report "$name"

finish
