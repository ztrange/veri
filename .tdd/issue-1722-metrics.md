### 📊 Metrics — issue 1722

Wall time for the issue: 252 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 9 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 1108 | 17463 | 13779 | 0.05 |
| red | 2 | 1 | 0 | 0 | 47 | 39 | 12 | 22 | 4465 | 342061 | 37650 | 0.17 |
| green | 3 | 0 | 0 | 0 | 65 | 55 | 14 | 26 | 4963 | 382301 | 50527 | 0.33 |
| exhausted | 1 | 0 | 0 | 0 | 25 | 22 | 5 | 10 | 1881 | 142313 | 17635 | 0.15 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 26 | 20 | 5 | 8 | 2351 | 95560 | 29351 | 0.11 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 31 | 27 | 8 | 16 | 3222 | 263964 | 22078 | 0.11 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 90 | 77 | 19 | 36 | 6844 | 524614 | 68162 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 47 | 0.17 |
| green | 0 | 0.00 | 65 | 0.33 |
| exhausted | 0 | 0.00 | 25 | 0.15 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `stop-reason.sh` with no argument prints a usage line on stderr and exits 2, and `stop-reason.sh <issue>` for an issue with no run under `.tdd/wt/<issue>` exits 2; the script is a `/bin/sh` shim over a `veri/` module (the `status.sh` convention) and is listed in `SCRIPTS.md` as its declared caller ⟦criterion 5⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 116 | 31 | 58 | 11309 | 866675 | 105812 | 0.66 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| affected | 1 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 32 | 60 | 12417 | 884138 | 119591 | 0.70 |
