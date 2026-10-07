### 📊 Metrics — issue 924

Wall time for the issue: 3104 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 13 of 17 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1087.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 28 | 25 | 1 | 2 | 3218 | 12001 | 43117 | 0.21 |
| red | 13 | 4 | 0 | 0 | 380 | 333 | 68 | 136 | 34421 | 3448697 | 667357 | 5.88 |
| pin | 5 | 5 | 0 | 0 | 97 | 79 | 24 | 48 | 8457 | 1139836 | 239246 | 1.27 |
| green | 8 | 4 | 0 | 0 | 371 | 183 | 52 | 100 | 17966 | 2626020 | 400756 | 3.23 |
| refactor | 10 | 4 | 1 | 0 | 327 | 173 | 54 | 108 | 16357 | 2688276 | 491714 | 3.76 |
| diff | 6 | 3 | 0 | 0 | 321 | 153 | 36 | 70 | 14460 | 1811168 | 304264 | 2.43 |
| predicate | 1 | 0 | 0 | 0 | 14 | 11 | 3 | 6 | 1031 | 121214 | 45337 | 0.41 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 22 | 21 | 1 | 0 | 727 | 371 | 108 | 214 | 38789 | 5139333 | 1060425 | 5.66 |
| developer | claude-opus-5-5 | 22 | 0 | 0 | 0 | 811 | 586 | 130 | 256 | 57121 | 6707879 | 1131366 | 11.54 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 156 | 1.48 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tests/unit/cover-outcome.test.sh holds a case, written against the bash script before the port, asserting that `cover-outcome.sh` fed a report with no `COVERED:` line exits 2 with nothing on stdout and stderr exactly the one line `cover-outcome: no COVERED: line found` ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 13 | 26 | 4233 | 672490 | 99015 | 0.80 | unknown | unknown | unknown | unknown |  |  | pin |
| cover-outcome.sh, run through a symlink to the skill directory and from another working directory, exits with the same code and prints the same stdout and stderr as when run in place, for a `COVERED: yes` report (exit 0) and a report with no `COVERED:` line (exit 2) — a case in tests/unit/cover-outcome.test.sh, written against the bash script before the port ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 9 | 18 | 5438 | 434839 | 101260 | 0.80 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_cover_outcome.py: veri.cover_outcome.main(argv), stdin faked in-process as bytes, returns 0 with stdout `widget.test.sh: a stubbed widget stays blue\n` for a report ending `COVERED: yes` then `CAUGHT_BY: widget.test.sh: a stubbed widget stays blue`, and the same 0 and stdout for `["--bogus"]` as for `[]`; returns 1 with nothing on stdout or stderr for `COVERED: no`; returns 2 with nothing on stdout and stderr `cover-outcome: no COVERED: line found\n` for a report with no `COVERED:` line; returns 3 with stdout `type-only: npx tsc --noEmit\n` for `COVERED: type-only` then `PROOF: npx tsc --noEmit`; every return inside 0–3; cover-outcome.sh is removed from migration slice 2's list in the same commit, the slice's other scripts staying: replaces 'migration slice 2 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 182 | 51 | 100 | 18791 | 2641817 | 409040 | 3.31 | 461 | 1/2 | 1/5 | nothing-structural |  |  | full |
| tests/unit/cover-outcome.test.sh's symlink case builds its scratch directory through the sourced harness rather than its own mktemp, so tests/unit/no-report-copies.test.sh's 'no suite builds its own scratch directory, exit trap or tmp git repository' passes and make unit is green, the symlink case's assertions unchanged ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 10 | 20 | 4595 | 492098 | 98966 | 0.77 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_report.py: veri.report.report_read(text, keys), imported in-process, returns a dict holding for each key the value of its last occurrence (`COVERED: no` then `COVERED: yes` gives `yes`), omits a key that never appears, matches a line only when it starts with exactly `<key>: ` at column 0 and case-sensitively (an indented key, `COVERED:yes` and `covered: yes` are not read; `COVERED:  yes` reads ` yes`), and takes a line for the first key in `keys` order it matches ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 146 | 41 | 82 | 14475 | 2156175 | 297807 | 2.47 | 289 | unknown | 1/5 | nothing-structural |  |  | full |
| veri.report.report_read splits lines on `\n` only: a `\r` stays in the value (`COVERED: yes\r\n` reads `yes\r`), a line holding `\v`, `\f`, `\x1c`, `\x85` or ` ` is not split there, a non-empty last line with no trailing newline is read, an empty text returns an empty dict, and no `str` input raises (tests/py/test_report.py) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 9 | 18 | 4484 | 429547 | 98380 | 0.76 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.cover_outcome.main reads the report through veri.report.report_read and pins the `COVERED:` branches the contract cases leave open: `COVERED: yes` with no `CAUGHT_BY:` line returns 0 printing exactly `\n`, and `COVERED: yes` with a `PROOF:` line still prints the `CAUGHT_BY:` value; an unknown `COVERED:` value (`Yes`, `YES`, `yes ` with a trailing space, `maybe`) and an empty `COVERED: ` value return 2 with nothing on stdout and stderr exactly `cover-outcome: no COVERED: line found\n`; `COVERED: no` with `CAUGHT_BY:` and `PROOF:` lines returns 1 printing nothing on either stream; the last `COVERED:` line wins (`COVERED: no` then `COVERED: yes` returns 0); a `COVERED: yes\r` line returns 2; an unterminated last line `COVERED: no` is read and returns 1 (tests/py/test_cover_outcome.py) ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 10 | 20 | 6547 | 502781 | 102311 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.cover_outcome.main pins the proof branches: `COVERED: unreachable` or `type-only` with no `PROOF:` line, an empty `PROOF: ` value, a `PROOF:NONE` line with no space (not read) or `PROOF: NONE` returns 2 with nothing on stdout and stderr exactly `cover-outcome: COVERED: <kind> without a PROOF: line\n`; `PROOF: none`, `PROOF: NONE ` with a trailing space and `PROOF: NONE — no caller` are proofs, returning 3 with stdout `<kind>: <proof>\n` and nothing on stderr; `COVERED: unreachable` with a proof prints `unreachable: <proof>\n` (tests/py/test_cover_outcome.py) ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 94 | 29 | 56 | 9304 | 1341849 | 297159 | 2.21 | 201 | unknown | 0/5 | nothing-left |  |  | full |
| veri.cover_outcome.main reads stdin and writes stdout and stderr as bytes: a report whose `CAUGHT_BY:` value holds byte `\xff` returns 0 writing that byte unchanged to stdout, and one whose `PROOF:` value holds it returns 3 writing it unchanged, never raising (tests/py/test_cover_outcome.py) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 104 | 26 | 52 | 9334 | 1231233 | 295135 | 2.17 | 211 | unknown | 0/5 | nothing-left |  |  | full |
| cover-outcome.sh is a /bin/sh shim that execs python3 on veri/cover_outcome.py once per invocation, holding no Python source, carrying a lowercase `usage: cover-outcome.sh (the cover leaf's report on stdin)` line in its header that names no `<…>` outside `[…]`, citing no issue number in any comment and carrying no `exit "$var"`; veri/cover_outcome.py imports `report_read` from the `report` module with no second copy of the reader and carries no wrapper turning an uncaught exception into exit 2; all 5 original cases of tests/unit/cover-outcome.test.sh pass with their assertions unmodified against the shim, under the guard as #710 left it; the commit touches test suites only in copy lines and stub libs, and comes before any cut ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 13 | 26 | 4967 | 693171 | 102209 | 0.84 | 147 | n/a | n/a | n/a |  |  | full |
| tests/unit/cover-outcome.test.sh holds the survivors and the floor — "COVERED: yes exits 0 printing CAUGHT_BY, COVERED: no exits 1, neither exits 2" (exits 0, 1, 2), "#679: COVERED: unreachable or type-only with a PROOF: line exits 3 printing '<kind>: <proof>'" (exit 3), the no-COVERED-line stderr case and the symlink case — with those cases' assertions unchanged; every other case ("#679: COVERED: unreachable or type-only with no PROOF: line or PROOF: NONE exits 2", "#679: COVERED: no with a PROOF: line still exits 1", "#679: a PROOF: line leaves COVERED: yes exiting 0 printing CAUGHT_BY, COVERED: no exiting 1 and no COVERED: line exiting 2") is removed, each replaced by a tests/py/test_cover_outcome.py case asserting the same return code and stdout, which the same commit adds if no earlier step did ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 13 | 26 | 5368 | 692341 | 105458 | 0.86 | 107 | n/a | n/a | n/a |  |  | full |
| tests/unit/missing-argument-exit.test.sh is changed only by removing cover-outcome.sh from slice 2's list; lib/report.sh, lib/exit-contract.sh, tests/skill-refactor-kind.test.sh, tests/structural-predicate.test.sh, tests/py/test_comment_class.py, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh and tests/no-python-in-ported-scripts.test.sh are unchanged in the branch's diff, and no suite other than tests/unit/cover-outcome.test.sh runs cover-outcome.sh through its entry point ⟦diff-checked⟧ ⟦criterion 6⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 53 | 13 | 24 | 5156 | 546870 | 141934 | 1.14 | 117 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tests/py/test_cover_outcome.py: veri.cover_outcome.main(argv), stdin faked in-process as bytes, returns 0 with stdout `widget.test.sh: a stubbed widget stays blue\n` for a report ending `COVERED: yes` then `CAUGHT_BY: widget.test.sh: a stubbed widget stays blue`, and the same 0 and stdout for `["--bogus"]` as for `[]`; returns 1 with nothing on stdout or stderr for `COVERED: no`; returns 2 with nothing on stdout and stderr `cover-outcome: no COVERED: line found\n` for a report with no `COVERED:` line; returns 3 with stdout `type-only: npx tsc --noEmit\n` for `COVERED: type-only` then `PROOF: npx tsc --noEmit`; every return inside 0–3; cover-outcome.sh is removed from migration slice 2's list in the same commit, the slice's other scripts staying: replaces 'migration slice 2 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 1 | 156 | 1.48 |
| tests/py/test_report.py: veri.report.report_read(text, keys), imported in-process, returns a dict holding for each key the value of its last occurrence (`COVERED: no` then `COVERED: yes` gives `yes`), omits a key that never appears, matches a line only when it starts with exactly `<key>: ` at column 0 and case-sensitively (an indented key, `COVERED:yes` and `covered: yes` are not read; `COVERED:  yes` reads ` yes`), and takes a line for the first key in `keys` order it matches ⟦criterion 4⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 87 | 0.90 |
| veri.cover_outcome.main pins the proof branches: `COVERED: unreachable` or `type-only` with no `PROOF:` line, an empty `PROOF: ` value, a `PROOF:NONE` line with no space (not read) or `PROOF: NONE` returns 2 with nothing on stdout and stderr exactly `cover-outcome: COVERED: <kind> without a PROOF: line\n`; `PROOF: none`, `PROOF: NONE ` with a trailing space and `PROOF: NONE — no caller` are proofs, returning 3 with stdout `<kind>: <proof>\n` and nothing on stderr; `COVERED: unreachable` with a proof prints `unreachable: <proof>\n` (tests/py/test_cover_outcome.py) ⟦criterion 7⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.72 |
| veri.cover_outcome.main reads stdin and writes stdout and stderr as bytes: a report whose `CAUGHT_BY:` value holds byte `\xff` returns 0 writing that byte unchanged to stdout, and one whose `PROOF:` value holds it returns 3 writing it unchanged, never raising (tests/py/test_cover_outcome.py) ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 41 | 0.66 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 3 | 0 | 3 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 7 | 15 |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 16 | 16 | 16 | 16 | 16 | 15 | 15 | 16 | 16 | 15 | 15 | 15 | 15 | 16 | 16 | 16 | 16 | 16 | 16 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 238 | 470 | 95910 | 11847212 | 2191791 | 17.19 |
