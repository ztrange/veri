### 📊 Metrics — issue 1808

Wall time for the issue: 6758 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 12 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1876.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.89 over 89 turns, in 1 sessions.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 84041 |
| 2 | $0.03 | 85753 |
| 3 | $0.03 | 87665 |
| 4 | $0.02 | 87930 |
| 5 | $0.02 | 88320 |
| 6 | $0.02 | 88613 |
| 7 | $0.02 | 88990 |
| 8 | $0.02 | 89579 |
| 9 | $0.02 | 90098 |
| 10 | $0.02 | 90678 |
| 11 | $0.02 | 90993 |
| 12 | $0.09 | 99438 |
| 13 | $0.03 | 100584 |
| 14 | $0.03 | 102300 |
| 15 | $0.05 | 106125 |
| 16 | $0.10 | 115553 |
| 17 | $0.08 | 122165 |
| 18 | $0.03 | 122499 |
| 19 | $0.03 | 123015 |
| 20 | $0.03 | 123762 |
| 21 | $0.03 | 123967 |
| 22 | $0.03 | 125173 |
| 23 | $0.03 | 126068 |
| 24 | $0.03 | 126956 |
| 25 | $0.03 | 127641 |
| 26 | $0.03 | 127950 |
| 27 | $0.03 | 128771 |
| 28 | $0.03 | 129740 |
| 29 | $0.03 | 130641 |
| 30 | $0.04 | 132208 |
| 31 | $0.03 | 133152 |
| 32 | $0.03 | 133858 |
| 33 | $0.04 | 134947 |
| 34 | $0.03 | 135862 |
| 35 | $0.04 | 137301 |
| 36 | $0.05 | 140416 |
| 37 | $0.05 | 142880 |
| 38 | $0.03 | 143333 |
| 39 | $0.04 | 144348 |
| 40 | $0.04 | 145389 |
| 41 | $0.03 | 145971 |
| 42 | $0.04 | 146958 |
| 43 | $0.03 | 147584 |
| 44 | $0.04 | 149316 |
| 45 | $0.03 | 149851 |
| 46 | $0.04 | 151012 |
| 47 | $0.04 | 151687 |
| 48 | $0.03 | 151936 |
| 49 | $0.04 | 153251 |
| 50 | $0.03 | 153744 |
| 51 | $0.03 | 153948 |
| 52 | $0.05 | 155893 |
| 53 | $0.04 | 156477 |
| 54 | $0.04 | 157426 |
| 55 | $0.04 | 158420 |
| 56 | $0.04 | 159016 |
| 57 | $0.03 | 159219 |
| 58 | $0.04 | 160439 |
| 59 | $0.04 | 160913 |
| 60 | $0.04 | 161860 |
| 61 | $0.04 | 162359 |
| 62 | $0.04 | 162562 |
| 63 | $0.04 | 163340 |
| 64 | $0.03 | 163586 |
| 65 | $0.06 | 166374 |
| 66 | $0.04 | 166938 |
| 67 | $0.05 | 168419 |
| 68 | $0.05 | 169916 |
| 69 | $0.04 | 170398 |
| 70 | $0.04 | 170925 |
| 71 | $0.04 | 171490 |
| 72 | $0.04 | 172154 |
| 73 | $0.04 | 173180 |
| 74 | $0.04 | 174005 |
| 75 | $0.04 | 174537 |
| 76 | $0.04 | 175380 |
| 77 | $0.04 | 175823 |
| 78 | $0.04 | 176162 |
| 79 | $0.04 | 176695 |
| 80 | $0.04 | 177131 |
| 81 | $0.04 | 177886 |
| 82 | $0.04 | 178658 |
| 83 | $0.04 | 179720 |
| 84 | $0.04 | 180480 |
| 85 | $0.04 | 181050 |
| 86 | $0.04 | 181311 |
| 87 | $0.04 | 181702 |
| 88 | $0.04 | 182513 |
| 89 | $0.04 | 183233 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 13 | 1 | 2 | 1744 | 0 | 32756 | 0.10 |
| red | 12 | 3 | 0 | 0 | 412 | 295 | 78 | 156 | 35550 | 2656893 | 274474 | 1.31 |
| green | 8 | 3 | 1 | 0 | 949 | 138 | 44 | 86 | 11668 | 1213127 | 144292 | 0.71 |
| refactor | 6 | 3 | 0 | 0 | 121 | 48 | 23 | 44 | 4783 | 604783 | 85481 | 0.32 |
| pin | 6 | 6 | 0 | 0 | 128 | 94 | 33 | 66 | 10103 | 948739 | 94986 | 0.43 |
| diff | 6 | 3 | 0 | 0 | 1516 | 200 | 68 | 134 | 22451 | 2471438 | 213774 | 1.01 |
| rebase | 2 | 1 | 0 | 0 | 1316 | 51 | 8 | 18 | 2582 | 228115 | 31752 | 0.28 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 21 | 20 | 1 | 0 | 2207 | 302 | 101 | 200 | 30606 | 2758628 | 386041 | 1.55 |
| developer | claude-sonnet-5-5 | 18 | 0 | 0 | 0 | 2152 | 482 | 144 | 288 | 55179 | 5123114 | 442037 | 2.32 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 98 | 55 | 10 | 18 | 3096 | 241353 | 49437 | 0.29 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 162 | 0.41 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `wrong-test-route.sh <report> <red-test-id>`, run with `VERI_STEP` set and no `reroute` event for that step in `.tdd/events.jsonl`, prints `missing <behaviour>` and exits 0 when the report is a verify-green reason (`VERDICT: REJECT` / `REASON:` lines) carrying a `MISSING_TEST: <behaviour>` line, `<behaviour>` being that line's text after the colon; pinned by an in-process case in `tests/py/unit/test_wrong_test_route.py`. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard); if an existing test pins behaviour this changes, Red moves that test's expectation. ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 139 | 44 | 86 | 12135 | 1243849 | 151273 | 0.74 | 362 | 1/2 | 1/5 | nothing-left |  |  | full |
| `wrong-test-route.sh` prints `missing <behaviour>` and exits 0 for a revise-green report in the revise template's shape (`OUTCOME: IMPOSSIBLE — …` and `AGAINST_UNMODIFIED: N/A` around a `MISSING_TEST: <behaviour>` line), the revise answering `IMPOSSIBLE` because the fix is a test the step lacks; pinned by an in-process case. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 9 | 18 | 2983 | 259120 | 32225 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| `mutation-parity.sh <pairs-table>` writes, on stderr, one `MISSING_TEST: <old case>: no kept case fails when its mutation is applied` line for each row it reports `unproven` because the mutation turned the old case red and no kept case caught it (never for a row unproven because a case already failed unmutated, and never on stdout, so the pairs table the PR body quotes is unchanged); and `wrong-test-route.sh` given that stderr as its report prints `missing <that line's behaviour>` and exits 0. Pinned by a case for the stderr line (a medium case marked `@pytest.mark.process(...)` when it runs a real pytest or git) and an in-process routing case. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 70 | 25 | 50 | 8267 | 727569 | 97275 | 0.40 | 266 | unknown | 0/5 | nothing-left |  |  | full |
| The `missing` route shares the per-step reroute bound with the `red <case>` (#1621) and `repair <case>` (#1765) routes: once `.tdd/events.jsonl` holds a `reroute` event for the step `VERI_STEP` names (written by any of the three routes), a `MISSING_TEST:` report answers `revise` and exits 3; and after a reroute event written for a `missing` route, a `WRONG_TEST:` naming a contradicted case or a red-record case also answers `revise` and exits 3. A reroute event for a different step does not count. Pinned by in-process cases. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 13 | 26 | 5156 | 411651 | 39002 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| A verify-green reason that rejects for a product defect — `VERDICT: REJECT` and a `REASON:` naming the defect, with no `MISSING_TEST:` and no `WRONG_TEST:` line — makes `wrong-test-route.sh` print `revise` and exit 3, so it spends revise budget as today; a `MISSING_TEST:` with an empty behaviour also answers `revise`. Pinned by in-process cases. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 9 | 18 | 3531 | 266495 | 34924 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `build-develop-prompt.sh red-missing <issue-spec-file> <step-text> <test-cmd> <reason-file>` renders a new `develop-red-missing` prompt carrying the reason file's text verbatim as the brief, telling the leaf to add exactly one case that pins the behaviour the reason's `MISSING_TEST:` line names (no production code, never editing another case), run the affected suites, and report the red footer (`TEST_PATH:`, `TARGET_TEST:`, `AGAINST_UNMODIFIED: FAILS | PASSES | UNTESTABLE`, `WHY:`, `FAIL_OUTPUT:` and the prediction lines); a missing `<reason-file>` argument exits 2 with the usage. The new template and every checksum or verbatim pin it moves (`report_formats.py`, `test_build_develop_prompt.py`, `test_emitted_text.py` and the like) land in one commit. ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 78 | 25 | 48 | 7949 | 927240 | 55406 | 0.31 | 336 | n/a | n/a | n/a |  |  | full |
| A case on the prompt `build-develop-prompt.sh red-missing` renders pins that it carries the reason file's `MISSING_TEST:` line verbatim and tells the leaf to add one case pinning that behaviour, writing no production code and editing no other case; and that a missing `<reason-file>` argument exits 2 with the usage on stderr. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 18 | 36 | 7131 | 619826 | 47296 | 0.25 | unknown | unknown | unknown | unknown |  |  | pin |
| The verify-green prompt (`build-verify-prompt.sh green …`) tells the verifier that a REJECT whose cause is a behaviour no test pins carries one `MISSING_TEST: <behaviour>` line before its verdict; and the develop-revise prompt for green (`build-develop-prompt.sh revise green …`) tells the leaf that when the objection can only be met by a test the step lacks it answers `OUTCOME: IMPOSSIBLE` with a `MISSING_TEST: <behaviour>` line and edits no test. The template sentences and every checksum or verbatim pin they move land in one commit. ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 21 | 42 | 6011 | 763601 | 44269 | 0.25 | 184 | n/a | n/a | n/a |  |  | full |
| A case pins that the rendered verify-green prompt asks a missing-test REJECT for a `MISSING_TEST: <behaviour>` line, and that the rendered `revise green` prompt asks an `IMPOSSIBLE` whose fix is a test edit for a `MISSING_TEST: <behaviour>` line and no test edit. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 12 | 24 | 4736 | 383613 | 40963 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's Green section and REVISE.md route each of the three entries — a verify-green REJECT (`.tdd/verify-green.reason`), the conductor's mutation-parity REJECT (its stderr saved to a reason file), and a revise-green report answering `IMPOSSIBLE` — through `$S/wrong-test-route.sh` before any revise attempt is spent: on `missing <behaviour>` the conductor writes a `reroute` event, writes no `revise` mark and spends no `REVISE_BUDGET` attempt, launches the `red-missing` Red through `supervise.sh` with that reason file as its brief, sends the added case through verify-red (verify-pin when it reports `AGAINST_UNMODIFIED: PASSES`), re-records the step's frozen tests with `tests-frozen.sh record --step` over the test paths, then runs Green again; the step's second reroute of any kind and a product-defect rejection (`revise`, exit 3) spend `REVISE_BUDGET` as today. SCRIPTS.md's `wrong-test-route.sh`, `build-develop-prompt.sh` and `mutation-parity.sh` entries name the new answer, phase and stderr line. ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 69 | 22 | 44 | 8491 | 780597 | 114099 | 0.45 | 1116 | n/a | n/a | n/a |  |  | full |
| A SKILL.md/REVISE.md-reading prose case in the style of `skill-tests-frozen` pins that a `missing <behaviour>` answer from each of the three entries (verify-green REJECT, mutation-parity REJECT, revise-green `IMPOSSIBLE`) launches the `red-missing` Red with no `revise` mark and no `REVISE_BUDGET` attempt, verifies the added case with verify-red or verify-pin before Green runs again, and that the route's exit 3 spends a revise attempt; each pinned line watched red when deleted. No production change. ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 93 | 21 | 42 | 11261 | 799622 | 50616 | 0.32 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_report_formats.py — FAILED test_report_formats.py::test_1568_every_stop_skip_give_up_or_say_so_line_in_the_real_develop_prompts_names_a_declared_format_or_is_exempt - AssertionError: develop-red-missing.md:91 (the new develop-red-missing prompt line 91 names no declared report format and is not exempt) ⟦suite-repair⟧ ⟦criterion 1⟧ | 8 | 4 | 0 | 0 | 0 | 0 | 122 | 35 | 70 | 9486 | 939912 | 137411 | 0.69 | 782 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `wrong-test-route.sh <report> <red-test-id>`, run with `VERI_STEP` set and no `reroute` event for that step in `.tdd/events.jsonl`, prints `missing <behaviour>` and exits 0 when the report is a verify-green reason (`VERDICT: REJECT` / `REASON:` lines) carrying a `MISSING_TEST: <behaviour>` line, `<behaviour>` being that line's text after the colon; pinned by an in-process case in `tests/py/unit/test_wrong_test_route.py`. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard); if an existing test pins behaviour this changes, Red moves that test's expectation. ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 52 | 0.14 |
| `mutation-parity.sh <pairs-table>` writes, on stderr, one `MISSING_TEST: <old case>: no kept case fails when its mutation is applied` line for each row it reports `unproven` because the mutation turned the old case red and no kept case caught it (never for a row unproven because a case already failed unmutated, and never on stdout, so the pairs table the PR body quotes is unchanged); and `wrong-test-route.sh` given that stderr as its report prints `missing <that line's behaviour>` and exits 0. Pinned by a case for the stderr line (a medium case marked `@pytest.mark.process(...)` when it runs a real pytest or git) and an in-process routing case. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 37 | 0.09 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_report_formats.py — FAILED test_report_formats.py::test_1568_every_stop_skip_give_up_or_say_so_line_in_the_real_develop_prompts_names_a_declared_format_or_is_exempt - AssertionError: develop-red-missing.md:91 (the new develop-red-missing prompt line 91 names no declared report format and is not exempt) ⟦suite-repair⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 32 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 0 | 2 | 0 | 2 | 0 | 1 | 2 | 2 | 3 | 5 | 5 | 24 | 22 | 5 | 2 | 2 | 76 | 4 | 4 | 4 | 0 | 8 | 8 | 5 | 0 | 302 | 304 | 339 | 2 | 2 | 2 | 1 |
| fast | 14 | 14 | 13 | 15 | 15 | 14 | 15 | 15 | 15 | 15 | 13 | 13 | 13 | 14 | 15 | 14 | 14 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 13 | 1 | 0 | 0 | 0 | 2 | 0 | 1 | 2 | 1 | 2 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 2 |  |  |  |  |  |  |  |  |
| all | 628 | 630 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 255 | 506 | 88881 | 8123095 | 877515 | 4.16 |
