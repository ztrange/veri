### 📊 Metrics — issue 1379

Wall time for the issue: 2031 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1564.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 15 | 3 | 6 | 1824 | 124049 | 45726 | 0.21 |
| red | 4 | 2 | 0 | 0 | 95 | 70 | 21 | 40 | 7922 | 972024 | 192253 | 0.95 |
| green | 4 | 2 | 0 | 0 | 816 | 100 | 22 | 42 | 6074 | 1031567 | 141953 | 1.11 |
| refactor | 4 | 2 | 0 | 0 | 166 | 39 | 15 | 30 | 3391 | 661971 | 178526 | 0.81 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 610 | 112 | 35 | 70 | 11654 | 1658885 | 320846 | 1.57 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 486 | 112 | 26 | 48 | 7557 | 1130726 | 237612 | 1.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `classify-bail.sh step-add-refused` prints `system` and exits 0 — the cause an `add-ledger-step.sh` exit 2 bails with is one classify-bail.sh knows, as a system failure ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 33 | 60 | 7837 | 1421589 | 269761 | 1.30 | 349 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md` says, at every call site of `add-ledger-step.sh` (the over-budget split, the Green `SPLIT:`, the refactor PASS growth, the suite-repair step, the CI-repair steps and the revise-exhausted split), that its exit 2 bails with cause `step-add-refused`, and *Bailing*'s cause list names `step-add-refused` as a **system** failure ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 133 | 25 | 52 | 9550 | 1243973 | 242971 | 1.57 | 885 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `classify-bail.sh step-add-refused` prints `system` and exits 0 — the cause an `add-ledger-step.sh` exit 2 bails with is one classify-bail.sh knows, as a system failure ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 87 | 0.42 |
| `SKILL.md` says, at every call site of `add-ledger-step.sh` (the over-budget split, the Green `SPLIT:`, the refactor PASS growth, the suite-repair step, the CI-repair steps and the revise-exhausted split), that its exit 2 bails with cause `step-add-refused`, and *Bailing*'s cause list names `step-add-refused` as a **system** failure ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 79 | 0.40 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 243 |
| fast | 55 | 54 | 53 | 54 | 54 | 54 |  |  |  |
| target | 1 | 1 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 61 | 118 | 19211 | 2789611 | 558458 | 3.09 |
