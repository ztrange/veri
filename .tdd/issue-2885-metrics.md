### 📊 Metrics — issue 2885

Wall time for the issue: 4644 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 10 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.74 over 73 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89307 tokens, largest 187964 tokens
Conductor context: first turn 89304 tokens, largest 109672 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 89307 |
| 2 | $0.08 | 96278 |
| 3 | $0.04 | 97746 |
| 4 | $0.05 | 99303 |
| 5 | $0.03 | 99608 |
| 6 | $0.04 | 100261 |
| 7 | $0.03 | 100479 |
| 8 | $0.03 | 100767 |
| 9 | $0.04 | 101009 |
| 10 | $0.03 | 101297 |
| 11 | $0.04 | 101620 |
| 12 | $0.03 | 102041 |
| 13 | $0.04 | 102899 |
| 14 | $0.04 | 103372 |
| 15 | $0.03 | 104053 |
| 16 | $0.04 | 104402 |
| 17 | $0.06 | 108282 |
| 18 | $0.07 | 113022 |
| 19 | $0.07 | 117646 |
| 20 | $0.07 | 121129 |
| 21 | $0.06 | 124467 |
| 22 | $0.04 | 124958 |
| 23 | $0.04 | 125541 |
| 24 | $0.04 | 125948 |
| 25 | $0.04 | 126300 |
| 26 | $0.04 | 126516 |
| 27 | $0.04 | 127340 |
| 28 | $0.16 | 142881 |
| 29 | $0.06 | 145622 |
| 30 | $0.05 | 146295 |
| 31 | $0.04 | 146598 |
| 32 | $0.05 | 147165 |
| 33 | $0.04 | 147713 |
| 34 | $0.05 | 148957 |
| 35 | $0.06 | 150152 |
| 36 | $0.04 | 150903 |
| 37 | $0.05 | 151550 |
| 38 | $0.04 | 151799 |
| 39 | $0.05 | 152507 |
| 40 | $0.05 | 153357 |
| 41 | $0.05 | 154487 |
| 42 | $0.05 | 155387 |
| 43 | $0.11 | 163467 |
| 44 | $0.06 | 165781 |
| 45 | $0.05 | 166729 |
| 46 | $0.05 | 167474 |
| 47 | $0.05 | 168272 |
| 48 | $0.06 | 169206 |
| 49 | $0.06 | 170981 |
| 50 | $0.05 | 171855 |
| 51 | $0.06 | 173553 |
| 52 | $0.05 | 174398 |
| 53 | $0.05 | 175217 |
| 54 | $0.06 | 176730 |
| 55 | $0.06 | 177574 |
| 56 | $0.05 | 178482 |
| 57 | $0.05 | 178984 |
| 58 | $0.06 | 180092 |
| 59 | $0.05 | 180909 |
| 60 | $0.06 | 181788 |
| 61 | $0.08 | 186362 |
| 62 | $0.06 | 187245 |
| 63 | $0.05 | 187964 |
| 64 | $0.57 | 89304 |
| 65 | $0.07 | 96285 |
| 66 | $0.03 | 97743 |
| 67 | $0.03 | 99658 |
| 68 | $0.03 | 101535 |
| 69 | $0.03 | 102127 |
| 70 | $0.02 | 102678 |
| 71 | $0.03 | 103387 |
| 72 | $0.03 | 104868 |
| 73 | $0.06 | 109672 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 1 | 2 | 1376 | 0 | 31990 | 0.09 |
| red | 5 | 2 | 0 | 0 | 294 | 82 | 25 | 48 | 9730 | 720650 | 116685 | 0.46 |
| pin | 1 | 1 | 0 | 0 | 38 | 16 | 5 | 10 | 1859 | 139786 | 15645 | 0.07 |
| green | 10 | 1 | 4 | 0 | 1531 | 185 | 61 | 120 | 19712 | 1822664 | 182804 | 1.14 |
| refactor | 1 | 0 | 0 | 0 | 11 | 7 | 2 | 4 | 755 | 30302 | 32526 | 0.09 |
| exhausted | 1 | 0 | 0 | 0 | 69 | 10 | 3 | 6 | 977 | 76303 | 12958 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 5 | 4 | 0 | 960 | 132 | 40 | 78 | 14849 | 1083880 | 138033 | 0.60 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 127 | 64 | 17 | 34 | 7847 | 499974 | 116389 | 0.42 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 871 | 115 | 40 | 78 | 11713 | 1205851 | 138186 | 0.94 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 243 | 0.31 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 1531 | 1.14 |
| refactor | 0 | 0.00 | 11 | 0.09 |
| exhausted | 0 | 0.00 | 69 | 0.10 |
| preflight | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With `VERI_CI_ON_PR` unset, a mergeable PR with no checks yet whose head tree holds a workflow under `.github/workflows/` with `on: pull_request` keeps today's wait: `wait-ci.sh` exits 3 when the slice runs out (unit case in test_wait_ci.py, gh faked in-process) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 11 | 22 | 5061 | 324611 | 56469 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| With `VERI_CI_ON_PR` unset, a mergeable PR with no checks whose head tree (read at the PR head sha, the tree `pull_request` reads workflows from) holds under `.github/workflows/` only a workflow triggering `on: push` makes `wait-ci.sh` exit 0 and warn on stderr that no check will come (unit case in test_wait_ci.py, gh faked in-process) ⟦criterion 1⟧ | 16 | 3 | 4 | 0 | 0 | 0 | 260 | 85 | 166 | 27972 | 2465094 | 304149 | 1.64 | unknown | 3/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 11 | 7 | 7 | 11 | 10 | 7 | 22 | 9 | 8 | 8 | 7 | 7 | 8 | 7 | 5 | 7 |
| target | 8 | 8 | 9 | 8 | 8 | 7 | 5 |  |  |  |  |  |  |  |  |  |  |
| fast | 74 | 59 | 74 | 82 | 68 | 79 | 56 | 59 | 56 | 63 | 61 | 54 | 50 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 190 | 34409 | 2789705 | 392608 | 6.70 (estimate) |
