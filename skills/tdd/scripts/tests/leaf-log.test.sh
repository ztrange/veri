#!/usr/bin/env bash
# Unit tests for scripts/veri/leaf_log.py — the one scan for the result records of a leaf's
# stream-json log.
#
# Contract under test:
#   veri/leaf_log.py  result_records(<lines>) → every {"type":"result"} record, in log order.
#                     Its importers — harvest-usage.sh, extract-result.sh and supervise.sh's
#                     terminal_outcome — find it under veri/, not lib/, and scripts/lib/
#                     holds no .py file.
#
# Run: scripts/tests/leaf-log.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$(cd "$HERE/.." && pwd)"
source "$HERE/lib/harness.sh"

problems=()
for py in "$SCRIPTS"/lib/*.py; do
  [[ ! -e "$py" ]] || problems+=("scripts/lib/${py##*/} still exists")
done
scratch="$(scratch_dir)"
mkdir -p "$scratch/scripts" "$scratch/work/.tdd"
cp -R "$SCRIPTS/lib" "$SCRIPTS/veri" "$scratch/scripts/"
rm -rf "$scratch/scripts/lib/leaf_log.py" "$scratch/scripts/lib/__pycache__" "$scratch/scripts/veri/__pycache__"
cp "$SCRIPTS/harvest-usage.sh" "$SCRIPTS/extract-result.sh" "$SCRIPTS/supervise.sh" "$SCRIPTS/event.sh" \
  "$scratch/scripts/"
cat > "$scratch/scripts/veri/leaf_log.py" <<'PY'
def result_records(lines):
    list(lines)
    return [{"type": "result", "is_error": True, "result": "decoy from veri",
             "duration_ms": 4242, "duration_api_ms": 1, "num_turns": 1, "total_cost_usd": 0.5,
             "usage": {"input_tokens": 1, "output_tokens": 1,
                       "cache_read_input_tokens": 1, "cache_creation_input_tokens": 1}}]
PY
printf '%s\n' '{"type":"result","is_error":false,"result":"the real text"}' > "$scratch/work/.tdd/develop-red.log"
run() { (cd "$scratch/work" && env PYTHONDONTWRITEBYTECODE=1 "$@" 2>&1); }

out="$(run "$scratch/scripts/extract-result.sh" < "$scratch/work/.tdd/develop-red.log")" && code=0 || code=$?
[[ "$code" -eq 0 && "$out" == "decoy from veri" ]] \
  || problems+=("extract-result.sh beside a stand-in veri/leaf_log.py: exit $code, output '$out', want 'decoy from veri'")
out="$(run "$scratch/scripts/harvest-usage.sh" develop-red)" && code=0 || code=$?
events="$(cat "$scratch/work/.tdd/events.jsonl" 2>/dev/null)"
[[ "$code" -eq 0 && "$events" == *4242* ]] \
  || problems+=("harvest-usage.sh beside a stand-in veri/leaf_log.py: exit $code, output '$out', events '$events', want duration_ms 4242")
out="$(HERE="$scratch/scripts" run bash -c \
  "$(sed -n '/^terminal_outcome() {/,/^}/p' "$SCRIPTS/supervise.sh"); terminal_outcome .tdd/develop-red.log")" \
  && code=0 || code=$?
[[ "$code" -eq 0 && "$out" == failure ]] \
  || problems+=("supervise.sh's terminal_outcome beside a stand-in veri/leaf_log.py: exit $code, output '$out', want 'failure'")

report "leaf_log is a module of scripts/veri/, leaving no .py file under scripts/lib/: harvest-usage.sh, extract-result.sh and supervise.sh read result records through veri/leaf_log.py"

finish
