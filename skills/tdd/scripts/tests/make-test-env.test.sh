#!/usr/bin/env bash
# Unit tests for the environment the Makefile's `test` recipe gives every suite it runs,
# observed through fixtures/make-test-env/reports-env.test.sh handed to `make test TESTS=…`.
#
# Contract under test:
#   1. A suite runs under LC_ALL=C, whatever locale `make test` was invoked in.
#   2. A suite's stdin is /dev/null, whatever stdin `make test` was given.
#   3. `git` on a suite's PATH is a symlink straight to the git `xcrun -f git` names, when
#      xcrun answers,
#   4. and straight to the git `command -v git` names when it does not.
#
# Run: skills/tdd/scripts/tests/make-test-env.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

FIXTURE='skills/tdd/scripts/tests/fixtures/make-test-env/reports-env.test.sh'

work="$(scratch_dir)"
on_exit 'exec 3>&- 2>/dev/null'
probe="$work/probe"


flat() { printf '%s' "$1" | tr '\n' '/'; }

recipe() {
  local in="$1"; shift
  rm -f "$probe"
  recipe_out="$(env "$@" PROBE_OUT="$probe" make -C "$ROOT" test TESTS="$FIXTURE" UNIT_TESTS= 2>&1 < "$in")" &&
    recipe_code=0 || recipe_code=$?
  [[ "$recipe_code" -eq 0 ]] ||
    problems+=("make test over the fixture exited $recipe_code: $(flat "$recipe_out")")
  [[ -s "$probe" ]] ||
    problems+=("the fixture wrote no report, so the recipe never ran it: $(flat "$recipe_out")")
}

saw() { sed -n "s/^$1=//p" "$probe" 2>/dev/null; }

expect() {
  local got; got="$(saw "$1")"
  [[ "$got" == "$2" ]] || problems+=("a suite saw $1=${got:-<nothing>}, want $2 — $3")
}

fake_git_with_exec_path() {
  mkdir -p "$(dirname "$1")"
  printf '#!/bin/sh\n[ "$1" = --exec-path ] && echo "%s"\n' "$work/fake-libexec" > "$1"
  chmod +x "$1"
}

stub="$work/bin"
mkdir -p "$stub"
cat > "$stub/xcrun" <<'EOF'
#!/bin/sh
if [ "$1" = -f ] && [ "$2" = git ] && [ -n "${XCRUN_GIT:-}" ]; then echo "$XCRUN_GIT"; exit 0; fi
echo "xcrun: error: unable to find utility \"$2\"" >&2
exit 1
EOF
chmod +x "$stub/xcrun"

xcrun_git="$work/xcrun-git/git"
mkdir -p "$(dirname "$xcrun_git")"
printf '#!/bin/sh\necho fake xcrun git\n' > "$xcrun_git"
chmod +x "$xcrun_git"

problems=()
recipe /dev/null LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
expect LC_ALL C "the recipe passed the caller's locale through, and BSD text tools run ~12x slower in UTF-8"
report "make test runs every suite under LC_ALL=C, whatever locale it was invoked in"

problems=()
fifo="$work/stdin"
if mkfifo "$fifo" && exec 3<>"$fifo"; then
  recipe "$fifo"
  expect stdin devnull "a suite inherited make's stdin, and a stub reading it to end-of-file waits for ever"
  exec 3>&-
else
  problems+=("could not hold a FIFO open to hand make as stdin, so the case went unasked")
fi
report "make test gives every suite /dev/null as stdin, whatever stdin it was given"

problems=()
recipe /dev/null -u OFFLINE_REAL_GIT PATH="$stub:$PATH" XCRUN_GIT="$xcrun_git"
expect OFFLINE_REAL_GIT "$xcrun_git" \
  "the git symlink on PATH points at the git xcrun names, which on a Mac is xcrun's shim at ~21 ms a call on top"
expect GIT_LINK_TARGET "$xcrun_git" \
  "the git symlink on a suite's PATH should point straight at the same binary OFFLINE_REAL_GIT names, with no wrapper in between"
report "make test's git symlink points at the git xcrun names, when xcrun answers"

problems=()
want_git="$(PATH="$stub:$PATH" command -v git)"
recipe /dev/null -u OFFLINE_REAL_GIT PATH="$stub:$PATH"
expect OFFLINE_REAL_GIT "$want_git" "with no xcrun to ask, the git symlink points at the git on PATH, the real one"
expect GIT_LINK_TARGET "$want_git" \
  "the git symlink on a suite's PATH should point straight at the same binary OFFLINE_REAL_GIT names, with no wrapper in between"
report "make test's git symlink points at the git on PATH, when xcrun does not answer"

problems=()
exec_git="$work/exec-git/git"
fake_git_with_exec_path "$exec_git"
recipe /dev/null -u OFFLINE_REAL_GIT -u GIT_EXEC_PATH PATH="$stub:$PATH" XCRUN_GIT="$exec_git"
expect GIT_EXEC_PATH "$work/fake-libexec" \
  "git run through the symlink derives its prefix from the symlink's directory and names a libexec that does not exist"
report "make test gives every suite the GIT_EXEC_PATH the real git reports at its own path (#582)"

problems=()
tmpl_git="$work/tmpl-git/bin/git"
fake_git_with_exec_path "$tmpl_git"
mkdir -p "$work/tmpl-git/share/git-core/templates"
recipe /dev/null -u OFFLINE_REAL_GIT -u GIT_TEMPLATE_DIR PATH="$stub:$PATH" XCRUN_GIT="$tmpl_git"
got_templates="$(saw GIT_TEMPLATE_DIR)"
got_resolved="$(cd "$got_templates" 2>/dev/null && pwd -P)"
want_resolved="$(cd "$work/tmpl-git/share/git-core/templates" && pwd -P)"
[[ "$got_resolved" == "$want_resolved" ]] ||
  problems+=("a suite saw GIT_TEMPLATE_DIR=${got_templates:-<nothing>}, want the templates directory beside the real git ($want_resolved) — git run through the symlink looks for templates under a prefix that does not exist")
rm -rf "$work/tmpl-git/share"
recipe /dev/null -u OFFLINE_REAL_GIT GIT_TEMPLATE_DIR="$work/ambient-templates" PATH="$stub:$PATH" XCRUN_GIT="$tmpl_git"
expect GIT_TEMPLATE_DIR "<unset>" "with no templates directory beside the real git, the recipe must leave GIT_TEMPLATE_DIR unset"
report "make test gives every suite a GIT_TEMPLATE_DIR beside the real git when that directory exists, and none when it does not (#582)"

problems=()
recipe /dev/null
unit_listed=""
for unit_suite in "$HERE"/unit/*.test.sh; do
  printf '%s\n' "$recipe_out" | grep -Fx "== $(basename "$unit_suite")" > /dev/null &&
    unit_listed+="$(basename "$unit_suite") "
done
[[ -z "$unit_listed" ]] ||
  problems+=("the nested make test over the fixture also ran suites from tests/unit/: $(flat "$unit_listed")")
report "the nested make test over the fixture runs only the fixture, no suite from tests/unit/"

finish
