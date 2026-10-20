### 📊 Metrics — issue 1867

Wall time for the issue: 1038 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1899.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 12 | 2 | 4 | 1371 | 46075 | 14829 | 0.06 |
| red | 5 | 2 | 0 | 0 | 105 | 91 | 19 | 38 | 6930 | 535106 | 83988 | 0.33 |
| green | 4 | 2 | 0 | 0 | 83 | 48 | 12 | 24 | 3131 | 306287 | 52892 | 0.19 |
| refactor | 4 | 2 | 0 | 0 | 82 | 57 | 21 | 36 | 4085 | 499900 | 56605 | 0.23 |
| pin | 1 | 1 | 0 | 0 | 12 | 9 | 3 | 6 | 750 | 74453 | 12644 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 128 | 82 | 25 | 50 | 6406 | 634869 | 108199 | 0.40 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 168 | 135 | 32 | 58 | 9861 | 826952 | 112759 | 0.46 |

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
| A run with no end event and no live conductor, and no conductor log in either the run's `.tdd/` or the clone's `.tdd/`, exits 2 with `stop-reason.sh: no conductor log at <path>` on stderr (the path of the clone's `.tdd/conductor-<n>.log`, the last place looked) and nothing on stdout, never a generic exception; a small unit case driven in-process through run_cli ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 80 | 22 | 42 | 5789 | 561109 | 88528 | 0.34 | 211 | unknown | 1/5 | nothing-structural |  |  | full |
| A run with no end event and no live conductor whose conductor log sits in the run's own `.tdd/` (`.tdd/wt/<n>/.tdd/conductor-<n>.log`) reports from that log, and prefers it over a different conductor log in the clone's `.tdd/`; a small unit case driven in-process through run_cli ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 93 | 26 | 48 | 6387 | 664699 | 87109 | 0.35 | 201 | unknown | 1/5 | nothing-structural |  |  | full |
| A run with no end event and no live conductor whose conductor log is absent from the run's `.tdd/` but present in the clone's `.tdd/` (`.tdd/conductor-<n>.log`) reports from the clone's log; a small unit case driven in-process through run_cli ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 7 | 14 | 2720 | 189938 | 30492 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A run with no end event and no live conductor, and no conductor log in either the run's `.tdd/` or the clone's `.tdd/`, exits 2 with `stop-reason.sh: no conductor log at <path>` on stderr (the path of the clone's `.tdd/conductor-<n>.log`, the last place looked) and nothing on stdout, never a generic exception; a small unit case driven in-process through run_cli ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 33 | 0.11 |
| A run with no end event and no live conductor whose conductor log sits in the run's own `.tdd/` (`.tdd/wt/<n>/.tdd/conductor-<n>.log`) reports from that log, and prefers it over a different conductor log in the clone's `.tdd/`; a small unit case driven in-process through run_cli ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 49 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 |
| fast | 5 | 5 | 6 | 6 | 6 | 6 |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 57 | 108 | 16267 | 1461821 | 220958 | 0.86 |
