### 📊 Metrics — issue 2195

Wall time for the issue: 3877 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 11 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.46 over 91 turns, in 3 sessions.
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
| 64 | $0.56 | 87217 |
| 65 | $0.03 | 88809 |
| 66 | $0.04 | 91548 |
| 67 | $0.05 | 95390 |
| 68 | $0.02 | 96070 |
| 69 | $0.02 | 96518 |
| 70 | $0.02 | 96965 |
| 71 | $0.02 | 97429 |
| 72 | $0.02 | 97867 |
| 73 | $0.03 | 98729 |
| 74 | $0.04 | 101098 |
| 75 | $0.03 | 102280 |
| 76 | $0.08 | 109541 |
| 77 | $0.07 | 115462 |
| 78 | $0.03 | 115965 |
| 79 | $0.03 | 116846 |
| 80 | $0.03 | 117575 |
| 81 | $0.03 | 117824 |
| 82 | $0.08 | 125379 |
| 83 | $0.04 | 127821 |
| 84 | $0.03 | 128377 |
| 85 | $0.03 | 128643 |
| 86 | $0.03 | 128909 |
| 87 | $0.03 | 129175 |
| 88 | $0.03 | 129879 |
| 89 | $0.05 | 133013 |
| 90 | $0.06 | 137457 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1193 | 0 | 30926 | 0.09 |
| red | 5 | 1 | 0 | 0 | 1383 | 150 | 29 | 58 | 15681 | 857301 | 191170 | 0.72 |
| green | 2 | 1 | 0 | 0 | 302 | 46 | 12 | 24 | 5325 | 375670 | 37552 | 0.18 |
| refactor | 2 | 1 | 0 | 0 | 63 | 15 | 7 | 12 | 1313 | 152385 | 27615 | 0.10 |
| pin | 5 | 1 | 0 | 0 | 74 | 15 | 4 | 8 | 1365 | 106381 | 15265 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 322 | 66 | 19 | 36 | 6775 | 458955 | 93088 | 0.35 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 1512 | 169 | 34 | 68 | 18102 | 1032782 | 209440 | 0.81 |
| verifier | not recorded | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 1167 | 0.36 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Two concurrent full runs serialise: while one full `make test` run (the pytest leg launched as a full run) is running its suites, a second full run started from a different working tree waits for the first to finish before starting its own suites, writes once (not repeatedly) that it is waiting and on whom — the holder's pid and working tree — and then runs normally and exits as its suites decide; the lock lives under the user's machine-wide veri state (the user's home, like ~/.veri-pytest-legs), never under a clone or worktree. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 114 | 30 | 58 | 11515 | 852957 | 126076 | 0.52 | 562 | unknown | 0/5 | nothing-structural |  |  | full |
| A full run holds the lock for the whole run and releases it on every exit path: after the holder exits normally, exits red, or is ended by SIGTERM, SIGINT or SIGHUP, a waiting full run starts its suites. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 11 | 22 | 5842 | 349461 | 40373 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| A killed holder's lock is taken over: a lock whose recorded holder pid no longer answers `kill -0` (the holder was SIGKILLed and never released it) does not make a new full run wait; the new run takes the lock and runs its suites. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 6 | 0 | 0 | 0 | 0 | 0 | 57 | 11 | 22 | 6327 | 289319 | 105153 | 0.36 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Two concurrent full runs serialise: while one full `make test` run (the pytest leg launched as a full run) is running its suites, a second full run started from a different working tree waits for the first to finish before starting its own suites, writes once (not repeatedly) that it is waiting and on whom — the holder's pid and working tree — and then runs normally and exits as its suites decide; the lock lives under the user's machine-wide veri state (the user's home, like ~/.veri-pytest-legs), never under a clone or worktree. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 63 | 0.10 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 19 | 20 | 16 | 16 | 15 | 37 | 19 | 17 |
| fast | 17 | 17 | 19 |  |  |  |  |  |
| target | 13 | 13 | 28 | 12 | 12 | 6 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 53 | 104 | 24877 | 1491737 | 302528 | 1.15 |
