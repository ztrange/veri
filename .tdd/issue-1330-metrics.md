### 📊 Metrics — issue 1330

Wall time for the issue: 7508 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1560.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 17 | 3 | 6 | 1526 | 130600 | 50557 | 0.23 |
| red | 6 | 0 | 0 | 0 | 843 | 453 | 83 | 160 | 54881 | 5795819 | 411779 | 2.78 |
| pin | 6 | 6 | 0 | 0 | 145 | 102 | 28 | 56 | 9913 | 1326889 | 284428 | 1.37 |
| green | 10 | 5 | 0 | 0 | 2090 | 284 | 68 | 132 | 23029 | 3544200 | 471221 | 2.82 |
| refactor | 10 | 5 | 0 | 0 | 635 | 163 | 51 | 98 | 14640 | 2377252 | 481461 | 2.31 |
| diff | 5 | 1 | 1 | 0 | 1272 | 170 | 50 | 96 | 16567 | 2694601 | 263446 | 2.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 19 | 18 | 1 | 0 | 1562 | 365 | 107 | 202 | 36509 | 4996931 | 926829 | 4.57 |
| developer | claude-sonnet-5-5 | 16 | 0 | 0 | 0 | 2497 | 706 | 141 | 276 | 73325 | 8840059 | 872710 | 5.46 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 949 | 118 | 35 | 70 | 10722 | 2032371 | 163353 | 1.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 1188 | 1.57 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| dashboard.sh's page-content and roster behaviours are pinned by small pytest cases in tests/py/test_dashboard.py driving the CLI through run_cli or reading dashboard.html, asserting the same exit codes, stdout, stderr and files, faking only process boundaries, reusing an existing pytest case as the replacement where one already pins the behaviour, with no production change: replaces "make test runs this suite", "dashboard.html, read off disk, fetches the Runs, Metrics and Events endpoints", "dashboard.html, read off disk, schedules each pane's next request only from the previous one settling", "dashboard.html, read off disk, gives the Tests and Chatter panes an endpoint apiece to poll" in skills/tdd/scripts/tests/dashboard.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 178 | 46 | 88 | 18151 | 2402337 | 306182 | 1.65 | 578 | unknown | 1/5 | nothing-left |  |  | already-satisfied |
| dashboard.sh's serving behaviours are pinned by pytest cases in tests/py/test_dashboard.py asserting the same exit codes, responses, bind address and stdout, each case that needs a real listening server, a signal or a symlinked entry point marked @pytest.mark.process("<boundary>") as a medium case and every other case small through run_cli, faking only process boundaries, with no production change: replaces "dashboard.sh with no argument serves the page at / on port 8765 and exits 0 when sent SIGINT", "dashboard.sh with a port argument serves the page on that port, binds 127.0.0.1 only, and answers every pane endpoint with JSON", "the page dashboard.sh serves at / is dashboard.html, byte for byte", "/api/events answers while an /api/runs request is still blocked inside a process status starts", "dashboard.sh, run through a symlink to the skill directory and from another working directory, serves dashboard.html at / and status.sh --json's stdout at /api/runs" in skills/tdd/scripts/tests/dashboard.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 273 | 60 | 114 | 29432 | 3856213 | 345041 | 2.06 | 2075 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| status.sh's behaviours are pinned by pytest cases in tests/py/test_status.py driving the CLI through run_cli with solvable-issues.sh faked at the subprocess boundary (fake_processes), asserting the same exit codes, stdout and stderr, the symlinked-entry-point case marked @pytest.mark.process("<boundary>") and every other case small, with no production change: replaces "no runs under the main working tree prints 'no runs' and exits 3", "a run under .tdd/wt/* is listed with its issue number, title, branch and step n of m", "a run shows its state: running, done with its PR url, bailed with phase and classification, or stale", "--watch [seconds] redraws in place, recomputing every run from disk on each render", "#846: status.sh run through its entry point exits 2 on a failure veri/status.py turns into exit 2", "status.sh given a bad argument names it on stderr", "status.sh run through a symlink to the skill directory and from another working directory answers as it does when run in place" in skills/tdd/scripts/tests/status.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 216 | 39 | 76 | 18277 | 2273846 | 279445 | 1.88 | 856 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| metrics.sh's behaviours are pinned by pytest cases in tests/py/test_metrics.py driving the CLI through run_cli, asserting the same exit codes, stdout and stderr, the symlinked-entry-point case marked @pytest.mark.process("<boundary>") and every other case small, with no production change: replaces "#454 every By-step column that existed before, and every other section, reads the same for an existing log", "metrics.sh run through a symlink to the skill directory, from another working directory, answers with the same stdout and exit code as run in place, reading that directory's .tdd/ and never the skill's", "metrics.sh run in a working directory with no .tdd/events.jsonl exits 2 and prints nothing on stdout" in skills/tdd/scripts/tests/metrics.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 188 | 46 | 90 | 21012 | 2580700 | 331580 | 1.79 | 783 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| metrics.sh <n>, run through run_cli in a directory whose .tdd/issue-<n>.md holds bytes that are not UTF-8, exits 0 and prints its report, with nothing on stderr and no traceback — a small pytest case in tests/py/test_metrics.py ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 13 | 26 | 4631 | 677736 | 96668 | 0.50 | unknown | unknown | unknown | unknown |  |  | pin |
| render-leaf-log.sh's behaviours are pinned by pytest cases in tests/py/test_render_leaf_log.py driving the CLI through run_cli, asserting the same exit codes, stdout and stderr, the symlinked-entry-point case marked @pytest.mark.process("<boundary>") and every other case small, with no production change: replaces "renders text, tool calls and truncated results one per line", "exits 2 on a line that is not JSON", "a JSON line that is not an object exits 2, and an extra argument is ignored with the stdin still rendered and exit 0", "render-leaf-log.sh run through a symlink to the skill directory and from another working directory renders as it does when run in place" in skills/tdd/scripts/tests/render-leaf-log.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 102 | 26 | 52 | 10960 | 1253328 | 289973 | 1.39 | 542 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| Every bash suite this issue emptied (dashboard.test.sh, status.test.sh, metrics.test.sh, render-leaf-log.test.sh, whichever hold no case) is deleted, no guard table, exemption table, roster, workflow comment or CLAUDE.md count outside .tdd/ and docs/ still names it, CLAUDE.md's suite counts match the tree, and any suite left with cases still passes ⟦diff-checked⟧ ⟦criterion 3⟧ | 5 | 1 | 1 | 0 | 0 | 0 | 170 | 50 | 96 | 16567 | 2694601 | 263446 | 2.04 | 1363 | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| dashboard.sh's page-content and roster behaviours are pinned by small pytest cases in tests/py/test_dashboard.py driving the CLI through run_cli or reading dashboard.html, asserting the same exit codes, stdout, stderr and files, faking only process boundaries, reusing an existing pytest case as the replacement where one already pins the behaviour, with no production change: replaces "make test runs this suite", "dashboard.html, read off disk, fetches the Runs, Metrics and Events endpoints", "dashboard.html, read off disk, schedules each pane's next request only from the previous one settling", "dashboard.html, read off disk, gives the Tests and Chatter panes an endpoint apiece to poll" in skills/tdd/scripts/tests/dashboard.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 110 | 0.47 |
| dashboard.sh's serving behaviours are pinned by pytest cases in tests/py/test_dashboard.py asserting the same exit codes, responses, bind address and stdout, each case that needs a real listening server, a signal or a symlinked entry point marked @pytest.mark.process("<boundary>") as a medium case and every other case small through run_cli, faking only process boundaries, with no production change: replaces "dashboard.sh with no argument serves the page at / on port 8765 and exits 0 when sent SIGINT", "dashboard.sh with a port argument serves the page on that port, binds 127.0.0.1 only, and answers every pane endpoint with JSON", "the page dashboard.sh serves at / is dashboard.html, byte for byte", "/api/events answers while an /api/runs request is still blocked inside a process status starts", "dashboard.sh, run through a symlink to the skill directory and from another working directory, serves dashboard.html at / and status.sh --json's stdout at /api/runs" in skills/tdd/scripts/tests/dashboard.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 99 | 0.46 |
| status.sh's behaviours are pinned by pytest cases in tests/py/test_status.py driving the CLI through run_cli with solvable-issues.sh faked at the subprocess boundary (fake_processes), asserting the same exit codes, stdout and stderr, the symlinked-entry-point case marked @pytest.mark.process("<boundary>") and every other case small, with no production change: replaces "no runs under the main working tree prints 'no runs' and exits 3", "a run under .tdd/wt/* is listed with its issue number, title, branch and step n of m", "a run shows its state: running, done with its PR url, bailed with phase and classification, or stale", "--watch [seconds] redraws in place, recomputing every run from disk on each render", "#846: status.sh run through its entry point exits 2 on a failure veri/status.py turns into exit 2", "status.sh given a bad argument names it on stderr", "status.sh run through a symlink to the skill directory and from another working directory answers as it does when run in place" in skills/tdd/scripts/tests/status.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 211 | 0.45 |
| metrics.sh's behaviours are pinned by pytest cases in tests/py/test_metrics.py driving the CLI through run_cli, asserting the same exit codes, stdout and stderr, the symlinked-entry-point case marked @pytest.mark.process("<boundary>") and every other case small, with no production change: replaces "#454 every By-step column that existed before, and every other section, reads the same for an existing log", "metrics.sh run through a symlink to the skill directory, from another working directory, answers with the same stdout and exit code as run in place, reading that directory's .tdd/ and never the skill's", "metrics.sh run in a working directory with no .tdd/events.jsonl exits 2 and prints nothing on stdout" in skills/tdd/scripts/tests/metrics.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 113 | 0.52 |
| render-leaf-log.sh's behaviours are pinned by pytest cases in tests/py/test_render_leaf_log.py driving the CLI through run_cli, asserting the same exit codes, stdout and stderr, the symlinked-entry-point case marked @pytest.mark.process("<boundary>") and every other case small, with no production change: replaces "renders text, tool calls and truncated results one per line", "exits 2 on a line that is not JSON", "a JSON line that is not an object exits 2, and an extra argument is ignored with the stdin still rendered and exit 0", "render-leaf-log.sh run through a symlink to the skill directory and from another working directory renders as it does when run in place" in skills/tdd/scripts/tests/render-leaf-log.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 102 | 0.41 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 7 | 7 | 8 | 8 | 1 | 1 | 491 | 2 | 0 | 1 | 1 | 2 | 93 | 1 | 72 | 0 | 1 | 0 | 1 | 88 | 0 | 224 | 117 | 0 |
| target | 0 | 0 | 1 | 0 | 1 | 1 | 6 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 71 | 0 | 1 | 0 | 1 | 0 | 0 |  |  |  |
| fast | 58 | 58 | 54 | 57 | 56 | 55 | 59 | 59 | 66 | 65 | 72 | 77 | 63 | 60 | 73 | 70 | 70 | 74 | 56 | 58 | 58 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 283 | 548 | 120556 | 15869361 | 1962892 | 11.55 |
