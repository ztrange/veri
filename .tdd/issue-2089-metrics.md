### 📊 Metrics — issue 2089

Wall time for the issue: 930 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2105.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.34 over 101 turns, in 3 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 86036 |
| 2 | $0.04 | 87042 |
| 3 | $0.04 | 89003 |
| 4 | $0.03 | 89363 |
| 5 | $0.03 | 89770 |
| 6 | $0.03 | 90073 |
| 7 | $0.04 | 90381 |
| 8 | $0.03 | 90940 |
| 9 | $0.03 | 91371 |
| 10 | $0.03 | 91772 |
| 11 | $0.04 | 92364 |
| 12 | $0.03 | 93269 |
| 13 | $0.04 | 94392 |
| 14 | $0.04 | 95536 |
| 15 | $0.07 | 101019 |
| 16 | $0.05 | 103830 |
| 17 | $0.10 | 111674 |
| 18 | $0.05 | 114451 |
| 19 | $0.05 | 116055 |
| 20 | $0.04 | 116364 |
| 21 | $0.04 | 117175 |
| 22 | $0.03 | 117763 |
| 23 | $0.04 | 118358 |
| 24 | $0.04 | 118948 |
| 25 | $0.09 | 125229 |
| 26 | $0.04 | 125956 |
| 27 | $0.04 | 126786 |
| 28 | $0.05 | 128269 |
| 29 | $0.04 | 129010 |
| 30 | $0.04 | 129836 |
| 31 | $0.04 | 130564 |
| 32 | $0.05 | 131655 |
| 33 | $0.04 | 132293 |
| 34 | $0.04 | 132666 |
| 35 | $0.04 | 133318 |
| 36 | $0.05 | 134172 |
| 37 | $0.04 | 134932 |
| 38 | $0.06 | 137446 |
| 39 | $0.04 | 138117 |
| 40 | $0.04 | 138675 |
| 41 | $0.04 | 139182 |
| 42 | $0.05 | 140426 |
| 43 | $0.05 | 141634 |
| 44 | $0.07 | 145474 |
| 45 | $0.05 | 146263 |
| 46 | $0.04 | 147220 |
| 47 | $0.56 | 86022 |
| 48 | $0.03 | 86365 |
| 49 | $0.03 | 87162 |
| 50 | $0.03 | 87613 |
| 51 | $0.04 | 89854 |
| 52 | $0.03 | 90701 |
| 53 | $0.04 | 91997 |
| 54 | $0.03 | 92363 |
| 55 | $0.03 | 92681 |
| 56 | $0.03 | 93173 |
| 57 | $0.04 | 95187 |
| 58 | $0.03 | 95707 |
| 59 | $0.03 | 95975 |
| 60 | $0.03 | 96681 |
| 61 | $0.03 | 97256 |
| 62 | $0.04 | 98906 |
| 63 | $0.04 | 99712 |
| 64 | $0.55 | 86056 |
| 65 | $0.03 | 87293 |
| 66 | $0.03 | 89186 |
| 67 | $0.05 | 92827 |
| 68 | $0.06 | 97525 |
| 69 | $0.06 | 102356 |
| 70 | $0.02 | 102692 |
| 71 | $0.03 | 103503 |
| 72 | $0.03 | 104552 |
| 73 | $0.02 | 104915 |
| 74 | $0.02 | 105389 |
| 75 | $0.02 | 105680 |
| 76 | $0.02 | 105983 |
| 77 | $0.02 | 106437 |
| 78 | $0.02 | 106821 |
| 79 | $0.03 | 107543 |
| 80 | $0.05 | 110756 |
| 81 | $0.03 | 111131 |
| 82 | $0.03 | 111913 |
| 83 | $0.03 | 112554 |
| 84 | $0.02 | 112828 |
| 85 | $0.03 | 114241 |
| 86 | $0.03 | 115211 |
| 87 | $0.04 | 117755 |
| 88 | $0.03 | 118281 |
| 89 | $0.03 | 118670 |
| 90 | $0.03 | 119092 |
| 91 | $0.03 | 119578 |
| 92 | $0.03 | 120414 |
| 93 | $0.03 | 120795 |
| 94 | $0.03 | 121188 |
| 95 | $0.03 | 121545 |
| 96 | $0.03 | 121907 |
| 97 | $0.03 | 122366 |
| 98 | $0.03 | 122866 |
| 99 | $0.03 | 123262 |
| 100 | $0.03 | 123617 |
| 101 | $0.03 | 123999 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 3 | 6 | 1192 | 61988 | 31891 | 0.10 |
| diff | 4 | 2 | 0 | 0 | 337 | 49 | 17 | 34 | 4952 | 427534 | 67401 | 0.26 |
| prose | 3 | 0 | 0 | 0 | 115 | 101 | 3 | 6 | 14509 | 2866 | 217361 | 0.69 |
| red | 2 | 0 | 0 | 0 | 355 | 79 | 21 | 40 | 10457 | 724552 | 74730 | 0.36 |
| pin | 1 | 1 | 0 | 0 | 46 | 11 | 3 | 6 | 896 | 57819 | 30866 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 159 | 44 | 13 | 26 | 4421 | 293390 | 86401 | 0.29 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 594 | 106 | 31 | 60 | 13076 | 978503 | 118487 | 0.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `skills/tdd/SKILL.md`'s *Draft PR* regrade code block exits with the highest code any unit's `grade-prose.sh` call returned, in place of `|| rc=1`: units returning 2 and 1, in either order, make the block exit 2; units returning 1 and 0 make it exit 1; all 0 exits 0; it still grades every unit the run signed and still reads each `grade-prose.sh` call's stdin from `/dev/null`; the existing cases `test_1871_draft_pr_regrades_every_signed_unit_on_the_rebased_tip_with_grade_prose_sh_and_repairs_a_reject_like_a_red_full_suite` and the `test_2037_…` regrade-block cases in `skills/tdd/scripts/tests/py/test_grade_prose_process.py` still pass; the unit is regraded by the later skill-edit step, so this step adds no test and does not touch `GRADED` ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 8 | 16 | 2447 | 185391 | 40998 | 0.15 | 181 | n/a | n/a | n/a |  |  | full |
| `skills/tdd/SKILL.md`'s *Draft PR* prose beside the regrade block says that a regrade exit 2 (no verdict could be obtained) is a system-failure bail with cause `no-verdict` (see `<base directory>/BAIL.md`), never a repair step, and that exit 1 (a REJECT) appends the repair step as today; the existing Draft PR cases in `skills/tdd/scripts/tests/py/unit/test_skill_draft_pr.py` still pass; this step adds no test and does not touch `GRADED` ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 9 | 18 | 2505 | 242143 | 26403 | 0.12 | 280 | n/a | n/a | n/a |  |  | full |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` grades the edited `skills/tdd/SKILL.md` against its requirements list and signs it in `GRADED`, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 32 | 1 | 2 | 4857 | 649 | 72765 | 0.23 | 53 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` grades the edited `skills/tdd/SKILL.md` against its requirements list and signs it in `GRADED`, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 31 | 1 | 2 | 4448 | 1568 | 71853 | 0.22 | 50 | unknown | unknown | unknown |  |  | full |
| A parametrized case in `skills/tdd/scripts/tests/py/test_grade_prose_process.py` extracts the regrade code block from `skills/tdd/SKILL.md`'s *Draft PR* section and runs it as written (only `$S` and the angle-bracket placeholders filled in) in a temporary git repository whose branch signed two units since its base (two `GRADED` lines added, each unit with its sibling `REQUIREMENTS.md`), with the grader replaced by a stub `claude` (`CLAUDE_BIN`) whose answer per unit makes `grade-prose.sh` exit 2 (an answer no verdict can be read from), 1 (REJECT) or 0 (PASS), and asserts the block's exit code: (2,1) → 2, (1,2) → 2, (1,0) → 1, (0,0) → 0; the text already holds after the first step, so this step's Red reports that the case already passes and it takes the pin route; a process case (`@pytest.mark.process`), no production change ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 90 | 24 | 46 | 11353 | 782371 | 105596 | 0.46 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 18 | 17 | 16 |  |  |  |  |  |  |
| affected | 22 | 146 | 7 | 29 | 25 | 17 | 13 | 13 | 24 |
| target | 15 | 16 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 47 | 92 | 32006 | 1274759 | 422249 | 1.50 |
