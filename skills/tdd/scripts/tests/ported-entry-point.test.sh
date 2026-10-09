#!/usr/bin/env bash
# Unit tests for the modules a shim execs — each one's __main__ block goes through the shared
# entry point.
#
# Contract under test:
#   A module veri/<module>.py named by a shim's `exec python3 …/veri/<module>.py` line under
#   skills/tdd/scripts/ calls entry.run inside its `if __name__ == "__main__":` block. An
#   offender is reported as `<module>:<line>`, the line of that `if`. Sources are read as text.
#
# Run: skills/tdd/scripts/tests/ported-entry-point.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

SCRIPTS='skills/tdd/scripts'

source "$HERE/lib/harness.sh"

shimmed_modules() {
  sed -nE 's|^exec python3 .*/veri/([[:alnum:]_]+\.py)".*|\1|p' "$ROOT/$SCRIPTS"/*.sh | sort -u
}

bypassing_main_line() {
  awk '
    /^if __name__ == "__main__":[[:space:]]*$/ { line = NR; inblock = 1; next }
    inblock && /^[^[:space:]]/ { inblock = 0 }
    inblock && /entry\.run\(/ { through = 1 }
    END { if (line && !through) print line }
  ' "$1"
}

probe_every_shimmed_module_goes_through_entry() {
  local module line
  while IFS= read -r module; do
    [[ -f "$ROOT/$SCRIPTS/veri/$module" ]] || continue
    line="$(bypassing_main_line "$ROOT/$SCRIPTS/veri/$module")"
    [[ -z "$line" ]] ||
      problems+=("$module:$line is a __main__ block that does not call entry.run, so an exception escaping main exits 1 with a traceback: end it with \`import entry\` and \`entry.run(main, sys.argv[1:])\`")
  done < <(shimmed_modules)
  return 0
}

name="every module a shim execs goes through the shared entry point"
problems=()
probe_every_shimmed_module_goes_through_entry
report "$name"

finish
