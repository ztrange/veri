### 📊 Metrics — issue 2206

Wall time for the issue: 7239 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 11 of 11 planned.
Outcome: the run bailed — suite-red, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.32 over 93 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88622 |
| 2 | $0.03 | 89825 |
| 3 | $0.03 | 91950 |
| 4 | $0.02 | 92242 |
| 5 | $0.02 | 92604 |
| 6 | $0.02 | 92933 |
| 7 | $0.02 | 93242 |
| 8 | $0.02 | 93836 |
| 9 | $0.03 | 94724 |
| 10 | $0.05 | 98796 |
| 11 | $0.04 | 100825 |
| 12 | $0.03 | 102311 |
| 13 | $0.04 | 104128 |
| 14 | $0.03 | 105300 |
| 15 | $0.03 | 106217 |
| 16 | $0.13 | 119992 |
| 17 | $0.03 | 120962 |
| 18 | $0.03 | 121929 |
| 19 | $0.03 | 123250 |
| 20 | $0.03 | 124226 |
| 21 | $0.03 | 125141 |
| 22 | $0.03 | 125873 |
| 23 | $0.03 | 126396 |
| 24 | $0.03 | 127133 |
| 25 | $0.04 | 128393 |
| 26 | $0.04 | 130276 |
| 27 | $0.03 | 130965 |
| 28 | $0.03 | 132056 |
| 29 | $0.03 | 132515 |
| 30 | $0.03 | 132885 |
| 31 | $0.09 | 140413 |
| 32 | $0.04 | 142250 |
| 33 | $0.03 | 142795 |
| 34 | $0.03 | 143084 |
| 35 | $0.04 | 144146 |
| 36 | $0.03 | 144624 |
| 37 | $0.04 | 145773 |
| 38 | $0.04 | 146625 |
| 39 | $0.04 | 148246 |
| 40 | $0.04 | 149376 |
| 41 | $0.04 | 150689 |
| 42 | $0.03 | 151152 |
| 43 | $0.04 | 152046 |
| 44 | $0.03 | 152496 |
| 45 | $0.04 | 153659 |
| 46 | $0.04 | 154710 |
| 47 | $0.03 | 155040 |
| 48 | $0.04 | 156439 |
| 49 | $0.05 | 158277 |
| 50 | $0.04 | 159044 |
| 51 | $0.04 | 160336 |
| 52 | $0.04 | 160863 |
| 53 | $0.05 | 162809 |
| 54 | $0.05 | 164915 |
| 55 | $0.04 | 165488 |
| 56 | $0.04 | 166499 |
| 57 | $0.04 | 166921 |
| 58 | $0.05 | 168452 |
| 59 | $0.05 | 171103 |
| 60 | $0.04 | 171565 |
| 61 | $0.04 | 171746 |
| 62 | $0.04 | 172402 |
| 63 | $0.04 | 173461 |
| 64 | $0.05 | 174947 |
| 65 | $0.04 | 175665 |
| 66 | $0.05 | 177023 |
| 67 | $0.04 | 177968 |
| 68 | $0.04 | 178635 |
| 69 | $0.04 | 179195 |
| 70 | $0.04 | 180060 |
| 71 | $0.04 | 181134 |
| 72 | $0.04 | 182132 |
| 73 | $0.05 | 183965 |
| 74 | $0.04 | 184730 |
| 75 | $0.04 | 185153 |
| 76 | $0.05 | 186330 |
| 77 | $0.04 | 186724 |
| 78 | $0.05 | 187899 |
| 79 | $0.05 | 189530 |
| 80 | $0.04 | 190029 |
| 81 | $0.05 | 190938 |
| 82 | $0.04 | 191329 |
| 83 | $0.04 | 192133 |
| 84 | $0.06 | 195414 |
| 85 | $0.05 | 196592 |
| 86 | $0.04 | 196938 |
| 87 | $0.04 | 197192 |
| 88 | $0.05 | 198031 |
| 89 | $0.05 | 198948 |
| 90 | $0.04 | 199332 |
| 91 | $0.04 | 199854 |
| 92 | $0.04 | 200183 |
| 93 | $0.07 | 204421 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 10 | 1 | 2 | 1081 | 0 | 30513 | 0.09 |
| red | 16 | 7 | 0 | 0 | 957 | 431 | 88 | 172 | 35953 | 2691715 | 374104 | 1.56 |
| green | 18 | 7 | 2 | 0 | 1572 | 440 | 88 | 170 | 28267 | 2430120 | 281655 | 1.46 |
| refactor | 14 | 7 | 0 | 0 | 521 | 165 | 46 | 86 | 8880 | 1076743 | 201920 | 0.70 |
| diff | 6 | 2 | 1 | 0 | 1635 | 351 | 76 | 148 | 26907 | 3360063 | 252896 | 1.63 |
| pin | 2 | 2 | 0 | 0 | 102 | 32 | 10 | 18 | 2840 | 224364 | 46130 | 0.17 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 29 | 26 | 3 | 0 | 2051 | 511 | 112 | 214 | 34053 | 2762352 | 485105 | 1.83 |
| developer | claude-sonnet-5-5 | 23 | 0 | 0 | 0 | 1826 | 685 | 147 | 288 | 51904 | 5185635 | 549386 | 2.41 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 928 | 233 | 50 | 94 | 17971 | 1835018 | 152727 | 1.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 836 | 1.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 968 | 1.07 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `tests-frozen.sh check-earlier <ledger> --step <text>` exiting 0 writes a pass marker under the run's `.tdd/` naming the step text it checked and the HEAD sha it checked at ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 129 | 29 | 58 | 9714 | 847133 | 114623 | 0.47 | 632 | unknown | 1/5 | nothing-structural |  |  | full |
| `tests-frozen.sh check-earlier` exiting 1 (an earlier step's frozen case changed) or 2 (no answer) removes any pass marker for that step, leaving markers of other steps in place ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 256 | 48 | 90 | 16167 | 1269738 | 177590 | 0.96 | 843 | 2/2 | 0/5 | nothing-left |  |  | full |
| `tests-frozen.sh check-earlier` exiting 2 (not inside a git repository, or an unreadable ledger) removes an existing pass marker for that step, leaving markers of other steps in place ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 135 | 22 | 44 | 6756 | 591547 | 89143 | 0.35 | 475 | unknown | 0/5 | nothing-left |  |  | full |
| Existing cases that launch a `verify-red` or `verify-green` leaf through `supervise.sh` with `VERI_STEP` set, and expect it to launch, first write a current check-earlier pass marker for that step at that HEAD, so they keep launching once the supervisor's guard lands (test-only, no production change) ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 180 | 35 | 68 | 11750 | 1777884 | 103913 | 0.56 | 742 | n/a | n/a | n/a |  |  | full |
| `supervise.sh verify-red …` or `supervise.sh verify-green …` with no check-earlier pass marker for the current step exits 2, its stderr naming the missing check-earlier check, writes `.tdd/<name>.exit` and launches no leaf process ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 123 | 26 | 52 | 8224 | 751928 | 98728 | 0.40 | 430 | unknown | 0/5 | structural-owed |  |  | full |
| `supervise.sh verify-red` / `verify-green` exits 2 and launches nothing when the only pass marker is for another step's text, or for the current step at a HEAD other than the current one ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 26 | 50 | 8035 | 697401 | 93295 | 0.38 | 395 | unknown | 0/5 | nothing-left |  |  | full |
| `supervise.sh verify-red` / `verify-green` launches as today when a pass marker exists for the current step at the current HEAD, and every other leaf name (develop-*, revise-*, verify-pin, verify-refactor, verdict-*) launches as today with no marker ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 12 | 22 | 5169 | 349491 | 41338 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| `supervise.sh verify-red` / `verify-green` launched with `VERI_STEP` set to the current step's ledger text (as every conductor launch sets it, not a step number) and no current pass marker for that text exits 2 and launches nothing; with a current marker for that text at HEAD it launches ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 89 | 27 | 50 | 7196 | 689561 | 91864 | 0.37 | 389 | unknown | 0/5 | nothing-left |  |  | full |
| Existing cases that launch a `verify-red` or `verify-green` leaf through `supervise.sh` with `VERI_STEP` unset or naming no ledger step, and expect it to launch, first set `VERI_STEP` to a ledger step and write a current check-earlier pass marker for it, so they keep launching once an unresolved step is refused (test-only, no production change) ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 171 | 41 | 80 | 15157 | 1582179 | 148983 | 1.07 | 1095 | 1/2 | unknown | unknown |  |  | full |
| `supervise.sh verify-red` / `verify-green` launched with `VERI_STEP` unset, or set to a step that resolves to no ledger step, exits 2 naming the missing check-earlier check and launches nothing, instead of skipping the marker gate ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 71 | 21 | 42 | 6523 | 558353 | 113618 | 0.41 | 332 | unknown | 0/5 | nothing-left |  |  | full |
| fix the full-suite failure: test_verify.py — FAILED test_verify_sh_preserves_a_rejected_or_no_verdict_attempt_under_its_ref_and_a_copy_its_verdict_event_names_and_answers_the_verdicts_reason_and_code_alone[reject-preserved] (and 18 more there); test_verify_process.py — FAILED test_verify_sh_green_rejects_a_pass_on_a_replaces_case_step_naming_each_case_its_suite_still_holds_1507; test_verdict_chain.py — FAILED test_1463_wait_leaf_returns_the_verdict_the_stub_verifier_gave_through_the_real_chain; test_run_conductor.py — FAILED test_cli_each_phases_leaf_is_launched_with_its_tier_red_and_refactor_affected_green_verify_green_and_verify_refactor_fast_and_affected: each launches a verify-red or verify-green leaf through supervise.sh with VERI_STEP unset or naming no ledger step and no current check-earlier pass marker, which supervise now refuses with exit 2 ⟦suite-repair⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 96 | 21 | 38 | 8156 | 667790 | 83610 | 0.36 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `tests-frozen.sh check-earlier <ledger> --step <text>` exiting 0 writes a pass marker under the run's `.tdd/` naming the step text it checked and the HEAD sha it checked at ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 101 | 0.11 |
| `tests-frozen.sh check-earlier` exiting 1 (an earlier step's frozen case changed) or 2 (no answer) removes any pass marker for that step, leaving markers of other steps in place ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 77 | 0.14 |
| `tests-frozen.sh check-earlier` exiting 2 (not inside a git repository, or an unreadable ledger) removes an existing pass marker for that step, leaving markers of other steps in place ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 83 | 0.09 |
| `supervise.sh verify-red …` or `supervise.sh verify-green …` with no check-earlier pass marker for the current step exits 2, its stderr naming the missing check-earlier check, writes `.tdd/<name>.exit` and launches no leaf process ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 70 | 0.10 |
| `supervise.sh verify-red` / `verify-green` exits 2 and launches nothing when the only pass marker is for another step's text, or for the current step at a HEAD other than the current one ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 72 | 0.09 |
| `supervise.sh verify-red` / `verify-green` launched with `VERI_STEP` set to the current step's ledger text (as every conductor launch sets it, not a step number) and no current pass marker for that text exits 2 and launches nothing; with a current marker for that text at HEAD it launches ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 61 | 0.09 |
| `supervise.sh verify-red` / `verify-green` launched with `VERI_STEP` unset, or set to a step that resolves to no ledger step, exits 2 naming the missing check-earlier check and launches nothing, instead of skipping the marker gate ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 57 | 0.08 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 21 | 15 | 41 | 21 | 35 | 17 | 16 | 16 | 14 | 0 | 15 | 16 | 15 | 15 | 16 | 0 | 16 | 15 | 14 | 12 | 45 | 23 | 16 | 89 | 88 | 130 | 19 | 13 | 25 | 20 | 23 | 20 | 0 | 27 | 25 | 18 | 17 | 15 | 16 | 11 | 17 | 22 | 17 | 18 | 40 | 88 | 20 | 88 | 17 | 11 | 16 | 17 | 16 |
| fast | 19 | 64 | 19 | 0 | 18 | 17 | 0 | 18 | 18 | 18 | 17 | 17 | 23 | 27 | 26 | 18 | 18 | 18 | 18 | 19 | 18 | 22 | 18 | 18 | 18 | 17 | 18 | 18 | 18 | 19 | 19 | 16 | 16 | 18 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 4 | 12 | 11 | 12 | 6 | 12 | 3 | 11 | 12 | 12 | 0 | 12 | 11 | 10 | 19 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 309 | 596 | 103928 | 9783005 | 1187218 | 5.60 |
