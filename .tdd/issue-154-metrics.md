### 📊 Metrics — issue 154

Wall time for the issue: 0 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 852 s, excluded from it.
Steps done: 1 of 5 planned.
Outcome: the run bailed — untestable-criterion, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 0 | 9 | 1 | 2 | 960 | 11624 | 26589 | 0.12 |
| red | 2 | 0 | 0 | 0 | 0 | 83 | 19 | 38 | 7555 | 898528 | 86823 | 0.60 |
| pin | 1 | 1 | 0 | 0 | 0 | 28 | 6 | 12 | 2129 | 231185 | 38295 | 0.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.21 |
| pin | 0 | 0.00 | 0 | 0.00 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| lane-insulation.test.sh's third case asks build-guards.test.sh, over the tree owing commentary, for only the git-budget case (`ONLY='a build asks git once per script'`) instead of the whole suite, and still reports a suite that dies before its count line (the 18b stderr-as-numbers bug) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 85 | 20 | 40 | 7723 | 946458 | 86110 | 0.61 | unknown | unknown | unknown | unknown |  |  | pin |
| lane-insulation.test.sh no longer runs build-guards.test.sh unfiltered over the planted tree: the whole-suite run is gone and the filtered git-budget case is the only observation that the suite reaches its count line ⟦added⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 26 | 5 | 10 | 1961 | 183255 | 39008 | 0.21 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 0 | 0 | 132 |
| target | 134 | 122 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 26 | 52 | 10644 | 1141337 | 151707 | 0.94 |
