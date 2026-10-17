### 📊 Metrics — issue 1605

Wall time for the issue: 4909 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1695.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 41 | 31 | 6 | 12 | 3281 | 201397 | 71970 | 0.34 |
| red | 10 | 5 | 0 | 0 | 574 | 243 | 62 | 120 | 18621 | 2604363 | 411688 | 2.09 |
| green | 10 | 5 | 0 | 0 | 830 | 160 | 53 | 102 | 13008 | 2030429 | 355565 | 1.76 |
| refactor | 10 | 5 | 0 | 0 | 1743 | 224 | 59 | 110 | 15278 | 2248152 | 369310 | 1.86 |
| predicate | 3 | 0 | 0 | 0 | 57 | 43 | 11 | 22 | 2304 | 393660 | 97510 | 0.45 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 17 | 16 | 1 | 0 | 2381 | 402 | 100 | 190 | 28930 | 3829337 | 624386 | 3.17 |
| developer | claude-sonnet-5-5 | 18 | 0 | 0 | 0 | 864 | 299 | 91 | 176 | 23562 | 3648664 | 681657 | 3.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When `git fetch -q origin` fails, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the failed fetch of origin, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 103 | 30 | 60 | 7586 | 1222036 | 223036 | 1.09 | 433 | unknown | 0/5 | nothing-left |  |  | full |
| When `git ls-remote origin refs/heads/<default>` fails after a successful fetch, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the failed ls-remote of the default branch, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 109 | 34 | 66 | 9476 | 1363248 | 222621 | 1.12 | 452 | unknown | 1/5 | structural-owed |  |  | full |
| When `origin/<default>` after the fetch is not the sha `ls-remote` reports, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the stale remote-tracking ref, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 136 | 39 | 72 | 10821 | 1507723 | 228807 | 1.17 | 1077 | unknown | 0/5 | nothing-left |  |  | full |
| When `git rebase -q <onto>` fails while a rebase was already in progress before it ran, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the rebase already in progress, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 135 | 32 | 62 | 9552 | 1277659 | 231909 | 1.15 | 450 | unknown | 0/5 | nothing-left |  |  | full |
| When `git rebase -q <onto>` fails without leaving a rebase in progress, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the rebase refused without a conflict, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 9 | 3 | 0 | 0 | 0 | 0 | 187 | 50 | 94 | 11776 | 1905938 | 327700 | 1.62 | 1107 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When `git fetch -q origin` fails, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the failed fetch of origin, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 106 | 0.34 |
| When `git ls-remote origin refs/heads/<default>` fails after a successful fetch, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the failed ls-remote of the default branch, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 146 | 0.40 |
| When `origin/<default>` after the fetch is not the sha `ls-remote` reports, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the stale remote-tracking ref, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 686 | 0.39 |
| When `git rebase -q <onto>` fails while a rebase was already in progress before it ran, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the rebase already in progress, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 96 | 0.36 |
| When `git rebase -q <onto>` fails without leaving a rebase in progress, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the rebase refused without a conflict, a line distinct from every other exit-2 refusal's stderr line (a small in-process case with git faked) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 709 | 0.37 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 33 | 33 | 33 | 33 | 0 | 37 | 33 | 33 | 33 | 34 | 34 | 33 | 34 | 0 | 33 | 0 | 620 | 32 | 6 | 33 | 33 | 0 | 0 | 33 | 15 | 0 | 33 | 33 | 0 | 615 |
| fast | 16 | 16 | 16 | 16 | 16 | 16 | 15 | 16 | 18 | 16 | 16 | 16 | 16 | 16 | 17 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 16 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 191 | 366 | 52492 | 7478001 | 1306043 | 6.50 |
