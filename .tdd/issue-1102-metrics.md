### 📊 Metrics — issue 1102

Wall time for the issue: 1788 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1134.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 814 | 12001 | 31246 | 0.14 |
| red | 6 | 3 | 0 | 0 | 149 | 129 | 38 | 68 | 12475 | 1558736 | 268690 | 2.20 |
| green | 6 | 3 | 0 | 0 | 269 | 132 | 38 | 74 | 12407 | 1609320 | 242266 | 1.98 |
| refactor | 6 | 3 | 0 | 0 | 273 | 163 | 51 | 100 | 16357 | 2403198 | 264299 | 2.24 |
| diff | 2 | 1 | 0 | 0 | 90 | 38 | 12 | 24 | 3454 | 519950 | 80403 | 0.64 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 11 | 0 | 0 | 437 | 231 | 75 | 146 | 24665 | 3319301 | 444666 | 2.69 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 353 | 238 | 65 | 122 | 20842 | 2783904 | 442238 | 4.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a prompt file that cannot be read (a directory given as the prompt file, inside the case's scratch tree) makes run_leaf.main return 2, not 1, launch no leaf, and still print its one `run-leaf.sh: <path>: <reason>` stderr line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 106 | 34 | 62 | 10292 | 1315063 | 245647 | 1.92 | 248 | unknown | 0/5 | nothing-left |  |  | full |
| copying ~/.gitconfig into the leaf's temp git config raising OSError (faked at the process boundary in tests/py/) makes run_leaf.main return 2, not 1, launch no leaf, leave no temp file, and still print its one `run-leaf.sh: <path>: <reason>` stderr line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 43 | 84 | 14294 | 1970127 | 269021 | 2.25 | 308 | unknown | 0/5 | nothing-left |  |  | full |
| the stream temp file in $TMPDIR vanishing during the leaf's run, so the re-read after the leaf ends fails, makes run_leaf.main return 2, not 1, and still print its one `run-leaf.sh: <path>: <reason>` stderr line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 160 | 50 | 96 | 16653 | 2286064 | 260587 | 2.25 | 320 | unknown | 0/5 | nothing-left |  |  | full |
| each of the three failure paths has a case that forces it using the path's type or shape inside the case's scratch tree, or a fake at the process boundary in tests/py/, and no case on this branch forces a failure with permission bits or a system path ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 12 | 24 | 3454 | 519950 | 80403 | 0.64 | 110 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| a prompt file that cannot be read (a directory given as the prompt file, inside the case's scratch tree) makes run_leaf.main return 2, not 1, launch no leaf, and still print its one `run-leaf.sh: <path>: <reason>` stderr line ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 50 | 0.58 |
| copying ~/.gitconfig into the leaf's temp git config raising OSError (faked at the process boundary in tests/py/) makes run_leaf.main return 2, not 1, launch no leaf, leave no temp file, and still print its one `run-leaf.sh: <path>: <reason>` stderr line ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 97 | 0.78 |
| the stream temp file in $TMPDIR vanishing during the leaf's run, so the re-read after the leaf ends fails, makes run_leaf.main return 2, not 1, and still print its one `run-leaf.sh: <path>: <reason>` stderr line ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 126 | 0.89 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 2 | 1 | 0 | 0 | 1 | 2 | 2 | 2 | 0 | 0 | 2 | 2 | 1 | 2 |
| fast | 16 | 17 | 16 | 17 | 17 | 16 | 18 | 17 | 18 | 18 | 18 | 21 |  |  |  |  |
| target | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 140 | 268 | 45507 | 6103205 | 886904 | 7.20 |
