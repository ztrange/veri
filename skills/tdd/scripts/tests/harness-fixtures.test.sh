#!/usr/bin/env bash
# Tests for scripts/tests/lib/harness.sh fixtures: scratch_dir, on_exit, new_repo, claude_stub.
# Not in the unit tier: new_repo runs git.
#
# Run: scripts/tests/harness-fixtures.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

name="fixtures: scratch_dir is removed at exit, on_exit runs, new_repo commits, claude_stub runs, and a later bg_start keeps the trap"
cat > "$work/child.sh" <<CHILD
set -u
source "$HERE/lib/harness.sh"
source "$HERE/../lib/background.sh"
d="\$(scratch_dir)"
echo "\$d" > "$work/dir"
on_exit "echo cleaned > $work/marker"
new_repo "\$d/repo"
git -C "\$d/repo" commit --allow-empty -q -m x && echo committed > "$work/commit"
claude_stub "\$d" 'echo stubbed'
head -n 1 "\$d/claude" > "$work/shebang"
"\$d/claude" > "$work/stub-out"
bg_start "$work/rec" sleep 30
CHILD
HOME="$work" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
  bash "$work/child.sh" > /dev/null 2> "$work/err"
problems=()
dir="$(cat "$work/dir" 2>/dev/null)"
[[ -n "$dir" && ! -e "$dir" ]] || problems+=("scratch dir '$dir' still exists after exit")
[[ "$(cat "$work/marker" 2>/dev/null)" == cleaned ]] || problems+=("on_exit command did not run")
[[ "$(cat "$work/commit" 2>/dev/null)" == committed ]] || problems+=("commit in new_repo failed")
[[ "$(cat "$work/shebang" 2>/dev/null)" == '#!/bin/sh' ]] || problems+=("claude_stub shebang: $(cat "$work/shebang" 2>/dev/null)")
[[ "$(cat "$work/stub-out" 2>/dev/null)" == stubbed ]] || problems+=("claude_stub output: $(cat "$work/stub-out" 2>/dev/null)")
grep -F "still running at exit" "$work/err" > /dev/null || problems+=("bg_start survivor report lost from the EXIT trap")
while read -r pid _; do kill "$pid" 2>/dev/null || true; done < "$work/rec" 2>/dev/null
report "$name"

name="count line: a suite dying before finish is refused by run-suite.sh, and one finishing after a failing case exits non-zero with its own count line"
cat > "$work/dies.test.sh" <<DIES
#!/usr/bin/env bash
set -uo pipefail
source "$HERE/lib/harness.sh"
ok
[[ 1 -le \$unset_bound ]] && ok
finish
DIES
cat > "$work/fails.test.sh" <<FAILS
#!/usr/bin/env bash
set -uo pipefail
source "$HERE/lib/harness.sh"
ok
no "planted"
finish
FAILS
chmod +x "$work/dies.test.sh" "$work/fails.test.sh"
"$HERE/../run-suite.sh" "$work/dies.test.sh" > "$work/dies-out" 2>&1; dies_code=$?
"$work/fails.test.sh" > "$work/fails-out" 2>&1; fails_code=$?
problems=()
[[ "$dies_code" -eq 1 ]] || problems+=("dying suite: run-suite.sh exit $dies_code, expected 1")
[[ "$(tail -n 1 "$work/dies-out")" == "dies.test.sh: never reached its count line" ]] || problems+=("dying suite: last line '$(tail -n 1 "$work/dies-out")'")
[[ "$fails_code" -ne 0 ]] || problems+=("failing suite: exit 0")
[[ "$(tail -n 1 "$work/fails-out")" == "1 passed, 1 failed" ]] || problems+=("failing suite: last line '$(tail -n 1 "$work/fails-out")'")
report "$name"

finish
