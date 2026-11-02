### 📊 Metrics — issue 2750

Wall time for the issue: 20203 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 16 of 31 planned.
Outcome: the run bailed — needs-user, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $11.15 over 198 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87212 tokens, largest 257328 tokens
Conductor context: first turn 87214 tokens, largest 113933 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87212 |
| 2 | $0.09 | 94293 |
| 3 | $0.04 | 95983 |
| 4 | $0.04 | 97944 |
| 5 | $0.03 | 98295 |
| 6 | $0.03 | 98585 |
| 7 | $0.03 | 98897 |
| 8 | $0.03 | 99129 |
| 9 | $0.03 | 99324 |
| 10 | $0.02 | 99563 |
| 11 | $0.03 | 99870 |
| 12 | $0.03 | 100176 |
| 13 | $0.03 | 100343 |
| 14 | $0.04 | 100943 |
| 15 | $0.03 | 101284 |
| 16 | $0.04 | 103392 |
| 17 | $0.14 | 116749 |
| 18 | $0.05 | 119093 |
| 19 | $0.06 | 123726 |
| 20 | $0.05 | 125515 |
| 21 | $0.05 | 127967 |
| 22 | $0.04 | 128581 |
| 23 | $0.04 | 129108 |
| 24 | $0.04 | 129678 |
| 25 | $0.04 | 131091 |
| 26 | $0.04 | 131557 |
| 27 | $0.05 | 133067 |
| 28 | $0.13 | 145545 |
| 29 | $0.04 | 145968 |
| 30 | $0.04 | 146669 |
| 31 | $0.04 | 147092 |
| 32 | $0.04 | 147723 |
| 33 | $0.04 | 147902 |
| 34 | $0.05 | 148699 |
| 35 | $0.04 | 149109 |
| 36 | $0.04 | 149606 |
| 37 | $0.05 | 150935 |
| 38 | $0.05 | 153080 |
| 39 | $0.04 | 153312 |
| 40 | $0.04 | 153610 |
| 41 | $0.04 | 153899 |
| 42 | $0.11 | 162245 |
| 43 | $0.05 | 163351 |
| 44 | $0.04 | 163569 |
| 45 | $0.04 | 164053 |
| 46 | $0.05 | 164823 |
| 47 | $0.04 | 165248 |
| 48 | $0.05 | 165443 |
| 49 | $0.04 | 165831 |
| 50 | $0.04 | 166373 |
| 51 | $0.05 | 167016 |
| 52 | $0.04 | 167253 |
| 53 | $0.05 | 167714 |
| 54 | $0.04 | 168230 |
| 55 | $0.05 | 168637 |
| 56 | $0.05 | 169552 |
| 57 | $0.04 | 170283 |
| 58 | $0.05 | 170857 |
| 59 | $0.04 | 171262 |
| 60 | $0.05 | 171550 |
| 61 | $0.05 | 172149 |
| 62 | $0.04 | 172588 |
| 63 | $0.05 | 173740 |
| 64 | $0.05 | 174644 |
| 65 | $0.06 | 175983 |
| 66 | $0.05 | 177615 |
| 67 | $0.06 | 178983 |
| 68 | $0.04 | 179758 |
| 69 | $0.05 | 180288 |
| 70 | $0.05 | 180905 |
| 71 | $0.05 | 181228 |
| 72 | $0.05 | 181916 |
| 73 | $0.05 | 182527 |
| 74 | $0.04 | 182745 |
| 75 | $0.05 | 183671 |
| 76 | $0.05 | 183972 |
| 77 | $0.05 | 184553 |
| 78 | $0.05 | 184941 |
| 79 | $0.04 | 185231 |
| 80 | $0.05 | 186019 |
| 81 | $0.06 | 187059 |
| 82 | $0.05 | 187831 |
| 83 | $0.05 | 188135 |
| 84 | $0.05 | 188665 |
| 85 | $0.05 | 189263 |
| 86 | $0.05 | 190299 |
| 87 | $0.05 | 190502 |
| 88 | $0.05 | 191687 |
| 89 | $0.06 | 192912 |
| 90 | $0.06 | 194533 |
| 91 | $0.05 | 195870 |
| 92 | $0.06 | 196959 |
| 93 | $0.06 | 198259 |
| 94 | $0.06 | 200506 |
| 95 | $0.05 | 201052 |
| 96 | $0.06 | 201755 |
| 97 | $0.05 | 202170 |
| 98 | $0.05 | 202324 |
| 99 | $0.05 | 202931 |
| 100 | $0.05 | 203302 |
| 101 | $0.06 | 204277 |
| 102 | $0.05 | 204512 |
| 103 | $0.05 | 205048 |
| 104 | $0.05 | 205369 |
| 105 | $0.05 | 205856 |
| 106 | $0.06 | 207122 |
| 107 | $0.06 | 207837 |
| 108 | $0.05 | 208220 |
| 109 | $0.05 | 208626 |
| 110 | $0.06 | 209048 |
| 111 | $0.05 | 209534 |
| 112 | $0.05 | 209815 |
| 113 | $0.06 | 211152 |
| 114 | $0.07 | 213015 |
| 115 | $0.05 | 213683 |
| 116 | $0.05 | 213978 |
| 117 | $0.06 | 215303 |
| 118 | $0.06 | 215735 |
| 119 | $0.05 | 216152 |
| 120 | $0.06 | 216544 |
| 121 | $0.07 | 219230 |
| 122 | $0.06 | 220341 |
| 123 | $0.05 | 220666 |
| 124 | $0.06 | 221122 |
| 125 | $0.06 | 222495 |
| 126 | $0.06 | 222686 |
| 127 | $0.06 | 223653 |
| 128 | $0.05 | 224242 |
| 129 | $0.06 | 224797 |
| 130 | $0.06 | 226017 |
| 131 | $0.06 | 226766 |
| 132 | $0.06 | 227148 |
| 133 | $0.05 | 227304 |
| 134 | $0.06 | 227502 |
| 135 | $0.06 | 228453 |
| 136 | $0.05 | 228817 |
| 137 | $0.06 | 229524 |
| 138 | $0.06 | 229797 |
| 139 | $0.05 | 229969 |
| 140 | $0.06 | 230395 |
| 141 | $0.06 | 230717 |
| 142 | $0.05 | 231430 |
| 143 | $0.06 | 231729 |
| 144 | $0.06 | 231916 |
| 145 | $0.05 | 232253 |
| 146 | $0.06 | 232954 |
| 147 | $0.06 | 233242 |
| 148 | $0.06 | 233521 |
| 149 | $0.05 | 233855 |
| 150 | $0.06 | 234541 |
| 151 | $0.06 | 234799 |
| 152 | $0.06 | 235388 |
| 153 | $0.05 | 235659 |
| 154 | $0.06 | 235964 |
| 155 | $0.06 | 236274 |
| 156 | $0.06 | 236486 |
| 157 | $0.05 | 236978 |
| 158 | $0.06 | 237254 |
| 159 | $0.06 | 237534 |
| 160 | $0.06 | 237864 |
| 161 | $0.06 | 238535 |
| 162 | $0.05 | 238797 |
| 163 | $0.06 | 239003 |
| 164 | $0.06 | 239188 |
| 165 | $0.06 | 239477 |
| 166 | $0.05 | 239691 |
| 167 | $0.06 | 240258 |
| 168 | $0.06 | 240504 |
| 169 | $0.06 | 240729 |
| 170 | $0.06 | 241093 |
| 171 | $0.06 | 241791 |
| 172 | $0.06 | 242070 |
| 173 | $0.06 | 242522 |
| 174 | $0.06 | 243974 |
| 175 | $0.07 | 244759 |
| 176 | $0.06 | 245940 |
| 177 | $0.08 | 248328 |
| 178 | $0.06 | 248804 |
| 179 | $0.06 | 249468 |
| 180 | $0.10 | 254373 |
| 181 | $0.07 | 256439 |
| 182 | $0.07 | 257328 |
| 183 | $0.56 | 87214 |
| 184 | $0.07 | 93902 |
| 185 | $0.03 | 95455 |
| 186 | $0.03 | 97066 |
| 187 | $0.02 | 97575 |
| 188 | $0.04 | 100725 |
| 189 | $0.03 | 101628 |
| 190 | $0.03 | 102705 |
| 191 | $0.04 | 105349 |
| 192 | $0.08 | 112128 |
| 193 | $0.03 | 112735 |
| 194 | $0.03 | 113933 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 33 | 24 | 2 | 4 | 3120 | 17157 | 47782 | 0.15 |
| red | 50 | 18 | 2 | 0 | 3338 | 1060 | 285 | 536 | 105422 | 7836926 | 1127337 | 6.36 |
| green | 56 | 16 | 11 | 0 | 9584 | 1110 | 342 | 624 | 94356 | 9130272 | 1055974 | 5.14 |
| refactor | 19 | 3 | 0 | 0 | 646 | 178 | 66 | 132 | 12669 | 1741491 | 323924 | 1.11 |
| red-missing | 5 | 0 | 0 | 0 | 275 | 108 | 22 | 44 | 13051 | 587090 | 139146 | 0.54 |
| pin | 5 | 5 | 0 | 0 | 235 | 81 | 21 | 38 | 6608 | 508287 | 75714 | 0.31 |
| red-supersede | 2 | 0 | 0 | 0 | 146 | 97 | 14 | 28 | 9358 | 469836 | 47152 | 0.26 |
| exhausted | 1 | 0 | 0 | 0 | 69 | 10 | 3 | 6 | 1040 | 75812 | 13050 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 57 | 43 | 14 | 0 | 6838 | 880 | 252 | 470 | 77479 | 6329898 | 941666 | 3.76 |
| developer | claude-sonnet-5-5 | 55 | 0 | 0 | 0 | 4472 | 957 | 294 | 534 | 86461 | 7660117 | 1126364 | 4.77 |
| developer | claude-opus-5-5 | 28 | 0 | 0 | 0 | 3016 | 831 | 209 | 408 | 81684 | 6376856 | 762049 | 5.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 812 | 1.34 | 231 | 0.62 |
| green | 9743 | 5.40 | 163 | 0.07 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 67 | 0.10 |
| exhausted | 0 | 0.00 | 69 | 0.10 |
| preflight | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `status.sh --report` exits 0 and prints the section headings Landed, Running, Queue and Waiting, in that order (logic in `veri/status.py`, the `.sh` shim unchanged) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 50 | 22 | 38 | 5418 | 504788 | 93367 | 0.34 | 463 | unknown | 0/5 | nothing-left |  |  | full |
| With no `.tdd/report-cache.json` snapshot, Queue says there is no snapshot while Landed, Running and Waiting still print ⟦criterion 3⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 88 | 32 | 64 | 8551 | 868204 | 124603 | 0.60 | 743 | 1/2 | 0/5 | nothing-left |  |  | full |
| An empty Landed, Running or Waiting section keeps its heading and says "none" ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 51 | 20 | 40 | 5363 | 544342 | 72329 | 0.29 | 427 | unknown | 0/5 | nothing-left |  |  | full |
| With a snapshot present, Queue's first line states the snapshot's age, computed from its `fetched_at` ⟦criterion 3⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 121 | 34 | 68 | 10416 | 941759 | 132126 | 0.63 | 774 | 1/2 | 0/5 | nothing-left |  |  | full |
| Queue counts the snapshot's open opted-in (`VERI_LABEL`) issues by label ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 111 | 27 | 54 | 8038 | 764079 | 93081 | 0.39 | 712 | unknown | 1/5 | nothing-left |  |  | full |
| Queue lists each open opted-in issue the snapshot shows blocked, with the open issue blocking it, taken from that issue's `blockedBy` ⟦criterion 1⟧ | 12 | 4 | 1 | 0 | 0 | 0 | 178 | 65 | 124 | 19769 | 1773835 | 208804 | 1.13 | 1296 | 2/2 | 1/5 | nothing-left |  |  | already-satisfied |
| Landed lists one line per local `vN.M` tag, carrying the tag and its message (the capability) ⟦criterion 1⟧ | 14 | 3 | 3 | 0 | 0 | 0 | 383 | 98 | 188 | 37572 | 2974521 | 384281 | 2.01 | 2588 | red 2/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| Landed leaves out a tag cut before the time in `.tdd/status-last` ⟦criterion 1⟧ | 7 | 2 | 0 | 0 | 0 | 0 | 150 | 39 | 72 | 14843 | 989722 | 192410 | 0.95 | 1028 | 2/2 | 0/5 | nothing-left |  |  | full |
| Running lists one block headed `#<n>` for each run whose journal (`$VERI_HOME/runs/<owner>-<repo>/<n>.jsonl`) holds a `conductor-start` event whose `pid` answers `kill -0` with a start time matching its `started` ⟦criterion 1⟧ | 12 | 3 | 2 | 0 | 0 | 0 | 316 | 74 | 134 | 23701 | 1988251 | 249905 | 1.34 | 1309 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| Running leaves out a run whose journal's `conductor-start` pid is dead or whose start time does not match `started` ⟦criterion 1⟧ | 11 | 3 | 1 | 0 | 0 | 0 | 221 | 57 | 106 | 22235 | 1509848 | 217619 | 1.19 | 964 | 2/2 | 0/5 | structural-owed |  |  | already-satisfied |
| A Running block shows the run's steps ticked of planned: its journal's `step-done` events of the latest `plan` event's `steps` ⟦criterion 1⟧ | 7 | 2 | 0 | 0 | 0 | 0 | 144 | 48 | 88 | 15757 | 1316716 | 195417 | 1.08 | 981 | 2/2 | 0/5 | nothing-left |  |  | full |
| A Running block shows the run's phase now, from its journal's latest `launch` event ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 97 | 40 | 74 | 9826 | 1091663 | 95558 | 0.45 | 673 | unknown | 1/5 | nothing-left |  |  | full |
| A Running block shows the attempts in the run's current phase, from its journal's `launch` events ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 76 | 29 | 50 | 7953 | 721096 | 80644 | 0.35 | 595 | unknown | 0/5 | nothing-left |  |  | full |
| A Running block shows the run's PASS and REJECT verdict counts, from its journal's `verdict` events ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 83 | 27 | 48 | 6033 | 687039 | 78805 | 0.33 | 655 | unknown | 0/5 | nothing-left |  |  | full |
| A Running block shows the run's cost as the `| total |` row of its metrics, computed in-process from its journal ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 175 | 50 | 94 | 14643 | 1328367 | 201613 | 0.88 | 1739 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| A Running block shows the model each role (developer, revise, verifier, conductor) ran on, computed in-process from its journal ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 231 | 54 | 100 | 17406 | 1384024 | 218520 | 0.97 | 1654 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| Running's awake wall time for a run is its journal's last event's `awake` minus its first event's `awake` ⟦criterion 5⟧ | 7 | 1 | 0 | 0 | 0 | 0 | 169 | 37 | 66 | 14980 | 961460 | 143215 | 0.89 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `status.sh --report` exits 0 and prints the section headings Landed, Running, Queue and Waiting, in that order (logic in `veri/status.py`, the `.sh` shim unchanged) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |
| With no `.tdd/report-cache.json` snapshot, Queue says there is no snapshot while Landed, Running and Waiting still print ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 12 | 0.09 |
| An empty Landed, Running or Waiting section keeps its heading and says "none" ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 13 | 0.05 |
| With a snapshot present, Queue's first line states the snapshot's age, computed from its `fetched_at` ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 12 | 0.09 |
| Queue counts the snapshot's open opted-in (`VERI_LABEL`) issues by label ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 125 | 0.11 |
| Queue lists each open opted-in issue the snapshot shows blocked, with the open issue blocking it, taken from that issue's `blockedBy` ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 172 | 0.12 |
| Landed lists one line per local `vN.M` tag, carrying the tag and its message (the capability) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.08 |
| Landed leaves out a tag cut before the time in `.tdd/status-last` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 39 | 0.07 |
| Running lists one block headed `#<n>` for each run whose journal (`$VERI_HOME/runs/<owner>-<repo>/<n>.jsonl`) holds a `conductor-start` event whose `pid` answers `kill -0` with a start time matching its `started` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 26 | 0.05 |
| Running leaves out a run whose journal's `conductor-start` pid is dead or whose start time does not match `started` ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 9 | 0.04 |
| A Running block shows the run's steps ticked of planned: its journal's `step-done` events of the latest `plan` event's `steps` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |
| A Running block shows the run's phase now, from its journal's latest `launch` event ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 171 | 0.15 |
| A Running block shows the attempts in the run's current phase, from its journal's `launch` events ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| A Running block shows the run's PASS and REJECT verdict counts, from its journal's `verdict` events ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 17 | 0.04 |
| A Running block shows the run's cost as the `| total |` row of its metrics, computed in-process from its journal ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.04 |
| A Running block shows the model each role (developer, revise, verifier, conductor) ran on, computed in-process from its journal ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.04 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 9 | 6 | 12 | 12 | 6 | 6 | 8 | 10 | 11 | 11 | 6 | 6 | 6 | 11 | 8 | 10 | 14 | 10 | 8 | 6 | 9 | 7 | 6 | 11 | 11 | 8 | 9 | 7 | 5 | 5 | 5 | 9 | 7 | 9 | 13 | 8 | 1 | 9 | 7 | 8 | 17 | 17 | 9 | 9 | 7 | 11 | 14 | 13 | 7 | 8 | 17 | 11 | 9 | 9 | 11 | 12 | 18 | 18 | 16 | 11 | 9 | 12 | 10 | 15 | 9 | 13 | 8 | 10 | 12 | 8 | 12 | 8 | 11 | 7 | 9 | 8 | 9 | 8 | 8 | 11 | 0 | 12 | 9 | 10 | 9 | 10 | 10 | 12 | 12 | 13 | 9 | 11 | 12 | 8 | 8 | 11 | 10 | 8 | 7 | 7 | 11 | 11 | 9 | 10 | 9 | 13 | 11 | 9 | 9 | 7 | 8 | 19 | 17 | 11 | 11 | 13 | 33 | 17 | 23 | 26 | 23 | 15 | 11 | 12 | 16 | 13 | 18 | 19 | 11 | 11 | 12 | 11 | 10 | 9 | 10 | 15 | 11 | 10 |
| fast | 62 | 77 | 73 | 62 | 85 | 53 | 60 | 53 | 88 | 74 | 72 | 55 | 68 | 88 | 81 | 59 | 59 | 108 | 73 | 90 | 98 | 82 | 83 | 80 | 82 | 94 | 81 | 96 | 62 | 57 | 65 | 50 | 51 | 59 | 60 | 56 | 61 | 65 | 49 | 61 | 85 | 56 | 54 | 52 | 64 | 59 | 63 | 68 | 66 | 92 | 72 | 73 | 74 | 126 | 108 | 150 | 85 | 76 | 70 | 91 | 86 | 66 | 50 | 74 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 6 | 7 | 7 | 9 | 7 | 7 | 6 | 5 | 9 | 9 | 8 | 6 | 6 | 7 | 10 | 11 | 11 | 6 | 10 | 8 | 9 | 8 | 12 | 16 | 14 | 10 | 8 | 10 | 7 | 9 | 8 | 7 | 8 | 8 | 8 | 7 | 7 | 6 | 5 | 6 | 9 | 10 | 10 | 7 | 10 | 11 | 10 | 11 | 12 | 10 | 7 | 9 | 9 | 8 | 8 | 8 | 8 | 8 | 10 | 9 | 10 | 9 | 9 | 10 | 10 | 7 | 7 | 7 | 7 | 7 | 7 | 13 | 16 | 13 | 12 | 11 | 13 | 13 | 11 | 13 | 20 | 18 | 16 | 14 | 14 | 18 | 13 | 12 | 12 | 11 | 10 | 10 | 11 | 10 | 11 | 8 | 9 | 8 | 7 | 9 | 9 | 9 | 9 | 9 | 10 | 9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 755 | 1412 | 245624 | 20366871 | 2830079 | 25.10 (estimate) |
