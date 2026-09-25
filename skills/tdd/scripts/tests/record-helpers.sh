# record-helpers.sh — the helpers the *-recorded.test.sh suites share (issue #225). Each of
# those suites reads a passage in a tracked document as text and asks whether it records a
# rule. Sourced, never run: the name sits outside make test's `*.test.sh` glob on purpose.
# A sourcing suite owns `pass`, `fail` and `problems`; these functions only read and bump them.

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which document is missing which sentence rather than just that one is.
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

# plain — stdin with emphasis marks and backticks dropped and the case folded, so a regex
# is written one way and still matches prose that marked the same words up as `VERI_MODEL`
# or **separate**.
plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; }

# records — stdin as one line per record, normalised by `plain`: a top-level `- ` or `* `
# bullet with its continuation lines, or a paragraph, joined with spaces, so a regex can ask
# a sentence the document wrapped mid-way.
records() {
  awk '/^[-*] / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec == "" { rec = $0; next }
       { rec = rec " " $0 }
       END { if (rec != "") print rec }' | plain
}

# bullet <regex> — the one top-level bullet of the file named by the sourcing suite's
# `skill_path` whose first line matches, up to the next bullet or heading, as one
# normalised line.
bullet() {
  awk -v want="$1" '
    $0 ~ want { inside = 1; print; next }
    inside && /^([-*] |#)/ { exit }
    inside' "$skill_path" | plain | tr '\n' ' '
}

# says <fact> <regex>... — one fact the sourcing suite's `passage_text` has to carry: some
# ONE record of it has to match every <regex>, and one problem naming `passage_from` and the
# fact is appended if none does. A pair split across two records is not a statement.
says() {
  local fact="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<< "$passage_text"
  problems+=("$passage_from does not say $fact")
}
