### 📊 Metrics — issue 1603

Wall time for the issue: 1028 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1604.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 2 | 4 | 1087 | 59294 | 35348 | 0.16 |
| red | 9 | 4 | 0 | 0 | 208 | 144 | 50 | 100 | 16349 | 2161677 | 355618 | 1.80 |
| green | 8 | 4 | 0 | 0 | 441 | 123 | 47 | 88 | 12338 | 1825638 | 295150 | 1.49 |
| refactor | 8 | 4 | 0 | 0 | 224 | 63 | 27 | 52 | 6033 | 951114 | 287143 | 1.30 |
| pin | 1 | 1 | 0 | 0 | 13 | 8 | 3 | 6 | 896 | 106292 | 36303 | 0.16 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 14 | 0 | 0 | 528 | 193 | 64 | 128 | 19477 | 2539950 | 510851 | 2.49 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 370 | 155 | 65 | 122 | 17226 | 2564065 | 498711 | 2.42 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| replaces_case.parse, given a step text that names the replaces-case mark but carries no replaces clause with a quoted case, returns None instead of raising AttributeError ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 65 | 29 | 52 | 7103 | 1025770 | 219016 | 1.05 | 278 | unknown | 0/5 | nothing-left |  |  | full |
| verify.sh green, run with --step text that names the replaces-case mark but carries no replaces clause with a quoted case ... in a suite path, returns the verifier's verdict: exit 0 and the verifier's reason on a PASS, not exit 2 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 32 | 64 | 9642 | 1366975 | 234103 | 1.17 | 299 | unknown | 0/5 | nothing-left |  |  | full |
| unreplaced-cases.sh, given a step that names the replaces-case mark but carries no replaces clause with a quoted case ... in a suite path, exits 0 and prints no case name, not exit 2 with a traceback ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 68 | 27 | 54 | 7230 | 1084910 | 221879 | 1.07 | 264 | unknown | 0/5 | nothing-left |  |  | full |
| replaces_case.parse, given a step with a quoted replaces clause naming a case but no in-suite-path clause after it, does not raise ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 84 | 28 | 54 | 7706 | 1082515 | 219504 | 1.06 | 292 | unknown | 0/5 | nothing-left |  |  | full |
| verify.sh green, run with --step text carrying a quoted replaces clause naming a case but no in-suite-path clause after it, returns the verifier's verdict: exit 0 and the verifier's reason on a PASS, not exit 2 ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 11 | 22 | 3935 | 484551 | 79712 | 0.41 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| replaces_case.parse, given a step text that names the replaces-case mark but carries no replaces clause with a quoted case, returns None instead of raising AttributeError ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 63 | 0.32 |
| verify.sh green, run with --step text that names the replaces-case mark but carries no replaces clause with a quoted case ... in a suite path, returns the verifier's verdict: exit 0 and the verifier's reason on a PASS, not exit 2 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 61 | 0.34 |
| unreplaced-cases.sh, given a step that names the replaces-case mark but carries no replaces clause with a quoted case ... in a suite path, exits 0 and prints no case name, not exit 2 with a traceback ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 46 | 0.32 |
| replaces_case.parse, given a step with a quoted replaces clause naming a case but no in-suite-path clause after it, does not raise ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 54 | 0.32 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 7 | 0 | 11 | 0 | 1 | 11 | 0 | 8 | 0 | 0 | 0 | 1 | 12 | 1 | 0 | 0 | 0 | 9 |
| fast | 37 | 30 | 40 | 29 | 26 | 26 | 24 | 25 | 25 | 33 | 27 | 33 |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 129 | 250 | 36703 | 5104015 | 1009562 | 4.92 |
