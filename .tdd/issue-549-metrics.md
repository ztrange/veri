### 📊 Metrics — issue 549

Wall time for the issue: 17912 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/610.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 16 | 2 | 4 | 1650 | 58234 | 37309 | 0.34 |
| red | 18 | 8 | 0 | 0 | 1931 | 675 | 148 | 286 | 64433 | 7119299 | 851465 | 9.53 |
| green | 20 | 8 | 2 | 0 | 7461 | 758 | 196 | 386 | 74083 | 9493957 | 836362 | 10.07 |
| refactor | 15 | 7 | 0 | 0 | 1766 | 443 | 108 | 214 | 43457 | 5054738 | 652813 | 7.10 |
| pin | 2 | 2 | 0 | 0 | 211 | 64 | 11 | 20 | 3912 | 411033 | 82306 | 0.82 |
| rebase | 3 | 1 | 0 | 0 | 2613 | 93 | 28 | 56 | 8667 | 1489100 | 126474 | 1.48 |
| structural | 8 | 0 | 0 | 0 | 384 | 100 | 29 | 58 | 8808 | 1080820 | 291587 | 2.73 |
| transform | 2 | 2 | 0 | 0 | 183 | 29 | 9 | 18 | 2639 | 348960 | 72762 | 0.70 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 8678 | 7.40 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| with no `total-seconds` argument (omitted or empty), `wait-ci.sh`'s total bound is 2 × the mean wall time (`updatedAt − startedAt`) of the 5 most recent runs of the CI workflow whose conclusion is `success` or `failure`, read through `gh run list`, skipped and cancelled runs not counted — the deadline recorded in `.tdd/ci-deadline-<sha>` is that many seconds after the first call ⟦criterion 1⟧ | 15 | 5 | 2 | 0 | 0 | 0 | 639 | 136 | 268 | 64557 | 6781244 | 640399 | 7.77 | 5577 | 2/2 | 4/5 | structural-owed |  |  | full |
| the computed total bound is never more than 600 s, however slow the last 5 runs were ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 143 | 39 | 78 | 13223 | 1739378 | 249752 | 2.61 | 984 | unknown | 0/5 | nothing-left |  |  | full |
| when fewer than 5 success/failure CI runs exist, the total bound falls back to 540 s and `wait-ci.sh` says so on stderr, naming that fewer than 5 runs were found ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 178 | 50 | 98 | 17384 | 2396645 | 279477 | 3.06 | 1480 | unknown | 1/5 | structural-owed |  |  | full |
| when `gh run list` fails, the total bound falls back to 540 s and `wait-ci.sh` says so on stderr, naming that `gh` could not answer ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 240 | 54 | 102 | 21929 | 2462989 | 267314 | 3.07 | 946 | unknown | 1/5 | nothing-structural |  |  | full |
| one `wait-ci.sh` call's slice is never longer than 540 s: a `slice-seconds` argument above 540 is capped to 540, so a call still returns exit 3 within 540 s while a longer total bound spans calls ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 179 | 48 | 96 | 17362 | 2289506 | 264265 | 2.92 | 860 | unknown | 1/5 | structural-owed |  |  | full |
| an explicit `total-seconds` argument overrides the computed bound (no `gh run list` reading needed), but a value above 600 is capped at 600 ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 197 | 48 | 92 | 17883 | 2166158 | 264275 | 2.91 | 858 | unknown | 1/5 | structural-owed |  |  | full |
| `workflow-timeouts.test.sh` fails a workflow job that declares a `timeout-minutes` above 10, naming the job, and every job in `.github/workflows/ci.yml` passes it (the `gates` job's 8 is not raised) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 84 | 15 | 30 | 5832 | 706399 | 86542 | 0.95 | unknown | unknown | unknown | unknown |  |  | pin |
| the Draft PR step in `skills/tdd/SKILL.md` calls `wait-ci.sh` without a fixed total (no `1800`) and its prose states the bound's rule — twice the mean of the last 5 completed CI runs, capped at 10 minutes, 540 s fallback — not a number standing for it ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 207 | 57 | 112 | 20745 | 2807556 | 279615 | 3.21 | 596 | unknown | 0/5 | nothing-left |  |  | full |
| repair the full-suite failure: wait-ci.test.sh's #544 case ("wait-ci.sh keeps its total bound separate from one call's slice … and SKILL.md's Draft PR step passes that total bound") fails with "SKILL.md passes wait-ci.sh no total bound" now that the Draft PR step deliberately omits the total so wait-ci.sh computes it — the case must keep pinning the slice/total separation without requiring SKILL.md to pass a fixed total ⟦added⟧ ⟦criterion 6⟧ | 7 | 4 | 0 | 0 | 0 | 1 | 195 | 53 | 104 | 18276 | 2567212 | 290543 | 3.20 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| with no `total-seconds` argument (omitted or empty), `wait-ci.sh`'s total bound is 2 × the mean wall time (`updatedAt − startedAt`) of the 5 most recent runs of the CI workflow whose conclusion is `success` or `failure`, read through `gh run list`, skipped and cancelled runs not counted — the deadline recorded in `.tdd/ci-deadline-<sha>` is that many seconds after the first call ⟦criterion 1⟧ | 2 | 4/5 | structural-owed | PASS | 0 | 578 | 1.79 |
| the computed total bound is never more than 600 s, however slow the last 5 runs were ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 146 | 0.81 |
| when fewer than 5 success/failure CI runs exist, the total bound falls back to 540 s and `wait-ci.sh` says so on stderr, naming that fewer than 5 runs were found ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 308 | 0.90 |
| when `gh run list` fails, the total bound falls back to 540 s and `wait-ci.sh` says so on stderr, naming that `gh` could not answer ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 170 | 0.90 |
| one `wait-ci.sh` call's slice is never longer than 540 s: a `slice-seconds` argument above 540 is capped to 540, so a call still returns exit 3 within 540 s while a longer total bound spans calls ⟦criterion 3⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 292 | 1.02 |
| an explicit `total-seconds` argument overrides the computed bound (no `gh run list` reading needed), but a value above 600 is capped at 600 ⟦criterion 4⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 210 | 0.85 |
| the Draft PR step in `skills/tdd/SKILL.md` calls `wait-ci.sh` without a fixed total (no `1800`) and its prose states the bound's rule — twice the mean of the last 5 completed CI runs, capped at 10 minutes, 540 s fallback — not a number standing for it ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 62 | 0.83 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 2/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 83 | 79 | 81 | 76 | 78 | 77 | 77 | 78 | 78 | 112 | 112 | 79 | 114 | 0 | 82 | 82 | 79 | 83 | 83 | 84 | 118 | 81 | 80 | 80 | 79 | 80 | 30 | 3 | 78 | 79 | 79 | 79 | 79 | 79 | 45 | 0 | 46 | 48 | 49 | 49 | 81 | 0 | 49 | 49 | 49 | 48 | 0 | 49 | 48 | 81 | 46 | 47 | 0 | 0 | 3 | 3 | 0 | 135 | 0 | 123 | 3 | 46 | 33 | 34 | 35 | 35 | 34 | 37 | 34 | 39 | 35 | 35 | 3 |
| fast | 15 | 13 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 11 | 12 | 12 | 12 | 11 | 13 | 11 | 11 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 80 | 78 | 77 | 79 | 81 | 94 | 80 | 80 | 45 | 48 | 46 | 1 | 0 | 0 | 3 | 47 | 46 | 43 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 888 | 919 | 865 | 877 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 531 | 1042 | 207649 | 25056141 | 2951078 | 32.78 |
