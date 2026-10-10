### 📊 Metrics — issue 1389

Wall time for the issue: 6399 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1392.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 921 | 12193 | 36189 | 0.16 |
| red | 8 | 3 | 0 | 0 | 320 | 151 | 39 | 78 | 14506 | 1871906 | 375487 | 3.07 |
| pin | 1 | 1 | 0 | 0 | 21 | 13 | 4 | 8 | 1502 | 174733 | 43913 | 0.21 |
| green | 6 | 3 | 0 | 0 | 2943 | 115 | 31 | 60 | 8775 | 1454300 | 238858 | 2.36 |
| refactor | 6 | 3 | 0 | 0 | 382 | 90 | 28 | 56 | 9500 | 1335171 | 281596 | 2.07 |
| diff | 2 | 1 | 0 | 0 | 296 | 38 | 12 | 24 | 2899 | 562825 | 88068 | 0.65 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 12 | 0 | 0 | 866 | 149 | 47 | 94 | 15356 | 2046605 | 522142 | 2.45 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 3107 | 266 | 68 | 134 | 22747 | 3364523 | 541969 | 6.06 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| run_cli answers the integer itself as the exit code when a throwaway module's main returns an integer, and when it raises SystemExit carrying an integer ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 12 | 24 | 4374 | 612265 | 97903 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |
| run_cli answers exit code 0 when a throwaway module's main returns None, raises SystemExit with no code, or raises SystemExit(None) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 119 | 36 | 70 | 11511 | 1776811 | 291208 | 2.30 | 1368 | unknown | 1/5 | nothing-structural |  |  | full |
| run_cli answers exit code 1 when a throwaway module's main raises SystemExit carrying a non-integer object such as a message string, and the captured stderr ends with that object's text followed by a newline ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 92 | 30 | 58 | 9275 | 1368282 | 281393 | 2.07 | 1271 | unknown | 0/5 | structural-owed |  |  | full |
| run_cli answers exit code 1 and writes the object's text followed by a newline to the captured stderr when main raises SystemExit carrying an object that is neither an integer nor a string, such as a float or a tuple ⟦added⟧ ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 118 | 24 | 50 | 9123 | 1078752 | 269350 | 2.54 | 1289 | 1/2 | 0/5 | nothing-structural |  |  | full |
| CLAUDE.md's description of the run_cli fixture states that its exit code is the status the module's .sh entry point would exit with, replacing "takes a SystemExit's code as the exit code" ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 12 | 24 | 2899 | 562825 | 88068 | 0.65 | 326 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| run_cli answers exit code 0 when a throwaway module's main returns None, raises SystemExit with no code, or raises SystemExit(None) ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 202 | 0.83 |
| run_cli answers exit code 1 when a throwaway module's main raises SystemExit carrying a non-integer object such as a message string, and the captured stderr ends with that object's text followed by a newline ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 94 | 0.63 |
| run_cli answers exit code 1 and writes the object's text followed by a newline to the captured stderr when main raises SystemExit carrying an object that is neither an integer nor a string, such as a float or a tuple ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 86 | 0.60 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 1 | 844 | 17 | 2 | 1 | 67 | 2 | 2 | 59 | 818 | 2 | 1 | 2 | 60 | 772 | 2 | 0 | 43 |
| target | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |
| fast | 54 | 68 | 71 | 56 | 57 | 59 | 59 | 56 | 55 | 60 | 63 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 115 | 228 | 38103 | 5411128 | 1064111 | 8.51 |
