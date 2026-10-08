### 📊 Metrics — issue 873

Wall time for the issue: 1289 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1196.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 960 | 12385 | 31283 | 0.14 |
| red | 4 | 1 | 0 | 0 | 169 | 143 | 33 | 62 | 14429 | 1713606 | 208572 | 2.13 |
| green | 2 | 1 | 0 | 0 | 106 | 40 | 13 | 26 | 3770 | 571594 | 80050 | 0.66 |
| refactor | 2 | 1 | 0 | 0 | 55 | 24 | 8 | 16 | 2132 | 311467 | 77011 | 0.55 |
| pin | 2 | 2 | 0 | 0 | 46 | 32 | 13 | 26 | 3524 | 559594 | 77945 | 0.46 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 171 | 87 | 29 | 58 | 9208 | 1187379 | 224308 | 1.23 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 216 | 160 | 39 | 74 | 15607 | 1981267 | 250553 | 2.71 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Under a leaf launched by run-leaf.sh, a Python module mutated and reverted at the same whole-second mtime and the same byte size is re-read from source on its next import: the reverted module answers as it did before the mutation ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 125 | 34 | 66 | 12127 | 1451959 | 246479 | 2.00 | 311 | unknown | 0/5 | nothing-left |  |  | full |
| run-leaf.sh hands the leaf PYTHONDONTWRITEBYTECODE=1 whatever its own environment carries: unset, set to 0, or set to the empty string ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 18 | 34 | 6037 | 911218 | 99200 | 0.92 | unknown | unknown | unknown | unknown |  |  | pin |
| A Python process started under a leaf launched by run-leaf.sh writes no .pyc file into the directory tree it imports from ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 15 | 30 | 5691 | 793084 | 97899 | 0.88 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Under a leaf launched by run-leaf.sh, a Python module mutated and reverted at the same whole-second mtime and the same byte size is re-read from source on its next import: the reverted module answers as it did before the mutation ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 55 | 0.55 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 2 | 3 | 0 | 1 | 2 | 2 |
| fast | 24 | 24 | 23 |  |  |  |  |  |
| target | 1 | 1 | 2 | 0 | 2 | 1 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 68 | 132 | 24815 | 3168646 | 474861 | 3.94 |
