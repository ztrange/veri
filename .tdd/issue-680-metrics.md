### 📊 Metrics — issue 680

Wall time for the issue: 8243 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/735.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 27 | 20 | 3 | 6 | 1601 | 109434 | 41912 | 0.39 |
| red | 11 | 5 | 0 | 0 | 2138 | 641 | 105 | 208 | 57752 | 5924106 | 585402 | 7.02 |
| pin | 1 | 1 | 0 | 0 | 207 | 31 | 6 | 12 | 3004 | 262335 | 41503 | 0.44 |
| green | 10 | 5 | 0 | 0 | 3067 | 390 | 90 | 180 | 34118 | 4557297 | 462908 | 5.30 |
| refactor | 10 | 5 | 0 | 0 | 772 | 165 | 53 | 106 | 16046 | 2330349 | 429236 | 4.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 17 | 17 | 0 | 0 | 3184 | 455 | 116 | 232 | 42255 | 5361022 | 743039 | 7.86 |
| developer | claude-opus-5-5 | 16 | 0 | 0 | 0 | 3027 | 792 | 141 | 280 | 70266 | 7822499 | 817922 | 9.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| the split-event case's stub delivers its one assistant event in two separate writes with no `sleep` between them, the second write held back by a file or FIFO the stub waits on without a time bound, and the case still asserts exactly one `context 7 53438` line ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 188 | 27 | 54 | 17662 | 1716675 | 125226 | 1.70 | unknown | unknown | unknown | unknown |  |  | pin |
| `stub_waits`' `await_context` waits for its `context <issue> <tokens>` line with no `sleep` and no iteration cap, returning only once that line has arrived ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 256 | 41 | 82 | 23787 | 2043011 | 269580 | 3.04 | 1149 | unknown | 0/5 | nothing-left |  |  | full |
| `stub_waits`' `heartbeats` carries no `sleep`, and the stop, under, beside and VERI_PARALLEL=1 cases that call it still assert the same expected marks, the stubs waiting on a file or FIFO rather than on elapsed time for the launcher to stop them ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 211 | 49 | 98 | 19910 | 2591348 | 290414 | 3.24 | 1224 | unknown | 0/5 | nothing-left |  |  | full |
| the stop case and the VERI_PARALLEL=1 one case wait for the stopped stub to be gone with no `sleep` and no iteration cap before reading its marks ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 193 | 47 | 94 | 17613 | 2316311 | 277328 | 3.03 | 1139 | unknown | 0/5 | nothing-left |  |  | full |
| the beside case's #8 stub waits for #7's stub to be gone with no `sleep` and no iteration cap, and the case still asserts `before-result-7`, `8-outlived-7`, `end-8` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 180 | 41 | 82 | 15856 | 1916292 | 265761 | 2.83 | 1024 | unknown | 0/5 | nothing-left |  |  | full |
| the again case's stub, after its step-done result, holds on a file or FIFO rather than `sleep 2`, and the case still asserts launches 7, 7, 8 and one `restarted 7` line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 199 | 49 | 96 | 16092 | 2490450 | 290740 | 3.15 | 1054 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `stub_waits`' `await_context` waits for its `context <issue> <tokens>` line with no `sleep` and no iteration cap, returning only once that line has arrived ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 158 | 0.80 |
| `stub_waits`' `heartbeats` carries no `sleep`, and the stop, under, beside and VERI_PARALLEL=1 cases that call it still assert the same expected marks, the stubs waiting on a file or FIFO rather than on elapsed time for the launcher to stop them ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 146 | 0.87 |
| the stop case and the VERI_PARALLEL=1 one case wait for the stopped stub to be gone with no `sleep` and no iteration cap before reading its marks ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 147 | 0.79 |
| the beside case's #8 stub waits for #7's stub to be gone with no `sleep` and no iteration cap, and the case still asserts `before-result-7`, `8-outlived-7`, `end-8` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 165 | 0.88 |
| the again case's stub, after its step-done result, holds on a file or FIFO rather than `sleep 2`, and the case still asserts launches 7, 7, 8 and one `restarted 7` line ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 156 | 0.87 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 83 | 86 | 87 | 85 | 88 | 88 | 85 | 86 | 85 | 84 | 82 | 79 | 81 | 79 | 87 | 82 | 84 | 0 | 80 | 79 | 81 | 85 | 86 | 85 | 86 | 82 | 83 | 83 |
| target | 84 | 86 | 87 | 81 | 87 | 83 | 81 | 82 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 27 | 29 | 26 | 27 | 26 | 26 | 25 | 27 | 27 | 25 | 25 | 27 | 24 | 26 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 257 | 512 | 112521 | 13183521 | 1560961 | 17.38 |
