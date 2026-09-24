### 📊 Metrics — issue 271

Wall time for the issue: unknown s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 20 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 50 | 41 | 5 | 10 | 4232 | 161383 | 76726 | 0.73 |
| red | 9 | 4 | 0 | 0 | 310 | 258 | 60 | 120 | 24751 | 2672069 | 372862 | 4.01 |
| green | 14 | 3 | 4 | 0 | 1610 | 469 | 110 | 220 | 45234 | 5115897 | 529143 | 6.16 |
| refactor | 6 | 3 | 0 | 0 | 238 | 127 | 33 | 66 | 12089 | 1381401 | 238233 | 2.42 |
| pin | 1 | 1 | 0 | 0 | 22 | 15 | 3 | 6 | 1427 | 102088 | 36860 | 0.34 |
| exhausted | 1 | 0 | 0 | 0 | 32 | 29 | 6 | 12 | 2611 | 265678 | 47412 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 70 | 0.93 |
| green | 442 | 1.72 | 880 | 2.49 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 32 | 0.48 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `workqueue.sh assign <worker> <issue>...` appends one `<worker>	<issue>	queued	` line per issue to `.tdd/workqueue`, in the order given ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 186 | 43 | 86 | 18188 | 1948941 | 256183 | 2.80 | 479 | unknown | 0/5 | nothing-left |
| `workqueue.sh <unknown-subcommand> …` (e.g. `workqueue.sh frobnicate alpha 12`) exits 2 and leaves `.tdd/workqueue` byte-identical (absent if it was absent) ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 141 | 39 | 78 | 13555 | 1665127 | 234585 | 2.48 | 235 | unknown | 0/5 | structural-owed |
| `workqueue.sh frobnicate alpha 12` in a repo with no `.tdd/workqueue` exits 2 and leaves `.tdd/workqueue` absent ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 12 | 24 | 4628 | 507815 | 77523 | 0.81 | unknown | unknown | unknown | unknown |
| `workqueue.sh assign` refuses with exit 2, leaving the file byte-identical, an issue already `queued` or `running` for any worker ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 216 | 51 | 102 | 20468 | 2202883 | 320915 | 3.42 | 634 | 1/2 | 1/5 | nothing-structural |
| `workqueue.sh next <worker>` prints that worker's first `queued` issue whose `## Blocked by` names no open issue, skipping a blocked one, read from `VERI_GH_JSON` fixtures ⟦criterion 2⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 308 | 67 | 134 | 29273 | 3212367 | 335304 | 3.91 | unknown | 2/2 | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 1 | 0 | 106 | 0 | 65 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| fast | 2 | 3 | 3 | 2 | 3 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 292 | 296 | 297 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 217 | 434 | 90344 | 9698516 | 1301236 | 14.16 |
