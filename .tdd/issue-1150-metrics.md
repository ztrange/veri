### 📊 Metrics — issue 1150

Wall time for the issue: 21750 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1227.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 10 | 1 | 2 | 1276 | 11966 | 42162 | 0.18 |
| red | 14 | 7 | 0 | 0 | 816 | 408 | 93 | 180 | 40512 | 4948372 | 712365 | 6.17 |
| green | 16 | 7 | 1 | 0 | 7568 | 598 | 150 | 296 | 55648 | 8362019 | 805350 | 7.63 |
| refactor | 14 | 7 | 0 | 0 | 1308 | 203 | 54 | 104 | 16122 | 2273294 | 641228 | 4.59 |
| rebase | 4 | 2 | 0 | 0 | 4527 | 104 | 36 | 72 | 9242 | 1864873 | 196176 | 1.69 |
| predicate | 4 | 0 | 0 | 0 | 94 | 62 | 14 | 28 | 4723 | 598600 | 176137 | 1.62 |
| structural | 3 | 0 | 0 | 0 | 306 | 77 | 20 | 40 | 6786 | 1008765 | 141420 | 1.47 |
| transform | 2 | 2 | 0 | 0 | 1274 | 45 | 14 | 28 | 3913 | 680314 | 90830 | 0.54 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 27 | 26 | 1 | 0 | 8910 | 409 | 133 | 260 | 40612 | 6039776 | 1214070 | 6.47 |
| developer | claude-opus-5-5 | 31 | 0 | 0 | 0 | 6999 | 1098 | 249 | 490 | 97610 | 13708427 | 1591598 | 17.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 571 | 1.55 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The shared entry point `veri/entry.py` exits with the code a faked `main` returns, for each of 0, 1, 2 and 3, and lets a `SystemExit` raised inside `main` through with its own code unchanged (in-process pytest in `tests/py/test_entry.py`) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 101 | 30 | 60 | 9723 | 1487653 | 280769 | 2.19 | 571 | unknown | 0/5 | nothing-left |  |  | full |
| The shared entry point turns an `Exception` escaping a faked `main` into exit 2 with exactly one stderr line, `<script>.sh: <ExceptionType>: <message folded to one line>`, where `<script>.sh` is derived from the calling module's file name (`render_leaf_log.py` → `render-leaf-log.sh`), and prints no `Traceback` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 124 | 34 | 64 | 11590 | 1539211 | 271873 | 2.16 | 562 | unknown | 0/5 | structural-owed |  |  | full |
| The shared entry point flushes stdout inside its guard, so a stdout write failure that would otherwise surface only at interpreter shutdown (Python's exit 120) exits 2 with the same one stderr line instead | 6 | 3 | 0 | 0 | 0 | 0 | 124 | 32 | 64 | 10390 | 1515994 | 268667 | 2.11 | 648 | unknown | 0/5 | nothing-left |  |  | full |
| The shared entry point turns a `BrokenPipeError` on stdout into exit 141 with nothing on stdout or stderr, the one exception it does not map to 2 ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 169 | 43 | 86 | 15291 | 2072248 | 368269 | 2.92 | 833 | 1/2 | 0/5 | structural-owed |  |  | full |
| Every module a shim under `skills/tdd/scripts/` `exec`s calls the shared entry point from its `__main__` block in place of `sys.exit(main(sys.argv[1:]))`, `status.py`'s own traceback-printing wrapper replaced by it, and a module's existing `__main__`-level handling (`orchestrate.py`'s stdout-gone exit 2, `run_suite.py`'s SIGTERM handler) keeping its behaviour; proven through a real shim: `structural-predicate.sh` with stdin a directory exits 2 with exactly one stderr line beginning `structural-predicate.sh: ` and no `Traceback` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 257 | 57 | 110 | 25742 | 3220680 | 326595 | 3.14 | 3591 | unknown | 0/5 | structural-owed |  |  | full |
| A guard suite fails the run naming `<module>:<line>` when a module named by a shim's `exec python3 …/veri/<module>.py` line has a `__main__` block that does not go through the shared entry point, reading sources as text and starting no process; a plant suite watches it go red over a scratch tree holding a shim plus a bare `sys.exit(main(...))` module, and green once the offender is removed ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 189 | 39 | 74 | 17724 | 1911917 | 306445 | 2.57 | 615 | unknown | 0/5 | malformed |  |  | full |
| fix the full-suite failure: no-nested-suites.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another real suite outside the exemptions recorded here (ported-entry-guard.test.sh:18 and :138 name ported-entry-point.test.sh); hermetic-suites.test.sh — FAIL - #954: leaf-timeout.test.sh run inside a run worktree with VERI_ISSUE=954 in its environment, as a leaf's test run is, leaves no .tdd/issue-954-timeout in that worktree (leaf-timeout.test.sh 0 passed, 6 failed); watch.test.sh — FAIL - make watch: reruns make unit once per detected change, never between changes ⟦suite-repair⟧ ⟦criterion 2⟧ | 19 | 7 | 0 | 0 | 0 | 0 | 533 | 146 | 290 | 46486 | 7988534 | 940888 | 8.62 | 3315 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The shared entry point `veri/entry.py` exits with the code a faked `main` returns, for each of 0, 1, 2 and 3, and lets a `SystemExit` raised inside `main` through with its own code unchanged (in-process pytest in `tests/py/test_entry.py`) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 132 | 0.58 |
| The shared entry point turns an `Exception` escaping a faked `main` into exit 2 with exactly one stderr line, `<script>.sh: <ExceptionType>: <message folded to one line>`, where `<script>.sh` is derived from the calling module's file name (`render_leaf_log.py` → `render-leaf-log.sh`), and prints no `Traceback` ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 133 | 0.59 |
| The shared entry point flushes stdout inside its guard, so a stdout write failure that would otherwise surface only at interpreter shutdown (Python's exit 120) exits 2 with the same one stderr line instead | 1 | 0/5 | nothing-left | PASS | 0 | 252 | 0.60 |
| The shared entry point turns a `BrokenPipeError` on stdout into exit 141 with nothing on stdout or stderr, the one exception it does not map to 2 ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 142 | 0.65 |
| Every module a shim under `skills/tdd/scripts/` `exec`s calls the shared entry point from its `__main__` block in place of `sys.exit(main(sys.argv[1:]))`, `status.py`'s own traceback-printing wrapper replaced by it, and a module's existing `__main__`-level handling (`orchestrate.py`'s stdout-gone exit 2, `run_suite.py`'s SIGTERM handler) keeping its behaviour; proven through a real shim: `structural-predicate.sh` with stdin a directory exits 2 with exactly one stderr line beginning `structural-predicate.sh: ` and no `Traceback` ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 166 | 0.80 |
| A guard suite fails the run naming `<module>:<line>` when a module named by a shim's `exec python3 …/veri/<module>.py` line has a `__main__` block that does not go through the shared entry point, reading sources as text and starting no process; a plant suite watches it go red over a scratch tree holding a shim plus a bare `sys.exit(main(...))` module, and green once the offender is removed ⟦criterion 2⟧ | 1 | 0/5 | malformed | PASS | 0 | 143 | 0.72 |
| fix the full-suite failure: no-nested-suites.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another real suite outside the exemptions recorded here (ported-entry-guard.test.sh:18 and :138 name ported-entry-point.test.sh); hermetic-suites.test.sh — FAIL - #954: leaf-timeout.test.sh run inside a run worktree with VERI_ISSUE=954 in its environment, as a leaf's test run is, leaves no .tdd/issue-954-timeout in that worktree (leaf-timeout.test.sh 0 passed, 6 failed); watch.test.sh — FAIL - make watch: reruns make unit once per detected change, never between changes ⟦suite-repair⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 340 | 0.64 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 2/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 6 | 0 | 0 | 0 | 11 | 0 | 3 | 3 | 0 | 1 | 9 | 1 | 1 | 0 | 0 | 8 | 103 | 1 | 3 | 0 | 8 | 7 | 1 | 1 | 1 | 0 | 893 | 847 | 1 | 4 | 0 | 24 | 1 | 1 | 0 | 0 | 1 | 183 | 4 | 36 | 150 | 1224 | 6 | 98 | 77 | 1213 | 21 | 13 |
| fast | 101 | 102 | 105 | 101 | 101 | 103 | 99 | 94 | 114 | 96 | 101 | 107 | 95 | 95 | 91 | 99 | 92 | 85 | 93 | 94 | 94 | 102 | 102 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 0 | 99 | 3 | 1 | 0 | 31 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 1194 | 1190 | 1194 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 382 | 750 | 138222 | 19748203 | 2805668 | 23.90 |
