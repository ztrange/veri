### 📊 Metrics — issue 866

Wall time for the issue: 19946 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 10 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/885.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 74 | 64 | 8 | 16 | 5597 | 366020 | 97754 | 0.97 |
| red | 12 | 3 | 0 | 0 | 2856 | 493 | 119 | 228 | 49342 | 6679243 | 667437 | 7.66 |
| pin | 6 | 6 | 0 | 0 | 1580 | 117 | 29 | 56 | 11492 | 1256704 | 271205 | 2.65 |
| green | 10 | 3 | 2 | 0 | 4885 | 374 | 90 | 176 | 36049 | 4706681 | 412318 | 4.96 |
| refactor | 6 | 3 | 0 | 0 | 1031 | 135 | 30 | 58 | 10901 | 1350829 | 287932 | 2.79 |
| diff | 2 | 1 | 0 | 0 | 340 | 20 | 6 | 12 | 2103 | 237133 | 88076 | 0.79 |
| rebase | 4 | 2 | 0 | 0 | 6109 | 298 | 67 | 134 | 27536 | 4159205 | 240683 | 3.31 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 22 | 19 | 3 | 0 | 8126 | 622 | 141 | 278 | 58328 | 6876478 | 962705 | 10.24 |
| developer | claude-opus-5-5 | 20 | 0 | 0 | 0 | 8749 | 879 | 208 | 402 | 84692 | 11879337 | 1102700 | 12.89 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 4740 | 4.54 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 2485 | 1.48 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a launch whose conductor exits with `.tdd/wt/<n>` registered as a git worktree keeps `.tdd/issue-<n>-skill-commit`, and the next launch runs the recorded commit ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 76 | 17 | 32 | 7591 | 982896 | 117281 | 1.29 | unknown | unknown | unknown | unknown |  |  | pin |
| a launch whose conductor exits with a local `tdd/<n>-*` branch and no worktree keeps `.tdd/issue-<n>-skill-commit`, and the next launch runs the recorded commit ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 13 | 26 | 6593 | 666229 | 96439 | 1.04 | unknown | unknown | unknown | unknown |  |  | pin |
| a launch whose conductor exits with no registered `.tdd/wt/<n>` worktree and no local `tdd/<n>-*` branch leaves no `.tdd/issue-<n>-skill-commit`, whether the conductor exits 0 or non-zero; the existing `run-conductor.test.sh` cases whose later launch relies on the record surviving a stub conductor (the resume-snapshot, keeps-its-pin and unresolvable-commit cases) model a run past preflight by giving their caller repo a local `tdd/<n>-*` branch in fixture setup, with their assertions unchanged ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 365 | 78 | 154 | 32451 | 4279405 | 434402 | 4.98 | 3406 | 2/2 | 0/5 | nothing-left |  |  | full |
| a local branch for a different issue whose number merely starts with `<n>` (e.g. `tdd/<n>6-x`) does not count as a run past preflight: the record is removed ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 16 | 32 | 5961 | 826349 | 93692 | 1.03 | unknown | unknown | unknown | unknown |  |  | pin |
| after a launch that left no worktree and no branch, the next launch of the same issue, with VERI_NEW_SKILL unset, pins the default branch's tip at that moment rather than the earlier launch's commit ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 14 | 26 | 5770 | 711752 | 103094 | 1.08 | unknown | unknown | unknown | unknown |  |  | pin |
| an unregistered `.tdd/wt/<n>` directory holding only `.tdd/events.jsonl`, as `VERI_NEW_SKILL=1` leaves it, does not count as a run past preflight: with no registered worktree and no branch the record is removed when the conductor exits ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 185 | 47 | 90 | 16954 | 2294043 | 287189 | 3.10 | 2224 | unknown | 1/5 | nothing-structural |  |  | full |
| a recorded commit the clone cannot resolve still exits 2 before launching any conductor ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 71 | 17 | 32 | 7149 | 869447 | 101818 | 1.13 | unknown | unknown | unknown | unknown |  |  | pin |
| `VERI_NEW_SKILL=1` still re-pins the record to the fresh tip and writes its `skill-repin` event ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 70 | 17 | 30 | 7561 | 837074 | 104349 | 1.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `SKILL.md`'s *The skill snapshot* says the record survives only a run that got past preflight, and that this is decided after the conductor exits by a registered `.tdd/wt/<n>` worktree or a local `tdd/<n>-*` branch, not by the conductor's exit code ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 177 | 49 | 96 | 17754 | 2526262 | 300628 | 3.27 | 1252 | unknown | 0/5 | nothing-left |  |  | full |
| every case `run-conductor.test.sh` and `issue-worktree.test.sh` already held on the default branch is still present with its assertions unchanged by this branch's diff (fixture setup may change) ⟦diff-checked⟧ ⟦criterion 7⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 197 | 47 | 94 | 18287 | 2821597 | 211088 | 2.62 | 356 | unknown | unknown | unknown |  |  | full |
| the repository's full test command passes ⟦full-suite⟧ ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 121 | 26 | 52 | 11352 | 1574741 | 117671 | 1.48 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| a launch whose conductor exits with no registered `.tdd/wt/<n>` worktree and no local `tdd/<n>-*` branch leaves no `.tdd/issue-<n>-skill-commit`, whether the conductor exits 0 or non-zero; the existing `run-conductor.test.sh` cases whose later launch relies on the record surviving a stub conductor (the resume-snapshot, keeps-its-pin and unresolvable-commit cases) model a run past preflight by giving their caller repo a local `tdd/<n>-*` branch in fixture setup, with their assertions unchanged ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 250 | 0.93 |
| an unregistered `.tdd/wt/<n>` directory holding only `.tdd/events.jsonl`, as `VERI_NEW_SKILL=1` leaves it, does not count as a run past preflight: with no registered worktree and no branch the record is removed when the conductor exits ⟦criterion 4⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 372 | 0.93 |
| `SKILL.md`'s *The skill snapshot* says the record survives only a run that got past preflight, and that this is decided after the conductor exits by a registered `.tdd/wt/<n>` worktree or a local `tdd/<n>-*` branch, not by the conductor's exit code ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 409 | 0.93 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 94 | 95 | 99 | 105 | 108 | 113 | 114 | 103 | 115 | 117 | 113 | 0 | 119 | 3 | 0 | 13 | 116 | 120 | 125 | 133 | 0 | 128 | 127 | 314 | 131 | 130 | 148 | 138 | 0 | 0 | 0 | 247 | 244 | 306 | 157 |
| target | 92 | 94 | 100 | 103 | 115 | 114 | 122 | 117 | 120 | 127 | 126 | 128 | 130 | 129 | 140 | 145 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 59 | 58 | 57 | 58 | 58 | 58 | 63 | 58 | 57 | 58 | 59 | 59 | 57 | 57 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 1140 | 1155 | 1144 | 1166 | 1174 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 349 | 680 | 143020 | 18755815 | 2065405 | 23.14 |
