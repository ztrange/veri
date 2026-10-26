### 📊 Metrics — issue 2474

Wall time for the issue: 3517 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 7 planned.
Outcome: the run bailed — rebased-tip-red, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.21 over 70 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88668 tokens, largest 177109 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88668 |
| 2 | $0.03 | 90735 |
| 3 | $0.03 | 92363 |
| 4 | $0.02 | 93025 |
| 5 | $0.02 | 93385 |
| 6 | $0.02 | 94138 |
| 7 | $0.02 | 94736 |
| 8 | $0.02 | 95334 |
| 9 | $0.04 | 98004 |
| 10 | $0.05 | 102105 |
| 11 | $0.04 | 104955 |
| 12 | $0.04 | 107819 |
| 13 | $0.04 | 110303 |
| 14 | $0.04 | 112824 |
| 15 | $0.03 | 114263 |
| 16 | $0.04 | 115892 |
| 17 | $0.08 | 123209 |
| 18 | $0.04 | 125235 |
| 19 | $0.04 | 126721 |
| 20 | $0.03 | 127240 |
| 21 | $0.03 | 127852 |
| 22 | $0.03 | 128483 |
| 23 | $0.03 | 129452 |
| 24 | $0.03 | 130262 |
| 25 | $0.03 | 130870 |
| 26 | $0.06 | 134954 |
| 27 | $0.03 | 135656 |
| 28 | $0.03 | 136455 |
| 29 | $0.03 | 137274 |
| 30 | $0.03 | 137640 |
| 31 | $0.04 | 139519 |
| 32 | $0.03 | 140405 |
| 33 | $0.04 | 141364 |
| 34 | $0.04 | 142267 |
| 35 | $0.04 | 143185 |
| 36 | $0.03 | 143954 |
| 37 | $0.03 | 144673 |
| 38 | $0.03 | 145044 |
| 39 | $0.04 | 146154 |
| 40 | $0.04 | 148052 |
| 41 | $0.04 | 149292 |
| 42 | $0.03 | 149673 |
| 43 | $0.04 | 151422 |
| 44 | $0.04 | 152110 |
| 45 | $0.04 | 153055 |
| 46 | $0.04 | 153704 |
| 47 | $0.04 | 154516 |
| 48 | $0.03 | 154893 |
| 49 | $0.04 | 155518 |
| 50 | $0.04 | 157017 |
| 51 | $0.04 | 157557 |
| 52 | $0.04 | 159104 |
| 53 | $0.04 | 159665 |
| 54 | $0.04 | 160707 |
| 55 | $0.04 | 161352 |
| 56 | $0.04 | 162289 |
| 57 | $0.05 | 164726 |
| 58 | $0.04 | 165107 |
| 59 | $0.04 | 165359 |
| 60 | $0.04 | 166104 |
| 61 | $0.04 | 166382 |
| 62 | $0.04 | 166658 |
| 63 | $0.04 | 167171 |
| 64 | $0.04 | 167967 |
| 65 | $0.04 | 169330 |
| 66 | $0.04 | 170307 |
| 67 | $0.04 | 171164 |
| 68 | $0.04 | 171773 |
| 69 | $0.04 | 172898 |
| 70 | $0.07 | 177109 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 59 | 52 | 5 | 10 | 4569 | 129091 | 57172 | 0.20 |
| diff | 4 | 2 | 0 | 0 | 491 | 53 | 15 | 30 | 4321 | 403571 | 80171 | 0.28 |
| red | 7 | 3 | 0 | 0 | 183 | 143 | 32 | 62 | 14573 | 998223 | 153016 | 0.63 |
| green | 6 | 3 | 0 | 0 | 759 | 107 | 36 | 68 | 10485 | 1090428 | 130141 | 0.54 |
| refactor | 3 | 0 | 0 | 0 | 20 | 13 | 7 | 14 | 708 | 166344 | 66939 | 0.19 |
| pin | 1 | 1 | 0 | 0 | 23 | 16 | 3 | 6 | 945 | 80641 | 16401 | 0.06 |
| prose | 23 | 0 | 0 | 0 | 481 | 417 | 23 | 46 | 60453 | 35145 | 365493 | 1.52 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 10 | 1 | 0 | 806 | 176 | 37 | 72 | 14574 | 996859 | 209515 | 0.77 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 729 | 208 | 61 | 118 | 21027 | 1871439 | 294325 | 1.13 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The case test_a_full_pass_writes_one_graded_line_carrying_the_unit_its_signature_the_date_and_the_grading_events_id in skills/tdd/scripts/tests/py/test_grade_prose_process.py checks the first four fields of the GRADED line (unit, signature, date, grading id) without requiring the line to hold exactly four, so a GRADED line that also names its grader template still passes it; a test-only change, no production change ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 7 | 14 | 2268 | 174791 | 48547 | 0.16 | 376 | n/a | n/a | n/a |  |  | full |
| A full grade-prose.sh PASS writes a GRADED line that states which grader template its signature was produced under (an identity derived from GRADER_INSTRUCTIONS, such as a short hash of it), and the line keeps the unit, signature, date and grading id it carries today; a small in-process case, no real process ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 70 | 26 | 52 | 8640 | 821753 | 118165 | 0.46 | 490 | unknown | 0/5 | nothing-left |  |  | full |
| Every committed GRADED line (skills/tdd/GRADED, operator/GRADED and the ten skills/veri-*/GRADED files) states which grader template its signature was produced under, and a case reads that template identity back from a committed GRADED line of the repository and finds it present and well-formed (it never requires it to equal the current GRADER_INSTRUCTIONS identity, so a later template edit leaves the case green); the committed signatures stay valid, so prose-owed.sh <repo-root> stays at exit 0 ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 85 | 23 | 42 | 7758 | 652519 | 105374 | 0.41 | 341 | unknown | 0/5 | nothing-left |  |  | full |
| The case test_a_units_signature_changes_when_the_grader_prompt_template_changes_and_when_the_grader_conf_model_changes_1725 in skills/tdd/scripts/tests/py/unit/test_grade_prose.py asserts only that a unit's signature changes when the grader.conf model changes, dropping its assertion that a GRADER_INSTRUCTIONS change changes the signature (renamed to say so); a test-only change, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 8 | 16 | 2053 | 228780 | 31624 | 0.12 | 192 | n/a | n/a | n/a |  |  | full |
| An edit to GRADER_INSTRUCTIONS that changes no requirement row and no unit text leaves prose-owed.sh <repo-root> at exit 0, with every committed signature still valid: grade_prose.signature no longer hashes GRADER_INSTRUCTIONS (still hashing the unit text, its requirement claims and the grader.conf model), and the green recomputes every committed GRADED line's signature field under the new formula over unchanged inputs, keeping its template identity, date and grading id and regrading no unit, so make unit stays green; a small in-process case pins today's exit 1 (red on current code, green after) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 77 | 20 | 40 | 6332 | 614953 | 102466 | 0.38 | 280 | unknown | 0/5 | nothing-left |  |  | full |
| A change to one unit's text, or to that unit's requirement rows, makes prose-owed.sh <repo-root> exit 1 printing that unit and only that unit, while every other unit's signature stays valid; a small in-process case ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 9 | 16 | 3981 | 246411 | 40492 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A full grade-prose.sh PASS writes a GRADED line that states which grader template its signature was produced under (an identity derived from GRADER_INSTRUCTIONS, such as a short hash of it), and the line keeps the unit, signature, date and grading id it carries today; a small in-process case, no real process ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.09 |
| Every committed GRADED line (skills/tdd/GRADED, operator/GRADED and the ten skills/veri-*/GRADED files) states which grader template its signature was produced under, and a case reads that template identity back from a committed GRADED line of the repository and finds it present and well-formed (it never requires it to equal the current GRADER_INSTRUCTIONS identity, so a later template edit leaves the case green); the committed signatures stay valid, so prose-owed.sh <repo-root> stays at exit 0 ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| An edit to GRADER_INSTRUCTIONS that changes no requirement row and no unit text leaves prose-owed.sh <repo-root> at exit 0, with every committed signature still valid: grade_prose.signature no longer hashes GRADER_INSTRUCTIONS (still hashing the unit text, its requirement claims and the grader.conf model), and the green recomputes every committed GRADED line's signature field under the new formula over unchanged inputs, keeping its template identity, date and grading id and regrading no unit, so make unit stays green; a small in-process case pins today's exit 1 (red on current code, green after) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.05 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 18 | 21 | 18 | 19 | 20 | 17 | 23 | 18 | 21 | 21 | 19 | 19 |  |  |  |  |  |  |  |  |
| affected | 74 | 75 | 86 | 2 | 2 | 2 | 125 | 2 | 2 | 2 | 90 | 1 | 75 | 2 | 87 | 1 | 1 | 81 | 1 | 2 |
| target | 1 | 1 | 1 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 121 | 236 | 96054 | 2903443 | 869333 | 3.42 |
