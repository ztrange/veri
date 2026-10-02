### 📊 Metrics — issue 656

Wall time for the issue: 1172 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/676.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 16 | 3 | 6 | 1458 | 106779 | 38598 | 0.36 |
| red | 2 | 0 | 0 | 0 | 117 | 92 | 16 | 30 | 9462 | 788341 | 103025 | 1.17 |
| pin | 2 | 2 | 0 | 0 | 73 | 49 | 13 | 24 | 4669 | 513627 | 78943 | 0.83 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 3 | 3 | 0 | 0 | 93 | 65 | 16 | 30 | 6127 | 620406 | 117541 | 1.19 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 117 | 92 | 16 | 30 | 9462 | 788341 | 103025 | 1.17 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| unit-tier.test.sh case 5 fails, naming itself, when tests/unit-guard/python3 is deleted: under `make unit` a fixture suite that runs real python3 must make the run fail with a line naming python3 ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 14 | 26 | 6825 | 620310 | 90334 | 0.98 | unknown | unknown | unknown | unknown |  |  | pin |
| unit-tier.test.sh case 5 fails, naming itself, when tests/offline/curl is deleted: under `make unit` a fixture suite that runs real curl must make the run fail with a line naming curl ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 76 | 15 | 28 | 7306 | 681658 | 91634 | 1.02 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 |  |
| target | 3 | 2 | 3 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 32 | 60 | 15589 | 1408747 | 220566 | 2.36 |
