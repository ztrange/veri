### 📊 Metrics — issue 1318

Wall time for the issue: 2131 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1411.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 15 | 4 | 8 | 1810 | 161938 | 42841 | 0.21 |
| red | 2 | 0 | 0 | 0 | 167 | 148 | 29 | 54 | 14153 | 1931579 | 156975 | 1.93 |
| pin | 2 | 2 | 0 | 0 | 44 | 35 | 11 | 22 | 4113 | 484530 | 85487 | 0.43 |
| green | 4 | 2 | 0 | 0 | 287 | 81 | 27 | 54 | 8082 | 1266539 | 176723 | 1.41 |
| refactor | 4 | 2 | 0 | 0 | 239 | 135 | 36 | 72 | 14221 | 1902731 | 192518 | 1.80 |
| diff | 2 | 1 | 0 | 0 | 119 | 46 | 13 | 26 | 3350 | 565771 | 78232 | 0.63 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 287 | 112 | 38 | 76 | 13309 | 1623703 | 336574 | 1.64 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 587 | 348 | 82 | 160 | 32420 | 4689385 | 396202 | 4.76 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The sha's own check runs (pending, unreadable, failed, neutral/skipped, paged, all-green, all-skipped) are pinned in tests/py/test_wait_ci.py through run_cli with the same exit codes and stderr: replaces 'wait-ci.sh exits 3 while the sha's own check runs are still in progress, even when the PR already reports that sha as its head and its rollup still shows a previous head's green (#552)', 'wait-ci.sh exits 2 naming the sha when gh cannot read that sha's own check runs, even though gh printed a body (#552)', 'wait-ci.sh exits 1 when the sha's own check runs hold a completed failure, even while the PR rollup reads all green (#552)', 'wait-ci.sh never reads a completed NEUTRAL or SKIPPED run among the sha's own check runs as red: with another still in progress it exits 3 (#552)', 'wait-ci.sh reads every page of the sha's own check runs: a failed run beyond the first page exits 1, even while the PR rollup reads all green (#552)', 'wait-ci.sh exits 0 when the sha's own check runs and statuses have all succeeded, even while the PR rollup still shows a previous head's failed or pending checks (#552)', 'wait-ci.sh exits 3, never 0, when every one of the sha's own check runs concluded skipped, even while the PR rollup reads all green (#552)' in skills/tdd/scripts/tests/wait-ci.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 192 | 51 | 100 | 19408 | 2863221 | 313011 | 2.84 | 469 | unknown | 2/5 | structural-owed |  |  | already-satisfied |
| The sha's legacy statuses (failure/error, unreadable or empty /status, pending, none at all) and the no-head-sha form (PR head read over REST, with GraphQL working or refused) are pinned in tests/py/test_wait_ci.py through run_cli with the same exit codes and stderr: replaces 'wait-ci.sh exits 1 when a legacy status context of the sha is in a failure or error state, even while the sha's own check runs all succeeded (#552)', 'wait-ci.sh exits 2 naming the sha when gh cannot read its /status, and reads a /status with no statuses as none, while its own check runs all succeeded (#552)', 'wait-ci.sh exits 3 while a legacy status context of the sha is still pending, even when the sha's own check runs all succeeded (#552)', 'wait-ci.sh exits 3, never 0, while the sha has no check runs and no statuses yet, even when the PR rollup reads all green (#552)', 'wait-ci.sh called with no head-sha reads the PR's head sha and exits 3 while that sha's own check runs are in progress, even when the PR rollup reads all green (#552)', 'wait-ci.sh called with no head-sha against a gh that refuses GraphQL with the 403 and answers REST reads the PR's head sha and exits 0, 1, 3 and 2 on green, red, pending and unreadable checks, the same as against a working gh (#568)' in skills/tdd/scripts/tests/wait-ci.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 207 | 52 | 102 | 21161 | 2722158 | 298692 | 2.72 | 432 | unknown | 2/5 | nothing-structural |  |  | already-satisfied |
| wait-ci.test.sh keeps its remaining cases and still passes, is not deleted, and no guard table, roster, workflow comment or CLAUDE.md count outside .tdd/ and docs/ needs to change; CLAUDE.md's suite counts match the tree ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 13 | 26 | 3350 | 565771 | 78232 | 0.63 | 141 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The sha's own check runs (pending, unreadable, failed, neutral/skipped, paged, all-green, all-skipped) are pinned in tests/py/test_wait_ci.py through run_cli with the same exit codes and stderr: replaces 'wait-ci.sh exits 3 while the sha's own check runs are still in progress, even when the PR already reports that sha as its head and its rollup still shows a previous head's green (#552)', 'wait-ci.sh exits 2 naming the sha when gh cannot read that sha's own check runs, even though gh printed a body (#552)', 'wait-ci.sh exits 1 when the sha's own check runs hold a completed failure, even while the PR rollup reads all green (#552)', 'wait-ci.sh never reads a completed NEUTRAL or SKIPPED run among the sha's own check runs as red: with another still in progress it exits 3 (#552)', 'wait-ci.sh reads every page of the sha's own check runs: a failed run beyond the first page exits 1, even while the PR rollup reads all green (#552)', 'wait-ci.sh exits 0 when the sha's own check runs and statuses have all succeeded, even while the PR rollup still shows a previous head's failed or pending checks (#552)', 'wait-ci.sh exits 3, never 0, when every one of the sha's own check runs concluded skipped, even while the PR rollup reads all green (#552)' in skills/tdd/scripts/tests/wait-ci.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 2/5 | structural-owed | PASS | 0 | 108 | 0.82 |
| The sha's legacy statuses (failure/error, unreadable or empty /status, pending, none at all) and the no-head-sha form (PR head read over REST, with GraphQL working or refused) are pinned in tests/py/test_wait_ci.py through run_cli with the same exit codes and stderr: replaces 'wait-ci.sh exits 1 when a legacy status context of the sha is in a failure or error state, even while the sha's own check runs all succeeded (#552)', 'wait-ci.sh exits 2 naming the sha when gh cannot read its /status, and reads a /status with no statuses as none, while its own check runs all succeeded (#552)', 'wait-ci.sh exits 3 while a legacy status context of the sha is still pending, even when the sha's own check runs all succeeded (#552)', 'wait-ci.sh exits 3, never 0, while the sha has no check runs and no statuses yet, even when the PR rollup reads all green (#552)', 'wait-ci.sh called with no head-sha reads the PR's head sha and exits 3 while that sha's own check runs are in progress, even when the PR rollup reads all green (#552)', 'wait-ci.sh called with no head-sha against a gh that refuses GraphQL with the 403 and answers REST reads the PR's head sha and exits 0, 1, 3 and 2 on green, red, pending and unreadable checks, the same as against a working gh (#568)' in skills/tdd/scripts/tests/wait-ci.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 131 | 0.98 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 12 | 11 | 0 | 11 | 0 | 11 | 1 | 9 | 10 | 9 | 11 | 0 | 10 | 0 | 11 | 10 |
| target | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |  |  |  |  |
| fast | 24 | 24 | 22 | 23 | 24 | 24 | 23 | 24 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 120 | 236 | 45729 | 6313088 | 732776 | 6.40 |
