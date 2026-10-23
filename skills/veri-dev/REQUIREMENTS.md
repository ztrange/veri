## skills/veri-dev/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| D1 | Invoked as `/veri-dev [<lane>] [N] [--resume <file>]`. N defaults to 1. It carries standing merge permission in the project repo for the runs it finishes; it never merges in another repo. | Mario, 2026-10-18: both operator skills always include merge permission. |
| D2 | It keeps exactly N conductors running while the solvable list is non-empty. | Idle slots were the recurring waste. |
| D3 | Each conductor is a detached `run-conductor.sh <n>`, never a conductor run inline. | An inline conductor costs ~60k tokens per issue in the session. |
| D4 | It launches the next issue only after the previous launch's ledger exists. | A claim appears only ~10 minutes into a run. |
| D5 | On each exit it routes by fact: ✅ Done → review, then `veri-merge` on OK; a bail → `veri-bail`; no closing comment → P10. | |
| D6 | After every merge, park or exit it recounts and refills to N. | |
| D7 | It applies the coordinator's changes to N or to the order at the next slot decision. | |
| D8 | It stops and asks only for: red CI it cannot fix, a ⟦human-owed⟧ step, an unresolvable conflict, a decision a ledger step asks for. | |
| D9 | It does not file, groom or reprioritise issues, and does not edit veri's scripts. | Those are the coordinator's job, and a veri fix is an issue for veri. |
| D10 | Where it describes reporting to the coordinator, it says that with a coordinator attached each event P4 lets it speak about goes to the coordinator, not to the human, unless it stops and asks (D8). It says so as a pointer to P4, never a copy of P4's rule. | 2026-10-20: the mu dev session re-stated a pending decision to Mario about 15 times. A copied rule drifts from P4. |
| D11 | Before merging a ✅ Done run, whether on its own OK or on a coordinator's merge instruction, it sends the coordinator every caveat its review found of three kinds: a test never watched failing, a change to a guard or other product code outside the issue's stated scope, a departure from the issue's wording. It merges only after a reply that names each caveat. A review with no such caveat says so in the same report. | 2026-10-20: a merge order crossed the dev session's caveat report about 6 times. |
| D12 | Every conductor launch, a resume included, appends its output with `>>` to `.tdd/conductor-<n>.log` in the target repo's main working tree, the file `stop-reason.sh` and `metrics.sh` read. No launch truncates it. | 2026-10-20: every mu run's log sat in a scratchpad, so `stop-reason.sh` answered "no conductor log" for each one. A `>` on resume destroys the first launch's evidence. |
