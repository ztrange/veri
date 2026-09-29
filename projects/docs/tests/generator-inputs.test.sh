#!/usr/bin/env bash
# Unit test for the two inputs the walkthrough build resolves paths against: the
# SCRIPTS_DIR constant projects/docs/build-walkthrough.py and projects/docs/check-walkthrough.py each spell,
# and the set of scripts projects/docs/wt/commentary.py declares listings for. Like
# commentary-figures.test.sh and suite-lanes.test.sh this suite has no script as its
# subject — it reads three files as text and asserts the page's generator is still pointed
# at the skill it documents. Zero-dependency plain-shell asserts, same idiom as the other
# suites under projects/docs/tests/.
#
# Why this exists (issue #146): this fact was guarded from the development lane, by
# skills/tdd/scripts/tests/skill-identity.test.sh case 3, which put a docs fact inside
# `make test` — the command every veri leaf runs and the conductor reads its baseline off,
# so an edit to the page's generator could stop a TDD cycle on a red the scripts did not
# cause (ADR 0016). The docs lane is where it belongs, and `make docs-test` globs this
# directory, so this suite runs by existing (#137).
#
# Contract under test:
#   Both python entry points resolve script paths against skills/tdd/scripts, and every
#   listing projects/docs/wt/commentary.py declares names a file that is there. Either half broken
#   is a `make docs` that reports "missing script" per listing and emits no page, so the
#   failure names the file, what it says and what it must say.
#
# It is a separate question from "is the committed page fresh" (docs-fresh) and from "do
# the build's guards still fire" (build-guards.test.sh, which judges only trees it builds
# itself). This suite judges neither a page nor a build: it reads the wiring, statically,
# before either can run. That is also why it is cheap — three files, a handful of greps,
# no page build and no question asked of git.
#
# The constant is deliberately checked as the whole assignment line rather than by
# searching for the directory as one string: the python spells it as path COMPONENTS,
# `ROOT / "skills" / "tdd" / "scripts"`, so the joined path "skills/tdd/scripts" never
# appears in either file and a sweep for it would pass over a generator left pointing
# somewhere else entirely.
#
# Run: projects/docs/tests/generator-inputs.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"

# The directory the page documents, written down once: both halves of the case below quote
# it, so a skill rename is one edit here rather than one per probe.
skill_dir="skills/tdd"
COMMENTARY='projects/docs/wt/commentary.py'
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which file drifted rather than just that the case did.
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

# --- the generators read the skill's scripts, and document only scripts that are there ---
name="projects/docs/build-walkthrough.py and projects/docs/check-walkthrough.py read $skill_dir/scripts, and $COMMENTARY documents only scripts that live there"

problems=()
# "skills/tdd/scripts" as python spells it — `"skills" / "tdd" / "scripts"` — derived from
# $skill_dir rather than written out again: quote each path segment, then join on " / ".
py_scripts_dir="$(printf '%s/scripts' "$skill_dir" | sed 's#[^/]*#"&"#g; s#/# / #g')"
for py in projects/docs/build-walkthrough.py projects/docs/check-walkthrough.py; do
  if [[ -f "$ROOT/$py" ]]; then
    # -x so a line that merely mentions the components does not answer for the constant,
    # -F because the expression is a literal, quotes and slashes and all.
    grep -qxF "SCRIPTS_DIR = ROOT / $py_scripts_dir" "$ROOT/$py" ||
      problems+=("$py: want SCRIPTS_DIR = ROOT / $py_scripts_dir, got $(printf '%q' "$(grep -m1 '^SCRIPTS_DIR' "$ROOT/$py")")")
  else
    problems+=("want the page's $py, found none")
  fi
done

# The page's listings are declared in the commentary, one `file="<name>.sh"` per script;
# the build resolves each against SCRIPTS_DIR. A name with no file under the skill's
# scripts directory is exactly the "missing script" the build refuses on.
if [[ -f "$ROOT/$COMMENTARY" ]]; then
  documented="$(sed -n 's/.*file="\([^"]*\)".*/\1/p' "$ROOT/$COMMENTARY")"
  # Fail closed: no names extracted means the declaration moved and nothing was checked,
  # which must not read as "every documented script is present".
  if [[ -z "$documented" ]]; then
    problems+=("$COMMENTARY declares no script listings — the page's set of scripts could not be read")
  else
    while IFS= read -r f; do
      [[ -n "$f" ]] || continue
      [[ -f "$ROOT/$skill_dir/scripts/$f" ]] ||
        problems+=("$COMMENTARY documents $f, which is not in $skill_dir/scripts")
    done <<< "$documented"
  fi
else
  problems+=("want the page's commentary at $COMMENTARY, found none")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
