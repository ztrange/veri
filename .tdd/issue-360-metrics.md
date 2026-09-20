### 📊 Metrics — issue 360

Wall time for the issue: 7706 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 12 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/395.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 21 | 9 | 0 | 0 | 1304 | 1175 | 224 | 400 | 96409 | 9962524 | 972020 | 17.11 |
| green | 18 | 9 | 0 | 0 | 1986 | 1262 | 275 | 492 | 101494 | 12639682 | 853568 | 17.40 |
| refactor | 18 | 9 | 0 | 0 | 1520 | 1381 | 238 | 448 | 115862 | 12039683 | 895248 | 17.87 |
| pin | 3 | 3 | 0 | 0 | 99 | 82 | 24 | 42 | 7019 | 897964 | 112678 | 1.75 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 324 | 4.20 |
| green | 0 | 0.00 | 163 | 1.73 |
| refactor | 0 | 0.00 | 127 | 1.62 |
| pin | 0 | 0.00 | 99 | 1.75 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| add-ledger-step.sh inserts `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` after the anchor step, carrying the anchor's k, exit 0 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 362 | 71 | 126 | 29799 | 3029522 | 264265 | 4.90 | unknown | unknown | 1/5 | structural-owed |
| `before` inserts several texts, in the order given, on the lines before the anchor step ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 356 | 73 | 130 | 28560 | 3276110 | 263735 | 4.99 | 454 | unknown | 3/5 | structural-owed |
| an anchor step carrying no `⟦criterion k⟧` yields an added step carrying none ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 88 | 19 | 36 | 7573 | 835038 | 80849 | 1.42 | unknown | unknown | unknown | unknown |
| criterion-finished.sh does not report k finished while an unchecked `⟦added⟧` step serving k remains ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 21 | 38 | 6866 | 886326 | 81411 | 1.43 | unknown | unknown | unknown | unknown |
| over budget, the call inserts no checkbox, exits 1, and appends every text as a plain bullet under a trailing `## Owed steps` heading ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 384 | 72 | 134 | 32065 | 3394595 | 273072 | 5.23 | 676 | unknown | 2/5 | nothing-structural |
| next-unchecked.sh never returns a bullet under `## Owed steps` ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 108 | 21 | 40 | 9368 | 953849 | 84453 | 1.56 | unknown | unknown | unknown | unknown |
| an anchor matching no step, or more than one, exits 2 and leaves the ledger byte-identical ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 330 | 66 | 120 | 26716 | 2905555 | 258794 | 4.71 | 426 | unknown | 2/5 | structural-owed |
| VERI_STEP_GROWTH unset allows 3 added steps; a value that is not a non-negative integer, set-but-empty included, exits 2 and leaves the ledger byte-identical ⟦criterion 8⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 445 | 81 | 144 | 35402 | 3751757 | 294928 | 5.71 | 548 | unknown | 3/5 | structural-owed |
| SKILL.md's preflight refuses to start on a bad VERI_STEP_GROWTH, as it does a bad VERI_REFACTOR_BUDGET ⟦criterion 9⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 434 | 79 | 136 | 33650 | 3551351 | 299472 | 5.61 | 645 | unknown | 2/5 | nothing-structural |
| SKILL.md's Draft PR section copies the ledger's `## Owed steps` bullets into the PR body under `## Owed steps` ⟦criterion 10⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 444 | 82 | 148 | 39152 | 4022183 | 310115 | 6.09 | 647 | unknown | 1/5 | structural-owed |
| SKILL.md says each insertion emits a `step-added` event | 6 | 3 | 0 | 0 | 0 | 0 | 450 | 91 | 170 | 36472 | 4652541 | 317271 | 6.41 | 652 | unknown | 2/5 | structural-owed |
| CLAUDE.md's budgets invariant names VERI_STEP_GROWTH as a fifth axis, plan growth, never merged with the other four ⟦criterion 11⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 419 | 85 | 160 | 35161 | 4281026 | 305149 | 6.07 | 622 | unknown | 2/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 183 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 54 | 54 | 0 | 0 | 0 | 0 | 0 | 47 | 54 | 0 | 0 | 0 | 1 | 1 | 0 | 47 | 53 | 1 | 0 | 1 | 1 | 1 | 19 | 19 | 22 | 1 | 1 | 1 |
| fast | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 761 | 1382 | 320784 | 35539853 | 2833514 | 54.13 |
