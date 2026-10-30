### 📊 Metrics — issue 2718

Wall time for the issue: 3943 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2732.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.84 over 33 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86645 tokens, largest 147836 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86645 |
| 2 | $0.07 | 93648 |
| 3 | $0.03 | 94542 |
| 4 | $0.04 | 96886 |
| 5 | $0.03 | 97916 |
| 6 | $0.02 | 98218 |
| 7 | $0.02 | 98488 |
| 8 | $0.02 | 99045 |
| 9 | $0.02 | 99489 |
| 10 | $0.06 | 103976 |
| 11 | $0.11 | 115669 |
| 12 | $0.05 | 118851 |
| 13 | $0.06 | 123008 |
| 14 | $0.04 | 124689 |
| 15 | $0.03 | 125719 |
| 16 | $0.03 | 126352 |
| 17 | $0.04 | 128476 |
| 18 | $0.03 | 129335 |
| 19 | $0.04 | 131138 |
| 20 | $0.03 | 131873 |
| 21 | $0.04 | 133282 |
| 22 | $0.05 | 136021 |
| 23 | $0.06 | 140133 |
| 24 | $0.04 | 141846 |
| 25 | $0.04 | 142770 |
| 26 | $0.04 | 143931 |
| 27 | $0.04 | 144708 |
| 28 | $0.03 | 145105 |
| 29 | $0.03 | 145478 |
| 30 | $0.03 | 146169 |
| 31 | $0.03 | 146866 |
| 32 | $0.03 | 147269 |
| 33 | $0.03 | 147836 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 13 | 2 | 4 | 1635 | 31910 | 34760 | 0.11 |
| diff | 2 | 1 | 0 | 0 | 210 | 24 | 9 | 18 | 2456 | 233003 | 46252 | 0.16 |
| red | 3 | 1 | 0 | 0 | 190 | 72 | 24 | 46 | 9168 | 795063 | 68138 | 0.34 |
| green | 2 | 1 | 0 | 0 | 155 | 22 | 9 | 18 | 2233 | 257802 | 30784 | 0.13 |
| refactor | 1 | 0 | 0 | 0 | 7 | 3 | 2 | 4 | 164 | 48616 | 14841 | 0.04 |
| pin | 1 | 1 | 0 | 0 | 37 | 19 | 8 | 14 | 2032 | 214793 | 19360 | 0.09 |
| prose | 3 | 0 | 0 | 0 | 89 | 80 | 3 | 6 | 12479 | 2843 | 132415 | 0.46 |
| skill-edit | 1 | 0 | 0 | 0 | 10 | 7 | 4 | 8 | 547 | 203777 | 44668 | 0.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 256 | 62 | 21 | 38 | 6766 | 510424 | 97616 | 0.36 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 359 | 91 | 33 | 66 | 10922 | 1070763 | 116519 | 0.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 60 | 0.30 |
| skill-edit | 0 | 0.00 | 10 | 0.14 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| test_rerecord_rebased_exits_2_naming_an_unreadable_ledger_on_stderr_and_writes_no_record_2552 in skills/tdd/scripts/tests/py/test_tests_frozen_process.py hands rerecord-rebased a ledger path that exists but cannot be read (a directory) in place of a missing file, its name and its exit-2 assertions unchanged, and no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 9 | 18 | 2456 | 233003 | 46252 | 0.16 | 312 | n/a | n/a | n/a |  |  | full |
| rerecord-rebased with no ledger file at the path it is given, as a relaunch after a preflight refusal on a moved default branch has, exits 3 with nothing on stdout and rewrites no record, which PREFLIGHT's "Exit 0 or 3 goes on" reads as carrying on rather than bailing ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 70 | 26 | 50 | 7978 | 762505 | 85967 | 0.37 | 369 | unknown | 0/5 | nothing-left |  |  | full |
| rerecord-rebased with a ledger present and a stale case whose re-record raises FileNotFoundError still exits 2, naming the record on stderr, not read as a missing ledger; a pin in skills/tdd/scripts/tests/py/test_tests_frozen_process.py, a process case with a real git repository, no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 17 | 32 | 5619 | 553769 | 47156 | 0.23 | unknown | unknown | unknown | unknown |  |  | pin |
| Unit skills/tdd/SCRIPTS.md: the $S/tests-frozen.sh catalogue entry says rerecord-rebased exits 3 when the ledger file does not exist, and that a ledger that exists but cannot be read stays exit 2 ⟦skill-edit⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 60 | 6 | 12 | 8728 | 205971 | 132652 | 0.44 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| rerecord-rebased with no ledger file at the path it is given, as a relaunch after a preflight refusal on a moved default branch has, exits 3 with nothing on stdout and rewrites no record, which PREFLIGHT's "Exit 0 or 3 goes on" reads as carrying on rather than bailing ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 35 | 35 | 38 | 27 | 27 |  |  |  |
| affected | 23 | 21 | 21 | 12 | 3 | 0 | 14 | 17 |
| target | 3 | 6 | 6 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 61 | 118 | 30714 | 1787807 | 391218 | 3.31 (estimate) |
