### 📊 Metrics — issue 1621

Wall time for the issue: 5147 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1699.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1131 | 12193 | 28882 | 0.13 |
| red | 12 | 5 | 0 | 0 | 313 | 240 | 76 | 148 | 27997 | 3242480 | 481797 | 2.53 |
| green | 17 | 3 | 5 | 0 | 3418 | 415 | 132 | 256 | 45021 | 5808290 | 628647 | 4.32 |
| exhausted | 1 | 0 | 0 | 0 | 36 | 23 | 4 | 8 | 2051 | 148829 | 35979 | 0.36 |
| refactor | 6 | 3 | 0 | 0 | 2092 | 141 | 48 | 96 | 15540 | 2614228 | 247647 | 1.41 |
| pin | 2 | 2 | 0 | 0 | 36 | 25 | 8 | 16 | 2723 | 295474 | 69455 | 0.33 |
| predicate | 1 | 0 | 0 | 0 | 14 | 10 | 3 | 6 | 993 | 101990 | 32791 | 0.15 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 19 | 14 | 5 | 0 | 2954 | 349 | 114 | 220 | 38337 | 4637109 | 652859 | 3.46 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 2006 | 323 | 104 | 206 | 38427 | 5215472 | 556500 | 3.13 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 961 | 191 | 54 | 106 | 18692 | 2370903 | 315839 | 2.64 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 88 | 0.79 |
| green | 249 | 1.25 | 2215 | 2.10 |
| exhausted | 0 | 0.00 | 36 | 0.36 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A new script `wrong-test-route.sh <green-report> <red-test-id>` (a ported `/bin/sh` shim over a `veri/` module, unit-tested in-process) decides the leaf that follows a green whose report carries `WRONG_TEST:`: when that line names an existing test case other than the step's own red test id, it prints `red <case>` and exits 0 (route to a red that updates that case, spending no revise attempt); when the report has no `WRONG_TEST:` line, or its line names no case or only the step's own red test, it prints `revise` and exits 3; an unreadable report or bad arguments exit 2 with nothing on stdout. Pinned by a case where a green's `WRONG_TEST:` names a contradicted case and the answer is a red over that case, not a revise. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard); if an existing test pins behaviour this changes, Red moves that test's expectation. ⟦criterion 1⟧ | 5 | 1 | 1 | 0 | 0 | 0 | 97 | 28 | 54 | 10894 | 1124418 | 189437 | 1.14 | unknown | 1/2 | unknown | unknown |  |  | full |
| `wrong-test-route.sh <green-report> <red-test-id>` (a ported `/bin/sh` shim over a `veri/` module, unit-tested in-process) prints `red <case>` and exits 0 when the green report's `WRONG_TEST:` line names an existing test case other than the step's own red test id. Pinned by a case where a green's `WRONG_TEST:` names a contradicted case and the answer is a red over that case, not a revise. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦added⟧ ⟦criterion 1⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 178 | 52 | 104 | 18578 | 2211881 | 287667 | 2.10 | unknown | 2/2 | unknown | unknown |  |  | full |
| A new script `wrong-test-route.sh <green-report> <red-test-id>` (a ported `/bin/sh` shim over a `veri/` module, unit-tested in-process) decides the leaf that follows a green whose report carries `WRONG_TEST:`, and lands in this one step together with its usage contract and its SKILL.md caller (ledger re-cut by coordinator ruling, #1700: the repo-wide audits `missing-argument-exit.test.sh` and `test_unreachable.py` make a script without its usage line or without a caller unpassable). When the `WRONG_TEST:` line names an existing test case other than the step's own red test id, it prints `red <case>` and exits 0 (route to a red that updates that case, spending no revise attempt); pinned by a case where a green's `WRONG_TEST:` names a contradicted case and the answer is a red over that case, not a revise. It prints `revise` and exits 3, each pinned by its own case, when: the report has no `WRONG_TEST:` line; the line names no test case; the line names only the step's own red test id; the line names a test case that does not exist. Called with no arguments, the wrong number of arguments or an empty argument, it exits 2 with a usage line `usage: wrong-test-route.sh <green-report> <red-test-id>` on stderr and nothing on stdout; an unreadable report (a directory given where a file is expected, never a permission bit) exits 2 with nothing on stdout. SKILL.md's Green section names `wrong-test-route.sh` as the check run on a green report carrying `WRONG_TEST:` before any revise, so the script has a caller. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard); if an existing test pins behaviour this changes, Red moves that test's expectation. ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 119 | 40 | 74 | 13838 | 1639412 | 239072 | 1.26 | 396 | unknown | 0/5 | nothing-structural |  |  | full |
| wrong-test-route.sh prints `revise` and exits 3, each pinned by its own in-process case in tests/py/unit/test_wrong_test_route.py, when: the green report has no `WRONG_TEST:` line; the line names no test case; the line names only the step's own red test id; the line names a test case that does not exist. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 10 | 20 | 4010 | 404753 | 73117 | 0.37 | unknown | unknown | unknown | unknown |  |  | pin |
| wrong-test-route.sh called with no arguments, the wrong number of arguments or an empty argument exits 2 with `usage: wrong-test-route.sh <green-report> <red-test-id>` on stderr and nothing on stdout, and given a directory where the report file is expected (never a permission bit) exits 2 with nothing on stdout; each pinned by its own in-process case in tests/py/unit/test_wrong_test_route.py. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard). ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 12 | 24 | 4068 | 512200 | 74945 | 0.39 | unknown | unknown | unknown | unknown |  |  | pin |
| `build-develop-prompt.sh red-contradicted <spec-file> <step-text> <test-cmd> <case>` builds a red prompt from a versioned template that tells the leaf to update the expectation of the named existing case to the step's criterion (editing that case only, writing no new test and no production code), run the suite holding it, and report the same footer a red does — `TEST_PATH:`, `TARGET_TEST:` naming that case, `AGAINST_UNMODIFIED: FAILS | PASSES | UNTESTABLE`, `WHY:`, `FAIL_OUTPUT:`, and the prediction lines; a missing spec file or empty case exits 2 with no stdout. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard); if an existing test pins behaviour this changes, Red moves that test's expectation. ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 265 | 87 | 170 | 28638 | 4518640 | 364205 | 2.44 | 2373 | 1/2 | 1/5 | nothing-structural |  |  | full |
| SKILL.md's Green section (develop-green and revise-green alike) routes a `WRONG_TEST:` report through `wrong-test-route.sh` before any revise: on its exit 0 the conductor writes no `revise` mark and spends no `REVISE_BUDGET` attempt, launches the `red-contradicted` red over the printed case through the supervisor, verifies it with verify-red like any red, re-records the step's frozen tests with `tests-frozen.sh record --step` over both test paths, and then retries green; on exit 3 the existing revise path runs unchanged; on exit 2 it bails as a system failure. Pinned by a SKILL.md-reading case in the style of `skill-tests-frozen`, asserting the routing text names the script, the red launch and the absence of a revise. If an existing test pins behaviour this changes, Red moves that test's expectation. ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 128 | 42 | 84 | 14299 | 1799987 | 267873 | 1.39 | 958 | unknown | 0/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A new script `wrong-test-route.sh <green-report> <red-test-id>` (a ported `/bin/sh` shim over a `veri/` module, unit-tested in-process) decides the leaf that follows a green whose report carries `WRONG_TEST:`, and lands in this one step together with its usage contract and its SKILL.md caller (ledger re-cut by coordinator ruling, #1700: the repo-wide audits `missing-argument-exit.test.sh` and `test_unreachable.py` make a script without its usage line or without a caller unpassable). When the `WRONG_TEST:` line names an existing test case other than the step's own red test id, it prints `red <case>` and exits 0 (route to a red that updates that case, spending no revise attempt); pinned by a case where a green's `WRONG_TEST:` names a contradicted case and the answer is a red over that case, not a revise. It prints `revise` and exits 3, each pinned by its own case, when: the report has no `WRONG_TEST:` line; the line names no test case; the line names only the step's own red test id; the line names a test case that does not exist. Called with no arguments, the wrong number of arguments or an empty argument, it exits 2 with a usage line `usage: wrong-test-route.sh <green-report> <red-test-id>` on stderr and nothing on stdout; an unreadable report (a directory given where a file is expected, never a permission bit) exits 2 with nothing on stdout. SKILL.md's Green section names `wrong-test-route.sh` as the check run on a green report carrying `WRONG_TEST:` before any revise, so the script has a caller. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard); if an existing test pins behaviour this changes, Red moves that test's expectation. ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 59 | 0.33 |
| `build-develop-prompt.sh red-contradicted <spec-file> <step-text> <test-cmd> <case>` builds a red prompt from a versioned template that tells the leaf to update the expectation of the named existing case to the step's criterion (editing that case only, writing no new test and no production code), run the suite holding it, and report the same footer a red does — `TEST_PATH:`, `TARGET_TEST:` naming that case, `AGAINST_UNMODIFIED: FAILS | PASSES | UNTESTABLE`, `WHY:`, `FAIL_OUTPUT:`, and the prediction lines; a missing spec file or empty case exits 2 with no stdout. In a `tests/py/unit/` file no string argument may end in `test_<x>.py` or `.test.sh` (#1668 guard); if an existing test pins behaviour this changes, Red moves that test's expectation. ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 1985 | 0.75 |
| SKILL.md's Green section (develop-green and revise-green alike) routes a `WRONG_TEST:` report through `wrong-test-route.sh` before any revise: on its exit 0 the conductor writes no `revise` mark and spends no `REVISE_BUDGET` attempt, launches the `red-contradicted` red over the printed case through the supervisor, verifies it with verify-red like any red, re-records the step's frozen tests with `tests-frozen.sh record --step` over both test paths, and then retries green; on exit 3 the existing revise path runs unchanged; on exit 2 it bails as a system failure. Pinned by a SKILL.md-reading case in the style of `skill-tests-frozen`, asserting the routing text names the script, the red launch and the absence of a revise. If an existing test pins behaviour this changes, Red moves that test's expectation. ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 48 | 0.33 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 600 | 1 | 1 | 0 | 1 | 2 | 1 | 1 | 601 | 1 | 0 | 1 | 1 | 6 | 1 | 1 | 4 | 1 | 0 | 6 | 1 | 1 | 3 | 2 | 1 | 1 | 1 | 5 | 612 | 606 | 605 | 1 | 0 | 0 | 276 | 0 | 0 |
| fast | 1 | 16 | 16 | 16 | 16 | 16 | 16 | 15 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 17 | 15 | 16 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 16 | 0 | 0 | 0 | 16 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 272 | 532 | 95456 | 12223484 | 1525198 | 9.24 |
