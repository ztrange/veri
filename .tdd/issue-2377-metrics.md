### 📊 Metrics — issue 2377

Wall time for the issue: 3161 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2378.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.67 over 73 turns, in 2 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92618 tokens, largest 105451 tokens
Conductor context: first turn 92636 tokens, largest 159018 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.61 | 92618 |
| 2 | $0.03 | 93678 |
| 3 | $0.07 | 99515 |
| 4 | $0.04 | 100226 |
| 5 | $0.03 | 100644 |
| 6 | $0.03 | 101001 |
| 7 | $0.03 | 101387 |
| 8 | $0.02 | 101687 |
| 9 | $0.04 | 102158 |
| 10 | $0.04 | 104827 |
| 11 | $0.04 | 105451 |
| 12 | $0.60 | 92636 |
| 13 | $0.02 | 93070 |
| 14 | $0.02 | 93852 |
| 15 | $0.03 | 95876 |
| 16 | $0.03 | 96612 |
| 17 | $0.03 | 97599 |
| 18 | $0.03 | 98317 |
| 19 | $0.02 | 98666 |
| 20 | $0.02 | 98953 |
| 21 | $0.02 | 99307 |
| 22 | $0.03 | 100014 |
| 23 | $0.02 | 100413 |
| 24 | $0.03 | 101091 |
| 25 | $0.03 | 102422 |
| 26 | $0.04 | 105275 |
| 27 | $0.05 | 109406 |
| 28 | $0.05 | 112991 |
| 29 | $0.03 | 114054 |
| 30 | $0.03 | 115031 |
| 31 | $0.03 | 115562 |
| 32 | $0.03 | 116347 |
| 33 | $0.03 | 117537 |
| 34 | $0.03 | 118271 |
| 35 | $0.03 | 119545 |
| 36 | $0.03 | 120017 |
| 37 | $0.03 | 120682 |
| 38 | $0.03 | 121467 |
| 39 | $0.03 | 121811 |
| 40 | $0.03 | 122518 |
| 41 | $0.03 | 123187 |
| 42 | $0.03 | 124010 |
| 43 | $0.03 | 124825 |
| 44 | $0.03 | 125443 |
| 45 | $0.03 | 126602 |
| 46 | $0.03 | 127784 |
| 47 | $0.03 | 128614 |
| 48 | $0.04 | 130849 |
| 49 | $0.09 | 139260 |
| 50 | $0.04 | 140517 |
| 51 | $0.04 | 141687 |
| 52 | $0.04 | 142657 |
| 53 | $0.04 | 143624 |
| 54 | $0.04 | 144475 |
| 55 | $0.03 | 145199 |
| 56 | $0.03 | 145899 |
| 57 | $0.04 | 146916 |
| 58 | $0.03 | 147568 |
| 59 | $0.04 | 148301 |
| 60 | $0.04 | 149342 |
| 61 | $0.05 | 151835 |
| 62 | $0.04 | 152576 |
| 63 | $0.03 | 152875 |
| 64 | $0.04 | 153766 |
| 65 | $0.04 | 154605 |
| 66 | $0.04 | 155595 |
| 67 | $0.04 | 156242 |
| 68 | $0.04 | 157037 |
| 69 | $0.03 | 157330 |
| 70 | $0.03 | 157670 |
| 71 | $0.04 | 158188 |
| 72 | $0.03 | 158532 |
| 73 | $0.04 | 159018 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 8 | 1 | 2 | 1095 | 0 | 30930 | 0.09 |
| red | 4 | 2 | 0 | 0 | 210 | 142 | 25 | 50 | 11845 | 883223 | 113711 | 0.49 |
| green | 3 | 1 | 0 | 0 | 183 | 46 | 15 | 28 | 3559 | 398803 | 45593 | 0.19 |
| red-contradicted | 1 | 0 | 0 | 0 | 36 | 24 | 6 | 12 | 2649 | 188353 | 20434 | 0.10 |
| refactor | 1 | 0 | 0 | 0 | 13 | 10 | 4 | 8 | 767 | 112307 | 15765 | 0.06 |
| pin | 1 | 1 | 0 | 0 | 60 | 18 | 5 | 10 | 1667 | 137230 | 15395 | 0.07 |
| diff | 2 | 1 | 0 | 0 | 112 | 27 | 8 | 16 | 1707 | 206260 | 23527 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 241 | 102 | 18 | 36 | 6245 | 442251 | 103295 | 0.36 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 386 | 173 | 46 | 90 | 17044 | 1483925 | 162060 | 0.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A `verify-*` leaf's full `make test` waits on a full-suite lock another live run holds and starts its suites only once that lock is released, as any other full run does (#2195's lock, no longer switched off for verifiers by the launcher). Pinned by a medium case with real processes (`@pytest.mark.process`) that launches a verify leaf through the launcher (`supervise`) while another process holds the full-suite lock, and sees the leaf's full run wait and then start once the lock is released. The existing case `test_main_hands_a_verify_leaf_veri_test_lock_0_and_a_develop_leaf_no_such_variable_2195` in `skills/tdd/scripts/tests/py/test_supervise.py` asserts the behaviour this step reverses ⟦criterion 1⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 170 | 39 | 76 | 13335 | 1144341 | 164219 | 0.66 | 592 | unknown | 0/5 | nothing-left |  |  | full |
| #2195's guarantee still holds: a verify leaf whose mutation breaks the full-suite lock code under it (its release or its wait) fails within its bound instead of hanging. Pinned by a medium case with real processes (`@pytest.mark.process`) that breaks the lock code under a verify leaf launched through the launcher and sees the leaf finish inside its bound ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 70 | 16 | 32 | 7152 | 575575 | 46679 | 0.25 | unknown | unknown | unknown | unknown |  |  | pin |
| CLAUDE.md's Testing idiom no longer says the launcher sets `VERI_TEST_LOCK=0` in a verifier's environment, and says instead that a verifier's full run takes the full-suite lock like any other while a verifier that breaks the lock code still cannot hang on it ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 8 | 16 | 1707 | 206260 | 23527 | 0.10 | 197 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A `verify-*` leaf's full `make test` waits on a full-suite lock another live run holds and starts its suites only once that lock is released, as any other full run does (#2195's lock, no longer switched off for verifiers by the launcher). Pinned by a medium case with real processes (`@pytest.mark.process`) that launches a verify leaf through the launcher (`supervise`) while another process holds the full-suite lock, and sees the leaf's full run wait and then start once the lock is released. The existing case `test_main_hands_a_verify_leaf_veri_test_lock_0_and_a_develop_leaf_no_such_variable_2195` in `skills/tdd/scripts/tests/py/test_supervise.py` asserts the behaviour this step reverses ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 13 | 0.06 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 20 | 19 | 9 | 8 | 4 | 9 | 9 | 4 |
| fast | 24 | 26 | 23 | 54 | 24 |  |  |  |
| target | 1 | 5 | 33 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 64 | 126 | 23289 | 1926176 | 265355 | 1.09 |
