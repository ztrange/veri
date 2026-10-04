### 📊 Metrics — issue 875

Wall time for the issue: 2726 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/876.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 11 | 2 | 4 | 1300 | 41767 | 47042 | 0.21 |
| red | 6 | 3 | 0 | 0 | 221 | 197 | 49 | 94 | 18044 | 2478800 | 287938 | 2.65 |
| green | 8 | 3 | 1 | 0 | 769 | 264 | 67 | 134 | 24729 | 3368023 | 371665 | 3.43 |
| refactor | 6 | 3 | 0 | 0 | 153 | 62 | 21 | 42 | 4819 | 758949 | 229767 | 1.62 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 10 | 1 | 0 | 591 | 156 | 49 | 98 | 16362 | 1907754 | 432483 | 2.28 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 565 | 378 | 90 | 176 | 32530 | 4739785 | 503929 | 5.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 286 | 1.82 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| build-verify-prompt.sh diff takes the step's own base sha after the branch point (`diff <spec> <branch-base-sha> <step-base-sha>`) and its prompt judges the criterion against `git diff <branch-base-sha>..HEAD` while the "adds no test" REJECT applies only to a test added in `git diff <step-base-sha>..HEAD`, so a test an earlier Red/Green step added is not a ground to REJECT | 6 | 3 | 0 | 0 | 0 | 0 | 138 | 34 | 66 | 13136 | 1547708 | 259660 | 2.15 | 318 | unknown | 0/5 | nothing-left |  |  | full |
| build-verify-prompt.sh diff refuses with exit 2 and no stdout when the step base sha is missing or is not 7-40 lowercase hex characters | 8 | 3 | 1 | 0 | 0 | 0 | 214 | 56 | 110 | 19220 | 2855495 | 376024 | 3.28 | 490 | 1/2 | 0/5 | nothing-left |  |  | full |
| SKILL.md's ⟦diff-checked⟧ section records the step's base sha (`git rev-parse HEAD` before the develop-diff leaf runs) and passes it to the blind diff verifier after the branch point, `run-verdict.sh --step "<STEP>" diff <spec-file> <branch-base-sha> <step-base-sha>` | 6 | 3 | 0 | 0 | 0 | 0 | 171 | 47 | 94 | 15236 | 2202569 | 253686 | 2.26 | 505 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| build-verify-prompt.sh diff takes the step's own base sha after the branch point (`diff <spec> <branch-base-sha> <step-base-sha>`) and its prompt judges the criterion against `git diff <branch-base-sha>..HEAD` while the "adds no test" REJECT applies only to a test added in `git diff <step-base-sha>..HEAD`, so a test an earlier Red/Green step added is not a ground to REJECT | 1 | 0/5 | nothing-left | PASS | 0 | 37 | 0.52 |
| build-verify-prompt.sh diff refuses with exit 2 and no stdout when the step base sha is missing or is not 7-40 lowercase hex characters | 1 | 0/5 | nothing-left | PASS | 0 | 77 | 0.56 |
| SKILL.md's ⟦diff-checked⟧ section records the step's base sha (`git rev-parse HEAD` before the develop-diff leaf runs) and passes it to the blind diff verifier after the branch point, `run-verdict.sh --step "<STEP>" diff <spec-file> <branch-base-sha> <step-base-sha>` | 1 | 0/5 | nothing-left | PASS | 0 | 39 | 0.54 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 1 | 2 | 2 | 38 | 37 | 0 | 0 | 71 |
| fast | 13 | 14 | 13 | 13 | 12 | 13 | 13 | 12 | 13 |  |
| target | 2 | 2 | 2 | 1 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 139 | 274 | 48892 | 6647539 | 936412 | 7.91 |
