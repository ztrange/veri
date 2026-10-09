### 📊 Metrics — issue 1281

Wall time for the issue: 4313 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1290.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 26 | 18 | 3 | 6 | 1192 | 116617 | 42096 | 0.20 |
| red | 6 | 3 | 0 | 0 | 282 | 226 | 44 | 88 | 22597 | 2425378 | 317276 | 2.89 |
| green | 6 | 3 | 0 | 0 | 2711 | 184 | 47 | 92 | 16490 | 2358406 | 294544 | 2.53 |
| refactor | 6 | 3 | 0 | 0 | 405 | 103 | 29 | 56 | 8224 | 1272682 | 272128 | 2.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 10 | 0 | 0 | 1576 | 195 | 53 | 102 | 16856 | 2333777 | 442546 | 2.41 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 1848 | 336 | 70 | 140 | 31647 | 3839306 | 483498 | 5.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Every SKILL.md add-ledger-step.sh call that may add a step serving a criterion other than its anchor's — the over-budget split, the Green leaf's SPLIT: values, the uncovered-spec growth at verify-refactor PASS and the revise-exhausted split — passes --criterion <k> naming the criterion the added step serves, and the script's entry under The scripts documents --criterion ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 161 | 37 | 72 | 14942 | 1908273 | 302546 | 2.53 | 1073 | unknown | 0/5 | nothing-structural |  |  | full |
| The SKILL.md add-ledger-step.sh calls that keep the anchor's criterion on purpose — the ⟦suite-repair⟧ step after a red full run and the ⟦ci-repair⟧ step after a red CI check — say they pass no --criterion because the repair step serves its anchor's criterion ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 181 | 43 | 84 | 14418 | 2080742 | 280577 | 2.35 | 1070 | unknown | 0/5 | nothing-structural |  |  | full |
| SKILL.md's three split sites — the over-budget split, the Green leaf's SPLIT: values and the revise-exhausted split — pass no --criterion and say a split keeps its anchor's criterion because it is the same behaviour broken smaller; and the uncovered-spec growth on a refactor PASS passes --criterion <k>, naming the issue's numbered acceptance criteria as where k is read, adding behaviours that serve different criteria in one add-ledger-step.sh call per criterion, and bailing naming the cause when add-ledger-step.sh exits 2 because no ledger step carries k (superseding the first step's --criterion at the splits; skill-green-split.test.sh pins all of this so it fails on the text the first step left) ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 171 | 40 | 80 | 17951 | 2067451 | 300825 | 2.59 | 1585 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Every SKILL.md add-ledger-step.sh call that may add a step serving a criterion other than its anchor's — the over-budget split, the Green leaf's SPLIT: values, the uncovered-spec growth at verify-refactor PASS and the revise-exhausted split — passes --criterion <k> naming the criterion the added step serves, and the script's entry under The scripts documents --criterion ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 124 | 0.67 |
| The SKILL.md add-ledger-step.sh calls that keep the anchor's criterion on purpose — the ⟦suite-repair⟧ step after a red full run and the ⟦ci-repair⟧ step after a red CI check — say they pass no --criterion because the repair step serves its anchor's criterion ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 150 | 0.68 |
| SKILL.md's three split sites — the over-budget split, the Green leaf's SPLIT: values and the revise-exhausted split — pass no --criterion and say a split keeps its anchor's criterion because it is the same behaviour broken smaller; and the uncovered-spec growth on a refactor PASS passes --criterion <k>, naming the issue's numbered acceptance criteria as where k is read, adding behaviours that serve different criteria in one add-ledger-step.sh call per criterion, and bailing naming the cause when add-ledger-step.sh exits 2 because no ledger step carries k (superseding the first step's --criterion at the splits; skill-green-split.test.sh pins all of this so it fails on the text the first step left) ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 131 | 0.70 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 372 | 132 | 0 | 1 | 1 | 1 | 446 | 0 | 1 | 0 | 0 | 0 | 352 |
| fast | 86 | 82 | 80 | 89 | 87 | 92 | 78 | 76 | 84 |  |  |  |  |  |  |
| target | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 123 | 242 | 48503 | 6173083 | 926044 | 7.68 |
