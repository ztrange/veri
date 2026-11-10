Closes #3544. Both plan steps went through a blind-verified Red → Green → Refactor cycle, and the ledger `.tdd/issue-3544.md` is committed.

- **Step 1 (criterion 1):** a step whose prose mentions ⟦skill-edit⟧ is a skill-edit step only when it starts with the marker or carries it in its trailing tag run. Otherwise it is added as a plain step (exit 0), with no unit lookup.
- **Step 2 (criterion 2):** when a skill-edit step's unit has no requirements list, the step is refused with exit 2 and `add-ledger-step.sh: <unit>: the unit file does not exist`. There is no traceback. verify-green replaced the guard with `return False` and watched the case go red.

The branch was rebased onto main, resolving a conflict with `unit_of`'s move into `ledger.py`, and verify-rebase passed it. The full suite is green on the rebased tip, and so is CI.

### 📊 Metrics — issue 3544

Wall time for the issue: 7921 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3561.
Lane: ready-for-agent
Suite flakes: skills/tdd/scripts/tests/py/unit/test_skill_diff_checked_readers.py.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.95 over 73 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78471 tokens, largest 163697 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.49 | 78471 |
| 2 | $0.06 | 84538 |
| 3 | $0.03 | 86174 |
| 4 | $0.03 | 88139 |
| 5 | $0.02 | 88856 |
| 6 | $0.02 | 89193 |
| 7 | $0.02 | 89581 |
| 8 | $0.02 | 89873 |
| 9 | $0.02 | 90190 |
| 10 | $0.02 | 90447 |
| 11 | $0.02 | 90799 |
| 12 | $0.02 | 91239 |
| 13 | $0.02 | 91778 |
| 14 | $0.03 | 92700 |
| 15 | $0.02 | 93451 |
| 16 | $0.02 | 93735 |
| 17 | $0.04 | 96441 |
| 18 | $0.03 | 97977 |
| 19 | $0.03 | 98846 |
| 20 | $0.02 | 99212 |
| 21 | $0.03 | 99907 |
| 22 | $0.02 | 100433 |
| 23 | $0.02 | 100758 |
| 24 | $0.02 | 101316 |
| 25 | $0.03 | 102643 |
| 26 | $0.02 | 103177 |
| 27 | $0.03 | 104861 |
| 28 | $0.10 | 114142 |
| 29 | $0.03 | 114892 |
| 30 | $0.03 | 115369 |
| 31 | $0.03 | 116143 |
| 32 | $0.03 | 117127 |
| 33 | $0.03 | 117938 |
| 34 | $0.03 | 118706 |
| 35 | $0.03 | 119195 |
| 36 | $0.03 | 120188 |
| 37 | $0.04 | 121634 |
| 38 | $0.03 | 122103 |
| 39 | $0.03 | 122578 |
| 40 | $0.03 | 123260 |
| 41 | $0.03 | 123723 |
| 42 | $0.03 | 124386 |
| 43 | $0.03 | 125026 |
| 44 | $0.03 | 125519 |
| 45 | $0.04 | 127606 |
| 46 | $0.04 | 129445 |
| 47 | $0.03 | 130254 |
| 48 | $0.04 | 132077 |
| 49 | $0.03 | 132915 |
| 50 | $0.03 | 133790 |
| 51 | $0.03 | 134753 |
| 52 | $0.04 | 135815 |
| 53 | $0.04 | 136983 |
| 54 | $0.15 | 152784 |
| 55 | $0.03 | 153052 |
| 56 | $0.03 | 153270 |
| 57 | $0.03 | 153566 |
| 58 | $0.03 | 154054 |
| 59 | $0.04 | 155461 |
| 60 | $0.04 | 156510 |
| 61 | $0.04 | 158033 |
| 62 | $0.04 | 158492 |
| 63 | $0.04 | 159110 |
| 64 | $0.04 | 160600 |
| 65 | $0.04 | 161154 |
| 66 | $0.03 | 161417 |
| 67 | $0.03 | 161732 |
| 68 | $0.04 | 162133 |
| 69 | $0.03 | 162381 |
| 70 | $0.04 | 162707 |
| 71 | $0.03 | 162998 |
| 72 | $0.04 | 163415 |
| 73 | $0.03 | 163697 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 2 | 32 | $0.00 |
| 🟢 Green | 2 | 57 | $0.00 |
| 🛠️ Refactor | 2 | 24 | $0.00 |
| 🔎 verify-green | 2 | 57 | $0.00 |
| 🔎 verify-refactor | 2 | 24 | $0.00 |
| 🔎 verify-<phase> (revised) | 3 | 40 | $0.00 |
| 🗺️ Plan | 1 | 16 | $0.00 |
| 🗺️ verify-plan | 1 | 16 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 9 | 153 | $0.00 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 5 | 1 | 2 | 655 | 0 | 18961 | 0.05 |
| red | 6 | 2 | 0 | 0 | 547 | 168 | 43 | 82 | 16539 | 924452 | 142883 | 0.90 |
| green | 4 | 2 | 0 | 0 | 849 | 74 | 24 | 42 | 5495 | 358374 | 70737 | 0.27 |
| refactor | 2 | 0 | 0 | 0 | 22 | 17 | 6 | 12 | 771 | 82120 | 34284 | 0.10 |
| rebase | 3 | 1 | 0 | 0 | 1594 | 73 | 20 | 34 | 6461 | 261932 | 83625 | 0.42 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 2018 | 74 | 21 | 40 | 5827 | 266481 | 118325 | 0.38 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 662 | 200 | 51 | 94 | 19790 | 1045928 | 158560 | 1.10 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 344 | 63 | 22 | 38 | 4304 | 314469 | 73605 | 0.26 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| add-ledger-step.sh adds a new step whose prose mentions the skill-edit marker (with a backticked path in its prose) but does not carry it in its trailing tag run as a plain step, exiting 0, with no unit or requirements-list lookup ⟦criterion 1⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 158 | 43 | 86 | 13716 | 934174 | 140606 | 0.78 | 1214 | 1/2 | 0/5 | nothing-left |  |  | full |
| add-ledger-step.sh refuses a new step carrying the skill-edit marker as its trailing tag whose unit file does not exist with exit 2 and a stderr message naming the unit, with no Python exception text (the case must go red when the missing-unit guard is removed and the missing file raises again) ⟦criterion 2⟧ | 9 | 3 | 0 | 0 | 0 | 0 | 174 | 50 | 84 | 15550 | 692704 | 190923 | 0.90 | 587 | red 1/2, rebase 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| add-ledger-step.sh adds a new step whose prose mentions the skill-edit marker (with a backticked path in its prose) but does not carry it in its trailing tag run as a plain step, exiting 0, with no unit or requirements-list lookup ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.06 |
| add-ledger-step.sh refuses a new step carrying the skill-edit marker as its trailing tag whose unit file does not exist with exit 2 and a stderr message naming the unit, with no Python exception text (the case must go red when the missing-unit guard is removed and the missing file raises again) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| add-ledger-step.sh adds a new step whose prose mentions the skill-edit marker (with a backticked path in its prose) but does not carry it in its trailing tag run as a plain step, exiting 0, with no unit or requirements-list lookup ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| add-ledger-step.sh refuses a new step carrying the skill-edit marker as its trailing tag whose unit file does not exist with exit 2 and a stderr message naming the unit, with no Python exception text (the case must go red when the missing-unit guard is removed and the missing file raises again) ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 3 | ? | ? | nothing-left 2, nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 9 | 8 | 12 | 15 | 6 | 11 | 5 | 6 | 4 | 4 | 3 | 10 |
| fast | 96 | 77 | 144 | 61 | 88 | 102 |  |  |  |  |  |  |
| target | 11 | 5 | 4 | 6 | 3 | 3 |  |  |  |  |  |  |
| all | 116 | 109 | 1161 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 94 | 172 | 29921 | 1626878 | 350490 | 4.69 (estimate) |
