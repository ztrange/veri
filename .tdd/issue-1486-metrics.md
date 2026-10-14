### 📊 Metrics — issue 1486

Wall time for the issue: 2719 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1530.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 7 | 1 | 2 | 924 | 10394 | 43928 | 0.19 |
| red | 5 | 1 | 0 | 0 | 305 | 136 | 35 | 70 | 16404 | 1947088 | 271550 | 1.45 |
| green | 2 | 1 | 0 | 0 | 502 | 51 | 15 | 30 | 5526 | 791833 | 99384 | 0.53 |
| refactor | 2 | 1 | 0 | 0 | 244 | 39 | 4 | 10 | 554 | 182753 | 46309 | 0.46 |
| pin | 3 | 3 | 0 | 0 | 75 | 47 | 15 | 30 | 4616 | 699695 | 137963 | 0.67 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 441 | 112 | 25 | 52 | 8389 | 1128116 | 273741 | 1.55 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 697 | 168 | 45 | 90 | 19635 | 2503647 | 325393 | 1.75 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| verify.sh diff exits 1 without launching the verifier leaf, its stdout reason naming `<file>::<case>`, when a pytest case (`def test_…` in a `test_*.py`) absent at the branch-base sha and present at the step-base sha is absent from every test file at HEAD ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 31 | 64 | 11062 | 1626991 | 251507 | 1.53 | 916 | unknown | 0/5 | nothing-left |  |  | full |
| verify.sh diff does not trip on a case an earlier step added and this step moved to another `test_*.py` file under the same name: the verifier leaf is still launched ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 11 | 22 | 4814 | 550547 | 98675 | 0.50 | unknown | unknown | unknown | unknown |  |  | pin |
| verify.sh diff exits 2 without launching the verifier leaf when the branch-base sha or the step-base sha cannot be resolved ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 12 | 24 | 5156 | 615873 | 101652 | 0.52 | unknown | unknown | unknown | unknown |  |  | pin |
| verify.sh diff still launches the verifier leaf and returns its verdict when the step deletes only cases that existed at the branch-base sha ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 15 | 30 | 6068 | 827958 | 103372 | 0.56 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| verify.sh diff exits 1 without launching the verifier leaf, its stdout reason naming `<file>::<case>`, when a pytest case (`def test_…` in a `test_*.py`) absent at the branch-base sha and present at the step-base sha is absent from every test file at HEAD ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 244 | 0.46 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 19 | 18 | 1 | 144 | 18 | 0 | 145 | 4 | 22 | 21 | 22 | 31 |
| fast | 57 | 61 | 59 |  |  |  |  |  |  |  |  |  |
| target | 2 | 3 | 2 | 2 | 1 | 4 | 1 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 70 | 142 | 28024 | 3631763 | 599134 | 3.29 |
