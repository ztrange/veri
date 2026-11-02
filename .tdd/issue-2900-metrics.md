### 📊 Metrics — issue 2900

Wall time for the issue: 1675 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 20 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.23 over 52 turns, in 1 sessions, on opus.
Conductor context: first turn 87232 tokens, largest 173563 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87232 |
| 2 | $0.08 | 94109 |
| 3 | $0.06 | 97760 |
| 4 | $0.05 | 99377 |
| 5 | $0.03 | 100053 |
| 6 | $0.04 | 100584 |
| 7 | $0.03 | 100827 |
| 8 | $0.04 | 101313 |
| 9 | $0.04 | 101963 |
| 10 | $0.03 | 102299 |
| 11 | $0.05 | 104327 |
| 12 | $0.05 | 107150 |
| 13 | $0.06 | 110351 |
| 14 | $0.04 | 110821 |
| 15 | $0.06 | 113905 |
| 16 | $0.11 | 123296 |
| 17 | $0.05 | 125902 |
| 18 | $0.06 | 128504 |
| 19 | $0.05 | 130162 |
| 20 | $0.05 | 131477 |
| 21 | $0.06 | 134601 |
| 22 | $0.05 | 135311 |
| 23 | $0.04 | 135844 |
| 24 | $0.04 | 136479 |
| 25 | $0.06 | 138034 |
| 26 | $0.04 | 138781 |
| 27 | $0.07 | 142355 |
| 28 | $0.05 | 143235 |
| 29 | $0.05 | 145232 |
| 30 | $0.04 | 145455 |
| 31 | $0.05 | 146211 |
| 32 | $0.05 | 147056 |
| 33 | $0.05 | 147969 |
| 34 | $0.05 | 149797 |
| 35 | $0.05 | 150671 |
| 36 | $0.08 | 155249 |
| 37 | $0.05 | 156406 |
| 38 | $0.06 | 158094 |
| 39 | $0.04 | 158433 |
| 40 | $0.06 | 159771 |
| 41 | $0.05 | 160456 |
| 42 | $0.05 | 161579 |
| 43 | $0.05 | 162079 |
| 44 | $0.05 | 162578 |
| 45 | $0.05 | 163585 |
| 46 | $0.04 | 163999 |
| 47 | $0.06 | 165778 |
| 48 | $0.05 | 166100 |
| 49 | $0.05 | 166949 |
| 50 | $0.09 | 171883 |
| 51 | $0.05 | 172768 |
| 52 | $0.05 | 173563 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 32 | 29 | 2 | 4 | 3385 | 33346 | 38641 | 0.13 |
| red | 6 | 3 | 0 | 0 | 212 | 128 | 23 | 46 | 12326 | 689764 | 143826 | 0.71 |
| green | 20 | 0 | 10 | 0 | 1154 | 437 | 93 | 180 | 40676 | 2968092 | 348228 | 2.00 |
| red-missing | 4 | 0 | 0 | 0 | 202 | 156 | 28 | 54 | 16849 | 983658 | 100769 | 0.52 |
| pin | 4 | 3 | 1 | 0 | 115 | 74 | 19 | 38 | 7357 | 600641 | 86170 | 0.35 |
| exhausted | 2 | 0 | 0 | 0 | 94 | 62 | 10 | 20 | 4525 | 315108 | 40887 | 0.36 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 19 | 7 | 12 | 0 | 991 | 413 | 76 | 152 | 38637 | 2439876 | 295537 | 1.37 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 357 | 229 | 47 | 90 | 24457 | 1549237 | 203394 | 1.04 |
| developer | claude-opus-5-5 | 11 | 0 | 0 | 0 | 461 | 244 | 52 | 100 | 22024 | 1601496 | 259590 | 1.66 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 212 | 0.71 |
| green | 0 | 0.00 | 1154 | 2.00 |
| red-missing | 0 | 0.00 | 202 | 0.52 |
| pin | 0 | 0.00 | 115 | 0.35 |
| exhausted | 0 | 0.00 | 94 | 0.36 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails ⟦criterion 1⟧ | 13 | 2 | 4 | 0 | 0 | 0 | 247 | 57 | 112 | 24420 | 1779058 | 251197 | 1.34 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails; every guard the step adds is pinned by a case only it decides ⟦criterion 1⟧ | 23 | 4 | 7 | 0 | 0 | 0 | 610 | 116 | 226 | 57313 | 3778205 | 468683 | 2.60 | unknown | red 1/2, green 2/2 | unknown | unknown |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 0 | 1 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 2 | 3 | 2 | 3 | 0 | 3 | 4 | 3 | 3 | 0 | 2 | 2 |
| fast | 19 | 20 | 18 | 19 | 21 | 22 | 19 | 21 | 19 | 18 | 19 | 19 | 19 | 19 | 20 | 21 | 21 | 21 | 19 | 19 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 175 | 342 | 85118 | 5590609 | 758521 | 7.30 |
