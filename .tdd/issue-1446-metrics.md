### 📊 Metrics — issue 1446

Wall time for the issue: 1961 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1449.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 2 | 4 | 1159 | 56705 | 37707 | 0.17 |
| red | 3 | 1 | 0 | 0 | 116 | 104 | 24 | 46 | 10207 | 1210222 | 158887 | 1.51 |
| green | 2 | 1 | 0 | 0 | 125 | 48 | 15 | 30 | 4689 | 708174 | 88655 | 0.72 |
| refactor | 2 | 1 | 0 | 0 | 60 | 28 | 9 | 18 | 2418 | 374193 | 82257 | 0.60 |
| pin | 1 | 1 | 0 | 0 | 14 | 12 | 4 | 8 | 1575 | 156758 | 39042 | 0.19 |
| diff | 2 | 1 | 0 | 0 | 438 | 62 | 15 | 30 | 5096 | 705156 | 86810 | 0.73 |
| predicate | 1 | 0 | 0 | 0 | 14 | 11 | 3 | 6 | 936 | 105586 | 37749 | 0.34 |
| structural | 1 | 0 | 0 | 0 | 29 | 24 | 6 | 12 | 2564 | 262573 | 40575 | 0.43 |
| transform | 1 | 1 | 0 | 0 | 337 | 15 | 5 | 10 | 1598 | 204247 | 39240 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 851 | 98 | 34 | 68 | 11298 | 1424216 | 281110 | 1.38 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 294 | 215 | 49 | 96 | 18944 | 2359398 | 329812 | 3.49 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 60 | 0.65 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 14 | 0.19 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `tick-ledger.sh --phase-owed contract-a` and `--phase-owed contract-b` write the owed mark on a step listing that phase; any other phase, `contract (a)` and `contract (b)` included, exits 2 with the ledger byte-identical ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 125 | 37 | 74 | 12532 | 1743825 | 274806 | 2.18 | 335 | unknown | 0/5 | nothing-left |  |  | pin |
| A ledger whose phased step is written to SKILL.md's phase line `⟦phases: expand, migrate, contract-a, contract-b⟧` is accepted end to end: once expand and migrate are marked, `ledger-steps.sh next-phase` prints `contract-a`, and both `tick-ledger.sh --phase contract-a` and `tick-ledger.sh --phase-owed contract-a` accept it ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 67 | 15 | 28 | 6357 | 705522 | 94035 | 0.83 | unknown | unknown | unknown | unknown |  |  | already-satisfied |
| No file under `skills/` — SKILL.md, the prompt builders and their templates, `veri/ledger.py`, `veri/tick_ledger.py` and the suites testing them — spells a contract phase `contract (a)` or `contract (b)`; every one uses `contract-a` / `contract-b` ⟦diff-checked⟧ ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 112 | 29 | 58 | 10194 | 1277562 | 204374 | 1.69 | 472 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `tick-ledger.sh --phase-owed contract-a` and `--phase-owed contract-b` write the owed mark on a step listing that phase; any other phase, `contract (a)` and `contract (b)` included, exits 2 with the ledger byte-identical ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 60 | 0.60 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 4 | 1 | 1 | 2 | 313 | 0 | 1 | 1 | 320 |
| fast | 23 | 25 | 25 | 25 | 24 |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 83 | 164 | 30242 | 3783614 | 610922 | 4.87 |
