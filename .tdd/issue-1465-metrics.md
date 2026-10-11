### 📊 Metrics — issue 1465

Wall time for the issue: 5315 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1472.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 9 | 1 | 2 | 1175 | 12193 | 41932 | 0.18 |
| red | 9 | 3 | 0 | 0 | 370 | 253 | 66 | 132 | 25416 | 3699758 | 465480 | 4.33 |
| green | 6 | 3 | 0 | 0 | 643 | 126 | 41 | 78 | 13448 | 1922764 | 273329 | 2.19 |
| refactor | 6 | 3 | 0 | 0 | 310 | 90 | 33 | 66 | 9497 | 1567659 | 270210 | 2.01 |
| pin | 3 | 3 | 0 | 0 | 80 | 31 | 10 | 20 | 3376 | 406925 | 131374 | 0.60 |
| diff | 2 | 1 | 0 | 0 | 521 | 52 | 13 | 26 | 5406 | 642838 | 95143 | 0.77 |
| rebase | 2 | 1 | 0 | 0 | 1380 | 43 | 17 | 32 | 4522 | 830207 | 98857 | 0.82 |
| predicate | 2 | 0 | 0 | 0 | 37 | 25 | 6 | 12 | 2019 | 237551 | 84003 | 0.76 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 15 | 0 | 0 | 1493 | 204 | 68 | 134 | 22118 | 3023186 | 666036 | 3.19 |
| developer | claude-opus-5-5 | 16 | 0 | 0 | 0 | 1861 | 425 | 119 | 234 | 42741 | 6296709 | 794292 | 8.47 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With VERI_MODEL_REVISE and VERI_MODEL_DEVELOPER set to different models, leaf-model.sh prints VERI_MODEL_REVISE's model for a revise-* leaf name and for develop-exhausted, and VERI_MODEL_DEVELOPER's for a develop-* first-attempt name such as develop-red ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 96 | 34 | 66 | 10609 | 1589791 | 278223 | 2.10 | 425 | unknown | 0/5 | nothing-left |  |  | full |
| With VERI_MODEL_REVISE unset, leaf-model.sh prints for revise-*, develop-exhausted and develop-* leaf names exactly the model it prints today: VERI_MODEL_DEVELOPER's, else VERI_MODEL's, else nothing ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 10 | 20 | 4748 | 494083 | 95720 | 0.76 | unknown | unknown | unknown | unknown |  |  | pin |
| VERI_MODEL_REVISE set but empty makes leaf-model.sh exit 2 for a revise-* or develop-exhausted leaf name, with a stderr line naming VERI_MODEL_REVISE and nothing on stdout ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 114 | 37 | 72 | 12465 | 1761590 | 278099 | 2.18 | 480 | unknown | 1/5 | nothing-structural |  |  | full |
| VERI_MODEL_REVISE containing whitespace makes leaf-model.sh exit 2 for a revise-* or develop-exhausted leaf name, with nothing on stdout ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 10 | 20 | 3978 | 476410 | 92546 | 0.72 | unknown | unknown | unknown | unknown |  |  | pin |
| A leaf launched through supervise.sh under a revise-* name runs with VERI_MODEL_REVISE's model, so the launch's recorded model and the claude --model flag it passes are that model ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 22 | 44 | 8011 | 1462393 | 119304 | 1.20 | unknown | unknown | unknown | unknown |  |  | pin |
| The metrics report's "Models requested" line lists VERI_MODEL_REVISE with its value, or unset, beside the other three model knobs ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 37 | 74 | 11926 | 1812839 | 276501 | 2.17 | 377 | unknown | 0/5 | nothing-left |  |  | full |
| CLAUDE.md's model-knob invariant, SKILL.md's knob list under supervise.sh, and the leaf-model.sh usage header name VERI_MODEL_REVISE and say it governs revise-* and develop-exhausted leaves, and SKILL.md's preflight step 6 also asks leaf-model.sh about a revise leaf name so a bad VERI_MODEL_REVISE stops the run before any leaf launches ⟦diff-checked⟧ ⟦criterion 2⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 120 | 36 | 70 | 11947 | 1710596 | 278003 | 2.35 | 544 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With VERI_MODEL_REVISE and VERI_MODEL_DEVELOPER set to different models, leaf-model.sh prints VERI_MODEL_REVISE's model for a revise-* leaf name and for develop-exhausted, and VERI_MODEL_DEVELOPER's for a develop-* first-attempt name such as develop-red ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 108 | 0.68 |
| VERI_MODEL_REVISE set but empty makes leaf-model.sh exit 2 for a revise-* or develop-exhausted leaf name, with a stderr line naming VERI_MODEL_REVISE and nothing on stdout ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 111 | 0.71 |
| The metrics report's "Models requested" line lists VERI_MODEL_REVISE with its value, or unset, beside the other three model knobs ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 91 | 0.62 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 3 | 3 | 0 | 2 | 0 | 0 | 1 | 1 | 0 | 1 | 80 | 2 | 2 | 2 | 1 | 18 | 19 | 1 | 1 | 1 | 2 | 2 | 1 | 272 | 1 | 2 | 3 | 3 | 1 | 2 | 48 | 1 |
| fast | 66 | 66 | 64 | 64 | 63 | 59 | 61 | 59 | 58 | 57 | 66 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 0 | 1 | 1 | 0 | 17 | 18 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 660 | 665 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 187 | 368 | 64859 | 9319895 | 1460328 | 11.66 |
