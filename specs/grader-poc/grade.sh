#!/bin/bash
# grade.sh <prose-file> <req-file> <out-file>
prose=$1 req=$2 out=$3
prompt="## Requirements
$(sed 's/^\([A-Z]*[0-9]*\) | /\1: /' "$req")

## Prose
<<<PROSE
$(cat "$prose")
PROSE>>>"
cd "$(dirname "$0")"
printf '%s' "$prompt" | claude -p --setting-sources "" --tools "" --strict-mcp-config --no-session-persistence \
  --model claude-sonnet-5-5 --system-prompt "$(cat grader-system.txt)" --output-format json > "$out" 2> "$out.err" < /dev/stdin
echo "exit=$? $(jq -r '"cost=\(.total_cost_usd) in=\(.usage.input_tokens) out=\(.usage.output_tokens)"' "$out" 2>/dev/null)"
