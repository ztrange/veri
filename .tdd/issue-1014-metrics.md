### 📊 Metrics — issue 1014

Wall time for the issue: 2867 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1038.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 749 | 11866 | 29587 | 0.13 |
| red | 4 | 2 | 0 | 0 | 185 | 170 | 26 | 52 | 17440 | 1247006 | 189082 | 1.76 |
| green | 4 | 2 | 0 | 0 | 512 | 235 | 47 | 92 | 23587 | 2341111 | 191817 | 2.08 |
| refactor | 4 | 2 | 0 | 0 | 179 | 128 | 31 | 62 | 13222 | 1547898 | 180342 | 1.64 |
| diff | 2 | 1 | 0 | 0 | 266 | 101 | 23 | 44 | 10282 | 1103136 | 98843 | 0.95 |
| predicate | 3 | 0 | 0 | 0 | 78 | 70 | 16 | 32 | 6653 | 645637 | 113337 | 1.17 |
| structural | 3 | 0 | 0 | 0 | 276 | 163 | 34 | 68 | 15618 | 1653320 | 133273 | 1.71 |
| transform | 1 | 1 | 0 | 0 | 32 | 23 | 9 | 16 | 2231 | 339771 | 38010 | 0.24 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 9 | 0 | 0 | 441 | 205 | 60 | 118 | 23422 | 2575503 | 361436 | 2.20 |
| developer | claude-opus-5-5 | 13 | 0 | 0 | 0 | 1096 | 692 | 127 | 250 | 66360 | 6314242 | 612855 | 7.49 |

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
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| No partial under the prompt templates starts mid-sentence: every `_*.md` partial in `skills/tdd/scripts/prompts/` opens at the start of a sentence, a heading, a list item or a code block, never inside a clause that a template's text before the `{{INCLUDE:…}}` began, and the prompts that include it render the same text ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 335 | 59 | 118 | 34044 | 3067578 | 298963 | 3.09 | 670 | unknown | 1/5 | structural-owed |  |  | full |
| No partial under the prompt templates ends mid-sentence: every `_*.md` partial in `skills/tdd/scripts/prompts/` closes at the end of a sentence, a heading, a list item or a code block, never inside a clause that a template's text after the `{{INCLUDE:…}}` finishes, and the prompts that include it render the same text ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 45 | 88 | 20205 | 2068437 | 262278 | 2.40 | 379 | unknown | 0/5 | nothing-left |  |  | full |
| Every prompt builder renders the same text as before the branch: byte-identical, or different only in whitespace from rewrapping, across the same builder runs #703 used ⟦diff-checked⟧ ⟦criterion 2⟧ | 9 | 2 | 0 | 0 | 0 | 0 | 357 | 82 | 160 | 34784 | 3741864 | 383463 | 4.07 | 292 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| No partial under the prompt templates starts mid-sentence: every `_*.md` partial in `skills/tdd/scripts/prompts/` opens at the start of a sentence, a heading, a list item or a code block, never inside a clause that a template's text before the `{{INCLUDE:…}}` began, and the prompts that include it render the same text ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 135 | 1.09 |
| No partial under the prompt templates ends mid-sentence: every `_*.md` partial in `skills/tdd/scripts/prompts/` closes at the end of a sentence, a heading, a list item or a code block, never inside a clause that a template's text after the `{{INCLUDE:…}}` finishes, and the prompts that include it render the same text ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 44 | 0.55 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 64 | 74 | 0 | 3 | 0 | 0 | 3 | 3 | 0 | 0 | 2 | 0 | 2 | 3 | 0 | 4 | 3 | 2 | 1 | 0 | 1 | 4 | 1 | 0 | 50 | 1 | 0 | 0 | 3 | 0 | 2 | 0 | 1 | 75 | 5 | 4 | 6 | 0 | 0 | 0 | 2 | 3 | 0 |
| fast | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 187 | 368 | 89782 | 8889745 | 974291 | 9.69 |
