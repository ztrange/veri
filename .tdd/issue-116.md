# Plan for #116 — Resume after an interruption inside the refactor loop skips the last step's verify-refactor

- [x] `tick-ledger.sh --refactor-pending <ledger> <matcher>` checks the matching step off and appends ` ⟂ refactor pending` to that same line in the same write, while `tick-ledger.sh <ledger> <matcher>` without the flag still ticks the line with no mark
- [x] `next-pending-refactor.sh < ledger` prints the description of the first checked step whose line ends in ` ⟂ refactor pending`, without the mark, and exits 3 with no output when no step carries it
- [x] `clear-refactor-pending.sh <ledger> <matcher>` removes ` ⟂ refactor pending` from the first checked step containing the matcher that carries it, in place, and exits 3 leaving the file byte-identical when no such step matched
- [x] `SKILL.md`'s Green PASS ticks the ledger with `tick-ledger.sh --refactor-pending`, the pin path ticks without the flag, and verify-refactor PASS runs `clear-refactor-pending.sh` and commits the cleared ledger before the step is mirrored as done
- [ ] `SKILL.md`'s Resume asks `next-pending-refactor.sh` before `next-unchecked.sh`, and on a pending step resets uncommitted work, re-enters that step's refactor loop with the files of its green commit (the last commit that changed the ledger) and the count of `refactor:` commits since it, then runs verify-refactor — going to the draft PR only when both scripts exit 3
- [ ] `SKILL.md`'s Draft PR step refuses to push or open the PR while `git status --porcelain` is non-empty or `next-pending-refactor.sh` still finds a pending step
- [ ] `CLAUDE.md`'s ledger invariant and `CONTEXT.md`'s **Ledger** entry say a checked step also carries a refactor-pending mark until its verify-refactor passes
