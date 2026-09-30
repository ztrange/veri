### 📊 Metrics — issue 568

Wall time for the issue: 156 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 17 planned.
Outcome: the run bailed — step-too-big, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 1 | 0 | 0 | 53 | 45 | 10 | 20 | 6042 | 393331 | 77795 | 0.45 |
| green | 1 | 0 | 0 | 0 | 63 | 35 | 14 | 20 | 4391 | 476550 | 45631 | 0.32 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 53 | 0.45 |
| green | 0 | 0.00 | 63 | 0.32 |
| develop-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A suite fails naming `<file>:<line>` for any `gh issue`, `gh pr` or `gh repo` call left in skills/tdd/SKILL.md or skills/tdd/scripts/*.sh, exempting only the helper's ready-for-review route ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 80 | 24 | 40 | 10433 | 869881 | 123426 | 0.77 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 21 |
| fast | 5 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 24 | 40 | 10433 | 869881 | 123426 | 0.77 |
