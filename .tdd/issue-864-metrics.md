### 📊 Metrics — issue 864

Wall time for the issue: 3377 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/883.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 12 | 2 | 4 | 1164 | 63107 | 42168 | 0.37 |
| red | 4 | 2 | 0 | 0 | 201 | 169 | 37 | 72 | 14895 | 2086211 | 218671 | 2.46 |
| green | 4 | 2 | 0 | 0 | 890 | 153 | 37 | 74 | 12917 | 1863441 | 186346 | 2.12 |
| refactor | 4 | 2 | 0 | 0 | 435 | 75 | 21 | 42 | 7631 | 972540 | 181215 | 1.80 |
| diff | 4 | 2 | 0 | 0 | 247 | 58 | 16 | 32 | 5981 | 671628 | 168688 | 1.60 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 9 | 9 | 0 | 0 | 993 | 212 | 52 | 104 | 20816 | 2414579 | 400544 | 4.10 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 797 | 255 | 61 | 120 | 21772 | 3242348 | 396544 | 4.26 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| SKILL.md preflight step 0.2 names `gh api user` as the GitHub check, and says a non-zero exit from it stops the run as a preflight failure ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 190 | 46 | 92 | 16376 | 2364839 | 292654 | 3.14 | 1182 | unknown | 0/5 | nothing-left |  |  | full |
| a suite fails naming `<file>:<line>` when a `gh auth status` call is planted in skills/tdd/SKILL.md or in a skills/tdd/scripts/*.sh, and passes on a tree holding none ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 207 | 49 | 96 | 19067 | 2557353 | 293578 | 3.24 | 505 | unknown | 1/5 | nothing-left |  |  | full |
| the `claude auth status` half of step 0.2 and the `leaf-launchable.sh` check that follows it are unchanged on this branch ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 7 | 14 | 2580 | 278596 | 82510 | 0.77 | 59 | unknown | unknown | unknown |  |  | full |
| no assertion of an existing SKILL.md prose suite or of `no-graphql-gh-calls.test.sh` is changed on this branch ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 3401 | 393032 | 86178 | 0.84 | 232 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md preflight step 0.2 names `gh api user` as the GitHub check, and says a non-zero exit from it stops the run as a preflight failure ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 321 | 0.88 |
| a suite fails naming `<file>:<line>` when a `gh auth status` call is planted in skills/tdd/SKILL.md or in a skills/tdd/scripts/*.sh, and passes on a tree holding none ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 114 | 0.92 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 201 | 0 | 270 | 212 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 82 |
| fast | 57 | 56 | 59 | 61 | 57 | 58 |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 113 | 224 | 42588 | 5656927 | 797088 | 8.36 |
