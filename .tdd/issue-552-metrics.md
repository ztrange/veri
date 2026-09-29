### 📊 Metrics — issue 552

Wall time for the issue: 12275 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/553.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 41 | 33 | 4 | 8 | 3080 | 113365 | 72521 | 0.66 |
| red | 17 | 8 | 0 | 0 | 897 | 490 | 126 | 246 | 46976 | 5832778 | 758672 | 8.18 |
| green | 30 | 8 | 7 | 0 | 7469 | 1086 | 257 | 508 | 106409 | 12415842 | 1096284 | 13.38 |
| refactor | 16 | 8 | 0 | 0 | 947 | 412 | 106 | 210 | 40657 | 4752405 | 678852 | 7.20 |
| pin | 1 | 1 | 0 | 0 | 60 | 17 | 5 | 10 | 1749 | 204092 | 40055 | 0.40 |
| structural | 14 | 0 | 0 | 0 | 875 | 198 | 57 | 114 | 17039 | 2171233 | 511008 | 4.86 |
| transform | 5 | 5 | 0 | 0 | 447 | 110 | 28 | 54 | 10051 | 1077479 | 183066 | 1.88 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 7565 | 13.22 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Given a stub whose PR rollup shows a previous head's green while the sha's own check runs (`gh api repos/<owner>/<repo>/commits/<sha>/check-runs`) are still in progress, wait-ci.sh exits 3 ⟦criterion 3⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 350 | 85 | 170 | 34443 | 4175336 | 393420 | 4.67 | 2167 | 2/2 | 0/5 | nothing-left |  |  | full |
| wait-ci.sh exits 1 when the given sha's own check runs hold a completed failure, even while the PR rollup reads all green ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 226 | 61 | 120 | 22719 | 2834101 | 317569 | 3.56 | 1170 | 1/2 | 1/5 | structural-owed |  |  | full |
| wait-ci.sh reads every page of the given sha's check runs, so a failed run beyond the first page of results still exits 1 ⟦added⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 247 | 57 | 112 | 24988 | 2573942 | 302927 | 3.44 | 1284 | 1/2 | 1/5 | structural-owed |  |  | full |
| wait-ci.sh exits 0 when the given sha's own check runs and statuses have all succeeded, even while the PR rollup still shows a previous head's failed or pending checks ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 257 | 61 | 122 | 24635 | 2956225 | 324590 | 3.68 | 1319 | 1/2 | 1/5 | structural-owed |  |  | full |
| wait-ci.sh exits 3, never 0, when every one of the given sha's own check runs concluded skipped ⟦added⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 208 | 56 | 112 | 19864 | 2512396 | 296293 | 3.27 | 1137 | 1/2 | 0/5 | structural-owed |  |  | full |
| wait-ci.sh exits 1 when a legacy status context of the sha, read from `gh api repos/<owner>/<repo>/commits/<sha>/status`, is in a failure or error state, even when the sha's check runs all succeeded ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 298 | 69 | 136 | 28374 | 3247665 | 318998 | 3.77 | 1571 | 1/2 | 1/5 | structural-owed |  |  | full |
| wait-ci.sh exits 3 when a legacy status context of the sha, read from its `/status` endpoint, is still pending, even when the sha's check runs all succeeded ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 126 | 37 | 72 | 11915 | 1557994 | 247861 | 2.53 | 409 | unknown | 0/5 | structural-owed |  |  | full |
| No check runs and no statuses for the given sha is pending: wait-ci.sh exits 3, never 0 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 17 | 34 | 5964 | 824919 | 87361 | 0.98 | unknown | unknown | unknown | unknown |  |  | pin |
| Called with no head-sha argument, wait-ci.sh reads the PR's current head sha and judges that sha's own check runs and statuses, never the PR rollup | 6 | 3 | 0 | 0 | 0 | 0 | 233 | 51 | 96 | 22889 | 2522539 | 284844 | 3.24 | 748 | unknown | 1/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Given a stub whose PR rollup shows a previous head's green while the sha's own check runs (`gh api repos/<owner>/<repo>/commits/<sha>/check-runs`) are still in progress, wait-ci.sh exits 3 ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 73 | 0.80 |
| wait-ci.sh exits 1 when the given sha's own check runs hold a completed failure, even while the PR rollup reads all green ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 108 | 0.94 |
| wait-ci.sh reads every page of the given sha's check runs, so a failed run beyond the first page of results still exits 1 ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 149 | 0.94 |
| wait-ci.sh exits 0 when the given sha's own check runs and statuses have all succeeded, even while the PR rollup still shows a previous head's failed or pending checks ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 148 | 0.97 |
| wait-ci.sh exits 3, never 0, when every one of the given sha's own check runs concluded skipped ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 91 | 0.86 |
| wait-ci.sh exits 1 when a legacy status context of the sha, read from `gh api repos/<owner>/<repo>/commits/<sha>/status`, is in a failure or error state, even when the sha's check runs all succeeded ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 137 | 1.02 |
| wait-ci.sh exits 3 when a legacy status context of the sha, read from its `/status` endpoint, is still pending, even when the sha's check runs all succeeded ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 91 | 0.79 |
| Called with no head-sha argument, wait-ci.sh reads the PR's current head sha and judges that sha's own check runs and statuses, never the PR rollup | 1 | 1/5 | structural-owed | PASS | 0 | 150 | 0.87 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 5/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 16 | 16 | 17 | 17 | 27 | 19 | 25 | 0 | 15 | 16 | 16 | 16 | 18 | 18 | 16 | 1 | 16 | 17 | 17 | 19 | 18 | 16 | 16 | 16 | 16 | 17 | 16 | 19 | 20 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 19 | 20 | 0 | 18 | 18 | 18 | 0 | 20 | 18 | 18 | 17 | 20 | 18 | 18 | 18 | 18 | 19 | 18 | 18 | 21 | 18 | 19 | 18 | 18 | 43 | 45 | 43 | 43 | 43 | 44 | 44 | 44 | 43 | 44 | 44 | 44 | 43 | 0 | 46 | 43 | 43 | 43 | 43 | 43 | 44 | 44 | 43 | 46 | 43 |
| fast | 7 | 8 | 8 | 6 | 7 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 7 | 6 | 7 | 6 | 7 | 7 | 6 | 7 | 6 | 7 | 6 | 6 | 6 | 7 | 6 | 7 | 7 | 7 | 7 | 7 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 19 | 0 | 18 | 16 | 16 | 16 | 16 | 17 | 17 | 17 | 17 | 17 | 17 | 18 | 18 | 18 | 19 | 19 | 43 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 569 | 538 | 539 | 542 | 540 | 539 | 539 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 583 | 1150 | 225961 | 26567194 | 3340458 | 36.56 |
