### 📊 Metrics — issue 2205

Wall time for the issue: 2042 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 8 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2273.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.57 over 58 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89178 |
| 2 | $0.02 | 89642 |
| 3 | $0.04 | 93021 |
| 4 | $0.03 | 94245 |
| 5 | $0.03 | 96121 |
| 6 | $0.02 | 96561 |
| 7 | $0.02 | 96887 |
| 8 | $0.02 | 97209 |
| 9 | $0.02 | 97837 |
| 10 | $0.02 | 98241 |
| 11 | $0.04 | 100206 |
| 12 | $0.05 | 103455 |
| 13 | $0.09 | 112531 |
| 14 | $0.04 | 114916 |
| 15 | $0.04 | 116549 |
| 16 | $0.03 | 116910 |
| 17 | $0.03 | 117478 |
| 18 | $0.03 | 118026 |
| 19 | $0.03 | 118925 |
| 20 | $0.03 | 119398 |
| 21 | $0.03 | 120698 |
| 22 | $0.03 | 121449 |
| 23 | $0.04 | 123879 |
| 24 | $0.03 | 124764 |
| 25 | $0.03 | 125843 |
| 26 | $0.03 | 126722 |
| 27 | $0.03 | 127165 |
| 28 | $0.03 | 128000 |
| 29 | $0.03 | 128446 |
| 30 | $0.03 | 129204 |
| 31 | $0.03 | 129622 |
| 32 | $0.03 | 130515 |
| 33 | $0.03 | 130954 |
| 34 | $0.03 | 131701 |
| 35 | $0.03 | 132136 |
| 36 | $0.08 | 139322 |
| 37 | $0.04 | 140626 |
| 38 | $0.03 | 141104 |
| 39 | $0.03 | 141486 |
| 40 | $0.03 | 142145 |
| 41 | $0.04 | 144053 |
| 42 | $0.04 | 145010 |
| 43 | $0.04 | 145841 |
| 44 | $0.03 | 146293 |
| 45 | $0.03 | 146638 |
| 46 | $0.03 | 147107 |
| 47 | $0.04 | 148447 |
| 48 | $0.03 | 148917 |
| 49 | $0.03 | 149347 |
| 50 | $0.03 | 149828 |
| 51 | $0.03 | 150405 |
| 52 | $0.03 | 150898 |
| 53 | $0.04 | 152332 |
| 54 | $0.04 | 152905 |
| 55 | $0.03 | 153416 |
| 56 | $0.04 | 154146 |
| 57 | $0.03 | 154432 |
| 58 | $0.03 | 154772 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 10 | 2 | 4 | 1307 | 34003 | 35752 | 0.11 |
| red | 8 | 0 | 0 | 0 | 306 | 137 | 40 | 80 | 16589 | 1253958 | 201592 | 0.92 |
| pin | 8 | 7 | 1 | 0 | 259 | 84 | 30 | 58 | 8305 | 813436 | 112013 | 0.44 |
| prose | 3 | 0 | 0 | 0 | 39 | 30 | 3 | 6 | 4487 | 2866 | 30781 | 0.12 |
| skill-edit | 1 | 0 | 0 | 0 | 15 | 13 | 3 | 6 | 1871 | 56750 | 30173 | 0.10 |
| reconcile | 1 | 0 | 0 | 0 | 16 | 10 | 3 | 6 | 618 | 63691 | 32963 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 8 | 1 | 0 | 276 | 94 | 32 | 62 | 9612 | 847439 | 147765 | 0.55 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 234 | 107 | 33 | 66 | 12862 | 1022214 | 178223 | 0.68 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 88 | 40 | 10 | 20 | 4345 | 295435 | 56332 | 0.34 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 64 | 0.09 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| reconcile | 0 | 0.00 | 16 | 0.09 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A run whose events log's only end mark is the runner's `bail cause=needs-user` event with an empty `phase` and no `classification` field makes `stop-reason.sh <n>` print `bailed  None` as its first line and exit 0; one small case in `skills/tdd/scripts/tests/py/unit/test_stop_reason.py`, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 6 | 12 | 2305 | 149343 | 53567 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| `classify-bail.sh red-baseline` exits 2 and prints nothing to stdout; one small case in `skills/tdd/scripts/tests/py/unit/test_classify_bail.py`, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 20 | 7 | 14 | 2107 | 200819 | 33522 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| `stop-reason.sh <n>` on a run with no end event, no live conductor and a conductor log whose last launch has no result record prints `killed` as its first line followed by a `gap <ts> <ts>` line for a pair of consecutive events more than `VERI_SLEEP_GAP` seconds apart; one small case in `skills/tdd/scripts/tests/py/unit/test_stop_reason.py`, no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 8 | 16 | 2870 | 247068 | 37885 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `stop-reason.sh <n>` run where the current directory holds no `.tdd/wt/<n>` exits 2 and prints nothing to stdout; one small in-process case in `skills/tdd/scripts/tests/py/unit/test_stop_reason.py`, no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 8 | 16 | 2530 | 233955 | 34584 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| A `bail` mark made through `event.sh` with the current directory inside a git worktree at `.tdd/wt/<n>` of a repository lands in `.tdd/wt/<n>/.tdd/events.jsonl`, and `stop-reason.sh <n>` run from the main working tree prints `bailed <phase> <classification>` from that mark; one medium case with real git and real processes, `@pytest.mark.process`, in `skills/tdd/scripts/tests/py/test_stop_reason_process.py`, no production change ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 12 | 24 | 4267 | 389647 | 41597 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| `stop-reason.sh <n>` run with the current directory inside `.tdd/wt/<n>` exits 2 with a stderr diagnostic naming `.tdd/wt`; one small in-process case in `skills/tdd/scripts/tests/py/unit/test_stop_reason.py`, no production change ⟦criterion 4⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 62 | 18 | 36 | 6835 | 532933 | 74665 | 0.43 | unknown | 1/2 | unknown | unknown |  |  | pin |
| Saving every uncommitted edit in a git worktree as a binary-safe patch under `.tdd/` (`git add -A && git diff --cached --binary HEAD`), restoring the tree (`git reset --hard && git clean -fd`) and re-applying the patch with `git apply` brings back both a tracked and an untracked binary edit with matching content hashes; one medium case with real git, `@pytest.mark.process`, in `skills/tdd/scripts/tests/py/test_veri_bail_patch_process.py`, no production change ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 11 | 20 | 3980 | 313629 | 37785 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_fast_tier_guard.py — FAILED test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table - Failed: Timeout (>30s) ⟦suite-repair⟧ ⟦criterion 6⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 10 | 3 | 6 | 618 | 63691 | 32963 | 0.09 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 9 | 2 | 10 | 10 | 11 | 10 | 10 |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 11 | 11 | 10 | 11 | 12 | 11 | 10 | 10 | 12 | 3 | 9 | 11 | 10 | 11 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 81 | 160 | 33177 | 2224704 | 443274 | 1.79 |
