### 📊 Metrics — issue 840

Wall time for the issue: 2873 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 12 of 16 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/909.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 16 | 1 | 2 | 2005 | 11866 | 41028 | 0.19 |
| red | 15 | 6 | 0 | 0 | 621 | 571 | 108 | 212 | 45701 | 5659708 | 767308 | 6.94 |
| pin | 3 | 3 | 0 | 0 | 51 | 40 | 12 | 24 | 4462 | 521167 | 136310 | 0.69 |
| green | 15 | 5 | 1 | 0 | 691 | 405 | 106 | 206 | 33988 | 5356757 | 674211 | 5.72 |
| refactor | 10 | 5 | 0 | 0 | 264 | 159 | 41 | 78 | 13219 | 1717872 | 476607 | 3.39 |
| diff | 8 | 4 | 0 | 0 | 335 | 165 | 32 | 64 | 12231 | 1416510 | 361086 | 2.66 |
| predicate | 1 | 0 | 0 | 0 | 32 | 30 | 4 | 8 | 1608 | 173843 | 44447 | 0.42 |
| structural | 1 | 0 | 0 | 0 | 52 | 44 | 6 | 12 | 2510 | 295133 | 47557 | 0.49 |
| transform | 1 | 1 | 0 | 0 | 365 | 11 | 3 | 6 | 951 | 115553 | 43965 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 28 | 25 | 1 | 0 | 1090 | 418 | 121 | 232 | 43691 | 5209731 | 1244952 | 6.46 |
| developer | claude-opus-5-5 | 27 | 0 | 0 | 0 | 1340 | 1023 | 192 | 380 | 72984 | 10058678 | 1347567 | 14.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 242 | 1.84 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 32 | 0.42 |
| structural | 0 | 0.00 | 52 | 0.49 |
| transform | 0 | 0.00 | 365 | 0.21 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a floor case in tests/leaf-model.test.sh, written against the bash script before the port, runs leaf-model.sh with no argument and with one empty argument and asserts exit 2, nothing on stdout and stderr exactly the one line `usage: leaf-model.sh <leaf-name>` ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 13 | 26 | 4641 | 667792 | 96050 | 0.80 | unknown | unknown | unknown | unknown |  |  | pin |
| leaf-model.sh, run through a symlink to the skill directory and from another working directory, answers as it does when run in place: under VERI_MODEL=sonnet it prints `sonnet` for `develop-red` and exits 0, with nothing on stderr (a case in tests/leaf-model.test.sh, written against the bash script before the port, its scratch directory taken from the harness) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 69 | 14 | 28 | 5503 | 733856 | 96980 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_leaf_model.py calls veri.leaf_model.main(argv), clearing VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER first and faking nothing past argv and the environment, and asserts: return 2, nothing on stdout and stderr exactly `usage: leaf-model.sh <leaf-name>` for `[]` and `[""]`; return 0 with `sonnet` on stdout for `["develop-red"]` under VERI_MODEL=sonnet; return 0 with nothing on stdout for `["verify-green"]` with the three variables unset; every return inside 0–3; leaf-model.sh is removed from migration slice 4's list in the same commit, the slice's other scripts staying: replaces 'migration slice 4 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 245 | 58 | 112 | 21014 | 2953126 | 394869 | 3.33 | 435 | 1/2 | 0/5 | nothing-left |  |  | full |
| veri.leaf_model.main prints VERI_MODEL for a leaf of either role and nothing (no newline) when no model variable is set; VERI_MODEL_DEVELOPER beats VERI_MODEL for `develop-*` and `revise-*` leaves only, VERI_MODEL_VERIFIER for `verify-*` leaves only, and VERI_MODEL_CONDUCTOR for `conductor-*` leaves (`VERI_MODEL_CONDUCTOR=opus` prints `opus` for `conductor-x`); a role variable set but empty falls through to VERI_MODEL, and VERI_MODEL set but empty prints nothing; the other role's variable is never read; values such as `opus[1m]` and one holding a backslash print verbatim with one trailing newline; arguments after the first are ignored; return 0 and nothing on stderr throughout (tests/py/test_leaf_model.py, faking only argv and the environment) ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 167 | 37 | 74 | 15068 | 1943306 | 307890 | 2.53 | 262 | unknown | 0/5 | structural-owed |  |  | full |
| veri.leaf_model.main refuses a resolved value holding any of space, tab, newline, vertical tab, form feed or carriage return with return 2, nothing on stdout and the one stderr line `leaf-model: model '<value>' contains whitespace (a model id or alias is one word)`, the value verbatim; a value holding 0x1c, 0x85 or U+00A0 is printed, return 0; whitespace only in a shadowed VERI_MODEL or in the other role's variable passes with return 0 (tests/py/test_leaf_model.py, faking only argv and the environment) ⟦criterion 4⟧ | 11 | 4 | 0 | 0 | 0 | 1 | 261 | 60 | 110 | 21726 | 2681245 | 478206 | 3.79 | 315 | unknown | 0/5 | nothing-left |  |  | full |
| veri.leaf_model.main maps the name before reading any model variable: a name veri.leaf_role refuses returns 2 with nothing on stdout and leaf_role's own one stderr line — `leaf-role: leaf name 'frobnicate-red' has an unknown leading word (want develop-*|revise-*|verify-*|conductor-*)` and `leaf-role: leaf name 'develop' says no phase (want develop-*|revise-*|verify-*|conductor-*)` — both with no model variable set and under VERI_MODEL holding whitespace (tests/py/test_leaf_model.py, faking only argv and the environment) ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 144 | 35 | 70 | 11075 | 1737197 | 292066 | 2.28 | 265 | unknown | 0/5 | nothing-left |  |  | full |
| veri.leaf_model.main prints a resolved value as bash's builtin echo does: a value that is wholly `-` followed by one or more of `n`, `e` and `E` is read as options, so `-n`, `-nE` and `-ne` print nothing at all and `-e` and `-E` a bare newline, while `-`, `--`, `-x` and `-nx` print as given with a newline; all return 0 (tests/py/test_leaf_model.py, faking only argv and the environment) ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 144 | 36 | 72 | 11448 | 1785008 | 287215 | 2.28 | 257 | unknown | 0/5 | nothing-left |  |  | full |
| veri.leaf_model.main reads the model variables and writes the value as bytes: a VERI_MODEL holding byte 0xff reaches stdout as that one raw byte, and the whitespace refusal carries it raw on stderr; with sys.stdout set to None, as Python leaves it when fd 1 is closed, main raises for a resolved non-empty value rather than returning 0, so the shim exits 1 as the bash script's failed echo under set -e does, and veri.leaf_model carries no wrapper turning an uncaught exception into a return code (tests/py/test_leaf_model.py, faking only argv, the environment and the standard streams) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 88 | 14 | 28 | 6895 | 753974 | 101160 | 0.89 | unknown | unknown | unknown | unknown |  |  | pin |
| veri/leaf_model.py imports the name→actor mapping from veri/leaf_role.py and defines no actor table, `want` text or attempt regex of its own, imports nothing from veri/harvest_usage.py and starts no process ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 8 | 16 | 2486 | 343458 | 87992 | 0.63 | 57 | unknown | unknown | unknown |  |  | full |
| leaf-model.sh is a /bin/sh shim that execs python3 on "$(dirname "$0")/veri/leaf_model.py" once per invocation, as status.sh does — so a symlink to the file itself still fails, now with python3's exit 2, unpinned — holding no Python source (no heredoc, no `python3 -c`), keeping the lowercase header line `usage: leaf-model.sh <leaf-name>` and citing no issue number in any comment; every case in tests/leaf-model.test.sh passes with its assertions unmodified against the shim, in a commit that precedes any cut, whose diff in the test suites touches only copy lines and stub libs and changes no assertion ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 12 | 24 | 5066 | 604480 | 97048 | 0.81 | 192 | unknown | unknown | unknown |  |  | full |
| tests/leaf-model.test.sh cuts no case — its three model cases run the script through its entry point and observe only exit, stdout and stderr, so ADR 0027's survival rule keeps them as contract cases, and the SKILL.md preflight case never runs leaf-model.sh — and holds besides only the floor case and the symlink case, with no pre-existing case's assertions changed ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 6 | 12 | 1954 | 234001 | 88508 | 0.61 | 40 | unknown | unknown | unknown |  |  | full |
| lib/leaf-model.sh, lib/leaf-role.sh, supervise.sh, verify.sh, veri/leaf_role.py, veri/harvest_usage.py, tests/unit/emitted-text.test.sh, tests/hermetic-suites.test.sh, tests/supervise.test.sh, tests/verify.test.sh, tests/py/test_comment_class.py, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh and tests/no-python-in-ported-scripts.test.sh are unchanged by the branch, supervise.sh and verify.sh still source lib/leaf-model.sh, and tests/unit/missing-argument-exit.test.sh is changed only by the removal of leaf-model.sh from migration slice 4's list ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 6 | 12 | 2725 | 234571 | 87538 | 0.62 | 95 | unknown | unknown | unknown |  |  | full |
| make test is green, tests/unit/missing-argument-exit.test.sh, tests/unit/emitted-text.test.sh, tests/hermetic-suites.test.sh, tests/supervise.test.sh, tests/verify.test.sh, tests/py/test_comment_class.py, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh and tests/no-python-in-ported-scripts.test.sh among its suites ⟦full-suite⟧ ⟦criterion 5⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 85 | 13 | 26 | 5069 | 584529 | 135969 | 1.12 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tests/py/test_leaf_model.py calls veri.leaf_model.main(argv), clearing VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER first and faking nothing past argv and the environment, and asserts: return 2, nothing on stdout and stderr exactly `usage: leaf-model.sh <leaf-name>` for `[]` and `[""]`; return 0 with `sonnet` on stdout for `["develop-red"]` under VERI_MODEL=sonnet; return 0 with nothing on stdout for `["verify-green"]` with the three variables unset; every return inside 0–3; leaf-model.sh is removed from migration slice 4's list in the same commit, the slice's other scripts staying: replaces 'migration slice 4 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 50 | 0.65 |
| veri.leaf_model.main prints VERI_MODEL for a leaf of either role and nothing (no newline) when no model variable is set; VERI_MODEL_DEVELOPER beats VERI_MODEL for `develop-*` and `revise-*` leaves only, VERI_MODEL_VERIFIER for `verify-*` leaves only, and VERI_MODEL_CONDUCTOR for `conductor-*` leaves (`VERI_MODEL_CONDUCTOR=opus` prints `opus` for `conductor-x`); a role variable set but empty falls through to VERI_MODEL, and VERI_MODEL set but empty prints nothing; the other role's variable is never read; values such as `opus[1m]` and one holding a backslash print verbatim with one trailing newline; arguments after the first are ignored; return 0 and nothing on stderr throughout (tests/py/test_leaf_model.py, faking only argv and the environment) ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 63 | 0.73 |
| veri.leaf_model.main refuses a resolved value holding any of space, tab, newline, vertical tab, form feed or carriage return with return 2, nothing on stdout and the one stderr line `leaf-model: model '<value>' contains whitespace (a model id or alias is one word)`, the value verbatim; a value holding 0x1c, 0x85 or U+00A0 is printed, return 0; whitespace only in a shadowed VERI_MODEL or in the other role's variable passes with return 0 (tests/py/test_leaf_model.py, faking only argv and the environment) ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 50 | 0.68 |
| veri.leaf_model.main maps the name before reading any model variable: a name veri.leaf_role refuses returns 2 with nothing on stdout and leaf_role's own one stderr line — `leaf-role: leaf name 'frobnicate-red' has an unknown leading word (want develop-*|revise-*|verify-*|conductor-*)` and `leaf-role: leaf name 'develop' says no phase (want develop-*|revise-*|verify-*|conductor-*)` — both with no model variable set and under VERI_MODEL holding whitespace (tests/py/test_leaf_model.py, faking only argv and the environment) ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.69 |
| veri.leaf_model.main prints a resolved value as bash's builtin echo does: a value that is wholly `-` followed by one or more of `n`, `e` and `E` is read as options, so `-n`, `-nE` and `-ne` print nothing at all and `-e` and `-E` a bare newline, while `-`, `--`, `-x` and `-nx` print as given with a newline; all return 0 (tests/py/test_leaf_model.py, faking only argv and the environment) ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 49 | 0.66 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 2 | 1 | 0 | 3 | 0 | 3 | 1 | 1 | 0 | 2 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 53 | 1 | 5 |
| target | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 16 | 16 | 16 | 16 | 15 | 15 | 16 | 16 | 15 | 15 | 16 | 16 | 14 | 14 | 15 | 16 | 16 | 15 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 313 | 612 | 116675 | 15268409 | 2592519 | 20.71 |
