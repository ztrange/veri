### 📊 Metrics — issue 2695

Wall time for the issue: 2861 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2696.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.48 over 55 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 85991 tokens, largest 156958 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 85991 |
| 2 | $0.07 | 92623 |
| 3 | $0.03 | 93843 |
| 4 | $0.03 | 95741 |
| 5 | $0.02 | 96081 |
| 6 | $0.02 | 96424 |
| 7 | $0.02 | 96761 |
| 8 | $0.02 | 97028 |
| 9 | $0.02 | 97255 |
| 10 | $0.02 | 97555 |
| 11 | $0.02 | 98046 |
| 12 | $0.03 | 98810 |
| 13 | $0.03 | 100307 |
| 14 | $0.02 | 100798 |
| 15 | $0.05 | 105129 |
| 16 | $0.04 | 107693 |
| 17 | $0.02 | 108041 |
| 18 | $0.03 | 108832 |
| 19 | $0.03 | 109366 |
| 20 | $0.04 | 111958 |
| 21 | $0.03 | 112728 |
| 22 | $0.08 | 120096 |
| 23 | $0.03 | 120733 |
| 24 | $0.03 | 121019 |
| 25 | $0.03 | 121584 |
| 26 | $0.03 | 121982 |
| 27 | $0.04 | 123529 |
| 28 | $0.03 | 124371 |
| 29 | $0.03 | 124984 |
| 30 | $0.04 | 127037 |
| 31 | $0.03 | 127873 |
| 32 | $0.03 | 128223 |
| 33 | $0.09 | 136256 |
| 34 | $0.04 | 138245 |
| 35 | $0.03 | 138856 |
| 36 | $0.04 | 140367 |
| 37 | $0.03 | 141065 |
| 38 | $0.04 | 142514 |
| 39 | $0.04 | 143656 |
| 40 | $0.03 | 144431 |
| 41 | $0.04 | 145897 |
| 42 | $0.03 | 146580 |
| 43 | $0.03 | 147066 |
| 44 | $0.03 | 147466 |
| 45 | $0.04 | 148828 |
| 46 | $0.04 | 149681 |
| 47 | $0.04 | 151532 |
| 48 | $0.04 | 152340 |
| 49 | $0.04 | 154025 |
| 50 | $0.04 | 155035 |
| 51 | $0.03 | 155490 |
| 52 | $0.03 | 155731 |
| 53 | $0.03 | 155950 |
| 54 | $0.04 | 156430 |
| 55 | $0.04 | 156958 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 950 | 0 | 32236 | 0.09 |
| red | 5 | 2 | 0 | 0 | 214 | 75 | 26 | 50 | 8825 | 776799 | 121864 | 0.47 |
| pin | 2 | 2 | 0 | 0 | 50 | 21 | 6 | 12 | 2326 | 158146 | 31930 | 0.12 |
| green | 7 | 2 | 1 | 0 | 549 | 95 | 32 | 62 | 10238 | 900730 | 119878 | 0.59 |
| red-missing | 1 | 0 | 0 | 0 | 50 | 26 | 6 | 12 | 2723 | 250362 | 30768 | 0.13 |
| refactor | 2 | 0 | 0 | 0 | 15 | 8 | 4 | 8 | 638 | 98150 | 30942 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 543 | 93 | 29 | 56 | 10009 | 764098 | 134105 | 0.51 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 345 | 139 | 46 | 90 | 15691 | 1420089 | 233513 | 0.98 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 425 | 0.46 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When the merge commit GitHub reports never shows up in the clone after any fetch, queued-merge prints "is not in the clone after a fetch", lists `tag` in the "merged, but cleanup failed" summary and exits 2 (a small case in tests/py/unit/test_queued_merge.py that sets VERI_FETCH_RETRY_SLEEP so it never sleeps) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 10 | 20 | 3400 | 298553 | 54596 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| When the merge commit is absent after the first fetch and present after a later one, queued-merge fetches again a bounded number of times, waiting between attempts for VERI_FETCH_RETRY_SLEEP read as a tunable so tests never sleep, then tags that commit, pushes the tag and exits 0 (a small case in tests/py/unit/test_queued_merge.py) ⟦criterion 1⟧ | 10 | 3 | 1 | 0 | 0 | 0 | 141 | 43 | 86 | 15217 | 1327920 | 193536 | 0.86 | 819 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| When `git fetch origin` itself exits non-zero, queued-merge's message names the failed fetch and its exit code rather than a missing commit, and `tag` is still listed as failed with exit 2 (a small case in tests/py/unit/test_queued_merge.py) ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 55 | 21 | 38 | 6133 | 557714 | 87250 | 0.34 | 342 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When the merge commit is absent after the first fetch and present after a later one, queued-merge fetches again a bounded number of times, waiting between attempts for VERI_FETCH_RETRY_SLEEP read as a tunable so tests never sleep, then tags that commit, pushes the tag and exits 0 (a small case in tests/py/unit/test_queued_merge.py) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| When `git fetch origin` itself exits non-zero, queued-merge's message names the failed fetch and its exit code rather than a missing commit, and `tag` is still listed as failed with exit 2 (a small case in tests/py/unit/test_queued_merge.py) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 6 | 4 | 7 | 26 | 7 | 6 | 29 | 8 | 9 | 8 |
| target | 3 | 4 | 2 | 3 | 2 | 3 | 3 | 8 | 7 |  |  |
| fast | 28 | 25 | 23 | 36 | 34 | 30 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 75 | 146 | 25700 | 2184187 | 367618 | 3.97 (estimate) |
