### 📊 Metrics — issue 1510

Wall time for the issue: 851 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1681.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 952 | 12445 | 33138 | 0.14 |
| red | 1 | 0 | 0 | 0 | 25 | 21 | 5 | 10 | 2405 | 217851 | 40921 | 0.21 |
| pin | 1 | 1 | 0 | 0 | 17 | 13 | 4 | 8 | 1279 | 156110 | 37204 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 26 | 20 | 5 | 10 | 2231 | 168555 | 70342 | 0.32 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 25 | 21 | 5 | 10 | 2405 | 217851 | 40921 | 0.21 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| test_skill_md_reports_a_verifier_whose_supervisor_died_the_way_it_reports_a_killed_developer_leaf in tests/py/test_wait_leaf.py, rewritten in place, passes only while the "Launching a leaf — detach, then wait in the foreground" section of SKILL.md says that wait-leaf.sh verdict-<phase> exiting 2 because its supervisor died is read as a killed-stuck verifier and bailed on, and fails with that paragraph deleted while the script-reference list under "The scripts" is unchanged; a test-only change (no production change, SKILL.md untouched), so the rewritten case passes against the unmodified code and is pinned by a mutation deleting that paragraph ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 3684 | 373961 | 78125 | 0.39 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| affected | 1 |  |
| target | 0 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 10 | 20 | 4636 | 386406 | 111263 | 0.53 |
