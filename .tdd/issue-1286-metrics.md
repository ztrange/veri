### 📊 Metrics — issue 1286

Wall time for the issue: 1341 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1291.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 944 | 12385 | 30694 | 0.13 |
| red | 2 | 0 | 0 | 0 | 169 | 104 | 22 | 40 | 10888 | 1034046 | 100325 | 1.23 |
| pin | 2 | 2 | 0 | 0 | 74 | 42 | 13 | 26 | 4712 | 532487 | 75563 | 0.46 |
| diff | 2 | 1 | 0 | 0 | 108 | 38 | 10 | 20 | 3246 | 417686 | 79524 | 0.62 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 130 | 60 | 17 | 34 | 6609 | 648645 | 144141 | 0.77 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 230 | 131 | 29 | 54 | 13181 | 1347959 | 141965 | 1.67 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The stash-rule case in build-verify-prompt.test.sh asserts on the built prompts: every prompt built from a template that includes `_shared.md` or `_develop-shared.md` carries the git stash rule verbatim, and the case no longer reads either partial's source ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 77 | 18 | 36 | 8190 | 850353 | 87521 | 0.87 | unknown | unknown | unknown | unknown |  |  | pin |
| The `git checkout --` case in build-verify-prompt.test.sh asserts on the built prompts: every prompt built from a template that includes `_shared.md` or `_develop-shared.md` carries the sentence forbidding `git checkout -- <file>`, no built prompt names `git checkout --` outside that sentence, and no built prompt contains `git stash push` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 69 | 17 | 30 | 7410 | 716180 | 88367 | 0.81 | unknown | unknown | unknown | unknown |  |  | pin |
| Neither rewritten case reads the source of `_shared.md` or `_develop-shared.md`, or of any file under `prompts/`, so both stay green when the stash rule and the forbidding sentence move from those two partials into one partial both include ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 10 | 20 | 3246 | 417686 | 79524 | 0.62 | 133 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 2 |  |  |  |
| target | 2 | 2 | 2 | 2 | 3 | 2 | 2 |
| fast | 28 | 29 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 46 | 88 | 19790 | 1996604 | 286106 | 2.44 |
