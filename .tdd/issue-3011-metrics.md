### 📊 Metrics — issue 3011

Wall time for the issue: 22563 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 8 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.50 over 59 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89848 tokens, largest 139214 tokens
Conductor context: first turn 89814 tokens, largest 117852 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 89848 |
| 2 | $0.08 | 96995 |
| 3 | $0.04 | 99938 |
| 4 | $0.03 | 101514 |
| 5 | $0.03 | 103014 |
| 6 | $0.03 | 103633 |
| 7 | $0.02 | 104027 |
| 8 | $0.02 | 104327 |
| 9 | $0.02 | 104714 |
| 10 | $0.02 | 105016 |
| 11 | $0.02 | 105348 |
| 12 | $0.02 | 105829 |
| 13 | $0.02 | 106228 |
| 14 | $0.02 | 106467 |
| 15 | $0.03 | 107410 |
| 16 | $0.03 | 108437 |
| 17 | $0.05 | 111659 |
| 18 | $0.05 | 114701 |
| 19 | $0.03 | 115137 |
| 20 | $0.04 | 116770 |
| 21 | $0.03 | 118224 |
| 22 | $0.03 | 118618 |
| 23 | $0.03 | 119664 |
| 24 | $0.03 | 120215 |
| 25 | $0.03 | 120627 |
| 26 | $0.03 | 121264 |
| 27 | $0.03 | 122060 |
| 28 | $0.04 | 123496 |
| 29 | $0.03 | 124239 |
| 30 | $0.03 | 124616 |
| 31 | $0.03 | 125141 |
| 32 | $0.03 | 125971 |
| 33 | $0.03 | 126818 |
| 34 | $0.03 | 127653 |
| 35 | $0.05 | 130239 |
| 36 | $0.03 | 131013 |
| 37 | $0.03 | 131343 |
| 38 | $0.03 | 131673 |
| 39 | $0.04 | 133083 |
| 40 | $0.03 | 133447 |
| 41 | $0.05 | 136016 |
| 42 | $0.03 | 136729 |
| 43 | $0.03 | 137072 |
| 44 | $0.03 | 137740 |
| 45 | $0.03 | 138551 |
| 46 | $0.03 | 138839 |
| 47 | $0.03 | 139214 |
| 48 | unpriced | 0 |
| 49 | $0.58 | 89814 |
| 50 | $0.07 | 96764 |
| 51 | $0.04 | 99640 |
| 52 | $0.03 | 101463 |
| 53 | $0.04 | 103790 |
| 54 | $0.05 | 107719 |
| 55 | $0.03 | 108214 |
| 56 | $0.05 | 111410 |
| 57 | $0.02 | 111724 |
| 58 | $0.03 | 113252 |
| 59 | $0.06 | 117852 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 7 | 1 | 2 | 942 | 0 | 33497 | 0.09 |
| prose | 13 | 0 | 0 | 0 | 122 | 74 | 13 | 26 | 8772 | 34287 | 87998 | 0.31 |
| skill-edit | 3 | 0 | 0 | 0 | 48 | 37 | 11 | 18 | 1950 | 194755 | 46380 | 0.15 |
| diff | 2 | 1 | 0 | 0 | 3485 | 112 | 23 | 46 | 6401 | 628353 | 158718 | 0.52 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 531 | 56 | 8 | 16 | 3124 | 205568 | 71701 | 0.23 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 2965 | 63 | 16 | 32 | 4219 | 422785 | 120514 | 0.39 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| develop-contract-b.md's opening paragraph says the old interface is deleted, its proxy after expand and the old interface itself after beside, never "the old interface's proxy is deleted" unconditionally, with rows CB1, CB3 and CB6 reworded to match, in skills/tdd/scripts/prompts/develop-contract-b.md ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 30 | 8 | 14 | 3352 | 65990 | 51853 | 0.17 | 85 | unknown | unknown | unknown |  |  | full |
| develop-contract-b.md's step 1 tells the leaf to delete the proxy after expand and the interface itself after beside, and row CB6 calls list item 1 "delete the old interface", in skills/tdd/scripts/prompts/develop-contract-b.md ⟦skill-edit⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 5 | 1 | 2 | 521 | 1516 | 7936 | 0.03 | 31 | unknown | unknown | unknown |  |  | full |
| verify-contract-b.md's opening, check 2 ("The old interface is deleted") and closing paragraph state the deletion for both shapes, so a beside-shape contract-b passes with no proxy ever existing, with rows VK2, VK3 and VK6 reworded to match, in skills/tdd/scripts/prompts/verify-contract-b.md ⟦skill-edit⟧ ⟦criterion 3⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 43 | 8 | 14 | 3896 | 84721 | 33394 | 0.13 | 89 | unknown | unknown | unknown |  |  | full |
| develop-contract-a.md's step 1 says the old interface stays because deleting it (its proxy, after expand) is contract-b, with rows CA2 and CA3 reworded to match, in skills/tdd/scripts/prompts/develop-contract-a.md ⟦skill-edit⟧ ⟦criterion 4⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 21 | 5 | 10 | 1623 | 73783 | 25283 | 0.09 | 55 | unknown | unknown | unknown |  |  | full |
| Row VA3's Why says a test still on the old interface keeps the old interface alive, not the proxy, in skills/tdd/scripts/prompts/verify-contract-a.md ⟦skill-edit⟧ ⟦criterion 4⟧ | 2 | 0 | 0 | 0 | 0 | 0 | 12 | 2 | 4 | 1330 | 3032 | 15912 | 0.05 | 31 | unknown | unknown | unknown |  |  | full |
| Every change to the five prompts and their rows landed through the skill-edit steps above, each unit signed by a grader PASS, and no other step edited them ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 112 | 23 | 46 | 6401 | 628353 | 158718 | 0.52 | 4302 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 65 | 137 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 1054 | 1339 | 331 | 41 | 58 | 291 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 14 | 12 | 12 | 13 | 15 | 16 | 23 | 17 | 18 | 11 | 11 | 16 | 12 | 10 | 13 | 12 | 13 | 11 | 10 | 9 | 11 | 14 | 11 | 12 | 10 | 13 | 14 | 15 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 48 | 92 | 18065 | 857395 | 326593 | 4.59 (estimate) |
