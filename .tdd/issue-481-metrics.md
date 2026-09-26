### 📊 Metrics — issue 481

Wall time for the issue: 5196 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 10 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/483.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 40 | 35 | 5 | 10 | 3621 | 219642 | 48558 | 0.50 |
| red | 21 | 11 | 0 | 0 | 853 | 714 | 178 | 346 | 67485 | 8554607 | 960551 | 10.75 |
| green | 20 | 10 | 0 | 0 | 2370 | 823 | 205 | 404 | 78346 | 9521283 | 874368 | 10.47 |
| refactor | 20 | 10 | 0 | 0 | 953 | 501 | 125 | 248 | 47911 | 5350268 | 820914 | 8.60 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md's *Scope & plan* writes a criterion whose only observable is that the repository's test command passes as one ledger line `- [ ] <criterion> ⟦full-suite⟧ ⟦criterion k⟧`, recorded as covered by the full-suite run and not planned as a Red/Green step ⟦criterion 1⟧ | 7 | 4 | 0 | 0 | 0 | 0 | 217 | 51 | 102 | 19824 | 2341737 | 306710 | 3.32 | 667 | unknown | 0/5 | nothing-left |
| `next-unchecked.sh` skips an unchecked ledger line carrying `⟦full-suite⟧` and prints the first unchecked line without it, so the cycle loop never hands that line to a leaf ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 139 | 41 | 80 | 12400 | 1694422 | 231791 | 2.44 | 275 | unknown | 0/5 | nothing-left |
| SKILL.md's *Draft PR* step ticks every `⟦full-suite⟧` ledger line, with no refactor-pending mark, and the issue-body criterion it finishes, only once the run's last full-suite run before the PR is readied is green — the rebased tip's run when the branch was rebased — and never after a red one ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 255 | 57 | 110 | 24336 | 2733470 | 289683 | 3.35 | 790 | unknown | 0/5 | nothing-left |
| SKILL.md's *Scope & plan* writes a criterion whose deliverable is the record of a manual check as one ledger line `- [ ] <criterion> ⟦human-owed⟧ ⟦criterion k⟧`, marked owed by a human, not planned as a Red/Green step and never handed to a developer leaf ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 225 | 53 | 106 | 21529 | 2527686 | 272154 | 3.11 | 460 | unknown | 1/5 | nothing-left |
| `next-unchecked.sh` skips an unchecked ledger line carrying `⟦human-owed⟧` and prints the first unchecked line without it ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 44 | 88 | 14361 | 1907661 | 233867 | 2.54 | 256 | unknown | 1/5 | nothing-left |
| SKILL.md's *Draft PR* step lists every `⟦human-owed⟧` ledger line in the PR body under an `## Owed by a human` heading, each naming its criterion number, and adds no such section when the ledger holds none ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 219 | 57 | 110 | 21314 | 2647856 | 275435 | 3.16 | 701 | unknown | 0/5 | nothing-left |
| `prompts/verify-plan.md` tells the blind plan verifier to REJECT a plan that turns a criterion whose only observable is the test command passing into a Red/Green step instead of a `⟦full-suite⟧` line ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 194 | 51 | 102 | 18641 | 2503092 | 267206 | 3.01 | 316 | unknown | 0/5 | nothing-left |
| `prompts/verify-plan.md` tells the blind plan verifier to REJECT a plan that turns a criterion whose deliverable is the record of a manual check into a Red/Green step instead of a `⟦human-owed⟧` line ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 199 | 52 | 100 | 20562 | 2297848 | 250049 | 2.87 | 332 | unknown | 2/5 | nothing-left |
| `prompts/verify-plan.md` counts a `⟦full-suite⟧` or `⟦human-owed⟧` line tagged `⟦criterion k⟧` as delivering criterion k, so a plan written the way *Scope & plan* prescribes for either shape passes check 1 ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 218 | 52 | 100 | 20719 | 2383519 | 259213 | 2.97 | 339 | unknown | 0/5 | nothing-left |
| SKILL.md's *Draft PR* entry condition and *Resume*'s go-to-draft-PR condition say that unchecked `⟦full-suite⟧` and `⟦human-owed⟧` lines do not hold a run back from its draft PR, so an issue carrying either shape reaches it with no Red leaf launched for them and no `untestable-criterion` bail ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 214 | 50 | 100 | 20056 | 2388867 | 269725 | 3.04 | 620 | unknown | 0/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 100 | 2 | 101 | 0 | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 99 | 102 | 3 | 0 | 100 | 0 | 0 | 0 | 0 | 0 | 39 | 0 | 100 | 0 | 0 | 1 | 1 | 0 | 4 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 100 | 0 | 100 | 0 | 86 | 2 | 3 | 3 | 0 | 3 | 0 | 3 | 3 | 2 | 2 | 3 | 0 | 2 | 0 | 3 | 0 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 100 | 101 | 100 | 1 |
| fast | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 3 | 3 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 513 | 1008 | 197363 | 23645800 | 2704391 | 30.32 |
