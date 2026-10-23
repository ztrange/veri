### 📊 Metrics — issue 2195

Wall time for the issue: 3995 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 12 planned.
Outcome: the run bailed — killed-stuck, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $8.35 over 153 turns, in 4 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87230 |
| 2 | $0.03 | 87886 |
| 3 | $0.03 | 88688 |
| 4 | $0.05 | 90645 |
| 5 | $0.03 | 90940 |
| 6 | $0.03 | 91337 |
| 7 | $0.03 | 91701 |
| 8 | $0.03 | 92028 |
| 9 | $0.03 | 92845 |
| 10 | $0.04 | 93903 |
| 11 | $0.04 | 95081 |
| 12 | $0.11 | 106179 |
| 13 | $0.06 | 109801 |
| 14 | $0.05 | 112055 |
| 15 | $0.06 | 114816 |
| 16 | $0.03 | 115107 |
| 17 | $0.04 | 115700 |
| 18 | $0.03 | 116264 |
| 19 | $0.04 | 116506 |
| 20 | $0.04 | 117596 |
| 21 | $0.15 | 132110 |
| 22 | $0.04 | 133075 |
| 23 | $0.04 | 133503 |
| 24 | $0.04 | 134270 |
| 25 | $0.05 | 135259 |
| 26 | $0.04 | 136233 |
| 27 | $0.04 | 136913 |
| 28 | $0.05 | 137590 |
| 29 | $0.04 | 137929 |
| 30 | $0.04 | 138847 |
| 31 | $0.05 | 140078 |
| 32 | $0.04 | 141310 |
| 33 | $0.06 | 143794 |
| 34 | $0.05 | 144440 |
| 35 | $0.04 | 144661 |
| 36 | $0.04 | 145151 |
| 37 | $0.04 | 145841 |
| 38 | $0.05 | 146562 |
| 39 | $0.04 | 147113 |
| 40 | $0.05 | 148222 |
| 41 | $0.04 | 148485 |
| 42 | $0.05 | 150566 |
| 43 | $0.05 | 151022 |
| 44 | $0.04 | 152106 |
| 45 | $0.05 | 152614 |
| 46 | $0.05 | 153693 |
| 47 | $0.07 | 157688 |
| 48 | $0.05 | 158655 |
| 49 | $0.04 | 159185 |
| 50 | $0.08 | 163569 |
| 51 | $0.57 | 87229 |
| 52 | $0.02 | 87667 |
| 53 | $0.04 | 88660 |
| 54 | $0.04 | 90618 |
| 55 | $0.03 | 91128 |
| 56 | $0.10 | 100627 |
| 57 | $0.03 | 101205 |
| 58 | $0.04 | 101606 |
| 59 | $0.03 | 101978 |
| 60 | $0.03 | 102304 |
| 61 | $0.03 | 102894 |
| 62 | $0.04 | 104260 |
| 63 | $0.03 | 104931 |
| 64 | $0.57 | 87217 |
| 65 | $0.04 | 88809 |
| 66 | $0.05 | 91548 |
| 67 | $0.06 | 95390 |
| 68 | $0.03 | 96070 |
| 69 | $0.04 | 96518 |
| 70 | $0.03 | 96965 |
| 71 | $0.03 | 97429 |
| 72 | $0.04 | 97867 |
| 73 | $0.03 | 98729 |
| 74 | $0.05 | 101098 |
| 75 | $0.04 | 102280 |
| 76 | $0.09 | 109541 |
| 77 | $0.08 | 115462 |
| 78 | $0.04 | 115965 |
| 79 | $0.04 | 116846 |
| 80 | $0.04 | 117575 |
| 81 | $0.04 | 117824 |
| 82 | $0.09 | 125379 |
| 83 | $0.06 | 127821 |
| 84 | $0.04 | 128377 |
| 85 | $0.04 | 128643 |
| 86 | $0.03 | 128909 |
| 87 | $0.04 | 129175 |
| 88 | $0.04 | 129879 |
| 89 | $0.07 | 133013 |
| 90 | $0.07 | 137457 |
| 91 | $0.04 | 138440 |
| 92 | $0.05 | 139410 |
| 93 | $0.57 | 88336 |
| 94 | $0.02 | 88844 |
| 95 | $0.03 | 90497 |
| 96 | $0.02 | 90944 |
| 97 | $0.03 | 92259 |
| 98 | $0.04 | 94395 |
| 99 | $0.05 | 98063 |
| 100 | $0.02 | 98503 |
| 101 | $0.02 | 98836 |
| 102 | $0.02 | 99210 |
| 103 | $0.03 | 100036 |
| 104 | $0.02 | 100655 |
| 105 | $0.03 | 101302 |
| 106 | $0.03 | 101974 |
| 107 | $0.02 | 102178 |
| 108 | $0.03 | 103571 |
| 109 | $0.03 | 104484 |
| 110 | $0.06 | 109531 |
| 111 | $0.03 | 110007 |
| 112 | $0.03 | 110554 |
| 113 | $0.03 | 111005 |
| 114 | $0.03 | 111542 |
| 115 | $0.03 | 112232 |
| 116 | $0.03 | 112898 |
| 117 | $0.03 | 114407 |
| 118 | $0.04 | 116732 |
| 119 | $0.03 | 117444 |
| 120 | $0.03 | 117899 |
| 121 | $0.08 | 125106 |
| 122 | $0.03 | 125835 |
| 123 | $0.03 | 126456 |
| 124 | $0.03 | 127573 |
| 125 | $0.03 | 128321 |
| 126 | $0.03 | 129196 |
| 127 | $0.03 | 129940 |
| 128 | $0.03 | 130293 |
| 129 | $0.03 | 130589 |
| 130 | $0.03 | 131257 |
| 131 | $0.03 | 131478 |
| 132 | $0.04 | 132838 |
| 133 | $0.03 | 133696 |
| 134 | $0.03 | 134506 |
| 135 | $0.03 | 135299 |
| 136 | $0.04 | 136342 |
| 137 | $0.04 | 137397 |
| 138 | $0.03 | 138188 |
| 139 | $0.04 | 139132 |
| 140 | $0.04 | 140079 |
| 141 | $0.03 | 140457 |
| 142 | $0.03 | 141141 |
| 143 | $0.04 | 142223 |
| 144 | $0.04 | 143188 |
| 145 | $0.03 | 143395 |
| 146 | $0.03 | 143664 |
| 147 | $0.04 | 145620 |
| 148 | $0.04 | 146991 |
| 149 | $0.03 | 147590 |
| 150 | $0.03 | 148014 |
| 151 | $0.03 | 148221 |
| 152 | $0.06 | 152502 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1193 | 0 | 30926 | 0.09 |
| red | 10 | 3 | 0 | 1 | 4295 | 253 | 52 | 104 | 23344 | 1628870 | 316450 | 1.19 |
| green | 8 | 3 | 1 | 0 | 891 | 176 | 49 | 94 | 14296 | 1402998 | 140045 | 0.77 |
| refactor | 6 | 3 | 0 | 0 | 221 | 69 | 18 | 34 | 3166 | 414516 | 100732 | 0.33 |
| pin | 5 | 1 | 0 | 0 | 74 | 15 | 4 | 8 | 1365 | 106381 | 15265 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 11 | 1 | 0 | 795 | 177 | 44 | 86 | 13405 | 1113181 | 199564 | 0.74 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 1 | 4479 | 302 | 64 | 126 | 26369 | 1987075 | 350236 | 1.34 |
| verifier | not recorded | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 219 | 43 | 16 | 30 | 3590 | 452509 | 53618 | 0.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 3884 | 0.36 |
| green | 409 | 0.45 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Two concurrent full runs serialise: while one full `make test` run (the pytest leg launched as a full run) is running its suites, a second full run started from a different working tree waits for the first to finish before starting its own suites, writes once (not repeatedly) that it is waiting and on whom — the holder's pid and working tree — and then runs normally and exits as its suites decide; the lock lives under the user's machine-wide veri state (the user's home, like ~/.veri-pytest-legs), never under a clone or worktree. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 114 | 30 | 58 | 11515 | 852957 | 126076 | 0.52 | 562 | unknown | 0/5 | nothing-structural |  |  | full |
| A full run holds the lock for the whole run and releases it on every exit path: after the holder exits normally, exits red, or is ended by SIGTERM, SIGINT or SIGHUP, a waiting full run starts its suites. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 11 | 22 | 5842 | 349461 | 40373 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| A killed holder's lock is taken over: a lock whose recorded holder pid no longer answers `kill -0` (the holder was SIGKILLed and never released it) does not make a new full run wait; the new run takes the lock and runs its suites. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 7 | 0 | 0 | 1 | 1 | 0 | 57 | 11 | 22 | 6327 | 289319 | 105153 | 0.36 | unknown | unknown | unknown | unknown |  |  | full |
| `VERI_TEST_LOCK=0` disables the lock: with the lock held by a live full run, a full run started with VERI_TEST_LOCK=0 starts its suites at once without waiting and writes no waiting message. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 166 | 38 | 74 | 10700 | 1015977 | 191965 | 0.83 | 764 | 1/2 | 0/5 | nothing-left |  |  | full |
| Every verifier leaf (`verify-*`) runs with `VERI_TEST_LOCK=0` in its environment, set where the leaf is launched, so a verifier's own suite never waits on a lock its mutation broke; a developer leaf does not get it. Pinned by a case that launches a verify leaf through the launcher with a stub and sees `VERI_TEST_LOCK=0` in its environment, and one showing a developer leaf (`develop-*`) does not get it ⟦added⟧ ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 121 | 33 | 64 | 7787 | 1045051 | 108925 | 0.45 | 480 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Two concurrent full runs serialise: while one full `make test` run (the pytest leg launched as a full run) is running its suites, a second full run started from a different working tree waits for the first to finish before starting its own suites, writes once (not repeatedly) that it is waiting and on whom — the holder's pid and working tree — and then runs normally and exits as its suites decide; the lock lives under the user's machine-wide veri state (the user's home, like ~/.veri-pytest-legs), never under a clone or worktree. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 63 | 0.10 |
| `VERI_TEST_LOCK=0` disables the lock: with the lock held by a live full run, a full run started with VERI_TEST_LOCK=0 starts its suites at once without waiting and writes no waiting message. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 76 | 0.14 |
| Every verifier leaf (`verify-*`) runs with `VERI_TEST_LOCK=0` in its environment, set where the leaf is launched, so a verifier's own suite never waits on a lock its mutation broke; a developer leaf does not get it. Pinned by a case that launches a verify leaf through the launcher with a stub and sees `VERI_TEST_LOCK=0` in its environment, and one showing a developer leaf (`develop-*`) does not get it ⟦added⟧ ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 82 | 0.09 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 19 | 20 | 16 | 16 | 15 | 37 | 19 | 17 | 19 | 18 | 17 | 19 | 52 | 21 | 17 | 17 | 17 | 25 | 13 | 16 | 24 | 18 |
| fast | 17 | 17 | 19 | 17 | 14 | 26 | 17 | 21 | 16 | 17 | 23 |  |  |  |  |  |  |  |  |  |  |  |
| target | 13 | 13 | 28 | 12 | 12 | 6 | 14 | 16 | 10 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 124 | 242 | 43364 | 3552765 | 603418 | 2.44 |
