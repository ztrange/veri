### 📊 Metrics — issue 1143

Wall time for the issue: 2088 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1241.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 9 | 2 | 4 | 1071 | 54956 | 37311 | 0.17 |
| red | 6 | 2 | 1 | 0 | 199 | 172 | 41 | 78 | 17573 | 1936323 | 243878 | 2.30 |
| green | 4 | 2 | 0 | 0 | 227 | 66 | 22 | 44 | 6647 | 930480 | 157308 | 1.24 |
| refactor | 4 | 2 | 0 | 0 | 175 | 99 | 28 | 56 | 10063 | 1309352 | 170285 | 1.49 |
| predicate | 1 | 0 | 0 | 0 | 14 | 10 | 4 | 8 | 901 | 148306 | 35307 | 0.33 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 281 | 104 | 37 | 74 | 11193 | 1510666 | 277434 | 1.52 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 347 | 252 | 60 | 116 | 25062 | 2868751 | 366655 | 4.01 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 140 | 1.56 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| test_build_verify_prompt.py's blindness-contract assertion on the red prompt needs its whole match on one line of the rendered prompt: a red prompt whose contract sentence is split across two lines, or whose `never` and `reason` sit on different lines, makes the case fail ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 209 | 55 | 106 | 21853 | 2579839 | 324289 | 2.98 | 473 | 1/2 | 1/5 | nothing-structural |  |  | full |
| test_build_verify_prompt.py's full-suite assertion on the green prompt needs its whole `full … test … suite` match on one line of the rendered prompt: a green prompt with `full test` on one line and `suite` on the next makes the case fail ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 138 | 40 | 80 | 13331 | 1744622 | 282489 | 2.38 | 310 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| test_build_verify_prompt.py's blindness-contract assertion on the red prompt needs its whole match on one line of the rendered prompt: a red prompt whose contract sentence is split across two lines, or whose `never` and `reason` sit on different lines, makes the case fail ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 92 | 0.80 |
| test_build_verify_prompt.py's full-suite assertion on the green prompt needs its whole `full … test … suite` match on one line of the rendered prompt: a green prompt with `full test` on one line and `suite` on the next makes the case fail ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 83 | 0.69 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 1 |
| fast | 29 | 28 | 26 | 26 | 27 | 28 |  |  |  |  |  |  |  |  |
| target | 30 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 190 | 36255 | 4379417 | 644089 | 5.53 |
