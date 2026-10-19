### 📊 Metrics — issue 1375

Wall time for the issue: 2909 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1817.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 45 | 37 | 8 | 16 | 3476 | 241551 | 37281 | 0.15 |
| red | 2 | 0 | 0 | 0 | 88 | 80 | 18 | 32 | 8598 | 595985 | 53617 | 0.28 |
| pin | 2 | 2 | 0 | 0 | 42 | 37 | 13 | 24 | 3327 | 355288 | 34386 | 0.15 |
| green | 4 | 2 | 0 | 0 | 133 | 81 | 25 | 50 | 7189 | 776761 | 71164 | 0.33 |
| refactor | 4 | 2 | 0 | 0 | 79 | 50 | 13 | 26 | 3250 | 355607 | 59546 | 0.22 |
| diff | 8 | 3 | 1 | 0 | 559 | 213 | 54 | 108 | 16951 | 1629338 | 161198 | 0.90 |
| rebase | 2 | 1 | 0 | 0 | 680 | 48 | 10 | 20 | 2463 | 254816 | 55790 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 11 | 2 | 0 | 787 | 243 | 67 | 132 | 20624 | 1917267 | 230220 | 0.97 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 725 | 212 | 58 | 112 | 19874 | 1796360 | 187427 | 0.85 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 114 | 91 | 16 | 32 | 4756 | 495719 | 55335 | 0.40 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 166 | 0.55 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| missing-argument-exit.test.sh's no-argument audit holds as a pytest case. One parametrized small case in skills/tdd/scripts/tests/py/unit/test_missing_argument_cli.py with one case id per script, carrying @pytest.mark.tree_audit for its sweep of skills/tdd/scripts/*.sh. Its subjects are every scripts/*.sh whose first usage line names a <…> outside […], found as lib/missing-argument-exit.sh's requires_argument finds them, and each script maps to the veri/ module its shim execs. For each, run_cli(module, []) with VERI_* unset by the hermetic fixture must exit 2, with a stderr line carrying "usage" that names <script>.sh. Where a module's launch floor would start a process before it reads its arguments (run-conductor's bash and Python floor), the case answers that floor through its env knobs. The case is in-process only: no process, no subprocess. The case and every helper it calls are defined in that file. Red is expected to report AGAINST_UNMODIFIED: PASSES. No production change: every script and veri/ module stays unchanged: replaces `a script requiring a positional argument exits 2 with a usage line when called with none` in skills/tdd/scripts/tests/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 124 | 32 | 60 | 9704 | 940332 | 106828 | 0.46 | 315 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| missing-argument-exit.test.sh's later-argument and bad-value rosters hold as pytest cases. A parametrized small case table in skills/tdd/scripts/tests/py/unit/test_missing_argument_cli.py has one case id per roster call, with the argv the bash roster passes, unchanged, and each call goes through run_cli on that script's veri/ module. Every later-argument call must exit 2 with "usage" on stderr. Every bad-value call and every migration-slice-6 call must exit 2 with a usage line naming the script on stderr. That covers solvable-issues.sh, push-branch.sh and stop-requested.sh too. The case is in-process only (no process), with VERI_* unset by the hermetic fixture, and its helpers are defined in that file. Red is expected to report AGAINST_UNMODIFIED: PASSES. No production change: replaces `a script exits 2 with a usage line when a later required argument is missing`, `a script given a bad argument value exits 2 with its own usage text on stderr`, `migration slice 6 refuses an unresolvable commit or a missing file with the script's own usage text` in skills/tdd/scripts/tests/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 124 | 37 | 72 | 12660 | 1143309 | 111885 | 0.52 | 274 | unknown | 1/5 | nothing-left |  |  | already-satisfied |
| missing-argument-exit.test.sh's audit-of-the-audit cases are deleted as dead, and so are its bare-expansion scan and all four cases of unit/missing-argument-guard.test.sh. Each one is listed by its literal name= text, with the reason it is dead, in the committed .tdd/issue-1375-dead-cases.md, which is the pairs table's dead rows. The audit-of-the-audit cases are `the missing-argument audit covers a script added…`, `…returns 1 when a script it audits is an offender`, `…over a directory holding no script…` and `…calls only scripts whose usage line names a required argument…`. The bare-expansion scan is `no script guards a required positional argument with a bare \${N:?…} expansion`. Their subject is lib/missing-argument-exit.sh, which leaves with the audit, or positional parsing in shell, which no scripts/*.sh shim does. No other case changes, and no production change. ⟦diff-checked⟧ ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 131 | 27 | 54 | 8097 | 811866 | 89127 | 0.55 | 245 | 1/2 | unknown | unknown |  |  | full |
| The emptied missing-argument-exit.test.sh and unit/missing-argument-guard.test.sh are deleted, together with lib/missing-argument-exit.sh. Every remaining user moves off them, with its assertions kept. affected-suites.test.sh's no-range case no longer sources the lib and still asserts exit 2 with a usage line naming affected-suites.sh. scanner-status-guards.test.sh's #1648 case checks only scratch-copy-libs.test.sh, and its name says so. unit/no-report-copies.test.sh's GUARD_SUITES no longer lists missing-argument-exit. Outside .tdd/ and docs/, no guard table, exemption table, roster, sourced path or fixture of a real suite path names a deleted file; a scratch plant's invented file name is not a real path. No production change. ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 14 | 28 | 5586 | 439588 | 38760 | 0.20 | 108 | n/a | n/a | n/a |  |  | full |
| SKILL.md's Scope & plan sentence about a step that adds a script stops naming the deleted missing-argument-exit audit among the repo-wide audits. It names the run_cli no-argument case in tests/py/unit/test_missing_argument_cli.py beside unreachable instead, and keeps its usage line, exit 2, caller and same-step rule. The pin in tests/py/unit/test_skill_script_contract_step.py moves in the same commit, so it checks for the new name and no longer for missing-argument-exit. No script changes. ⟦diff-checked⟧ ⟦criterion 1⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 87 | 23 | 46 | 5731 | 632700 | 89101 | 0.34 | 363 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| missing-argument-exit.test.sh's no-argument audit holds as a pytest case. One parametrized small case in skills/tdd/scripts/tests/py/unit/test_missing_argument_cli.py with one case id per script, carrying @pytest.mark.tree_audit for its sweep of skills/tdd/scripts/*.sh. Its subjects are every scripts/*.sh whose first usage line names a <…> outside […], found as lib/missing-argument-exit.sh's requires_argument finds them, and each script maps to the veri/ module its shim execs. For each, run_cli(module, []) with VERI_* unset by the hermetic fixture must exit 2, with a stderr line carrying "usage" that names <script>.sh. Where a module's launch floor would start a process before it reads its arguments (run-conductor's bash and Python floor), the case answers that floor through its env knobs. The case is in-process only: no process, no subprocess. The case and every helper it calls are defined in that file. Red is expected to report AGAINST_UNMODIFIED: PASSES. No production change: every script and veri/ module stays unchanged: replaces `a script requiring a positional argument exits 2 with a usage line when called with none` in skills/tdd/scripts/tests/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 39 | 0.10 |
| missing-argument-exit.test.sh's later-argument and bad-value rosters hold as pytest cases. A parametrized small case table in skills/tdd/scripts/tests/py/unit/test_missing_argument_cli.py has one case id per roster call, with the argv the bash roster passes, unchanged, and each call goes through run_cli on that script's veri/ module. Every later-argument call must exit 2 with "usage" on stderr. Every bad-value call and every migration-slice-6 call must exit 2 with a usage line naming the script on stderr. That covers solvable-issues.sh, push-branch.sh and stop-requested.sh too. The case is in-process only (no process), with VERI_* unset by the hermetic fixture, and its helpers are defined in that file. Red is expected to report AGAINST_UNMODIFIED: PASSES. No production change: replaces `a script exits 2 with a usage line when a later required argument is missing`, `a script given a bad argument value exits 2 with its own usage text on stderr`, `migration slice 6 refuses an unresolvable commit or a missing file with the script's own usage text` in skills/tdd/scripts/tests/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 40 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 3 | 1 | 3 | 1 | 0 | 1 | 1 | 2 | 1 | 1 | 0 | 0 | 1 | 0 | 4 | 4 | 0 | 126 | 131 |
| target | 0 | 0 | 1 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 7 | 7 | 7 | 6 | 7 | 9 | 7 | 7 | 7 | 6 | 8 | 6 | 7 | 7 |  |  |  |  |  |  |  |  |
| all | 312 | 314 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 141 | 276 | 45254 | 4209346 | 472982 | 2.22 |
