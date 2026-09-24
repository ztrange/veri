### 📊 Metrics — issue 457

Wall time for the issue: 2237 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 4 planned.
Outcome: the run bailed — untestable-criterion, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 543 | 11207 | 28705 | 0.24 |
| red | 5 | 1 | 0 | 0 | 591 | 290 | 46 | 86 | 26740 | 2373758 | 276232 | 3.22 |
| green | 4 | 1 | 1 | 0 | 1040 | 180 | 37 | 74 | 17129 | 1788010 | 181830 | 2.16 |
| refactor | 2 | 1 | 0 | 0 | 112 | 63 | 16 | 32 | 5251 | 762843 | 85588 | 0.94 |
| pin | 2 | 2 | 0 | 0 | 314 | 58 | 13 | 22 | 5580 | 483598 | 90795 | 0.93 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 31 | 0.47 |
| green | 1040 | 2.16 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A detached launch whose leaf answers and whose completion file lands only after every recorded pid has exited is reported by what the leaf saw, never as `<no completion file under leaf …>` ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 357 | 71 | 140 | 33057 | 3475281 | 377847 | 4.38 | 1404 | 1/2 | 1/5 | nothing-structural |
| A launch whose derived leaf name no completion file is written under is still reported as a naming fault, answered well inside the wait budget rather than after it ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 109 | 20 | 36 | 9878 | 995038 | 107229 | 1.25 | unknown | unknown | unknown | unknown |
| A launch line that reaches no supervisor at all is reported as `<no leaf ran>` by a case of its own ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 97 | 17 | 30 | 9373 | 776904 | 100836 | 1.15 | unknown | unknown | unknown | unknown |
| Removing any one of the three behaviours — trusting the leaf's answer after a late completion file, the fast naming-fault report, the `<no leaf ran>` report — turns a named case of skill-leaf-env.test.sh red ⟦criterion 4⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 28 | 4 | 8 | 2392 | 160986 | 48533 | 0.47 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 16 | 0 | 14 | 15 | 15 | 61 | 15 | 0 | 17 | 17 | 16 | 18 |
| fast | 2 | 2 | 3 | 2 | 2 |  |  |  |  |  |  |  |
| target | 15 | 14 | 18 | 194 | 18 | 16 |  |  |  |  |  |  |
| all | 302 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 113 | 216 | 55243 | 5419416 | 663150 | 7.49 |
