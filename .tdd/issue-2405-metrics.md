### 📊 Metrics — issue 2405

Wall time for the issue: 612 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 3 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.58 over 33 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87751 tokens, largest 129678 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87751 |
| 2 | $0.04 | 90044 |
| 3 | $0.03 | 91946 |
| 4 | $0.02 | 92273 |
| 5 | $0.02 | 92682 |
| 6 | $0.02 | 93013 |
| 7 | $0.02 | 93338 |
| 8 | $0.02 | 93952 |
| 9 | $0.02 | 94311 |
| 10 | $0.05 | 97669 |
| 11 | $0.03 | 99296 |
| 12 | $0.02 | 99721 |
| 13 | $0.03 | 100526 |
| 14 | $0.02 | 100982 |
| 15 | $0.02 | 101564 |
| 16 | $0.03 | 102342 |
| 17 | $0.03 | 103815 |
| 18 | $0.03 | 104737 |
| 19 | $0.03 | 105456 |
| 20 | $0.03 | 106579 |
| 21 | $0.03 | 107903 |
| 22 | $0.03 | 108894 |
| 23 | $0.09 | 116933 |
| 24 | $0.03 | 117974 |
| 25 | $0.03 | 118949 |
| 26 | $0.03 | 119946 |
| 27 | $0.03 | 120856 |
| 28 | $0.03 | 121330 |
| 29 | $0.03 | 122228 |
| 30 | $0.03 | 123279 |
| 31 | $0.03 | 124116 |
| 32 | $0.03 | 125102 |
| 33 | $0.06 | 129678 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1108 | 0 | 33000 | 0.09 |
| red | 2 | 1 | 0 | 0 | 43 | 34 | 10 | 18 | 4180 | 256221 | 56602 | 0.21 |
| green | 6 | 0 | 3 | 0 | 355 | 145 | 39 | 78 | 14625 | 1245325 | 101896 | 0.78 |
| exhausted | 1 | 0 | 0 | 0 | 20 | 18 | 4 | 8 | 1212 | 113724 | 16692 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 2 | 3 | 0 | 194 | 77 | 21 | 42 | 8645 | 623385 | 76451 | 0.34 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 20 | 17 | 5 | 8 | 2260 | 104532 | 36963 | 0.13 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 215 | 112 | 28 | 56 | 10220 | 887353 | 94776 | 0.74 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 43 | 0.21 |
| green | 0 | 0.00 | 355 | 0.78 |
| exhausted | 0 | 0.00 | 20 | 0.13 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| python3 run directly on veri/next_unchecked.py, with PYTHONPYCACHEPREFIX unset and a stale tunables .pyc planted in veri/__pycache__ (same mtime second and size as tunables.py), runs the current tunables source, not the planted bytecode; pinned by a new process case (a real python3 process, @pytest.mark.process) in skills/tdd/scripts/tests/py/test_stale_bytecode_process.py that plants tunables.pyc, not ledger.pyc, and restores whatever it planted over ⟦criterion 1⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 197 | 53 | 104 | 20017 | 1615270 | 175190 | 1.11 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 2 | 2 | 0 | 31 | 1 | 1 |
| fast | 16 | 17 | 27 | 18 | 17 | 17 | 16 |  |  |
| target | 2 | 1 | 1 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 54 | 106 | 21125 | 1615270 | 208190 | 1.21 |
