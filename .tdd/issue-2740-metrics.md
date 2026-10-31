### 📊 Metrics — issue 2740

Wall time for the issue: 421 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 4 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.43 over 17 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87090 tokens, largest 149936 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87090 |
| 2 | $0.08 | 95189 |
| 3 | $0.04 | 97563 |
| 4 | $0.02 | 98211 |
| 5 | $0.02 | 98705 |
| 6 | $0.02 | 99022 |
| 7 | $0.02 | 99290 |
| 8 | $0.10 | 108992 |
| 9 | $0.05 | 112416 |
| 10 | $0.05 | 116353 |
| 11 | $0.06 | 121266 |
| 12 | $0.14 | 135303 |
| 13 | $0.03 | 136102 |
| 14 | $0.05 | 138720 |
| 15 | $0.06 | 142132 |
| 16 | $0.04 | 144015 |
| 17 | $0.08 | 149936 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 10 | 1 | 2 | 1272 | 0 | 32307 | 0.09 |
| diff | 2 | 1 | 0 | 0 | 134 | 29 | 9 | 18 | 3437 | 241968 | 50506 | 0.18 |
| red | 1 | 0 | 0 | 0 | 28 | 14 | 3 | 6 | 2110 | 86124 | 20569 | 0.08 |
| pin | 2 | 0 | 0 | 0 | 55 | 21 | 8 | 16 | 2493 | 231792 | 19178 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 2 | 0 | 0 | 132 | 40 | 12 | 24 | 4631 | 309140 | 65742 | 0.24 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 100 | 34 | 9 | 18 | 4681 | 250744 | 56818 | 0.21 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 28 | 0.08 |
| pin | 0 | 0.00 | 55 | 0.10 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The cases in `skills/tdd/scripts/tests/py/unit/test_watch_runs.py` that expect `vanished 5` from `watch_runs.main` (`test_2588_main_still_reports_vanished_when_the_conductor_pid_file_holds_no_pid_that_answers_kill_0`, `test_2588_main_reports_vanished_when_the_pid_answers_kill_0_but_its_start_time_differs_from_conductor_pid_line_2`), and any fake clock they share, hold whether `vanished` fires at the first missed poll or only after the conductor has stayed absent a while: a generous `--max-wait` and an endless fake clock that jumps far ahead each call; test-only, no production change, and the keep-watching and timeout cases sharing that helper keep asserting what they assert ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 9 | 18 | 3437 | 241968 | 50506 | 0.18 | 238 | n/a | n/a | n/a |  |  | full |
| A run whose conductor is gone for good, with no ledger, no events and a conductor pid file that answers nothing, absent from `live_conductors()` on every poll while the clock runs on far past any wait, makes `watch_runs.main` print `vanished <issue>` and return 2; a small in-process case in `tests/py/unit/test_watch_runs.py`, no production change ⟦criterion 2⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 35 | 11 | 22 | 4603 | 317916 | 39747 | 0.18 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| fast | 0 | 37 | 40 |  |
| affected | 0 | 6 | 7 | 5 |
| target | 5 | 5 | 4 | 5 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 21 | 42 | 9312 | 559884 | 122560 | 1.88 (estimate) |
