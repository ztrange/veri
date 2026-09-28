### 📊 Metrics — issue 544

Wall time for the issue: 2131 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 9 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/548.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 15 | 2 | 4 | 1553 | 57354 | 35894 | 0.33 |
| red | 25 | 11 | 1 | 0 | 3405 | 1051 | 204 | 394 | 100059 | 10041047 | 1124646 | 13.01 |
| green | 29 | 10 | 4 | 0 | 6851 | 1313 | 280 | 540 | 122083 | 13339954 | 1231542 | 14.96 |
| refactor | 20 | 10 | 0 | 0 | 1848 | 613 | 153 | 302 | 58399 | 7236124 | 866897 | 9.55 |
| pin | 1 | 1 | 0 | 0 | 52 | 17 | 4 | 8 | 1619 | 152004 | 38698 | 0.37 |
| structural | 3 | 0 | 0 | 0 | 3230 | 45 | 14 | 28 | 3896 | 568359 | 116022 | 1.12 |
| transform | 2 | 1 | 1 | 0 | 166 | 58 | 14 | 28 | 4901 | 598727 | 83241 | 0.88 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 1716 | 1.85 | 215 | 2.01 |
| green | 5594 | 8.86 | 688 | 2.10 |
| refactor | 0 | 0.00 | 337 | 1.78 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a new `wait-ci.sh <pr-url> [max-seconds]` reads the PR's statusCheckRollup through `gh` and exits 3 while a check is still pending and its bound has not run out, 0 when every check completed SUCCESS, NEUTRAL or SKIPPED, and 1 when a completed check has any other conclusion; an empty rollup is never exit 0 ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 507 | 95 | 184 | 47999 | 4662903 | 415846 | 5.22 | 3112 | 2/2 | 2/5 | nothing-structural |  |  | full |
| `wait-ci.sh`'s bound is enforced across calls, not within one: the deadline is recorded on the first call for the PR's head commit, and a later call that still finds a check pending past that deadline exits 2 rather than starting a fresh bound ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 413 | 79 | 152 | 39377 | 3677846 | 426351 | 4.93 | 2982 | red 1/2, green 1/2 | 1/5 | structural-owed |  |  | full |
| `wait-ci.sh` branches on `__typename`: a legacy StatusContext row with `state` PENDING or EXPECTED and no `status` key counts as pending, never green, and one in FAILURE or ERROR counts as failed ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 162 | 40 | 76 | 15570 | 1675046 | 247924 | 2.63 | 407 | unknown | 1/5 | nothing-structural |  |  | full |
| `wait-ci.sh` reads a legacy StatusContext row whose `state` is SUCCESS as a completed green check: beside a pending CheckRun the rollup still exits 3, beside only green checks it exits 0 ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 12 | 22 | 4952 | 480167 | 82379 | 0.85 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's Draft PR step waits on CI by calling `wait-ci.sh` again on its exit 3, with no wait loop inside one Bash call and no pending test that reads `.status` alone ⟦criterion 1⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 407 | 82 | 158 | 40820 | 4184327 | 388816 | 4.76 | 1436 | 1/2 | 1/5 | structural-owed |  |  | full |
| SKILL.md's Draft PR step stops at a `ci-timeout` or `ci-red` bail: it goes to *Bailing*, and neither the `done` mark nor the `metrics:` commit follows it in that step's command block ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 339 | 75 | 144 | 30701 | 3917038 | 304386 | 3.83 | 1070 | unknown | 2/5 | structural-owed |  |  | full |
| `add-ledger-step.sh` inserts a CI repair step marked `⟦ci-repair⟧` without counting it against `VERI_STEP_GROWTH`, and `next-unchecked.sh` still hands that step over ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 307 | 62 | 124 | 25269 | 2918501 | 307271 | 3.55 | 1155 | 1/2 | 1/5 | nothing-left |  |  | full |
| SKILL.md's Draft PR step appends its CI repair step through that `⟦ci-repair⟧` path and recognises a second red by the `⟦ci-repair⟧` mark on a ledger line, not by matching the repair step's prose ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 210 | 53 | 106 | 18870 | 2584510 | 273905 | 3.09 | 701 | unknown | 1/5 | structural-owed |  |  | full |
| SKILL.md's Draft PR step leaves no CI run on the readied PR that nothing reads: a push after the CI read has its own run read by `wait-ci.sh`, or no push follows the CI read ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 202 | 48 | 92 | 19570 | 2287638 | 286501 | 3.14 | 6358 | unknown | 0/5 | nothing-left |  |  | full |
| `wait-ci.sh`'s total bound across calls is separate from one call's slice: with a total bound of 1800 s and a slice of 540 s, a call made 600 s after the first that still finds a check pending exits 3, not 2, and SKILL.md's Draft PR step passes that total bound ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 251 | 54 | 106 | 24946 | 2616433 | 281075 | 3.27 | unknown | unknown | 1/5 | structural-owed |  |  | full |
| `wait-ci.sh` never reads a rollup whose every check concluded SKIPPED as green: it exits 3 while its bound lasts, because a check skipped on a draft push has not tested the head ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 145 | 41 | 80 | 14086 | 1764720 | 247329 | 2.61 | unknown | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| a new `wait-ci.sh <pr-url> [max-seconds]` reads the PR's statusCheckRollup through `gh` and exits 3 while a check is still pending and its bound has not run out, 0 when every check completed SUCCESS, NEUTRAL or SKIPPED, and 1 when a completed check has any other conclusion; an empty rollup is never exit 0 ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 440 | 1.01 |
| `wait-ci.sh`'s bound is enforced across calls, not within one: the deadline is recorded on the first call for the PR's head commit, and a later call that still finds a check pending past that deadline exits 2 rather than starting a fresh bound ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 84 | 0.90 |
| `wait-ci.sh` branches on `__typename`: a legacy StatusContext row with `state` PENDING or EXPECTED and no `status` key counts as pending, never green, and one in FAILURE or ERROR counts as failed ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 113 | 0.91 |
| SKILL.md's Draft PR step waits on CI by calling `wait-ci.sh` again on its exit 3, with no wait loop inside one Bash call and no pending test that reads `.status` alone ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 81 | 0.93 |
| SKILL.md's Draft PR step stops at a `ci-timeout` or `ci-red` bail: it goes to *Bailing*, and neither the `done` mark nor the `metrics:` commit follows it in that step's command block ⟦criterion 3⟧ | 1 | 2/5 | structural-owed | PASS | 0 | 459 | 1.43 |
| `add-ledger-step.sh` inserts a CI repair step marked `⟦ci-repair⟧` without counting it against `VERI_STEP_GROWTH`, and `next-unchecked.sh` still hands that step over ⟦criterion 6⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 71 | 0.83 |
| SKILL.md's Draft PR step appends its CI repair step through that `⟦ci-repair⟧` path and recognises a second red by the `⟦ci-repair⟧` mark on a ledger line, not by matching the repair step's prose ⟦criterion 4⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 205 | 0.97 |
| SKILL.md's Draft PR step leaves no CI run on the readied PR that nothing reads: a push after the CI read has its own run read by `wait-ci.sh`, or no push follows the CI read ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 58 | 0.81 |
| `wait-ci.sh`'s total bound across calls is separate from one call's slice: with a total bound of 1800 s and a slice of 540 s, a call made 600 s after the first that still finds a check pending exits 3, not 2, and SKILL.md's Draft PR step passes that total bound ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 240 | 0.94 |
| `wait-ci.sh` never reads a rollup whose every check concluded SKIPPED as green: it exits 3 while its bound lasts, because a check skipped on a draft push has not tested the head ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 97 | 0.84 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 144 | 187 | 0 | 109 | 1 | 0 | 157 | 168 | 165 | 6 | 6 | 7 | 0 | 5 | 6 | 6 | 5 | 0 | 160 | 5 | 0 | 6 | 14 | 13 | 9 | 10 | 10 | 10 | 10 | 12 | 2 | 2 | 2 | 3 | 0 | 2 | 106 | 140 | 2 | 3 | 2 | 2 | 120 | 3 | 149 | 133 | 134 | 2 | 3 | 0 | 0 | 0 | 0 | 54 | 1 | 0 | 0 | 1 | 2 | 3 | 111 | 0 | 119 | 123 | 3 | 2 | 3 | 3 | 123 | 121 | 2 | 4 | 1 | 58 | 3 | 3 | 6 | 12 | 12 | 0 | 131 | 1 | 133 | 132 | 0 | 14 | 14 | 13 | 16 | 0 | 19 | 0 | 16 |
| fast | 7 | 7 | 6 | 6 | 7 | 7 | 8 | 7 | 7 | 8 | 7 | 7 | 7 | 7 | 8 | 7 | 8 | 8 | 9 | 7 | 7 | 9 | 7 | 7 | 7 | 6 | 7 | 7 | 8 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 4 | 0 | 4 | 0 | 5 | 6 | 7 | 10 | 12 | 18 | 3 | 3 | 0 | 0 | 2 | 3 | 0 | 2 | 14 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 536 | 571 | 708 | 632 | 564 | 630 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 671 | 1304 | 292510 | 31993569 | 3496940 | 40.23 |
