#!/usr/bin/env bash
# The clock audit: names a stub script a supervisor suite writes under `$stub/` whose
# silence is REAL elapsed time — a `sleep` in its body with no `clock-jump` beside it —
# unless this file records that dependence as deliberate, with the reason it cannot be
# injected away. Exit 0 and say nothing when every stub is either clock-injected or
# exempted, exit 1 and name each one that is not, exit 2 when it was given no file it
# could read. The four codes are this repository's own (CLAUDE.md, *Exit codes are the
# API*): 1 is a clean negative, 2 is no answer obtained.
#
# A helper rather than a suite, so `make test`'s `*.test.sh` glob does not pick it up: its
# caller is supervise.test.sh's last case, which asks it twice — once over that suite as
# committed, where it must be silent, and once over a planted suite holding one stub that
# jumps the clock and one that merely waits, where it must name the second and only the
# second. An audit that named everything, or nothing, would pass a rule that says nothing.
#
# Why this exists (issue #300): supervise.test.sh case 4 failed about one run in ten. Its
# leaf emitted every 0.3 s of REAL time against a 2 s heartbeat window, and a scheduling
# delay landing near a whole-second boundary — the supervisor's clock is `date +%s`, whole
# seconds — read as a stall, so an alive leaf was killed as stuck. The fix was to give the
# suite an injected clock: a stub leaf calls `clock-jump <s>` and the silence it wants
# exists on that clock alone, in milliseconds of wall time. That fix is worth exactly as
# much as the next stub leaf written without a jump, and a green run says nothing about
# the discipline — which is what this file is for.
#
# Scope: the stub scripts a suite writes with `cat > "$stub/<name>" <<TERM`, from that line
# to the terminator. That is where a leaf's silence is authored, and it is the one place in
# these suites where waiting means "look unresponsive to the supervisor". A `sleep` in the
# suite's OWN body — the kill-grace and pid-file polls, `for _ in $(seq 1 20); do kill -0 …
# || break; sleep 0.1; done` — is a different animal: it watches an OS fact (a process is
# gone, a file has content) and exits the moment that fact lands, so it neither produces
# silence nor depends on where a second boundary falls. Those are not audited, and widening
# this to every `sleep` in the file would bury the two stubs that matter under a dozen polls
# that never could.
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
