#!/bin/sh
# push-branch.sh — shim: the logic lives in go/pushbranch (see go/main.go). The contract is
# unchanged (issue #191, #232): run from the issue's worktree; an unreachable origin is retried
# VERI_PUSH_RETRIES times with a VERI_PUSH_BACKOFF-second wait doubled per retry and exits 0
# after a push-failed event; a non-fast-forward rejection exits 1 after one attempt with a
# push-rejected event; a non-integer tunable exits 2 before any push; an event that cannot be
# written exits 2. event.sh is found beside this shim, which is why VERI_SCRIPTS_DIR is set.
#
# /bin/sh rather than bash: the shim only execs, and sh starts in a third of the time.
here="${0%/*}"; [ "$here" = "$0" ] && here=.
bin="$here/go/bin/veri"
if [ ! -x "$bin" ]; then
  command -v go >/dev/null 2>&1 || { echo "push-branch.sh: $bin is not built and go is not on PATH; run \`make go-build\`" >&2; exit 2; }
  (cd "$here/go" && go build -o bin/veri .) || exit 2
fi
VERI_SCRIPTS_DIR="$here" exec "$bin" push-branch "$@"
