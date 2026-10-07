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
#   5. The pytest leg runs $VERI_VENV/bin/python3 when it is present, else the python3 on PATH.
#   6. `make install-dev` creates the environment at $VERI_VENV, else at ~/.veri-tools/venv.
#   7. A suite whose nested `make test` would re-run itself ends within a deadline.
#   8. A suite's nested `make test TESTS=<x>` runs only <x>, when the outer one was given SUITES=.
#   9. ... and when the outer one ran with a MAKEFLAGS in its environment carrying SUITES= or TESTS=.
#  10. A make test nested deeper than a fixed bound refuses with exit 2 and a stderr line naming
#      the depth, before running any suite.
#  11. A commit a suite makes in a repository whose own config forces auto maintenance on, in
#      the foreground, leaves its loose objects where they are.
#  12. The same commit made outside the recipe's environment repacks them.
#  13. A suite run by make test or make unit sees neither BASH_ENV nor ENV the caller exported.
#  14. A suite that sets BASH_ENV itself still has it: a bash child it starts sources that file.
#  15. A suite run through run-suite.sh reads maintenance.auto=false from its git config, as it
#      does under make test.
#
# Run: skills/tdd/scripts/tests/make-test-env.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
source "$HERE/../lib/background.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

FIXTURE='skills/tdd/scripts/tests/fixtures/make-test-env/reports-env.test.sh'

work="$(scratch_dir)"
on_exit 'exec 3>&- 2>/dev/null'
probe="$work/probe"


flat() { printf '%s' "$1" | tr '\n' '/'; }

make_args=()

recipe() {
  local in="$1"; shift
  rm -f "$probe"
  recipe_out="$(env "$@" PROBE_OUT="$probe" make -C "$ROOT" test TESTS="$FIXTURE" UNIT_TESTS= "${make_args[@]}" 2>&1 < "$in")" &&
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
startup="$work/startup.sh"
printf ':\n' > "$startup"
recipe /dev/null BASH_ENV="$startup" ENV="$startup"
expect BASH_ENV "<unset>" "make test passed the caller's BASH_ENV through, so every bash a suite starts re-reads the caller's startup file"
expect ENV "<unset>" "make test passed the caller's ENV through, the POSIX-sh counterpart of BASH_ENV"
rm -f "$probe"
unit_out="$(env BASH_ENV="$startup" ENV="$startup" PROBE_OUT="$probe" \
  make -C "$ROOT" unit UNIT_TESTS="$FIXTURE" 2>&1 < /dev/null)" || problems+=("make unit over the fixture failed: $(flat "$unit_out")")
[[ -s "$probe" ]] || problems+=("make unit wrote no fixture report, so the recipe never ran it: $(flat "$unit_out")")
expect BASH_ENV "<unset>" "make unit passed the caller's BASH_ENV through"
expect ENV "<unset>" "make unit passed the caller's ENV through"
report "#949: a suite run by make test or make unit sees neither BASH_ENV nor ENV, even when the caller exported both"

problems=()
recipe /dev/null BASH_ENV="$startup" ENV="$startup"
expect OWN_BASH_ENV sourced "a bash child the suite started with its own BASH_ENV did not source that file"
report "#949: a suite run by make test that sets BASH_ENV itself for one case still has it: a bash child it starts with its own BASH_ENV sources that file"

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

problems=()
venv="$work/venv"
path_py="$work/path-py"
mkdir -p "$venv/bin" "$path_py"
printf '#!/bin/sh\necho "venv python3 $*"\n' > "$venv/bin/python3"
printf '#!/bin/sh\ncase "$1" in */veri/*.py) exec "%s" "$@" ;; esac\necho "path python3 $*"\n' "$(command -v python3)" > "$path_py/python3"
chmod +x "$venv/bin/python3" "$path_py/python3"
py_tests=("$ROOT"/skills/tdd/scripts/tests/py/test_*.py)
make_args=(PY_TESTS="${py_tests[0]#"$ROOT/"}")
recipe /dev/null VERI_VENV="$venv" VERI_PYTHON_VERSION=3.12.0 VERI_PYTEST_IMPORTABLE=1 PATH="$path_py:$PATH"
[[ "$recipe_out" == *"venv python3 -m pytest skills/tdd/scripts/tests/py/test_"* ]] ||
  problems+=("want \$VERI_VENV/bin/python3 to run the pytest leg when it is present, got: $(flat "$recipe_out")")
recipe /dev/null VERI_VENV="$work/no-venv" VERI_PYTHON_VERSION=3.12.0 VERI_PYTEST_IMPORTABLE=1 PATH="$path_py:$PATH"
[[ "$recipe_out" == *"path python3 -m pytest skills/tdd/scripts/tests/py/test_"* ]] ||
  problems+=("want the python3 on PATH to run the pytest leg when \$VERI_VENV/bin/python3 is absent, got: $(flat "$recipe_out")")
make_args=()
report "make test's pytest leg runs \$VERI_VENV/bin/python3 when it is present and the python3 on PATH when it is absent"

problems=()
venv_maker="$work/venv-maker"
mkdir -p "$venv_maker"
cat > "$venv_maker/python3" <<'SH'
#!/bin/sh
if [ "$1" = -m ] && [ "$2" = venv ]; then
  mkdir -p "$3/bin"
  printf '#!/bin/sh\nexit 0\n' > "$3/bin/python3"
  chmod +x "$3/bin/python3"
fi
SH
chmod +x "$venv_maker/python3"
install_out="$(env VERI_VENV="$work/set-venv" HOME="$work/home-set" PATH="$venv_maker:$PATH" \
  make --no-print-directory -C "$ROOT" install-dev 2>&1 < /dev/null)"
[[ -x "$work/set-venv/bin/python3" && ! -e "$work/home-set/.veri-tools/venv" ]] ||
  problems+=("VERI_VENV set: want the environment created at \$VERI_VENV and nothing under \$HOME/.veri-tools/venv, got: $(flat "$install_out")")
install_out="$(env -u VERI_VENV HOME="$work/home-unset" PATH="$venv_maker:$PATH" \
  make --no-print-directory -C "$ROOT" install-dev 2>&1 < /dev/null)"
[[ -x "$work/home-unset/.veri-tools/venv/bin/python3" ]] ||
  problems+=("VERI_VENV unset: want the environment created at \$HOME/.veri-tools/venv, got: $(flat "$install_out")")
report "make install-dev creates the environment at \$VERI_VENV, or at ~/.veri-tools/venv when VERI_VENV is unset"


problems=()
tree="$(scratch_dir)"
mkdir -p "$tree/skills/tdd/scripts/lib" "$tree/skills/tdd/scripts/tests"
cp "$ROOT/Makefile" "$tree/Makefile"
cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$tree/skills/tdd/scripts/lib/"
cp "$ROOT/skills/tdd/scripts/run-suite.sh" "$tree/skills/tdd/scripts/"
cp -R "$ROOT/skills/tdd/scripts/veri" "$tree/skills/tdd/scripts/"
cp -R "$ROOT/skills/tdd/scripts/tests/offline" "$ROOT/skills/tdd/scripts/tests/unit-guard" "$tree/skills/tdd/scripts/tests/"
cat > "$tree/skills/tdd/scripts/tests/reenters.test.sh" <<'SH'
#!/usr/bin/env bash
make -C "$(cd "$(dirname "$0")/../../../.." && pwd)" test TESTS=skills/tdd/scripts/tests/inner.test.sh UNIT_TESTS=
echo "1 passed, 0 failed"
SH
printf '#!/bin/sh\necho "1 passed, 0 failed"\n' > "$tree/skills/tdd/scripts/tests/inner.test.sh"
chmod +x "$tree/skills/tdd/scripts/tests/reenters.test.sh" "$tree/skills/tdd/scripts/tests/inner.test.sh"
cap=$(( $(ps -U "$(id -u)" -o pid= | wc -l) + 500 ))
deadline=8
done_file="$work/reentry.exit"
bg_start "$work/reentry.pid" env -u MAKEFLAGS -u MAKELEVEL -u MFLAGS bash -c '
  ulimit -u "$1" || exit 2
  shift
  exec python3 -c "import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])" \
    sh -c "\"\$@\"; echo \$? > \"\$0\"" "$@"
' _ "$cap" "$done_file" make -C "$tree" test SUITES=skills/tdd/scripts/tests/reenters.test.sh \
  > "$work/reentry.out" 2>&1 < /dev/null
read -r reentry_pid _ < "$work/reentry.pid"
start=$SECONDS
while [[ ! -s "$done_file" ]] && (( SECONDS - start < deadline )); do sleep 0.1; done
if [[ ! -s "$done_file" ]]; then
  kill -KILL -- "-$reentry_pid" 2>/dev/null || kill -KILL "$reentry_pid" 2>/dev/null
  problems+=("make test SUITES=<a suite whose nested make test names another> was still running at the ${deadline} s deadline, and its process group was killed: $(flat "$(tail -n 5 "$work/reentry.out")")")
fi
wait "$reentry_pid" 2>/dev/null
grep -F 'Resource temporarily unavailable' "$work/reentry.out" > /dev/null &&
  problems+=("the planted re-entry ended only because it ran out of processes: $(flat "$(tail -n 5 "$work/reentry.out")")")
report "a planted re-entry through make test SUITES=… ends with a refusal or a bounded run, not a growing process tree (#816)"

problems=()
cat > "$tree/skills/tdd/scripts/tests/runs-inner.test.sh" <<'SH'
#!/usr/bin/env bash
root="$(cd "$(dirname "$0")/../../../.." && pwd)"
if mkdir "$root/nested-ran" 2>/dev/null; then
  make -C "$root" test TESTS=skills/tdd/scripts/tests/inner.test.sh UNIT_TESTS= > "$root/nested.out" 2>&1
fi
echo "1 passed, 0 failed"
SH
chmod +x "$tree/skills/tdd/scripts/tests/runs-inner.test.sh"
outer_out="$(env -u MAKEFLAGS -u MAKELEVEL -u MFLAGS \
  make -C "$tree" test SUITES=skills/tdd/scripts/tests/runs-inner.test.sh 2>&1 < /dev/null)"
nested_ran="$(sed -n 's/^== //p' "$tree/nested.out" 2>/dev/null)"
[[ "$nested_ran" == inner.test.sh ]] ||
  problems+=("the nested make test TESTS=inner.test.sh ran [$(flat "$nested_ran")], want only [inner.test.sh]: $(flat "$outer_out")")
report "a suite's nested make test TESTS=<x> runs only <x> when the outer make test was given SUITES= (#816)"

problems=()
for carried in SUITES TESTS; do
  rm -rf "$tree/nested-ran" "$tree/nested.out"
  outer_out="$(env -u MAKEFLAGS -u MAKELEVEL -u MFLAGS MAKEFLAGS="$carried=skills/tdd/scripts/tests/runs-inner.test.sh" \
    make -C "$tree" test 2>&1 < /dev/null)"
  nested_ran="$(sed -n 's/^== //p' "$tree/nested.out" 2>/dev/null)"
  [[ "$nested_ran" == inner.test.sh ]] ||
    problems+=("MAKEFLAGS=$carried=…: the nested make test TESTS=inner.test.sh ran [$(flat "$nested_ran")], want only [inner.test.sh]: $(flat "$outer_out")")
done
report "a suite's nested make test TESTS=<x> runs only <x> when the outer make test ran with MAKEFLAGS carrying SUITES= or TESTS= (#816)"

problems=()
cat > "$tree/skills/tdd/scripts/tests/self.test.sh" <<'SH'
#!/usr/bin/env bash
root="$(cd "$(dirname "$0")/../../../.." && pwd)"
mkdir -p "$root/self"
make -C "$root" test TESTS=skills/tdd/scripts/tests/self.test.sh UNIT_TESTS= \
  > "$root/self/$$.out" 2> "$root/self/$$.err"
echo $? > "$root/self/$$.code"
echo "1 passed, 0 failed"
SH
chmod +x "$tree/skills/tdd/scripts/tests/self.test.sh"
done_file="$work/depth.exit"
bg_start "$work/depth.pid" env -u MAKEFLAGS -u MAKELEVEL -u MFLAGS bash -c '
  ulimit -u "$1" || exit 2
  shift
  exec python3 -c "import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])" \
    sh -c "\"\$@\"; echo \$? > \"\$0\"" "$@"
' _ "$cap" "$done_file" make -C "$tree" test TESTS=skills/tdd/scripts/tests/self.test.sh UNIT_TESTS= \
  > "$work/depth.out" 2>&1 < /dev/null
read -r depth_pid _ < "$work/depth.pid"
start=$SECONDS
while [[ ! -s "$done_file" ]] && (( SECONDS - start < deadline )); do sleep 0.1; done
if [[ ! -s "$done_file" ]]; then
  kill -KILL -- "-$depth_pid" 2>/dev/null || kill -KILL "$depth_pid" 2>/dev/null
  problems+=("make test TESTS=<a suite whose nested make test names itself> was still running at the ${deadline} s deadline, and its process group was killed")
fi
wait "$depth_pid" 2>/dev/null
refused=""
for code in "$tree"/self/*.code; do
  [[ "$(cat "$code" 2>/dev/null)" == 2 ]] || continue
  level="${code%.code}"
  grep -i 'depth' "$level.err" | grep '[0-9]' > /dev/null || continue
  grep '^== ' "$level.out" > /dev/null &&
    problems+=("the make test that refused at depth still ran a suite: $(flat "$(cat "$level.out")")")
  refused="$level"
done
[[ -n "$refused" ]] ||
  problems+=("no nested make test exited 2 with a stderr line naming the depth; nested exits [$(flat "$(cat "$tree"/self/*.code 2>/dev/null)")]: $(flat "$(tail -n 5 "$work/depth.out")")")
report "a make test nested deeper than a fixed bound refuses with exit 2 and a stderr line naming the depth, before running any suite (#816)"

problems=()
forced="$work/forced-maintenance"
new_repo "$forced"
git -C "$forced" config gc.auto 1
git -C "$forced" config gc.autoDetach false
git -C "$forced" config maintenance.autoDetach false
git -C "$forced" config maintenance.geometric-repack.auto -1
for i in $(seq 1 600); do echo "$i" > "$forced/f$i"; done
git -C "$forced" add -A
fanout_before="$(find "$forced/.git/objects" -mindepth 1 -maxdepth 1 -name '[0-9a-f][0-9a-f]' | wc -l | tr -d ' ')"
recipe /dev/null COMMIT_REPO="$forced"
fanout_after="$(find "$forced/.git/objects" -mindepth 1 -maxdepth 1 -name '[0-9a-f][0-9a-f]' | wc -l | tr -d ' ')"
packs="$(find "$forced/.git/objects/pack" -name '*.pack' | wc -l | tr -d ' ')"
[[ "$fanout_after" -ge "$fanout_before" && "$fanout_before" -gt 0 ]] ||
  problems+=("the commit left $fanout_after of $fanout_before objects/<xx> fan-out directories — git's auto maintenance repacked the suite's scratch repo")
[[ "$packs" -eq 0 ]] ||
  problems+=("the commit wrote $packs pack(s) into the suite's scratch repo, want 0 — auto maintenance ran")
report "under make test, a commit in a scratch repo whose own config forces foreground auto maintenance leaves its loose objects in place (#862)"

problems=()
unguarded="$work/unguarded-maintenance"
new_repo "$unguarded"
git -C "$unguarded" config gc.auto 1
git -C "$unguarded" config gc.autoDetach false
git -C "$unguarded" config maintenance.autoDetach false
git -C "$unguarded" config maintenance.geometric-repack.auto -1
for i in $(seq 1 600); do echo "$i" > "$unguarded/f$i"; done
git -C "$unguarded" add -A
env -u GIT_CONFIG_COUNT git -C "$unguarded" commit -qm forced
fanout_after="$(find "$unguarded/.git/objects" -mindepth 1 -maxdepth 1 -name '[0-9a-f][0-9a-f]' | wc -l | tr -d ' ')"
packs="$(find "$unguarded/.git/objects/pack" -name '*.pack' | wc -l | tr -d ' ')"
[[ "$fanout_after" -eq 0 ]] ||
  problems+=("outside the recipe the forced commit left $fanout_after objects/<xx> fan-out directories, want 0 — $(git --version) did not repack, so the hazard the recipe removes was not shown real")
[[ "$packs" -gt 0 ]] ||
  problems+=("outside the recipe the forced commit wrote no pack — $(git --version) ran no auto maintenance")
report "outside make test's environment, the same forced commit repacks the scratch repo's loose objects, so the hazard is real on this git (#862)"

problems=()
planted="$work/reads-maintenance.test.sh"
cat > "$planted" <<'SH'
#!/bin/sh
git config --get maintenance.auto > "$PROBE_OUT"
echo "1 passed, 0 failed"
SH
chmod +x "$planted"
rm -f "$probe"
runner_out="$(cd "$work" && env -u GIT_CONFIG_COUNT -u GIT_CONFIG_KEY_3 -u GIT_CONFIG_VALUE_3 \
  GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 PROBE_OUT="$probe" \
  "$ROOT/skills/tdd/scripts/run-suite.sh" "$planted" 2>&1 < /dev/null)"
got="$(cat "$probe" 2>/dev/null)"
[[ "$got" == false ]] ||
  problems+=("a suite run through run-suite.sh saw maintenance.auto=${got:-<nothing>}, want false, as under make test: $(flat "$runner_out")")
report "a suite run through run-suite.sh reads maintenance.auto=false from its git config, as it does under make test"

finish
