### 📊 Metrics — issue 2684

Wall time for the issue: 1903 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2795.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.65 over 27 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87279 tokens, largest 144365 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87279 |
| 2 | $0.07 | 94282 |
| 3 | $0.07 | 100981 |
| 4 | $0.04 | 103112 |
| 5 | $0.02 | 103612 |
| 6 | $0.02 | 104054 |
| 7 | $0.02 | 104356 |
| 8 | $0.02 | 104673 |
| 9 | $0.06 | 109117 |
| 10 | $0.07 | 114800 |
| 11 | $0.06 | 119380 |
| 12 | $0.05 | 122035 |
| 13 | $0.03 | 122613 |
| 14 | $0.03 | 123327 |
| 15 | $0.04 | 124779 |
| 16 | $0.06 | 129083 |
| 17 | $0.04 | 130652 |
| 18 | $0.07 | 135649 |
| 19 | $0.03 | 136471 |
| 20 | $0.04 | 138680 |
| 21 | $0.04 | 140124 |
| 22 | $0.03 | 140522 |
| 23 | $0.03 | 140767 |
| 24 | $0.03 | 141204 |
| 25 | $0.03 | 141840 |
| 26 | $0.04 | 143674 |
| 27 | $0.03 | 144365 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1134 | 0 | 38457 | 0.11 |
| prose | 8 | 0 | 0 | 0 | 79 | 43 | 8 | 16 | 6938 | 10568 | 72798 | 0.25 |
| red | 2 | 0 | 0 | 0 | 62 | 33 | 10 | 18 | 4577 | 294522 | 66695 | 0.24 |
| pin | 2 | 2 | 0 | 0 | 51 | 25 | 8 | 16 | 2519 | 254611 | 43709 | 0.16 |
| diff | 2 | 1 | 0 | 0 | 132 | 30 | 14 | 28 | 3119 | 498334 | 44991 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 139 | 48 | 14 | 28 | 5196 | 417129 | 102866 | 0.35 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 117 | 49 | 19 | 36 | 6153 | 630338 | 90986 | 0.35 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-edit step for the unit `skills/tdd/scripts/prompts/verify-contract-a.md`: `skill-edit-step.sh` adds the issue's pre-approved rows VA1–VA6, exactly as the issue's table gives them, to `skills/tdd/scripts/prompts/REQUIREMENTS.md` under `## skills/tdd/scripts/prompts/verify-contract-a.md` (appending after the sections already there), rewriting no other unit's rows; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/tdd/GRADED` with a line whose signature matches its current text, so `skills/tdd/scripts/prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 6 | 1 | 2 | 894 | 649 | 9708 | 0.03 | 27 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/scripts/prompts/verify-contract-b.md`: `skill-edit-step.sh` adds the issue's pre-approved rows VK1–VK6, exactly as the issue's table gives them, to `skills/tdd/scripts/prompts/REQUIREMENTS.md` under `## skills/tdd/scripts/prompts/verify-contract-b.md` (appending after the sections already there), rewriting no other unit's rows; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/tdd/GRADED` with a line whose signature matches its current text, so `skills/tdd/scripts/prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 4 | 1 | 2 | 597 | 1545 | 8816 | 0.03 | 17 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/scripts/prompts/verify-expand.md`: `skill-edit-step.sh` adds the issue's pre-approved rows VE1–VE7, exactly as the issue's table gives them, to `skills/tdd/scripts/prompts/REQUIREMENTS.md` under `## skills/tdd/scripts/prompts/verify-expand.md` (appending after the sections already there), rewriting no other unit's rows; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/tdd/GRADED` with a line whose signature matches its current text, so `skills/tdd/scripts/prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 6 | 1 | 2 | 1016 | 1545 | 8966 | 0.03 | 19 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/scripts/prompts/verify-migrate.md`: `skill-edit-step.sh` adds the issue's pre-approved rows VM1–VM7, exactly as the issue's table gives them, to `skills/tdd/scripts/prompts/REQUIREMENTS.md` under `## skills/tdd/scripts/prompts/verify-migrate.md` (appending after the sections already there), rewriting no other unit's rows; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/tdd/GRADED` with a line whose signature matches its current text, so `skills/tdd/scripts/prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 5 | 1 | 2 | 896 | 1545 | 8935 | 0.03 | 16 | unknown | unknown | unknown |  |  | full |
| Once all four units are signed, a case in `skills/tdd/scripts/tests/py/test_prose_owed_process.py` (process-marked and tree_audit-marked, like `test_2682_the_six_verify_fragment_units_are_listed_signed_and_owe_no_grade` beside it) asserts that `skills/tdd/GRADED` carries a line for each of `verify-contract-a.md`, `verify-contract-b.md`, `verify-expand.md` and `verify-migrate.md` (all under `skills/tdd/scripts/prompts/`), that `skills/tdd/scripts/prompts/REQUIREMENTS.md` holds a `## skills/tdd/scripts/prompts/<file>` heading for each, and that `prose-owed.sh` run on the repository prints nothing, exiting 0; no production change (pin: already holds) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 8 | 14 | 3404 | 208273 | 63783 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| In `skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py`, `test_main_renders_an_expand_and_a_migrate_verify_prompt_stating_what_each_phase_changes_and_that_test_files_stay_frozen` and `test_main_renders_a_contract_a_and_a_contract_b_verify_prompt_stating_production_frozen_then_the_proxy_deleted_and_test_files_frozen` are deleted whole, and nothing else in that file changes save an import only they used; every case the issue lists under *Cases that stay* is untouched, and what still reads the four units asserts only mechanical facts (argument refusals, accepted phase names, the `{{LAST_PHASE_CHECK}}` selection, the affected run's command line); test-only, no production change and no prose edit, and the affected suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 14 | 28 | 3119 | 498334 | 44991 | 0.19 | 214 | n/a | n/a | n/a |  |  | full |
| A case in `skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py` pins what the deletion leaves: rendering each of the `expand`, `migrate`, `contract-a` and `contract-b` verify prompts through `build_verify_prompt.main` exits 0 with an empty stderr, and each render carries its own phase heading `## Phase: verify-<phase>`, the one mechanical fact of which template each phase selects; the case holds no regex over the templates' prose; no production change (pin: already holds) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 10 | 20 | 3692 | 340860 | 46621 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 4 | 4 | 21 | 7 |
| target | 3 | 5 | 4 | 4 |
| fast | 30 | 36 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 41 | 80 | 18287 | 1058035 | 266650 | 2.61 (estimate) |
