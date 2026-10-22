### 📊 Metrics — issue 1989

Wall time for the issue: 1030 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2107.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 742 | 17051 | 13035 | 0.04 |
| red | 6 | 2 | 0 | 0 | 163 | 106 | 31 | 62 | 11281 | 945233 | 115823 | 0.50 |
| green | 4 | 2 | 0 | 0 | 142 | 56 | 18 | 36 | 4874 | 489271 | 55116 | 0.24 |
| refactor | 4 | 2 | 0 | 0 | 62 | 31 | 11 | 22 | 2255 | 273153 | 52157 | 0.18 |
| pin | 2 | 2 | 0 | 0 | 37 | 20 | 7 | 14 | 2220 | 178580 | 27145 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 9 | 0 | 0 | 189 | 85 | 28 | 56 | 8514 | 706035 | 122247 | 0.46 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 223 | 134 | 40 | 80 | 12858 | 1197253 | 141029 | 0.60 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| supervise refuses develop-green with exit 2 and its existing "has no verify-red PASS after its latest red leaf" message for a step that names ⟦ci-repair⟧ mid-sentence but not among its trailing markers, when the step's latest red leaf has no verify-red PASS (ci_repair_step reads the step's trailing markers the way tests_frozen.py does) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 26 | 52 | 7399 | 721675 | 92406 | 0.38 | 259 | unknown | 0/5 | nothing-left |  |  | full |
| supervise still launches develop-green without a verify-red PASS for a step whose trailing markers include ⟦ci-repair⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 9 | 18 | 3781 | 264464 | 35312 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| build_develop_prompt.py adds no fixture-repair fragment for a step naming ⟦fixture-repair⟧ mid-sentence but not among its trailing markers ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 54 | 22 | 44 | 5903 | 601708 | 87870 | 0.34 | 181 | unknown | 0/5 | nothing-left |  |  | full |
| build_develop_prompt.py still adds the fixture-repair fragment for a step whose trailing markers include ⟦fixture-repair⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 10 | 20 | 3547 | 298390 | 34653 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| supervise refuses develop-green with exit 2 and its existing "has no verify-red PASS after its latest red leaf" message for a step that names ⟦ci-repair⟧ mid-sentence but not among its trailing markers, when the step's latest red leaf has no verify-red PASS (ci_repair_step reads the step's trailing markers the way tests_frozen.py does) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 37 | 0.10 |
| build_develop_prompt.py adds no fixture-repair fragment for a step naming ⟦fixture-repair⟧ mid-sentence but not among its trailing markers ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 25 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 8 | 9 | 8 | 8 | 8 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| fast | 5 | 5 | 5 | 5 | 5 | 6 | 6 |  |  |  |  |  |  |
| target | 3 | 3 | 3 | 3 | 3 | 4 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 68 | 136 | 21372 | 1903288 | 263276 | 1.06 |
