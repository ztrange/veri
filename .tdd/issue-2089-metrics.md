### 📊 Metrics — issue 2089

Wall time for the issue: 955 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run bailed — no-verdict, a system failure.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.03 over 44 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86036 |
| 2 | $0.03 | 87042 |
| 3 | $0.03 | 89003 |
| 4 | $0.02 | 89363 |
| 5 | $0.02 | 89770 |
| 6 | $0.02 | 90073 |
| 7 | $0.02 | 90381 |
| 8 | $0.02 | 90940 |
| 9 | $0.02 | 91371 |
| 10 | $0.02 | 91772 |
| 11 | $0.02 | 92364 |
| 12 | $0.03 | 93269 |
| 13 | $0.03 | 94392 |
| 14 | $0.03 | 95536 |
| 15 | $0.06 | 101019 |
| 16 | $0.04 | 103830 |
| 17 | $0.08 | 111674 |
| 18 | $0.04 | 114451 |
| 19 | $0.04 | 116055 |
| 20 | $0.03 | 116364 |
| 21 | $0.03 | 117175 |
| 22 | $0.03 | 117763 |
| 23 | $0.03 | 118358 |
| 24 | $0.03 | 118948 |
| 25 | $0.07 | 125229 |
| 26 | $0.03 | 125956 |
| 27 | $0.03 | 126786 |
| 28 | $0.04 | 128269 |
| 29 | $0.03 | 129010 |
| 30 | $0.03 | 129836 |
| 31 | $0.03 | 130564 |
| 32 | $0.03 | 131655 |
| 33 | $0.03 | 132293 |
| 34 | $0.03 | 132666 |
| 35 | $0.03 | 133318 |
| 36 | $0.03 | 134172 |
| 37 | $0.03 | 134932 |
| 38 | $0.05 | 137446 |
| 39 | $0.03 | 138117 |
| 40 | $0.03 | 138675 |
| 41 | $0.03 | 139182 |
| 42 | $0.04 | 140426 |
| 43 | $0.04 | 141634 |
| 44 | $0.06 | 145474 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 3 | 6 | 1192 | 61988 | 31891 | 0.10 |
| diff | 4 | 2 | 0 | 0 | 337 | 49 | 17 | 34 | 4952 | 427534 | 67401 | 0.26 |
| prose | 2 | 0 | 0 | 0 | 74 | 63 | 2 | 4 | 9305 | 2217 | 144618 | 0.45 |
| red | 1 | 0 | 0 | 0 | 273 | 50 | 15 | 28 | 6715 | 537382 | 29717 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 113 | 33 | 10 | 20 | 3525 | 235571 | 55535 | 0.20 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 512 | 77 | 25 | 48 | 9334 | 791333 | 73474 | 0.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 273 | 0.20 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `skills/tdd/SKILL.md`'s *Draft PR* regrade code block exits with the highest code any unit's `grade-prose.sh` call returned, in place of `|| rc=1`: units returning 2 and 1, in either order, make the block exit 2; units returning 1 and 0 make it exit 1; all 0 exits 0; it still grades every unit the run signed and still reads each `grade-prose.sh` call's stdin from `/dev/null`; the existing cases `test_1871_draft_pr_regrades_every_signed_unit_on_the_rebased_tip_with_grade_prose_sh_and_repairs_a_reject_like_a_red_full_suite` and the `test_2037_…` regrade-block cases in `skills/tdd/scripts/tests/py/test_grade_prose_process.py` still pass; the unit is regraded by the later skill-edit step, so this step adds no test and does not touch `GRADED` ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 8 | 16 | 2447 | 185391 | 40998 | 0.15 | 181 | n/a | n/a | n/a |  |  | full |
| `skills/tdd/SKILL.md`'s *Draft PR* prose beside the regrade block says that a regrade exit 2 (no verdict could be obtained) is a system-failure bail with cause `no-verdict` (see `<base directory>/BAIL.md`), never a repair step, and that exit 1 (a REJECT) appends the repair step as today; the existing Draft PR cases in `skills/tdd/scripts/tests/py/unit/test_skill_draft_pr.py` still pass; this step adds no test and does not touch `GRADED` ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 9 | 18 | 2505 | 242143 | 26403 | 0.12 | 280 | n/a | n/a | n/a |  |  | full |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` grades the edited `skills/tdd/SKILL.md` against its requirements list and signs it in `GRADED`, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 32 | 1 | 2 | 4857 | 649 | 72765 | 0.23 | 53 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` grades the edited `skills/tdd/SKILL.md` against its requirements list and signs it in `GRADED`, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 31 | 1 | 2 | 4448 | 1568 | 71853 | 0.22 | 50 | unknown | unknown | unknown |  |  | full |
| A parametrized case in `skills/tdd/scripts/tests/py/test_grade_prose_process.py` extracts the regrade code block from `skills/tdd/SKILL.md`'s *Draft PR* section and runs it as written (only `$S` and the angle-bracket placeholders filled in) in a temporary git repository whose branch signed two units since its base (two `GRADED` lines added, each unit with its sibling `REQUIREMENTS.md`), with the grader replaced by a stub `claude` (`CLAUDE_BIN`) whose answer per unit makes `grade-prose.sh` exit 2 (an answer no verdict can be read from), 1 (REJECT) or 0 (PASS), and asserts the block's exit code: (2,1) → 2, (1,2) → 2, (1,0) → 1, (0,0) → 0; the text already holds after the first step, so this step's Red reports that the case already passes and it takes the pin route; a process case (`@pytest.mark.process`), no production change ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 50 | 15 | 28 | 6715 | 537382 | 29717 | 0.20 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 18 | 17 | 16 |  |  |  |  |  |
| affected | 22 | 146 | 7 | 29 | 25 | 17 | 13 | 13 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 37 | 72 | 22164 | 1029121 | 273627 | 1.01 |
