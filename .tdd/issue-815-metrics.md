### 📊 Metrics — issue 815

Wall time for the issue: 3482 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 18 of 22 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1084.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 35 | 32 | 1 | 2 | 3870 | 12001 | 44015 | 0.22 |
| red | 20 | 6 | 0 | 0 | 588 | 519 | 114 | 224 | 49886 | 5843475 | 1043977 | 9.25 |
| pin | 8 | 8 | 0 | 0 | 127 | 102 | 31 | 62 | 10777 | 1395529 | 382647 | 1.92 |
| green | 14 | 6 | 1 | 0 | 641 | 356 | 92 | 182 | 33384 | 4867355 | 672995 | 5.66 |
| refactor | 12 | 6 | 0 | 0 | 329 | 201 | 57 | 112 | 18276 | 2751447 | 602290 | 4.51 |
| diff | 4 | 2 | 0 | 0 | 207 | 120 | 31 | 60 | 11881 | 1660837 | 209605 | 1.78 |
| predicate | 2 | 0 | 0 | 0 | 32 | 26 | 6 | 12 | 1378 | 244899 | 92012 | 0.81 |
| structural | 1 | 0 | 0 | 0 | 20 | 18 | 4 | 8 | 1632 | 181948 | 51246 | 0.48 |
| transform | 1 | 0 | 1 | 0 | 8 | 6 | 2 | 4 | 651 | 63254 | 44544 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 31 | 29 | 2 | 0 | 822 | 480 | 142 | 278 | 51052 | 6634544 | 1464300 | 7.70 |
| developer | claude-opus-5-5 | 32 | 0 | 0 | 0 | 1165 | 900 | 196 | 388 | 80683 | 10386201 | 1679031 | 17.12 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 218 | 1.64 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 32 | 0.81 |
| structural | 0 | 0.00 | 20 | 0.48 |
| transform | 0 | 0.00 | 8 | 0.20 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a case in tests/unit/clear-refactor-pending.test.sh runs clear-refactor-pending.sh with no argument and asserts exit 2, nothing on stdout and stderr exactly `usage: clear-refactor-pending.sh <ledger-file> <matcher>`, written against the bash script before the port ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 11 | 22 | 4010 | 565644 | 99551 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |
| a case in tests/unit/clear-refactor-pending.test.sh runs clear-refactor-pending.sh on a ledger path that does not exist and asserts exit 1 and nothing on stdout, written against the bash script before the port ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 9 | 18 | 3683 | 431963 | 98309 | 0.74 | unknown | unknown | unknown | unknown |  |  | pin |
| clear-refactor-pending.sh, run through a symlink to the skill directory and from another working directory with a relative `<ledger-file>`, clears the mark in the ledger under the caller's working directory with the same exit code and output as when run in place (a case in tests/unit/clear-refactor-pending.test.sh, written against the bash script before the port, inside the fast tier's admission bar) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 10 | 18 | 4685 | 435608 | 99632 | 0.77 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_clear_refactor_pending.py calls veri.clear_refactor_pending.main(argv) with no subprocess and asserts nothing on stdout and: return code 2 and stderr `usage: clear-refactor-pending.sh <ledger-file> <matcher>` for `[]` and `[""]`; return code 0 for `[<file>, "a"]` on a tmp_path file `- [x] a ⟂ refactor pending\n- [x] b ⟂ refactor pending\n`, the file then `- [x] a\n- [x] b ⟂ refactor pending\n`; return code 3 and the file byte-identical for `[<file>, "zeta"]`; in the same commit clear-refactor-pending.sh is removed from migration slice 1's list, build-develop-prompt.sh and build-verify-prompt.sh staying: replaces 'migration slice 1 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 210 | 47 | 94 | 19045 | 2542443 | 376393 | 3.21 | 402 | 1/2 | 0/5 | structural-owed |  |  | full |
| a tests/py/test_clear_refactor_pending.py case substitutes `ledger_clear_pending` on the top-level `ledger` module object veri.clear_refactor_pending imports it from (as veri/status.py:14 imports its sibling), never a function of veri.clear_refactor_pending itself, and asserts main([<file>, "collapse to single hyphen"]) returns 0, passes the substitute that matcher and writes what the substitute returns ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 12 | 24 | 4781 | 630863 | 102292 | 0.83 | unknown | unknown | unknown | unknown |  |  | pin |
| a tests/py/test_clear_refactor_pending.py case substitutes the `ledger` module's `ledger_clear_pending` with one handing back status 7 and asserts main returns 2 with the ledger byte-identical — the foreign transform status mapped into 0–3 as to_contract maps it ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 127 | 36 | 70 | 12066 | 1808170 | 307630 | 2.42 | 232 | unknown | 0/5 | structural-owed |  |  | full |
| veri.clear_refactor_pending.main reads its arguments as the bash script does: `[<file>]` alone reads the matcher as empty and clears the first marked done step, and arguments after the second are ignored (tests/py/test_clear_refactor_pending.py, files under tmp_path) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 108 | 30 | 60 | 9677 | 1465847 | 293623 | 2.21 | 203 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.clear_refactor_pending.main matches the matcher as a literal substring of the whole line: `refactor pending`, `[x] a` and `a ⟂` each clear the first marked done step whatever its text, and `*` matches only a literal `*` (tests/py/test_clear_refactor_pending.py) ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 7 | 14 | 4548 | 315331 | 101117 | 0.76 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.clear_refactor_pending.main returns 3 with the file byte-identical for an open step carrying the mark, a CRLF line whose mark is followed by `\r`, and a mark followed by a space; and a line ending in the mark twice loses only the last one (tests/py/test_clear_refactor_pending.py) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 168 | 42 | 82 | 16067 | 2219977 | 310881 | 2.61 | 264 | unknown | 1/5 | nothing-left |  |  | full |
| veri.clear_refactor_pending.main rewrites the ledger on a clear as bash's `printf '%s\n' "$(…)"` does — a ledger with no final newline gains one, one ending `\n\n\n` ends `\n` — while on return code 3 a `\n\n\n` ledger keeps its bytes and an empty file returns 3 and stays empty (tests/py/test_clear_refactor_pending.py) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 97 | 28 | 56 | 9249 | 1361606 | 299133 | 2.22 | 191 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.clear_refactor_pending.main drops a NUL byte on a clear — `- [x] a\0z ⟂ refactor pending\n` becomes `- [x] az\n`, return code 0, nothing on stderr — and passes a non-UTF-8 byte through in the file and in the matcher: the matcher `os.fsdecode(b"a\xff")` on `- [x] a\xff ⟂ refactor pending\n` returns 0 and leaves `- [x] a\xff\n` (tests/py/test_clear_refactor_pending.py, compared as bytes) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 109 | 30 | 58 | 10356 | 1436786 | 306916 | 2.32 | 203 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.clear_refactor_pending.main matches a step line by lib/ledger.sh's C-locale grammar: `[X]`, a tab after the dash, and spaces or `\f` before the dash clear the mark, while `\034` or U+00A0 before the dash returns 3 with the file byte-identical (tests/py/test_clear_refactor_pending.py) ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 11 | 22 | 4147 | 568509 | 102497 | 0.81 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.clear_refactor_pending.main writes the ledger in place: a symlinked ledger stays a symlink with its target rewritten, and a relative `<ledger-file>` is read from the working directory (tests/py/test_clear_refactor_pending.py, files under tmp_path) ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 11 | 22 | 5652 | 567756 | 103626 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.clear_refactor_pending.main on a ledger path that does not exist, on one that is a directory, and on one whose write-back is refused with PermissionError (forced at the file-open boundary, never by permission bits, which uid 0 ignores) raises out of main rather than returning a code — no wrapper turns an exception into exit 2, so the shim exits 1 as the bash script does — the refused ledger left byte-identical (tests/py/test_clear_refactor_pending.py) ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 10 | 20 | 4357 | 507303 | 100309 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |
| clear-refactor-pending.sh is a /bin/sh shim that execs python3 on veri/clear_refactor_pending.py once per invocation, holding no Python source (no heredoc, no `python3 -c`), keeping the lowercase header line `usage: clear-refactor-pending.sh <ledger-file> <matcher>`, citing no issue number and spelling neither the pending mark nor a box; veri/clear_refactor_pending.py imports ledger_clear_pending from veri/ledger.py with no second copy of the step grammar, starts no process, has no wrapper turning an uncaught exception into exit 2, and ports neither lib/exit-contract.sh nor lib/ledger.sh; in the same commit the two implementation cases are cut — 'clears through lib/ledger.sh's ledger_clear_pending' from tests/unit/clear-refactor-pending.test.sh and 'a foreign ledger-transform code exits 2 from clear-refactor-pending.sh' (with its stub setup) from tests/tick-ledger.test.sh — and no other test line changes, every remaining case of both suites passing with its assertions unmodified against the shim ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 70 | 18 | 36 | 6478 | 1040080 | 107956 | 0.98 | 133 | n/a | n/a | n/a |  |  | full |
| lib/ledger.sh, tests/unit/ledger.test.sh, tests/unit/emitted-text.test.sh, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh, tests/unit/pending-mark-literal.test.sh and tests/py/test_comment_class.py are unchanged by the branch; tests/unit/missing-argument-exit.test.sh is changed only by removing clear-refactor-pending.sh from migration slice 1's list; tests/tick-ledger.test.sh is changed only by removing the clear-refactor-pending.sh foreign-code case; tests/unit/clear-refactor-pending.test.sh keeps its two contract cases with assertions unchanged beside the exit-2, exit-1 and symlink cases ⟦diff-checked⟧ ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 13 | 24 | 5403 | 620757 | 101649 | 0.81 | 103 | n/a | n/a | n/a |  |  | full |
| make test is green, tests/unit/missing-argument-exit.test.sh, tests/unit/emitted-text.test.sh, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh, tests/unit/pending-mark-literal.test.sh and tests/unit/ledger.test.sh passing and tests/py/test_comment_class.py in the pytest leg ⟦full-suite⟧ ⟦criterion 7⟧ | 4 | 0 | 1 | 0 | 0 | 0 | 50 | 12 | 24 | 3661 | 490101 | 187802 | 1.49 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tests/py/test_clear_refactor_pending.py calls veri.clear_refactor_pending.main(argv) with no subprocess and asserts nothing on stdout and: return code 2 and stderr `usage: clear-refactor-pending.sh <ledger-file> <matcher>` for `[]` and `[""]`; return code 0 for `[<file>, "a"]` on a tmp_path file `- [x] a ⟂ refactor pending\n- [x] b ⟂ refactor pending\n`, the file then `- [x] a\n- [x] b ⟂ refactor pending\n`; return code 3 and the file byte-identical for `[<file>, "zeta"]`; in the same commit clear-refactor-pending.sh is removed from migration slice 1's list, build-develop-prompt.sh and build-verify-prompt.sh staying: replaces 'migration slice 1 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 55 | 0.73 |
| a tests/py/test_clear_refactor_pending.py case substitutes the `ledger` module's `ledger_clear_pending` with one handing back status 7 and asserts main returns 2 with the ledger byte-identical — the foreign transform status mapped into 0–3 as to_contract maps it ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 50 | 0.72 |
| veri.clear_refactor_pending.main reads its arguments as the bash script does: `[<file>]` alone reads the matcher as empty and clears the first marked done step, and arguments after the second are ignored (tests/py/test_clear_refactor_pending.py, files under tmp_path) ⟦criterion 6⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 48 | 0.69 |
| veri.clear_refactor_pending.main returns 3 with the file byte-identical for an open step carrying the mark, a CRLF line whose mark is followed by `\r`, and a mark followed by a space; and a line ending in the mark twice loses only the last one (tests/py/test_clear_refactor_pending.py) ⟦criterion 6⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 88 | 0.95 |
| veri.clear_refactor_pending.main rewrites the ledger on a clear as bash's `printf '%s\n' "$(…)"` does — a ledger with no final newline gains one, one ending `\n\n\n` ends `\n` — while on return code 3 a `\n\n\n` ledger keeps its bytes and an empty file returns 3 and stays empty (tests/py/test_clear_refactor_pending.py) ⟦criterion 6⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 42 | 0.69 |
| veri.clear_refactor_pending.main drops a NUL byte on a clear — `- [x] a\0z ⟂ refactor pending\n` becomes `- [x] az\n`, return code 0, nothing on stderr — and passes a non-UTF-8 byte through in the file and in the matcher: the matcher `os.fsdecode(b"a\xff")` on `- [x] a\xff ⟂ refactor pending\n` returns 0 and leaves `- [x] a\xff\n` (tests/py/test_clear_refactor_pending.py, compared as bytes) ⟦criterion 6⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 46 | 0.73 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 3 | 0 | 0 | 4 | 2 | 0 | 1 | 1 | 4 | 2 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | 0 |
| target | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 15 | 17 | 16 | 16 | 15 | 15 | 15 | 16 | 15 | 15 | 16 | 15 | 15 | 16 | 16 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 338 | 666 | 131735 | 17020745 | 3143331 | 24.82 |
