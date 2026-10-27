### 📊 Metrics — issue 2553

Wall time for the issue: 3176 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2567.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.47 over 76 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89065 tokens, largest 182172 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89065 |
| 2 | $0.02 | 89372 |
| 3 | $0.04 | 92148 |
| 4 | $0.03 | 94060 |
| 5 | $0.02 | 94380 |
| 6 | $0.02 | 94745 |
| 7 | $0.02 | 95448 |
| 8 | $0.02 | 95989 |
| 9 | $0.02 | 96608 |
| 10 | $0.02 | 96925 |
| 11 | $0.03 | 98523 |
| 12 | $0.03 | 100030 |
| 13 | $0.03 | 101773 |
| 14 | $0.04 | 104137 |
| 15 | $0.04 | 105951 |
| 16 | $0.05 | 109879 |
| 17 | $0.03 | 111502 |
| 18 | $0.03 | 112510 |
| 19 | $0.08 | 120274 |
| 20 | $0.04 | 122199 |
| 21 | $0.04 | 123825 |
| 22 | $0.03 | 124727 |
| 23 | $0.04 | 126052 |
| 24 | $0.03 | 126454 |
| 25 | $0.03 | 127036 |
| 26 | $0.03 | 128104 |
| 27 | $0.03 | 128771 |
| 28 | $0.03 | 129616 |
| 29 | $0.10 | 138845 |
| 30 | $0.04 | 139849 |
| 31 | $0.03 | 140533 |
| 32 | $0.03 | 141107 |
| 33 | $0.03 | 141903 |
| 34 | $0.03 | 142664 |
| 35 | $0.05 | 145079 |
| 36 | $0.04 | 146023 |
| 37 | $0.03 | 146344 |
| 38 | $0.03 | 146803 |
| 39 | $0.04 | 147511 |
| 40 | $0.04 | 148612 |
| 41 | $0.04 | 149400 |
| 42 | $0.04 | 150426 |
| 43 | $0.04 | 152032 |
| 44 | $0.03 | 152529 |
| 45 | $0.04 | 153196 |
| 46 | $0.04 | 154076 |
| 47 | $0.04 | 155398 |
| 48 | $0.07 | 159882 |
| 49 | $0.04 | 161386 |
| 50 | $0.04 | 162356 |
| 51 | $0.04 | 162781 |
| 52 | $0.04 | 163545 |
| 53 | $0.04 | 164350 |
| 54 | $0.04 | 165067 |
| 55 | $0.04 | 166144 |
| 56 | $0.04 | 167099 |
| 57 | $0.04 | 167719 |
| 58 | $0.04 | 168639 |
| 59 | $0.04 | 169241 |
| 60 | $0.04 | 170161 |
| 61 | $0.04 | 171243 |
| 62 | $0.04 | 172191 |
| 63 | $0.04 | 172699 |
| 64 | $0.04 | 173402 |
| 65 | $0.04 | 174346 |
| 66 | $0.04 | 175245 |
| 67 | $0.04 | 175944 |
| 68 | $0.04 | 176457 |
| 69 | $0.04 | 177170 |
| 70 | $0.05 | 178433 |
| 71 | $0.04 | 179317 |
| 72 | $0.04 | 179712 |
| 73 | $0.04 | 180591 |
| 74 | $0.04 | 181093 |
| 75 | $0.04 | 181854 |
| 76 | $0.04 | 182172 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 27 | 24 | 2 | 4 | 1659 | 34821 | 36257 | 0.11 |
| diff | 7 | 3 | 0 | 0 | 918 | 193 | 50 | 98 | 12423 | 1631185 | 177099 | 0.73 |
| red | 1 | 0 | 0 | 0 | 30 | 23 | 5 | 10 | 2221 | 171460 | 24259 | 0.10 |
| pin | 1 | 1 | 0 | 0 | 20 | 15 | 3 | 6 | 738 | 82318 | 16538 | 0.06 |
| prose | 5 | 0 | 0 | 0 | 585 | 575 | 5 | 10 | 89828 | 5037 | 537331 | 2.24 |
| skill-edit | 2 | 0 | 0 | 0 | 38 | 34 | 9 | 18 | 3192 | 920950 | 221539 | 0.68 |
| rebase | 2 | 1 | 0 | 0 | 238 | 34 | 12 | 24 | 3092 | 361791 | 62289 | 0.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 559 | 120 | 23 | 46 | 8182 | 626704 | 173449 | 0.58 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 674 | 169 | 49 | 96 | 11951 | 1654871 | 142993 | 0.64 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skills/tdd/scripts/prompts/verify-plan.md gains one REJECT rule: a plan whose step text names more than one observable outcome (a behaviour plus each distinct refusal, exit code or fail-closed branch) is refused, the reason naming the step and the split it needs, one outcome per step; a step naming exactly one outcome (a behaviour alone, or one guard alone) is still accepted, the rule keyed on the count of named outcomes and never on the mere presence of a guard; no other prompt text changes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 83 | 21 | 40 | 5007 | 681743 | 58420 | 0.26 | 211 | n/a | n/a | n/a |  |  | full |
| the rendered plan-verifier prompt (build-verify-prompt.sh plan) refuses a step naming more than one observable outcome, naming the one-outcome-per-step split, and states that a step naming exactly one outcome is accepted and that a guard's mere presence is no ground to refuse, pinned by a small case in skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 8 | 16 | 2959 | 253778 | 40797 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| the Red phase's instructions agree with the split rule: the branch leaves the one-case rule in skills/tdd/scripts/prompts/_develop-red-lead.md and _develop-red-cases.md as it stands and adds no instruction under skills/tdd/scripts/prompts/ telling a Red leaf to add a second case or to leave a guard its step names unpinned ⟦diff-checked⟧ ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 71 | 20 | 40 | 5192 | 688441 | 86601 | 0.34 | 305 | n/a | n/a | n/a |  |  | full |
| verify-green's demand is unchanged: the branch leaves skills/tdd/scripts/prompts/verify-green.md's rejection of a guard that survives deletion with every suite green, and the existing cases pinning it, unchanged ⟦diff-checked⟧ ⟦criterion 3⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 73 | 21 | 42 | 5316 | 622792 | 94367 | 0.35 | 305 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 17 | 18 | 16 | 16 | 16 | 17 | 17 | 17 | 17 |
| affected | 4 | 4 | 4 | 169 | 0 | 182 | 176 | 2 |  |
| target | 1 | 1 |  |  |  |  |  |  |  |
| all | 17 | 182 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 86 | 170 | 113153 | 3207562 | 1075312 | 7.61 (estimate) |
