### 📊 Metrics — issue 2081

Wall time for the issue: 1256 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2095.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 966 | 17051 | 14451 | 0.05 |
| red | 8 | 3 | 0 | 0 | 170 | 111 | 36 | 64 | 12919 | 913546 | 133605 | 0.55 |
| green | 6 | 3 | 0 | 0 | 186 | 79 | 35 | 62 | 8890 | 885748 | 93521 | 0.41 |
| refactor | 6 | 3 | 0 | 0 | 78 | 38 | 15 | 30 | 3158 | 369813 | 80874 | 0.27 |
| pin | 2 | 2 | 0 | 0 | 43 | 24 | 7 | 14 | 2072 | 180564 | 27172 | 0.11 |
| diff | 4 | 2 | 0 | 0 | 88 | 41 | 21 | 42 | 3943 | 566028 | 51341 | 0.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 14 | 0 | 0 | 286 | 142 | 51 | 100 | 14197 | 1307534 | 195991 | 0.76 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 289 | 158 | 64 | 114 | 17751 | 1625216 | 204973 | 0.85 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `veri/prose_owed.py` gains a pure decision function taking a ledger's text and the list of owed units: a unit named in backticks on an unchecked (`- [ ]`) ledger line carrying `⟦skill-edit⟧` is waived, returned paired with that step's text, and is no longer owed; pinned by a small in-process case in `skills/tdd/scripts/tests/py/unit/test_prose_owed_waiver.py` (no git, no process) driving the decision with such a ledger and owed units `[U]`, which leaves nothing owed and U waived by that step ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 55 | 23 | 40 | 5628 | 528157 | 85227 | 0.32 | 187 | unknown | 0/5 | nothing-left |  |  | full |
| Go-red check in `skills/tdd/scripts/tests/py/unit/test_prose_owed_waiver.py`: with U owed and no unchecked `⟦skill-edit⟧` line naming U — the ledger holds no such step, or the step naming U is already checked (`- [x]`), or an unchecked `⟦skill-edit⟧` step names a different unit — the decision waives nothing and U stays owed ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 7 | 14 | 2829 | 185787 | 29337 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| Go-red check in `skills/tdd/scripts/tests/py/unit/test_prose_owed_waiver.py`: with U named by a pending `⟦skill-edit⟧` step and a second unit V also owed (V named by no pending step), the decision waives U only and V stays owed, so `prose-owed.sh` still prints V and exits 1; an orphan GRADED entry is never waived ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 7 | 12 | 2563 | 155507 | 29086 | 0.11 | unknown | unknown | unknown | unknown |  |  | pin |
| `prose-owed.sh <repo-root>` run in a checkout whose current branch is `tdd/<n>-<slug>` applies the decision to that root's committed-path ledger `.tdd/issue-<n>.md`: when every owed unit is waived it prints nothing and exits 0, so the preflight baseline `make test` is green and the run proceeds to the pending step; on any other branch, or with no such ledger, its output and exit are unchanged. The branch is read through the `veri/git.py` wrapper; pinned by a case in `skills/tdd/scripts/tests/py/test_prose_owed_waiver_process.py` marked `@pytest.mark.process("git")` driving the shim against a temporary repository ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 73 | 27 | 50 | 8824 | 710585 | 95452 | 0.40 | 228 | unknown | 0/5 | nothing-left |  |  | full |
| Every unit `prose-owed.sh` waives is logged as a `prose-owed-waived` event in the run's event log (`.tdd/events.jsonl` under the repo root, through `veri/event.py`), carrying `unit=<U>` and `step=<the pending skill-edit step's text>`, so the run log shows the baseline was passed over a stale unit and which step owes the regrade; no event is written when nothing is waived ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 73 | 29 | 54 | 7195 | 769635 | 96070 | 0.39 | 198 | unknown | 0/5 | nothing-left |  |  | full |
| The branch's diff leaves the `test unit` recipe's failure aggregation in `Makefile` unchanged: the pytest leg's red still sets `fail=1` independently of `prose-owed.sh`'s exit, so any non-prose-owed suite failure still turns the baseline red and stops the run ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 17 | 9 | 18 | 1565 | 236214 | 24265 | 0.10 | 62 | n/a | n/a | n/a |  |  | full |
| `skills/tdd/SCRIPTS.md`'s `prose-owed.sh` entry documents the waiver: which units it waives (named in backticks by an unchecked `⟦skill-edit⟧` line of the ledger of the `tdd/<n>-…` branch it runs on), that every other finding still exits 1, and the `prose-owed-waived` event it writes ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 12 | 24 | 2378 | 329814 | 27076 | 0.12 | 74 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `veri/prose_owed.py` gains a pure decision function taking a ledger's text and the list of owed units: a unit named in backticks on an unchecked (`- [ ]`) ledger line carrying `⟦skill-edit⟧` is waived, returned paired with that step's text, and is no longer owed; pinned by a small in-process case in `skills/tdd/scripts/tests/py/unit/test_prose_owed_waiver.py` (no git, no process) driving the decision with such a ledger and owed units `[U]`, which leaves nothing owed and U waived by that step ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 23 | 0.09 |
| `prose-owed.sh <repo-root>` run in a checkout whose current branch is `tdd/<n>-<slug>` applies the decision to that root's committed-path ledger `.tdd/issue-<n>.md`: when every owed unit is waived it prints nothing and exits 0, so the preflight baseline `make test` is green and the run proceeds to the pending step; on any other branch, or with no such ledger, its output and exit are unchanged. The branch is read through the `veri/git.py` wrapper; pinned by a case in `skills/tdd/scripts/tests/py/test_prose_owed_waiver_process.py` marked `@pytest.mark.process("git")` driving the shim against a temporary repository ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 27 | 0.10 |
| Every unit `prose-owed.sh` waives is logged as a `prose-owed-waived` event in the run's event log (`.tdd/events.jsonl` under the repo root, through `veri/event.py`), carrying `unit=<U>` and `step=<the pending skill-edit step's text>`, so the run log shows the baseline was passed over a stale unit and which step owes the regrade; no event is written when nothing is waived ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 28 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 10 | 3 | 4 | 4 | 4 | 3 | 3 | 3 | 3 | 13 |
| fast | 6 | 5 | 5 | 4 | 5 | 6 | 5 | 5 | 4 | 6 | 5 | 4 | 5 | 5 |  |  |  |  |  |  |  |  |
| target | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 115 | 214 | 31948 | 2932750 | 400964 | 1.62 |
