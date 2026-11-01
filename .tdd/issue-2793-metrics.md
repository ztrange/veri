### 📊 Metrics — issue 2793

Wall time for the issue: 2724 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 22 of 24 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2796.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.39 over 35 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87303 tokens, largest 175007 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.70 | 87303 |
| 2 | $0.09 | 96537 |
| 3 | $0.03 | 98401 |
| 4 | $0.07 | 104517 |
| 5 | $0.03 | 105305 |
| 6 | $0.02 | 105678 |
| 7 | $0.02 | 105995 |
| 8 | $0.06 | 110917 |
| 9 | $0.18 | 130082 |
| 10 | $0.05 | 133601 |
| 11 | $0.04 | 135846 |
| 12 | $0.04 | 138024 |
| 13 | $0.05 | 140501 |
| 14 | $0.07 | 145718 |
| 15 | $0.04 | 146702 |
| 16 | $0.04 | 147538 |
| 17 | $0.07 | 152208 |
| 18 | $0.04 | 153847 |
| 19 | $0.05 | 155786 |
| 20 | $0.06 | 159650 |
| 21 | $0.05 | 162041 |
| 22 | $0.04 | 162567 |
| 23 | $0.04 | 163208 |
| 24 | $0.05 | 165546 |
| 25 | $0.04 | 166495 |
| 26 | $0.04 | 167196 |
| 27 | $0.04 | 167995 |
| 28 | $0.04 | 169186 |
| 29 | $0.04 | 169653 |
| 30 | $0.04 | 169905 |
| 31 | $0.04 | 170125 |
| 32 | $0.04 | 170485 |
| 33 | $0.05 | 172453 |
| 34 | $0.04 | 173742 |
| 35 | $0.04 | 175007 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 12 | 1 | 2 | 1416 | 0 | 35172 | 0.10 |
| diff | 2 | 1 | 0 | 0 | 236 | 51 | 16 | 32 | 6586 | 507665 | 65526 | 0.28 |
| prose | 28 | 0 | 0 | 0 | 454 | 333 | 28 | 56 | 54081 | 40714 | 385854 | 1.51 |
| red | 7 | 0 | 0 | 0 | 217 | 143 | 40 | 80 | 16744 | 1288634 | 162367 | 0.70 |
| pin | 7 | 7 | 0 | 0 | 159 | 73 | 27 | 50 | 8694 | 671889 | 129558 | 0.48 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 9 | 0 | 0 | 291 | 110 | 35 | 66 | 13414 | 903736 | 191702 | 0.70 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 335 | 169 | 49 | 98 | 20026 | 1564452 | 200921 | 0.86 |

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
| All of the mechanical rename in one commit: each of the 12 skills/veri-<name>/ directories git-moved to skills/v<name>/ (skills/tdd/ untouched), frontmatter name: v<name>, every long name substituted to its short name by that substitution only (requirement rows included) in README.md, REQUIREMENTS.md, operator/PRINCIPLES.md, operator/REQUIREMENTS.md, skills/tdd/SCRIPTS.md, skills/tdd/REQUIREMENTS.md, the renamed skills' own files and .on-demand files, and the ten named test files with their assertions otherwise unchanged; skills/tdd/scripts/tests/py/unit/test_grade_prose.py's glob and its tree_audit reason become skills/v*/GRADED; each GRADED line carries its new path with its old signature, the regrade being the later steps' work; specs/, .tdd/, veri-planted in test_conftest_guards.py, tmpdir prefixes and ~/.veri-* paths stay. Expected and allowed red at this step, and only until the regrade steps below re-sign their units: exactly the three cases of test_prd_015_prose_signed.py asserting skills/vplan/SKILL.md, skills/vfile/SKILL.md and README.md are not owed, whose copied tree carries no ledger so no waiver reaches them; any other red case is a real red ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 16 | 32 | 6586 | 507665 | 65526 | 0.28 | 310 | n/a | n/a | n/a |  |  | full |
| A case in skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py: each of the 12 skills lives in skills/v<name>/ with frontmatter name: v<name>, and no skills/veri-<name>/ directory remains (a pin, no production change) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 10 | 18 | 3043 | 233383 | 68235 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| A case in test_prd_016_short_names.py: skills/tdd/ exists and its SKILL.md frontmatter name is still tdd (a pin, no production change) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 18 | 7 | 14 | 2354 | 195734 | 31384 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| A case in skills/tdd/scripts/tests/py/test_prd_016_tracked_names_process.py, carrying a process mark for git: no tracked file outside specs/ and .tdd/ contains veri- followed by a renamed skill's name and then no word character, so veri-planted is no hit; the test builds its pattern at run time so its own source does not match (a pin, no production change) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 13 | 24 | 4980 | 379030 | 38065 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| A second case in test_prd_016_tracked_names_process.py, for its own go-red: the same sweep, run on a temporary git repo in tmp_path where one tracked file holds such a reference, reports that file, and a file under specs/ holding one is not reported (a pin, no production change) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 7 | 14 | 3433 | 198613 | 33765 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| A case in test_prd_016_short_names.py, in the shape of test_prd_015_prose_signed.py: each of the 11 renamed units with a requirements list (vjudge has none) has a GRADED line under its new path whose signature equals grade_prose.signature of its current text and rows (a pin, no production change) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 11 | 22 | 4334 | 374729 | 47710 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| A case in test_prd_016_short_names.py: prose-owed.sh, run on a copy of the tip carrying no ledger so no waiver applies, reports no unit owed and no orphan GRADED line, README.md, operator/PRINCIPLES.md and skills/tdd/SCRIPTS.md included (a pin, no production change) ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 12 | 24 | 4294 | 381334 | 38844 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| test_every_committed_graded_line_names_the_grader_template_it_was_signed_under_2474 in test_grade_prose.py reads the renamed skills' GRADED files and fails when its skills/v*/GRADED glob matches none of them, its existing assertion kept and the case not renamed (a test-only pin, no production change) ⟦criterion 8⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 7 | 14 | 3000 | 197700 | 33922 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 60 | 3 | 2 | 4 | 3 | 4 | 3 | 4 | 3 |  |  |  |  |  |
| target | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 5 | 3 | 4 | 4 | 3 | 5 | 4 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 112 | 220 | 87521 | 2508902 | 778477 | 5.47 (estimate) |
