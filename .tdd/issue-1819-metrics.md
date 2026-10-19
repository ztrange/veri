### 📊 Metrics — issue 1819

Wall time for the issue: 589 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: unknown of 2 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1098 | 17463 | 12109 | 0.04 |
| red | 2 | 1 | 0 | 0 | 364 | 56 | 18 | 36 | 4601 | 571566 | 56628 | 0.24 |
| green | 3 | 0 | 0 | 0 | 71 | 56 | 13 | 24 | 4426 | 311030 | 61118 | 0.39 |
| exhausted | 1 | 0 | 0 | 0 | 10 | 8 | 2 | 4 | 783 | 45180 | 10852 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 29 | 24 | 7 | 14 | 2721 | 171096 | 45210 | 0.16 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 346 | 41 | 12 | 24 | 2978 | 417933 | 23527 | 0.13 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 81 | 64 | 15 | 28 | 5209 | 356210 | 71970 | 0.47 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 364 | 0.24 |
| green | 0 | 0.00 | 71 | 0.39 |
| exhausted | 0 | 0.00 | 10 | 0.08 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A medium case (`@pytest.mark.process("git")`, real git) builds a scratch git repository with a `main` branch and no tags, runs handoff_state in it through `run_cli`, and gets exit 0, a first line `main <sha> (none)` naming main's sha and `(none)` for the missing tag, and no traceback on stderr ⟦criterion 2⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 120 | 33 | 64 | 9810 | 927776 | 128598 | 0.71 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 1 |
| fast | 5 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 34 | 66 | 10908 | 945239 | 140707 | 0.75 |
