### 📊 Metrics — issue 2626

Wall time for the issue: 17281 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 11 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2760.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $9.14 over 149 turns, in 3 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87084 tokens, largest 165097 tokens
Conductor context: first turn 87123 tokens, largest 150688 tokens
Conductor context: first turn 87122 tokens, largest 221822 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87084 |
| 2 | $0.10 | 94087 |
| 3 | $0.05 | 96102 |
| 4 | $0.05 | 98211 |
| 5 | $0.05 | 98747 |
| 6 | $0.04 | 99085 |
| 7 | $0.04 | 99403 |
| 8 | $0.04 | 99681 |
| 9 | $0.07 | 103957 |
| 10 | $0.06 | 106149 |
| 11 | $0.14 | 118692 |
| 12 | $0.09 | 125558 |
| 13 | $0.09 | 130509 |
| 14 | $0.05 | 131563 |
| 15 | $0.06 | 133602 |
| 16 | $0.05 | 134477 |
| 17 | $0.07 | 136751 |
| 18 | $0.07 | 139695 |
| 19 | $0.06 | 142216 |
| 20 | $0.06 | 143944 |
| 21 | $0.12 | 152512 |
| 22 | $0.06 | 153998 |
| 23 | $0.06 | 155119 |
| 24 | $0.06 | 156164 |
| 25 | $0.06 | 158547 |
| 26 | $0.09 | 163299 |
| 27 | $0.07 | 165097 |
| 28 | $0.58 | 87123 |
| 29 | $0.10 | 95875 |
| 30 | $0.05 | 97847 |
| 31 | $0.05 | 99929 |
| 32 | $0.14 | 112485 |
| 33 | $0.05 | 114346 |
| 34 | $0.05 | 114831 |
| 35 | $0.04 | 115208 |
| 36 | $0.04 | 115580 |
| 37 | $0.12 | 125884 |
| 38 | $0.05 | 127549 |
| 39 | $0.09 | 132730 |
| 40 | $0.04 | 133573 |
| 41 | $0.06 | 135489 |
| 42 | $0.05 | 136592 |
| 43 | $0.06 | 137746 |
| 44 | $0.06 | 139806 |
| 45 | $0.05 | 141788 |
| 46 | $0.06 | 142810 |
| 47 | $0.05 | 143817 |
| 48 | $0.06 | 145503 |
| 49 | $0.05 | 146357 |
| 50 | $0.05 | 147422 |
| 51 | $0.05 | 147890 |
| 52 | $0.05 | 148612 |
| 53 | $0.06 | 150688 |
| 54 | $0.56 | 87122 |
| 55 | $0.07 | 94125 |
| 56 | $0.04 | 96184 |
| 57 | $0.04 | 98913 |
| 58 | $0.08 | 106552 |
| 59 | $0.03 | 107808 |
| 60 | $0.03 | 108425 |
| 61 | $0.02 | 108811 |
| 62 | $0.10 | 118086 |
| 63 | $0.03 | 119456 |
| 64 | $0.05 | 122267 |
| 65 | $0.03 | 123082 |
| 66 | $0.03 | 124318 |
| 67 | $0.04 | 126191 |
| 68 | $0.04 | 127548 |
| 69 | $0.05 | 130411 |
| 70 | $0.03 | 131434 |
| 71 | $0.03 | 132141 |
| 72 | $0.04 | 134181 |
| 73 | $0.06 | 137948 |
| 74 | $0.07 | 143222 |
| 75 | $0.06 | 147094 |
| 76 | $0.04 | 148040 |
| 77 | $0.04 | 149372 |
| 78 | $0.04 | 150150 |
| 79 | $0.04 | 150932 |
| 80 | $0.03 | 151268 |
| 81 | $0.06 | 154824 |
| 82 | $0.04 | 156137 |
| 83 | $0.04 | 157006 |
| 84 | $0.03 | 157319 |
| 85 | $0.03 | 157664 |
| 86 | $0.04 | 158338 |
| 87 | $0.04 | 159487 |
| 88 | $0.03 | 159829 |
| 89 | $0.04 | 160705 |
| 90 | $0.04 | 162265 |
| 91 | $0.04 | 163421 |
| 92 | $0.04 | 164391 |
| 93 | $0.04 | 165151 |
| 94 | $0.04 | 166054 |
| 95 | $0.05 | 168502 |
| 96 | $0.04 | 169431 |
| 97 | $0.05 | 171034 |
| 98 | $0.04 | 172040 |
| 99 | $0.04 | 172944 |
| 100 | $0.06 | 176028 |
| 101 | $0.09 | 183072 |
| 102 | $0.04 | 184016 |
| 103 | $0.05 | 185521 |
| 104 | $0.04 | 185999 |
| 105 | $0.05 | 187572 |
| 106 | $0.05 | 189112 |
| 107 | $0.05 | 190268 |
| 108 | $0.05 | 191996 |
| 109 | $0.04 | 192668 |
| 110 | $0.05 | 194040 |
| 111 | $0.04 | 194410 |
| 112 | $0.05 | 195596 |
| 113 | $0.04 | 195942 |
| 114 | $0.05 | 197054 |
| 115 | $0.05 | 198792 |
| 116 | $0.05 | 199569 |
| 117 | $0.05 | 200824 |
| 118 | $0.04 | 201382 |
| 119 | $0.04 | 201662 |
| 120 | $0.07 | 205263 |
| 121 | $0.04 | 205726 |
| 122 | $0.05 | 206353 |
| 123 | $0.04 | 206804 |
| 124 | $0.04 | 207216 |
| 125 | $0.05 | 207665 |
| 126 | $0.05 | 208260 |
| 127 | $0.05 | 209157 |
| 128 | $0.05 | 210773 |
| 129 | $0.05 | 212100 |
| 130 | $0.05 | 212635 |
| 131 | $0.04 | 212934 |
| 132 | $0.06 | 214572 |
| 133 | $0.05 | 215431 |
| 134 | $0.05 | 216290 |
| 135 | $0.05 | 217447 |
| 136 | $0.05 | 218292 |
| 137 | $0.05 | 218500 |
| 138 | $0.05 | 218797 |
| 139 | $0.05 | 219236 |
| 140 | $0.05 | 219487 |
| 141 | $0.05 | 219758 |
| 142 | $0.05 | 220902 |
| 143 | $0.05 | 221822 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 11 | 1 | 2 | 1414 | 0 | 33589 | 0.10 |
| red | 20 | 8 | 0 | 0 | 1167 | 459 | 126 | 252 | 58600 | 4318463 | 570726 | 2.45 |
| green | 38 | 6 | 13 | 0 | 5105 | 941 | 230 | 434 | 100493 | 7285483 | 840701 | 5.52 |
| prose | 10 | 0 | 0 | 0 | 562 | 528 | 10 | 20 | 83364 | 190868 | 553928 | 2.24 |
| skill-edit | 2 | 0 | 0 | 0 | 34 | 23 | 7 | 14 | 2169 | 545430 | 158248 | 0.47 |
| exhausted | 2 | 0 | 0 | 0 | 1449 | 50 | 12 | 16 | 4989 | 199822 | 92780 | 0.60 |
| refactor | 7 | 1 | 0 | 0 | 148 | 50 | 24 | 48 | 4347 | 645428 | 151927 | 0.49 |
| pin | 6 | 6 | 0 | 0 | 205 | 115 | 38 | 76 | 13128 | 1182174 | 117061 | 0.54 |
| red-contradicted | 1 | 0 | 0 | 0 | 31 | 21 | 5 | 10 | 2596 | 156881 | 20408 | 0.09 |
| red-missing | 1 | 0 | 0 | 0 | 70 | 27 | 3 | 6 | 2897 | 236099 | 120574 | 0.35 |
| rebase | 4 | 1 | 1 | 0 | 7829 | 91 | 26 | 46 | 8538 | 437641 | 400576 | 1.60 |
| cover | 1 | 0 | 0 | 0 | 43 | 16 | 5 | 10 | 1878 | 133272 | 36391 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 37 | 23 | 14 | 0 | 5774 | 517 | 158 | 314 | 56889 | 4477938 | 692747 | 2.75 |
| developer | claude-sonnet-5-5 | 29 | 0 | 0 | 0 | 1961 | 706 | 192 | 380 | 83022 | 6671080 | 916105 | 4.06 |
| developer | claude-opus-5-5 | 15 | 0 | 0 | 0 | 8328 | 558 | 120 | 206 | 58969 | 3446245 | 775881 | 5.06 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 257 | 0.48 |
| green | 6968 | 6.23 | 1853 | 1.88 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 1449 | 0.60 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| rebase | 7829 | 1.60 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| New `tests-frozen.sh rerecord-refactored <ledger> <green-sha>`: after a refactor commit past `<green-sha>` changes a non-assertion line of a ticked step's own frozen case, keeping its title and every assertion line identical modulo whitespace, the command exits 0 and `check-earlier` for the next step then exits 0 on HEAD; the case's fixture writes `.tdd/verdict-refactor.exit` holding `0`, the verdict's completion file, a real-git case marked `process` in `skills/tdd/scripts/tests/py/test_tests_frozen_process.py` ⟦criterion 1⟧ | 18 | 2 | 6 | 0 | 0 | 0 | 403 | 104 | 188 | 46163 | 3009335 | 511505 | 2.96 | unknown | 4/2 | unknown | unknown |  |  | full |
| New `tests-frozen.sh rerecord-refactored <ledger> <green-sha>`: after a refactor commit past `<green-sha>` changes a non-assertion line of a ticked step's own frozen case, keeping its title and every assertion line identical modulo whitespace, the command exits 0 and `check-earlier` for the next step then exits 0 on HEAD, and leaves a case's record as it was when the case's body at `<green-sha>` already differed from the record, so `check-earlier` at the next step exits 1 naming the case; the case's fixture writes `.tdd/verdict-refactor.exit` holding `0`, the verdict's completion file, a real-git case marked `process` in `skills/tdd/scripts/tests/py/test_tests_frozen_process.py` ⟦added⟧ ⟦criterion 1⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 225 | 49 | 94 | 25156 | 1634989 | 263312 | 1.46 | 998 | 2/2 | 0/5 | nothing-left |  |  | full |
| `tests-frozen.sh rerecord-refactored` run outside a git work tree (`_toplevel()` is None) exits 2 with nothing re-recorded, pinned by a case that runs it from a non-repository directory ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 18 | 36 | 6603 | 625681 | 46605 | 0.25 | unknown | unknown | unknown | unknown |  |  | pin |
| `tests-frozen.sh rerecord-refactored` exits 2 with nothing re-recorded when its ledger cannot be read (the ledger read raises OSError), pinned by a case whose ledger path is a directory or unreadable ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 18 | 36 | 5371 | 601691 | 43042 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| `tests-frozen.sh rerecord-refactored` exits 2 when rewriting the frozen records raises OSError (`_rewrite_records`), pinned by a case whose record file cannot be written ⟦added⟧ ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 62 | 25 | 50 | 7127 | 760230 | 96142 | 0.39 | 365 | unknown | 0/5 | structural-owed |  |  | full |
| `tests-frozen.sh rerecord-refactored` also re-records an earlier ticked step's case, whatever that step's verification mode, when the refactor moved that case's non-assertion body lines into a shared helper in the same test file and its assertion lines stayed in the case identical modulo whitespace: `check-earlier` at the next step exits 0 on HEAD; fixture writes `.tdd/verdict-refactor.exit` holding `0`, a `process` case ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 12 | 24 | 5451 | 407076 | 50084 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| `tests-frozen.sh rerecord-refactored` leaves a Python case's record as it was when the refactor changed an assertion line beyond whitespace, so `check-earlier` at the next step exits 1 naming the case; fixture writes `.tdd/verdict-refactor.exit` holding `0`, a `process` case ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 72 | 27 | 54 | 8298 | 828039 | 115080 | 0.45 | 483 | unknown | 1/5 | nothing-left |  |  | full |
| `tests-frozen.sh rerecord-refactored` leaves a JavaScript case's record as it was when the refactor changed an `expect(` line beyond whitespace, so `check-earlier` at the next step exits 1 naming the case; fixture writes `.tdd/verdict-refactor.exit` holding `0`, a `process` case ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 70 | 26 | 50 | 8556 | 800043 | 96118 | 0.41 | 371 | unknown | 0/5 | nothing-left |  |  | full |
| `tests-frozen.sh rerecord-refactored` leaves the record as it was when the refactor changed a frozen case's title and its body together, so `check-earlier` at the next step exits 1 naming the case (a rename with the text otherwise unchanged stays accepted, as it is today); fixture writes `.tdd/verdict-refactor.exit` holding `0`, a `process` case ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 108 | 24 | 48 | 13558 | 901981 | 56086 | 0.37 | unknown | unknown | unknown | unknown |  |  | pin |
| `tests-frozen.sh rerecord-refactored` re-records nothing and exits 3 unless `.tdd/verdict-refactor.exit` holds `0`: with that file absent or holding `1` the record file is byte-identical afterwards, a `process` case ⟦criterion 3⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 127 | 43 | 86 | 14708 | 1331293 | 172046 | 0.71 | 708 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| When `check-earlier` refuses a case whose change since its record landed in a commit with a `refactor:` subject, its stdout line still names the case and its owning step and says the record is stale against a verified refactor rather than that a frozen case was edited, and exit stays 1, a `process` case ⟦criterion 4⟧ | 15 | 3 | 4 | 0 | 0 | 0 | 453 | 92 | 176 | 46059 | 3123992 | 464157 | 2.61 | 2184 | 3/2 | 0/5 | nothing-left |  |  | already-satisfied |
| Unit skills/tdd/SKILL.md takes the issue's RF57 row: the Refactor loop's verify-refactor PASS paragraph runs `$S/tests-frozen.sh rerecord-refactored .tdd/issue-<n>.md <green-sha>` only after that PASS and before the step's ledger commit ⟦skill-edit⟧ ⟦criterion 1⟧ | 11 | 1 | 1 | 0 | 0 | 0 | 422 | 40 | 74 | 58570 | 1157567 | 836730 | 3.26 | 359 | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| New `tests-frozen.sh rerecord-refactored <ledger> <green-sha>`: after a refactor commit past `<green-sha>` changes a non-assertion line of a ticked step's own frozen case, keeping its title and every assertion line identical modulo whitespace, the command exits 0 and `check-earlier` for the next step then exits 0 on HEAD, and leaves a case's record as it was when the case's body at `<green-sha>` already differed from the record, so `check-earlier` at the next step exits 1 naming the case; the case's fixture writes `.tdd/verdict-refactor.exit` holding `0`, the verdict's completion file, a real-git case marked `process` in `skills/tdd/scripts/tests/py/test_tests_frozen_process.py` ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.10 |
| `tests-frozen.sh rerecord-refactored` exits 2 when rewriting the frozen records raises OSError (`_rewrite_records`), pinned by a case whose record file cannot be written ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 16 | 0.08 |
| `tests-frozen.sh rerecord-refactored` leaves a Python case's record as it was when the refactor changed an assertion line beyond whitespace, so `check-earlier` at the next step exits 1 naming the case; fixture writes `.tdd/verdict-refactor.exit` holding `0`, a `process` case ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 102 | 0.12 |
| `tests-frozen.sh rerecord-refactored` leaves a JavaScript case's record as it was when the refactor changed an `expect(` line beyond whitespace, so `check-earlier` at the next step exits 1 naming the case; fixture writes `.tdd/verdict-refactor.exit` holding `0`, a `process` case ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| `tests-frozen.sh rerecord-refactored` re-records nothing and exits 3 unless `.tdd/verdict-refactor.exit` holds `0`: with that file absent or holding `1` the record file is byte-identical afterwards, a `process` case ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| When `check-earlier` refuses a case whose change since its record landed in a commit with a `refactor:` subject, its stdout line still names the case and its owning step and says the record is stale against a verified refactor rather than that a frozen case was edited, and exit stays 1, a `process` case ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.09 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 10 | 9 | 32 | 40 | 21 | 24 | 33 | 0 | 32 | 24 | 25 | 29 | 27 | 0 | 18 | 18 | 0 | 31 | 3 | 3 | 19 | 26 | 0 | 14 | 18 | 0 | 22 | 21 | 13 | 13 | 14 | 13 | 17 | 17 | 3 | 14 | 19 | 21 | 23 | 22 | 20 | 0 | 7 | 4 | 17 | 22 | 14 | 26 | 5 | 14 | 17 | 17 | 4 | 14 | 0 | 14 | 15 | 19 | 19 | 20 | 0 | 19 | 20 | 19 | 14 | 0 | 15 | 14 | 14 | 15 | 0 | 20 | 7 | 633 | 22 |
| fast | 61 | 45 | 47 | 32 | 40 | 41 | 47 | 46 | 41 | 33 | 37 | 48 | 57 | 31 | 37 | 25 | 30 | 35 | 33 | 33 | 33 | 34 | 34 | 32 | 28 | 37 | 31 | 34 | 34 | 27 | 31 | 34 | 31 | 32 | 30 | 27 | 32 | 26 | 30 | 26 | 29 | 27 | 39 | 33 | 33 | 34 | 29 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 7 | 19 | 0 | 9 | 5 | 4 | 31 | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 2 | 3 | 3 | 3 | 4 | 4 | 4 | 6 | 5 | 4 | 3 | 3 | 3 | 6 | 4 | 3 | 3 | 4 | 4 | 4 | 5 | 4 | 5 | 4 | 5 | 3 | 4 | 22 | 5 | 4 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 1518 | 1644 | 918 | 1431 | 1512 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 487 | 934 | 284413 | 15331561 | 3096909 | 23.72 (estimate) |
