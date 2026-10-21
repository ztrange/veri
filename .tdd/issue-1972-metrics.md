### 📊 Metrics — issue 1972

Wall time for the issue: 2217 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2042.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 13 | 2 | 4 | 1557 | 31315 | 35810 | 0.11 |
| diff | 6 | 3 | 0 | 0 | 129 | 64 | 27 | 52 | 5934 | 678178 | 98779 | 0.37 |
| red | 6 | 2 | 0 | 0 | 240 | 219 | 45 | 90 | 16910 | 1554952 | 132791 | 0.66 |
| green | 4 | 2 | 0 | 0 | 156 | 91 | 26 | 48 | 9594 | 773714 | 77534 | 0.37 |
| refactor | 4 | 2 | 0 | 0 | 75 | 48 | 17 | 30 | 3852 | 420966 | 62665 | 0.24 |
| pin | 2 | 2 | 0 | 0 | 48 | 40 | 10 | 20 | 3119 | 274208 | 31332 | 0.14 |
| cover | 3 | 0 | 0 | 0 | 72 | 60 | 12 | 24 | 4089 | 301484 | 58992 | 0.22 |
| predicate | 3 | 0 | 0 | 0 | 33 | 26 | 10 | 20 | 1818 | 254524 | 35992 | 0.13 |
| structural | 3 | 0 | 0 | 0 | 74 | 64 | 21 | 28 | 5193 | 403464 | 48401 | 0.21 |
| transform | 3 | 1 | 2 | 0 | 30 | 22 | 9 | 18 | 2121 | 202910 | 53214 | 0.17 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 13 | 2 | 0 | 289 | 185 | 52 | 104 | 15510 | 1308250 | 247884 | 0.91 |
| developer | claude-sonnet-5-5 | 20 | 0 | 0 | 0 | 585 | 462 | 127 | 230 | 38677 | 3587465 | 387626 | 1.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 72 | 0.22 |
| predicate | 0 | 0.00 | 33 | 0.13 |
| structural | 0 | 0.00 | 74 | 0.21 |
| transform | 0 | 0.00 | 30 | 0.17 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| clear_refactor_pending.py drops its dead non-bool branch (lines 29-30, `if not isinstance(cleared, bool): return to_contract(cleared)`, and `to_contract` once nothing calls it), and the case tests/py/unit/test_clear_refactor_pending.py::test_main_returns_2_leaving_the_ledger_byte_identical_when_the_ledger_modules_ledger_clear_pending_hands_back_status_7, which pins only that branch, is removed in the same commit; no other test changes ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 18 | 9 | 16 | 2103 | 196452 | 46026 | 0.16 | 73 | n/a | n/a | n/a |  |  | full |
| the case tests/py/unit/test_tick_ledger.py::test_cli_exits_2_with_one_path_and_reason_stderr_line_for_a_ledger_that_does_not_decode_leaving_it_byte_identical, which pins the strict-UTF-8 exit 2 that the NUL and non-UTF-8 byte criterion replaces, is removed; no production change and no other test changes ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 21 | 8 | 16 | 1719 | 208316 | 25364 | 0.10 | 74 | n/a | n/a | n/a |  |  | full |
| tick-ledger.sh, add-ledger-step.sh, reorder-ledger-steps.sh and clear-refactor-pending.sh read a ledger holding a NUL byte and a non-UTF-8 byte the same way: the NUL is dropped, the non-UTF-8 byte survives their rewrite unchanged, and none of them exits 2 for it; the read lives in veri/ledger.py and the four entry points call it rather than opening and decoding the file themselves; pinned by a unit-tier case (in-process, no subprocess) over all four; every existing case in the seven suites the issue names keeps its name and outcome ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 146 | 41 | 80 | 13390 | 1299639 | 112970 | 0.55 | 306 | unknown | 1/5 | structural-owed |  |  | full |
| the case tests/py/unit/test_add_ledger_step.py::test_main_reads_and_rewrites_the_ledger_as_bytes_line_by_line_in_place keeps its name but stops asserting that the ledger's inode is unchanged (the in-place write the atomic-replace criterion replaces), still pinning the same rewritten bytes and exit codes; no production change and no other test changes ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 10 | 20 | 2112 | 273410 | 27389 | 0.12 | 68 | n/a | n/a | n/a |  |  | full |
| add-ledger-step.sh replaces the ledger atomically through veri/ledger.py's replace_ledger, both when it inserts steps and when it files owed steps: when the write fails, the original ledger is left byte-identical and no temporary file is left beside it; pinned by a unit-tier case (in-process); the existing case test_main_returns_2_naming_the_anchor_for_a_missing_or_directory_ledger_and_raises_on_a_failed_write in tests/py/unit/test_add_ledger_step.py must keep passing unchanged (a ledger that open(path, "w"/"a") refuses with PermissionError still raises it and is left byte-identical), as must every other existing case in the seven suites the issue names ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 27 | 48 | 8531 | 706329 | 107574 | 0.42 | 212 | unknown | 0/5 | nothing-left |  |  | full |
| each of tick-ledger.sh, add-ledger-step.sh, reorder-ledger-steps.sh and clear-refactor-pending.sh exits 2 and names the temporary file on stderr when a failed write leaves it behind (ledger.LeftBehind); pinned by a unit-tier case (in-process) over all four; every existing case in the seven suites the issue names keeps its name and outcome ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 16 | 32 | 6622 | 586405 | 47303 | 0.24 | 128 | unknown | unknown | unknown |  |  | pin |
| each of tick-ledger.sh, add-ledger-step.sh, reorder-ledger-steps.sh and clear-refactor-pending.sh exits 2 with the ledger path and the OS reason on stderr when the ledger path is unreadable (for example, a directory); pinned by a unit-tier case (in-process) over all four; every existing case in the seven suites the issue names keeps its name and outcome ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 84 | 14 | 28 | 4932 | 431467 | 36475 | 0.18 | 122 | unknown | unknown | unknown |  |  | pin |
| every existing case in the seven suites the issue names keeps its name and its outcome, but the three it lets change ⟦full-suite⟧ ⟦criterion 5⟧ | 12 | 1 | 2 | 0 | 0 | 0 | 172 | 52 | 90 | 13221 | 1162382 | 196599 | 0.74 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tick-ledger.sh, add-ledger-step.sh, reorder-ledger-steps.sh and clear-refactor-pending.sh read a ledger holding a NUL byte and a non-UTF-8 byte the same way: the NUL is dropped, the non-UTF-8 byte survives their rewrite unchanged, and none of them exits 2 for it; the read lives in veri/ledger.py and the four entry points call it rather than opening and decoding the file themselves; pinned by a unit-tier case (in-process, no subprocess) over all four; every existing case in the seven suites the issue names keeps its name and outcome ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 50 | 0.14 |
| add-ledger-step.sh replaces the ledger atomically through veri/ledger.py's replace_ledger, both when it inserts steps and when it files owed steps: when the write fails, the original ledger is left byte-identical and no temporary file is left beside it; pinned by a unit-tier case (in-process); the existing case test_main_returns_2_naming_the_anchor_for_a_missing_or_directory_ledger_and_raises_on_a_failed_write in tests/py/unit/test_add_ledger_step.py must keep passing unchanged (a ledger that open(path, "w"/"a") refuses with PermissionError still raises it and is left byte-identical), as must every other existing case in the seven suites the issue names ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 25 | 0.10 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 7 | 8 | 8 | 6 | 0 | 6 | 6 | 6 | 7 | 7 | 8 | 7 | 8 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 0 | 1 | 1 | 1 | 1 | 2 | 0 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 2 | 2 | 1 |
| target | 0 | 0 | 1 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 179 | 334 | 54187 | 4895715 | 635510 | 2.62 |
