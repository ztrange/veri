### 📊 Metrics — issue 1281

Wall time for the issue: 5069 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1290.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 26 | 18 | 3 | 6 | 1192 | 116617 | 42096 | 0.20 |
| red | 4 | 2 | 0 | 0 | 176 | 138 | 27 | 54 | 13300 | 1501404 | 210687 | 1.87 |
| green | 4 | 2 | 0 | 0 | 1488 | 131 | 32 | 62 | 10801 | 1576903 | 192439 | 1.66 |
| refactor | 4 | 2 | 0 | 0 | 274 | 73 | 21 | 40 | 5259 | 910708 | 179997 | 1.35 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 703 | 147 | 37 | 70 | 12060 | 1588747 | 307933 | 1.67 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 1261 | 213 | 46 | 92 | 18492 | 2516885 | 317286 | 3.41 |

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

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Every SKILL.md add-ledger-step.sh call that may add a step serving a criterion other than its anchor's — the over-budget split, the Green leaf's SPLIT: values, the uncovered-spec growth at verify-refactor PASS and the revise-exhausted split — passes --criterion <k> naming the criterion the added step serves, and the script's entry under The scripts documents --criterion ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 124 | 0.67 |
| The SKILL.md add-ledger-step.sh calls that keep the anchor's criterion on purpose — the ⟦suite-repair⟧ step after a red full run and the ⟦ci-repair⟧ step after a red CI check — say they pass no --criterion because the repair step serves its anchor's criterion ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 150 | 0.68 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 372 | 132 | 0 | 1 | 1 | 1 | 446 | 0 |
| fast | 86 | 82 | 80 | 89 | 87 | 92 |  |  |  |  |
| target | 1 | 1 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 83 | 162 | 30552 | 4105632 | 625219 | 5.08 |
