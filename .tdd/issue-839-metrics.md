### 📊 Metrics — issue 839

Wall time for the issue: 1521 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 13 of 17 planned.
Outcome: the run bailed — ci-red, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 28 | 26 | 1 | 2 | 3487 | 11866 | 40930 | 0.20 |
| red | 22 | 9 | 0 | 0 | 695 | 610 | 126 | 250 | 54774 | 6263322 | 1081916 | 9.20 |
| pin | 3 | 3 | 0 | 0 | 47 | 37 | 12 | 24 | 3816 | 521053 | 135902 | 0.69 |
| green | 17 | 8 | 0 | 0 | 837 | 427 | 119 | 224 | 38177 | 5701738 | 817917 | 6.83 |
| refactor | 15 | 7 | 0 | 0 | 407 | 243 | 63 | 126 | 20251 | 2835534 | 702528 | 5.21 |
| diff | 6 | 3 | 0 | 0 | 138 | 110 | 24 | 48 | 8955 | 1067401 | 273377 | 2.00 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 31 | 31 | 0 | 0 | 796 | 445 | 133 | 258 | 47208 | 5710029 | 1422945 | 7.31 |
| developer | claude-opus-5-5 | 33 | 0 | 0 | 0 | 1356 | 1008 | 212 | 416 | 82252 | 10690885 | 1629625 | 16.82 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| ci | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a floor case in tests/leaf-role.test.sh, written against the bash script before the port, runs leaf-role.sh with no argument and with one empty argument and asserts exit 2, nothing on stdout and stderr exactly the one line `usage: leaf-role.sh <leaf-name>` ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 11 | 22 | 4387 | 539887 | 94982 | 0.76 | unknown | unknown | unknown | unknown |  |  | pin |
| leaf-role.sh, run through a symlink to the skill directory and from another working directory, prints the same stdout and stderr and exits with the same code as when run in place, for `develop-red` (exit 0) and `plan-red` (exit 2) (a case in tests/leaf-role.test.sh, written against the bash script before the port) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 11 | 20 | 5378 | 484877 | 97360 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_leaf_role.py calls veri.leaf_role.main(argv), faking nothing past argv, and asserts: return 2, nothing on stdout and stderr exactly `usage: leaf-role.sh <leaf-name>` for `[]` and `[""]`; return 0 with exactly `VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1` on stdout and nothing on stderr for `["develop-red"]`; every return inside 0–3; leaf-role.sh is removed from migration slice 4's list in the same commit, the slice's other scripts staying: replaces 'migration slice 4 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 260 | 62 | 120 | 22442 | 3119625 | 445082 | 3.82 | 277 | unknown | 0/5 | nothing-left |  |  | full |
| the symlink case in tests/leaf-role.test.sh takes its scratch directory from the harness rather than its own mktemp -d, so tests/unit/no-report-copies.test.sh is green again and the case still passes with its assertions unchanged ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 129 | 34 | 66 | 10844 | 1647235 | 290343 | 2.28 | 245 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.leaf_role.main maps the leading word before the first dash, matched exactly and case-sensitively: `develop` and `revise` print actor developer, `verify` verifier, `conductor` conductor; `revise-green-2` prints phase green attempt 2, `verify-refactor` phase refactor attempt 1, `conductor-506` phase 506 attempt 1; each printed as the one line `VERI_ACTOR=<actor> VERI_PHASE=<phase> VERI_ATTEMPT=<attempt>`, single spaces, nothing on stderr, return 0 (tests/py/test_leaf_role.py, faking nothing past argv) ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 111 | 30 | 58 | 10316 | 1357242 | 281074 | 2.13 | 220 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.leaf_role.main refuses with return 2, nothing on stdout and exactly one stderr line: `leaf-role: leaf name '<name>' has an unknown leading word (want develop-*|revise-*|verify-*|conductor-*)` for `plan-red`, `Develop-red` and `-red`, and `leaf-role: leaf name '<name>' says no phase (want develop-*|revise-*|verify-*|conductor-*)` for `develop` and `develop-`, the name verbatim between unescaped single quotes (tests/py/test_leaf_role.py, faking nothing past argv) ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 118 | 32 | 62 | 11117 | 1477914 | 282643 | 2.19 | 219 | unknown | 1/5 | nothing-structural |  |  | full |
| veri.leaf_role.main splits a trailing dash-and-digits off as the attempt, greedily and anchored, keeping the digits as written: `verify-red-2-3` is phase red-2 attempt 3, `revise-green-007` attempt 007, `develop--2` an empty phase and attempt 2 with return 0, `develop-red-` phase red- attempt 1, `develop-2` phase 2 attempt 1; a newline inside the name is matched as POSIX does, so `develop-a` newline `b-2` is phase a-newline-b attempt 2; a phase holding a space or `=` is printed verbatim; arguments after the first are ignored (tests/py/test_leaf_role.py, faking nothing past argv) ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 99 | 27 | 54 | 9451 | 1248483 | 284845 | 2.11 | 200 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.leaf_role.main writes a name's bytes as given: a name holding byte 0xff, as Python hands argv over with surrogateescape, reaches stdout in the phase and stderr in a refusal as that one raw byte, never as the four characters backslash-x-f-f (tests/py/test_leaf_role.py, faking only argv and the standard streams' byte buffers) ⟦criterion 5⟧ | 12 | 5 | 0 | 0 | 0 | 0 | 298 | 67 | 134 | 25523 | 3274734 | 572348 | 4.74 | 497 | 1/2 | 1/5 | nothing-structural |  |  | full |
| veri.leaf_role.main with sys.stdout set to None, as Python leaves it when fd 1 is closed, raises out of main for a name it maps rather than returning 0, so the shim exits 1 as the bash script's failed echo under set -e does; veri.leaf_role carries no wrapper turning an uncaught exception into a return code (tests/py/test_leaf_role.py, faking only the standard streams) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 11 | 22 | 3827 | 541482 | 95558 | 0.75 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.leaf_role.leaf_role(name) is importable in-process and returns, for every name a tests/py/test_leaf_role.py case gives main, the dict of VERI_ACTOR, VERI_PHASE and VERI_ATTEMPT, all three strings, whose entries main prints, or None after the same stderr line with nothing on stdout where main returns 2; leaf_role("") returns None after the one line `leaf-role: usage: leaf-role.sh <leaf-name>` on stderr; it starts no process, never exits and raises nothing for any str, among them a name of only dashes, only digits and one holding NUL (tests/py/test_leaf_role.py) ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 154 | 35 | 66 | 13733 | 1630168 | 294028 | 2.35 | 252 | unknown | 0/5 | nothing-structural |  |  | full |
| leaf-role.sh is a /bin/sh shim that execs python3 on "$(dirname "$0")/veri/leaf_role.py" once per invocation, as status.sh does — so a symlink to the file itself still fails, now with python3's exit 2 rather than bash's 1, unpinned — holding no Python source (no heredoc, no `python3 -c`), keeping the lowercase header line `usage: leaf-role.sh <leaf-name>`, citing no issue number in any comment and not repeating the stale claim that harvest-usage.sh sources lib/leaf-role.sh; every case in tests/leaf-role.test.sh passes with its assertions unmodified against the shim, in a commit that precedes any cut, whose diff in the test suites touches only copy lines and stub libs and changes no assertion ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 12 | 24 | 4598 | 601286 | 98153 | 0.79 | 1573 | unknown | unknown | unknown |  |  | full |
| tests/leaf-role.test.sh cuts no case — all five original cases run the script through its entry point, so ADR 0027's survival rule keeps them as contract cases — and holds besides only the floor case and the symlink case, with no pre-existing case's assertions changed ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 5 | 10 | 1605 | 178011 | 87539 | 0.58 | 42 | unknown | unknown | unknown |  |  | full |
| lib/leaf-role.sh, lib/leaf-model.sh, supervise.sh, verify.sh, veri/harvest_usage.py, tests/py/test_harvest_usage.py, tests/py/test_comment_class.py, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh, tests/no-python-in-ported-scripts.test.sh, tests/unit/emitted-text.test.sh, tests/leaf-model.test.sh, tests/supervise.test.sh and tests/parallel-conductors.test.sh are unchanged by the branch, lib/leaf-model.sh, supervise.sh and verify.sh still source lib/leaf-role.sh, and tests/unit/missing-argument-exit.test.sh is changed only by the removal of leaf-role.sh from migration slice 4's list ⟦diff-checked⟧ ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 7 | 14 | 2752 | 288104 | 87685 | 0.62 | 62 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| the symlink case in tests/leaf-role.test.sh takes its scratch directory from the harness rather than its own mktemp -d, so tests/unit/no-report-copies.test.sh is green again and the case still passes with its assertions unchanged ⟦added⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 52 | 0.68 |
| tests/py/test_leaf_role.py calls veri.leaf_role.main(argv), faking nothing past argv, and asserts: return 2, nothing on stdout and stderr exactly `usage: leaf-role.sh <leaf-name>` for `[]` and `[""]`; return 0 with exactly `VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1` on stdout and nothing on stderr for `["develop-red"]`; every return inside 0–3; leaf-role.sh is removed from migration slice 4's list in the same commit, the slice's other scripts staying: replaces 'migration slice 4 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 53 | 0.64 |
| veri.leaf_role.main maps the leading word before the first dash, matched exactly and case-sensitively: `develop` and `revise` print actor developer, `verify` verifier, `conductor` conductor; `revise-green-2` prints phase green attempt 2, `verify-refactor` phase refactor attempt 1, `conductor-506` phase 506 attempt 1; each printed as the one line `VERI_ACTOR=<actor> VERI_PHASE=<phase> VERI_ATTEMPT=<attempt>`, single spaces, nothing on stderr, return 0 (tests/py/test_leaf_role.py, faking nothing past argv) ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 51 | 0.67 |
| veri.leaf_role.main refuses with return 2, nothing on stdout and exactly one stderr line: `leaf-role: leaf name '<name>' has an unknown leading word (want develop-*|revise-*|verify-*|conductor-*)` for `plan-red`, `Develop-red` and `-red`, and `leaf-role: leaf name '<name>' says no phase (want develop-*|revise-*|verify-*|conductor-*)` for `develop` and `develop-`, the name verbatim between unescaped single quotes (tests/py/test_leaf_role.py, faking nothing past argv) ⟦criterion 5⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 63 | 0.73 |
| veri.leaf_role.main splits a trailing dash-and-digits off as the attempt, greedily and anchored, keeping the digits as written: `verify-red-2-3` is phase red-2 attempt 3, `revise-green-007` attempt 007, `develop--2` an empty phase and attempt 2 with return 0, `develop-red-` phase red- attempt 1, `develop-2` phase 2 attempt 1; a newline inside the name is matched as POSIX does, so `develop-a` newline `b-2` is phase a-newline-b attempt 2; a phase holding a space or `=` is printed verbatim; arguments after the first are ignored (tests/py/test_leaf_role.py, faking nothing past argv) ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 42 | 0.63 |
| veri.leaf_role.main writes a name's bytes as given: a name holding byte 0xff, as Python hands argv over with surrogateescape, reaches stdout in the phase and stderr in a refusal as that one raw byte, never as the four characters backslash-x-f-f (tests/py/test_leaf_role.py, faking only argv and the standard streams' byte buffers) ⟦criterion 5⟧ | 2 | 1/5 | nothing-structural | PASS | 0 | 87 | 1.17 |
| veri.leaf_role.leaf_role(name) is importable in-process and returns, for every name a tests/py/test_leaf_role.py case gives main, the dict of VERI_ACTOR, VERI_PHASE and VERI_ATTEMPT, all three strings, whose entries main prints, or None after the same stderr line with nothing on stdout where main returns 2; leaf_role("") returns None after the one line `leaf-role: usage: leaf-role.sh <leaf-name>` on stderr; it starts no process, never exits and raises nothing for any str, among them a name of only dashes, only digits and one holding NUL (tests/py/test_leaf_role.py) ⟦criterion 4⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 59 | 0.68 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 1 | 0 | 15 | 3 | 4 | 1 | 1 | 0 | 0 | 1 | 0 | 2 | 2 | 4 | 2 | 0 | 3 | 0 | 1 | 4 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 2 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 10 | 0 | 1 |
| target | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 25 | 16 | 16 | 16 | 17 | 17 | 16 | 16 | 16 | 17 | 16 | 16 | 16 | 17 | 16 | 17 | 16 | 15 | 17 | 17 | 18 | 16 | 17 | 18 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 345 | 674 | 129460 | 16400914 | 3052570 | 24.13 |
