### 📊 Metrics — issue 802

Wall time for the issue: 7801 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 17 of 22 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/837.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 78 | 74 | 6 | 12 | 7084 | 339726 | 62173 | 0.71 |
| red | 23 | 9 | 0 | 0 | 952 | 755 | 178 | 352 | 74231 | 10269201 | 1286630 | 13.83 |
| green | 28 | 9 | 5 | 0 | 2565 | 1094 | 249 | 494 | 98806 | 14553411 | 1288288 | 15.20 |
| refactor | 18 | 9 | 0 | 0 | 953 | 480 | 101 | 200 | 33815 | 5283102 | 949366 | 9.33 |
| pin | 5 | 5 | 0 | 0 | 157 | 97 | 23 | 46 | 9132 | 1144909 | 259765 | 2.49 |
| diff | 6 | 3 | 0 | 0 | 449 | 198 | 34 | 68 | 19292 | 1908445 | 341818 | 3.50 |
| predicate | 1 | 0 | 0 | 0 | 13 | 8 | 3 | 6 | 671 | 129274 | 47142 | 0.42 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 41 | 36 | 5 | 0 | 2739 | 1343 | 267 | 530 | 115959 | 14651529 | 1951304 | 20.86 |
| developer | claude-opus-5-5 | 41 | 0 | 0 | 0 | 2428 | 1363 | 327 | 648 | 127072 | 18976539 | 2283878 | 24.61 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2485 | 11.92 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| veri.ledger.ledger_steps returns kind `diff-checked` for an open step whose text is `x`, then the diff-checked marker, then a criterion-3 marker (the double-bracketed tags the ledger grammar reads), as lib/ledger.sh's ledger_steps prints under LC_ALL=C (a tests/py/test_ledger.py case; tests/py/test_status.py unmodified) ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 119 | 37 | 74 | 12136 | 1977653 | 309502 | 3.11 | 343 | unknown | 0/5 | nothing-left |  |  | full |
| veri.ledger.ledger_steps marks `added` by lib/ledger.sh's suffix rule — a space and the added marker ending the text once one trailing refactor-pending mark and then one trailing criterion marker are cut — so `a`, added marker, `b`, criterion-2 marker is added 0, a text that is only the added marker is added 0, and `t`, added marker, criterion-2 marker, refactor-pending mark on an open step is added 1 (tests/py/test_ledger.py cases) ⟦criterion 3⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 359 | 84 | 166 | 33474 | 4824559 | 443138 | 5.18 | 815 | 2/2 | 1/5 | nothing-structural |  |  | full |
| veri.ledger.ledger_steps reads the step grammar's whitespace as `[[:space:]]` under LC_ALL=C — space, tab, newline, vertical tab, form feed, carriage return only — so a line led by NBSP, by EM SPACE or by `\x1c` is no step (tests/py/test_ledger.py cases) ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 184 | 46 | 92 | 15338 | 2565009 | 317840 | 3.36 | 390 | unknown | 1/5 | nothing-structural |  |  | full |
| tests/ledger-steps.test.sh holds a case, written against the bash script before the port, asserting that `ledger-steps.sh bogus` exits 2 with nothing on stdout and stderr exactly the one line `usage: ledger-steps.sh [current|last-done|criterion <k>]` ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 13 | 26 | 4645 | 734660 | 107142 | 1.10 | unknown | unknown | unknown | unknown |  |  | pin |
| ledger-steps.sh, run through a symlink to the skill directory and from another working directory, prints the same stdout and stderr and exits with the same code as when run in place, for the no-argument form and for `current` over a ledger with no open step (a case in tests/ledger-steps.test.sh, written against the bash script before the port) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 15 | 30 | 7619 | 903975 | 113817 | 1.24 | unknown | unknown | unknown | unknown |  |  | pin |
| the #495 planned-step-count case in tests/metrics.test.sh stubs ledger-steps.sh itself — an executable `ledger-steps.sh` in `$stub/` printing the same three records, which metrics.sh runs as a process — in place of a stub lib/ledger.sh, its assertion `progress_says "$ledger_steps_out" 1 3` unchanged, passing against the bash script ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 15 | 30 | 6605 | 853111 | 120179 | 1.26 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_ledger_steps.py: veri.ledger_steps.main(argv), stdin faked as bytes, returns 2 with nothing on stdout and stderr exactly `usage: ledger-steps.sh [current|last-done|criterion <k>]` for `["bogus"]`, `["criterion"]`, `["criterion", "two"]` and `["criterion", "1\n"]`; returns 3 with nothing on stdout for `["current"]` over a ledger with no pending and no open step-kind step; returns 0 printing every record for `[]`; every return inside 0–3; ledger-steps.sh is removed from migration slice 4's list in the same commit, the slice's other scripts staying: replaces 'migration slice 4 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 561 | 93 | 184 | 39752 | 5683141 | 480162 | 5.77 | 1066 | 2/2 | 0/5 | structural-owed |  |  | full |
| veri.ledger_steps.main(["current"]) prints the first done refactor-pending step's text with ` ⟂ refactor pending` cut, else the first open step whose kind is `step` or `diff-checked` (an open ⟦replaces-case⟧ step among them, ⟦human-owed⟧ and ⟦full-suite⟧ skipped), returning 0 (tests/py/test_ledger_steps.py, faking only argv and stdin) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 176 | 40 | 80 | 16976 | 2291866 | 332655 | 3.46 | 387 | unknown | 0/5 | nothing-left |  |  | full |
| veri.ledger_steps.main(["last-done"]) prints the last done step's text, `[x]` and `[X]` alike, with the pending mark cut, and returns 0; a last done step with empty text prints one empty line and returns 0; no done step returns 3 with nothing on stdout (tests/py/test_ledger_steps.py) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 147 | 41 | 80 | 14354 | 2180142 | 315194 | 3.24 | 338 | unknown | 1/5 | nothing-structural |  |  | full |
| veri.ledger_steps.main(["criterion", k]) prints the k-th step-grammar line kept from every line starting `## Acceptance criteria` up to the next line starting `## ` — `## Acceptance criteriaX` opens a section, a `### ` line does not close one, a second matching heading keeps the count going, `[x]` and an indented `  - [ ]` count, `* [ ]` does not, a `[x]` line's pending mark is cut, a last line with no final newline is read — and returns 3 with nothing on stdout when fewer than k lines were kept (tests/py/test_ledger_steps.py) ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 238 | 56 | 110 | 21832 | 3104541 | 386582 | 4.15 | 532 | 1/2 | 0/5 | nothing-left |  |  | full |
| veri.ledger_steps.main reads `<k>` as bash's `$((10#k))` does: `08` is the 8th, `0` returns 3, `18446744073709551617` wraps to the 1st, `99999999999999999999` wraps past the count and returns 3; and refuses with return 2 and the usage line for `<k>` empty, `-1`, ` 1` and `١` (tests/py/test_ledger_steps.py) ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 155 | 38 | 76 | 14217 | 2063916 | 314388 | 3.21 | 352 | unknown | 0/5 | nothing-left |  |  | full |
| veri.ledger_steps.main reads the verb from argv[0] alone: `["current", "extra"]` and `["criterion", "1", "extra"]` answer as without the extra argument, `[""]` prints every record as `[]` does, and empty stdin prints nothing and returns 0 (tests/py/test_ledger_steps.py) ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 11 | 22 | 5492 | 595853 | 107284 | 1.09 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.ledger_steps.main passes bytes through as bash does: a `\xff` byte in a step's text reaches stdout as that byte, a NUL byte is dropped, and in a CRLF document the `\r` stays at the end of every text — `criterion 1` prints `c1\r`, a heading `## Acceptance criteria\r` still opens the section, and a `[x]` line ending ` ⟂ refactor pending\r` keeps its mark and is not pending (tests/py/test_ledger_steps.py) ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 172 | 43 | 84 | 16202 | 2338662 | 325980 | 3.40 | 377 | unknown | 0/5 | nothing-left |  |  | full |
| veri.ledger_steps.main, with sys.stdout set to None as Python leaves it when fd 1 is closed, raises out of main rather than returning 0, and with a stdin that cannot be read raises too — no wrapper converts an exception to a return code — so the shim exits 1, as the bash script does (tests/py/test_ledger_steps.py, faking only the standard streams) ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 79 | 19 | 38 | 7342 | 1133535 | 110186 | 1.26 | unknown | unknown | unknown | unknown |  |  | pin |
| ledger-steps.sh is a /bin/sh shim that execs python3 on veri/ledger_steps.py once per invocation, holding no Python source, carrying a lowercase `usage: ledger-steps.sh [current|last-done|criterion <k>]` line in its header and citing no issue number in any comment; veri/ledger_steps.py imports `from ledger import ledger_steps` with no second copy of the step grammar and carries no wrapper turning an uncaught exception into exit 2; every case of tests/ledger-steps.test.sh passes with its assertions unmodified against the shim; the same commit adds `"$SCRIPTS/veri"` to what tests/skill-leaf-env.test.sh's stage_recorder links, and touches the test suites only in copy lines and stub libs, coming before any cut ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 13 | 26 | 7327 | 723130 | 112727 | 1.19 | 240 | unknown | unknown | unknown |  |  | full |
| tests/ledger-steps.test.sh holds the survivors and the floor — the no-argument records case (exit 0), the `current … else exits 3` case (exit 3), the exact-usage case (exit 2 and its stderr byte for byte) and the symlink case — with those cases' assertions unchanged; every other case is removed, each replaced by a tests/py/test_ledger_steps.py case asserting the same thing ⟦diff-checked⟧ ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 83 | 14 | 28 | 8221 | 859722 | 128600 | 1.37 | 112 | unknown | unknown | unknown |  |  | full |
| tests/metrics.test.sh is changed only in the #495 planned-step-count case, tests/skill-leaf-env.test.sh only in stage_recorder's copy line, tests/unit/missing-argument-exit.test.sh only by removing ledger-steps.sh from slice 4's list; tests/py/test_comment_class.py, tests/py/test_status.py, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh and lib/ledger.sh are unchanged, and the eight other scripts that sourced lib/ledger.sh still do ⟦diff-checked⟧ ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 7 | 14 | 3744 | 325593 | 100491 | 0.94 | 151 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.ledger.ledger_steps returns kind `diff-checked` for an open step whose text is `x`, then the diff-checked marker, then a criterion-3 marker (the double-bracketed tags the ledger grammar reads), as lib/ledger.sh's ledger_steps prints under LC_ALL=C (a tests/py/test_ledger.py case; tests/py/test_status.py unmodified) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 82 | 0.99 |
| veri.ledger.ledger_steps marks `added` by lib/ledger.sh's suffix rule — a space and the added marker ending the text once one trailing refactor-pending mark and then one trailing criterion marker are cut — so `a`, added marker, `b`, criterion-2 marker is added 0, a text that is only the added marker is added 0, and `t`, added marker, criterion-2 marker, refactor-pending mark on an open step is added 1 (tests/py/test_ledger.py cases) ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 104 | 1.07 |
| veri.ledger.ledger_steps reads the step grammar's whitespace as `[[:space:]]` under LC_ALL=C — space, tab, newline, vertical tab, form feed, carriage return only — so a line led by NBSP, by EM SPACE or by `\x1c` is no step (tests/py/test_ledger.py cases) ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 108 | 1.07 |
| tests/py/test_ledger_steps.py: veri.ledger_steps.main(argv), stdin faked as bytes, returns 2 with nothing on stdout and stderr exactly `usage: ledger-steps.sh [current|last-done|criterion <k>]` for `["bogus"]`, `["criterion"]`, `["criterion", "two"]` and `["criterion", "1\n"]`; returns 3 with nothing on stdout for `["current"]` over a ledger with no pending and no open step-kind step; returns 0 printing every record for `[]`; every return inside 0–3; ledger-steps.sh is removed from migration slice 4's list in the same commit, the slice's other scripts staying: replaces 'migration slice 4 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 226 | 1.12 |
| veri.ledger_steps.main(["current"]) prints the first done refactor-pending step's text with ` ⟂ refactor pending` cut, else the first open step whose kind is `step` or `diff-checked` (an open ⟦replaces-case⟧ step among them, ⟦human-owed⟧ and ⟦full-suite⟧ skipped), returning 0 (tests/py/test_ledger_steps.py, faking only argv and stdin) ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 90 | 0.98 |
| veri.ledger_steps.main(["last-done"]) prints the last done step's text, `[x]` and `[X]` alike, with the pending mark cut, and returns 0; a last done step with empty text prints one empty line and returns 0; no done step returns 3 with nothing on stdout (tests/py/test_ledger_steps.py) ⟦criterion 6⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 88 | 1.04 |
| veri.ledger_steps.main(["criterion", k]) prints the k-th step-grammar line kept from every line starting `## Acceptance criteria` up to the next line starting `## ` — `## Acceptance criteriaX` opens a section, a `### ` line does not close one, a second matching heading keeps the count going, `[x]` and an indented `  - [ ]` count, `* [ ]` does not, a `[x]` line's pending mark is cut, a last line with no final newline is read — and returns 3 with nothing on stdout when fewer than k lines were kept (tests/py/test_ledger_steps.py) ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 83 | 1.05 |
| veri.ledger_steps.main reads `<k>` as bash's `$((10#k))` does: `08` is the 8th, `0` returns 3, `18446744073709551617` wraps to the 1st, `99999999999999999999` wraps past the count and returns 3; and refuses with return 2 and the usage line for `<k>` empty, `-1`, ` 1` and `١` (tests/py/test_ledger_steps.py) ⟦criterion 7⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 84 | 0.98 |
| veri.ledger_steps.main passes bytes through as bash does: a `\xff` byte in a step's text reaches stdout as that byte, a NUL byte is dropped, and in a CRLF document the `\r` stays at the end of every text — `criterion 1` prints `c1\r`, a heading `## Acceptance criteria\r` still opens the section, and a `[x]` line ending ` ⟂ refactor pending\r` keeps its mark and is not pending (tests/py/test_ledger_steps.py) ⟦criterion 7⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 88 | 1.04 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 2 | 2 | 2 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 13 | 0 | 3 | 0 | 0 | 8 | 6 | 5 | 7 | 0 | 2 | 1 | 1 | 3 | 9 | 0 | 8 | 1 | 1 | 1 | 0 | 8 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 0 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 6 | 6 | 1 | 1 | 0 | 1 | 85 | 2 | 79 |
| fast | 41 | 38 | 38 | 36 | 36 | 38 | 39 | 38 | 40 | 38 | 39 | 38 | 40 | 38 | 35 | 36 | 37 | 35 | 36 | 38 | 38 | 38 | 40 | 40 | 36 | 37 | 35 | 34 | 36 | 37 | 37 | 38 | 39 | 36 | 37 | 37 | 39 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 0 | 13 | 14 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 594 | 1178 | 243031 | 33628068 | 4235182 | 45.47 |
