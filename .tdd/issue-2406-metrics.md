### 📊 Metrics — issue 2406

Wall time for the issue: 1710 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2431.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.81 over 45 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87975 tokens, largest 123696 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87975 |
| 2 | $0.03 | 89940 |
| 3 | $0.03 | 91906 |
| 4 | $0.02 | 92189 |
| 5 | $0.02 | 92607 |
| 6 | $0.02 | 92907 |
| 7 | $0.02 | 93247 |
| 8 | $0.02 | 93899 |
| 9 | $0.02 | 94220 |
| 10 | $0.04 | 96465 |
| 11 | $0.04 | 98862 |
| 12 | $0.03 | 100172 |
| 13 | $0.03 | 100937 |
| 14 | $0.03 | 101639 |
| 15 | $0.02 | 101954 |
| 16 | $0.03 | 102710 |
| 17 | $0.03 | 103286 |
| 18 | $0.03 | 104274 |
| 19 | $0.02 | 104521 |
| 20 | $0.03 | 105890 |
| 21 | $0.03 | 106657 |
| 22 | $0.03 | 107549 |
| 23 | $0.02 | 107978 |
| 24 | $0.03 | 108543 |
| 25 | $0.03 | 110016 |
| 26 | $0.03 | 111085 |
| 27 | $0.03 | 112406 |
| 28 | $0.03 | 113254 |
| 29 | $0.03 | 113619 |
| 30 | $0.03 | 114395 |
| 31 | $0.03 | 115209 |
| 32 | $0.03 | 115766 |
| 33 | $0.03 | 116398 |
| 34 | $0.03 | 117255 |
| 35 | $0.03 | 118140 |
| 36 | $0.03 | 119474 |
| 37 | $0.03 | 120163 |
| 38 | $0.03 | 120956 |
| 39 | $0.03 | 121251 |
| 40 | $0.03 | 121584 |
| 41 | $0.03 | 122123 |
| 42 | $0.03 | 122378 |
| 43 | $0.03 | 122964 |
| 44 | $0.03 | 123349 |
| 45 | $0.03 | 123696 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 765 | 0 | 33081 | 0.09 |
| red | 2 | 1 | 0 | 0 | 44 | 35 | 10 | 20 | 4407 | 304372 | 60621 | 0.23 |
| green | 2 | 1 | 0 | 0 | 170 | 46 | 14 | 28 | 5446 | 482267 | 45062 | 0.22 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 2 | 4 | 428 | 50194 | 18439 | 0.06 |
| diff | 2 | 1 | 0 | 0 | 66 | 21 | 9 | 18 | 2206 | 260398 | 32707 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 99 | 39 | 13 | 26 | 4296 | 344405 | 84470 | 0.29 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 196 | 73 | 23 | 46 | 8956 | 752826 | 105440 | 0.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After a same-second, same-size mutation of a veri/ module's source, a veri shim run outside make (next-unchecked.sh, with PYTHONPYCACHEPREFIX and VERI_PYCACHE unset and VERI_PYCACHE's default prefix pointed at the case's tmp_path via TMPDIR) reads the current source rather than a .pyc an earlier shim run left in the shared prefix: pinned by a medium case (a real process) in skills/tdd/scripts/tests/py/test_stale_bytecode_process.py that runs the shim twice around such a mutation and fails on the current code by serving the stale bytecode; the mutation is made on a copy of the scripts tree under tmp_path, never on the repository's own sources ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 85 | 26 | 52 | 10281 | 836833 | 124122 | 0.50 | 329 | unknown | 0/5 | nothing-left |  |  | full |
| CLAUDE.md's Testing idiom paragraph on the bytecode cache says where the shim's shared prefix comes from and what keeps a non-pytest shim run from being served a stale .pyc from it, not only the pytest leg's manifest purge ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 21 | 9 | 18 | 2206 | 260398 | 32707 | 0.13 | 103 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| After a same-second, same-size mutation of a veri/ module's source, a veri shim run outside make (next-unchecked.sh, with PYTHONPYCACHEPREFIX and VERI_PYCACHE unset and VERI_PYCACHE's default prefix pointed at the case's tmp_path via TMPDIR) reads the current source rather than a .pyc an earlier shim run left in the shared prefix: pinned by a medium case (a real process) in skills/tdd/scripts/tests/py/test_stale_bytecode_process.py that runs the shim twice around such a mutation and fails on the current code by serving the stale bytecode; the mutation is made on a copy of the scripts tree under tmp_path, never on the repository's own sources ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.06 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 67 | 10 |
| fast | 18 | 19 | 19 |  |  |
| target | 1 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 36 | 72 | 13252 | 1097231 | 189910 | 0.72 |
