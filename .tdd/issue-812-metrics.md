### 📊 Metrics — issue 812

Wall time for the issue: 2508 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 12 of 16 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/996.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 21 | 1 | 2 | 2763 | 11866 | 39376 | 0.19 |
| red | 13 | 4 | 0 | 0 | 506 | 450 | 92 | 180 | 40215 | 4662557 | 639738 | 6.07 |
| pin | 5 | 5 | 0 | 0 | 84 | 70 | 19 | 38 | 7408 | 801053 | 223985 | 1.13 |
| green | 10 | 4 | 1 | 0 | 439 | 232 | 63 | 124 | 20922 | 3054919 | 425562 | 3.60 |
| refactor | 7 | 3 | 0 | 0 | 152 | 86 | 26 | 52 | 7168 | 1094701 | 315855 | 2.31 |
| diff | 6 | 3 | 0 | 0 | 297 | 166 | 41 | 80 | 16009 | 1988226 | 286292 | 2.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 21 | 20 | 1 | 0 | 577 | 328 | 91 | 180 | 33970 | 3976864 | 903622 | 4.75 |
| developer | claude-opus-5-5 | 21 | 0 | 0 | 0 | 924 | 697 | 151 | 296 | 60515 | 7636458 | 1027186 | 10.96 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 267 | 2.15 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tests/unit/criterion-finished.test.sh holds a case, written against the bash script before the port, asserting that `criterion-finished.sh` with no argument and with an empty argument exits 2 with nothing on stdout, stdin unread, and stderr exactly the one line `usage: criterion-finished.sh <k> < .tdd/issue-<n>.md` ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 13 | 26 | 5376 | 661128 | 93888 | 0.81 | unknown | unknown | unknown | unknown |  |  | pin |
| criterion-finished.sh, run through a symlink to the skill directory and from another working directory, exits with the same code and prints the same stdout and stderr as when run in place, for a finished criterion (exit 0), an unfinished one (exit 3) and no argument (exit 2) — a case in tests/unit/criterion-finished.test.sh, written against the bash script before the port ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 13 | 26 | 6506 | 664249 | 96820 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_criterion_finished.py: veri.criterion_finished.main(argv), stdin faked as bytes, returns 2 with nothing on stdout, stdin unread and stderr exactly `usage: criterion-finished.sh <k> < .tdd/issue-<n>.md` for `[]` and for `[""]`; returns 0 for `["1"]` over a ticked step `a` tagged with the criterion-1 marker and 3 for `["1"]` over the same step unticked; every return inside 0–3; criterion-finished.sh is removed from migration slice 2's list in the same commit, the slice's other scripts staying: replaces 'migration slice 2 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 13 | 5 | 1 | 0 | 0 | 0 | 310 | 76 | 148 | 26561 | 3647943 | 572816 | 4.80 | 574 | 1/2 | 0/5 | nothing-left |  |  | full |
| veri.criterion_finished.main compares `k` to each step's criterion as a string, as bash's quoted `==` does: `["01"]` does not match the criterion-1 marker and a criterion-01 marker matches only `["01"]`; `["1 "]` and `["*"]` match nothing; a criterion marker whose digit is the full-width `１` serves nothing — each returning 3; extra arguments are ignored (`["1", "junk"]` answers as `["1"]`) (tests/py/test_criterion_finished.py) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 12 | 24 | 4903 | 585901 | 93189 | 0.77 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.criterion_finished.main takes a step's first criterion marker as its criterion — a ticked step `a` carrying the criterion-1 marker then the criterion-2 marker finishes 1 (return 0) and serves 2 not at all (return 3), and a ticked step whose criterion-1 marker is followed directly by `x` finishes 1; the first open or pending serving step returns 3, `[X]` counts as ticked, a step serving no criterion or empty stdin returns 3, `* [x]` and `- [ ]b` are not steps, `-<TAB>[ ]` is, and the last line counts without a trailing newline (tests/py/test_criterion_finished.py) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 13 | 26 | 6132 | 661633 | 97338 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.criterion_finished.main reads stdin as bytes, as bash's read does: a NUL byte is dropped, a `\xff` byte in a step line keeps the line (decoded with surrogateescape, never raising), and `\r\n` is kept — a ticked serving step ending ` ⟂ refactor pending\r\n`, or ` ⟂ refactor pending ` with a trailing space, reads finished (return 0) while a CRLF open serving step returns 3 (tests/py/test_criterion_finished.py) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 143 | 30 | 60 | 12621 | 1415233 | 284944 | 2.24 | 259 | unknown | 0/5 | nothing-left |  |  | full |
| veri.criterion_finished.main, with sys.stdin set to None as Python leaves it when fd 0 is closed, returns 3 printing nothing on stdout or stderr, rather than raising (tests/py/test_criterion_finished.py, faking only the standard streams) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 106 | 32 | 62 | 8914 | 1434676 | 270312 | 2.06 | 209 | unknown | 0/5 | nothing-left |  |  | full |
| veri.criterion_finished.main reads its steps through the `ledger` module (`ledger.ledger_steps(text)`), so with `sys.modules["ledger"].ledger_steps` faked to return a done record serving criterion 1 for a ledger whose markdown holds only the open step `found open in the markdown` tagged with the criterion-1 marker, `main(["1"])` returns 0: replaces 'criterion 1 is finished when lib/ledger.sh'"'"'s ledger_steps says so: exits 0 (#495)' in skills/tdd/scripts/tests/unit/criterion-finished.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 11 | 22 | 4700 | 542467 | 95833 | 0.77 | unknown | unknown | unknown | unknown |  |  | pin |
| criterion-finished.sh is a /bin/sh shim that execs python3 on veri/criterion_finished.py once per invocation, holding no Python source, carrying a lowercase `usage: criterion-finished.sh <k> < .tdd/issue-<n>.md` line in its header, citing no issue number in any comment and carrying no `exit "$var"`; veri/criterion_finished.py imports the `ledger` module with no second copy of the step grammar and carries no wrapper turning an uncaught exception into exit 2; every remaining case of tests/unit/criterion-finished.test.sh passes with its assertions unmodified against the shim, under the guard as #710 left it; the commit touches test suites only in copy lines and stub libs, and comes before any cut ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 12 | 24 | 4293 | 593997 | 95598 | 0.77 | 102 | n/a | n/a | n/a |  |  | full |
| tests/unit/criterion-finished.test.sh holds the survivors and the floor — the two-steps-serve-criterion-1 case (exits 3 and 0), the exit-2 usage case (exit 2 and its stderr byte for byte) and the symlink case — with those cases' assertions unchanged; every other case ("a step serving no criterion makes no criterion finished", "an unchecked ⟦added⟧ step serving criterion 1 keeps it unfinished", "a ticked untagged step whose text is 3 does not finish criterion 3") is removed, each replaced by a tests/py/test_criterion_finished.py case asserting the same return code, which the same commit adds if no earlier step did ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 12 | 24 | 5337 | 602567 | 99088 | 0.81 | 104 | n/a | n/a | n/a |  |  | full |
| tests/unit/missing-argument-exit.test.sh is changed only by removing criterion-finished.sh from slice 2's list; tests/unit/emitted-text.test.sh, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh, lib/ledger.sh, lib/exit-contract.sh and veri/ledger.py are unchanged in the branch's diff ⟦diff-checked⟧ ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 17 | 32 | 6379 | 791662 | 91606 | 0.82 | 134 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tests/py/test_criterion_finished.py: veri.criterion_finished.main(argv), stdin faked as bytes, returns 2 with nothing on stdout, stdin unread and stderr exactly `usage: criterion-finished.sh <k> < .tdd/issue-<n>.md` for `[]` and for `[""]`; returns 0 for `["1"]` over a ticked step `a` tagged with the criterion-1 marker and 3 for `["1"]` over the same step unticked; every return inside 0–3; criterion-finished.sh is removed from migration slice 2's list in the same commit, the slice's other scripts staying: replaces 'migration slice 2 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 63 | 1.02 |
| tests/py/test_criterion_finished.py: veri.criterion_finished.main(argv), stdin faked as bytes, returns 2 with nothing on stdout, stdin unread and stderr exactly `usage: criterion-finished.sh <k> < .tdd/issue-<n>.md` for `[]` and for `[""]`; returns 0 for `["1"]` over a ticked step `a` tagged with the criterion-1 marker and 3 for `["1"]` over the same step unticked; every return inside 0–3; criterion-finished.sh is removed from migration slice 2's list in the same commit, the slice's other scripts staying: replaces 'migration slice 2 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 2 | 0/5 | nothing-left |  | 0 | 0 | 0.00 |
| veri.criterion_finished.main reads stdin as bytes, as bash's read does: a NUL byte is dropped, a `\xff` byte in a step line keeps the line (decoded with surrogateescape, never raising), and `\r\n` is kept — a ticked serving step ending ` ⟂ refactor pending\r\n`, or ` ⟂ refactor pending ` with a trailing space, reads finished (return 0) while a CRLF open serving step returns 3 (tests/py/test_criterion_finished.py) ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 44 | 0.67 |
| veri.criterion_finished.main, with sys.stdin set to None as Python leaves it when fd 0 is closed, returns 3 printing nothing on stdout or stderr, rather than raising (tests/py/test_criterion_finished.py, faking only the standard streams) ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 45 | 0.62 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 2 | 3 | 2 | 2 | 1 | 2 | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 4 | 1 | 1 | 1 | 0 | 0 | 1 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 |
| target | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 15 | 15 | 16 | 15 | 15 | 16 | 17 | 15 | 14 | 14 | 14 | 14 | 15 | 15 | 15 | 15 | 15 | 15 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 242 | 476 | 94485 | 11613322 | 1930808 | 15.71 |
