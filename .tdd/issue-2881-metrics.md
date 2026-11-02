### 📊 Metrics — issue 2881

Wall time for the issue: 624 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2951.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.54 over 78 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88032 tokens, largest 165473 tokens
Conductor context: first turn 88361 tokens, largest 130419 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88032 |
| 2 | $0.08 | 94719 |
| 3 | $0.04 | 96180 |
| 4 | $0.04 | 97729 |
| 5 | $0.05 | 99085 |
| 6 | $0.03 | 99833 |
| 7 | $0.04 | 100175 |
| 8 | $0.03 | 100480 |
| 9 | $0.04 | 101060 |
| 10 | $0.04 | 102359 |
| 11 | $0.05 | 104294 |
| 12 | $0.03 | 104934 |
| 13 | $0.06 | 107640 |
| 14 | $0.09 | 115410 |
| 15 | $0.04 | 116063 |
| 16 | $0.04 | 116665 |
| 17 | $0.04 | 117211 |
| 18 | $0.04 | 117640 |
| 19 | $0.10 | 125341 |
| 20 | $0.06 | 128021 |
| 21 | $0.04 | 128874 |
| 22 | $0.04 | 129153 |
| 23 | $0.04 | 129797 |
| 24 | $0.05 | 130808 |
| 25 | $0.04 | 131812 |
| 26 | $0.04 | 132303 |
| 27 | $0.06 | 133996 |
| 28 | $0.04 | 134758 |
| 29 | $0.10 | 142803 |
| 30 | $0.05 | 144184 |
| 31 | $0.05 | 144801 |
| 32 | $0.05 | 145567 |
| 33 | $0.04 | 146185 |
| 34 | $0.05 | 146883 |
| 35 | $0.05 | 147963 |
| 36 | $0.05 | 148968 |
| 37 | $0.04 | 149412 |
| 38 | $0.06 | 150874 |
| 39 | $0.04 | 151328 |
| 40 | $0.05 | 152082 |
| 41 | $0.05 | 153531 |
| 42 | $0.05 | 153841 |
| 43 | $0.05 | 154646 |
| 44 | $0.05 | 156572 |
| 45 | $0.09 | 161824 |
| 46 | $0.05 | 163077 |
| 47 | $0.06 | 164514 |
| 48 | $0.05 | 165473 |
| 49 | $0.57 | 88361 |
| 50 | $0.07 | 95513 |
| 51 | $0.03 | 97042 |
| 52 | $0.04 | 99604 |
| 53 | $0.06 | 104110 |
| 54 | $0.04 | 106804 |
| 55 | $0.03 | 107505 |
| 56 | $0.05 | 110691 |
| 57 | $0.03 | 111390 |
| 58 | $0.03 | 111903 |
| 59 | $0.03 | 112324 |
| 60 | $0.03 | 112672 |
| 61 | $0.03 | 113091 |
| 62 | $0.03 | 113831 |
| 63 | $0.05 | 117694 |
| 64 | $0.03 | 118362 |
| 65 | $0.03 | 119131 |
| 66 | $0.03 | 119911 |
| 67 | $0.03 | 120135 |
| 68 | $0.07 | 125679 |
| 69 | $0.03 | 126342 |
| 70 | $0.03 | 126685 |
| 71 | $0.03 | 127271 |
| 72 | $0.03 | 127815 |
| 73 | $0.03 | 128227 |
| 74 | $0.03 | 128719 |
| 75 | $0.03 | 128974 |
| 76 | $0.03 | 129199 |
| 77 | $0.03 | 129762 |
| 78 | $0.03 | 130419 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 10 | 1 | 2 | 1128 | 0 | 32103 | 0.09 |
| red | 5 | 1 | 0 | 0 | 252 | 96 | 31 | 46 | 9477 | 711819 | 118255 | 0.46 |
| pin | 3 | 3 | 0 | 0 | 98 | 38 | 11 | 22 | 4165 | 298701 | 46580 | 0.19 |
| green | 4 | 1 | 1 | 0 | 418 | 69 | 19 | 36 | 5670 | 510411 | 68203 | 0.38 |
| refactor | 1 | 0 | 0 | 0 | 11 | 6 | 3 | 4 | 288 | 47605 | 16293 | 0.05 |
| diff | 4 | 2 | 0 | 0 | 341 | 47 | 12 | 24 | 2470 | 286272 | 70231 | 0.23 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 8 | 1 | 0 | 606 | 134 | 30 | 60 | 10555 | 793620 | 140513 | 0.54 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 338 | 101 | 37 | 56 | 10176 | 816157 | 161115 | 0.59 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 189 | 31 | 10 | 18 | 2467 | 245031 | 50037 | 0.28 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 418 | 0.38 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A report whose single-line `PREDICATE:` line (a command that fails) is followed only by blank lines makes `structural-predicate.sh` run the command, write the record and exit 0, as a single-line predicate does: blank lines after it never make it multi-line (a case in skills/tdd/scripts/tests/py/test_structural_predicate.py, no real process) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 12 | 20 | 4537 | 292980 | 55344 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| A report whose `PREDICATE:` value is a heredoc (`python3 - <<'PY'` followed by its body lines and `PY`) makes `structural-predicate.sh` exit 2 with a stderr message naming the multi-line predicate as the cause; it runs nothing and writes no record (a case in skills/tdd/scripts/tests/py/test_structural_predicate.py, no real process) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 110 | 31 | 54 | 8382 | 759528 | 119984 | 0.56 | 719 | 1/2 | 0/5 | nothing-left |  |  | full |
| A report whose `PREDICATE:` line ends in a trailing `\` continuation followed by a further non-blank line makes `structural-predicate.sh` exit 2 with a stderr message naming the multi-line predicate as the cause; it runs nothing and writes no record (a case in skills/tdd/scripts/tests/py/test_structural_predicate.py, no real process) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 11 | 18 | 3518 | 280138 | 36152 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| A report whose `PREDICATE:` line is followed by any other non-blank line (plain prose, no heredoc, no `\`) makes `structural-predicate.sh` exit 2 with a stderr message naming the multi-line predicate as the cause; it runs nothing and writes no record (a case in skills/tdd/scripts/tests/py/test_structural_predicate.py, no real process) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 10 | 16 | 3163 | 235890 | 37851 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| The existing single-line cases of skills/tdd/scripts/tests/py/test_structural_predicate.py pinning exit 0 with the record written when the command fails, 1 when it succeeds, 3 for `NONE` and 2 for a missing `PREDICATE:` line are left unchanged by the branch's diff ⟦diff-checked⟧ ⟦criterion 2⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 47 | 12 | 24 | 2470 | 286272 | 70231 | 0.23 | 349 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A report whose `PREDICATE:` value is a heredoc (`python3 - <<'PY'` followed by its body lines and `PY`) makes `structural-predicate.sh` exit 2 with a stderr message naming the multi-line predicate as the cause; it runs nothing and writes no record (a case in skills/tdd/scripts/tests/py/test_structural_predicate.py, no real process) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 7 | 7 | 9 | 7 | 7 | 7 | 9 | 10 | 8 | 7 | 7 | 9 |  |
| target | 8 | 8 | 7 | 6 | 5 | 6 | 7 | 7 | 9 | 10 | 7 | 7 | 7 | 8 |
| fast | 74 | 59 | 50 | 56 | 65 | 57 | 57 | 65 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 77 | 134 | 23198 | 1854808 | 351665 | 5.94 (estimate) |
