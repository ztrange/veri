### 📊 Metrics — issue 1183

Wall time for the issue: 3373 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1197.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 12 | 2 | 4 | 1399 | 55297 | 37908 | 0.18 |
| red | 11 | 5 | 0 | 0 | 302 | 258 | 64 | 124 | 26786 | 2867504 | 512993 | 4.35 |
| green | 10 | 5 | 0 | 0 | 962 | 192 | 65 | 126 | 20468 | 2753982 | 402726 | 3.29 |
| refactor | 9 | 4 | 0 | 0 | 460 | 135 | 46 | 92 | 13305 | 1928243 | 364264 | 2.89 |
| pin | 1 | 1 | 0 | 0 | 16 | 11 | 4 | 8 | 1518 | 152866 | 37945 | 0.20 |
| predicate | 3 | 0 | 0 | 0 | 53 | 42 | 11 | 22 | 3270 | 399686 | 107980 | 1.01 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 16 | 0 | 0 | 887 | 241 | 85 | 170 | 26900 | 3519796 | 623996 | 3.47 |
| developer | claude-opus-5-5 | 19 | 0 | 0 | 0 | 921 | 409 | 107 | 206 | 39846 | 4637782 | 839820 | 8.44 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When reading `~/.gitconfig` before the verifier leaf is launched fails — it is a directory, or reading it raises any other OSError — `verify.sh` exits 2 with a stderr message naming the global git config, launches no leaf and prints no traceback; the existing cases that pin exit 1 for this path now expect 2 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 109 | 34 | 66 | 11878 | 1456545 | 261839 | 2.10 | 411 | unknown | 0/5 | nothing-left |  |  | full |
| When the verifier leaf leaves `~/.gitconfig` a directory after it ran, `verify.sh` exits 2 with a message naming the global git config and prints no traceback, never exit 1 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 131 | 40 | 76 | 13596 | 1724533 | 253758 | 2.13 | 488 | unknown | 1/5 | nothing-left |  |  | full |
| When the verifier leaf leaves `~/.gitconfig` unreadable after it ran (reading it raises PermissionError or another OSError), `verify.sh` exits 2 with a message naming the global git config and prints no traceback ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 11 | 22 | 5567 | 501888 | 88370 | 0.75 | unknown | unknown | unknown | unknown |  |  | pin |
| When the verifier leaf moved HEAD and restoring it with `git update-ref HEAD <before>` exits non-zero, `verify.sh` exits 2, never the git status such as 128, with no traceback ⟦criterion 2⟧ | 11 | 5 | 0 | 0 | 0 | 0 | 199 | 60 | 118 | 20301 | 2541944 | 465773 | 3.77 | 748 | unknown | 0/5 | structural-owed |  |  | full |
| When the verifier leaf moved HEAD and git cannot be started to restore it, `verify.sh` exits 2 with no traceback ⟦criterion 2⟧ | 9 | 3 | 0 | 0 | 0 | 0 | 150 | 45 | 90 | 14005 | 1877371 | 356168 | 2.98 | 402 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When reading `~/.gitconfig` before the verifier leaf is launched fails — it is a directory, or reading it raises any other OSError — `verify.sh` exits 2 with a stderr message naming the global git config, launches no leaf and prints no traceback; the existing cases that pin exit 1 for this path now expect 2 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 95 | 0.60 |
| When the verifier leaf leaves `~/.gitconfig` a directory after it ran, `verify.sh` exits 2 with a message naming the global git config and prints no traceback, never exit 1 ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 147 | 0.71 |
| When the verifier leaf moved HEAD and restoring it with `git update-ref HEAD <before>` exits non-zero, `verify.sh` exits 2, never the git status such as 128, with no traceback ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 116 | 0.98 |
| When the verifier leaf moved HEAD and restoring it with `git update-ref HEAD <before>` exits non-zero, `verify.sh` exits 2, never the git status such as 128, with no traceback ⟦criterion 2⟧ | 2 | 0/5 | structural-owed |  | 0 | 0 | 0.00 |
| When the verifier leaf moved HEAD and git cannot be started to restore it, `verify.sh` exits 2 with no traceback ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 102 | 0.60 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 39 | 39 | 0 | 0 | 1 | 35 | 34 | 0 | 35 | 1 | 38 | 1 | 0 | 1 | 0 | 0 | 39 | 38 | 0 | 1 | 36 | 36 | 38 | 0 | 37 | 1 | 1 | 38 | 0 | 0 | 38 | 0 | 0 | 0 | 38 |
| fast | 23 | 27 | 25 | 24 | 27 | 25 | 24 | 27 | 24 | 26 | 27 | 25 | 27 | 28 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 192 | 376 | 66746 | 8157578 | 1463816 | 11.91 |
