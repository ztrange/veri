### 📊 Metrics — issue 1130

Wall time for the issue: 2421 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1177.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 880 | 12385 | 31207 | 0.14 |
| red | 7 | 3 | 0 | 0 | 377 | 247 | 49 | 90 | 23941 | 2332151 | 345538 | 3.20 |
| green | 8 | 3 | 1 | 0 | 619 | 180 | 50 | 98 | 17073 | 2208160 | 298772 | 2.61 |
| refactor | 6 | 3 | 0 | 0 | 182 | 81 | 27 | 54 | 7247 | 1091892 | 239930 | 1.78 |
| pin | 1 | 1 | 0 | 0 | 53 | 18 | 7 | 14 | 2120 | 305454 | 40777 | 0.25 |
| diff | 2 | 1 | 0 | 0 | 103 | 35 | 12 | 24 | 2950 | 501655 | 75000 | 0.60 |
| predicate | 1 | 0 | 0 | 0 | 11 | 8 | 3 | 6 | 571 | 102550 | 35635 | 0.32 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 12 | 1 | 0 | 592 | 190 | 59 | 118 | 19794 | 2408521 | 467232 | 2.55 |
| developer | claude-opus-5-5 | 13 | 0 | 0 | 0 | 763 | 387 | 90 | 170 | 34988 | 4145726 | 599627 | 6.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 226 | 1.17 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| with its stdout a pipe whose reader has exited, orchestrate.sh exits 2 with one stderr line saying its stdout is gone and no traceback, where it now lets BrokenPipeError escape ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 163 | 42 | 78 | 15067 | 1891246 | 265514 | 2.30 | 507 | unknown | 0/5 | nothing-left |  |  | full |
| with its stdout closed (sys.stdout is None), orchestrate.sh exits 2 with the same one stderr line and no traceback, where it now carries on ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 156 | 42 | 84 | 15165 | 1829156 | 300651 | 2.50 | 453 | 1/2 | 0/5 | nothing-left |  |  | full |
| when its stdout breaks — a pipe whose reader has exited, or closed — the conductor orchestrate.sh launched is stopped by SIGTERM to its process group before orchestrate.sh exits ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 145 | 33 | 64 | 13696 | 1506919 | 268189 | 2.21 | 425 | unknown | 0/5 | nothing-left |  |  | full |
| when its stdout breaks — a pipe whose reader has exited, or closed — solvable-issues.sh is asked no further time after the break ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 16 | 30 | 6453 | 710336 | 90663 | 0.81 | unknown | unknown | unknown | unknown |  |  | pin |
| orchestrate.sh's header lists a broken stdout among the causes of exit 2 ⟦diff-checked⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 43 | 15 | 30 | 3521 | 604205 | 110635 | 0.91 | 121 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| with its stdout a pipe whose reader has exited, orchestrate.sh exits 2 with one stderr line saying its stdout is gone and no traceback, where it now lets BrokenPipeError escape ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 55 | 0.56 |
| with its stdout closed (sys.stdout is None), orchestrate.sh exits 2 with the same one stderr line and no traceback, where it now carries on ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 70 | 0.62 |
| when its stdout breaks — a pipe whose reader has exited, or closed — the conductor orchestrate.sh launched is stopped by SIGTERM to its process group before orchestrate.sh exits ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 57 | 0.59 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 7 | 9 | 7 | 22 | 7 | 8 | 8 | 16 | 8 | 1 | 0 | 0 | 0 | 23 | 23 | 8 | 8 | 0 | 8 | 9 | 8 | 0 |
| fast | 21 | 21 | 21 | 20 | 21 | 21 | 21 | 20 | 20 | 21 | 20 | 21 | 22 |  |  |  |  |  |  |  |  |  |  |
| target | 8 | 8 | 8 | 8 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 149 | 288 | 54782 | 6554247 | 1066859 | 8.88 |
