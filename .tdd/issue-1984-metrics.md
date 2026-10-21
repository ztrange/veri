### 📊 Metrics — issue 1984

Wall time for the issue: 1382 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2046.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 13 | 1 | 2 | 758 | 0 | 29542 | 0.08 |
| diff | 6 | 3 | 0 | 0 | 417 | 116 | 34 | 62 | 14283 | 986471 | 146100 | 0.61 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 204 | 51 | 14 | 26 | 4252 | 313926 | 80388 | 0.27 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 229 | 78 | 21 | 38 | 10789 | 672545 | 95254 | 0.41 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| In skills/tdd/scripts/tests/py/test_skill_leaf_env.py, the launch-line scans (the step-title, verdict-step-title, every-step-title, conductor-title, prompt-title and last-done scans) share one staged scripts directory linked once per suite run instead of linking every script anew for each scan, while every launch-line scan the suite makes today is still made, and the case that reports a SKILL.md launch line launched more than once per ledger shape still reports its line number and shape and stays green; test-only, no production script changes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 14 | 24 | 7336 | 426568 | 73677 | 0.30 | 248 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_skill_leaf_env.py, the developer and verifier launch scans through supervise.sh are run once per suite run and their launched trees shared by the cases that read the leaf's VERI_TEST_CMD, its events' issue and step, and its VERI_STEP, instead of each case relaunching every line, while a launch line that no longer passes the run's test command, step, issue or verifier environment through to the leaf is still named by file, line and variable by those cases and by the single-broken-launch-line fixture case; test-only, no production script changes ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 12 | 24 | 5144 | 382540 | 44321 | 0.20 | 158 | n/a | n/a | n/a |  |  | full |
| With the shared staged scripts directory, a recorder still replaces the stage's link rather than writing through it, and the case asserting every script under skills/tdd/scripts is byte-identical after the suite runs is kept and passes; test-only, no production script changes ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 8 | 14 | 1803 | 177363 | 28102 | 0.11 | 131 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| fast | 7 | 7 | 7 |
| affected | 63 | 31 | 30 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 35 | 64 | 15041 | 986471 | 175642 | 0.69 |
