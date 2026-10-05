### 📊 Metrics — issue 925

Wall time for the issue: 3374 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 11 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/941.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 54 | 50 | 3 | 6 | 5002 | 99213 | 52932 | 0.54 |
| red | 11 | 3 | 0 | 0 | 487 | 427 | 98 | 192 | 41798 | 4610118 | 470816 | 5.53 |
| pin | 5 | 5 | 0 | 0 | 164 | 135 | 29 | 58 | 13993 | 1229124 | 193420 | 2.07 |
| green | 10 | 3 | 2 | 0 | 615 | 305 | 90 | 178 | 31311 | 4153031 | 331775 | 4.11 |
| refactor | 6 | 3 | 0 | 0 | 196 | 108 | 27 | 54 | 10464 | 1093654 | 229035 | 2.26 |
| diff | 6 | 3 | 0 | 0 | 284 | 123 | 31 | 60 | 11859 | 1227447 | 219550 | 2.24 |
| predicate | 2 | 0 | 0 | 0 | 36 | 29 | 5 | 10 | 2569 | 164690 | 68918 | 0.64 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 20 | 18 | 2 | 0 | 893 | 546 | 124 | 244 | 55846 | 5288688 | 717369 | 7.91 |
| developer | claude-opus-5-5 | 21 | 0 | 0 | 0 | 943 | 631 | 159 | 314 | 61150 | 7288589 | 849077 | 9.47 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 514 | 3.25 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 36 | 0.64 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| next-unchecked.sh run through a symlink to the skill directory, from another working directory, prints the same first open step and exit code as run in place — a case in tests/unit/next-unchecked.test.sh, against the bash script ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 104 | 19 | 38 | 9335 | 929092 | 90093 | 1.09 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.next_unchecked.main([]) over the slugify ledger returns 0 printing "collapse non-alphanumerics to a single hyphen" and one newline with empty stderr, returns 3 with empty stdout and stderr over an all-done ledger, and answers ["--bogus"] as it answers []; next-unchecked.sh leaves slice 5's list: replaces 'migration slice 5 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 244 | 62 | 122 | 23562 | 2827120 | 289597 | 3.35 | 508 | 1/2 | 0/5 | nothing-left |  |  | full |
| veri.next_unchecked.main([]) over a ledger mixing an upper-case X box, a vertical-tab-indented step, full-suite, human-owed and diff-checked lines and a done step prints the text of the first record veri.ledger.ledger_steps returns whose state is open and kind step or diff-checked: replaces 'the first open ordinary step comes from lib/ledger.sh's ledger_steps (#495)' in skills/tdd/scripts/tests/unit/next-unchecked.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 226 | 62 | 122 | 22405 | 2806967 | 284611 | 3.29 | 433 | 1/2 | 0/5 | nothing-left |  |  | full |
| veri.next_unchecked.main prints the step text followed by exactly one newline, and an open step with no text (a bare box, or a box and one space) as an empty line with return 0 ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 13 | 26 | 5460 | 578903 | 77148 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.next_unchecked.main returns 3 with nothing on stdout for empty stdin, and keeps an open step's trailing refactor-pending mark in the text it prints ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 89 | 21 | 42 | 9678 | 1004712 | 85785 | 1.08 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.next_unchecked.main drops NUL bytes from stdin and prints a non-UTF-8 byte in a step's text back as that same byte ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 142 | 41 | 80 | 14668 | 1751566 | 235454 | 2.53 | 280 | unknown | 0/5 | structural-owed |  |  | full |
| veri.next_unchecked.main writes nothing on stderr on any path: a printed step, exit 3 for no step, and arguments given ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 12 | 24 | 4784 | 526601 | 76862 | 0.82 | unknown | unknown | unknown | unknown |  |  | pin |
| next-unchecked.sh becomes a /bin/sh shim that execs python3 on veri/next_unchecked.py, its header carrying a lowercase usage line that names no angle-bracket argument and no issue number; no assertion in tests/unit/next-unchecked.test.sh, tests/tick-ledger.test.sh, tests/add-ledger-step.test.sh or tests/skill-leaf-env.test.sh is changed ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 11 | 22 | 4935 | 466531 | 75129 | 0.79 | 171 | unknown | unknown | unknown |  |  | full |
| tests/py/test_next_unchecked.py asserts in-process, through main(argv) with stdin faked as bytes, what each of the thirteen non-floor contract cases of tests/unit/next-unchecked.test.sh asserts (no checkboxes, nested step, verbatim special chars, first line unchecked, owed bullets, full-suite and human-owed skipped, a quoted marker handed out, a written marker skipped, a written-plus-quoted marker skipped, a fully ticked quoting ledger, suite-repair handed out, diff-checked handed out) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 69 | 14 | 28 | 7674 | 660966 | 85496 | 0.97 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/unit/next-unchecked.test.sh keeps only the floor — "first unchecked description", "all checked exits 3" and the symlink case — every other case cut, and no assertion of a kept case changed ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 9 | 18 | 2587 | 362049 | 73411 | 0.71 | 59 | unknown | unknown | unknown |  |  | full |
| lib/ledger.sh and veri/ledger.py are unchanged by the branch, the seven other scripts still source lib/ledger.sh, and none of the suites the issue lists as passing unmodified is changed by the branch except missing-argument-exit.test.sh's slice-5 line ⟦diff-checked⟧ ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 11 | 20 | 4337 | 398867 | 71010 | 0.73 | 108 | unknown | unknown | unknown |  |  | full |
| the suites the issue lists as reading next-unchecked.sh's source or running it pass unmodified against the shim ⟦full-suite⟧ ⟦criterion 7⟧ | 2 | 0 | 0 | 0 | 0 | 0 | 29 | 5 | 10 | 2569 | 164690 | 68918 | 0.64 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.next_unchecked.main([]) over the slugify ledger returns 0 printing "collapse non-alphanumerics to a single hyphen" and one newline with empty stderr, returns 3 with empty stdout and stderr over an all-done ledger, and answers ["--bogus"] as it answers []; next-unchecked.sh leaves slice 5's list: replaces 'migration slice 5 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 73 | 0.75 |
| veri.next_unchecked.main([]) over a ledger mixing an upper-case X box, a vertical-tab-indented step, full-suite, human-owed and diff-checked lines and a done step prints the text of the first record veri.ledger.ledger_steps returns whose state is open and kind step or diff-checked: replaces 'the first open ordinary step comes from lib/ledger.sh's ledger_steps (#495)' in skills/tdd/scripts/tests/unit/next-unchecked.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 58 | 0.75 |
| veri.next_unchecked.main drops NUL bytes from stdin and prints a non-UTF-8 byte in a step's text back as that same byte ⟦criterion 6⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 65 | 0.76 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 4 | 0 | 6 | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 40 | 22 | 1 | 0 | 40 |
| target | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 19 | 19 | 20 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 20 | 20 | 20 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 283 | 558 | 116996 | 12577277 | 1566446 | 17.39 |
