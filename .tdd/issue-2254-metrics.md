### 📊 Metrics — issue 2254

Wall time for the issue: 3566 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2371.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.39 over 99 turns, in 2 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92504 tokens, largest 180068 tokens
Conductor context: first turn 92456 tokens, largest 134928 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.61 | 92504 |
| 2 | $0.05 | 94259 |
| 3 | $0.04 | 96185 |
| 4 | $0.04 | 96548 |
| 5 | $0.03 | 96928 |
| 6 | $0.04 | 97489 |
| 7 | $0.03 | 98066 |
| 8 | $0.04 | 98366 |
| 9 | $0.04 | 99123 |
| 10 | $0.03 | 99553 |
| 11 | $0.05 | 101880 |
| 12 | $0.06 | 105664 |
| 13 | $0.06 | 108828 |
| 14 | $0.05 | 110223 |
| 15 | $0.04 | 110822 |
| 16 | $0.04 | 112413 |
| 17 | $0.05 | 113591 |
| 18 | $0.04 | 114379 |
| 19 | $0.10 | 122805 |
| 20 | $0.04 | 123560 |
| 21 | $0.04 | 123856 |
| 22 | $0.05 | 124598 |
| 23 | $0.05 | 127269 |
| 24 | $0.05 | 128442 |
| 25 | $0.04 | 128965 |
| 26 | $0.05 | 129723 |
| 27 | $0.04 | 130323 |
| 28 | $0.06 | 132521 |
| 29 | $0.04 | 133272 |
| 30 | $0.05 | 134207 |
| 31 | $0.11 | 143028 |
| 32 | $0.04 | 144005 |
| 33 | $0.05 | 144606 |
| 34 | $0.04 | 144917 |
| 35 | $0.05 | 145563 |
| 36 | $0.11 | 154399 |
| 37 | $0.05 | 155381 |
| 38 | $0.05 | 156109 |
| 39 | $0.05 | 156814 |
| 40 | $0.05 | 157676 |
| 41 | $0.05 | 158243 |
| 42 | $0.05 | 158917 |
| 43 | $0.05 | 159907 |
| 44 | $0.05 | 161123 |
| 45 | $0.06 | 162458 |
| 46 | $0.05 | 163802 |
| 47 | $0.06 | 164670 |
| 48 | $0.05 | 165858 |
| 49 | $0.05 | 166980 |
| 50 | $0.07 | 169036 |
| 51 | $0.05 | 169773 |
| 52 | $0.05 | 170613 |
| 53 | $0.05 | 171327 |
| 54 | $0.06 | 172599 |
| 55 | $0.05 | 173192 |
| 56 | $0.05 | 173779 |
| 57 | $0.09 | 178402 |
| 58 | $0.05 | 179280 |
| 59 | $0.05 | 180068 |
| 60 | $0.60 | 92456 |
| 61 | $0.03 | 94171 |
| 62 | $0.04 | 96684 |
| 63 | $0.03 | 97445 |
| 64 | $0.02 | 97887 |
| 65 | $0.02 | 98244 |
| 66 | $0.02 | 98595 |
| 67 | $0.03 | 99291 |
| 68 | $0.05 | 103000 |
| 69 | $0.05 | 107288 |
| 70 | $0.04 | 109257 |
| 71 | $0.03 | 109877 |
| 72 | $0.03 | 110991 |
| 73 | $0.03 | 111527 |
| 74 | $0.03 | 112057 |
| 75 | $0.04 | 114645 |
| 76 | $0.03 | 115696 |
| 77 | $0.03 | 116093 |
| 78 | $0.03 | 116738 |
| 79 | $0.07 | 123010 |
| 80 | $0.04 | 125481 |
| 81 | $0.03 | 126241 |
| 82 | $0.03 | 126577 |
| 83 | $0.03 | 127263 |
| 84 | $0.03 | 127771 |
| 85 | $0.03 | 128755 |
| 86 | $0.03 | 129208 |
| 87 | $0.03 | 129943 |
| 88 | $0.03 | 130157 |
| 89 | $0.03 | 131241 |
| 90 | $0.03 | 131865 |
| 91 | $0.03 | 132736 |
| 92 | $0.03 | 133330 |
| 93 | $0.03 | 133763 |
| 94 | $0.03 | 133973 |
| 95 | $0.03 | 134568 |
| 96 | $0.03 | 134928 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 29 | 25 | 2 | 4 | 3343 | 17160 | 46792 | 0.15 |
| red | 5 | 2 | 0 | 0 | 166 | 104 | 24 | 48 | 9493 | 754134 | 117738 | 0.46 |
| green | 4 | 2 | 0 | 0 | 274 | 57 | 21 | 40 | 5091 | 587636 | 64575 | 0.27 |
| refactor | 3 | 1 | 0 | 0 | 130 | 21 | 10 | 20 | 1578 | 271952 | 46191 | 0.16 |
| diff | 2 | 1 | 0 | 0 | 282 | 33 | 12 | 24 | 3193 | 330858 | 48629 | 0.19 |
| prose | 6 | 0 | 0 | 0 | 410 | 389 | 6 | 12 | 59435 | 82645 | 521690 | 1.91 |
| skill-edit | 1 | 0 | 0 | 0 | 13 | 11 | 3 | 6 | 576 | 260166 | 130502 | 0.36 |
| pin | 1 | 1 | 0 | 0 | 17 | 11 | 3 | 6 | 1152 | 60354 | 31830 | 0.10 |
| rebase | 2 | 1 | 0 | 0 | 1058 | 41 | 12 | 24 | 2900 | 280360 | 104319 | 0.32 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 1 | 0 | 656 | 114 | 29 | 58 | 10336 | 674823 | 218323 | 0.72 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 1300 | 178 | 55 | 108 | 16414 | 1627631 | 241751 | 0.93 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| wrong-test-route.sh, given a develop-green report whose only case line is one `SUPERSEDED:` line naming an earlier step's frozen pytest case by its bare name cut short with a trailing `…` (no `WRONG_TEST:` line; #2173's form, which today answers `revise`), prints `red <the full case name>` and exits 0; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 73 | 26 | 52 | 6888 | 746198 | 118227 | 0.44 | 428 | unknown | 1/5 | nothing-left |  |  | full |
| wrong-test-route.sh, given a revise-green report whose only case line is one `SUPERSEDED:` line naming an older pytest case by its node id `<file>.py::<case>` followed by prose (no `WRONG_TEST:` line; #2249's form, which today answers `revise`), prints `red <case>` and exits 0; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 69 | 20 | 38 | 4784 | 538673 | 84394 | 0.31 | 299 | unknown | 0/5 | nothing-left |  |  | full |
| REVISE.md states that a revise-green report carrying a `SUPERSEDED:` line, with or without `WRONG_TEST:`, is routed through `$S/wrong-test-route.sh .tdd/revise-green-<k>.out '<target-test-id>'` before the attempt is counted, exactly as a `WRONG_TEST:` report is (exit 0: no `revise` mark, no `REVISE_BUDGET` attempt, the red-contradicted red), and the verbatim WRONG_TEST_SENTENCE pin in skills/tdd/scripts/tests/py/unit/test_skill_tests_frozen.py moves with it in the same commit ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 12 | 24 | 3193 | 330858 | 48629 | 0.19 | 344 | n/a | n/a | n/a |  |  | full |
| skills/tdd/SKILL.md: add the pre-approved row (next free CY ID) to skills/tdd/REQUIREMENTS.md under `## skills/tdd/SKILL.md` — a green report carrying a `SUPERSEDED:` line, with or without `WRONG_TEST:`, goes through `wrong-test-route.sh` before any revise and shares the step's one free reroute — state it in SKILL.md's Green step, grade skills/tdd/SKILL.md PASS against its whole list and sign it ⟦skill-edit⟧ ⟦criterion 2⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 204 | 7 | 14 | 29209 | 340594 | 427836 | 1.40 | 1013 | unknown | unknown | unknown |  |  | full |
| conductor-level case: SKILL.md's Green step sends a develop-green report naming one older frozen case on a `SUPERSEDED:` line and none on `WRONG_TEST:` through `wrong-test-route.sh` before any revise, and on its `red <case>` answer launches the `red-contradicted` red, writes no `revise` mark and spends no `REVISE_BUDGET` attempt, then retries green; a small case in a new skills/tdd/scripts/tests/py/unit/test_skill_green_superseded.py, allow-listed in skills/tdd/scripts/tests/py/unit/test_skill_green_readers.py's ALLOWED (it reads the Green subsection); a pin step, since the skill-edit step above lands the text ⟦criterion 1⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 92 | 24 | 48 | 8542 | 669565 | 162032 | 0.56 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| wrong-test-route.sh, given a develop-green report whose only case line is one `SUPERSEDED:` line naming an earlier step's frozen pytest case by its bare name cut short with a trailing `…` (no `WRONG_TEST:` line; #2173's form, which today answers `revise`), prints `red <the full case name>` and exits 0; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 121 | 0.11 |
| wrong-test-route.sh, given a revise-green report whose only case line is one `SUPERSEDED:` line naming an older pytest case by its node id `<file>.py::<case>` followed by prose (no `WRONG_TEST:` line; #2249's form, which today answers `revise`), prints `red <case>` and exits 0; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 11 | 3 | 3 | 3 | 20 | 4 | 3 | 3 | 9 | 135 | 5 | 10 | 6 |
| fast | 32 | 25 | 76 | 26 | 72 | 24 | 24 | 28 | 24 |  |  |  |  |  |
| target | 1 | 4 | 2 | 1 |  |  |  |  |  |  |  |  |  |  |
| all | 287 | 473 | 244 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 93 | 184 | 86761 | 2645265 | 1112266 | 3.91 |
