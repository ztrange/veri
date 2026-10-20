### 📊 Metrics — issue 1862

Wall time for the issue: 9894 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1884.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.05 over 95 turns, in 1 sessions.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 84297 |
| 2 | $0.03 | 85658 |
| 3 | $0.03 | 87557 |
| 4 | $0.02 | 87858 |
| 5 | $0.02 | 88262 |
| 6 | $0.02 | 88561 |
| 7 | $0.02 | 88927 |
| 8 | $0.02 | 89590 |
| 9 | $0.02 | 89979 |
| 10 | $0.02 | 90708 |
| 11 | $0.02 | 91145 |
| 12 | $0.03 | 92796 |
| 13 | $0.04 | 95269 |
| 14 | $0.04 | 98132 |
| 15 | $0.04 | 101224 |
| 16 | $0.07 | 106855 |
| 17 | $0.05 | 110236 |
| 18 | $0.04 | 112871 |
| 19 | $0.04 | 114614 |
| 20 | $0.03 | 115255 |
| 21 | $0.03 | 115787 |
| 22 | $0.03 | 116338 |
| 23 | $0.03 | 116807 |
| 24 | $0.03 | 117571 |
| 25 | $0.06 | 122428 |
| 26 | $0.03 | 123122 |
| 27 | $0.03 | 124138 |
| 28 | $0.04 | 125392 |
| 29 | $0.04 | 127824 |
| 30 | $0.03 | 128507 |
| 31 | $0.03 | 128861 |
| 32 | $0.03 | 129666 |
| 33 | $0.03 | 130691 |
| 34 | $0.03 | 131397 |
| 35 | $0.03 | 132347 |
| 36 | $0.03 | 132643 |
| 37 | $0.03 | 133668 |
| 38 | $0.03 | 134560 |
| 39 | $0.03 | 135265 |
| 40 | $0.04 | 136253 |
| 41 | $0.04 | 137704 |
| 42 | $0.03 | 138464 |
| 43 | $0.04 | 139409 |
| 44 | $0.04 | 140463 |
| 45 | $0.04 | 141566 |
| 46 | $0.04 | 142694 |
| 47 | $0.03 | 143424 |
| 48 | $0.04 | 144881 |
| 49 | $0.04 | 145612 |
| 50 | $0.04 | 147055 |
| 51 | $0.04 | 147999 |
| 52 | $0.04 | 149243 |
| 53 | $0.04 | 150381 |
| 54 | $0.04 | 151035 |
| 55 | $0.04 | 151836 |
| 56 | $0.04 | 152722 |
| 57 | $0.03 | 153175 |
| 58 | $0.04 | 153877 |
| 59 | $0.04 | 154545 |
| 60 | $0.04 | 155342 |
| 61 | $0.04 | 156513 |
| 62 | $0.04 | 157281 |
| 63 | $0.04 | 158856 |
| 64 | $0.04 | 159591 |
| 65 | $0.06 | 162897 |
| 66 | $0.05 | 164482 |
| 67 | $0.04 | 165229 |
| 68 | $0.04 | 166473 |
| 69 | $0.04 | 167190 |
| 70 | $0.04 | 168234 |
| 71 | $0.04 | 168647 |
| 72 | $0.04 | 169004 |
| 73 | $0.04 | 169732 |
| 74 | $0.04 | 170668 |
| 75 | $0.04 | 171829 |
| 76 | $0.04 | 172518 |
| 77 | $0.05 | 173955 |
| 78 | $0.04 | 174584 |
| 79 | $0.04 | 174991 |
| 80 | $0.05 | 176303 |
| 81 | $0.04 | 176981 |
| 82 | $0.04 | 177928 |
| 83 | $0.04 | 178200 |
| 84 | $0.04 | 178750 |
| 85 | $0.05 | 179985 |
| 86 | $0.04 | 180391 |
| 87 | $0.04 | 180861 |
| 88 | $0.04 | 181716 |
| 89 | $0.04 | 182337 |
| 90 | $0.04 | 182695 |
| 91 | $0.04 | 183016 |
| 92 | $0.04 | 183508 |
| 93 | $0.05 | 184598 |
| 94 | $0.04 | 184931 |
| 95 | $0.04 | 185411 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 15 | 1 | 2 | 1908 | 16409 | 14958 | 0.06 |
| diff | 6 | 3 | 0 | 0 | 2769 | 165 | 62 | 124 | 17336 | 2007397 | 239497 | 0.97 |
| red | 10 | 4 | 0 | 0 | 734 | 173 | 56 | 112 | 19077 | 1851224 | 214279 | 0.91 |
| pin | 2 | 2 | 0 | 0 | 34 | 26 | 9 | 18 | 2615 | 246103 | 30904 | 0.13 |
| green | 10 | 4 | 1 | 0 | 1032 | 186 | 60 | 118 | 17816 | 1770098 | 175964 | 0.86 |
| refactor | 8 | 4 | 0 | 0 | 190 | 97 | 33 | 64 | 8062 | 889839 | 124493 | 0.48 |
| rebase | 2 | 1 | 0 | 0 | 2637 | 119 | 36 | 70 | 7809 | 1273509 | 161508 | 0.61 |
| predicate | 1 | 0 | 0 | 0 | 20 | 17 | 6 | 12 | 1300 | 167042 | 14338 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 20 | 19 | 1 | 0 | 2674 | 319 | 94 | 186 | 27937 | 2573499 | 346099 | 1.40 |
| developer | claude-sonnet-5-5 | 18 | 0 | 0 | 0 | 4685 | 442 | 158 | 312 | 44762 | 5319760 | 595137 | 2.47 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 74 | 37 | 11 | 22 | 3224 | 328362 | 34705 | 0.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 150 | 0.34 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skills/tdd/SKILL.md's *Scope & plan* section gains a planning rule: when a criterion changes text or output that existing cases outside the step's own Red pin (a usage string, a constant, rendered prompt text compared verbatim or by checksum), the plan holds a step that updates those older cases, placed ahead of the step that changes the text; and skills/tdd/scripts/prompts/verify-plan.md tells the plan verifier to REJECT a plan that changes such text without that step; every checksum or verbatim pin the changed prompt text moves (the `plan` rows of tests/py/unit/test_emitted_text.py) moves in the same commit ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 20 | 40 | 5098 | 704989 | 43241 | 0.23 | 750 | n/a | n/a | n/a |  |  | full |
| a case on the rendered `plan` verify prompt (build-verify-prompt.sh plan, driven in-process) pins that it tells the verifier to REJECT a plan changing text or output older cases pin without a step updating those cases ahead of the step that changes it; small case, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 17 | 34 | 4783 | 596613 | 48383 | 0.23 | unknown | unknown | unknown | unknown |  |  | pin |
| a prose case on skills/tdd/SKILL.md's *Scope & plan* section pins the rule that a criterion changing text older cases pin gets a step updating those cases, ahead of the step that changes the text; small case, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 12 | 24 | 3993 | 377556 | 35910 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| wrong-test-route.sh, given a green report carrying one `SUPERSEDED: <case>` line per older case that fails only because the step supersedes what it pins, naming two or more existing older cases outside the step's Red record, prints `supersede <case> <case> …` naming every one of them and exits 0, as the step's one free reroute (a later report in a step whose log already holds a reroute event still prints `revise`); pinned by a case whose step changes a usage string that two older cases compare against ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 26 | 50 | 8911 | 710302 | 94265 | 0.40 | 272 | unknown | 1/5 | nothing-left |  |  | full |
| build-develop-prompt.sh renders a `red-supersede` prompt from `<spec> <step> <test-cmd> <green-report> <case> [<case> …]` (a new template under skills/tdd/scripts/prompts/) that names every listed case, lets the leaf update the expectation of exactly those existing cases to the step's criterion, and forbids new cases and production code; the usage text build-develop-prompt.sh prints is left unchanged ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 95 | 29 | 58 | 10100 | 922051 | 126236 | 0.51 | 272 | unknown | 0/5 | nothing-left |  |  | full |
| skills/tdd/scripts/prompts/develop-green.md (and the revise-green rendering that shares its wrong-test report) tells the green leaf to report one `SUPERSEDED: <case>` line per older case that fails only because the step supersedes what it pins, distinct from a `WRONG_TEST:` line for any other conflict; every checksum or verbatim pin the changed text moves (the `green` and `revise green` rows of test_emitted_text.py, and any report-format registry entry) moves in the same commit ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 24 | 48 | 6981 | 817911 | 41590 | 0.26 | 443 | n/a | n/a | n/a |  |  | full |
| skills/tdd/SKILL.md's Green section and SCRIPTS.md's wrong-test-route.sh entry describe the `supersede` route: write the `reroute` event, launch the `red-supersede` red through supervise.sh over every named case, verify each edited case with verify-red like any red, re-record the step's frozen tests over every test path, then retry green — writing no `revise` mark and spending no `REVISE_BUDGET` attempt ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 18 | 36 | 5257 | 484497 | 154666 | 0.49 | 1716 | n/a | n/a | n/a |  |  | full |
| wrong-test-route.sh never gives the multi-case reroute to a conflict naming an older case the step's change does not supersede: a green report whose `SUPERSEDED:` lines are joined by a `WRONG_TEST:` line naming another existing older case that no `SUPERSEDED:` line names prints `revise` and exits 3, as today's revise path; pinned by a case ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 128 | 44 | 88 | 12750 | 1336744 | 130169 | 0.65 | 340 | 1/2 | 1/5 | nothing-left |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_report_formats.py — FAILED test_1568_every_stop_skip_give_up_or_say_so_line_in_the_real_develop_prompts_names_a_declared_format_or_is_exempt: AssertionError: develop-red-supersede.md:89 (a stop line in the new red-supersede prompt names no declared report format and is not exempt) ⟦suite-repair⟧ ⟦criterion 3⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 223 | 72 | 140 | 16142 | 2254549 | 286523 | 1.10 | 845 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| wrong-test-route.sh, given a green report carrying one `SUPERSEDED: <case>` line per older case that fails only because the step supersedes what it pins, naming two or more existing older cases outside the step's Red record, prints `supersede <case> <case> …` naming every one of them and exits 0, as the step's one free reroute (a later report in a step whose log already holds a reroute event still prints `revise`); pinned by a case whose step changes a usage string that two older cases compare against ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 54 | 0.12 |
| build-develop-prompt.sh renders a `red-supersede` prompt from `<spec> <step> <test-cmd> <green-report> <case> [<case> …]` (a new template under skills/tdd/scripts/prompts/) that names every listed case, lets the leaf update the expectation of exactly those existing cases to the step's criterion, and forbids new cases and production code; the usage text build-develop-prompt.sh prints is left unchanged ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 42 | 0.13 |
| wrong-test-route.sh never gives the multi-case reroute to a conflict naming an older case the step's change does not supersede: a green report whose `SUPERSEDED:` lines are joined by a `WRONG_TEST:` line naming another existing older case that no `SUPERSEDED:` line names prints `revise` and exits 3, as today's revise path; pinned by a case ⟦criterion 3⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 53 | 0.14 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_report_formats.py — FAILED test_1568_every_stop_skip_give_up_or_say_so_line_in_the_real_develop_prompts_names_a_declared_format_or_is_exempt: AssertionError: develop-red-supersede.md:89 (a stop line in the new red-supersede prompt names no declared report format and is not exempt) ⟦suite-repair⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 41 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 12 | 12 | 15 | 14 | 13 | 13 | 13 | 13 | 13 | 13 | 12 | 12 | 12 | 13 | 12 | 12 | 13 | 12 | 12 | 13 | 13 | 13 | 13 |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 267 | 265 | 3 | 2 | 2 | 2 | 3 | 3 | 2 | 1 | 4 | 5 | 8 | 8 | 4 | 0 | 8 | 267 | 0 | 311 | 309 | 311 | 310 | 2 | 2 | 0 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 |
| target | 1 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 636 | 632 | 642 | 635 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 263 | 520 | 75923 | 8221621 | 975941 | 4.09 |
