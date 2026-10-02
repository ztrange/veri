### 📊 Metrics — issue 619

Wall time for the issue: 3369 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/664.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 29 | 23 | 2 | 4 | 2363 | 59177 | 38471 | 0.37 |
| red | 19 | 7 | 1 | 0 | 983 | 768 | 174 | 340 | 69597 | 8774472 | 905848 | 10.39 |
| green | 20 | 6 | 4 | 0 | 1881 | 780 | 192 | 376 | 71791 | 9447348 | 836719 | 10.02 |
| refactor | 12 | 6 | 0 | 0 | 587 | 307 | 78 | 156 | 28615 | 3655336 | 536772 | 5.60 |
| exhausted | 1 | 0 | 0 | 0 | 30 | 26 | 5 | 10 | 2442 | 213918 | 44039 | 0.44 |
| pin | 3 | 3 | 0 | 0 | 143 | 77 | 15 | 30 | 7197 | 622982 | 120008 | 1.23 |
| structural | 4 | 0 | 0 | 0 | 117 | 60 | 14 | 28 | 5180 | 541412 | 155708 | 1.46 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 28 | 23 | 5 | 0 | 1567 | 753 | 181 | 360 | 69681 | 8200926 | 1101591 | 11.85 |
| developer | claude-opus-5-5 | 32 | 0 | 0 | 0 | 2203 | 1288 | 299 | 584 | 117504 | 15113719 | 1535974 | 17.66 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 324 | 3.31 | 0 | 0.00 |
| green | 1996 | 14.50 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| verify-green.md tells the verifier to run `cp <file> <file>.orig` before it mutates the code and `mv <file>.orig <file>` after the run under mutation ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 184 | 52 | 104 | 18071 | 2529357 | 264400 | 2.98 | 481 | unknown | 0/5 | structural-owed |  |  | full |
| verify-pin.md tells the verifier to run `cp <file> <file>.orig` before it mutates the code and `mv <file>.orig <file>` after the run under mutation ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 202 | 51 | 102 | 18757 | 2548736 | 274729 | 3.08 | 560 | unknown | 1/5 | nothing-structural |  |  | full |
| develop-cover.md tells the cover leaf to run `cp <file> <file>.orig` before it mutates the code and `mv <file>.orig <file>` after the run under mutation ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 227 | 55 | 110 | 20240 | 2719198 | 273897 | 3.14 | 493 | unknown | 1/5 | nothing-structural |  |  | full |
| verify-green.md, verify-pin.md and develop-cover.md each confirm the restore by comparing `git diff` with what it printed before the probe, and none of them contains `git checkout --` or `git diff --exit-code` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 268 | 59 | 116 | 23259 | 2985400 | 283603 | 3.33 | 546 | unknown | 1/5 | nothing-structural |  |  | full |
| _shared.md forbids `git checkout -- <file>` and `git restore` for undoing a probe and names `cp <file> <file>.orig` / `mv <file>.orig <file>` as the restore to use instead ⟦criterion 3⟧ | 19 | 4 | 5 | 0 | 0 | 0 | 625 | 140 | 272 | 57822 | 6676350 | 784664 | 8.77 | 745 | green 3/2, red 1/2 | 0/5 | structural-owed |  |  | full |
| _develop-shared.md forbids `git checkout -- <file>` and `git restore` for undoing a probe and names `cp <file> <file>.orig` / `mv <file>.orig <file>` as the restore to use instead ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 225 | 56 | 110 | 20436 | 2806090 | 291239 | 3.30 | 516 | unknown | 0/5 | structural-owed |  |  | full |
| _shared.md and _develop-shared.md still carry their "Never run `git stash`" rule unchanged and still recommend `git show HEAD:<path>` and `git worktree add --detach <scratch> HEAD` for reading the committed version ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 16 | 32 | 6487 | 815393 | 92241 | 1.03 | unknown | unknown | unknown | unknown |  |  | pin |
| no file under skills/tdd/scripts/prompts/ contains `git stash push`, and `git checkout -- <file>` appears only in `_shared.md` and `_develop-shared.md`, inside the sentence that forbids it (criterion 3) — no prompt prescribes it as a restore ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 74 | 15 | 28 | 7048 | 656809 | 87092 | 0.97 | unknown | unknown | unknown | unknown |  |  | pin |
| verify-green.md check 4 and verify-pin.md check 2 still require the restore to happen before the verifier reports, and develop-cover.md step 4 still requires the working tree to be exactly as the leaf found it ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 20 | 38 | 7522 | 976723 | 91521 | 1.08 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| verify-green.md tells the verifier to run `cp <file> <file>.orig` before it mutates the code and `mv <file>.orig <file>` after the run under mutation ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 78 | 0.84 |
| verify-pin.md tells the verifier to run `cp <file> <file>.orig` before it mutates the code and `mv <file>.orig <file>` after the run under mutation ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 120 | 1.03 |
| develop-cover.md tells the cover leaf to run `cp <file> <file>.orig` before it mutates the code and `mv <file>.orig <file>` after the run under mutation ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 121 | 1.05 |
| verify-green.md, verify-pin.md and develop-cover.md each confirm the restore by comparing `git diff` with what it printed before the probe, and none of them contains `git checkout --` or `git diff --exit-code` ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 110 | 0.96 |
| _shared.md forbids `git checkout -- <file>` and `git restore` for undoing a probe and names `cp <file> <file>.orig` / `mv <file>.orig <file>` as the restore to use instead ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 75 | 0.85 |
| _develop-shared.md forbids `git checkout -- <file>` and `git restore` for undoing a probe and names `cp <file> <file>.orig` / `mv <file>.orig <file>` as the restore to use instead ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 83 | 0.88 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 4 | 6 | 7 | 0 | 6 | 4 | 4 | 5 | 88 | 4 | 0 | 4 | 4 | 4 | 7 | 6 | 4 | 4 | 2 | 10 | 4 | 3 | 12 | 11 | 4 | 0 | 3 | 4 | 4 | 5 | 0 | 4 | 4 | 0 | 4 | 4 | 6 | 6 | 7 | 4 | 4 | 7 | 0 | 51 | 7 | 4 | 4 | 5 | 9 | 9 | 8 | 9 |
| fast | 22 | 22 | 22 | 23 | 24 | 22 | 23 | 24 | 23 | 24 | 23 | 22 | 23 | 21 | 23 | 22 | 23 | 23 | 23 | 23 | 23 | 22 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 4 | 0 | 3 | 0 | 4 | 0 | 5 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 5 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 480 | 944 | 187185 | 23314645 | 2637565 | 29.51 |
