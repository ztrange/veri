### 📊 Metrics — issue 506

Wall time for the issue: 416 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/532.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 6 | 2 | 4 | 514 | 55944 | 36258 | 0.31 |
| red | 3 | 1 | 0 | 0 | 94 | 78 | 22 | 42 | 7741 | 974344 | 131420 | 1.40 |
| green | 2 | 1 | 0 | 0 | 73 | 47 | 16 | 30 | 4809 | 647277 | 77603 | 0.85 |
| refactor | 2 | 1 | 0 | 0 | 52 | 36 | 10 | 20 | 3414 | 398207 | 79742 | 0.79 |
| pin | 1 | 1 | 0 | 0 | 29 | 21 | 5 | 10 | 2122 | 208272 | 43425 | 0.43 |

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
| Both refusal messages of lib/leaf-role.sh — the unknown-leading-word one and the no-phase one — name the conductor-* shape alongside develop-*, revise-* and verify-* ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 131 | 40 | 76 | 12914 | 1628257 | 241712 | 2.52 | 271 | unknown | 0/5 | nothing-left |  |  | full |
| A refused leaf name still makes lib/leaf-role.sh exit 2 and every accepted name (develop-*, revise-*, verify-*, conductor-*) still resolves to the same actor and phase as before ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 13 | 26 | 5172 | 599843 | 90478 | 0.95 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Both refusal messages of lib/leaf-role.sh — the unknown-leading-word one and the no-phase one — name the conductor-* shape alongside develop-*, revise-* and verify-* ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.79 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 1 | 1 | 0 | 0 | 1 | 0 |
| fast | 5 | 5 | 4 |  |  |  |  |  |
| target | 0 | 1 | 0 | 0 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 55 | 106 | 18600 | 2284044 | 368448 | 3.78 |
