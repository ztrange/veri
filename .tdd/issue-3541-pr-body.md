Closes #3541 — `tests-frozen.sh rerecord-refactored` no longer refuses an earlier step's frozen case whose body a ticked `⟦suite-repair⟧` step's green rewrote. It accepts a record that matches the case as it stood just before green, and the existing assertion and helper checks still apply. A case changed outside any suite-repair step still refuses. The run took 2 steps from the committed ledger `.tdd/issue-3541.md`:

1. Re-record a case a ticked suite-repair green rewrote (red → green, blind-verified; refactor: nothing left to tidy).
2. A case changed by an ordinary green still refuses: a regression pin, blind-verified by mutation (`repaired = True` turns it red).

The guard is scoped: `green^` stands for the record only when `green` is one of the own commits of a ticked `⟦suite-repair⟧` step of the ledger (`_is_suite_repair_green` in `skills/tdd/scripts/veri/tests_frozen.py`), not when any such step is ticked elsewhere in it. Own commits come from the committed ledger, as in `_step_commits`. A lookup that fails refuses, and cases pin an unrelated ticked step, an unticked step, a ledger line the committed ledger never held, and a later commit that rewrites the case again with a changed assertion. The `git rev-parse` refusal for a non-commit green is unreachable from outside: `green^` then fails too, so the case is skipped anyway.

### 📊 Metrics — issue 3541

Wall time for the issue: 8482 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3562.
Lane: ready-for-agent
Suite flakes: skills/tdd/scripts/tests/py/test_fast_tier_guard.py.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.87 over 65 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78471 tokens, largest 121432 tokens
Conductor context: first turn 122296 tokens, largest 153301 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.49 | 78471 |
| 2 | $0.08 | 84504 |
| 3 | $0.03 | 85818 |
| 4 | $0.04 | 87386 |
| 5 | $0.03 | 88014 |
| 6 | $0.03 | 88434 |
| 7 | $0.03 | 88737 |
| 8 | $0.02 | 88974 |
| 9 | $0.03 | 89230 |
| 10 | $0.03 | 89487 |
| 11 | $0.03 | 89809 |
| 12 | $0.03 | 90136 |
| 13 | $0.03 | 90680 |
| 14 | $0.03 | 91464 |
| 15 | $0.03 | 91805 |
| 16 | $0.03 | 92837 |
| 17 | $0.10 | 101813 |
| 18 | $0.04 | 103634 |
| 19 | $0.04 | 104759 |
| 20 | $0.04 | 105657 |
| 21 | $0.03 | 106249 |
| 22 | $0.04 | 107027 |
| 23 | $0.04 | 108920 |
| 24 | $0.04 | 109618 |
| 25 | $0.03 | 109968 |
| 26 | $0.03 | 110681 |
| 27 | $0.04 | 111486 |
| 28 | $0.04 | 112159 |
| 29 | $0.04 | 113666 |
| 30 | $0.03 | 114384 |
| 31 | $0.04 | 114700 |
| 32 | $0.03 | 115276 |
| 33 | $0.04 | 115872 |
| 34 | $0.04 | 116521 |
| 35 | $0.03 | 116871 |
| 36 | $0.04 | 117878 |
| 37 | $0.06 | 121111 |
| 38 | $0.03 | 121432 |
| 39 | $0.03 | 122296 |
| 40 | $0.03 | 122979 |
| 41 | $0.04 | 124697 |
| 42 | $0.03 | 125063 |
| 43 | $0.03 | 125479 |
| 44 | $0.03 | 126144 |
| 45 | $0.03 | 126901 |
| 46 | $0.05 | 130517 |
| 47 | $0.03 | 131167 |
| 48 | $0.03 | 131462 |
| 49 | $0.03 | 132025 |
| 50 | $0.04 | 133203 |
| 51 | $0.15 | 149039 |
| 52 | $0.03 | 149258 |
| 53 | $0.03 | 149516 |
| 54 | $0.03 | 149775 |
| 55 | $0.03 | 150199 |
| 56 | $0.03 | 150533 |
| 57 | $0.03 | 150880 |
| 58 | $0.03 | 151461 |
| 59 | $0.03 | 151719 |
| 60 | $0.03 | 151978 |
| 61 | $0.03 | 152301 |
| 62 | $0.03 | 152594 |
| 63 | $0.03 | 153015 |
| 64 | $0.03 | 153301 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 0 | 0 | $0.00 |
| 🟢 Green | 1 | 393 | $0.01 |
| 🛠️ Refactor | 1 | 393 | $0.01 |
| 🔎 verify-green | 1 | 393 | $0.01 |
| 🔎 verify-refactor | 1 | 393 | $0.01 |
| 🔎 verify-<phase> (revised) | 0 | 0 | $0.00 |
| 🗺️ Plan | 1 | 393 | $0.01 |
| 🗺️ verify-plan | 1 | 393 | $0.01 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 4 | 1572 | $0.03 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 8 | 1 | 2 | 904 | 0 | 18849 | 0.06 |
| red | 3 | 1 | 0 | 0 | 277 | 73 | 20 | 36 | 7462 | 365134 | 75983 | 0.30 |
| green | 2 | 1 | 0 | 0 | 1192 | 45 | 12 | 22 | 3611 | 167689 | 59689 | 0.20 |
| refactor | 1 | 0 | 0 | 0 | 6 | 3 | 2 | 4 | 140 | 18157 | 19204 | 0.05 |
| pin | 1 | 1 | 0 | 0 | 43 | 20 | 6 | 12 | 1899 | 93578 | 20913 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 943 | 66 | 17 | 32 | 5509 | 213511 | 98419 | 0.32 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 588 | 83 | 24 | 44 | 8507 | 431047 | 96219 | 0.37 |

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
| tests-frozen.sh rerecord-refactored re-records an earlier step's frozen case whose body a later ticked suite-repair-marked step's green commit rewrote (same assertion), its record still holding the body from before that green: the record is rewritten to the HEAD body, no `skipped:` line is printed, and it exits 0 so check-earlier accepts the case and the run does not bail needs-user ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 95 | 26 | 48 | 7915 | 408575 | 127841 | 0.44 | 2332 | unknown | 0/5 | nothing-left |  |  | full |
| tests-frozen.sh rerecord-refactored still refuses an earlier step's frozen case whose body was changed by a commit belonging to no ticked suite-repair-marked step (an ordinary feat: step's green, say): it prints `skipped: <file> <case> (body digest matches neither green nor HEAD)`, leaves the record as it was, and exits 1 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 14 | 26 | 5197 | 235983 | 47948 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tests-frozen.sh rerecord-refactored re-records an earlier step's frozen case whose body a later ticked suite-repair-marked step's green commit rewrote (same assertion), its record still holding the body from before that green: the record is rewritten to the HEAD body, no `skipped:` line is printed, and it exits 0 so check-earlier accepts the case and the run does not bail needs-user ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| tests-frozen.sh rerecord-refactored re-records an earlier step's frozen case whose body a later ticked suite-repair-marked step's green commit rewrote (same assertion), its record still holding the body from before that green: the record is rewritten to the HEAD body, no `skipped:` line is printed, and it exits 0 so check-earlier accepts the case and the run does not bail needs-user ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 2 | ? | ? | nothing-left 1, nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 11 | 6 | 201 | 217 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 66 | 85 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 7 | 3 | 3 | 3 | 4 | 2 | 2 | 2 | 3 | 3 | 3 | 4 | 5 | 4 | 6 | 5 | 7 | 6 | 7 | 6 | 6 | 7 | 5 | 6 | 8 | 8 | 8 | 10 | 9 | 5 | 4 | 8 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 41 | 76 | 14016 | 644558 | 194638 | 3.56 (estimate) |

## Owed by a human

pin-recheck flagged these for a look after step 1:
- needs a look: skills/tdd/scripts/veri/tests_frozen.py (old text gone) ×36
- needs a look: skills/tdd/scripts/veri/tests_frozen.py (old text occurs more than once) ×3
- needs a look: skills/tdd/scripts/veri/tests_frozen.py (base run failed)
