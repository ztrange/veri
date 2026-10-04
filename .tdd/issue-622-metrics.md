### 📊 Metrics — issue 622

Wall time for the issue: 1938 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/853.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 18 | 3 | 6 | 1682 | 112747 | 41313 | 0.39 |
| red | 3 | 1 | 0 | 0 | 149 | 127 | 27 | 54 | 10808 | 1445825 | 144494 | 1.66 |
| green | 2 | 1 | 0 | 0 | 157 | 57 | 15 | 30 | 5009 | 692477 | 83362 | 0.91 |
| refactor | 2 | 1 | 0 | 0 | 88 | 34 | 10 | 20 | 2851 | 440085 | 85241 | 0.83 |
| pin | 1 | 1 | 0 | 0 | 29 | 21 | 5 | 10 | 1830 | 217631 | 42722 | 0.42 |
| diff | 2 | 1 | 0 | 0 | 35 | 21 | 7 | 14 | 2040 | 271887 | 78311 | 0.72 |
| predicate | 1 | 0 | 0 | 0 | 15 | 11 | 2 | 4 | 923 | 61276 | 37883 | 0.33 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 6 | 6 | 0 | 0 | 256 | 131 | 32 | 64 | 11764 | 1400972 | 250020 | 2.52 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 240 | 158 | 37 | 74 | 13379 | 1840956 | 263306 | 2.74 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a writer started through `detach-command.sh start` whose reader closes early is killed by SIGPIPE (status 141) and prints nothing on stderr, as it does when started from a shell ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 162 | 40 | 80 | 13757 | 1854622 | 256842 | 2.70 | 443 | unknown | 0/5 | structural-owed |  |  | full |
| `detach-command.sh start` still runs its command in a session of its own, records its exit code in `.tdd/<name>.exit` and its output in `.tdd/<name>.out`, and `wait` keeps its exit codes 0/1/2/3 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 77 | 17 | 34 | 6741 | 941396 | 98977 | 1.12 | unknown | unknown | unknown | unknown |  |  | pin |
| every case `detach-command.test.sh` already holds is still in the suite with its assertions unchanged by the branch's diff ⟦diff-checked⟧ ⟦criterion 3⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 32 | 9 | 18 | 2963 | 333163 | 116194 | 1.06 | 59 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| a writer started through `detach-command.sh start` whose reader closes early is killed by SIGPIPE (status 141) and prints nothing on stderr, as it does when started from a shell ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 88 | 0.83 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 |
| fast | 41 | 40 | 41 |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 69 | 138 | 25143 | 3241928 | 513326 | 5.26 |
