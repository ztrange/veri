### 📊 Metrics — issue 817

Wall time for the issue: 7069 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 13 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1088.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 27 | 24 | 3 | 6 | 2039 | 110808 | 42049 | 0.40 |
| red | 19 | 8 | 0 | 0 | 806 | 674 | 131 | 258 | 58116 | 6624868 | 962064 | 10.18 |
| green | 22 | 8 | 3 | 0 | 2083 | 852 | 186 | 358 | 84620 | 9067133 | 1004518 | 11.54 |
| refactor | 16 | 8 | 0 | 0 | 797 | 351 | 85 | 170 | 34313 | 3916471 | 712634 | 7.17 |
| pin | 3 | 3 | 0 | 0 | 97 | 77 | 19 | 36 | 8122 | 826763 | 134037 | 1.40 |
| diff | 2 | 1 | 0 | 0 | 158 | 55 | 13 | 26 | 4444 | 604717 | 86789 | 0.90 |
| predicate | 6 | 0 | 0 | 0 | 111 | 80 | 20 | 40 | 6863 | 787905 | 245198 | 2.26 |
| structural | 3 | 0 | 0 | 0 | 146 | 85 | 17 | 34 | 5350 | 778934 | 126803 | 1.28 |
| transform | 3 | 1 | 2 | 0 | 59 | 42 | 11 | 22 | 3573 | 477168 | 80949 | 0.81 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 35 | 30 | 5 | 0 | 2108 | 978 | 233 | 462 | 95214 | 11036741 | 1486788 | 16.01 |
| developer | claude-opus-5-5 | 40 | 0 | 0 | 0 | 2176 | 1262 | 252 | 488 | 112226 | 12158026 | 1908253 | 19.94 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1296 | 7.03 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 118 | 1.63 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tick-ledger.sh, when writing the ticked ledger fails, leaves the ledger file byte-identical to what it was and exits 2 ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 265 | 52 | 104 | 24277 | 2488503 | 365907 | 3.91 | 715 | 1/2 | 0/5 | nothing-left |  |  | full |
| tick-ledger.sh, when the temporary file for the ticked ledger cannot be created beside it, leaves the ledger file byte-identical and exits 2 ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 135 | 36 | 72 | 13324 | 1769784 | 280499 | 2.86 | 355 | unknown | 0/5 | nothing-left |  |  | full |
| clear-refactor-pending.sh, when writing the cleared ledger fails, leaves the ledger file byte-identical to what it was and exits 2 ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 380 | 75 | 150 | 37589 | 3793947 | 437055 | 5.01 | 887 | 2/2 | 0/5 | nothing-left |  |  | full |
| clear-refactor-pending.sh, when every write to the ledger fails (the disk stays full), leaves the ledger file byte-identical and exits 2 ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 228 | 43 | 86 | 20780 | 2178594 | 294864 | 3.21 | 456 | unknown | 0/5 | malformed |  |  | full |
| clear-refactor-pending.sh, when the temporary file for the cleared ledger cannot be created beside it, leaves the ledger file byte-identical and exits 2 ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 131 | 36 | 70 | 13456 | 1641848 | 272412 | 2.78 | 350 | unknown | 0/5 | structural-owed |  |  | full |
| clear-refactor-pending.sh, when a trial write of the cleared ledger succeeds but the write to the ledger itself fails and so does writing its old contents back, leaves the ledger file byte-identical and exits 2 ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 42 | 80 | 19918 | 1964599 | 285661 | 3.08 | 437 | unknown | 1/5 | nothing-structural |  |  | full |
| clear-refactor-pending.sh never truncates the ledger before the cleared text is fully written: when the in-place write, the write-back and the fallback temp-file write all fail, the ledger file is byte-identical and it exits 2 ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 169 | 43 | 86 | 16894 | 2123600 | 279756 | 3.00 | 396 | unknown | 1/5 | structural-owed |  |  | full |
| add-ledger-step.sh finds a last ledger step that has no trailing newline as its anchor, inserting after it and keeping it in the ledger, rather than exiting 2 with "anchor matches no single step" ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 49 | 88 | 17917 | 2272379 | 296934 | 3.19 | 432 | unknown | 0/5 | nothing-left |  |  | full |
| add-ledger-step.sh keeps a last line that has no trailing newline in the ledger after an insertion anchored on an earlier step ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 95 | 14 | 26 | 5781 | 631882 | 95167 | 1.00 | unknown | unknown | unknown | unknown |  |  | pin |
| add-ledger-step.sh counts a last line with no trailing newline that carries ⟦added⟧ against VERI_STEP_GROWTH, so a batch that only fits without it exits 1 and files the texts as owed ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 70 | 15 | 28 | 6682 | 698416 | 96906 | 1.05 | unknown | unknown | unknown | unknown |  |  | pin |
| add-ledger-step.sh's `## Owed steps` append after a last line with no trailing newline starts that heading on a line of its own, leaving the last line intact ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 83 | 16 | 32 | 8553 | 871683 | 108092 | 1.21 | unknown | unknown | unknown | unknown |  |  | pin |
| no existing assertion in tick-ledger's, clear-refactor-pending's or add-ledger-step's suites (bash or pytest) changes, except one that pinned a defect criterion 1 or 2 fixes, changed only to the exit code, stderr or file state that criterion names ⟦diff-checked⟧ ⟦criterion 3⟧ | 14 | 2 | 2 | 0 | 0 | 0 | 262 | 61 | 122 | 20230 | 2648724 | 539739 | 5.25 | 177 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tick-ledger.sh, when writing the ticked ledger fails, leaves the ledger file byte-identical to what it was and exits 2 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 90 | 0.86 |
| tick-ledger.sh, when the temporary file for the ticked ledger cannot be created beside it, leaves the ledger file byte-identical and exits 2 ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 86 | 0.81 |
| clear-refactor-pending.sh, when writing the cleared ledger fails, leaves the ledger file byte-identical to what it was and exits 2 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 100 | 0.90 |
| clear-refactor-pending.sh, when every write to the ledger fails (the disk stays full), leaves the ledger file byte-identical and exits 2 ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | malformed | PASS | 0 | 114 | 0.93 |
| clear-refactor-pending.sh, when the temporary file for the cleared ledger cannot be created beside it, leaves the ledger file byte-identical and exits 2 ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 90 | 0.86 |
| clear-refactor-pending.sh, when a trial write of the cleared ledger succeeds but the write to the ledger itself fails and so does writing its old contents back, leaves the ledger file byte-identical and exits 2 ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 130 | 1.03 |
| clear-refactor-pending.sh never truncates the ledger before the cleared text is fully written: when the in-place write, the write-back and the fallback temp-file write all fail, the ledger file is byte-identical and it exits 2 ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 96 | 0.92 |
| add-ledger-step.sh finds a last ledger step that has no trailing newline as its anchor, inserting after it and keeping it in the ledger, rather than exiting 2 with "anchor matches no single step" ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 91 | 0.86 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 2 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 9 | 0 | 1 | 1 | 1 | 2 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 0 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 2 | 1 | 41 | 0 | 0 | 1 |
| fast | 41 | 42 | 45 | 49 | 42 | 42 | 42 | 42 | 42 | 48 | 42 | 41 | 41 | 41 | 42 | 42 | 41 | 42 | 42 | 41 | 42 | 42 | 41 | 42 | 43 | 41 | 42 | 41 | 41 | 41 | 45 | 42 | 41 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 485 | 950 | 207440 | 23194767 | 3395041 | 35.95 |
