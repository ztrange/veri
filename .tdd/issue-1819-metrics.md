### 📊 Metrics — issue 1819

Wall time for the issue: 1124 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run bailed — ci-timeout, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1098 | 17463 | 12109 | 0.04 |
| red | 5 | 2 | 0 | 0 | 475 | 158 | 40 | 78 | 11509 | 1247446 | 117430 | 0.53 |
| green | 5 | 1 | 0 | 0 | 120 | 82 | 22 | 42 | 6542 | 554167 | 87267 | 0.50 |
| exhausted | 1 | 0 | 0 | 0 | 10 | 8 | 2 | 4 | 783 | 45180 | 10852 | 0.08 |
| refactor | 2 | 1 | 0 | 0 | 30 | 20 | 6 | 12 | 1355 | 153465 | 26120 | 0.09 |
| pin | 1 | 1 | 0 | 0 | 39 | 36 | 5 | 10 | 1185 | 133273 | 12721 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 134 | 107 | 27 | 52 | 7997 | 686619 | 101132 | 0.40 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 470 | 142 | 34 | 68 | 9266 | 1108165 | 93397 | 0.44 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 81 | 64 | 15 | 28 | 5209 | 356210 | 71970 | 0.47 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 364 | 0.24 |
| green | 0 | 0.00 | 71 | 0.39 |
| exhausted | 0 | 0.00 | 10 | 0.08 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A medium case (`@pytest.mark.process("git")`, real git) builds a scratch git repository with a `main` branch and no tags, runs handoff_state in it through `run_cli`, and gets exit 0, a first line `main <sha> (none)` naming main's sha and `(none)` for the missing tag, and no traceback on stderr ⟦criterion 2⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 120 | 33 | 64 | 9810 | 927776 | 128598 | 0.71 | unknown | 2/2 | unknown | unknown |  |  | full |
| A medium case (`@pytest.mark.process("git")`, real git) builds a scratch git repository with a `main` branch and no tags, runs handoff_state in it through `run_cli` with `gh` faked the way test_handoff_state.py's cases do, by monkeypatching `handoff_state.open_prs` to return `[]` and `status.json_document` to return `(0, '{"runs": []}')`, so no network is reached, and gets exit 0, a first line `main <sha> (none)` naming main's sha and `(none)` for the missing tag, and no traceback on stderr ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 108 | 31 | 60 | 8130 | 885177 | 93442 | 0.40 | 264 | unknown | 0/5 | nothing-left |  |  | full |
| When `git tag` lists no tags, handoff_state's first line is `main <sha> (none)` with exit 0 and no traceback, pinned by a small in-process case faking git ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 76 | 11 | 22 | 3434 | 320578 | 32350 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A medium case (`@pytest.mark.process("git")`, real git) builds a scratch git repository with a `main` branch and no tags, runs handoff_state in it through `run_cli` with `gh` faked the way test_handoff_state.py's cases do, by monkeypatching `handoff_state.open_prs` to return `[]` and `status.json_document` to return `(0, '{"runs": []}')`, so no network is reached, and gets exit 0, a first line `main <sha> (none)` naming main's sha and `(none)` for the missing tag, and no traceback on stderr ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 30 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 1 |
| fast | 5 | 5 | 4 | 4 |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 76 | 148 | 22472 | 2150994 | 266499 | 1.31 |
