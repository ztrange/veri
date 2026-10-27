### 📊 Metrics — issue 2498

Wall time for the issue: 2414 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 8 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2540.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.26 over 66 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88985 tokens, largest 185793 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88985 |
| 2 | $0.04 | 91310 |
| 3 | $0.03 | 93282 |
| 4 | $0.02 | 93818 |
| 5 | $0.02 | 94119 |
| 6 | $0.02 | 94768 |
| 7 | $0.02 | 95059 |
| 8 | $0.02 | 95668 |
| 9 | $0.02 | 96208 |
| 10 | $0.05 | 99579 |
| 11 | $0.04 | 102544 |
| 12 | $0.04 | 104545 |
| 13 | $0.07 | 110171 |
| 14 | $0.05 | 113284 |
| 15 | $0.04 | 115413 |
| 16 | $0.04 | 117788 |
| 17 | $0.03 | 118209 |
| 18 | $0.03 | 118874 |
| 19 | $0.03 | 119263 |
| 20 | $0.08 | 125879 |
| 21 | $0.04 | 127580 |
| 22 | $0.03 | 128351 |
| 23 | $0.16 | 144629 |
| 24 | $0.04 | 145500 |
| 25 | $0.04 | 146470 |
| 26 | $0.04 | 148018 |
| 27 | $0.04 | 149120 |
| 28 | $0.04 | 150060 |
| 29 | $0.04 | 150736 |
| 30 | $0.03 | 151041 |
| 31 | $0.04 | 151894 |
| 32 | $0.04 | 152846 |
| 33 | $0.03 | 153265 |
| 34 | $0.04 | 154065 |
| 35 | $0.04 | 154744 |
| 36 | $0.04 | 155923 |
| 37 | $0.04 | 156856 |
| 38 | $0.04 | 157726 |
| 39 | $0.04 | 158757 |
| 40 | $0.04 | 160347 |
| 41 | $0.04 | 161333 |
| 42 | $0.05 | 163046 |
| 43 | $0.04 | 163783 |
| 44 | $0.04 | 165185 |
| 45 | $0.04 | 166377 |
| 46 | $0.04 | 167447 |
| 47 | $0.05 | 169890 |
| 48 | $0.04 | 170975 |
| 49 | $0.04 | 171285 |
| 50 | $0.04 | 172059 |
| 51 | $0.06 | 175107 |
| 52 | $0.04 | 176114 |
| 53 | $0.04 | 177112 |
| 54 | $0.05 | 178463 |
| 55 | $0.05 | 179821 |
| 56 | $0.04 | 180418 |
| 57 | $0.04 | 181163 |
| 58 | $0.04 | 181403 |
| 59 | $0.04 | 181868 |
| 60 | $0.04 | 182944 |
| 61 | $0.04 | 183414 |
| 62 | $0.04 | 184356 |
| 63 | $0.04 | 184592 |
| 64 | $0.04 | 185157 |
| 65 | $0.04 | 185500 |
| 66 | $0.04 | 185793 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 26 | 22 | 2 | 4 | 3056 | 34372 | 33038 | 0.12 |
| red | 6 | 2 | 0 | 0 | 236 | 204 | 41 | 82 | 20048 | 1506514 | 151473 | 0.73 |
| green | 4 | 2 | 0 | 0 | 239 | 93 | 28 | 54 | 8455 | 878390 | 76761 | 0.36 |
| refactor | 2 | 0 | 0 | 0 | 15 | 11 | 7 | 14 | 991 | 208026 | 37117 | 0.12 |
| diff | 6 | 3 | 0 | 0 | 287 | 89 | 29 | 58 | 8041 | 846790 | 97597 | 0.41 |
| pin | 2 | 2 | 0 | 0 | 55 | 42 | 8 | 16 | 2811 | 226962 | 32698 | 0.13 |
| rebase | 2 | 1 | 0 | 0 | 294 | 48 | 13 | 24 | 3457 | 364910 | 35073 | 0.16 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 11 | 1 | 0 | 623 | 191 | 45 | 86 | 16748 | 1198763 | 203965 | 0.80 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 529 | 318 | 83 | 166 | 30111 | 2867201 | 259792 | 1.24 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A fast-tier case (no `process` or `tree_audit` mark) drives `grade_prose` through `run_cli` on a unit with a requirements list, with the new shared leaf-launch wrapper `veri.leaf.launch` replaced in-process by a fake that writes a grader reply (every row PASS, `VERDICT: PASS`) to `.tdd/grade-prose.log` and answers 0; it asserts grade_prose exits 0 and records the PASS verdict (a grader outcome, not a call count). Green adds `skills/tdd/scripts/veri/leaf.py` with the wrapper that builds the `supervise.sh <name> run-leaf.sh <prompt> [args…]` argv and runs it with stdout piped and the caller's environment, and has `grade_prose`'s grader launch call it through the module attribute; no PATH entry, no shim script ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 120 | 33 | 64 | 11833 | 1091286 | 105872 | 0.49 | 324 | unknown | 0/5 | nothing-left |  |  | full |
| Test-only, no production change: every case in `skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py` that fakes the author leaf by replacing `skill_edit_step.subprocess` with a namespace whose `run` matches `cmd[0].endswith("supervise.sh")` instead fakes `subprocess.run` itself in-process (monkeypatch on the `subprocess` module), so the same fake keeps answering once the author launch moves into another module; every case still passes and asserts what it asserted before ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 12 | 24 | 3678 | 378606 | 39738 | 0.17 | 140 | n/a | n/a | n/a |  |  | full |
| A fast-tier case (no `process` or `tree_audit` mark) drives `skill_edit_step`'s author launch through `run_cli` with `veri.leaf.launch` replaced in-process by a fake that edits the unit and answers 0, and asserts the step's outcome — the edited unit graded and the exit code — not a call count. Green has `skill_edit_step._author` launch `author-skill-edit-<attempt>` with `--permission-mode bypassPermissions` through `veri.leaf.launch`, called through the module attribute ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 98 | 24 | 48 | 8399 | 731920 | 98261 | 0.40 | 251 | unknown | 0/5 | nothing-left |  |  | full |
| The wrapper is a seam, not a behaviour change: a small case calling `veri.leaf.launch` with `subprocess.run` replaced in-process observes exactly the argv `[<scripts>/supervise.sh, <leaf name>, <scripts>/run-leaf.sh, <prompt path>, <extra args…>]`, `stdout=subprocess.PIPE` and the environment the caller passed, and gets back the completed process's return code; for the grader that is leaf `grade-prose` with no extra args, for the author `author-skill-edit-<attempt>` with `--permission-mode bypassPermissions` ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 10 | 20 | 3470 | 312834 | 36253 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| Pin step: the #2490 criterion-1 case in `skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py` (`test_a_change_step_on_a_unit_already_graded_pass_grades_the_authors_edit_though_the_up_front_passs_own_graded_write_is_uncommitted_2490`) is rewritten so it no longer fakes `skill_edit_step._grade`: `grade_prose.main` runs for real, only the leaf launches are faked through `veri.leaf.launch` (grader replies written to `.tdd/grade-prose.log`, the author's edit to the unit), and the case observes the `grading` event for the edited unit as well as the tree; it stays in the fast tier (no `process` or `tree_audit` mark) and is expected to pass against the code the earlier steps left (no production change) ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 93 | 17 | 34 | 8603 | 683852 | 57663 | 0.30 | unknown | unknown | unknown | unknown |  |  | pin |
| Neither `skills/tdd/scripts/veri/grade_prose.py` nor `skills/tdd/scripts/veri/skill_edit_step.py` passes `os.path.join(SCRIPTS, "supervise.sh")` to `subprocess.run` or `subprocess.Popen`; each launches its leaf by calling the one shared wrapper, the only place in those two modules' launch path that builds a `supervise.sh` argv; `veri/parallel_conductors.py` and `veri/verify.py` keep their inline calls ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 8 | 16 | 2115 | 218717 | 29325 | 0.12 | 127 | n/a | n/a | n/a |  |  | full |
| A test can make the wrapper answer without starting a process by replacing it in-process: both modules reach it through a module attribute (`leaf.launch`) that `monkeypatch.setattr` replaces, with no PATH entry, no shim script and no process count ⟦diff-checked⟧ ⟦criterion 2⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 73 | 22 | 42 | 5705 | 614377 | 63607 | 0.28 | 129 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A fast-tier case (no `process` or `tree_audit` mark) drives `grade_prose` through `run_cli` on a unit with a requirements list, with the new shared leaf-launch wrapper `veri.leaf.launch` replaced in-process by a fake that writes a grader reply (every row PASS, `VERDICT: PASS`) to `.tdd/grade-prose.log` and answers 0; it asserts grade_prose exits 0 and records the PASS verdict (a grader outcome, not a call count). Green adds `skills/tdd/scripts/veri/leaf.py` with the wrapper that builds the `supervise.sh <name> run-leaf.sh <prompt> [args…]` argv and runs it with stdout piped and the caller's environment, and has `grade_prose`'s grader launch call it through the module attribute; no PATH entry, no shim script ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| A fast-tier case (no `process` or `tree_audit` mark) drives `skill_edit_step`'s author launch through `run_cli` with `veri.leaf.launch` replaced in-process by a fake that edits the unit and answers 0, and asserts the step's outcome — the edited unit graded and the exit code — not a call count. Green has `skill_edit_step._author` launch `author-skill-edit-<attempt>` with `--permission-mode bypassPermissions` through `veri.leaf.launch`, called through the module attribute ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.07 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 20 | 20 | 1 | 2 | 1 | 2 | 17 | 1 | 2 | 2 | 2 | 1 | 29 |
| fast | 17 | 17 | 16 | 17 | 16 | 18 | 17 | 17 |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 2 | 1 | 2 | 1 |  |  |  |  |  |  |  |  |  |
| all | 17 | 17 | 17 | 188 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 128 | 252 | 46859 | 4065964 | 463757 | 5.30 (estimate) |
