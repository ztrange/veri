### 📊 Metrics — issue 2040

Wall time for the issue: 2289 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2233.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.06 over 51 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88908 |
| 2 | $0.04 | 90037 |
| 3 | $0.04 | 91965 |
| 4 | $0.04 | 92225 |
| 5 | $0.03 | 92641 |
| 6 | $0.03 | 92939 |
| 7 | $0.03 | 93321 |
| 8 | $0.04 | 93925 |
| 9 | $0.03 | 94265 |
| 10 | $0.05 | 96140 |
| 11 | $0.07 | 101290 |
| 12 | $0.08 | 107040 |
| 13 | $0.05 | 109040 |
| 14 | $0.11 | 119138 |
| 15 | $0.07 | 123691 |
| 16 | $0.05 | 124728 |
| 17 | $0.04 | 125579 |
| 18 | $0.05 | 126963 |
| 19 | $0.57 | 88911 |
| 20 | $0.03 | 90289 |
| 21 | $0.02 | 90689 |
| 22 | $0.04 | 93650 |
| 23 | $0.03 | 94814 |
| 24 | $0.02 | 95401 |
| 25 | $0.02 | 95873 |
| 26 | $0.02 | 96256 |
| 27 | $0.02 | 96600 |
| 28 | $0.02 | 97234 |
| 29 | $0.04 | 99880 |
| 30 | $0.03 | 101704 |
| 31 | $0.03 | 103014 |
| 32 | $0.02 | 103330 |
| 33 | $0.07 | 109916 |
| 34 | $0.03 | 111263 |
| 35 | $0.03 | 112037 |
| 36 | $0.03 | 112641 |
| 37 | $0.03 | 113383 |
| 38 | $0.03 | 114014 |
| 39 | $0.11 | 125289 |
| 40 | $0.03 | 126097 |
| 41 | $0.03 | 126782 |
| 42 | $0.04 | 128173 |
| 43 | $0.03 | 128871 |
| 44 | $0.04 | 130340 |
| 45 | $0.03 | 131089 |
| 46 | $0.04 | 132310 |
| 47 | $0.03 | 132638 |
| 48 | $0.03 | 133444 |
| 49 | $0.03 | 133758 |
| 50 | $0.03 | 134246 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 1159 | 0 | 31042 | 0.09 |
| diff | 6 | 3 | 0 | 0 | 184 | 84 | 31 | 58 | 9460 | 944795 | 132924 | 0.52 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 90 | 38 | 12 | 24 | 4169 | 301086 | 78372 | 0.27 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 105 | 54 | 20 | 36 | 6450 | 643709 | 85594 | 0.34 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Every contract case in skills/tdd/scripts/tests/py/unit/test_orchestrate.py drives the module through the run_cli fixture (run_cli(orchestrate, argv) returning code, stdout, stderr) and asserts its exit code and stdout/stderr from that triple, with no direct orchestrate.main(...) call and no capsys/capfd read left in those cases; each case keeps its name and asserts the same values; the shim case in skills/tdd/scripts/tests/py/test_orchestrate_process.py stays as the one case proving argument and exit-code forwarding; no production file changes; test_github_sh.py and lib/github.sh untouched ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 13 | 24 | 5340 | 499284 | 83490 | 0.31 | 109 | n/a | n/a | n/a |  |  | full |
| The supervise case test_cli_launches_a_supervised_run_leaf_with_model_in_claudes_argv_only_when_the_run_chose_one_and_without_the_callers_session_variables in skills/tdd/scripts/tests/py/test_supervise.py asserts again that ["--model", "sonnet"] are the last two words of claude's argv (argv[-2:]), not only that the --model values equal ["sonnet"]; the case keeps its name; no production file changes ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 8 | 14 | 1991 | 180075 | 25846 | 0.10 | 80 | n/a | n/a | n/a |  |  | full |
| Across the branch's diff no existing test case is renamed or removed and none changes its outcome: every case name present at the branch point is still defined, and the fast tier and the affected suites are green ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 21 | 10 | 20 | 2129 | 265436 | 23588 | 0.11 | 87 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast | 5 | 6 | 6 | 6 | 7 |
| affected | 3 | 4 | 9 | 8 | 9 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 32 | 60 | 10619 | 944795 | 163966 | 0.61 |
