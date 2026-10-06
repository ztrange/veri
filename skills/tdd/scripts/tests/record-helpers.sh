source "${BASH_SOURCE[0]%/*}/lib/harness.sh"
source "${BASH_SOURCE[0]%/*}/lib/plain.sh"

records() {
  awk '/^[-*] / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec == "" { rec = $0; next }
       { rec = rec " " $0 }
       END { if (rec != "") print rec }' | plain
}

bullet() {
  want="$1" awk '
    $0 ~ ENVIRON["want"] { inside = 1; print; next }
    inside && /^([-*] |#)/ { exit }
    inside' "$skill_path" | plain --join
}

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
