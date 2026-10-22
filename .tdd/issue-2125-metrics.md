### 📊 Metrics — issue 2125

Wall time for the issue: 5487 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run bailed — ci-timeout, a system failure.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.56 over 84 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86197 |
| 2 | $0.02 | 86612 |
| 3 | $0.02 | 87480 |
| 4 | $0.03 | 89608 |
| 5 | $0.02 | 89904 |
| 6 | $0.02 | 90295 |
| 7 | $0.02 | 90643 |
| 8 | $0.02 | 90985 |
| 9 | $0.02 | 91564 |
| 10 | $0.02 | 91914 |
| 11 | $0.03 | 93319 |
| 12 | $0.09 | 102753 |
| 13 | $0.04 | 104901 |
| 14 | $0.03 | 106167 |
| 15 | $0.03 | 107002 |
| 16 | $0.03 | 107632 |
| 17 | $0.04 | 109640 |
| 18 | $0.03 | 111072 |
| 19 | $0.03 | 111501 |
| 20 | $0.03 | 112072 |
| 21 | $0.03 | 112680 |
| 22 | $0.03 | 113786 |
| 23 | $0.04 | 115434 |
| 24 | $0.03 | 116488 |
| 25 | $0.14 | 130748 |
| 26 | $0.03 | 131176 |
| 27 | $0.03 | 131861 |
| 28 | $0.03 | 132905 |
| 29 | $0.03 | 133685 |
| 30 | $0.03 | 134328 |
| 31 | $0.03 | 135014 |
| 32 | $0.03 | 135677 |
| 33 | $0.03 | 136061 |
| 34 | $0.03 | 136936 |
| 35 | $0.03 | 137168 |
| 36 | $0.04 | 138126 |
| 37 | $0.04 | 139161 |
| 38 | $0.03 | 139706 |
| 39 | $0.05 | 142132 |
| 40 | $0.03 | 142832 |
| 41 | $0.04 | 143636 |
| 42 | $0.03 | 144271 |
| 43 | $0.03 | 144517 |
| 44 | $0.03 | 145252 |
| 45 | $0.04 | 146845 |
| 46 | $0.03 | 147321 |
| 47 | $0.04 | 149051 |
| 48 | $0.03 | 149344 |
| 49 | $0.04 | 150883 |
| 50 | $0.03 | 151235 |
| 51 | $0.04 | 152039 |
| 52 | $0.03 | 152399 |
| 53 | $0.03 | 152824 |
| 54 | $0.03 | 153088 |
| 55 | $0.03 | 153401 |
| 56 | $0.03 | 153692 |
| 57 | $0.04 | 154418 |
| 58 | $0.04 | 155061 |
| 59 | $0.03 | 155376 |
| 60 | $0.03 | 155717 |
| 61 | $0.03 | 155987 |
| 62 | $0.04 | 156574 |
| 63 | $0.04 | 157332 |
| 64 | $0.04 | 158137 |
| 65 | $0.05 | 160079 |
| 66 | $0.03 | 160399 |
| 67 | $0.04 | 160838 |
| 68 | $0.04 | 161477 |
| 69 | $0.04 | 162590 |
| 70 | $0.04 | 163620 |
| 71 | $0.04 | 164423 |
| 72 | $0.04 | 165018 |
| 73 | $0.04 | 165785 |
| 74 | $0.04 | 166261 |
| 75 | $0.04 | 166556 |
| 76 | $0.04 | 167141 |
| 77 | $0.04 | 167599 |
| 78 | $0.04 | 168065 |
| 79 | $0.04 | 168456 |
| 80 | $0.04 | 169044 |
| 81 | $0.04 | 169576 |
| 82 | $0.04 | 170023 |
| 83 | $0.04 | 170376 |
| 84 | $0.06 | 173969 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 14 | 3 | 6 | 1501 | 62423 | 33674 | 0.11 |
| red | 11 | 4 | 0 | 0 | 1619 | 240 | 56 | 110 | 22826 | 1604933 | 259140 | 1.04 |
| green | 8 | 4 | 0 | 0 | 609 | 150 | 43 | 84 | 12388 | 1216247 | 129468 | 0.57 |
| refactor | 8 | 4 | 0 | 0 | 272 | 77 | 25 | 50 | 4757 | 640730 | 105217 | 0.37 |
| pin | 3 | 3 | 0 | 0 | 148 | 61 | 13 | 26 | 3786 | 327874 | 58283 | 0.22 |
| prose | 4 | 0 | 0 | 0 | 254 | 238 | 4 | 8 | 38538 | 4434 | 351193 | 1.26 |
| skill-edit | 1 | 0 | 0 | 0 | 22 | 17 | 6 | 10 | 2135 | 446976 | 93595 | 0.30 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 16 | 0 | 0 | 792 | 249 | 59 | 116 | 17767 | 1462533 | 278262 | 1.02 |
| developer | claude-sonnet-5-5 | 15 | 0 | 0 | 0 | 1876 | 293 | 81 | 160 | 27491 | 2389674 | 307520 | 1.28 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `tests-frozen.sh check-earlier <ledger> --step "<current step>"` exits 1 and prints one line per changed case, naming the case and the earlier ledger step whose frozen record (`tests-frozen.sh path` over that step's text) holds it, when the body of a case that earlier step recorded has changed since its record; `record --step` keeps what it needs per recorded case to tell its body changed, and existing readers of the record's `case: <name>` lines (`wrong-test-route.sh`) keep reading the same case names ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 95 | 29 | 58 | 9553 | 849863 | 120463 | 0.48 | 395 | unknown | 1/5 | nothing-left |  |  | full |
| `tests-frozen.sh check-earlier` exits 1 naming the case and its earlier step when a case an earlier step recorded has been deleted, whether the case alone was removed from its file or its whole test file was deleted ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 13 | 26 | 4860 | 390225 | 34630 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| `tests-frozen.sh check-earlier` exits 0 printing nothing when the current step only adds new cases to a test file an earlier step's cases live in, leaving those earlier cases byte-identical, and skips an earlier ledger step that has no frozen record on disk (a `⟦diff-checked⟧`, pin or repair step) rather than refusing ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 10 | 20 | 3919 | 285218 | 32518 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `tests-frozen.sh check-earlier … --except <case>` (repeatable) exempts each case named, the case a `red-contradicted`, `red-supersede` or `repair` route names, so a change to it is not printed while a changed earlier case not named still exits 1 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 96 | 25 | 50 | 6758 | 684866 | 88194 | 0.36 | 405 | unknown | 0/5 | nothing-left |  |  | full |
| `tests-frozen.sh check-earlier` exempts, without `--except`, the cases the current step's own text names when it is a `⟦replaces-case⟧` step, and the cases in the fixture file the current step names when it is a `⟦fixture-repair⟧` step, while still naming a changed earlier case outside them ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 1 | 0 | 99 | 27 | 50 | 7457 | 673499 | 131168 | 0.47 | 1456 | unknown | 0/5 | nothing-left |  |  | full |
| `tests-frozen.sh check-earlier` with a missing ledger argument or missing `--step`, or an unreadable ledger, prints its usage on stderr and exits 2, and the script's usage header and its `SCRIPTS.md` entry name the `check-earlier` mode ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 102 | 27 | 54 | 8551 | 766500 | 97025 | 0.40 | 337 | unknown | 0/5 | nothing-left |  |  | full |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` adds FZ1 to `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SKILL.md` exactly as the issue's table states it, states the rule in SKILL.md's prose (the conductor runs `tests-frozen.sh check-earlier` before each verify-red and verify-green launch, a changed or deleted earlier case is a REJECT naming the case and its step, route-named cases exempt), grades `skills/tdd/SKILL.md` PASS against its whole list and signs it in `GRADED`, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 2⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 139 | 8 | 14 | 22725 | 449193 | 269029 | 0.94 | 172 | unknown | unknown | unknown |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_skill_tests_frozen.py — FAILED test_every_tests_frozen_record_and_check_names_the_record_by_path_over_the_step_text_and_red_defines_the_key - AssertionError: SKILL.md:917 runs record or check without --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" (the new `tests-frozen.sh check-earlier` line is read as a `check` line) ⟦suite-repair⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 6 | 12 | 2659 | 139613 | 48110 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `tests-frozen.sh check-earlier <ledger> --step "<current step>"` exits 1 and prints one line per changed case, naming the case and the earlier ledger step whose frozen record (`tests-frozen.sh path` over that step's text) holds it, when the body of a case that earlier step recorded has changed since its record; `record --step` keeps what it needs per recorded case to tell its body changed, and existing readers of the record's `case: <name>` lines (`wrong-test-route.sh`) keep reading the same case names ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 80 | 0.11 |
| `tests-frozen.sh check-earlier … --except <case>` (repeatable) exempts each case named, the case a `red-contradicted`, `red-supersede` or `repair` route names, so a change to it is not printed while a changed earlier case not named still exits 1 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 64 | 0.08 |
| `tests-frozen.sh check-earlier` exempts, without `--except`, the cases the current step's own text names when it is a `⟦replaces-case⟧` step, and the cases in the fixture file the current step names when it is a `⟦fixture-repair⟧` step, while still naming a changed earlier case outside them ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 71 | 0.09 |
| `tests-frozen.sh check-earlier` with a missing ledger argument or missing `--step`, or an unreadable ledger, prints its usage on stderr and exits 2, and the script's usage header and its `SCRIPTS.md` entry name the `check-earlier` mode ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 57 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 16 | 14 | 13 | 15 | 16 | 16 | 14 | 13 | 13 | 13 | 33 | 19 | 15 | 14 | 14 | 13 | 14 | 15 | 11 | 12 | 30 | 13 | 15 | 11 |
| fast | 18 | 22 | 17 | 19 | 25 | 22 | 17 | 17 | 18 | 17 | 17 | 18 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 15 | 12 | 12 | 11 | 12 | 12 | 7 | 13 | 13 | 12 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 150 | 294 | 85931 | 4303617 | 1030570 | 3.87 |
