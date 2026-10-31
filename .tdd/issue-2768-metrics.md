### 📊 Metrics — issue 2768

Wall time for the issue: 2897 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2771.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.37 over 22 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87063 tokens, largest 129735 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 87063 |
| 2 | $0.07 | 94065 |
| 3 | $0.03 | 95719 |
| 4 | $0.04 | 98029 |
| 5 | $0.02 | 98505 |
| 6 | $0.02 | 98793 |
| 7 | $0.02 | 99051 |
| 8 | $0.04 | 101195 |
| 9 | $0.04 | 103129 |
| 10 | $0.09 | 111264 |
| 11 | $0.05 | 115181 |
| 12 | $0.05 | 118149 |
| 13 | $0.03 | 119351 |
| 14 | $0.04 | 121618 |
| 15 | $0.03 | 122576 |
| 16 | $0.04 | 124038 |
| 17 | $0.04 | 126457 |
| 18 | $0.03 | 127494 |
| 19 | $0.03 | 128298 |
| 20 | $0.03 | 128859 |
| 21 | $0.03 | 129084 |
| 22 | $0.03 | 129735 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 819 | 0 | 32462 | 0.09 |
| red | 3 | 1 | 0 | 0 | 121 | 50 | 19 | 38 | 5972 | 664822 | 93151 | 0.36 |
| pin | 1 | 1 | 0 | 0 | 29 | 12 | 4 | 8 | 1363 | 112809 | 17847 | 0.07 |
| green | 2 | 1 | 0 | 0 | 137 | 27 | 11 | 22 | 3174 | 336512 | 34836 | 0.15 |
| refactor | 1 | 0 | 0 | 0 | 7 | 3 | 2 | 4 | 136 | 49580 | 14840 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 159 | 40 | 13 | 26 | 4433 | 340530 | 84890 | 0.29 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 145 | 59 | 24 | 48 | 7031 | 823193 | 108246 | 0.42 |

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
| With the issue in the started list, `.tdd/wt/<n>/` absent and no `run_conductor.py <n>` process alive, `watch-runs.sh` prints `vanished <n>` and exits 2 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 10 | 20 | 3433 | 298857 | 58685 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| With the issue in the started list, `.tdd/wt/<n>/` absent for several consecutive polls and the issue's `run_conductor.py <n>` process alive, `watch-runs.sh` does not print `vanished` or exit 2 ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 63 | 26 | 52 | 7212 | 864866 | 101989 | 0.41 | 392 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With the issue in the started list, `.tdd/wt/<n>/` absent for several consecutive polls and the issue's `run_conductor.py <n>` process alive, `watch-runs.sh` does not print `vanished` or exit 2 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 4 | 4 | 6 | 7 |
| target | 3 | 9 | 4 | 6 | 35 |
| fast | 39 | 32 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 37 | 74 | 11464 | 1163723 | 193136 | 2.09 (estimate) |
