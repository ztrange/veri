# Plan for #544 — the Draft PR step's CI wait: one-call timeout, legacy status rows, bails that don't stop

- [x] a new `wait-ci.sh <pr-url> [max-seconds]` reads the PR's statusCheckRollup through `gh` and exits 3 while a check is still pending and its bound has not run out, 0 when every check completed SUCCESS, NEUTRAL or SKIPPED, and 1 when a completed check has any other conclusion; an empty rollup is never exit 0 ⟦criterion 1⟧
- [x] `wait-ci.sh`'s bound is enforced across calls, not within one: the deadline is recorded on the first call for the PR's head commit, and a later call that still finds a check pending past that deadline exits 2 rather than starting a fresh bound ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `wait-ci.sh` branches on `__typename`: a legacy StatusContext row with `state` PENDING or EXPECTED and no `status` key counts as pending, never green, and one in FAILURE or ERROR counts as failed ⟦criterion 2⟧
- [ ] SKILL.md's Draft PR step waits on CI by calling `wait-ci.sh` again on its exit 3, with no wait loop inside one Bash call and no pending test that reads `.status` alone ⟦criterion 1⟧
- [ ] SKILL.md's Draft PR step stops at a `ci-timeout` or `ci-red` bail: it goes to *Bailing*, and neither the `done` mark nor the `metrics:` commit follows it in that step's command block ⟦criterion 3⟧
- [ ] `add-ledger-step.sh` inserts a CI repair step marked `⟦ci-repair⟧` without counting it against `VERI_STEP_GROWTH`, and `next-unchecked.sh` still hands that step over ⟦criterion 6⟧
- [ ] SKILL.md's Draft PR step appends its CI repair step through that `⟦ci-repair⟧` path and recognises a second red by the `⟦ci-repair⟧` mark on a ledger line, not by matching the repair step's prose ⟦criterion 4⟧
- [ ] SKILL.md's Draft PR step leaves no CI run on the readied PR that nothing reads: a push after the CI read has its own run read by `wait-ci.sh`, or no push follows the CI read ⟦criterion 5⟧
