### 📊 Metrics — issue 2705

Wall time for the issue: 4129 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2804.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.19 over 33 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87308 tokens, largest 179481 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87308 |
| 2 | $0.10 | 98103 |
| 3 | $0.03 | 99739 |
| 4 | $0.03 | 100896 |
| 5 | $0.04 | 103298 |
| 6 | $0.02 | 103616 |
| 7 | $0.02 | 103882 |
| 8 | $0.07 | 109759 |
| 9 | $0.05 | 112822 |
| 10 | $0.12 | 125487 |
| 11 | $0.06 | 129523 |
| 12 | $0.05 | 132084 |
| 13 | $0.04 | 133915 |
| 14 | $0.04 | 135313 |
| 15 | $0.05 | 137665 |
| 16 | $0.04 | 139106 |
| 17 | $0.04 | 141178 |
| 18 | $0.04 | 142907 |
| 19 | $0.04 | 144605 |
| 20 | $0.05 | 147349 |
| 21 | $0.04 | 149051 |
| 22 | $0.05 | 151252 |
| 23 | $0.05 | 153157 |
| 24 | $0.05 | 155372 |
| 25 | $0.06 | 158956 |
| 26 | $0.05 | 161545 |
| 27 | $0.08 | 167878 |
| 28 | $0.05 | 170551 |
| 29 | $0.05 | 172887 |
| 30 | $0.06 | 176067 |
| 31 | $0.05 | 177611 |
| 32 | $0.04 | 178466 |
| 33 | $0.04 | 179481 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 11 | 2 | 4 | 1371 | 33283 | 35199 | 0.11 |
| red | 10 | 5 | 0 | 0 | 645 | 146 | 45 | 84 | 17576 | 1271484 | 216781 | 0.85 |
| green | 9 | 4 | 0 | 0 | 811 | 93 | 43 | 78 | 10704 | 1159527 | 137187 | 0.57 |
| red-contradicted | 1 | 0 | 0 | 0 | 28 | 18 | 5 | 10 | 2405 | 157273 | 19749 | 0.09 |
| refactor | 4 | 0 | 0 | 0 | 25 | 10 | 8 | 16 | 813 | 200138 | 63564 | 0.19 |
| diff | 2 | 1 | 0 | 0 | 320 | 31 | 17 | 30 | 3067 | 449830 | 49980 | 0.20 |
| pin | 1 | 1 | 0 | 0 | 25 | 10 | 4 | 8 | 1163 | 113844 | 17433 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 12 | 0 | 0 | 885 | 125 | 44 | 84 | 13439 | 1132587 | 234763 | 0.83 |
| developer | claude-sonnet-5-5 | 16 | 0 | 0 | 0 | 983 | 194 | 80 | 146 | 23660 | 2252792 | 305130 | 1.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `REVISE_BUDGET` is registered in `skills/tdd/scripts/veri/tunables.py` with default 2: with it unset, `tunables.resolve("REVISE_BUDGET")` answers the default of 2 and no error; a unit-tier case in `tests/py/unit/test_tunables.py` that deletes `REVISE_BUDGET` from its own environment, since the hermetic fixture only clears `VERI_*` ⟦criterion 1⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 90 | 34 | 58 | 10739 | 832127 | 143972 | 0.55 | 686 | unknown | 0/5 | nothing-left |  |  | full |
| A `REVISE_BUDGET` that is not a whole number refuses at `run-conductor.sh`: exit 2, exactly one stderr line naming `REVISE_BUDGET`, before any process starts (no `claude` launched and no `gh` asked); a case driving `run_conductor` in-process with `run_cli` and a bad value such as `three` ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 48 | 21 | 40 | 5734 | 599128 | 93019 | 0.35 | 463 | unknown | 0/5 | nothing-left |  |  | full |
| `test_1313` in `tests/py/unit/test_tunables.py` sweeps `REVISE_BUDGET` again: its `if name == "REVISE_BUDGET": continue` skip is gone and `ENTRY_POINTS` names `veri.run_conductor` for it, so the guard pins the refusal; test-only, no production change ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 17 | 30 | 3067 | 449830 | 49980 | 0.20 | 417 | n/a | n/a | n/a |  |  | full |
| A bad `REVISE_BUDGET` refuses before the bash-version probe too: with `VERI_BASH_MAJOR` unset, `run_conductor` exits 2 naming `REVISE_BUDGET` and starts no process at all, not even the `bash` that `launch_floor.bash_refusal` runs; a case driving `run_conductor` in-process with `run_cli` and `fake_processes` ⟦added⟧ ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 54 | 19 | 38 | 5891 | 560851 | 90041 | 0.34 | 407 | unknown | 0/5 | nothing-left |  |  | full |
| With `REVISE_BUDGET` unset, the conductor's prompt holds no line naming a revise budget value: a pin case on `run_conductor.prompt`, deleting `REVISE_BUDGET` from its own environment ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 11 | 22 | 5443 | 351577 | 40543 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| A set whole-number `REVISE_BUDGET` appears in the conductor's prompt, as one line carrying the name and the value, for example `REVISE_BUDGET=3` gives a line holding both `REVISE_BUDGET` and `3`; a case on `run_conductor.prompt`, with no change to any graded prose ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 46 | 20 | 38 | 4854 | 558583 | 87139 | 0.32 | 376 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `REVISE_BUDGET` is registered in `skills/tdd/scripts/veri/tunables.py` with default 2: with it unset, `tunables.resolve("REVISE_BUDGET")` answers the default of 2 and no error; a unit-tier case in `tests/py/unit/test_tunables.py` that deletes `REVISE_BUDGET` from its own environment, since the hermetic fixture only clears `VERI_*` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| A `REVISE_BUDGET` that is not a whole number refuses at `run-conductor.sh`: exit 2, exactly one stderr line naming `REVISE_BUDGET`, before any process starts (no `claude` launched and no `gh` asked); a case driving `run_conductor` in-process with `run_cli` and a bad value such as `three` ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.05 |
| A bad `REVISE_BUDGET` refuses before the bash-version probe too: with `VERI_BASH_MAJOR` unset, `run_conductor` exits 2 naming `REVISE_BUDGET` and starts no process at all, not even the `bash` that `launch_floor.bash_refusal` runs; a case driving `run_conductor` in-process with `run_cli` and `fake_processes` ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |
| A set whole-number `REVISE_BUDGET` appears in the conductor's prompt, as one line carrying the name and the value, for example `REVISE_BUDGET=3` gives a line holding both `REVISE_BUDGET` and `3`; a case on `run_conductor.prompt`, with no change to any graded prose ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 6 | 4 | 5 | 5 | 26 | 28 | 26 | 36 | 4 | 6 | 27 | 32 | 32 | 32 | 35 | 26 | 25 | 24 | 24 |
| fast | 43 | 43 | 41 | 30 | 30 | 37 | 31 | 38 | 28 | 26 |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 3 | 37 | 4 | 5 | 3 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 124 | 230 | 37099 | 3385379 | 539893 | 4.25 (estimate) |
