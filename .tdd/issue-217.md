# Plan for #217 — Nothing watches a conductor's context: an orchestrator loop that restarts at step-done, parks halted runs and keeps the skill standalone

- [x] orchestrate.sh launches one conductor per issue solvable-issues.sh prints, each through run-conductor.sh with that issue number, and exits 0 once the solvable set is empty ⟦criterion 1⟧
- [x] orchestrate.sh exits 2 without launching any conductor when solvable-issues.sh exits with anything other than 0 or 3, since then no answer about the solvable set could be obtained ⟦added⟧ ⟦criterion 1⟧
- [x] orchestrate.sh computes the conductor's context as cache_read_input_tokens + cache_creation_input_tokens from each assistant event's usage in the launched stream, as the stream arrives, and never needs a closing result record to know it ⟦criterion 2⟧
- [x] a conductor whose stream crosses VERI_CONDUCTOR_CTX_BUDGET mid-step is not stopped until a step-done is seen, and is stopped after it ⟦criterion 3⟧
- [x] a conductor whose stream never crosses VERI_CONDUCTOR_CTX_BUDGET is never stopped or restarted ⟦criterion 3⟧
- [ ] VERI_CONDUCTOR_CTX_BUDGET is a whole token count read as ${VAR:-default} with a default of 120000, and a value that is not a whole number is refused with exit 2 before any conductor launches ⟦criterion 3⟧
- [ ] a conductor stopped over budget is relaunched for the same issue through run-conductor.sh with the same argv, so it takes the ledger's resume path rather than re-planning ⟦criterion 4⟧
- [ ] a conductor that exits 0 while its issue is still in the solvable set and its ledger still has an unchecked step is treated as unfinished, not done ⟦criterion 5⟧
- [ ] an issue whose run wrote .tdd/parked/<n>.md is recorded as parked, its branch and ledger are left untouched, it is skipped on the next pass, and the next solvable issue is taken ⟦criterion 6⟧
- [ ] run-conductor.sh and SKILL.md launched directly for one issue, with no orchestrator, behave as before: nothing the orchestrator adds is required by a direct /tdd run ⟦criterion 7⟧
- [ ] CLAUDE.md's script and suite counts include orchestrate.sh and its suite ⟦criterion 8⟧
