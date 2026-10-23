### 📊 Metrics — issue 2195

Wall time for the issue: 3638 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 7 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.28 over 47 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87230 |
| 2 | $0.02 | 87886 |
| 3 | $0.02 | 88688 |
| 4 | $0.03 | 90645 |
| 5 | $0.02 | 90940 |
| 6 | $0.02 | 91337 |
| 7 | $0.02 | 91701 |
| 8 | $0.02 | 92028 |
| 9 | $0.02 | 92845 |
| 10 | $0.03 | 93903 |
| 11 | $0.03 | 95081 |
| 12 | $0.11 | 106179 |
| 13 | $0.05 | 109801 |
| 14 | $0.04 | 112055 |
| 15 | $0.04 | 114816 |
| 16 | $0.03 | 115107 |
| 17 | $0.03 | 115700 |
| 18 | $0.03 | 116264 |
| 19 | $0.03 | 116506 |
| 20 | $0.03 | 117596 |
| 21 | $0.14 | 132110 |
| 22 | $0.03 | 133075 |
| 23 | $0.03 | 133503 |
| 24 | $0.03 | 134270 |
| 25 | $0.03 | 135259 |
| 26 | $0.03 | 136233 |
| 27 | $0.03 | 136913 |
| 28 | $0.03 | 137590 |
| 29 | $0.03 | 137929 |
| 30 | $0.03 | 138847 |
| 31 | $0.04 | 140078 |
| 32 | $0.04 | 141310 |
| 33 | $0.05 | 143794 |
| 34 | $0.03 | 144440 |
| 35 | $0.03 | 144661 |
| 36 | $0.03 | 145151 |
| 37 | $0.03 | 145841 |
| 38 | $0.03 | 146562 |
| 39 | $0.03 | 147113 |
| 40 | $0.04 | 148222 |
| 41 | $0.03 | 148485 |
| 42 | $0.05 | 150566 |
| 43 | $0.03 | 151022 |
| 44 | $0.04 | 152106 |
| 45 | $0.03 | 152614 |
| 46 | $0.04 | 153693 |
| 47 | $0.06 | 157688 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1193 | 0 | 30926 | 0.09 |
| red | 4 | 1 | 0 | 0 | 290 | 117 | 23 | 46 | 12432 | 724805 | 108761 | 0.47 |
| green | 2 | 1 | 0 | 0 | 302 | 46 | 12 | 24 | 5325 | 375670 | 37552 | 0.18 |
| refactor | 2 | 1 | 0 | 0 | 63 | 15 | 7 | 12 | 1313 | 152385 | 27615 | 0.10 |
| pin | 3 | 1 | 0 | 0 | 74 | 15 | 4 | 8 | 1365 | 106381 | 15265 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 322 | 66 | 19 | 36 | 6775 | 458955 | 93088 | 0.35 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 419 | 136 | 28 | 56 | 14853 | 900286 | 127031 | 0.56 |
| verifier | not recorded | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 74 | 0.10 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Two concurrent full runs serialise: while one full `make test` run (the pytest leg launched as a full run) is running its suites, a second full run started from a different working tree waits for the first to finish before starting its own suites, writes once (not repeatedly) that it is waiting and on whom — the holder's pid and working tree — and then runs normally and exits as its suites decide; the lock lives under the user's machine-wide veri state (the user's home, like ~/.veri-pytest-legs), never under a clone or worktree. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 114 | 30 | 58 | 11515 | 852957 | 126076 | 0.52 | 562 | unknown | 0/5 | nothing-structural |  |  | full |
| A full run holds the lock for the whole run and releases it on every exit path: after the holder exits normally, exits red, or is ended by SIGTERM, SIGINT or SIGHUP, a waiting full run starts its suites. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 11 | 22 | 5842 | 349461 | 40373 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| A killed holder's lock is taken over: a lock whose recorded holder pid no longer answers `kill -0` (the holder was SIGKILLed and never released it) does not make a new full run wait; the new run takes the lock and runs its suites. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 24 | 5 | 10 | 3078 | 156823 | 22744 | 0.10 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Two concurrent full runs serialise: while one full `make test` run (the pytest leg launched as a full run) is running its suites, a second full run started from a different working tree waits for the first to finish before starting its own suites, writes once (not repeatedly) that it is waiting and on whom — the holder's pid and working tree — and then runs normally and exits as its suites decide; the lock lives under the user's machine-wide veri state (the user's home, like ~/.veri-pytest-legs), never under a clone or worktree. Pinned by a medium case with real processes, @pytest.mark.process ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 63 | 0.10 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 19 | 20 | 16 | 16 | 15 | 37 | 19 |
| fast | 17 | 17 | 19 |  |  |  |  |
| target | 13 | 13 | 28 | 12 | 12 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 47 | 92 | 21628 | 1359241 | 220119 | 0.90 |
