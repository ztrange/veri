### 📊 Metrics — issue 706

Wall time for the issue: 1408 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/744.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 16 | 2 | 4 | 1134 | 60013 | 39188 | 0.35 |
| diff | 8 | 4 | 0 | 0 | 290 | 105 | 30 | 60 | 9060 | 1181757 | 314767 | 2.94 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 5 | 5 | 0 | 0 | 233 | 65 | 16 | 32 | 5653 | 587949 | 193232 | 1.78 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 78 | 56 | 16 | 32 | 4541 | 653821 | 160723 | 1.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| In claude-md-guards-green.test.sh, the roster probe's function name and the first case's name say they check presence in `make test`'s roster, and neither contains the word "green" ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 20 | 7 | 14 | 1996 | 265242 | 75450 | 0.70 | 63 | unknown | unknown | unknown |  |  | full |
| The two planted-roster probes (the one naming each missing guard, the one on a roster naming no suite) write no guard stubs and hand the roster probe no stub directory ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 7 | 14 | 2224 | 273154 | 80072 | 0.74 | 46 | unknown | unknown | unknown |  |  | full |
| The started-child case still runs the roster probe with its failing stubs standing in as HERE, so a probe that starts a guard by `$HERE/<guard>` touches a `.started` file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 10 | 20 | 3012 | 427245 | 82396 | 0.80 | 205 | unknown | unknown | unknown |  |  | full |
| The started-child case and the header case keep their names and assertions unchanged by the branch ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 21 | 6 | 12 | 1828 | 216116 | 76849 | 0.69 | 47 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 32 | 64 | 10194 | 1241770 | 353955 | 3.28 |
