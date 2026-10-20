### 📊 Metrics — issue 1874

Wall time for the issue: 7509 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 13 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1877.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 25 | 22 | 4 | 8 | 2776 | 96519 | 34369 | 0.12 |
| red | 27 | 9 | 1 | 0 | 1459 | 636 | 190 | 374 | 67399 | 6211186 | 595404 | 3.53 |
| green | 22 | 9 | 2 | 0 | 3605 | 384 | 148 | 284 | 40100 | 4316474 | 426874 | 2.07 |
| refactor | 18 | 9 | 0 | 0 | 400 | 104 | 49 | 96 | 9365 | 1221139 | 253355 | 0.85 |
| pin | 4 | 3 | 1 | 0 | 82 | 55 | 15 | 30 | 5344 | 415415 | 50158 | 0.22 |
| diff | 2 | 1 | 0 | 0 | 136 | 40 | 15 | 28 | 4049 | 444342 | 37153 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 36 | 32 | 4 | 0 | 2521 | 428 | 153 | 298 | 43942 | 4111273 | 543149 | 2.21 |
| developer | claude-sonnet-5-5 | 26 | 0 | 0 | 0 | 1227 | 377 | 146 | 282 | 42424 | 4477026 | 506763 | 2.14 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 1959 | 436 | 122 | 240 | 42667 | 4116776 | 347401 | 2.62 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 114 | 0.53 | 0 | 0.00 |
| green | 2549 | 1.07 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 46 | 0.11 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A grader leaf that prints an all-PASS GRADES block and then exits 1 makes grade-prose.sh exit 2, print nothing on stdout and append no grading event to .tdd/events.jsonl (a medium case, a real stub claude through supervise.sh) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 70 | 30 | 58 | 7768 | 853407 | 116084 | 0.45 | 525 | unknown | 0/5 | nothing-left |  |  | full |
| A grader leaf whose reply carries a 429 rate-limit error alongside an all-PASS GRADES block makes grade-prose.sh exit 2, print nothing on stdout and append no grading event (a medium case, a real stub claude through supervise.sh) ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 143 | 35 | 68 | 13294 | 1181208 | 92252 | 0.69 | unknown | 1/2 | unknown | unknown |  |  | pin |
| A grader launch that supervise.sh refuses, with an all-PASS .tdd/grade-prose.log left by an earlier grading on disk, makes grade-prose.sh exit 2, print nothing on stdout and append no grading event: the stale log is never read (a medium case, a real supervise.sh) ⟦criterion 1⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 105 | 29 | 58 | 10532 | 979703 | 90580 | 0.67 | unknown | 2/2 | unknown | unknown |  |  | pin |
| The prompt grade-prose renders for a unit carries the PoC's grader instructions from specs/grader-poc/grader-system.txt, asking for the reply to end with a BEGIN GRADES … END GRADES block holding one line per requirement in the order given and the VERDICT: line inside the block ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 28 | 56 | 8255 | 823092 | 97782 | 0.41 | 202 | unknown | 0/5 | nothing-left |  |  | full |
| A reply in the PoC's pass-3 shape — one line per requirement and the VERDICT: line inside the BEGIN GRADES … END GRADES block, nothing after END GRADES — parses: all PASS with VERDICT: PASS exits 0, a FAIL line with VERDICT: REJECT exits 1 and prints the failing line ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 95 | 34 | 66 | 10637 | 1054237 | 110775 | 0.49 | 578 | unknown | 0/5 | nothing-left |  |  | full |
| Every existing grade-prose case whose stub reply puts its VERDICT: line after END GRADES instead puts it inside the block, as the last line before END GRADES, each case keeping the outcome it asserts; no production code changes ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 15 | 28 | 4049 | 444342 | 37153 | 0.18 | 156 | n/a | n/a | n/a |  |  | full |
| A reply with any line after END GRADES, a trailing VERDICT: line included (END GRADES, then VERDICT: REJECT, then VERDICT: PASS), makes grade-prose.sh exit 2 and append no grading event ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 69 | 28 | 54 | 7536 | 826724 | 101502 | 0.41 | 347 | unknown | 0/5 | nothing-left |  |  | full |
| A line starting with # inside a fenced code block, even one whose text equals the unit's heading, never starts the unit's section: the section starts only at the real heading outside any fence ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 12 | 24 | 3929 | 358188 | 31664 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| A unit with no requirements list in the requirements file makes grade-prose.sh exit 2 before launching anything ⟦criterion 3⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 174 | 52 | 100 | 18096 | 1586133 | 156142 | 1.02 | 288 | 2/2 | 0/5 | nothing-left |  |  | full |
| A GRADES line whose grade word is anything other than exactly PASS or FAIL, such as PASS-ish or FAIL-ish, makes grade-prose.sh exit 2 and append no grading event ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 62 | 23 | 44 | 6743 | 612838 | 95643 | 0.37 | 138 | unknown | 0/5 | nothing-left |  |  | full |
| The grader leaf is launched with no tools: the command the stub claude receives carries --tools with an empty value (a medium case, a real stub claude through supervise.sh) ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 134 | 52 | 102 | 13732 | 1591129 | 130742 | 0.70 | 1017 | 1/2 | 0/5 | nothing-left |  |  | full |
| The grader leaf's model comes only from grader.conf: with VERI_MODEL_GRADER set in the environment the stub claude still receives grader.conf's model (a medium case, a real stub claude through supervise.sh) ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 78 | 32 | 62 | 7922 | 920050 | 99337 | 0.42 | 454 | unknown | 0/5 | nothing-left |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_fast_tier_guard.py — FAILED test_the_guard_with_the_real_exemption_table_finds_no_offence_in_the_fast_tier_as_committed_and_names_a_planted_one_by_file_and_line (unit/test_grade_prose.py:57, :91, :115: starts a process through subprocess) ⟦suite-repair⟧ ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 132 | 47 | 92 | 13764 | 1377505 | 203288 | 0.87 | 1892 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A grader leaf that prints an all-PASS GRADES block and then exits 1 makes grade-prose.sh exit 2, print nothing on stdout and append no grading event to .tdd/events.jsonl (a medium case, a real stub claude through supervise.sh) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 56 | 0.09 |
| The prompt grade-prose renders for a unit carries the PoC's grader instructions from specs/grader-poc/grader-system.txt, asking for the reply to end with a BEGIN GRADES … END GRADES block holding one line per requirement in the order given and the VERDICT: line inside the block ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 22 | 0.10 |
| A reply in the PoC's pass-3 shape — one line per requirement and the VERDICT: line inside the BEGIN GRADES … END GRADES block, nothing after END GRADES — parses: all PASS with VERDICT: PASS exits 0, a FAIL line with VERDICT: REJECT exits 1 and prints the failing line ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 64 | 0.10 |
| A reply with any line after END GRADES, a trailing VERDICT: line included (END GRADES, then VERDICT: REJECT, then VERDICT: PASS), makes grade-prose.sh exit 2 and append no grading event ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 62 | 0.09 |
| A unit with no requirements list in the requirements file makes grade-prose.sh exit 2 before launching anything ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 21 | 0.09 |
| A GRADES line whose grade word is anything other than exactly PASS or FAIL, such as PASS-ish or FAIL-ish, makes grade-prose.sh exit 2 and append no grading event ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 24 | 0.10 |
| The grader leaf is launched with no tools: the command the stub claude receives carries --tools with an empty value (a medium case, a real stub claude through supervise.sh) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 63 | 0.10 |
| The grader leaf's model comes only from grader.conf: with VERI_MODEL_GRADER set in the environment the stub claude still receives grader.conf's model (a medium case, a real stub claude through supervise.sh) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 67 | 0.10 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_fast_tier_guard.py — FAILED test_the_guard_with_the_real_exemption_table_finds_no_offence_in_the_fast_tier_as_committed_and_names_a_planted_one_by_file_and_line (unit/test_grade_prose.py:57, :91, :115: starts a process through subprocess) ⟦suite-repair⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 21 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 36 | 36 | 36 | 36 | 0 | 36 | 36 | 36 | 36 | 37 | 37 | 1 | 1 | 1 | 37 | 1 | 40 | 40 | 40 | 40 | 40 | 41 | 40 | 40 | 41 | 41 | 41 | 0 | 41 | 42 | 41 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 44 | 42 | 0 | 0 | 87 | 1 | 134 | 46 | 0 | 150 | 43 | 44 | 44 | 0 | 44 | 44 | 3 | 3 | 3 | 3 |
| fast | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 5 | 5 | 5 | 6 | 5 | 5 | 5 | 6 | 5 | 5 | 0 | 6 | 6 | 5 | 5 | 5 | 5 | 5 | 6 | 6 | 5 | 6 | 7 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 2 | 1 | 0 | 1 | 0 | 3 | 0 | 7 | 5 | 5 | 6 | 0 | 1 | 0 | 42 | 42 | 44 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 421 | 820 | 129033 | 12705075 | 1397313 | 6.97 |
