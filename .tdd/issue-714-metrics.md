### 📊 Metrics — issue 714

Wall time for the issue: 3970 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 11 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/755.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 18 | 3 | 6 | 1763 | 118433 | 43726 | 0.41 |
| red | 10 | 1 | 0 | 0 | 555 | 448 | 93 | 186 | 42140 | 5161960 | 527220 | 6.09 |
| green | 4 | 1 | 1 | 0 | 495 | 224 | 44 | 86 | 23750 | 2399848 | 165560 | 2.28 |
| refactor | 2 | 1 | 0 | 0 | 117 | 62 | 13 | 26 | 4459 | 623625 | 88892 | 0.93 |
| pin | 8 | 8 | 0 | 0 | 285 | 214 | 43 | 86 | 19548 | 1949592 | 358121 | 3.65 |
| diff | 4 | 2 | 0 | 0 | 129 | 67 | 17 | 32 | 6496 | 692767 | 178859 | 1.70 |
| predicate | 2 | 0 | 0 | 0 | 44 | 33 | 7 | 14 | 3056 | 282769 | 81900 | 0.77 |
| structural | 2 | 0 | 0 | 0 | 99 | 43 | 12 | 24 | 4093 | 551103 | 84123 | 0.87 |
| transform | 2 | 2 | 0 | 0 | 53 | 33 | 9 | 18 | 3331 | 384532 | 83009 | 0.81 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 17 | 16 | 1 | 0 | 729 | 437 | 93 | 182 | 41672 | 4228326 | 721683 | 7.45 |
| developer | claude-opus-5-5 | 18 | 0 | 0 | 0 | 1071 | 705 | 148 | 296 | 66964 | 7936303 | 889727 | 10.05 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 495 | 2.28 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| veri.unreachable.main(argv) returns 0 and prints the unreachable scripts for a fixture repo with an orphan, and returns 2 with `usage: unreachable.sh <repo-root>` on stderr for [] (tests/py/test_unreachable.py); unreachable.sh becomes a /bin/sh shim that execs python3 on veri/unreachable.py once per invocation, holding no Python source, keeping a lowercase `usage: unreachable.sh <repo-root>` header line and citing no issue number in any comment, with no wrapper turning an uncaught exception into exit 2; every case in tests/unreachable.test.sh passes with its assertions unmodified, the case "make unreachable runs unreachable.sh over the repository it is run in …" adding veri/ to what it copies and nothing else changing in that suite ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 348 | 71 | 140 | 34325 | 3800890 | 356667 | 4.30 | 808 | 1/2 | 1/5 | structural-owed |  |  | full |
| unreachable.sh, run through a symlink to the skill directory and from another working directory, prints the same listing and exit code as when run in place (a case in tests/unreachable.test.sh) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 79 | 14 | 28 | 7045 | 710847 | 95820 | 1.05 | unknown | unknown | unknown | unknown |  |  | pin |
| unreachable.sh with no argument exits 2 with empty stdout and exactly `usage: unreachable.sh <repo-root>` on stderr (a case in tests/unreachable.test.sh) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 16 | 32 | 5353 | 806103 | 91217 | 1.00 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_unreachable.py asserts through veri.unreachable.main what 'scripts reached by no entry point are listed, including an orphan whose only caller is another orphan', 'an orphan whose name is the tail of a reached script's name is still listed' and 'a name alone on its line is a mention; one glued to a letter, digit, _ or - on either side, or to a . before it, is not' assert ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 18 | 36 | 7146 | 960630 | 99497 | 1.13 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_unreachable.py asserts through veri.unreachable.main what 'a script reached only from a procedure file, only from a Makefile recipe, or only from a git hook, directly or through a chain of scripts or a sourced lib/ file, is not listed', 'a repo with no git hooks directory is listed with nothing on stderr' and 'a repo with no lib/ directory is listed with nothing on stderr, even when a script is named lib.sh' assert ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 13 | 26 | 6668 | 673709 | 101179 | 1.08 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_unreachable.py asserts through veri.unreachable.main what the three built-path cases assert: 'a script named only through a built path such as "$S/build-$kind-prompt.sh" is not listed', 'a script named only through a braced built path such as "$S/build-${kind}-prompt.sh" is not listed' and 'a procedure file named only through a built path such as prompts/develop-$phase.md is read, so the script it names is not listed' ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 14 | 28 | 5769 | 704303 | 94688 | 1.01 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_unreachable.py asserts through veri.unreachable.main what 'a script whose only caller is its own test suite is listed as test-only, apart from the unreachable ones, and no file is deleted or modified', 'a VERI_* knob or a script name SKILL.md or CLAUDE.md promises and no script reads, or that does not exist, is listed as promised-unread', 'with neither SKILL.md nor CLAUDE.md there is nothing promised, so stdin is never read as a promise' and 'a scripts tree with no lib/ is searched for knobs without an error for the missing directory' assert ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 71 | 15 | 30 | 7322 | 791278 | 99132 | 1.10 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_unreachable.py asserts through veri.unreachable.main what 'this repository's scripts are each reached from a declared entry point, so the check lists no unreachable script in it' asserts ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 92 | 19 | 38 | 8544 | 1025472 | 102116 | 1.19 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_unreachable.py pins the behaviour the port keeps through veri.unreachable.main: nothing under scripts/veri/ is read, so a script called only from a veri/ module is `test-only` and a knob read only in Python is `promised-unread`; a test-only mention under scripts/tests/py/ counts; output is unreachable names in glob order, then promised-unread knobs, then promised-unread script names, each sorted and deduplicated in byte order; a <repo-root> that does not exist prints nothing and returns 0 ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 13 | 26 | 7725 | 661793 | 99477 | 1.08 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/unreachable.test.sh keeps only the survivor 'reached scripts that call each other are visited once, so the listing finishes', the floor — one exit-0 listing case ('scripts reached by no entry point are listed, including an orphan whose only caller is another orphan'), the exit-2 no-argument case with its stderr text, the symlink case — and the Makefile entry-point case 'make unreachable runs unreachable.sh over the repository it is run in …'; every other case, each replaced by a tests/py/test_unreachable.py case, is removed, and no remaining case's assertions changed ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 10 | 18 | 3574 | 414677 | 96382 | 0.93 | 70 | unknown | unknown | unknown |  |  | full |
| the Makefile, tests/unit/missing-argument-exit.test.sh, tests/unit/comment-class.test.sh, tests/unit/exit-contract.test.sh and tests/no-python-in-ported-scripts.test.sh are unchanged by the branch, and no suite other than tests/unreachable.test.sh runs unreachable.sh through its entry point ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 7 | 14 | 2922 | 278090 | 82477 | 0.77 | 93 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.unreachable.main(argv) returns 0 and prints the unreachable scripts for a fixture repo with an orphan, and returns 2 with `usage: unreachable.sh <repo-root>` on stderr for [] (tests/py/test_unreachable.py); unreachable.sh becomes a /bin/sh shim that execs python3 on veri/unreachable.py once per invocation, holding no Python source, keeping a lowercase `usage: unreachable.sh <repo-root>` header line and citing no issue number in any comment, with no wrapper turning an uncaught exception into exit 2; every case in tests/unreachable.test.sh passes with its assertions unmodified, the case "make unreachable runs unreachable.sh over the repository it is run in …" adding veri/ to what it copies and nothing else changing in that suite ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 117 | 0.93 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 2/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 3 | 1 | 0 | 6 | 12 | 7 | 6 | 6 | 6 | 4 | 4 | 3 | 0 | 0 | 1 | 1 | 0 | 2 | 4 | 1 | 37 | 1 | 3 | 3 | 0 | 3 | 33 | 3 |
| fast | 29 | 27 | 28 | 29 | 28 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 3 | 3 | 3 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 0 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 241 | 478 | 108636 | 12164629 | 1611410 | 17.50 |
