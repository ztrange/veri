### 📊 Metrics — issue 3089

Wall time for the issue: 6467 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3092.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.02 over 84 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90491 tokens, largest 193693 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90491 |
| 2 | $0.07 | 97553 |
| 3 | $0.03 | 98972 |
| 4 | $0.03 | 100835 |
| 5 | $0.02 | 101136 |
| 6 | $0.02 | 101583 |
| 7 | $0.02 | 101939 |
| 8 | $0.02 | 102261 |
| 9 | $0.02 | 102550 |
| 10 | $0.02 | 103028 |
| 11 | $0.02 | 103311 |
| 12 | $0.03 | 104017 |
| 13 | $0.05 | 108020 |
| 14 | $0.06 | 113355 |
| 15 | $0.07 | 118881 |
| 16 | $0.04 | 121491 |
| 17 | $0.08 | 128608 |
| 18 | $0.05 | 131244 |
| 19 | $0.05 | 134258 |
| 20 | $0.03 | 134617 |
| 21 | $0.03 | 135562 |
| 22 | $0.03 | 136154 |
| 23 | $0.03 | 136850 |
| 24 | $0.03 | 137517 |
| 25 | $0.11 | 147472 |
| 26 | $0.04 | 148195 |
| 27 | $0.04 | 148991 |
| 28 | $0.04 | 150320 |
| 29 | $0.04 | 151501 |
| 30 | $0.04 | 152456 |
| 31 | $0.04 | 153501 |
| 32 | $0.04 | 154417 |
| 33 | $0.04 | 155124 |
| 34 | $0.04 | 155804 |
| 35 | $0.04 | 156565 |
| 36 | $0.04 | 157240 |
| 37 | $0.04 | 157932 |
| 38 | $0.04 | 158680 |
| 39 | $0.04 | 159503 |
| 40 | $0.04 | 160212 |
| 41 | $0.06 | 163266 |
| 42 | $0.04 | 164103 |
| 43 | $0.03 | 164329 |
| 44 | $0.04 | 165014 |
| 45 | $0.04 | 165706 |
| 46 | $0.04 | 166931 |
| 47 | $0.04 | 167456 |
| 48 | $0.04 | 168697 |
| 49 | $0.04 | 169417 |
| 50 | $0.04 | 170225 |
| 51 | $0.04 | 170684 |
| 52 | $0.04 | 171366 |
| 53 | $0.04 | 172125 |
| 54 | $0.04 | 172583 |
| 55 | $0.04 | 173536 |
| 56 | $0.04 | 174540 |
| 57 | $0.04 | 175456 |
| 58 | $0.04 | 175936 |
| 59 | $0.04 | 176291 |
| 60 | $0.04 | 176631 |
| 61 | $0.04 | 177359 |
| 62 | $0.04 | 177992 |
| 63 | $0.05 | 179404 |
| 64 | $0.04 | 180171 |
| 65 | $0.04 | 180923 |
| 66 | $0.04 | 181314 |
| 67 | $0.04 | 182198 |
| 68 | $0.04 | 182751 |
| 69 | $0.04 | 183100 |
| 70 | $0.04 | 183459 |
| 71 | $0.04 | 183782 |
| 72 | $0.04 | 184403 |
| 73 | $0.04 | 184691 |
| 74 | $0.04 | 185116 |
| 75 | $0.04 | 185552 |
| 76 | $0.06 | 188614 |
| 77 | $0.05 | 189760 |
| 78 | $0.04 | 190349 |
| 79 | $0.04 | 191121 |
| 80 | $0.04 | 191860 |
| 81 | $0.04 | 192521 |
| 82 | $0.04 | 192921 |
| 83 | $0.04 | 193382 |
| 84 | $0.04 | 193693 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 11 | 1 | 2 | 1327 | 0 | 32340 | 0.09 |
| diff | 2 | 1 | 0 | 0 | 290 | 46 | 11 | 22 | 4595 | 330552 | 56538 | 0.22 |
| red | 9 | 3 | 0 | 0 | 403 | 238 | 51 | 100 | 19498 | 1690506 | 207927 | 0.88 |
| green | 6 | 3 | 0 | 0 | 820 | 170 | 38 | 72 | 12629 | 1157608 | 123106 | 0.55 |
| refactor | 5 | 2 | 0 | 0 | 192 | 71 | 19 | 38 | 4315 | 526162 | 97749 | 0.34 |
| pin | 3 | 3 | 0 | 0 | 67 | 37 | 9 | 18 | 3319 | 233738 | 44794 | 0.17 |
| predicate | 2 | 0 | 0 | 0 | 29 | 19 | 8 | 16 | 1170 | 196159 | 43530 | 0.14 |
| cover | 1 | 0 | 0 | 0 | 58 | 37 | 10 | 20 | 2688 | 300663 | 16164 | 0.10 |
| structural | 1 | 0 | 0 | 0 | 28 | 19 | 5 | 10 | 1175 | 137989 | 13673 | 0.06 |
| transform | 1 | 0 | 1 | 0 | 47 | 28 | 6 | 12 | 1716 | 148249 | 31124 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 13 | 1 | 0 | 1072 | 253 | 55 | 108 | 18321 | 1471118 | 256812 | 0.97 |
| developer | claude-sonnet-5-5 | 17 | 0 | 0 | 0 | 875 | 423 | 103 | 202 | 34111 | 3250508 | 410133 | 1.69 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 47 | 0.11 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Existing cases in skills/tdd/scripts/tests/py/unit/test_wait_ci.py whose expected outcome rests on wait-ci's three-failed-reads limit reached through a gh failure carrying an HTTP 4xx or 5xx status (the `gh_err` Bad Gateway cases, the `world` helper's Bad Gateway pull, `NOT_FOUND` where it ends a wait as unreadable, the `bad_gateway` page) are changed to fail with a gh error carrying no HTTP status, their expected exit codes, read counts and stderr otherwise unchanged; tests only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 11 | 22 | 4595 | 330552 | 56538 | 0.22 | 385 | n/a | n/a | n/a |  |  | full |
| With every read of a PR's checks failing with HTTP 5xx and the CI deadline passing before any read succeeds, wait-ci.sh exits 2 naming the checks it could not read (small in-process case in test_wait_ci.py, VERI_POLL=0, faked clock and sleep, no real sleeping) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 34 | 66 | 10887 | 1075099 | 128907 | 0.54 | 484 | unknown | 1/5 | structural-owed |  |  | full |
| With the CI deadline not yet passed, more than three consecutive HTTP 5xx failed reads of a PR's checks followed by a successful read do not exit 2: wait-ci.sh returns the later read's answer (small in-process case in test_wait_ci.py, faked clock and sleep, no real sleeping) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 9 | 18 | 4046 | 296689 | 41518 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| Consecutive retries after HTTP 5xx failed reads wait with a growing backoff whose base delay is read from a VERI_* knob, observed as the faked sleep calls' arguments, with no real sleeping (small in-process case in test_wait_ci.py) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 123 | 31 | 60 | 9669 | 940750 | 112719 | 0.47 | 610 | unknown | 1/5 | nothing-structural |  |  | full |
| An HTTP 429 (rate limit) failed read of a PR's checks is retried like an HTTP 5xx: more than three consecutive 429 reads followed by a successful read return the later read's answer, not exit 2 (small in-process case in test_wait_ci.py) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 9 | 16 | 3632 | 254465 | 42272 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| An HTTP 403 failed read whose gh message says the API rate limit was exceeded is retried like an HTTP 5xx: more than three consecutive such reads followed by a successful read return the later read's answer, not exit 2 (small in-process case in test_wait_ci.py) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 10 | 20 | 3813 | 314559 | 37865 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| A failed read of a PR's checks with an HTTP 4xx status other than a rate limit (e.g. HTTP 404) exits 2 on the first read, naming the checks it could not read, with no retry and no sleep (small in-process case in test_wait_ci.py) ⟦criterion 2⟧ | 10 | 2 | 1 | 0 | 0 | 0 | 209 | 53 | 106 | 14463 | 1509512 | 214786 | 0.83 | 654 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With every read of a PR's checks failing with HTTP 5xx and the CI deadline passing before any read succeeds, wait-ci.sh exits 2 naming the checks it could not read (small in-process case in test_wait_ci.py, VERI_POLL=0, faked clock and sleep, no real sleeping) ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 76 | 0.13 |
| Consecutive retries after HTTP 5xx failed reads wait with a growing backoff whose base delay is read from a VERI_* knob, observed as the faked sleep calls' arguments, with no real sleeping (small in-process case in test_wait_ci.py) ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 98 | 0.12 |
| A failed read of a PR's checks with an HTTP 4xx status other than a rate limit (e.g. HTTP 404) exits 2 on the first read, naming the checks it could not read, with no retry and no sleep (small in-process case in test_wait_ci.py) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 18 | 0.09 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 50 | 47 | 35 | 36 | 36 | 31 | 30 | 51 | 35 | 40 |  |  |  |  |  |  |  |  |  |  |  |
| affected | 3 | 4 | 3 | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 4 | 3 | 7 | 4 | 5 | 6 | 4 | 3 | 5 | 6 | 6 |
| target | 5 | 3 | 3 | 2 | 3 | 3 | 7 | 5 | 3 | 4 | 3 | 3 | 3 | 7 | 10 | 9 | 5 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 158 | 310 | 52432 | 4721626 | 666945 | 6.68 (estimate) |
