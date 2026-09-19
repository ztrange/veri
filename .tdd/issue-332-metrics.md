### 📊 Metrics — issue 332

Wall time for the issue: 3013 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/348.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 9 | 2 | 0 | 0 | 426 | 371 | 63 | 120 | 34338 | 2669746 | 380021 | 5.99 |
| green | 6 | 2 | 1 | 0 | 1435 | 185 | 41 | 80 | 16637 | 1698818 | 232965 | 3.60 |
| refactor | 4 | 2 | 0 | 0 | 408 | 84 | 18 | 36 | 8031 | 684677 | 146516 | 2.01 |
| pin | 5 | 5 | 0 | 0 | 275 | 94 | 25 | 48 | 8525 | 897225 | 177905 | 2.44 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 775 | 2.51 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| no-size-assertion.test.sh's probe makes exactly one grep invocation across the whole scanned directory before any per-file work, counted by a PATH-first counting shim in front of grep and sed, never a wall-clock measurement ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 33 | 66 | 14394 | 1329804 | 223434 | 3.26 | 1023 | unknown | 1/5 | structural-owed |
| against a fixture directory of N suites where only M (M < N) contain a size-verb line, the counting shim shows the probe's per-file subjects()/classification forks bounded by M, not N ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 11 | 20 | 5308 | 410416 | 78152 | 1.12 | unknown | unknown | unknown | unknown |
| a suite whose only size-verb line is inside a comment (`# wc -c the old way`) is still not reported by no-size-assertion.test.sh ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 12 | 22 | 5312 | 436218 | 76144 | 1.11 | unknown | unknown | unknown | unknown |
| a suite binding a variable to CLAUDE.md or SKILL.md three lines above the line that measures it (`doc="$ROOT/CLAUDE.md"` then `wc -c < "$doc"`) is still reported by no-size-assertion.test.sh, naming the suite and line ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 11 | 22 | 4708 | 443941 | 75315 | 1.09 | unknown | unknown | unknown | unknown |
| a suite that measures something else entirely with wc/stat/du is still not reported by no-size-assertion.test.sh ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 13 | 26 | 5716 | 549742 | 79818 | 1.22 | unknown | unknown | unknown | unknown |
| no-size-assertion.test.sh run against the current tree still ends in the same `<n> passed, <m> failed` outcome as before the restructure ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 259 | 50 | 96 | 24445 | 2051121 | 317418 | 4.81 | 1168 | 1/2 | 1/5 | structural-owed |
| every no-size-assertion.test.sh assertion that passed before still passes, and make test is green ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 81 | 17 | 32 | 7648 | 729224 | 87126 | 1.43 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 147 | 284 | 67531 | 5950466 | 937407 | 14.04 |
