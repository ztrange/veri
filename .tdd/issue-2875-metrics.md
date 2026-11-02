### 📊 Metrics — issue 2875

Wall time for the issue: 6588 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2879.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.37 over 42 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87081 tokens, largest 172403 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87081 |
| 2 | $0.09 | 95797 |
| 3 | $0.04 | 97917 |
| 4 | $0.02 | 98425 |
| 5 | $0.02 | 98969 |
| 6 | $0.05 | 102875 |
| 7 | $0.06 | 107875 |
| 8 | $0.04 | 109750 |
| 9 | $0.04 | 111909 |
| 10 | $0.03 | 112688 |
| 11 | $0.04 | 114972 |
| 12 | $0.03 | 115909 |
| 13 | $0.09 | 124531 |
| 14 | $0.07 | 129886 |
| 15 | $0.05 | 132592 |
| 16 | $0.05 | 135992 |
| 17 | $0.04 | 137095 |
| 18 | $0.05 | 139688 |
| 19 | $0.04 | 140773 |
| 20 | $0.05 | 143372 |
| 21 | $0.05 | 145593 |
| 22 | $0.05 | 148494 |
| 23 | $0.04 | 150169 |
| 24 | $0.04 | 151410 |
| 25 | $0.04 | 152514 |
| 26 | $0.03 | 152739 |
| 27 | $0.04 | 153327 |
| 28 | $0.03 | 153657 |
| 29 | $0.03 | 153928 |
| 30 | $0.03 | 154214 |
| 31 | $0.03 | 154646 |
| 32 | $0.03 | 154932 |
| 33 | $0.03 | 155215 |
| 34 | $0.03 | 155595 |
| 35 | $0.06 | 159138 |
| 36 | $0.04 | 159911 |
| 37 | $0.05 | 162410 |
| 38 | $0.04 | 163765 |
| 39 | $0.06 | 167498 |
| 40 | $0.05 | 169778 |
| 41 | $0.05 | 171381 |
| 42 | $0.04 | 172403 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER haiku, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-haiku-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 7 | 1 | 2 | 952 | 0 | 32177 | 0.09 |
| red | 4 | 1 | 0 | 0 | 311 | 143 | 30 | 52 | 29217 | 1085944 | 165866 | 0.10 |
| green | 4 | 1 | 1 | 0 | 570 | 89 | 28 | 48 | 14939 | 847108 | 90041 | 0.15 |
| pin | 2 | 2 | 0 | 0 | 64 | 27 | 8 | 16 | 3208 | 207903 | 50680 | 0.18 |
| refactor | 1 | 0 | 0 | 0 | 28 | 23 | 3 | 6 | 4724 | 95306 | 29106 | 0.01 |
| diff | 2 | 1 | 0 | 0 | 180 | 24 | 11 | 20 | 3554 | 303957 | 33677 | 0.06 |
| cover | 1 | 0 | 0 | 0 | 34 | 21 | 7 | 12 | 4138 | 197038 | 23232 | 0.01 |
| predicate | 1 | 0 | 0 | 0 | 11 | 8 | 4 | 8 | 1429 | 113108 | 14543 | 0.00 |
| structural | 1 | 0 | 0 | 0 | 9 | 6 | 2 | 4 | 1008 | 48812 | 12623 | 0.00 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 6 | 1 | 0 | 526 | 79 | 23 | 46 | 8665 | 589779 | 145887 | 0.51 |
| developer | claude-haiku-5-5 | 10 | 0 | 0 | 0 | 692 | 269 | 71 | 122 | 54504 | 2309397 | 306058 | 0.09 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 570 | 0.15 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A record whose unmutated run printed only `ok  \t<pkg>\t<time>` and whose mutated run exits non-zero printing a Go test failure (`--- FAIL:` and `FAIL\t<pkg>\t<time>`) counts as red: pin-recheck.sh exits 0, prints no `needs a look`, and the recorded file is restored byte for byte ⟦criterion 1⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 209 | 52 | 92 | 37970 | 1639882 | 241688 | 0.31 | 5613 | unknown | 0/5 | structural-owed |  |  | already-satisfied |
| A record whose unmutated run printed only `ok  \t<pkg>\t<time>` and whose mutated run exits non-zero printing Go's `FAIL\t<pkg> [build failed]` still prints `needs a look: <file> (mutation did not build)` on stdout and exits 1 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 17 | 30 | 14118 | 596379 | 94005 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| The non-Go behaviours of #2827 still hold: the branch leaves unchanged the existing test_2827 cases of skills/tdd/scripts/tests/py/test_pin_recheck_process.py, under which a mutated run printing only `error: build failed` against an unmutated run's result line is unbuilt (exit 1) and one still printing the unmutated run's result lines is red (exit 0) ⟦diff-checked⟧ ⟦criterion 3⟧ | 5 | 1 | 0 | 0 | 0 | 0 | 59 | 24 | 44 | 10129 | 662915 | 84075 | 0.07 | 297 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A record whose unmutated run printed only `ok  \t<pkg>\t<time>` and whose mutated run exits non-zero printing a Go test failure (`--- FAIL:` and `FAIL\t<pkg>\t<time>`) counts as red: pin-recheck.sh exits 0, prints no `needs a look`, and the recorded file is restored byte for byte ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 28 | 0.01 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 15 | 13 | 13 | 9 | 12 | 12 | 12 | 13 | 11 | 8 |  |  |  |  |
| fast | 83 | 94 | 59 | 67 | 67 | 54 |  |  |  |  |  |  |  |  |
| target | 15 | 7 | 6 | 7 | 7 | 8 | 7 | 7 | 1806 | 2325 | 7 | 6 | 7 | 7 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 94 | 168 | 63169 | 2899176 | 451945 | 2.97 (estimate) |
