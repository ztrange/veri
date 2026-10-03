### 📊 Metrics — issue 708

Wall time for the issue: 1938 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/746.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 14 | 2 | 4 | 1323 | 54821 | 37946 | 0.34 |
| diff | 6 | 3 | 0 | 0 | 193 | 133 | 29 | 58 | 12030 | 1254919 | 257220 | 2.55 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 4 | 4 | 0 | 0 | 121 | 75 | 14 | 28 | 5785 | 530090 | 162737 | 1.52 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 89 | 72 | 17 | 34 | 7568 | 779650 | 132429 | 1.37 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| fake_git takes an optional linked worktree, answering `git worktree list` with the main tree then that linked one, and the main-working-tree case uses it in place of its own fake_run, setattr and delenv, leaving test_status.py with one fake for subprocess.run ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 10 | 20 | 3322 | 426128 | 82225 | 0.81 | 78 | unknown | unknown | unknown |  |  | full |
| one helper taking the issue number and the ledger text makes `.tdd/wt/<issue>/.tdd/issue-<n>.md`, and every case that needs a run directory with a ledger gets it from that helper rather than its own mkdir(parents=True) and write_text ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 11 | 22 | 5604 | 506097 | 91930 | 0.95 | 117 | unknown | unknown | unknown |  |  | full |
| every case in test_status.py keeps its name and its assertions, and a command the fake does not expect still raises `unexpected command: …` ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 8 | 16 | 3104 | 322694 | 83065 | 0.79 | 70 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 1 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 31 | 62 | 13353 | 1309740 | 295166 | 2.89 |
