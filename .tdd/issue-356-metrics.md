### 📊 Metrics — issue 356

Wall time for the issue: 4563 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/382.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 11 | 5 | 0 | 0 | 753 | 685 | 134 | 240 | 53398 | 6153681 | 525272 | 9.67 |
| green | 12 | 5 | 1 | 0 | 1631 | 707 | 161 | 302 | 56708 | 7576942 | 561733 | 10.83 |
| refactor | 10 | 5 | 0 | 0 | 1304 | 906 | 141 | 266 | 67805 | 7554206 | 516937 | 10.64 |
| pin | 1 | 1 | 0 | 0 | 40 | 34 | 7 | 14 | 2048 | 301040 | 38269 | 0.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 423 | 2.99 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `red-divergence.sh` given a report with `PREDICTION: DIVERGED` exits 0 and prints the report's `PREDICTED_FAILURE:`, `FAIL_OUTPUT:` and `PREDICTION_NOTE:` values ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 437 | 84 | 154 | 33331 | 3674858 | 351227 | 6.18 | 885 | 1/2 | 0/5 | nothing-structural |
| `red-divergence.sh` given a report with `PREDICTION: MATCHED` exits 3 and prints nothing ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 293 | 67 | 126 | 21568 | 3019284 | 257250 | 4.62 | 420 | unknown | 2/5 | nothing-structural |
| `red-divergence.sh` given a report with no `PREDICTION:` line, or a value other than `MATCHED`/`DIVERGED`, exits 2 ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 97 | 24 | 48 | 7427 | 1170038 | 84770 | 1.62 | 140 | unknown | unknown | unknown |
| SKILL.md's Red section runs `red-divergence.sh` on the leaf's report and, on exit 0 or 2, skips verify-red and verify-pin, writes `.tdd/verify-red.reason`, emits `prediction-diverged` and enters the red revise loop ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 515 | 90 | 168 | 41618 | 4588632 | 322139 | 6.56 | 880 | unknown | 2/5 | structural-owed |
| The prompt `build-develop-prompt.sh revise red …` builds ends with `PREDICTED_FAILURE:` and `PREDICTION: MATCHED | DIVERGED` report lines ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 422 | 89 | 162 | 35253 | 4415323 | 301257 | 6.10 | 957 | unknown | 1/5 | structural-owed |
| SKILL.md's revise loop runs `red-divergence.sh` on a revise-red report before re-verifying, and on exit 0 or 2 spends the next attempt without launching the verifier ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 568 | 89 | 164 | 40762 | 4717734 | 325568 | 6.63 | 1020 | unknown | 3/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 52 | 62 | 0 | 57 | 55 | 1 | 1 | 1 | 194 | 193 | 1 | 1 | 2 | 0 | 0 | 48 | 58 | 49 | 49 | 52 | 60 |
| fast | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 173 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 443 | 822 | 179959 | 21585869 | 1642211 | 31.72 |
