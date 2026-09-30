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

finish
