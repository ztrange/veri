### 📊 Metrics — issue 391

Wall time for the issue: 5266 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/469.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 11 | 2 | 4 | 1020 | 55858 | 34305 | 0.31 |
| red | 8 | 4 | 0 | 0 | 372 | 319 | 71 | 140 | 29731 | 3393350 | 355523 | 4.12 |
| green | 9 | 4 | 0 | 0 | 2850 | 280 | 85 | 162 | 25629 | 3637571 | 374520 | 4.24 |
| refactor | 8 | 4 | 0 | 0 | 1284 | 254 | 60 | 120 | 23299 | 2766856 | 343747 | 3.77 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SCOPE-LOOP.md's Loop 4 stop conditions list an issue that ended in a stop, and say the loop then reports and stops without going back to Loop 1 or selecting another issue ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 1 | 225 | 57 | 110 | 20660 | 2571305 | 304253 | 3.36 | 1747 | unknown | 0/5 | nothing-left |
| SCOPE-LOOP.md says a stop, unlike a bail, has no continue-past option — no --continue-on-bail equivalent, because a stop is the operator speaking ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 50 | 98 | 18971 | 2257098 | 252601 | 2.85 | 666 | unknown | 1/5 | nothing-structural |
| SCOPE-LOOP.md's Loop 5 report gives a stopped issue a `stopped: <mode>` per-issue line alongside the PR url, bailed and skipped forms, and names the stop and the stopped issue's mode as what stopped the loop ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 212 | 50 | 100 | 19781 | 2274339 | 253532 | 2.88 | 1412 | unknown | 1/5 | nothing-structural |
| SCOPE-LOOP.md says re-invoking the same command after a stop resumes the stopped issue from its committed ledger and then carries on draining the scope | 6 | 3 | 0 | 0 | 0 | 0 | 218 | 59 | 114 | 19247 | 2695035 | 263404 | 3.03 | 1045 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 293 | 295 | 299 | 297 | 1 | 1 | 0 | 11 | 13 | 292 | 0 | 1 | 1 | 1 | 294 | 397 | 367 | 0 | 2 | 2 | 2 | 348 | 337 | 2 | 1 | 2 |
| fast | 3 | 2 | 3 | 2 | 3 | 2 | 2 | 3 | 2 | 3 | 3 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 218 | 426 | 79679 | 9853635 | 1108095 | 12.43 |
