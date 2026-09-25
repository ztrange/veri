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
