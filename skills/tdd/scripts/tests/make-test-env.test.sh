#!/usr/bin/env bash
# Unit tests for the environment the `test` recipe in this repository's Makefile gives every
# suite it runs. Like count-line-guard.test.sh this suite has no script as its subject: its
# subject is the runner, and it asks it through fixtures/make-test-env/reports-env.test.sh,
# handed to the real recipe as `make test TESTS=<fixture>`. The fixture writes down what it
# saw; the cases here judge it.
#
# Why this exists: on the development Mac a full `make test` took 393-515 s where CI takes
# 176 s, and two of the causes were the environment the recipe passed straight through
# rather than anything a suite did (measured 2026-09-18, all 76 suites green in every run):
#   - Locale. macOS's BSD awk, tr, grep and sed run ~12x slower over text in a UTF-8 locale:
#     model-knobs-recorded.test.sh took 2.7 s under LC_ALL=C and 33.5 s under en_US.UTF-8,
#     and the terminal the conductors run in sets UTF-8. 121 s of every run went to it.
#   - Git. /usr/bin/git on macOS is xcrun's shim, 30.8 ms a call against 9.6 ms for the git
#     it forwards to, and a run makes ~1,900 git calls. `git` on a suite's PATH is now a
#     symlink straight to the resolved real binary — no xcrun hop, and (since 2026-09-18) no
#     bash wrapper in front of it either, which is what cases 3 and 4 below pin.
# And one hang: a suite inherited whatever stdin `make test` was given. Under a leaf's
# backgrounded `make test` that is a socket that never closes, and the stub claude's
# `cat > "$PROMPT_OUT"` in run-conductor.test.sh blocked on it for 28 minutes.
#
# None of this asserts a duration. The speed-up is a fact about one machine, measured once
# and recorded in the PR that made it; what this suite pins is the environment that produced
# it, which is the same on every machine and so is a thing a test can hold.
#
# Contract under test:
#   1. A suite runs under LC_ALL=C, whatever locale `make test` was invoked in.
#   2. A suite's stdin is /dev/null, whatever stdin `make test` was given.
#   3. `git` on a suite's PATH is a symlink straight to the git `xcrun -f git` names, when
#      xcrun answers,
#   4. and straight to the git `command -v git` names when it does not — the Linux path,
#      which CI runs on. Neither hop goes through a bash wrapper any more (measured
#      2026-09-18: that wrapper cost ~26 ms/call against ~8 ms for the real binary, over
#      ~1,900 calls a run — 1,820 of the run's 4,834 bash starts).
#
# Run: skills/tdd/scripts/tests/make-test-env.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# Repo-relative, because that is what the recipe is handed; the fixture is never run on its
# own, since everything it reports is a fact about the runner.
FIXTURE='skills/tdd/scripts/tests/fixtures/make-test-env/reports-env.test.sh'

work="$(mktemp -d)"
trap 'exec 3>&- 2>/dev/null; rm -rf "$work"' EXIT
probe="$work/probe"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# flat <text> — one line of it, for a failure message.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# recipe <stdin> [<VAR=value>...] — run this repository's `test` recipe over the fixture alone,
# with <stdin> as make's stdin and the assignments added to its environment, and leave the
# fixture's report in `probe`. A recipe that did not pass the fixture is a problem of its own:
# the report of a run that failed is not an answer about the environment.
recipe() {
  local in="$1"; shift
  rm -f "$probe"
  recipe_out="$(env "$@" PROBE_OUT="$probe" make -C "$ROOT" test TESTS="$FIXTURE" 2>&1 < "$in")" &&
    recipe_code=0 || recipe_code=$?
  [[ "$recipe_code" -eq 0 ]] ||
    problems+=("make test over the fixture exited $recipe_code: $(flat "$recipe_out")")
  [[ -s "$probe" ]] ||
    problems+=("the fixture wrote no report, so the recipe never ran it: $(flat "$recipe_out")")
}

# saw <key> — the value the fixture reported for <key>, or nothing.
saw() { sed -n "s/^$1=//p" "$probe" 2>/dev/null; }

# expect <key> <want> <why> — one problem unless the fixture saw <want> for <key>.
expect() {
  local got; got="$(saw "$1")"
  [[ "$got" == "$2" ]] || problems+=("a suite saw $1=${got:-<nothing>}, want $2 — $3")
}

# An xcrun of our own, first on PATH for cases 3 and 4, so what xcrun answers is the case's
# choice rather than the machine's: on Linux there is no xcrun at all, and on a Mac it always
# answers. It names $XCRUN_GIT for `-f git` when that is set and fails otherwise, as xcrun does
# on a machine without developer tools.
stub="$work/bin"
mkdir -p "$stub"
cat > "$stub/xcrun" <<'EOF'
#!/bin/sh
if [ "$1" = -f ] && [ "$2" = git ] && [ -n "${XCRUN_GIT:-}" ]; then echo "$XCRUN_GIT"; exit 0; fi
echo "xcrun: error: unable to find utility \"$2\"" >&2
exit 1
EOF
chmod +x "$stub/xcrun"

# A real (if fake) binary for xcrun to name in case 3: the recipe now symlinks `git` on a
# suite's PATH straight to whatever it resolves as real, and a dangling symlink — one whose
# target does not exist — is invisible to `command -v`, which skips it and keeps searching.
# Naming a path that is not actually there would silently fall through to the real system git
# instead of pinning what the recipe chose.
xcrun_git="$work/xcrun-git/git"
mkdir -p "$(dirname "$xcrun_git")"
printf '#!/bin/sh\necho fake xcrun git\n' > "$xcrun_git"
chmod +x "$xcrun_git"

# 1. The locale. Asked with the caller in the UTF-8 locale a terminal sets, which is the one
#    that made the text-processing suites twelve times slower.
problems=()
recipe /dev/null LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
expect LC_ALL C "the recipe passed the caller's locale through, and BSD text tools run ~12x slower in UTF-8"
report "make test runs every suite under LC_ALL=C, whatever locale it was invoked in"

# 2. stdin. Asked with make's stdin a pipe that is open and will never be written to or closed:
#    fd 3 holds the FIFO open for writing, so a reader gets neither data nor end-of-file — the
#    shape of the socket a backgrounded command gets. The fixture only compares, so a red here
#    reports rather than hangs.
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

# 3. xcrun answers. OFFLINE_REAL_GIT is cleared because a suite running under `make test`
#    inherits the outer run's value, and the recipe keeps an inherited one on purpose (a nested
#    run must not re-resolve real git through its own, already-shadowed PATH); cleared, the
#    recipe has to resolve it. GIT_LINK_TARGET is the immediate target of the `git` symlink the
#    recipe puts on PATH — the fixture's own `command -v git` finds that symlink, not a bash
#    wrapper, so `readlink` names the real binary the recipe resolved rather than a shim it
#    forwards to.
problems=()
recipe /dev/null -u OFFLINE_REAL_GIT PATH="$stub:$PATH" XCRUN_GIT="$xcrun_git"
expect OFFLINE_REAL_GIT "$xcrun_git" \
  "the git symlink on PATH points at the git xcrun names, which on a Mac is xcrun's shim at ~21 ms a call on top"
expect GIT_LINK_TARGET "$xcrun_git" \
  "the git symlink on a suite's PATH should point straight at the same binary OFFLINE_REAL_GIT names, with no wrapper in between"
report "make test's git symlink points at the git xcrun names, when xcrun answers"

# 4. xcrun does not answer — the machine CI runs on. The expected value is computed under the
#    same PATH the recipe gets, so the case asks what the recipe chose, not what this machine has.
problems=()
want_git="$(PATH="$stub:$PATH" command -v git)"
recipe /dev/null -u OFFLINE_REAL_GIT PATH="$stub:$PATH"
expect OFFLINE_REAL_GIT "$want_git" "with no xcrun to ask, the git symlink points at the git on PATH, the real one"
expect GIT_LINK_TARGET "$want_git" \
  "the git symlink on a suite's PATH should point straight at the same binary OFFLINE_REAL_GIT names, with no wrapper in between"
report "make test's git symlink points at the git on PATH, when xcrun does not answer"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
