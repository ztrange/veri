### 📊 Metrics — issue 2784

Wall time for the issue: 3850 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2785.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.81 over 30 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87088 tokens, largest 152302 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 87088 |
| 2 | $0.08 | 94835 |
| 3 | $0.04 | 97206 |
| 4 | $0.02 | 97712 |
| 5 | $0.02 | 98065 |
| 6 | $0.02 | 98395 |
| 7 | $0.02 | 98670 |
| 8 | $0.03 | 100112 |
| 9 | $0.11 | 111173 |
| 10 | $0.04 | 113133 |
| 11 | $0.04 | 115174 |
| 12 | $0.04 | 117278 |
| 13 | $0.03 | 118211 |
| 14 | $0.04 | 120182 |
| 15 | $0.03 | 121066 |
| 16 | $0.06 | 125282 |
| 17 | $0.10 | 134322 |
| 18 | $0.05 | 136934 |
| 19 | $0.04 | 138168 |
| 20 | $0.04 | 139294 |
| 21 | $0.04 | 140782 |
| 22 | $0.06 | 144474 |
| 23 | $0.06 | 148406 |
| 24 | $0.04 | 149586 |
| 25 | $0.03 | 150211 |
| 26 | $0.03 | 150681 |
| 27 | $0.03 | 151206 |
| 28 | $0.03 | 151424 |
| 29 | $0.03 | 151639 |
| 30 | $0.04 | 152302 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 727 | 0 | 31614 | 0.09 |
| red | 3 | 1 | 0 | 0 | 234 | 49 | 14 | 28 | 5751 | 435696 | 82148 | 0.31 |
| green | 4 | 1 | 1 | 0 | 554 | 68 | 20 | 40 | 7717 | 600025 | 76775 | 0.46 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 2 | 4 | 313 | 30907 | 31859 | 0.09 |
| pin | 1 | 1 | 0 | 0 | 28 | 11 | 4 | 8 | 1376 | 109862 | 16289 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 4 | 1 | 0 | 454 | 52 | 16 | 32 | 5968 | 422294 | 82107 | 0.31 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 139 | 44 | 13 | 26 | 5279 | 388646 | 98745 | 0.34 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 239 | 42 | 12 | 24 | 4637 | 365550 | 57833 | 0.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 554 | 0.46 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After a refusal for an unreadable file left by a verifier leaf, a new file the leaf added no longer exists in the worktree and the exit is still 2: a process case in `skills/tdd/scripts/tests/py/test_verify.py` with a stub `CLAUDE_BIN` in a real git scratch repository, failing on the current code ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 97 | 29 | 58 | 10763 | 815610 | 165422 | 0.73 | 918 | 1/2 | 0/5 | nothing-left |  |  | full |
| After the same refusal, an untracked file that existed before the leaf launched is still there with its contents unchanged: a process case in `skills/tdd/scripts/tests/py/test_verify.py` with a stub `CLAUDE_BIN` in a real git scratch repository ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 11 | 22 | 4394 | 360880 | 41649 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| After a refusal for an unreadable file left by a verifier leaf, a new file the leaf added no longer exists in the worktree and the exit is still 2: a process case in `skills/tdd/scripts/tests/py/test_verify.py` with a stub `CLAUDE_BIN` in a real git scratch repository, failing on the current code ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 46 | 49 | 26 | 35 | 42 | 29 | 30 |
| fast | 27 | 32 | 33 | 33 |  |  |  |
| target | 7 | 7 | 6 | 6 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 41 | 82 | 15884 | 1176490 | 238685 | 2.81 (estimate) |
