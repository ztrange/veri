### 📊 Metrics — issue 1273

Wall time for the issue: 3502 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1409.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 10 | 1 | 2 | 1405 | 12489 | 34870 | 0.15 |
| diff | 6 | 3 | 0 | 0 | 489 | 87 | 36 | 70 | 10075 | 1578497 | 252044 | 1.27 |
| red | 3 | 0 | 0 | 0 | 176 | 161 | 42 | 74 | 21886 | 2378332 | 195609 | 1.24 |
| pin | 3 | 3 | 0 | 0 | 80 | 59 | 17 | 34 | 7176 | 778284 | 134981 | 0.69 |
| green | 8 | 3 | 1 | 0 | 795 | 165 | 62 | 122 | 19453 | 3005565 | 367862 | 1.97 |
| refactor | 6 | 3 | 0 | 0 | 541 | 79 | 33 | 62 | 8535 | 1391315 | 262511 | 1.27 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 13 | 1 | 0 | 1017 | 222 | 76 | 146 | 26420 | 3263385 | 598581 | 2.99 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 1077 | 339 | 115 | 218 | 42110 | 5881097 | 649296 | 3.61 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 527 | 0.94 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| the gh-fixture harness case '#588 a ready PR registered by the suite's stubs is not lost when another registers between its read of the PR lines and its write of prs.json' is retired from skills/tdd/scripts/tests/parallel-conductors.test.sh with no replacement, since it pins the suite's own lib/gh-fixture.sh stub registration and no behaviour of parallel-conductors.sh, and no other case of the suite is changed ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 15 | 28 | 3310 | 655600 | 86178 | 0.44 | 146 | n/a | n/a | n/a |  |  | full |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary reports a ready PR as '#<n> — done <pr-url>', a draft PR whose event log ends in a bail as '#<n> — bailed <pr-url>' and a draft PR whose log does not end in one as never bailed; a conductor whose supervisor exits 2 as '#<n> — killed after <VERI_RUN_TIMEOUT>s'; and prints one line per issue in launch order, then one line naming what stopped the loop: replaces 'a ready PR is reported '#<n> — done <pr-url>', a draft PR whose event log ends in a bail '#<n> — bailed <pr-url>', and a draft PR whose log does not end in one never bailed', 'a conductor its supervisor killed (supervise exit 2) is reported '#<n> — killed after <VERI_RUN_TIMEOUT>s'', 'the report prints one line per issue in launch order, then one line naming what stopped the loop' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 108 | 39 | 74 | 13284 | 1825209 | 282474 | 1.45 | 372 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary prints 'parked <n>' for a conductor that halts writing .tdd/parked/<n>.md, gives its slot to the next solvable issue and never launches <n> again, and never stops new launches for it or reports it as a bail with or without --continue-on-bail, even when its draft PR's log ends in one; the first bail stops new launches while running conductors finish and --continue-on-bail keeps launching and skips the bailed number; and the first kill stops new launches: replaces 'a conductor that halts writing .tdd/parked/<n>.md prints 'parked <n>', its slot takes the next solvable issue even without --continue-on-bail and with its draft PR's log ending in a bail, and <n> is not launched again while still solvable', 'a parked conductor does not stop new launches, with or without --continue-on-bail, and is never reported as a bail even when its draft PR's log ends in one', 'the first bail stops new launches while running conductors finish, and --continue-on-bail keeps launching and skips the bailed number', 'the first kill stops new launches: #8 is never launched after #7 is killed' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 208 | 67 | 126 | 25106 | 3322494 | 379665 | 2.10 | 784 | 1/2 | 1/5 | nothing-structural |  |  | already-satisfied |
| parallel-conductors.sh driven through run_cli with conductors and gh faked at their process boundaries exits 0 all done, 1 on a bail or a kill, 2 on plumbing and 3 with nothing solvable, with .tdd/parallel.exit carrying the final code on every exit path; and against a gh that refuses GraphQL with the 403 and answers REST in two pages, or serves open PRs over three pages and refuses repositories/{id} with the proxy's 403, prints the same report and exit code as against a single-page working gh: replaces 'exit 0 all done, 1 a bail or a kill, 2 plumbing, 3 nothing solvable, and .tdd/parallel.exit carries the final code on every exit path', '#568 against a gh that refuses GraphQL with the 403 and answers REST in two pages, the draft PR on the second, parallel-conductors.sh prints the same report and exit code as against a working gh', '#592 against a gh that serves open PRs over three pages on repos/{owner}/{repo}, the draft PR on the third, and refuses repositories/{id} with the proxy's 403, parallel-conductors.sh prints the same report and exit code as against a single-page fixture holding the same PRs' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 48 | 92 | 18660 | 2405793 | 298824 | 1.62 | 701 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| make hermetic's slice of parallel-conductors.test.sh in tests/hermetic/hermetic-suites.test.sh still matches the suite after the removals — its markers and its assertion count updated or the slice dropped — so the slice's own check does not report that the markers moved ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 12 | 24 | 3519 | 541240 | 82473 | 0.42 | 253 | n/a | n/a | n/a |  |  | full |
| parallel-conductors.test.sh's remaining cases still pass; if none remain the file is gone, no guard table, roster, workflow comment or CLAUDE.md count outside .tdd/ and docs/ names it, and CLAUDE.md's suite count matches the tree ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 9 | 18 | 3246 | 381657 | 83393 | 0.40 | 167 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary reports a ready PR as '#<n> — done <pr-url>', a draft PR whose event log ends in a bail as '#<n> — bailed <pr-url>' and a draft PR whose log does not end in one as never bailed; a conductor whose supervisor exits 2 as '#<n> — killed after <VERI_RUN_TIMEOUT>s'; and prints one line per issue in launch order, then one line naming what stopped the loop: replaces 'a ready PR is reported '#<n> — done <pr-url>', a draft PR whose event log ends in a bail '#<n> — bailed <pr-url>', and a draft PR whose log does not end in one never bailed', 'a conductor its supervisor killed (supervise exit 2) is reported '#<n> — killed after <VERI_RUN_TIMEOUT>s'', 'the report prints one line per issue in launch order, then one line naming what stopped the loop' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 70 | 0.39 |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary prints 'parked <n>' for a conductor that halts writing .tdd/parked/<n>.md, gives its slot to the next solvable issue and never launches <n> again, and never stops new launches for it or reports it as a bail with or without --continue-on-bail, even when its draft PR's log ends in one; the first bail stops new launches while running conductors finish and --continue-on-bail keeps launching and skips the bailed number; and the first kill stops new launches: replaces 'a conductor that halts writing .tdd/parked/<n>.md prints 'parked <n>', its slot takes the next solvable issue even without --continue-on-bail and with its draft PR's log ending in a bail, and <n> is not launched again while still solvable', 'a parked conductor does not stop new launches, with or without --continue-on-bail, and is never reported as a bail even when its draft PR's log ends in one', 'the first bail stops new launches while running conductors finish, and --continue-on-bail keeps launching and skips the bailed number', 'the first kill stops new launches: #8 is never launched after #7 is killed' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 69 | 0.47 |
| parallel-conductors.sh driven through run_cli with conductors and gh faked at their process boundaries exits 0 all done, 1 on a bail or a kill, 2 on plumbing and 3 with nothing solvable, with .tdd/parallel.exit carrying the final code on every exit path; and against a gh that refuses GraphQL with the 403 and answers REST in two pages, or serves open PRs over three pages and refuses repositories/{id} with the proxy's 403, prints the same report and exit code as against a single-page working gh: replaces 'exit 0 all done, 1 a bail or a kill, 2 plumbing, 3 nothing solvable, and .tdd/parallel.exit carries the final code on every exit path', '#568 against a gh that refuses GraphQL with the 403 and answers REST in two pages, the draft PR on the second, parallel-conductors.sh prints the same report and exit code as against a working gh', '#592 against a gh that serves open PRs over three pages on repos/{owner}/{repo}, the draft PR on the third, and refuses repositories/{id} with the proxy's 403, parallel-conductors.sh prints the same report and exit code as against a single-page fixture holding the same PRs' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 402 | 0.42 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 22 | 21 | 21 | 22 | 24 | 23 | 24 | 23 | 23 | 22 | 22 | 23 | 23 | 24 | 24 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 20 | 1 | 0 | 18 | 17 | 25 | 1 | 1 | 1 | 13 | 344 | 12 | 0 | 0 | 0 | 1 | 9 | 9 | 9 | 344 | 40 | 12 |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 191 | 364 | 68530 | 9144482 | 1247877 | 6.59 |
