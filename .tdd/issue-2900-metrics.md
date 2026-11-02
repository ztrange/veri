### 📊 Metrics — issue 2900

Wall time for the issue: 1013 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 18 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.56 over 50 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87232 tokens, largest 171883 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87232 |
| 2 | $0.07 | 94109 |
| 3 | $0.05 | 97760 |
| 4 | $0.03 | 99377 |
| 5 | $0.03 | 100053 |
| 6 | $0.02 | 100584 |
| 7 | $0.02 | 100827 |
| 8 | $0.02 | 101313 |
| 9 | $0.03 | 101963 |
| 10 | $0.02 | 102299 |
| 11 | $0.04 | 104327 |
| 12 | $0.04 | 107150 |
| 13 | $0.05 | 110351 |
| 14 | $0.03 | 110821 |
| 15 | $0.05 | 113905 |
| 16 | $0.10 | 123296 |
| 17 | $0.05 | 125902 |
| 18 | $0.05 | 128504 |
| 19 | $0.04 | 130162 |
| 20 | $0.04 | 131477 |
| 21 | $0.05 | 134601 |
| 22 | $0.03 | 135311 |
| 23 | $0.03 | 135844 |
| 24 | $0.03 | 136479 |
| 25 | $0.04 | 138034 |
| 26 | $0.03 | 138781 |
| 27 | $0.06 | 142355 |
| 28 | $0.04 | 143235 |
| 29 | $0.04 | 145232 |
| 30 | $0.03 | 145455 |
| 31 | $0.04 | 146211 |
| 32 | $0.04 | 147056 |
| 33 | $0.04 | 147969 |
| 34 | $0.04 | 149797 |
| 35 | $0.04 | 150671 |
| 36 | $0.07 | 155249 |
| 37 | $0.04 | 156406 |
| 38 | $0.04 | 158094 |
| 39 | $0.03 | 158433 |
| 40 | $0.04 | 159771 |
| 41 | $0.04 | 160456 |
| 42 | $0.04 | 161579 |
| 43 | $0.04 | 162079 |
| 44 | $0.04 | 162578 |
| 45 | $0.04 | 163585 |
| 46 | $0.04 | 163999 |
| 47 | $0.05 | 165778 |
| 48 | $0.04 | 166100 |
| 49 | $0.04 | 166949 |
| 50 | $0.07 | 171883 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 32 | 29 | 2 | 4 | 3385 | 33346 | 38641 | 0.13 |
| red | 2 | 1 | 0 | 0 | 62 | 35 | 8 | 16 | 3699 | 248527 | 41054 | 0.16 |
| green | 8 | 0 | 4 | 0 | 398 | 151 | 35 | 68 | 14781 | 1085565 | 148203 | 0.84 |
| red-missing | 1 | 0 | 0 | 0 | 32 | 24 | 6 | 12 | 3362 | 205313 | 22518 | 0.11 |
| pin | 1 | 1 | 0 | 0 | 20 | 12 | 5 | 10 | 1220 | 154132 | 19326 | 0.08 |
| exhausted | 1 | 0 | 0 | 0 | 47 | 25 | 3 | 6 | 1358 | 85521 | 20096 | 0.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 3 | 5 | 0 | 319 | 138 | 26 | 52 | 13804 | 793404 | 124445 | 0.53 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 187 | 97 | 25 | 48 | 10970 | 770892 | 125143 | 0.63 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 85 | 41 | 8 | 16 | 3031 | 248108 | 40250 | 0.31 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 62 | 0.16 |
| green | 0 | 0.00 | 398 | 0.84 |
| red-missing | 0 | 0.00 | 32 | 0.11 |
| pin | 0 | 0.00 | 20 | 0.08 |
| exhausted | 0 | 0.00 | 47 | 0.14 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails ⟦criterion 1⟧ | 13 | 2 | 4 | 0 | 0 | 0 | 247 | 57 | 112 | 24420 | 1779058 | 251197 | 1.34 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 2 | 2 |
| fast | 19 | 20 | 18 | 19 | 21 | 22 | 19 | 21 |  |  |  |
| target | 2 | 2 | 1 | 2 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 59 | 116 | 27805 | 1812404 | 289838 | 4.03 (estimate) |
