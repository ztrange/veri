### 📊 Metrics — issue 2254

Wall time for the issue: 1209 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.81 over 57 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92504 tokens, largest 178402 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.60 | 92504 |
| 2 | $0.03 | 94259 |
| 3 | $0.03 | 96185 |
| 4 | $0.02 | 96548 |
| 5 | $0.02 | 96928 |
| 6 | $0.02 | 97489 |
| 7 | $0.02 | 98066 |
| 8 | $0.02 | 98366 |
| 9 | $0.03 | 99123 |
| 10 | $0.02 | 99553 |
| 11 | $0.04 | 101880 |
| 12 | $0.05 | 105664 |
| 13 | $0.05 | 108828 |
| 14 | $0.03 | 110223 |
| 15 | $0.03 | 110822 |
| 16 | $0.03 | 112413 |
| 17 | $0.03 | 113591 |
| 18 | $0.03 | 114379 |
| 19 | $0.09 | 122805 |
| 20 | $0.03 | 123560 |
| 21 | $0.03 | 123856 |
| 22 | $0.03 | 124598 |
| 23 | $0.05 | 127269 |
| 24 | $0.03 | 128442 |
| 25 | $0.03 | 128965 |
| 26 | $0.03 | 129723 |
| 27 | $0.03 | 130323 |
| 28 | $0.04 | 132521 |
| 29 | $0.03 | 133272 |
| 30 | $0.03 | 134207 |
| 31 | $0.10 | 143028 |
| 32 | $0.04 | 144005 |
| 33 | $0.03 | 144606 |
| 34 | $0.03 | 144917 |
| 35 | $0.03 | 145563 |
| 36 | $0.10 | 154399 |
| 37 | $0.04 | 155381 |
| 38 | $0.04 | 156109 |
| 39 | $0.04 | 156814 |
| 40 | $0.04 | 157676 |
| 41 | $0.04 | 158243 |
| 42 | $0.04 | 158917 |
| 43 | $0.04 | 159907 |
| 44 | $0.04 | 161123 |
| 45 | $0.04 | 162458 |
| 46 | $0.04 | 163802 |
| 47 | $0.04 | 164670 |
| 48 | $0.04 | 165858 |
| 49 | $0.04 | 166980 |
| 50 | $0.05 | 169036 |
| 51 | $0.04 | 169773 |
| 52 | $0.04 | 170613 |
| 53 | $0.04 | 171327 |
| 54 | $0.04 | 172599 |
| 55 | $0.04 | 173192 |
| 56 | $0.04 | 173779 |
| 57 | $0.07 | 178402 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 29 | 25 | 2 | 4 | 3343 | 17160 | 46792 | 0.15 |
| red | 4 | 2 | 0 | 0 | 102 | 64 | 15 | 30 | 5003 | 425283 | 91855 | 0.32 |
| green | 4 | 2 | 0 | 0 | 274 | 57 | 21 | 40 | 5091 | 587636 | 64575 | 0.27 |
| refactor | 3 | 1 | 0 | 0 | 130 | 21 | 10 | 20 | 1578 | 271952 | 46191 | 0.16 |
| diff | 2 | 1 | 0 | 0 | 282 | 33 | 12 | 24 | 3193 | 330858 | 48629 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 378 | 90 | 22 | 44 | 8142 | 524552 | 150844 | 0.51 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 439 | 110 | 38 | 74 | 10066 | 1108337 | 147198 | 0.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| wrong-test-route.sh, given a develop-green report whose only case line is one `SUPERSEDED:` line naming an earlier step's frozen pytest case by its bare name cut short with a trailing `…` (no `WRONG_TEST:` line; #2173's form, which today answers `revise`), prints `red <the full case name>` and exits 0; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 73 | 26 | 52 | 6888 | 746198 | 118227 | 0.44 | 428 | unknown | 1/5 | nothing-left |  |  | full |
| wrong-test-route.sh, given a revise-green report whose only case line is one `SUPERSEDED:` line naming an older pytest case by its node id `<file>.py::<case>` followed by prose (no `WRONG_TEST:` line; #2249's form, which today answers `revise`), prints `red <case>` and exits 0; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 69 | 20 | 38 | 4784 | 538673 | 84394 | 0.31 | 299 | unknown | 0/5 | nothing-left |  |  | full |
| REVISE.md states that a revise-green report carrying a `SUPERSEDED:` line, with or without `WRONG_TEST:`, is routed through `$S/wrong-test-route.sh .tdd/revise-green-<k>.out '<target-test-id>'` before the attempt is counted, exactly as a `WRONG_TEST:` report is (exit 0: no `revise` mark, no `REVISE_BUDGET` attempt, the red-contradicted red), and the verbatim WRONG_TEST_SENTENCE pin in skills/tdd/scripts/tests/py/unit/test_skill_tests_frozen.py moves with it in the same commit ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 12 | 24 | 3193 | 330858 | 48629 | 0.19 | 344 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| wrong-test-route.sh, given a develop-green report whose only case line is one `SUPERSEDED:` line naming an earlier step's frozen pytest case by its bare name cut short with a trailing `…` (no `WRONG_TEST:` line; #2173's form, which today answers `revise`), prints `red <the full case name>` and exits 0; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 121 | 0.11 |
| wrong-test-route.sh, given a revise-green report whose only case line is one `SUPERSEDED:` line naming an older pytest case by its node id `<file>.py::<case>` followed by prose (no `WRONG_TEST:` line; #2249's form, which today answers `revise`), prints `red <case>` and exits 0; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.05 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 11 | 3 | 3 | 3 | 20 | 4 | 3 | 3 | 9 | 135 | 5 |
| fast | 32 | 25 | 76 | 26 | 72 | 24 | 24 | 28 | 24 |  |  |  |
| target | 1 | 4 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 60 | 118 | 18208 | 1632889 | 298042 | 1.09 |
