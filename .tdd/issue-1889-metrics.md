### 📊 Metrics — issue 1889

Wall time for the issue: 3086 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2064.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.67 over 58 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 85661 |
| 2 | $0.02 | 85968 |
| 3 | $0.03 | 87006 |
| 4 | $0.03 | 88997 |
| 5 | $0.02 | 89300 |
| 6 | $0.02 | 89736 |
| 7 | $0.02 | 90223 |
| 8 | $0.02 | 90705 |
| 9 | $0.02 | 90962 |
| 10 | $0.02 | 91588 |
| 11 | $0.03 | 92743 |
| 12 | $0.02 | 93469 |
| 13 | $0.05 | 97071 |
| 14 | $0.07 | 103983 |
| 15 | $0.03 | 104698 |
| 16 | $0.09 | 113432 |
| 17 | $0.04 | 115030 |
| 18 | $0.04 | 117265 |
| 19 | $0.03 | 118309 |
| 20 | $0.03 | 119051 |
| 21 | $0.03 | 120221 |
| 22 | $0.04 | 121797 |
| 23 | $0.04 | 123201 |
| 24 | $0.03 | 124355 |
| 25 | $0.03 | 125140 |
| 26 | $0.03 | 126119 |
| 27 | $0.05 | 129143 |
| 28 | $0.03 | 129530 |
| 29 | $0.03 | 130406 |
| 30 | $0.03 | 131111 |
| 31 | $0.03 | 131773 |
| 32 | $0.10 | 141277 |
| 33 | $0.04 | 142312 |
| 34 | $0.03 | 142979 |
| 35 | $0.04 | 144676 |
| 36 | $0.04 | 146105 |
| 37 | $0.04 | 146831 |
| 38 | $0.04 | 147695 |
| 39 | $0.04 | 148678 |
| 40 | $0.03 | 149194 |
| 41 | $0.04 | 149861 |
| 42 | $0.04 | 151556 |
| 43 | $0.05 | 154025 |
| 44 | $0.04 | 154927 |
| 45 | $0.03 | 155222 |
| 46 | $0.04 | 155800 |
| 47 | $0.04 | 157514 |
| 48 | $0.04 | 158086 |
| 49 | $0.04 | 158904 |
| 50 | $0.05 | 160910 |
| 51 | $0.04 | 161827 |
| 52 | $0.03 | 162124 |
| 53 | $0.04 | 162950 |
| 54 | $0.04 | 163402 |
| 55 | $0.03 | 163663 |
| 56 | $0.04 | 164073 |
| 57 | $0.04 | 164413 |
| 58 | $0.04 | 164720 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 10 | 1 | 2 | 1340 | 0 | 30655 | 0.09 |
| diff | 6 | 3 | 0 | 0 | 1703 | 117 | 45 | 90 | 11291 | 1224572 | 172924 | 0.67 |
| prose | 2 | 0 | 0 | 0 | 49 | 41 | 2 | 4 | 6632 | 2217 | 140656 | 0.42 |
| red | 2 | 0 | 0 | 0 | 67 | 39 | 11 | 22 | 4587 | 346296 | 40183 | 0.18 |
| pin | 2 | 2 | 0 | 0 | 48 | 23 | 8 | 16 | 2286 | 206837 | 26341 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 181 | 62 | 19 | 38 | 6054 | 420359 | 127552 | 0.42 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 1652 | 127 | 46 | 92 | 13450 | 1357346 | 142551 | 0.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `skills/tdd/scripts/prompts/verify-plan.md` says a step whose work adds a test case for behaviour that already holds is planned as a pin step (an ordinary step whose Red reports that the case already passes, `AGAINST_UNMODIFIED: PASSES`), never as `⟦diff-checked⟧`, and that `⟦diff-checked⟧` is reserved for steps that leave no test behind; its test-only rule no longer offers `⟦diff-checked⟧` for a change that adds a case; this step adds no test ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 17 | 34 | 4728 | 470586 | 64096 | 0.25 | 498 | n/a | n/a | n/a |  |  | full |
| `skills/tdd/SKILL.md`'s *Scope & plan* says the same — a step whose work adds a test case for behaviour that already holds is a pin step, never `⟦diff-checked⟧`, and `⟦diff-checked⟧` is reserved for steps that leave no test behind (its "test-only step (`⟦diff-checked⟧` or the pin)" sentence no longer sends a case-adding step to `⟦diff-checked⟧`); the same commit re-signs `skills/tdd/GRADED` with `grade-prose.sh skills/tdd/REQUIREMENTS.md skills/tdd/SKILL.md`, so `prose-owed.sh` prints nothing and `make unit` stays green; this step adds no test ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 15 | 30 | 3578 | 434945 | 29880 | 0.15 | 281 | n/a | n/a | n/a |  |  | full |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` grades the edited `skills/tdd/SKILL.md` against its requirements list and signs it in `GRADED`, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 20 | 1 | 2 | 3252 | 1568 | 69873 | 0.21 | 41 | unknown | unknown | unknown |  |  | full |
| A case in `skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py` pins that the rendered verify-plan prompt and SKILL.md's *Scope & plan* both send a step adding a test case for behaviour that already holds to a pin step, never `⟦diff-checked⟧`, and reserve `⟦diff-checked⟧` for steps that leave no test behind; the text already holds, so this step's Red reports that the case already passes and it takes the pin route; small case, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 10 | 20 | 3601 | 286037 | 32916 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/tdd/scripts/prompts/verify-plan.md` tells the plan verifier to REJECT a plan whose `⟦diff-checked⟧` step text asks for a test to be added (a case, a pinning case, a process case), because verify-diff rejects every `⟦diff-checked⟧` step whose own commits add a test, so such a step can never pass; this step adds no test ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 13 | 26 | 2985 | 319041 | 78948 | 0.26 | 1188 | n/a | n/a | n/a |  |  | full |
| A case in `skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py` renders the verify-plan prompt over a ledger like #1667's step 3 — a `⟦diff-checked⟧` step whose text asks for a process case to be added — and pins that the prompt it hands the plan verifier carries that ledger step and the rule to REJECT a plan whose `⟦diff-checked⟧` step text asks for a test to be added; the text already holds, so this step's Red reports that the case already passes and it takes the pin route; small case, no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 9 | 18 | 3272 | 267096 | 33608 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 65 | 58 | 49 | 18 | 32 | 20 |
| affected | 41 | 7 | 7 | 868 | 4 | 3 |
| target | 2 | 2 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 67 | 134 | 26136 | 1779922 | 410759 | 1.47 |
