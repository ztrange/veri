### 📊 Metrics — issue 2829

Wall time for the issue: 1101 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2842.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.64 over 27 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87727 tokens, largest 143571 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87727 |
| 2 | $0.07 | 94730 |
| 3 | $0.03 | 95704 |
| 4 | $0.04 | 97857 |
| 5 | $0.05 | 101237 |
| 6 | $0.03 | 102576 |
| 7 | $0.03 | 103578 |
| 8 | $0.03 | 105088 |
| 9 | $0.03 | 106182 |
| 10 | $0.04 | 108039 |
| 11 | $0.04 | 109996 |
| 12 | $0.03 | 110871 |
| 13 | $0.04 | 112491 |
| 14 | $0.03 | 113422 |
| 15 | $0.04 | 115317 |
| 16 | $0.09 | 124092 |
| 17 | $0.06 | 128722 |
| 18 | $0.03 | 129578 |
| 19 | $0.04 | 131916 |
| 20 | $0.07 | 137047 |
| 21 | $0.03 | 137430 |
| 22 | $0.03 | 138005 |
| 23 | $0.03 | 138902 |
| 24 | $0.04 | 140644 |
| 25 | $0.04 | 141654 |
| 26 | $0.04 | 142571 |
| 27 | $0.04 | 143571 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 6 | 1 | 2 | 721 | 0 | 31194 | 0.09 |
| red | 4 | 1 | 0 | 0 | 160 | 51 | 16 | 28 | 6188 | 401299 | 107015 | 0.37 |
| green | 2 | 1 | 0 | 0 | 154 | 22 | 11 | 18 | 2040 | 253356 | 29776 | 0.12 |
| refactor | 1 | 0 | 0 | 0 | 8 | 5 | 3 | 4 | 520 | 48153 | 23390 | 0.07 |
| pin | 2 | 2 | 0 | 0 | 63 | 22 | 6 | 12 | 2470 | 154792 | 30126 | 0.12 |
| cover | 1 | 0 | 0 | 0 | 18 | 8 | 3 | 6 | 926 | 75996 | 12290 | 0.05 |
| predicate | 1 | 0 | 0 | 0 | 6 | 4 | 3 | 6 | 442 | 74888 | 11597 | 0.04 |
| structural | 1 | 0 | 0 | 0 | 20 | 12 | 8 | 12 | 1380 | 166523 | 14298 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 224 | 44 | 15 | 30 | 4882 | 370680 | 90284 | 0.31 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 215 | 86 | 36 | 58 | 9805 | 804327 | 169402 | 0.60 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Running `install-links.sh` on a repo with none of the eight links prints exactly eight lines on stdout, one per skill name, and exits 0; a process case in skills/tdd/scripts/tests/py/test_install_links_process.py, driving the real script ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 48 | 21 | 36 | 4771 | 480176 | 109235 | 0.37 | 423 | unknown | 0/5 | nothing-left |  |  | full |
| Running `install-links.sh` a second time on a repo already holding all eight links prints nothing on stdout; a process case in skills/tdd/scripts/tests/py/test_install_links_process.py, driving the real script ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 8 | 14 | 2928 | 210423 | 40800 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| After one veri link is left dangling and recreated by `install-links.sh`, stdout holds exactly one line, for that skill only; a process case in skills/tdd/scripts/tests/py/test_install_links_process.py, driving the real script ⟦criterion 2⟧ | 5 | 1 | 0 | 0 | 0 | 0 | 50 | 21 | 36 | 6267 | 484408 | 78457 | 0.31 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Running `install-links.sh` on a repo with none of the eight links prints exactly eight lines on stdout, one per skill name, and exits 0; a process case in skills/tdd/scripts/tests/py/test_install_links_process.py, driving the real script ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.07 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 10 | 8 | 8 | 10 | 7 | 10 | 7 | 6 |  |  |  |  |  |  |  |  |
| fast | 39 | 49 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 4 | 6 | 6 | 6 | 7 | 7 | 6 | 7 | 6 | 6 | 4 | 6 | 6 | 6 | 6 | 7 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 51 | 88 | 14687 | 1175007 | 259686 | 2.55 (estimate) |
