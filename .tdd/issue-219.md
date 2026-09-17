# Plan for #219 — A verifier leaf that backgrounds its test command and ends its turn renders no verdict, and the run bails

- [x] verify.sh relaunches a verifier leaf that exited without being killed and printed no VERDICT: line, and returns the relaunched attempt's verdict (stub prints no verdict first, VERDICT: PASS second → exit 0, two launches)
- [x] no-verdict relaunches stop after VERI_NO_VERDICT_RETRIES (default 1): a stub that never prints a verdict yields exit 2 after exactly 1 + VERI_NO_VERDICT_RETRIES launches, and VERI_NO_VERDICT_RETRIES=0 yields exit 2 after one launch ⟂ refactor pending
- [ ] a non-integer VERI_NO_VERDICT_RETRIES makes verify.sh exit 2 without launching any verifier leaf
- [ ] a verifier killed by supervise.sh (exit 2, stuck or hard timeout) is not relaunched by verify.sh: exit 2 after supervise.sh's own attempts, whatever VERI_NO_VERDICT_RETRIES is
- [ ] VERI_STUCK_RETRIES does not change the no-verdict relaunch count, and VERI_NO_VERDICT_RETRIES does not change supervise.sh's stuck retry count
- [ ] a clean exit with no VERDICT: line is recorded in the event log under a cause distinct from a leaf killed before rendering one, on each relaunch and on the final exit 2
- [ ] metrics.sh reports no-verdict relaunches per run as their own count, distinct from retries and revise
- [ ] a relaunch's verifier prompt is byte-identical to the first attempt's, and build-verify-prompt.sh gains no parameter
- [ ] SKILL.md's exit-2 branch says a clean exit with no verdict is relaunched rather than bailed, and a new ADR docs/adr/0020-*.md records it, naming ADR-0011 and SKILL.md's exit-2 branch as what it narrows
- [ ] CLAUDE.md's budgets invariant names VERI_NO_VERDICT_RETRIES as a fourth axis and why it is not merged with VERI_STUCK_RETRIES
