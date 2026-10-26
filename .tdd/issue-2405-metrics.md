### 📊 Metrics — issue 2405

Wall time for the issue: 825 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 4 planned.
Outcome: the run bailed — killed-stuck, a system failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.18 over 81 turns, in 2 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87751 tokens, largest 131408 tokens
Conductor context: first turn 87962 tokens, largest 151058 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87751 |
| 2 | $0.05 | 90044 |
| 3 | $0.04 | 91946 |
| 4 | $0.04 | 92273 |
| 5 | $0.03 | 92682 |
| 6 | $0.03 | 93013 |
| 7 | $0.03 | 93338 |
| 8 | $0.04 | 93952 |
| 9 | $0.03 | 94311 |
| 10 | $0.06 | 97669 |
| 11 | $0.04 | 99296 |
| 12 | $0.04 | 99721 |
| 13 | $0.03 | 100526 |
| 14 | $0.04 | 100982 |
| 15 | $0.04 | 101564 |
| 16 | $0.03 | 102342 |
| 17 | $0.05 | 103815 |
| 18 | $0.04 | 104737 |
| 19 | $0.03 | 105456 |
| 20 | $0.05 | 106579 |
| 21 | $0.04 | 107903 |
| 22 | $0.04 | 108894 |
| 23 | $0.10 | 116933 |
| 24 | $0.04 | 117974 |
| 25 | $0.04 | 118949 |
| 26 | $0.04 | 119946 |
| 27 | $0.05 | 120856 |
| 28 | $0.04 | 121330 |
| 29 | $0.04 | 122228 |
| 30 | $0.04 | 123279 |
| 31 | $0.05 | 124116 |
| 32 | $0.04 | 125102 |
| 33 | $0.07 | 129678 |
| 34 | $0.05 | 130644 |
| 35 | $0.04 | 131408 |
| 36 | $0.56 | 87962 |
| 37 | $0.02 | 88544 |
| 38 | $0.03 | 90443 |
| 39 | $0.03 | 92547 |
| 40 | $0.06 | 97886 |
| 41 | $0.05 | 101620 |
| 42 | $0.04 | 103731 |
| 43 | $0.03 | 104330 |
| 44 | $0.03 | 104854 |
| 45 | $0.02 | 105227 |
| 46 | $0.02 | 105615 |
| 47 | $0.03 | 106501 |
| 48 | $0.04 | 108245 |
| 49 | $0.03 | 108931 |
| 50 | $0.03 | 109650 |
| 51 | $0.03 | 110363 |
| 52 | $0.04 | 112425 |
| 53 | $0.03 | 113544 |
| 54 | $0.04 | 115981 |
| 55 | $0.03 | 117082 |
| 56 | $0.05 | 119806 |
| 57 | $0.03 | 120755 |
| 58 | $0.03 | 121162 |
| 59 | $0.03 | 121888 |
| 60 | $0.03 | 122534 |
| 61 | $0.04 | 124120 |
| 62 | $0.03 | 124472 |
| 63 | $0.03 | 125209 |
| 64 | $0.03 | 126102 |
| 65 | $0.04 | 127626 |
| 66 | $0.03 | 128133 |
| 67 | $0.03 | 128876 |
| 68 | $0.03 | 129888 |
| 69 | $0.03 | 130935 |
| 70 | $0.03 | 131931 |
| 71 | $0.03 | 132812 |
| 72 | $0.03 | 133299 |
| 73 | $0.04 | 134929 |
| 74 | $0.03 | 135558 |
| 75 | $0.03 | 136284 |
| 76 | $0.04 | 137571 |
| 77 | $0.03 | 138031 |
| 78 | $0.06 | 141857 |
| 79 | $0.06 | 146183 |
| 80 | $0.04 | 147551 |
| 81 | $0.06 | 151058 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1108 | 0 | 33000 | 0.09 |
| red | 7 | 3 | 0 | 0 | 225 | 169 | 40 | 74 | 20415 | 1171488 | 183322 | 0.78 |
| green | 9 | 1 | 3 | 1 | 678 | 188 | 52 | 104 | 19410 | 1659400 | 141519 | 0.96 |
| exhausted | 1 | 0 | 0 | 0 | 20 | 18 | 4 | 8 | 1212 | 113724 | 16692 | 0.13 |
| pin | 1 | 1 | 0 | 0 | 17 | 12 | 3 | 6 | 1274 | 62664 | 32731 | 0.10 |
| refactor | 1 | 0 | 0 | 0 | 10 | 7 | 3 | 6 | 687 | 83599 | 17624 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 6 | 3 | 0 | 306 | 139 | 36 | 72 | 15054 | 1034226 | 163709 | 0.66 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 366 | 197 | 53 | 100 | 23653 | 1595238 | 222023 | 1.07 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 91 | 67 | 14 | 28 | 5399 | 461411 | 39156 | 0.40 |
| developer | not recorded | 1 | 0 | 0 | 1 | 198 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 70 | 0.19 |
| green | 1227 | 2.09 | 198 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| python3 run directly on veri/next_unchecked.py, with PYTHONPYCACHEPREFIX unset and a stale tunables .pyc planted in veri/__pycache__ (same mtime second and size as tunables.py), runs the current tunables source, not the planted bytecode; pinned by a new process case (a real python3 process, @pytest.mark.process) in skills/tdd/scripts/tests/py/test_stale_bytecode_process.py that plants tunables.pyc, not ledger.pyc, and restores whatever it planted over ⟦criterion 1⟧ | 14 | 3 | 3 | 0 | 0 | 0 | 286 | 78 | 152 | 29954 | 2352840 | 273771 | 1.53 | 294 | 2/2 | 0/5 | nothing-left |  |  | full |
| python3 run directly on veri/next_unchecked.py with VERI_PYCACHE set to a directory under tmp_path and PYTHONPYCACHEPREFIX unset writes its bytecode under that VERI_PYCACHE directory and none into veri/__pycache__; pinned by a process case in skills/tdd/scripts/tests/py/test_stale_bytecode_process.py, a pin of behaviour the current code already has, watched red by removing the VERI_PYCACHE read; it must land before step 1's green, which keeps that read ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 14 | 26 | 7687 | 407357 | 75730 | 0.31 | unknown | unknown | unknown | unknown |  |  | pin |
| every module under skills/tdd/scripts/veri/ that can be run directly (python3 <module>) gets the pycache prefix before its first veri import, from one shared place rather than a per-module guard after the first import; pinned by one check over the tree (not one case per module) in a test file under skills/tdd/scripts/tests/py/, marked as its size requires, that fails when any one runnable module is made to opt out ⟦criterion 2⟧ | 3 | 1 | 0 | 1 | 0 | 0 | 46 | 10 | 20 | 5357 | 330678 | 42387 | 0.19 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| python3 run directly on veri/next_unchecked.py, with PYTHONPYCACHEPREFIX unset and a stale tunables .pyc planted in veri/__pycache__ (same mtime second and size as tunables.py), runs the current tunables source, not the planted bytecode; pinned by a new process case (a real python3 process, @pytest.mark.process) in skills/tdd/scripts/tests/py/test_stale_bytecode_process.py that plants tunables.pyc, not ledger.pyc, and restores whatever it planted over ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.06 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 2 | 2 | 0 | 31 | 1 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 4 | 6 | 7 | 105 |
| fast | 16 | 17 | 27 | 18 | 17 | 17 | 16 | 16 | 16 | 23 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 1 | 1 | 2 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 103 | 200 | 44106 | 3090875 | 424888 | 2.13 |
