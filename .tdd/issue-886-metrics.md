### 📊 Metrics — issue 886

Wall time for the issue: 2141 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/890.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 884 | 11866 | 29604 | 0.13 |
| red | 14 | 4 | 3 | 0 | 913 | 498 | 97 | 190 | 44526 | 4526546 | 638117 | 5.63 |
| green | 8 | 4 | 0 | 0 | 1090 | 248 | 65 | 126 | 20829 | 2809297 | 322803 | 2.83 |
| refactor | 7 | 3 | 0 | 0 | 233 | 108 | 27 | 52 | 9328 | 958764 | 268872 | 2.03 |
| exhausted | 1 | 0 | 0 | 0 | 43 | 41 | 7 | 14 | 3178 | 320039 | 53093 | 0.55 |
| diff | 2 | 1 | 0 | 0 | 53 | 26 | 7 | 14 | 2089 | 246805 | 75793 | 0.54 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 13 | 3 | 0 | 991 | 276 | 80 | 154 | 27949 | 3060260 | 627596 | 3.40 |
| developer | claude-opus-5-5 | 17 | 0 | 0 | 0 | 1353 | 654 | 124 | 244 | 52885 | 5813057 | 760686 | 8.31 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 1278 | 7.47 | 170 | 0.95 |
| green | 0 | 0.00 | 415 | 0.78 |
| refactor | 0 | 0.00 | 75 | 0.59 |
| exhausted | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When run-conductor.sh's fetch of origin fails only because another process holds a ref lock in the skill clone (reproduced offline: a local bare remote as origin, plus a held `refs/remotes/origin/<branch>.lock` released while the run waits), the run is not refused — the fetch is retried and the conductor starts ⟦criterion 1⟧ | 11 | 5 | 0 | 0 | 0 | 0 | 326 | 72 | 138 | 28594 | 3119081 | 461131 | 3.99 | 1005 | unknown | 0/5 | nothing-left |  |  | full |
| A fetch of origin that fails for any other reason (an origin URL pointing at a path that is no remote) is still refused with exit 2 and the existing `fetch of origin failed` message, without waiting out the lock retries ⟦criterion 2⟧ | 13 | 3 | 3 | 0 | 0 | 0 | 379 | 76 | 152 | 33437 | 3297028 | 559061 | 4.73 | 2891 | 2/2 | 0/5 | nothing-left |  |  | full |
| When the skill clone's ref lock outlives five back-to-back fetches and is released only while the run waits between retries, run-conductor.sh sleeps between its fetch retries and the conductor starts with origin's tip pinned — a retry loop with no wait between attempts does not close the race ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 190 | 48 | 92 | 15830 | 2198537 | 262693 | 2.32 | unknown | unknown | 0/5 | nothing-left |  |  | full |
| The branch adds a case under skills/tdd/scripts/tests/ that reproduces the concurrent ref-lock case without the network — a local bare remote plus a held lock or competing ref update — and touches no other suite's existing cases ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 7 | 14 | 2089 | 246805 | 75793 | 0.54 | 80 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When run-conductor.sh's fetch of origin fails only because another process holds a ref lock in the skill clone (reproduced offline: a local bare remote as origin, plus a held `refs/remotes/origin/<branch>.lock` released while the run waits), the run is not refused — the fetch is retried and the conductor starts ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 93 | 0.90 |
| When run-conductor.sh's fetch of origin fails only because another process holds a ref lock in the skill clone (reproduced offline: a local bare remote as origin, plus a held `refs/remotes/origin/<branch>.lock` released while the run waits), the run is not refused — the fetch is retried and the conductor starts ⟦criterion 1⟧ | 2 | 0/5 | nothing-left |  | 0 | 0 | 0.00 |
| A fetch of origin that fails for any other reason (an origin URL pointing at a path that is no remote) is still refused with exit 2 and the existing `fetch of origin failed` message, without waiting out the lock retries ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 65 | 0.55 |
| When the skill clone's ref lock outlives five back-to-back fetches and is released only while the run waits between retries, run-conductor.sh sleeps between its fetch retries and the conductor starts with origin's tip pinned — a retry loop with no wait between attempts does not close the race ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 75 | 0.59 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 15 | 16 | 19 | 0 | 0 | 0 | 1 | 1 | 4 | 41 | 20 | 0 | 22 | 21 | 20 | 19 | 0 | 23 | 21 | 21 | 22 | 25 | 0 | 22 | 21 | 23 | 23 | 20 | 0 | 21 | 0 | 71 | 1 | 0 | 0 | 38 | 1 | 0 | 24 | 24 |
| fast | 14 | 15 | 16 | 15 | 15 | 16 | 16 | 14 | 14 | 14 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 18 | 21 | 22 | 24 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 204 | 398 | 80834 | 8873317 | 1388282 | 11.71 |
