### 📊 Metrics — issue 155

Wall time for the issue: 0 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1501 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/567.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 0 | 7 | 1 | 2 | 928 | 10120 | 27890 | 0.12 |
| red | 5 | 1 | 0 | 0 | 0 | 117 | 28 | 54 | 14216 | 1042929 | 181525 | 1.08 |
| pin | 3 | 3 | 0 | 0 | 0 | 40 | 12 | 24 | 4226 | 409400 | 100344 | 0.53 |
| green | 2 | 1 | 0 | 0 | 0 | 35 | 14 | 26 | 3766 | 499721 | 67803 | 0.41 |
| refactor | 3 | 1 | 0 | 0 | 0 | 50 | 11 | 22 | 3487 | 408970 | 70109 | 0.40 |
| structural | 2 | 0 | 0 | 0 | 0 | 43 | 15 | 20 | 5785 | 378475 | 71208 | 0.42 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.42 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `make -C projects/docs test` fails and names a fixture suite that runs one case, then references an unbound variable under `set -u` and exits 0 ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 13 | 26 | 6279 | 514582 | 70416 | 0.45 | unknown | unknown | unknown | unknown |  |  | pin |
| a fixture suite ending in its count line with `0 failed` and exit 0 still passes `make -C projects/docs test` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 9 | 16 | 3681 | 277069 | 68033 | 0.36 | unknown | unknown | unknown | unknown |  |  | pin |
| a fixture suite that prints a non-count last line and exits 3 is reported as nothing to do, not as a suite that never reached its count line, and does not fail the target ⟦criterion 2⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 122 | 34 | 66 | 11279 | 1236544 | 208536 | 1.19 | 0 | unknown | 1/5 | structural-owed |  |  | full |
| a second suite added under `projects/docs/tests/` beside an existing one is checked by the unedited runner: it is named when it never reaches its count line ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 9 | 18 | 4456 | 332825 | 72796 | 0.40 | unknown | unknown | unknown | unknown |  |  | pin |
| structural | 2 | 0 | 0 | 0 | 0 | 0 | 43 | 15 | 20 | 5785 | 378475 | 71208 | 0.42 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| a fixture suite that prints a non-count last line and exits 3 is reported as nothing to do, not as a suite that never reached its count line, and does not fail the target ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 0 | 0.40 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 2 | 0 | 2 | 2 |
| target | 1 | 1 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |
| fast | 18 | 4 | 4 | 4 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 81 | 148 | 32408 | 2749615 | 518879 | 2.95 |
