#!/bin/sh
# parse-verdict.sh — shim: the logic lives in go/verdict (see go/main.go). The contract is
# unchanged: stdin = a verifier leaf's raw output; stdout = the trimmed reason; exit 0 PASS ·
# 1 REJECT · 2 malformed (stdout empty, diagnostic on stderr).
#
# /bin/sh rather than bash: the shim only execs, and sh starts in a third of the time.
# `${0%/*}` is dirname without a fork; a bare `$0` (found via PATH) means the current dir.
here="${0%/*}"; [ "$here" = "$0" ] && here=.
bin="$here/go/bin/veri"
if [ ! -x "$bin" ]; then
  command -v go >/dev/null 2>&1 || { echo "parse-verdict.sh: $bin is not built and go is not on PATH; run \`make go-build\`" >&2; exit 2; }
  (cd "$here/go" && go build -o bin/veri .) || exit 2
fi
VERI_SCRIPTS_DIR="$here" exec "$bin" parse-verdict "$@"
