#!/usr/bin/env bash
# The clock audit: names a stub script a supervisor suite writes under `$stub/` whose
# silence is real elapsed time — a `sleep` in its body with no `clock-jump` beside it —
# unless this file exempts it with a reason.
#
# Contract under test:
#   real-clock-audit.sh <suite>...
#     exit 0  every stub written with `cat > "$stub/<name>" <<TERM` is clock-injected or exempted
#     exit 1  names each stub that is not
#     exit 2  no file given could be read
set -uo pipefail

declare -A EXEMPT=(
  [supervise.test.sh:leaf-term-sleep]="case 30 sends TERM to the supervisor and then asks whether the leaf is still alive, so the leaf must be a LIVE process for the whole case; it \`exec\`s into the sleep to be that process, and its own progress is never what the case reads — a clock jump would change nothing about it"
  [supervise.test.sh:await-poll]="not a leaf: the helper a stub leaf calls to be sure the supervisor has read the injected clock again. Its 0.01s poll waits on a counter the fake \`date\` appends to, an observed fact like the kill-grace polls above, and it returns the moment that fact lands rather than after any window"
)

if [[ "$#" -lt 1 ]]; then
  echo "usage: real-clock-audit.sh <suite-file>…" >&2
  exit 2
fi
for f in "$@"; do
  if [[ ! -r "$f" ]]; then
    echo "real-clock-audit.sh: cannot read $f" >&2
    exit 2
  fi
done

keys="$(IFS='|'; echo "${!EXEMPT[*]}")"

found=0
while IFS=$'\t' read -r file lineno stub; do
  found=1
  printf '%s:%s %s reaches its silence by real waiting: it sleeps with no clock-jump in its body, and no exemption is recorded for it\n' \
    "$file" "$lineno" "$stub"
done < <(awk -v keys="$keys" '
  BEGIN {
    n = split(keys, k, "|")
    for (i = 1; i <= n; i++) if (k[i] != "") exempt[k[i]] = 1
  }
  FNR == 1 { in_body = 0; base = FILENAME; sub(/^.*\//, "", base) }
  !in_body && /cat > "\$stub\// {
    name = $0; sub(/^.*cat > "\$stub\//, "", name); sub(/".*/, "", name)
    term = $0; sub(/^.*<<-?/, "", term); gsub(/[\047"]/, "", term); gsub(/[ \t]+$/, "", term)
    if (term == "") next
    in_body = 1; stub_name = name; stub_line = FNR; waits = 0; jumps = 0
    next
  }
  in_body && $0 ~ ("^[ \t]*" term "[ \t]*$") {
    in_body = 0
    if (waits && !jumps && !((base ":" stub_name) in exempt))
      print FILENAME "\t" stub_line "\t" stub_name
    next
  }
  in_body {
    if ($0 ~ /(^|[^A-Za-z0-9_-])sleep([^A-Za-z0-9_-]|$)/) waits = 1
    if (index($0, "clock-jump") > 0) jumps = 1
  }
' "$@")

[[ "$found" -eq 0 ]]
