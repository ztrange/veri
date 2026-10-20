### 📊 Metrics — issue 1878

Wall time for the issue: 1909 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1910.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 716 | 17463 | 12445 | 0.04 |
| red | 7 | 3 | 0 | 0 | 259 | 158 | 34 | 68 | 12062 | 1005618 | 148048 | 0.71 |
| green | 8 | 3 | 1 | 0 | 477 | 125 | 40 | 74 | 9724 | 1036088 | 103012 | 0.52 |
| refactor | 6 | 3 | 0 | 0 | 139 | 55 | 17 | 34 | 3690 | 432298 | 77861 | 0.27 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 10 | 1 | 0 | 431 | 133 | 36 | 72 | 10317 | 945336 | 139975 | 0.55 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 216 | 108 | 30 | 58 | 7911 | 828720 | 109048 | 0.43 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 236 | 103 | 26 | 48 | 7964 | 717411 | 92343 | 0.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 307 | 0.29 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When the `git diff` that `save_diff` runs exits non-zero (forced through git config: `diff.orderFile` naming a missing file), the refusal prints "diff could not be saved to .tdd/<leaf>.diff", writes no diff file, and still exits 2 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 94 | 25 | 50 | 6703 | 689626 | 88019 | 0.36 | 322 | unknown | 1/5 | nothing-structural |  |  | full |
| A `.tdd/<leaf>.diff` left by an earlier refusal is removed when a later refusal's diff could not be saved, so no file under `.tdd/` claims to be that refusal's evidence ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 73 | 23 | 44 | 5760 | 608883 | 90486 | 0.34 | 239 | unknown | 0/5 | nothing-left |  |  | full |
| The saved diff ignores the user's prefix, context and abbreviation config: with `diff.noprefix=true`, `diff.context=0` and `core.abbrev=4` set, the refusal's saved `.tdd/<leaf>.diff` passes `git apply --check` (save_diff passes explicit `--src-prefix=a/ --dst-prefix=b/ -U3 --full-index` or equivalent) ⟦criterion 3⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 171 | 43 | 82 | 13013 | 1175495 | 150416 | 0.80 | 582 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When the `git diff` that `save_diff` runs exits non-zero (forced through git config: `diff.orderFile` naming a missing file), the refusal prints "diff could not be saved to .tdd/<leaf>.diff", writes no diff file, and still exits 2 ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 58 | 0.10 |
| A `.tdd/<leaf>.diff` left by an earlier refusal is removed when a later refusal's diff could not be saved, so no file under `.tdd/` claims to be that refusal's evidence ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 40 | 0.09 |
| The saved diff ignores the user's prefix, context and abbreviation config: with `diff.noprefix=true`, `diff.context=0` and `core.abbrev=4` set, the refusal's saved `.tdd/<leaf>.diff` passes `git apply --check` (save_diff passes explicit `--src-prefix=a/ --dst-prefix=b/ -U3 --full-index` or equivalent) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 41 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 15 | 14 | 14 | 13 | 14 | 15 | 14 | 13 | 12 | 14 | 14 | 1 | 14 | 13 | 13 | 13 | 13 |
| fast | 6 | 6 | 6 | 5 | 5 | 5 | 6 | 5 | 6 | 5 | 6 |  |  |  |  |  |  |
| target | 1 | 1 | 15 | 13 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 92 | 178 | 26192 | 2491467 | 341366 | 1.54 |
