### 📊 Metrics — issue 718

Wall time for the issue: 2627 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 13 planned.
Outcome: the run bailed — no-verdict, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 15 | 2 | 4 | 1589 | 60040 | 45338 | 0.41 |
| red | 5 | 2 | 0 | 0 | 181 | 134 | 34 | 66 | 13097 | 1623117 | 233152 | 2.45 |
| pin | 1 | 1 | 0 | 0 | 22 | 17 | 4 | 8 | 1558 | 163255 | 42354 | 0.40 |
| green | 10 | 1 | 3 | 0 | 2016 | 432 | 91 | 182 | 43275 | 5002760 | 416528 | 5.20 |
| refactor | 2 | 1 | 0 | 0 | 90 | 29 | 8 | 16 | 2836 | 339584 | 86026 | 0.81 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 10 | 6 | 3 | 0 | 1593 | 333 | 73 | 146 | 33029 | 3880201 | 396011 | 4.61 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 734 | 294 | 66 | 130 | 29326 | 3308555 | 427387 | 4.67 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 59 | 0.93 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 908 | 4.07 | 1487 | 2.71 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| verify-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| parse-verdict.sh fed output with no VERDICT: line exits 2 with empty stdout and exactly `parse-verdict: no VERDICT: line found` on stderr (a case in tests/parse-verdict.test.sh, written against the bash script before the port) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 14 | 26 | 5173 | 638525 | 90918 | 0.96 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.parse_verdict.main([]) with stdin `VERDICT: MAYBE\nREASON: unsure` returns 2 with nothing on stdout and exactly `parse-verdict: unrecognised verdict word 'MAYBE'` on stderr (tests/py/test_parse_verdict.py), and parse-verdict.sh is removed from migration slice 5's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 299 | 65 | 130 | 28436 | 3230804 | 381835 | 4.27 | 798 | 2/2 | 0/5 | nothing-left |  |  | full |
| veri.parse_verdict.main([]) with stdin `VERDICT: PASS\nREASON: <text>` returns 0 and prints the reason, and `VERDICT: REJECT\nREASON: <text>` returns 1 and prints it (tests/py/test_parse_verdict.py); parse-verdict.sh becomes a /bin/sh shim that execs python3 on veri/parse_verdict.py once per invocation, holding no Python source, keeping a lowercase `usage:` header line and citing no issue number in any comment, with no wrapper turning an uncaught exception into exit 2; every case in tests/parse-verdict.test.sh passes with its assertions unmodified ⟦criterion 2⟧ | 6 | 1 | 1 | 0 | 0 | 0 | 262 | 58 | 116 | 27157 | 3259387 | 305307 | 3.64 | unknown | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.parse_verdict.main([]) with stdin `VERDICT: MAYBE\nREASON: unsure` returns 2 with nothing on stdout and exactly `parse-verdict: unrecognised verdict word 'MAYBE'` on stderr (tests/py/test_parse_verdict.py), and parse-verdict.sh is removed from migration slice 5's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 90 | 0.81 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 7 | 4 | 0 | 2 | 7 | 4 | 4 | 1 | 3 | 1 | 5 | 0 | 8 | 8 | 1 | 0 | 1 | 1 | 6 | 136 |
| target | 1 | 1 | 1 | 0 | 1 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 35 | 37 | 37 | 39 | 41 | 42 | 41 | 41 | 39 | 38 | 39 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 139 | 276 | 62355 | 7188756 | 823398 | 9.27 |
