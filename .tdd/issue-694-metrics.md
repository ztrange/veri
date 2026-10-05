### 📊 Metrics — issue 694

Wall time for the issue: 1596 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/916.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 15 | 2 | 4 | 1531 | 37396 | 38622 | 0.35 |
| cover | 2 | 0 | 0 | 0 | 28 | 20 | 6 | 12 | 1825 | 174131 | 49319 | 0.47 |
| transform | 4 | 2 | 0 | 0 | 112 | 87 | 24 | 48 | 7540 | 805607 | 104995 | 1.15 |
| diff | 4 | 2 | 0 | 0 | 86 | 64 | 17 | 34 | 6033 | 538603 | 102221 | 1.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 5 | 5 | 0 | 0 | 107 | 82 | 21 | 42 | 7712 | 642667 | 140829 | 1.41 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 138 | 104 | 28 | 56 | 9217 | 913070 | 154328 | 1.60 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Move Function: move `modes_named` out of `skills/tdd/scripts/stop-run.sh` into `skills/tdd/scripts/lib/stop-modes.sh`, unchanged, so it reads `STOP_MODES` at call time and `stop-run.sh` calls the library's copy at its two refusals. Predicate, false before and true after: `grep -Eq '^modes_named\(\)' skills/tdd/scripts/lib/stop-modes.sh && ! grep -Eq 'modes_named\(\)' skills/tdd/scripts/stop-run.sh && grep -Fq '$(modes_named)' skills/tdd/scripts/stop-run.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 52 | 16 | 32 | 4636 | 530243 | 77854 | 0.82 | 108 | unknown | unknown | unknown |  |  | full |
| Replace Literal with Function Call: `stop-requested.sh`'s malformed-request refusal builds the mode phrase with `$(modes_named)` in place of the hand-spelled `at-ledger, at-leaf or now`, its message otherwise unchanged. Predicate, false before and true after: `grep -Fq '$(modes_named)' skills/tdd/scripts/stop-requested.sh && ! grep -Fq 'at-ledger, at-leaf or now' skills/tdd/scripts/stop-requested.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 55 | 14 | 28 | 4729 | 449495 | 76460 | 0.80 | 95 | unknown | unknown | unknown |  |  | full |
| for every input, `stop-run.sh`'s and `stop-requested.sh`'s stdout, stderr and exit codes are what they are on origin/main, both exit-2 refusals still naming "at-ledger, at-leaf or now" ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 11 | 22 | 3901 | 369417 | 55036 | 0.59 | 70 | unknown | unknown | unknown |  |  | full |
| no test file is changed anywhere on the branch ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 21 | 6 | 12 | 2132 | 169186 | 47185 | 0.45 | 46 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 7 | 2 | 0 | 1 | 2 | 2 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 49 | 98 | 16929 | 1555737 | 295157 | 3.01 |
