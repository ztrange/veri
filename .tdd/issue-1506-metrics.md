### 📊 Metrics — issue 1506

Wall time for the issue: 2080 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 10 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1996.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 11 | 1 | 2 | 1194 | 17463 | 13750 | 0.05 |
| diff | 18 | 7 | 2 | 0 | 701 | 416 | 109 | 210 | 31562 | 2966583 | 280860 | 1.50 |
| red | 2 | 0 | 0 | 0 | 61 | 52 | 12 | 24 | 3523 | 355032 | 33908 | 0.16 |
| pin | 2 | 2 | 0 | 0 | 26 | 19 | 6 | 12 | 1711 | 152733 | 27724 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 10 | 2 | 0 | 363 | 206 | 46 | 92 | 15307 | 1209841 | 165899 | 0.69 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 314 | 206 | 61 | 116 | 17176 | 1718129 | 127286 | 0.66 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 124 | 86 | 21 | 40 | 5507 | 563841 | 63057 | 0.45 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 334 | 1.02 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| parallel_conductors.py reads VERI_CONDUCTOR_CTX_BUDGET through tunables.resolve (the TABLE entry orchestrate.py uses) instead of its own _ctx_budget() default and its _whole_number() check of that tunable, with parallel-conductors.sh's refusal text for a bad VERI_CONDUCTOR_CTX_BUDGET ("parallel-conductors: VERI_CONDUCTOR_CTX_BUDGET must be a whole number >= 0: '<value>'") and every existing case's name and outcome unchanged; no test edited ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 11 | 22 | 3234 | 310676 | 29281 | 0.14 | 94 | n/a | n/a | n/a |  |  | full |
| run_leaf.py reads VERI_LEAF_MODEL and VERI_SHIM_SET_COERCE through tunables rather than from its dict(os.environ) copy, the leaf's environment otherwise unchanged (VERI_SHIM_SET_COERCE still removed from it and PYTHONCOERCECLOCALE still dropped when it is "1"), every existing case's name and outcome unchanged; no test edited ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 13 | 24 | 3236 | 339921 | 28070 | 0.14 | 167 | n/a | n/a | n/a |  |  | full |
| push_branch.py, suite_reported.py, timed_test_run.py and harvest_usage.py hand event.context (and harvest) the run's VERI_* context taken through tunables rather than os.environ, the events they write carrying the same issue, step and other context fields as before, every existing case's name and outcome unchanged; no test edited ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 14 | 28 | 3390 | 404822 | 29575 | 0.15 | 93 | n/a | n/a | n/a |  |  | full |
| test_tunable_reads.py's direct_reads() flags a VERI_* read through a dict(os.environ) copy read with a VERI_ name on a later line, pinned by a planted case (tmp_path module, like the existing planted-variable case) that is watched red against the old direct_reads(); every module under veri/ still passes the tree-audit cases ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 16 | 32 | 5818 | 484512 | 31903 | 0.19 | 124 | n/a | n/a | n/a |  |  | full |
| test_tunable_reads.py's direct_reads() flags os.environ passed as an argument to a call that reads a VERI_* value from it (the event.context(os.environ) and harvest(argv[0], os.environ) shapes), pinned by a planted case watched red against the old direct_reads(); every module under veri/ still passes the tree-audit cases ⟦diff-checked⟧ ⟦criterion 3⟧ | 6 | 1 | 2 | 0 | 0 | 0 | 134 | 32 | 62 | 9675 | 851470 | 106382 | 0.63 | 271 | 2/2 | unknown | unknown |  |  | full |
| test_tunable_reads.py holds a planted case (tmp_path module, like the existing planted-variable case) in which os.environ is passed as an argument to a call that reads a VERI_* value from it, e.g. event.context(os.environ), and direct_reads() names that line; the case fails when direct_reads()'s passed-as-an-argument check is removed ⟦added⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 9 | 18 | 2589 | 253728 | 30704 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| test_tunable_reads.py's direct_reads() flags a VERI_* read through a bare environ imported with `from os import environ`, pinned by a planted case watched red against the old direct_reads(); every module under veri/ still passes the tree-audit cases ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 12 | 20 | 3662 | 277688 | 30954 | 0.14 | 95 | n/a | n/a | n/a |  |  | full |
| test_tunable_reads.py holds a planted case (tmp_path module, like the existing planted-variable case) reading a VERI_* name through a bare environ imported with `from os import environ`, and direct_reads() names that line; the case fails when direct_reads()'s bare-environ handling is removed ⟦added⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 9 | 18 | 2645 | 254037 | 30928 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| run_leaf and event are removed from test_tunable_reads.py's READS_DIRECTLY exemption, and the tree-audit case that honours that exemption stays green with them audited ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 11 | 22 | 2547 | 297494 | 24695 | 0.12 | 90 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 8 | 6 | 6 | 7 | 6 | 6 | 6 | 6 | 6 | 7 | 6 | 6 | 6 |  |  |
| affected | 3 | 3 | 2 | 1 | 1 | 4 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| target | 1 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 128 | 248 | 37990 | 3491811 | 356242 | 1.81 |
