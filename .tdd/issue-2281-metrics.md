### 📊 Metrics — issue 2281

Wall time for the issue: 914 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2289.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.49 over 124 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 89770 |
| 2 | $0.04 | 90876 |
| 3 | $0.04 | 92755 |
| 4 | $0.03 | 92941 |
| 5 | $0.03 | 93311 |
| 6 | $0.03 | 93591 |
| 7 | $0.03 | 93830 |
| 8 | $0.03 | 94335 |
| 9 | $0.04 | 95248 |
| 10 | $0.03 | 95814 |
| 11 | $0.08 | 102351 |
| 12 | $0.03 | 102980 |
| 13 | $0.09 | 109703 |
| 14 | $0.03 | 110041 |
| 15 | $0.04 | 110678 |
| 16 | $0.03 | 111178 |
| 17 | $0.04 | 111999 |
| 18 | $0.04 | 113316 |
| 19 | $0.04 | 114157 |
| 20 | $0.03 | 114602 |
| 21 | $0.04 | 115290 |
| 22 | $0.04 | 116227 |
| 23 | $0.04 | 117597 |
| 24 | $0.04 | 118426 |
| 25 | $0.04 | 119243 |
| 26 | $0.04 | 119891 |
| 27 | $0.03 | 120450 |
| 28 | $0.04 | 121123 |
| 29 | $0.04 | 121368 |
| 30 | $0.04 | 122392 |
| 31 | $0.04 | 122798 |
| 32 | $0.04 | 123941 |
| 33 | $0.04 | 124818 |
| 34 | $0.04 | 126385 |
| 35 | $0.04 | 127073 |
| 36 | $0.05 | 128518 |
| 37 | $0.04 | 129208 |
| 38 | $0.05 | 130959 |
| 39 | $0.03 | 131168 |
| 40 | $0.04 | 131573 |
| 41 | $0.04 | 131998 |
| 42 | $0.04 | 132456 |
| 43 | $0.04 | 133125 |
| 44 | $0.04 | 133336 |
| 45 | $0.03 | 133543 |
| 46 | $0.04 | 133715 |
| 47 | $0.05 | 134915 |
| 48 | $0.04 | 135976 |
| 49 | $0.04 | 136650 |
| 50 | $0.04 | 137337 |
| 51 | $0.04 | 137921 |
| 52 | $0.04 | 138325 |
| 53 | $0.05 | 139241 |
| 54 | $0.04 | 139880 |
| 55 | $0.04 | 140513 |
| 56 | $0.04 | 140804 |
| 57 | $0.04 | 141231 |
| 58 | $0.04 | 142110 |
| 59 | $0.05 | 142702 |
| 60 | $0.04 | 143087 |
| 61 | $0.04 | 143490 |
| 62 | $0.04 | 143773 |
| 63 | $0.04 | 144209 |
| 64 | $0.04 | 144508 |
| 65 | $0.04 | 145620 |
| 66 | $0.05 | 146484 |
| 67 | $0.04 | 146707 |
| 68 | $0.58 | 89803 |
| 69 | $0.02 | 90296 |
| 70 | $0.03 | 91235 |
| 71 | $0.02 | 91722 |
| 72 | $0.04 | 94563 |
| 73 | $0.02 | 95192 |
| 74 | $0.02 | 95680 |
| 75 | $0.02 | 95869 |
| 76 | $0.02 | 96192 |
| 77 | $0.02 | 96487 |
| 78 | $0.02 | 96776 |
| 79 | $0.02 | 97388 |
| 80 | $0.05 | 100648 |
| 81 | $0.03 | 102424 |
| 82 | $0.02 | 102891 |
| 83 | $0.03 | 103594 |
| 84 | $0.03 | 104199 |
| 85 | $0.02 | 104434 |
| 86 | $0.03 | 105821 |
| 87 | $0.03 | 106636 |
| 88 | $0.02 | 107017 |
| 89 | $0.03 | 107552 |
| 90 | $0.03 | 109069 |
| 91 | $0.03 | 109722 |
| 92 | $0.02 | 110002 |
| 93 | $0.03 | 110709 |
| 94 | $0.03 | 111317 |
| 95 | $0.03 | 112342 |
| 96 | $0.03 | 112988 |
| 97 | $0.08 | 120587 |
| 98 | $0.03 | 121730 |
| 99 | $0.04 | 123072 |
| 100 | $0.03 | 123503 |
| 101 | $0.03 | 124476 |
| 102 | $0.04 | 126508 |
| 103 | $0.03 | 127188 |
| 104 | $0.03 | 128362 |
| 105 | $0.03 | 129084 |
| 106 | $0.03 | 129798 |
| 107 | $0.03 | 130586 |
| 108 | $0.03 | 131032 |
| 109 | $0.03 | 131493 |
| 110 | $0.03 | 132097 |
| 111 | $0.03 | 132664 |
| 112 | $0.03 | 133347 |
| 113 | $0.03 | 133883 |
| 114 | $0.03 | 134177 |
| 115 | $0.03 | 134548 |
| 116 | $0.03 | 134736 |
| 117 | $0.03 | 135206 |
| 118 | $0.03 | 135863 |
| 119 | $0.03 | 136405 |
| 120 | $0.03 | 136700 |
| 121 | $0.03 | 137224 |
| 122 | $0.03 | 137512 |
| 123 | $0.03 | 137986 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 791 | 0 | 31006 | 0.09 |
| red | 6 | 3 | 0 | 0 | 122 | 97 | 23 | 46 | 9919 | 636133 | 176884 | 0.61 |
| green | 9 | 3 | 1 | 0 | 294 | 114 | 43 | 78 | 12182 | 1109637 | 150309 | 0.71 |
| refactor | 6 | 3 | 0 | 0 | 111 | 46 | 18 | 36 | 4407 | 480157 | 91216 | 0.32 |
| cover | 3 | 0 | 0 | 0 | 86 | 34 | 16 | 32 | 3939 | 428286 | 59342 | 0.23 |
| predicate | 3 | 0 | 0 | 0 | 27 | 20 | 11 | 22 | 1553 | 285230 | 35663 | 0.13 |
| structural | 2 | 0 | 0 | 0 | 21 | 15 | 8 | 16 | 1343 | 213289 | 25596 | 0.10 |
| transform | 1 | 1 | 0 | 0 | 13 | 9 | 4 | 8 | 809 | 86563 | 30085 | 0.09 |
| red-missing | 1 | 0 | 0 | 0 | 23 | 19 | 5 | 10 | 2738 | 163865 | 22541 | 0.10 |
| pin | 1 | 1 | 0 | 0 | 16 | 11 | 3 | 6 | 1344 | 77448 | 14685 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 12 | 1 | 0 | 299 | 120 | 43 | 84 | 13193 | 1059899 | 227802 | 0.81 |
| developer | claude-sonnet-5-5 | 20 | 0 | 0 | 0 | 422 | 251 | 89 | 172 | 25832 | 2420709 | 409525 | 1.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 146 | 0.44 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After a pin-guard refusal, skill-edit-step.sh restores every path the guard named to its content before the attempt (removing one the attempt created), so the next author attempt starts from the same tree as the first: a unit case (in-process, author and guard faked, no git) where attempt 1 edits an unnamed test file and is refused and attempt 2 edits only the unit and is accepted, exiting 0 with the unnamed file back to its original bytes ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 70 | 25 | 44 | 7915 | 618489 | 123082 | 0.45 | 246 | unknown | 0/5 | structural-owed |  |  | full |
| When skill-edit-step.sh's author attempts are exhausted (exit 1), the tree is as it was before it ran: the unit, the pin files, every path a guard refusal named, and the unit's REQUIREMENTS.md list (with the rows apply wrote removed) restored byte-for-byte, a list it created removed: a unit case (in-process, author and grader faked) ⟦criterion 2⟧ | 15 | 4 | 0 | 0 | 0 | 0 | 157 | 62 | 124 | 14180 | 1662989 | 252722 | 0.94 | 224 | unknown | 0/5 | structural-owed |  |  | full |
| _restore after a guard refusal never deletes a path it holds no snapshot for (a .tdd/ file, or anything _tree skipped); it unlinks only a path proven absent before the attempt: pinned by a case where an untracked .tdd/issue-<n>-added.md and a dirty .tdd/issue-<n>.md named by the guard both survive the refusal byte-identical ⟦added⟧ ⟦criterion 1⟧ | 11 | 4 | 1 | 0 | 0 | 0 | 138 | 44 | 86 | 16139 | 1199130 | 230517 | 0.96 | 458 | 1/2 | 1/5 | nothing-structural |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| After a pin-guard refusal, skill-edit-step.sh restores every path the guard named to its content before the attempt (removing one the attempt created), so the next author attempt starts from the same tree as the first: a unit case (in-process, author and guard faked, no git) where attempt 1 edits an unnamed test file and is refused and attempt 2 edits only the unit and is accepted, exiting 0 with the unnamed file back to its original bytes ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 36 | 0.10 |
| When skill-edit-step.sh's author attempts are exhausted (exit 1), the tree is as it was before it ran: the unit, the pin files, every path a guard refusal named, and the unit's REQUIREMENTS.md list (with the rows apply wrote removed) restored byte-for-byte, a list it created removed: a unit case (in-process, author and grader faked) ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 33 | 0.10 |
| _restore after a guard refusal never deletes a path it holds no snapshot for (a .tdd/ file, or anything _tree skipped); it unlinks only a path proven absent before the attempt: pinned by a case where an untracked .tdd/issue-<n>-added.md and a dirty .tdd/issue-<n>.md named by the guard both survive the refusal byte-identical ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 42 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 13 | 1 | 1 | 1 | 1 | 1 | 1 | 15 | 2 | 1 | 0 | 14 | 14 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 |
| fast | 15 | 15 | 15 | 16 | 15 | 16 | 15 | 16 | 16 | 16 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 132 | 256 | 39025 | 3480608 | 637327 | 2.44 |
