### 📊 Metrics — issue 2119

Wall time for the issue: 983 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2140.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 8 | 1 | 2 | 880 | 17051 | 13148 | 0.04 |
| red | 5 | 2 | 0 | 0 | 93 | 68 | 19 | 32 | 7467 | 438056 | 85985 | 0.33 |
| green | 6 | 2 | 1 | 0 | 164 | 89 | 26 | 46 | 6970 | 617887 | 91780 | 0.48 |
| refactor | 4 | 2 | 0 | 0 | 54 | 31 | 13 | 20 | 2712 | 243475 | 59223 | 0.20 |
| pin | 1 | 1 | 0 | 0 | 17 | 14 | 3 | 6 | 794 | 74342 | 13024 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 8 | 1 | 0 | 161 | 91 | 26 | 48 | 7846 | 601738 | 114719 | 0.43 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 125 | 91 | 24 | 38 | 8065 | 517010 | 99702 | 0.38 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 51 | 28 | 12 | 20 | 2912 | 272063 | 48739 | 0.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 106 | 0.37 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A stale unit named bare (no backticks) on an unchecked ⟦skill-edit⟧ ledger line is waived: prose-owed.sh exits 0 on a repo whose only stale unit is named bare by the run's ledger ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 102 | 33 | 52 | 8763 | 683042 | 127090 | 0.60 | 289 | 1/2 | 0/5 | nothing-left |  |  | full |
| A stale unit named in backticks on an unchecked ⟦skill-edit⟧ ledger line is still waived: prose-owed.sh exits 0, pinned through its exit code ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 6 | 12 | 2830 | 155361 | 29989 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| A ⟦skill-edit⟧ line naming the stale unit's path only inside a longer path (the unit path with a suffix such as .bak, or with a leading directory such as x/) does not waive it: prose-owed.sh still exits non-zero ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 71 | 22 | 40 | 6350 | 535357 | 92933 | 0.35 | 186 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A stale unit named bare (no backticks) on an unchecked ⟦skill-edit⟧ ledger line is waived: prose-owed.sh exits 0 on a repo whose only stale unit is named bare by the run's ledger ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 28 | 0.10 |
| A ⟦skill-edit⟧ line naming the stale unit's path only inside a longer path (the unit path with a suffix such as .bak, or with a leading directory such as x/) does not waive it: prose-owed.sh still exits non-zero ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 26 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 3 | 3 | 3 | 3 | 1 | 1 | 3 | 3 | 3 | 2 | 3 |
| fast | 5 | 5 | 5 | 5 | 4 | 5 | 4 | 5 |  |  |  |  |  |
| target | 3 | 3 | 1 | 1 | 3 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 62 | 106 | 18823 | 1390811 | 263160 | 1.11 |
