### 📊 Metrics — issue 1736

Wall time for the issue: 1289 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1767.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 20 | 16 | 4 | 8 | 1898 | 96017 | 27303 | 0.10 |
| red | 7 | 2 | 0 | 0 | 122 | 90 | 35 | 68 | 10958 | 1014778 | 124811 | 0.52 |
| pin | 3 | 3 | 0 | 0 | 37 | 27 | 10 | 20 | 2966 | 259100 | 39973 | 0.16 |
| green | 4 | 2 | 0 | 0 | 108 | 43 | 17 | 34 | 4143 | 466259 | 54782 | 0.23 |
| refactor | 4 | 2 | 0 | 0 | 65 | 25 | 13 | 24 | 2290 | 311191 | 53094 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 10 | 1 | 0 | 191 | 103 | 39 | 76 | 11057 | 1002517 | 150797 | 0.59 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 161 | 98 | 40 | 78 | 11198 | 1144828 | 149166 | 0.60 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.git/` (already satisfied by the existing skip: a regression pin, test only, no production change) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 9 | 18 | 2646 | 268737 | 34832 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.tdd/wt/<n>/`, another run's worktree (already satisfied by the existing skip: a regression pin, test only, no production change) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 8 | 14 | 2934 | 195419 | 34479 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.venv/` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 56 | 23 | 44 | 5864 | 600252 | 85415 | 0.33 | 185 | unknown | 0/5 | nothing-left |  |  | full |
| wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `node_modules/` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 58 | 25 | 50 | 5708 | 693864 | 85591 | 0.34 | 215 | unknown | 0/5 | nothing-left |  |  | full |
| wrong-test-route answers exit 3 `revise` when a green report names a real case of the repo's own tests only on lines other than `WRONG_TEST:` (already satisfied by the existing line filter: a regression pin, test only, no production change) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 10 | 20 | 3205 | 293056 | 32343 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.venv/` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.09 |
| wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `node_modules/` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 31 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 2 | 0 | 1 | 1 |
| target | 0 | 0 | 0 | 1 | 8 | 1 | 16 | 0 | 0 | 0 |  |  |  |
| fast | 10 | 14 | 14 | 13 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 79 | 154 | 22255 | 2147345 | 299963 | 1.19 |
