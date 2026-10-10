### 📊 Metrics — issue 1401

Wall time for the issue: 6638 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1405.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 7 | 2 | 4 | 734 | 65616 | 41792 | 0.18 |
| red | 6 | 3 | 0 | 0 | 279 | 128 | 33 | 62 | 10802 | 1493908 | 280924 | 2.14 |
| green | 6 | 3 | 0 | 0 | 2943 | 118 | 43 | 82 | 11885 | 2098676 | 291721 | 2.37 |
| refactor | 6 | 3 | 0 | 0 | 1263 | 123 | 36 | 72 | 12330 | 1811540 | 291970 | 2.32 |
| predicate | 1 | 0 | 0 | 0 | 15 | 9 | 3 | 6 | 792 | 118367 | 42051 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 10 | 0 | 0 | 707 | 119 | 40 | 78 | 12607 | 1680176 | 437887 | 2.05 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 3805 | 266 | 77 | 148 | 23936 | 3907931 | 510571 | 5.35 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| run_cli over a throwaway module whose main raises an uncaught exception (not SystemExit) gives exit 2 and exactly the one stderr line `<script>.sh: <Type>: <reason>` that entry.run(main, argv) gives a shell caller ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 136 | 44 | 82 | 13798 | 2128365 | 297524 | 2.46 | 2108 | unknown | 1/5 | nothing-structural |  |  | full |
| run_cli over a throwaway module whose main returns a string gives exit 1 and that string on stderr, as entry.run(main, argv) does ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 95 | 31 | 62 | 9584 | 1484308 | 279974 | 2.11 | 1244 | unknown | 0/5 | nothing-left |  |  | full |
| run_cli over a throwaway module whose main raises BrokenPipeError gives exit 141, as entry.run(main, argv) does ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 147 | 40 | 78 | 12427 | 1909818 | 329168 | 2.65 | 1358 | unknown | 1/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| run_cli over a throwaway module whose main raises an uncaught exception (not SystemExit) gives exit 2 and exactly the one stderr line `<script>.sh: <Type>: <reason>` that entry.run(main, argv) gives a shell caller ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 992 | 0.89 |
| run_cli over a throwaway module whose main returns a string gives exit 1 and that string on stderr, as entry.run(main, argv) does ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 99 | 0.65 |
| run_cli over a throwaway module whose main raises BrokenPipeError gives exit 141, as entry.run(main, argv) does ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 172 | 0.78 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 809 | 810 | 58 | 2 | 809 | 2 | 1 | 57 | 817 | 2 | 59 | 1 |
| fast | 60 | 57 | 59 | 57 | 59 | 61 | 58 | 58 | 59 |  |  |  |  |  |
| target | 2 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 117 | 226 | 36543 | 5588107 | 948458 | 7.39 |
