# lib/verify-options.sh — sourced, not run: defines `verify_takes_a_value`, the one place that
# says which of verify.sh's options carry a value rather than standing alone (#426).
#
# Two callers walk the same argv and must agree on that list. verify.sh collects those pairs
# into `flag_args` before reading its positionals. run-verdict.sh, which stands in front of it
# under `supervise.sh verdict-<phase>`, steps over the same pairs on a copy of argv to find the
# phase whose stale reason file it clears before the verifier starts.
#
# Spelled twice, a third value-taking option added to verify.sh alone would leave the launcher
# reading that option's VALUE as the phase: it would then clear `.tdd/verify-<some value>.reason`,
# a file nothing writes, and leave the real one holding the previous step's reason — which is
# the #424 failure exactly, a conductor spending a revise attempt on a 23-minute-old REJECT.
# One list, sourced by both, makes that drift impossible rather than merely unlikely.
#
# verify_takes_a_value <word> — returns 0 if <word> is an option verify.sh reads a value after,
# 1 otherwise, including for an empty word. It answers about the word alone and never about the
# value: whether that value is present and non-empty is verify.sh's refusal to make, spelled
# there with the usage line it quotes back.
verify_takes_a_value() {
  case "${1:-}" in
    --step|--fast-cmd) return 0 ;;
    *) return 1 ;;
  esac
}
