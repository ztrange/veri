### 📊 Metrics — issue 1312

Wall time for the issue: 9137 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 14 of 14 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1399.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 1104 | 12489 | 33129 | 0.14 |
| red | 31 | 15 | 0 | 0 | 1303 | 856 | 228 | 442 | 88226 | 10982213 | 1404454 | 12.28 |
| green | 32 | 14 | 2 | 0 | 4516 | 929 | 280 | 544 | 93618 | 13536254 | 1398746 | 12.43 |
| refactor | 27 | 13 | 0 | 0 | 1191 | 598 | 174 | 348 | 58196 | 8236701 | 1174271 | 9.60 |
| pin | 1 | 1 | 0 | 0 | 30 | 24 | 6 | 12 | 3119 | 263625 | 41487 | 0.22 |
| predicate | 6 | 0 | 0 | 0 | 110 | 93 | 21 | 42 | 7393 | 795882 | 231741 | 2.16 |
| structural | 4 | 0 | 0 | 0 | 183 | 135 | 34 | 68 | 13788 | 1708933 | 182699 | 2.08 |
| transform | 4 | 3 | 1 | 0 | 110 | 51 | 18 | 36 | 4991 | 723556 | 155541 | 0.74 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 50 | 47 | 3 | 0 | 3187 | 774 | 282 | 554 | 88061 | 12141903 | 1971978 | 9.98 |
| developer | claude-opus-5-5 | 56 | 0 | 0 | 0 | 4267 | 1920 | 480 | 940 | 182374 | 24117750 | 2650090 | 29.68 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 971 | 3.40 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 110 | 0.74 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `build-develop-prompt.sh` accepts an expand phase and a migrate phase, each printing a prompt that states what that phase changes (expand: production gains the new interface and the old one becomes a proxy; migrate: callers move to the new interface) and that test files stay frozen ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 172 | 45 | 90 | 17351 | 2225118 | 275178 | 2.39 | 370 | unknown | 1/5 | nothing-structural |  |  | full |
| `build-develop-prompt.sh` accepts a contract (a) phase and a contract (b) phase, the contract (a) prompt stating that tests are rewritten or deleted while production stays frozen, the contract (b) prompt stating that the old interface's proxy is deleted while test files stay frozen ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 166 | 52 | 102 | 17805 | 2555061 | 274669 | 2.42 | 303 | unknown | 1/5 | structural-owed |  |  | full |
| `build-verify-prompt.sh` accepts an expand phase and a migrate phase, each printing a prompt that states what that phase changes and that test files must be left frozen ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 271 | 73 | 144 | 28531 | 3680277 | 344233 | 3.24 | 506 | 1/2 | 1/5 | structural-owed |  |  | full |
| `build-verify-prompt.sh` accepts a contract (a) phase and a contract (b) phase, the contract (a) prompt stating that production must be left frozen, the contract (b) prompt stating that the proxy is deleted and test files must be left frozen ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 167 | 51 | 102 | 17530 | 2486271 | 266148 | 2.28 | 290 | unknown | 1/5 | structural-owed |  |  | full |
| `build-verify-prompt.sh`'s expand, migrate, contract (a) and contract (b) phases take only a phase, the spec file, the test path and a base sha, and exit 2 when that base sha does not match `^[0-9a-f]{7,40}$`, as the `refactor` phase does ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 70 | 14 | 28 | 7236 | 674225 | 91571 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |
| An unknown phase given to `build-develop-prompt.sh` or to `build-verify-prompt.sh` exits 2 with a message naming the expand, migrate, contract (a) and contract (b) phases among the phases it accepts ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 134 | 43 | 86 | 13256 | 2027293 | 257175 | 2.14 | 255 | unknown | 1/5 | nothing-structural |  |  | full |
| `SKILL.md` plans an interface change as one ledger step listing its phases (`⟦phases: …⟧`) and runs the phases it lists in order, each as a developer leaf then a blind verifier, ticking that phase's mark (`tick-ledger.sh --phase`) with that phase's commit ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 205 | 52 | 102 | 21885 | 2873826 | 306595 | 2.85 | 553 | unknown | 1/5 | nothing-left |  |  | full |
| `SKILL.md` rejects an expand, migrate or contract (b) phase's commit that `transform-touches-tests.sh` exits 1 on, and a contract (a) phase's commit that `production-frozen.sh` exits 1 on ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 178 | 51 | 96 | 18249 | 2395912 | 275709 | 2.45 | 765 | unknown | 1/5 | nothing-structural |  |  | full |
| `SKILL.md` starts a phased step's contract only once `no-product-caller.sh` on the old interface exits 0 ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 121 | 38 | 74 | 11951 | 1686142 | 260598 | 2.06 | 704 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md` spends one refactor of the budget for a whole phased step, not one per phase ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 156 | 44 | 84 | 13458 | 2029996 | 267184 | 2.23 | 647 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md`: a contract phase that exhausts `REVISE_BUDGET` is reset to its own base sha, the expand and migrate commits are kept, and the contract is filed under the ledger's `## Owed steps` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 44 | 86 | 13637 | 2053045 | 273605 | 2.22 | 747 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md` accepts a `⟦replaces-case⟧` group step's Green only once the conductor's own run of `mutation-parity.sh` on that step's pairs table exits 0 ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 139 | 43 | 78 | 13346 | 1878862 | 270307 | 2.23 | 531 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md` accepts a contract (a) phase only once the conductor's own run of `mutation-parity.sh` on that phase's pairs table exits 0 ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 121 | 42 | 82 | 13052 | 1934246 | 263551 | 2.15 | 522 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md` puts `mutation-parity.sh`'s report into the PR body as the pairs table, and each row it reports `owed` into the PR body under `## Owed by a human` ⟦criterion 3⟧ | 29 | 9 | 2 | 0 | 0 | 0 | 638 | 169 | 338 | 62044 | 7746890 | 1162416 | 10.05 | 1219 | 1/2 | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `build-develop-prompt.sh` accepts an expand phase and a migrate phase, each printing a prompt that states what that phase changes (expand: production gains the new interface and the old one becomes a proxy; migrate: callers move to the new interface) and that test files stay frozen ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 81 | 0.75 |
| `build-develop-prompt.sh` accepts a contract (a) phase and a contract (b) phase, the contract (a) prompt stating that tests are rewritten or deleted while production stays frozen, the contract (b) prompt stating that the old interface's proxy is deleted while test files stay frozen ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 101 | 0.87 |
| `build-verify-prompt.sh` accepts an expand phase and a migrate phase, each printing a prompt that states what that phase changes and that test files must be left frozen ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 145 | 1.02 |
| `build-verify-prompt.sh` accepts a contract (a) phase and a contract (b) phase, the contract (a) prompt stating that production must be left frozen, the contract (b) prompt stating that the proxy is deleted and test files must be left frozen ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 113 | 0.87 |
| An unknown phase given to `build-develop-prompt.sh` or to `build-verify-prompt.sh` exits 2 with a message naming the expand, migrate, contract (a) and contract (b) phases among the phases it accepts ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 72 | 0.69 |
| `SKILL.md` plans an interface change as one ledger step listing its phases (`⟦phases: …⟧`) and runs the phases it lists in order, each as a developer leaf then a blind verifier, ticking that phase's mark (`tick-ledger.sh --phase`) with that phase's commit ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 96 | 0.70 |
| `SKILL.md` rejects an expand, migrate or contract (b) phase's commit that `transform-touches-tests.sh` exits 1 on, and a contract (a) phase's commit that `production-frozen.sh` exits 1 on ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 105 | 0.72 |
| `SKILL.md` starts a phased step's contract only once `no-product-caller.sh` on the old interface exits 0 ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 68 | 0.58 |
| `SKILL.md` spends one refactor of the budget for a whole phased step, not one per phase ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 69 | 0.59 |
| `SKILL.md`: a contract phase that exhausts `REVISE_BUDGET` is reset to its own base sha, the expand and migrate commits are kept, and the contract is filed under the ledger's `## Owed steps` ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 74 | 0.62 |
| `SKILL.md` accepts a `⟦replaces-case⟧` group step's Green only once the conductor's own run of `mutation-parity.sh` on that step's pairs table exits 0 ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 76 | 0.62 |
| `SKILL.md` accepts a contract (a) phase only once the conductor's own run of `mutation-parity.sh` on that phase's pairs table exits 0 ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 68 | 0.58 |
| `SKILL.md` puts `mutation-parity.sh`'s report into the PR body as the pairs table, and each row it reports `owed` into the PR body under `## Owed by a human` ⟦criterion 3⟧ | 2 | 0/5 | structural-owed | PASS | 0 | 123 | 0.98 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 3/3 | budget-spent |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 4 | 1 | 2 | 1 | 2 | 2 | 1 | 1 | 3 | 0 | 1 | 1 | 2 | 2 | 1 | 1 | 4 | 5 | 5 | 0 | 1 | 1 | 2 | 2 | 1 | 0 | 1 | 4 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 2 | 1 | 0 | 1 | 2 | 2 | 3 | 2 | 3 | 0 | 1 | 14 | 15 | 0 | 141 | 15 | 14 | 15 | 0 | 8 | 0 | 141 | 16 | 15 | 16 | 0 | 140 | 16 | 16 | 16 | 0 | 0 | 144 | 0 | 7 | 16 | 16 | 135 | 0 | 15 | 15 | 0 | 139 | 16 | 16 | 17 | 0 | 0 | 135 | 18 | 18 | 18 | 0 | 141 | 19 | 20 | 0 | 149 | 21 | 4 | 5 | 23 | 21 | 2 | 2 | 23 | 2 | 2 |
| fast | 21 | 21 | 22 | 22 | 23 | 22 | 24 | 24 | 24 | 23 | 23 | 24 | 21 | 23 | 23 | 22 | 22 | 22 | 24 | 24 | 23 | 24 | 23 | 22 | 23 | 24 | 24 | 24 | 24 | 25 | 23 | 23 | 22 | 24 | 24 | 24 | 22 | 22 | 24 | 23 | 23 | 24 | 24 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 16 | 16 | 16 | 0 | 16 | 14 | 16 | 16 | 0 | 18 | 19 | 20 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 762 | 1494 | 270435 | 36259653 | 4622068 | 39.66 |
