### 📊 Metrics — issue 1306

Wall time for the issue: 3945 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1382.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 13 | 4 | 6 | 1672 | 118452 | 44147 | 0.21 |
| red | 7 | 3 | 0 | 0 | 581 | 168 | 45 | 86 | 17480 | 2198303 | 367991 | 3.03 |
| green | 6 | 3 | 0 | 0 | 2086 | 146 | 44 | 86 | 14833 | 2142255 | 278263 | 2.26 |
| refactor | 7 | 3 | 0 | 0 | 1715 | 127 | 44 | 86 | 12298 | 2091918 | 319473 | 2.34 |
| pin | 1 | 1 | 0 | 0 | 20 | 14 | 5 | 8 | 1558 | 173007 | 43645 | 0.21 |
| predicate | 1 | 0 | 0 | 0 | 17 | 13 | 4 | 8 | 1104 | 163155 | 40524 | 0.38 |
| structural | 1 | 0 | 0 | 0 | 195 | 28 | 8 | 16 | 2956 | 401335 | 48501 | 0.53 |
| transform | 1 | 1 | 0 | 0 | 172 | 10 | 4 | 8 | 1031 | 168642 | 41176 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 12 | 0 | 0 | 2793 | 212 | 71 | 136 | 21332 | 3140081 | 589127 | 2.88 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 2015 | 307 | 87 | 168 | 31600 | 4316986 | 594593 | 6.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A fetch of origin whose stderr is git 2.53's held-ref-lock wording (`error: fetching ref refs/remotes/origin/master failed: reference already exists`), fed in-process as the fetch's stderr, is retried through the sleep exactly as a `cannot lock ref` fetch is — at most 60 fetches and 59 sleeps — then refused with exit 2 ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 1 | 125 | 39 | 76 | 12225 | 1788718 | 323770 | 2.29 | 1475 | unknown | 0/5 | nothing-left |  |  | full |
| When a fetch refused after spending its retries failed on git 2.53's `reference already exists` wording, the refusal on stderr names the ref lock as the cause, as the `cannot lock ref` wording already does ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 42 | 82 | 15494 | 2073232 | 282280 | 2.31 | 1121 | unknown | 1/5 | nothing-structural |  |  | full |
| A fetch of origin failing with neither ref-lock wording is still refused at once — exit 2 after one fetch and no sleep — and its refusal does not name the ref lock ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 100 | 31 | 58 | 10414 | 1416197 | 229227 | 1.93 | unknown | unknown | unknown | unknown |  |  | pin |
| When a launch refuses because the ref lock was never released, stderr carries the conductor's own line naming the ref lock ("another process holds the ref lock") for the `cannot lock ref` wording as well as git 2.53's `reference already exists`, and the #1012 never-released case in `skills/tdd/scripts/tests/run-conductor.test.sh` asserts on that line rather than on `cannot lock ref`; watched red first on this Mac's git 2.50 ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 133 | 42 | 82 | 13127 | 2060468 | 304296 | 2.41 | 2023 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A fetch of origin whose stderr is git 2.53's held-ref-lock wording (`error: fetching ref refs/remotes/origin/master failed: reference already exists`), fed in-process as the fetch's stderr, is retried through the sleep exactly as a `cannot lock ref` fetch is — at most 60 fetches and 59 sleeps — then refused with exit 2 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 660 | 0.90 |
| When a fetch refused after spending its retries failed on git 2.53's `reference already exists` wording, the refusal on stderr names the ref lock as the cause, as the `cannot lock ref` wording already does ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 418 | 0.69 |
| When a launch refuses because the ref lock was never released, stderr carries the conductor's own line naming the ref lock ("another process holds the ref lock") for the `cannot lock ref` wording as well as git 2.53's `reference already exists`, and the #1012 never-released case in `skills/tdd/scripts/tests/run-conductor.test.sh` asserts on that line rather than on `cannot lock ref`; watched red first on this Mac's git 2.50 ⟦added⟧ ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 637 | 0.76 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 229 | 217 | 267 | 177 | 4 | 2 | 1 | 169 | 176 | 159 | 157 | 2 | 161 | 158 | 169 | 184 | 178 | 0 | 3 | 172 | 0 | 163 |
| fast | 75 | 68 | 72 | 68 | 64 | 61 | 57 | 66 | 61 | 64 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 1 | 0 | 1 | 0 | 173 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 158 | 304 | 52932 | 7457067 | 1183720 | 9.14 |
