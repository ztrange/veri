### 📊 Metrics — issue 1026

Wall time for the issue: 2155 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1159.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 903 | 11992 | 31013 | 0.14 |
| red | 4 | 2 | 0 | 0 | 133 | 109 | 26 | 52 | 11038 | 1202319 | 172657 | 1.50 |
| green | 4 | 2 | 0 | 0 | 330 | 100 | 31 | 60 | 10209 | 1374805 | 171904 | 1.48 |
| refactor | 4 | 2 | 0 | 0 | 91 | 41 | 13 | 26 | 3701 | 469273 | 154594 | 1.09 |
| diff | 2 | 1 | 0 | 0 | 633 | 80 | 21 | 40 | 7753 | 990025 | 90478 | 0.89 |
| predicate | 1 | 0 | 0 | 0 | 13 | 10 | 3 | 6 | 754 | 101934 | 35651 | 0.32 |
| structural | 1 | 0 | 0 | 0 | 13 | 7 | 2 | 4 | 679 | 54694 | 35262 | 0.31 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 519 | 123 | 36 | 72 | 12691 | 1447118 | 303993 | 1.63 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 704 | 231 | 61 | 118 | 22346 | 2757924 | 387566 | 4.10 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A skill-draft-pr.test.sh case fails when the Guardrails bullet about the full suite in skills/tdd/SKILL.md contains "exactly once" or "the only full-suite gate" (the existing case that demanded those words of the Guardrails invariant no longer does), and the bullet drops both phrases ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 125 | 32 | 64 | 11943 | 1388976 | 249526 | 2.00 | 286 | unknown | 0/5 | nothing-left |  |  | full |
| A skill-draft-pr.test.sh case fails unless the Guardrails full-suite bullet names both runs at the Draft PR step: the branch's own full run (again after each suite-repair step), and the extra run on the rebased tip when sub-step 1 rebased the branch — and the bullet names both ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 125 | 38 | 74 | 13005 | 1657421 | 249629 | 2.07 | 405 | unknown | 0/5 | nothing-left |  |  | full |
| The branch's diff adds or rewrites a case in skills/tdd/scripts/tests/skill-draft-pr.test.sh that pins the Guardrails full-suite bullet's wording, and that case goes red when "the only full-suite gate" is restored to the bullet ⟦diff-checked⟧ ⟦criterion 3⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 97 | 26 | 50 | 9186 | 1146653 | 161391 | 1.52 | 661 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A skill-draft-pr.test.sh case fails when the Guardrails bullet about the full suite in skills/tdd/SKILL.md contains "exactly once" or "the only full-suite gate" (the existing case that demanded those words of the Guardrails invariant no longer does), and the bullet drops both phrases ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 44 | 0.56 |
| A skill-draft-pr.test.sh case fails unless the Guardrails full-suite bullet names both runs at the Draft PR step: the branch's own full run (again after each suite-repair step), and the extra run on the rebased tip when sub-step 1 rebased the branch — and the bullet names both ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 47 | 0.54 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 0 | 4 | 3 | 3 | 3 | 0 | 5 | 0 | 0 | 0 | 91 | 3 |
| fast | 17 | 17 | 17 | 17 | 17 | 17 | 17 |  |  |  |  |  |  |
| target | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 190 | 35037 | 4205042 | 691559 | 5.73 |
