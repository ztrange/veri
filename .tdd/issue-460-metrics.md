### 📊 Metrics — issue 460

Wall time for the issue: 4918 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/461.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 16 | 2 | 4 | 1140 | 54299 | 35401 | 0.32 |
| red | 12 | 4 | 0 | 0 | 798 | 414 | 87 | 172 | 38683 | 3856941 | 501059 | 5.55 |
| green | 8 | 4 | 0 | 0 | 2460 | 264 | 71 | 140 | 23768 | 3191583 | 337513 | 3.81 |
| refactor | 8 | 4 | 0 | 0 | 520 | 149 | 39 | 78 | 13345 | 1581454 | 319749 | 3.14 |
| pin | 4 | 3 | 1 | 0 | 107 | 77 | 19 | 38 | 6860 | 738156 | 151787 | 1.50 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 58 | 0.79 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| An importable Python module under skills/tdd/scripts/lib/ returns the issue numbers a body names under `## Blocked by`, reading both the `#<n>` form and the full `https://github.com/<owner>/<name>/issues/<n>` URL of the given repository ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 161 | 39 | 76 | 15229 | 1651813 | 248149 | 2.62 | 1179 | unknown | 0/5 | nothing-left |
| The blocked-by module returns no blockers for a section reading `None.` and for a body with no `## Blocked by` section at all ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 134 | 35 | 70 | 11524 | 1455176 | 235230 | 2.40 | 845 | unknown | 0/5 | nothing-left |
| The blocked-by module ignores an issue URL naming another repository when a repository slug is given, and reads any github.com issue URL as local when none is ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 150 | 41 | 82 | 13767 | 1786865 | 246725 | 2.61 | 1163 | unknown | 0/5 | structural-owed |
| The blocked-by module stops reading the section at the next `## ` heading, so a `#<n>` under a later heading is not a blocker ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 12 | 24 | 3742 | 496938 | 75994 | 0.78 | unknown | unknown | unknown | unknown |
| solvable-issues.sh takes its blocker parsing from the blocked-by module rather than defining its own, with solvable-issues.test.sh passing unmodified ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 211 | 50 | 98 | 19044 | 2276266 | 257987 | 2.90 | 354 | unknown | 0/5 | nothing-structural |
| A caller that is not solvable-issues.sh can import the blocked-by module and get its answers with no gh, no repository and no child process started ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 13 | 26 | 6478 | 562765 | 81861 | 0.90 | unknown | unknown | unknown | unknown |
| solvable-issues.sh still resolves the main working tree through lib/main-working-tree.sh when run from a scratch scripts directory, so main-working-tree.test.sh passes again (repair: red on the Draft PR full-suite gate) ⟦added⟧ ⟦criterion 4⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 142 | 26 | 52 | 12872 | 1138311 | 164162 | 1.80 | unknown | 1/2 | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 298 | 298 | 297 | 0 | 0 | 0 | 0 | 299 | 302 | 0 | 0 | 0 | 301 | 304 | 301 | 0 | 0 | 0 | 5 | 5 | 6 | 5 | 0 | 1 |
| fast | 2 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 3 | 2 | 3 |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 310 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 218 | 432 | 83796 | 9422433 | 1345509 | 14.33 |
