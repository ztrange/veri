### 📊 Metrics — issue 2106

Wall time for the issue: 7537 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 11 of 14 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $12.07 over 221 turns, in 4 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 86114 |
| 2 | $0.03 | 86778 |
| 3 | $0.04 | 87718 |
| 4 | $0.04 | 89660 |
| 5 | $0.04 | 89956 |
| 6 | $0.03 | 90298 |
| 7 | $0.03 | 90630 |
| 8 | $0.03 | 90958 |
| 9 | $0.04 | 91545 |
| 10 | $0.04 | 92732 |
| 11 | $0.05 | 94758 |
| 12 | $0.06 | 98262 |
| 13 | $0.07 | 102903 |
| 14 | $0.07 | 108248 |
| 15 | $0.04 | 108673 |
| 16 | $0.04 | 109355 |
| 17 | $0.04 | 109966 |
| 18 | $0.04 | 111055 |
| 19 | $0.04 | 111853 |
| 20 | $0.05 | 113252 |
| 21 | $0.04 | 114491 |
| 22 | $0.05 | 116323 |
| 23 | $0.04 | 117137 |
| 24 | $0.05 | 117844 |
| 25 | $0.05 | 119784 |
| 26 | $0.05 | 122218 |
| 27 | $0.04 | 122911 |
| 28 | $0.04 | 123243 |
| 29 | $0.05 | 123912 |
| 30 | $0.05 | 125316 |
| 31 | $0.04 | 126110 |
| 32 | $0.06 | 129660 |
| 33 | $0.05 | 130985 |
| 34 | $0.05 | 131736 |
| 35 | $0.04 | 132556 |
| 36 | $0.05 | 133270 |
| 37 | $0.04 | 133706 |
| 38 | $0.05 | 134403 |
| 39 | $0.04 | 134792 |
| 40 | $0.05 | 136075 |
| 41 | $0.04 | 136916 |
| 42 | $0.05 | 137875 |
| 43 | $0.05 | 138879 |
| 44 | $0.05 | 139741 |
| 45 | $0.05 | 140995 |
| 46 | $0.04 | 141802 |
| 47 | $0.05 | 142477 |
| 48 | $0.05 | 143703 |
| 49 | $0.05 | 144431 |
| 50 | $0.04 | 145093 |
| 51 | $0.05 | 146156 |
| 52 | $0.05 | 146919 |
| 53 | $0.05 | 148363 |
| 54 | $0.05 | 149095 |
| 55 | $0.06 | 150594 |
| 56 | $0.04 | 151300 |
| 57 | $0.05 | 152123 |
| 58 | $0.06 | 153610 |
| 59 | $0.05 | 154282 |
| 60 | $0.05 | 155059 |
| 61 | $0.04 | 155358 |
| 62 | $0.05 | 156395 |
| 63 | $0.05 | 156924 |
| 64 | $0.05 | 157917 |
| 65 | $0.06 | 159330 |
| 66 | $0.06 | 161083 |
| 67 | $0.05 | 162263 |
| 68 | $0.05 | 163149 |
| 69 | $0.05 | 163456 |
| 70 | $0.05 | 163970 |
| 71 | $0.05 | 164245 |
| 72 | $0.05 | 164839 |
| 73 | $0.04 | 165267 |
| 74 | $0.05 | 165784 |
| 75 | $0.05 | 166263 |
| 76 | $0.06 | 167614 |
| 77 | $0.06 | 168778 |
| 78 | $0.04 | 169150 |
| 79 | $0.56 | 85562 |
| 80 | $0.03 | 86081 |
| 81 | $0.03 | 87487 |
| 82 | $0.03 | 88045 |
| 83 | $0.05 | 90998 |
| 84 | $0.06 | 94226 |
| 85 | $0.03 | 94616 |
| 86 | $0.03 | 95076 |
| 87 | $0.03 | 95391 |
| 88 | $0.03 | 95704 |
| 89 | $0.03 | 96164 |
| 90 | $0.03 | 96720 |
| 91 | $0.06 | 100715 |
| 92 | $0.04 | 101901 |
| 93 | $0.03 | 102842 |
| 94 | $0.57 | 86197 |
| 95 | $0.03 | 86684 |
| 96 | $0.04 | 88513 |
| 97 | $0.04 | 88942 |
| 98 | $0.05 | 91597 |
| 99 | $0.06 | 95144 |
| 100 | $0.06 | 99429 |
| 101 | $0.04 | 99717 |
| 102 | $0.04 | 100185 |
| 103 | $0.03 | 100524 |
| 104 | $0.04 | 100775 |
| 105 | $0.03 | 101248 |
| 106 | $0.04 | 101742 |
| 107 | $0.04 | 102383 |
| 108 | $0.03 | 103017 |
| 109 | $0.04 | 103967 |
| 110 | $0.07 | 107883 |
| 111 | $0.08 | 113622 |
| 112 | $0.06 | 116961 |
| 113 | $0.04 | 117300 |
| 114 | $0.05 | 119005 |
| 115 | $0.05 | 120236 |
| 116 | $0.04 | 120763 |
| 117 | $0.04 | 121208 |
| 118 | $0.13 | 133106 |
| 119 | $0.04 | 133954 |
| 120 | $0.05 | 135058 |
| 121 | $0.05 | 135768 |
| 122 | $0.04 | 136489 |
| 123 | $0.05 | 137319 |
| 124 | $0.05 | 138973 |
| 125 | $0.05 | 139696 |
| 126 | $0.05 | 140592 |
| 127 | $0.04 | 141475 |
| 128 | $0.05 | 142278 |
| 129 | $0.05 | 143005 |
| 130 | $0.04 | 143424 |
| 131 | $0.05 | 144127 |
| 132 | $0.05 | 145442 |
| 133 | $0.05 | 146364 |
| 134 | $0.05 | 147060 |
| 135 | $0.05 | 148038 |
| 136 | $0.05 | 149177 |
| 137 | $0.05 | 150843 |
| 138 | $0.06 | 151936 |
| 139 | $0.05 | 153688 |
| 140 | $0.05 | 154214 |
| 141 | $0.05 | 155075 |
| 142 | $0.05 | 156462 |
| 143 | $0.06 | 157334 |
| 144 | $0.04 | 157832 |
| 145 | $0.05 | 158464 |
| 146 | $0.06 | 159792 |
| 147 | $0.06 | 161582 |
| 148 | $0.06 | 163671 |
| 149 | $0.05 | 164089 |
| 150 | $0.05 | 164614 |
| 151 | $0.04 | 164925 |
| 152 | $0.05 | 165236 |
| 153 | $0.06 | 167196 |
| 154 | $0.05 | 167562 |
| 155 | $0.06 | 168758 |
| 156 | $0.07 | 172376 |
| 157 | $0.06 | 173455 |
| 158 | $0.05 | 174634 |
| 159 | $0.56 | 87230 |
| 160 | $0.02 | 87802 |
| 161 | $0.03 | 89220 |
| 162 | $0.05 | 93701 |
| 163 | $0.03 | 94896 |
| 164 | $0.17 | 113582 |
| 165 | $0.03 | 113967 |
| 166 | $0.03 | 114437 |
| 167 | $0.03 | 114767 |
| 168 | $0.03 | 115093 |
| 169 | $0.03 | 115983 |
| 170 | $0.03 | 116454 |
| 171 | $0.03 | 117127 |
| 172 | $0.03 | 118110 |
| 173 | $0.03 | 118733 |
| 174 | $0.03 | 120127 |
| 175 | $0.03 | 121146 |
| 176 | $0.03 | 122151 |
| 177 | $0.03 | 122712 |
| 178 | $0.03 | 123141 |
| 179 | $0.03 | 123698 |
| 180 | $0.03 | 124464 |
| 181 | $0.03 | 125238 |
| 182 | $0.03 | 125987 |
| 183 | $0.03 | 126383 |
| 184 | $0.08 | 133809 |
| 185 | $0.04 | 135014 |
| 186 | $0.03 | 135226 |
| 187 | $0.03 | 135438 |
| 188 | $0.03 | 135650 |
| 189 | $0.04 | 137242 |
| 190 | $0.04 | 138361 |
| 191 | $0.04 | 139399 |
| 192 | $0.04 | 140993 |
| 193 | $0.03 | 141579 |
| 194 | $0.03 | 142107 |
| 195 | $0.05 | 145054 |
| 196 | $0.04 | 146076 |
| 197 | $0.04 | 147570 |
| 198 | $0.04 | 148483 |
| 199 | $0.05 | 150937 |
| 200 | $0.05 | 152854 |
| 201 | $0.04 | 154421 |
| 202 | $0.04 | 155452 |
| 203 | $0.04 | 156696 |
| 204 | $0.04 | 158019 |
| 205 | $0.04 | 158807 |
| 206 | $0.04 | 160116 |
| 207 | $0.05 | 162853 |
| 208 | $0.04 | 163512 |
| 209 | $0.03 | 163771 |
| 210 | $0.04 | 164176 |
| 211 | $0.04 | 164628 |
| 212 | $0.04 | 165724 |
| 213 | $0.03 | 165936 |
| 214 | $0.05 | 167649 |
| 215 | $0.04 | 169009 |
| 216 | $0.04 | 169221 |
| 217 | $0.05 | 170776 |
| 218 | $0.04 | 171198 |
| 219 | $0.05 | 172752 |
| 220 | $0.04 | 173549 |
| 221 | $0.06 | 177288 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 1 | 2 | 1211 | 0 | 30905 | 0.09 |
| diff | 8 | 4 | 0 | 0 | 437 | 185 | 42 | 82 | 14678 | 1124470 | 178437 | 0.71 |
| red | 19 | 7 | 1 | 0 | 1209 | 535 | 105 | 210 | 45229 | 3317157 | 551967 | 2.69 |
| pin | 4 | 3 | 1 | 0 | 142 | 54 | 15 | 30 | 5254 | 359020 | 91649 | 0.32 |
| green | 19 | 4 | 2 | 0 | 7098 | 824 | 159 | 314 | 73095 | 5607351 | 793281 | 5.16 |
| refactor | 8 | 4 | 0 | 0 | 236 | 81 | 22 | 42 | 4031 | 523090 | 110132 | 0.37 |
| red-contradicted | 1 | 0 | 0 | 0 | 385 | 37 | 6 | 12 | 2641 | 142080 | 79471 | 0.24 |
| exhausted | 1 | 0 | 0 | 0 | 17 | 13 | 2 | 4 | 984 | 47087 | 12709 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 29 | 23 | 4 | 0 | 2667 | 484 | 105 | 210 | 36126 | 2682708 | 555597 | 2.02 |
| developer | claude-sonnet-5-5 | 20 | 0 | 0 | 0 | 1604 | 540 | 116 | 228 | 42954 | 3487992 | 515270 | 2.07 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 5268 | 716 | 131 | 258 | 68043 | 4949555 | 777684 | 5.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 758 | 1.66 |
| pin | 0 | 0.00 | 39 | 0.11 |
| green | 0 | 0.00 | 6228 | 4.48 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 385 | 0.24 |
| exhausted | 0 | 0.00 | 17 | 0.09 |
| verify-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The test helpers and older cases that pin a shim's exec line accept the venv-preferring canonical shim (after `#!/bin/sh` and comments, exactly three code lines: `py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"`, then `[ -x "$py" ] || py=python3`, then `exec "$py" "$(dirname "$0")/veri/<module>.py" "$@"`) as well as today's one-line `exec python3` shim, with the same module extraction: `CANONICAL_SHIM`, `SHIM_EXEC` and `shim_problems` in skills/tdd/scripts/tests/py/conftest.py, `SHIM_MODULE` in skills/tdd/scripts/tests/py/unit/test_missing_argument_cli.py, the `startswith("exec python3")` mutation in skills/tdd/scripts/tests/py/test_ensure_run_state_ignored.py, and any synthetic shim in skills/tdd/scripts/tests/py/test_shims.py that must now cover the new form; no production change, make test stays green ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 8 | 16 | 3934 | 198260 | 51133 | 0.19 | 185 | n/a | n/a | n/a |  |  | full |
| A ported script's `.sh` shim run with `VERI_VENV` naming a directory that has no executable `bin/python3` runs its module on the `python3` on PATH, and the script's normal output and exit code come back (a medium case marked process, starting the real shim) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 14 | 28 | 5676 | 454624 | 37506 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| A ported script's `.sh` shim run with a fixed PATH such as `/usr/bin:/bin:/usr/local/bin`, prefixed by a directory whose `python3` is a stub that exits 9, while `VERI_VENV` points at a venv whose `bin/python3` is the real interpreter, runs its module on the venv's interpreter: the script's normal output and exit code come back, not the stub's 9 (a medium case marked process, starting the real shim) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 121 | 26 | 52 | 7451 | 734460 | 119282 | 0.45 | 684 | unknown | 0/5 | nothing-structural |  |  | full |
| With `VERI_VENV` unset, a ported script's `.sh` shim finds the venv from `$HOME` (`$HOME/.veri-tools/venv/bin/python3`), never from PATH: run with HOME pointing at a scratch home whose `.veri-tools/venv/bin/python3` is the real interpreter and a PATH whose `python3` is a stub that exits 9, the script's normal output comes back (a medium case marked process, starting the real shim) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 8 | 16 | 3434 | 225153 | 38295 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| The test_1158 cases in skills/tdd/scripts/tests/py/test_stop_run.py that copy stop-run.sh and plant a mutation at its `exec python3` line find the exec line of the venv-preferring canonical shim (`exec "$py" …`) as well as today's, so stop-run.sh can take that shim with its `VERI_CALLER_DIR` preamble kept; no production change, make test stays green ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 11 | 22 | 2867 | 312679 | 30987 | 0.14 | 175 | n/a | n/a | n/a |  |  | full |
| A guard case reads every ported script's `.sh` shim under skills/tdd/scripts/ (tests excluded) and fails naming each one that execs PATH's `python3` unconditionally; every such shim, the exempted ones included with their preambles kept, becomes the venv-preferring canonical shim with its CLI contract unchanged (a tree_audit case) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 110 | 26 | 52 | 6967 | 719752 | 90113 | 0.37 | 345 | unknown | 0/5 | nothing-structural |  |  | full |
| CLAUDE.md's description of the port convention (a `/bin/sh` shim that `exec`s `python3`) says which interpreter the shim picks: `$VERI_VENV/bin/python3` (default `~/.veri-tools/venv/bin/python3`) when executable, else the `python3` on PATH ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 9 | 16 | 1562 | 204449 | 23289 | 0.09 | 138 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_bash_version_guard_process.py — FAILED test_run_conductor_sh_s_python_floor_refusal_names_veri_venv_bin_to_put_first_on_path_when_the_venv_there_meets_the_floor, FAILED test_leaf_launchable_sh_s_python_floor_refusal_names_veri_venv_bin_to_put_first_on_path_when_the_venv_there_meets_the_floor, FAILED test_run_conductor_sh_s_and_leaf_launchable_sh_s_python_floor_refusals_with_a_venv_at_veri_venv_below_the_floor_too_exit_2_with_today_s_message_and_name_no_venv_path (AssertionError: assert (0, '') == (2, 'run-cond...sion 3.11.9.'): the floor refusals of run-conductor.sh and leaf-launchable.sh no longer fire now that their shims run on the venv python3 ⟦suite-repair⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 9 | 18 | 4743 | 240611 | 73286 | 0.25 | unknown | unknown | unknown | unknown |  |  | pin |
| The test helpers and older cases that pin a shim exec line accept the floor-checking canonical shim (after `#!/bin/sh` and comments, exactly two code lines: `. "$(dirname "$0")/lib/shim-python.sh"`, then `exec "$py" "$(dirname "$0")/veri/<module>.py" "$@"`, with any exempted preamble such as stop-run.sh `export VERI_CALLER_DIR` kept ahead of them) as well as the two forms accepted today, with the same module extraction: `CANONICAL_SHIM`, `SHIM_EXEC`, `VENV_PREFIX` and `shim_problems` in skills/tdd/scripts/tests/py/conftest.py, `SHIM_MODULE` in skills/tdd/scripts/tests/py/unit/test_missing_argument_cli.py, the exec-line mutations in skills/tdd/scripts/tests/py/test_ensure_run_state_ignored.py and in the test_1158 cases of skills/tdd/scripts/tests/py/test_stop_run.py, and test_issue_2106_no_shim_execs_the_python3_on_path_unconditionally in skills/tdd/scripts/tests/py/test_shims.py, which must not flag the floor-checking form; no production change, make test stays green ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 14 | 28 | 6315 | 409082 | 73028 | 0.29 | 206 | n/a | n/a | n/a |  |  | full |
| A ported script `.sh` shim run with `VERI_VENV` pointing at a venv whose `bin/python3` is a stub reporting Python 3.9 (it prints `Python 3.9.6` for `--version` and exits 9 for anything else), and a PATH whose `python3` is the real interpreter meeting the 3.12 floor, runs its module on the PATH interpreter: the script normal output and exit code come back, not the stub 9. The shim reads each interpreter version with `<python3> --version` from the sourced POSIX sh file skills/tdd/scripts/lib/shim-python.sh, which sets `py`, holding no Python source; the shim under test takes the floor-checking canonical shim (a medium case marked process, starting the real shim) ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 122 | 23 | 44 | 7411 | 637611 | 105801 | 0.40 | 398 | unknown | 0/5 | nothing-left |  |  | full |
| A ported script `.sh` shim run with both the venv `python3` and the PATH `python3` stubs reporting Python 3.9 (each prints `Python 3.9.6` for `--version` and exits 9 for anything else) exits 2 without running its module, with a stderr line naming each interpreter it tried, where it came from (venv or PATH) and its version, 3.9.6 (a medium case marked process, starting the real shim) ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 29 | 58 | 10195 | 895515 | 107342 | 0.46 | 419 | unknown | 0/5 | structural-owed |  |  | full |
| A guard case reads every ported script `.sh` shim under skills/tdd/scripts/ (tests excluded) and fails naming each one that is not the floor-checking canonical shim (`. "$(dirname "$0")/lib/shim-python.sh"` then `exec "$py" …`); every such shim, the exempted ones included with their preambles kept, becomes that shim with its CLI contract unchanged (a tree_audit case) ⟦criterion 3⟧ | 22 | 3 | 4 | 0 | 0 | 0 | 936 | 174 | 344 | 85357 | 6088059 | 1067584 | 6.59 | unknown | green 4/2, red 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A ported script's `.sh` shim run with a fixed PATH such as `/usr/bin:/bin:/usr/local/bin`, prefixed by a directory whose `python3` is a stub that exits 9, while `VERI_VENV` points at a venv whose `bin/python3` is the real interpreter, runs its module on the venv's interpreter: the script's normal output and exit code come back, not the stub's 9 (a medium case marked process, starting the real shim) ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 63 | 0.09 |
| A guard case reads every ported script's `.sh` shim under skills/tdd/scripts/ (tests excluded) and fails naming each one that execs PATH's `python3` unconditionally; every such shim, the exempted ones included with their preambles kept, becomes the venv-preferring canonical shim with its CLI contract unchanged (a tree_audit case) ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 60 | 0.10 |
| A ported script `.sh` shim run with `VERI_VENV` pointing at a venv whose `bin/python3` is a stub reporting Python 3.9 (it prints `Python 3.9.6` for `--version` and exits 9 for anything else), and a PATH whose `python3` is the real interpreter meeting the 3.12 floor, runs its module on the PATH interpreter: the script normal output and exit code come back, not the stub 9. The shim reads each interpreter version with `<python3> --version` from the sourced POSIX sh file skills/tdd/scripts/lib/shim-python.sh, which sets `py`, holding no Python source; the shim under test takes the floor-checking canonical shim (a medium case marked process, starting the real shim) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.09 |
| A ported script `.sh` shim run with both the venv `python3` and the PATH `python3` stubs reporting Python 3.9 (each prints `Python 3.9.6` for `--version` and exits 9 for anything else) exits 2 without running its module, with a stderr line naming each interpreter it tried, where it came from (venv or PATH) and its version, 3.9.6 (a medium case marked process, starting the real shim) ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 61 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 16 | 20 | 28 | 20 | 25 | 16 | 26 | 25 | 26 | 18 | 16 | 17 | 15 | 15 | 18 | 16 | 19 | 19 | 19 | 17 | 18 | 19 | 17 | 17 | 49 | 0 | 17 | 16 | 18 | 17 | 20 | 52 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 8 | 7 | 8 | 7 | 90 | 107 | 7 | 11 | 10 | 9 | 13 | 8 | 7 | 10 | 0 | 7 | 10 | 14 | 13 | 11 | 11 | 11 | 3 | 10 | 12 | 11 | 4 | 11 | 15 | 11 | 11 | 13 | 91 | 12 | 222 | 1008 | 205 | 12 | 13 | 79 | 0 | 95 | 74 | 400 | 379 | 27 | 340 | 342 | 7 | 3 | 4 | 97 | 0 | 1101 | 103 | 341 | 28 |
| target | 7 | 7 | 7 | 7 | 7 | 10 | 10 | 10 | 11 | 5 | 11 | 12 | 11 | 16 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 352 | 696 | 147123 | 11120255 | 1848551 | 9.66 |
