### 📊 Metrics — issue 2552

Wall time for the issue: 1033 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: unknown of 13 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.17 over 38 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 84909 tokens, largest 169193 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 84909 |
| 2 | $0.07 | 91540 |
| 3 | $0.04 | 94507 |
| 4 | $0.03 | 96145 |
| 5 | $0.02 | 96764 |
| 6 | $0.03 | 97485 |
| 7 | $0.02 | 97917 |
| 8 | $0.02 | 98180 |
| 9 | $0.02 | 98407 |
| 10 | $0.02 | 99069 |
| 11 | $0.02 | 99469 |
| 12 | $0.07 | 106049 |
| 13 | $0.08 | 112898 |
| 14 | $0.06 | 117976 |
| 15 | $0.04 | 119715 |
| 16 | $0.04 | 121374 |
| 17 | $0.03 | 121769 |
| 18 | $0.06 | 126193 |
| 19 | $0.03 | 126560 |
| 20 | $0.03 | 127522 |
| 21 | $0.03 | 128032 |
| 22 | $0.05 | 130882 |
| 23 | $0.04 | 132097 |
| 24 | $0.17 | 150203 |
| 25 | $0.04 | 151145 |
| 26 | $0.04 | 151851 |
| 27 | $0.04 | 152665 |
| 28 | $0.04 | 153537 |
| 29 | $0.03 | 153866 |
| 30 | $0.06 | 157229 |
| 31 | $0.04 | 158366 |
| 32 | $0.04 | 159138 |
| 33 | $0.04 | 159535 |
| 34 | $0.05 | 161377 |
| 35 | $0.04 | 162112 |
| 36 | $0.05 | 164500 |
| 37 | $0.04 | 164997 |
| 38 | $0.07 | 169193 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 13 | 2 | 4 | 1359 | 35156 | 36380 | 0.11 |
| red | 2 | 1 | 0 | 0 | 144 | 62 | 9 | 18 | 5433 | 287335 | 67334 | 0.25 |
| green | 6 | 0 | 3 | 0 | 632 | 174 | 34 | 66 | 15277 | 1096192 | 116377 | 0.80 |
| exhausted | 1 | 0 | 0 | 0 | 67 | 21 | 3 | 6 | 1523 | 80477 | 15233 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 2 | 3 | 0 | 457 | 116 | 20 | 40 | 9210 | 607640 | 82143 | 0.36 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 65 | 44 | 6 | 12 | 4437 | 205737 | 50142 | 0.19 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 337 | 110 | 22 | 42 | 9945 | 685783 | 103039 | 0.74 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 144 | 0.25 |
| green | 0 | 0.00 | 632 | 0.80 |
| exhausted | 0 | 0.00 | 67 | 0.12 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `tests-frozen.sh rerecord-rebased <ledger> <pre-rebase-sha>` re-records an upstream-only stale case: on a branch whose ledger holds a ticked earlier step with a frozen case (recorded by `record --step`), where that case was then changed only on `origin/<default>` (the branch `refs/remotes/origin/HEAD` names) and the branch was rebased onto it, the verb rewrites that earlier step's record at the case's `HEAD` body and exits 0, and the next `check-earlier` for a later step exits 0; the module's usage line names the new verb. Pinned by one medium case (`@pytest.mark.process`, a real git repository with an `origin` remote under tmp_path) in skills/tdd/scripts/tests/py/test_tests_frozen_process.py ⟦criterion 1⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 257 | 46 | 90 | 22233 | 1464004 | 198944 | 1.18 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 17 | 17 | 17 | 18 | 13 | 0 | 13 | 12 | 12 |
| fast | 38 | 42 | 30 | 30 | 32 | 31 |  |  |  |
| target | 6 | 4 | 4 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 48 | 94 | 23592 | 1499160 | 235324 | 3.45 (estimate) |
