#!/usr/bin/env bash
# A fixture, not a suite: only make-test-env.test.sh runs it, as `make test TESTS=<this>`.
# Writes one `key=value` line each to $PROBE_OUT for the locale, OFFLINE_REAL_GIT, the target
# of the `git` symlink on PATH, the GIT_EXEC_PATH and GIT_TEMPLATE_DIR it was given and
# whether stdin is /dev/null, and whether a bash child it starts with its own BASH_ENV sources
# that file, then reports a pass. With $COMMIT_REPO set, first commits what
# that repository has staged.
set -uo pipefail

out="${PROBE_OUT:?PROBE_OUT names the file this fixture reports to}"
[[ -z "${COMMIT_REPO:-}" ]] || git -C "$COMMIT_REPO" commit -qm forced
if [[ /dev/stdin -ef /dev/null ]]; then stdin=devnull; else stdin=inherited; fi
# hazard: BSD and GNU `readlink -f` differ; plain `readlink` names the immediate target.
git_path="$(command -v git 2>/dev/null || echo '<none>')"
git_link_target="$(readlink "$git_path" 2>/dev/null || echo '<not-a-symlink>')"
printf 'export OWN_MARK=sourced\n' > "$out.startup"
own_bash_env="$(BASH_ENV="$out.startup" bash -c 'printf %s "${OWN_MARK-<unset>}"')"
{
  printf 'LC_ALL=%s\n' "${LC_ALL-<unset>}"
  printf 'OFFLINE_REAL_GIT=%s\n' "${OFFLINE_REAL_GIT-<unset>}"
  printf 'GIT_LINK_TARGET=%s\n' "$git_link_target"
  printf 'GIT_EXEC_PATH=%s\n' "${GIT_EXEC_PATH-<unset>}"
  printf 'GIT_TEMPLATE_DIR=%s\n' "${GIT_TEMPLATE_DIR-<unset>}"
  printf 'BASH_ENV=%s\n' "${BASH_ENV-<unset>}"
  printf 'ENV=%s\n' "${ENV-<unset>}"
  printf 'OWN_BASH_ENV=%s\n' "$own_bash_env"
  printf 'stdin=%s\n' "$stdin"
} > "$out"
echo "1 passed, 0 failed"
