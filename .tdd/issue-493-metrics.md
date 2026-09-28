### 📊 Metrics — issue 493

Wall time for the issue: 15482 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 18 of 19 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/534.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 32 | 27 | 3 | 6 | 2823 | 104976 | 36890 | 0.37 |
| red | 38 | 19 | 0 | 0 | 1425 | 1152 | 280 | 550 | 108560 | 13210427 | 1666342 | 18.15 |
| green | 46 | 19 | 4 | 0 | 8775 | 2163 | 492 | 976 | 208979 | 26052154 | 2115302 | 26.32 |
| refactor | 38 | 19 | 0 | 0 | 2051 | 848 | 221 | 438 | 82343 | 9357766 | 1542831 | 15.86 |
| pin | 1 | 1 | 0 | 0 | 43 | 27 | 8 | 16 | 2668 | 355709 | 41510 | 0.46 |
| structural | 11 | 0 | 0 | 0 | 308 | 121 | 35 | 68 | 10686 | 1266803 | 367669 | 3.41 |
| transform | 1 | 1 | 0 | 0 | 151 | 19 | 6 | 12 | 1922 | 240560 | 36348 | 0.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 3920 | 7.79 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A committed script under `skills/tdd/scripts/`, given shell files, prints every `#` line with its file, line number and class, and reports a comment in code outside any heredoc as class 1 ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 363 | 74 | 148 | 31118 | 3530192 | 349668 | 4.13 | 2085 | 1/2 | 0/5 | nothing-left |  |  | full |
| On a file containing both a comment and a heredoc carrying `#` lines, the classifier counts the heredoc's `#` lines separately from the comment, never as class 1 ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 247 | 52 | 102 | 23960 | 2225787 | 282637 | 3.19 | 945 | 1/2 | 2/5 | nothing-structural |  |  | full |
| A `#` line inside a heredoc opened with a quoted delimiter (`<<'EOF'`, `<<"EOF"`) or with `<<-` is never class 1, and a here-string `<<<` opens no heredoc ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 169 | 39 | 78 | 16586 | 1685438 | 239535 | 2.59 | 289 | unknown | 1/5 | structural-owed |  |  | full |
| A `#` line inside a heredoc whose output is redirected to a file is class 2, and a `#` line inside any other heredoc — one sent to a model, a variable or stdout — is class 3 ⟦criterion 1⟧ | 14 | 6 | 1 | 0 | 0 | 0 | 407 | 89 | 172 | 36940 | 3748967 | 528803 | 5.72 | 1173 | 1/2 | 0/5 | structural-owed |  |  | full |
| A `#` line inside a heredoc piped to a file writer (`cat <<EOF | tee "$f"`) is class 2 ⟦added⟧ ⟦criterion 1⟧ | 12 | 6 | 0 | 0 | 0 | 0 | 251 | 70 | 138 | 23685 | 2859462 | 464273 | 4.76 | 452 | unknown | 0/5 | nothing-left |  |  | full |
| The classifier's sweepable report lists class 1 and class 2 lines only, and never a class 3 line ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 146 | 40 | 80 | 12949 | 1786504 | 241549 | 2.55 | 266 | unknown | 0/5 | nothing-left |  |  | full |
| The sweepable report omits a file's leading contract header and any comment marked as a shell-hazard warning, so a file whose comments are only those reports nothing sweepable ⟦criterion 4⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 223 | 54 | 106 | 22140 | 2354995 | 287568 | 3.21 | 873 | 1/2 | 1/5 | nothing-left |  |  | full |
| Every script's usage output on a missing argument, and each prompt builder's output for fixed inputs, is pinned byte-identical to what it prints before the sweep ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 164 | 27 | 54 | 16867 | 1778717 | 128169 | 1.72 | 234 | unknown | unknown | unknown |  |  | pin |
| The sweepable report is empty for metrics.sh, event.sh and harvest-usage.sh ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 208 | 53 | 106 | 20340 | 2761397 | 280856 | 3.21 | 365 | unknown | 1/5 | nothing-left |  |  | full |
| The sweepable report is empty for supervise.sh, run-leaf.sh, detach-leaf.sh, wait-leaf.sh and run-verdict.sh ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 223 | 54 | 106 | 21491 | 2676520 | 281700 | 3.22 | 468 | unknown | 1/5 | nothing-left |  |  | full |
| The sweepable report is empty for issue-worktree.sh, verify.sh, parse-verdict.sh and extract-result.sh ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 208 | 52 | 104 | 20235 | 2785185 | 293070 | 3.31 | 734 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for detect-test-command.sh, solvable-issues.sh and session-cost.sh ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 201 | 54 | 106 | 19974 | 2708367 | 273614 | 3.13 | 358 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for build-develop-prompt.sh, build-verify-prompt.sh, run-conductor.sh, stop-run.sh and preserve-attempt.sh ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 233 | 60 | 120 | 23486 | 3149022 | 298447 | 3.49 | 515 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for leaf-timeout.sh, ensure-run-state-ignored.sh, orchestrate.sh, parallel-conductors.sh, workqueue.sh, push-branch.sh, refactor-triage.sh, invisible-work.sh, over-budget.sh, run-suite.sh, leaf-model.sh and leaf-launchable.sh ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 260 | 64 | 126 | 26366 | 3725040 | 322830 | 3.86 | 946 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for every remaining `skills/tdd/scripts/*.sh`, the classifier itself included ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 232 | 58 | 114 | 22754 | 2897053 | 295028 | 3.40 | 466 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for every shell file under `skills/tdd/scripts/lib/` ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 262 | 65 | 128 | 26304 | 3465094 | 299719 | 3.62 | 960 | unknown | 0/5 | nothing-left |  |  | full |
| No comment line in `skills/tdd/scripts/*.sh` or `skills/tdd/scripts/lib/*.sh`, the leading contract header included, cites an issue number (`#<digits>`), so the headers keep the contract and drop the rationale ⟦added⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 276 | 65 | 130 | 26252 | 3516707 | 294684 | 3.59 | 1529 | unknown | 1/5 | nothing-left |  |  | full |
| `make test` is green on the swept tree: CLAUDE.md's unit-tier suite count matches the unit suites on disk, now that `emitted-text.test.sh` exists ⟦criterion 5⟧ | 5 | 3 | 0 | 0 | 0 | 0 | 117 | 31 | 62 | 11103 | 1321609 | 203835 | 2.12 | 665 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A committed script under `skills/tdd/scripts/`, given shell files, prints every `#` line with its file, line number and class, and reports a comment in code outside any heredoc as class 1 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 199 | 0.81 |
| On a file containing both a comment and a heredoc carrying `#` lines, the classifier counts the heredoc's `#` lines separately from the comment, never as class 1 ⟦criterion 2⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 84 | 0.93 |
| A `#` line inside a heredoc opened with a quoted delimiter (`<<'EOF'`, `<<"EOF"`) or with `<<-` is never class 1, and a here-string `<<<` opens no heredoc ⟦added⟧ ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 74 | 0.87 |
| A `#` line inside a heredoc whose output is redirected to a file is class 2, and a `#` line inside any other heredoc — one sent to a model, a variable or stdout — is class 3 ⟦criterion 1⟧ | 2 | 0/5 | structural-owed | PASS | 0 | 107 | 1.51 |
| A `#` line inside a heredoc piped to a file writer (`cat <<EOF | tee "$f"`) is class 2 ⟦added⟧ ⟦criterion 1⟧ | 2 | 0/5 | nothing-left | PASS | 0 | 112 | 1.52 |
| The classifier's sweepable report lists class 1 and class 2 lines only, and never a class 3 line ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 46 | 0.73 |
| The sweepable report omits a file's leading contract header and any comment marked as a shell-hazard warning, so a file whose comments are only those reports nothing sweepable ⟦criterion 4⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 56 | 0.77 |
| The sweepable report is empty for metrics.sh, event.sh and harvest-usage.sh ⟦criterion 4⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 54 | 0.79 |
| The sweepable report is empty for supervise.sh, run-leaf.sh, detach-leaf.sh, wait-leaf.sh and run-verdict.sh ⟦criterion 4⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 110 | 0.85 |
| The sweepable report is empty for issue-worktree.sh, verify.sh, parse-verdict.sh and extract-result.sh ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 148 | 0.84 |
| The sweepable report is empty for detect-test-command.sh, solvable-issues.sh and session-cost.sh ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 75 | 0.88 |
| The sweepable report is empty for build-develop-prompt.sh, build-verify-prompt.sh, run-conductor.sh, stop-run.sh and preserve-attempt.sh ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 139 | 0.96 |
| The sweepable report is empty for leaf-timeout.sh, ensure-run-state-ignored.sh, orchestrate.sh, parallel-conductors.sh, workqueue.sh, push-branch.sh, refactor-triage.sh, invisible-work.sh, over-budget.sh, run-suite.sh, leaf-model.sh and leaf-launchable.sh ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 230 | 1.09 |
| The sweepable report is empty for every remaining `skills/tdd/scripts/*.sh`, the classifier itself included ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 113 | 0.93 |
| The sweepable report is empty for every shell file under `skills/tdd/scripts/lib/` ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 259 | 0.83 |
| No comment line in `skills/tdd/scripts/*.sh` or `skills/tdd/scripts/lib/*.sh`, the leading contract header included, cites an issue number (`#<digits>`), so the headers keep the contract and drop the rationale ⟦added⟧ ⟦criterion 4⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 62 | 0.81 |
| `make test` is green on the swept tree: CLAUDE.md's unit-tier suite count matches the unit suites on disk, now that `emitted-text.test.sh` exists ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 183 | 0.75 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s | run 146 s | run 147 s | run 148 s | run 149 s | run 150 s | run 151 s | run 152 s | run 153 s | run 154 s | run 155 s | run 156 s | run 157 s | run 158 s | run 159 s | run 160 s | run 161 s | run 162 s | run 163 s | run 164 s | run 165 s | run 166 s | run 167 s | run 168 s | run 169 s | run 170 s | run 171 s | run 172 s | run 173 s | run 174 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 114 | 0 | 0 | 110 | 0 | 136 | 0 | 140 | 0 | 0 | 0 | 1 | 45 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 2 | 1 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 11 | 12 | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 42 | 45 | 42 | 0 | 0 | 0 | 0 | 78 | 82 | 90 | 89 | 1 | 0 | 0 | 0 | 14 | 9 | 8 | 0 | 1 | 57 | 0 | 60 | 56 | 0 | 1 | 77 | 87 | 1 | 170 | 0 | 2 | 19 | 1 | 1 | 1 | 7 | 1 | 42 | 1 | 7 | 9 | 7 | 1 | 0 | 0 | 1 | 83 | 61 | 0 | 1 | 0 | 42 | 1 | 42 | 0 | 42 | 0 | 0 | 0 | 206 | 0 | 179 | 0 | 180 | 1 | 1 | 230 | 251 | 0 | 274 | 336 | 1 | 1 | 0 | 1 | 1 | 208 | 0 | 119 | 0 | 133 | 0 | 0 | 1 | 61 | 0 | 0 | 1 | 0 | 1 | 60 | 62 | 63 |
| fast | 5 | 5 | 5 | 6 | 4 | 5 | 4 | 5 | 4 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 4 | 5 | 5 | 4 | 5 | 5 | 5 | 4 | 5 | 5 | 6 | 5 | 5 | 4 | 5 | 6 | 7 | 6 | 7 | 7 | 7 | 7 | 7 | 8 | 8 | 7 | 8 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 8 | 7 | 6 | 7 | 6 | 7 | 7 | 7 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 2 | 2 | 2 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 511 | 536 | 501 | 523 | 504 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 1045 | 2066 | 417981 | 50588395 | 5806892 | 64.94 |
