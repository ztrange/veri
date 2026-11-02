### 📊 Metrics — issue 2900

Wall time for the issue: 1675 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 20 planned.
Outcome: the run bailed — revise-impossible, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $6.47 over 124 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87232 tokens, largest 173563 tokens
Conductor context: first turn 87226 tokens, largest 175817 tokens
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
| 53 | $0.56 | 87226 |
| 54 | $0.07 | 93924 |
| 55 | $0.05 | 97586 |
| 56 | $0.03 | 99158 |
| 57 | $0.05 | 103408 |
| 58 | $0.05 | 107303 |
| 59 | $0.03 | 107803 |
| 60 | $0.03 | 108332 |
| 61 | $0.02 | 108666 |
| 62 | $0.03 | 109160 |
| 63 | $0.03 | 109940 |
| 64 | $0.03 | 110763 |
| 65 | $0.03 | 112064 |
| 66 | $0.03 | 113209 |
| 67 | $0.03 | 113907 |
| 68 | $0.02 | 114132 |
| 69 | $0.03 | 115520 |
| 70 | $0.03 | 116435 |
| 71 | $0.03 | 117237 |
| 72 | $0.03 | 118361 |
| 73 | $0.04 | 119934 |
| 74 | $0.03 | 120521 |
| 75 | $0.04 | 122139 |
| 76 | $0.03 | 122803 |
| 77 | $0.04 | 124232 |
| 78 | $0.03 | 124669 |
| 79 | $0.03 | 125423 |
| 80 | $0.09 | 133446 |
| 81 | $0.04 | 134562 |
| 82 | $0.04 | 135655 |
| 83 | $0.03 | 136559 |
| 84 | $0.03 | 137078 |
| 85 | $0.03 | 137913 |
| 86 | $0.03 | 138614 |
| 87 | $0.05 | 141110 |
| 88 | $0.04 | 141971 |
| 89 | $0.04 | 142997 |
| 90 | $0.04 | 144289 |
| 91 | $0.03 | 144817 |
| 92 | $0.03 | 145535 |
| 93 | $0.03 | 145860 |
| 94 | $0.03 | 146253 |
| 95 | $0.04 | 147673 |
| 96 | $0.04 | 148442 |
| 97 | $0.03 | 148829 |
| 98 | $0.04 | 149726 |
| 99 | $0.04 | 150510 |
| 100 | $0.03 | 150979 |
| 101 | $0.04 | 151710 |
| 102 | $0.04 | 152673 |
| 103 | $0.04 | 153996 |
| 104 | $0.04 | 154620 |
| 105 | $0.04 | 155186 |
| 106 | $0.04 | 156726 |
| 107 | $0.03 | 157043 |
| 108 | $0.04 | 157716 |
| 109 | $0.04 | 158231 |
| 110 | $0.04 | 158787 |
| 111 | $0.04 | 159927 |
| 112 | $0.03 | 160196 |
| 113 | $0.04 | 161715 |
| 114 | $0.05 | 163737 |
| 115 | $0.04 | 164174 |
| 116 | $0.04 | 164499 |
| 117 | $0.04 | 165443 |
| 118 | $0.04 | 165688 |
| 119 | $0.04 | 166031 |
| 120 | $0.04 | 166345 |
| 121 | $0.04 | 167604 |
| 122 | $0.05 | 169278 |
| 123 | $0.05 | 171062 |
| 124 | $0.07 | 175817 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 32 | 29 | 2 | 4 | 3385 | 33346 | 38641 | 0.13 |
| red | 14 | 6 | 0 | 0 | 476 | 296 | 55 | 110 | 26052 | 1683015 | 311194 | 1.36 |
| green | 32 | 3 | 13 | 0 | 1764 | 649 | 143 | 278 | 58056 | 4476010 | 583344 | 3.15 |
| red-missing | 5 | 0 | 0 | 0 | 239 | 186 | 32 | 62 | 19518 | 1111937 | 122526 | 0.61 |
| pin | 7 | 6 | 1 | 0 | 191 | 130 | 32 | 64 | 11342 | 993544 | 142685 | 0.57 |
| exhausted | 2 | 0 | 0 | 0 | 94 | 62 | 10 | 20 | 4525 | 315108 | 40887 | 0.36 |
| refactor | 4 | 0 | 0 | 0 | 88 | 76 | 12 | 22 | 5583 | 308569 | 99136 | 0.50 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 31 | 16 | 15 | 0 | 1475 | 619 | 124 | 248 | 54861 | 3915572 | 492741 | 2.17 |
| developer | claude-sonnet-5-5 | 21 | 0 | 0 | 0 | 840 | 493 | 99 | 190 | 46101 | 3095465 | 488603 | 2.25 |
| developer | claude-opus-5-5 | 14 | 0 | 0 | 0 | 569 | 316 | 63 | 122 | 27499 | 1910492 | 357069 | 2.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 273 | 0.87 |
| green | 1128 | 1.97 | 1231 | 2.13 |
| red-missing | 0 | 0.00 | 202 | 0.52 |
| pin | 0 | 0.00 | 115 | 0.35 |
| exhausted | 0 | 0.00 | 94 | 0.36 |
| refactor | 0 | 0.00 | 64 | 0.39 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails ⟦criterion 1⟧ | 13 | 2 | 4 | 0 | 0 | 0 | 247 | 57 | 112 | 24420 | 1779058 | 251197 | 1.34 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails; every guard the step adds is pinned by a case only it decides ⟦criterion 1⟧ | 23 | 4 | 7 | 0 | 0 | 0 | 610 | 116 | 226 | 57313 | 3778205 | 468683 | 2.60 | unknown | red 1/2, green 2/2 | unknown | unknown |  |  | already-satisfied |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails. Minimal: its green adds only what this step's own case decides — no argument-shape check, no unknown-commit check, no signal handler; each lands in the later step that pins it ⟦criterion 1⟧ | 13 | 3 | 3 | 0 | 0 | 0 | 263 | 52 | 102 | 20501 | 1564736 | 262378 | 1.25 | 873 | 2/2 | 0/5 | nothing-left |  |  | already-satisfied |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` exits 1 when the command passes on the restored before-state ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 8 | 16 | 3418 | 244595 | 38848 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| `mutation-probe.sh --before` leaves `<test-path>` exactly as it is in the working tree while the command runs, not restored to `<sha>` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 11 | 22 | 3932 | 354999 | 41516 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| `mutation-probe.sh --before` leaves every file under `.tdd/` as it is in the working tree while the command runs, not restored to `<sha>` ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 83 | 19 | 36 | 5585 | 541747 | 96833 | 0.35 | 263 | unknown | 0/5 | nothing-left |  |  | full |
| `mutation-probe.sh --before` removes a file added since `<sha>` (tracked or untracked) while the command runs ⟦criterion 1⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 114 | 21 | 42 | 9907 | 624843 | 140317 | 0.68 | unknown | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails. Minimal: its green adds only what this step's own case decides — no argument-shape check, no unknown-commit check, no signal handler; each lands in the later step that pins it ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.06 |
| `mutation-probe.sh --before` leaves every file under `.tdd/` as it is in the working tree while the command runs, not restored to `<sha>` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 15 | 0.05 |
| `mutation-probe.sh --before` removes a file added since `<sha>` (tracked or untracked) while the command runs ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 1 | 64 | 0.39 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 0 | 1 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 2 | 3 | 2 | 3 | 0 | 3 | 4 | 3 | 3 | 0 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 3 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 2 | 3 | 2 | 2 |  |  |  |  |  |  |  |  |  |
| fast | 19 | 20 | 18 | 19 | 21 | 22 | 19 | 21 | 19 | 18 | 19 | 19 | 19 | 19 | 20 | 21 | 21 | 21 | 19 | 19 | 20 | 19 | 30 | 20 | 36 | 19 | 24 | 19 | 19 | 19 | 19 | 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 286 | 560 | 128461 | 8921529 | 1338413 | 13.15 (estimate) |
