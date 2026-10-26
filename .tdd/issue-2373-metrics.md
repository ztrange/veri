### 📊 Metrics — issue 2373

Wall time for the issue: 1525 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 7 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $11.75 over 206 turns, in 4 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87639 tokens, largest 196685 tokens
Conductor context: first turn 87634 tokens, largest 111033 tokens
Conductor context: first turn 88004 tokens, largest 175865 tokens
Conductor context: first turn 88111 tokens, largest 160879 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87639 |
| 2 | $0.04 | 88189 |
| 3 | $0.04 | 89141 |
| 4 | $0.04 | 91042 |
| 5 | $0.04 | 91367 |
| 6 | $0.03 | 91769 |
| 7 | $0.04 | 92155 |
| 8 | $0.03 | 92497 |
| 9 | $0.04 | 93135 |
| 10 | $0.04 | 94071 |
| 11 | $0.05 | 96406 |
| 12 | $0.05 | 99510 |
| 13 | $0.07 | 104000 |
| 14 | $0.05 | 106286 |
| 15 | $0.05 | 107190 |
| 16 | $0.03 | 107611 |
| 17 | $0.04 | 108405 |
| 18 | $0.04 | 108969 |
| 19 | $0.04 | 109562 |
| 20 | $0.04 | 110148 |
| 21 | $0.05 | 111548 |
| 22 | $0.04 | 112317 |
| 23 | $0.04 | 112746 |
| 24 | $0.04 | 113461 |
| 25 | $0.04 | 114070 |
| 26 | $0.04 | 114727 |
| 27 | $0.05 | 116469 |
| 28 | $0.05 | 117603 |
| 29 | $0.04 | 118344 |
| 30 | $0.05 | 119599 |
| 31 | $0.04 | 120217 |
| 32 | $0.10 | 127899 |
| 33 | $0.05 | 129727 |
| 34 | $0.05 | 130699 |
| 35 | $0.04 | 131794 |
| 36 | $0.05 | 132455 |
| 37 | $0.05 | 134222 |
| 38 | $0.05 | 134759 |
| 39 | $0.05 | 136212 |
| 40 | $0.06 | 139311 |
| 41 | $0.05 | 140115 |
| 42 | $0.05 | 140725 |
| 43 | $0.04 | 141153 |
| 44 | $0.05 | 142245 |
| 45 | $0.05 | 143091 |
| 46 | $0.05 | 143949 |
| 47 | $0.05 | 144871 |
| 48 | $0.04 | 145525 |
| 49 | $0.05 | 146445 |
| 50 | $0.06 | 147733 |
| 51 | $0.05 | 148826 |
| 52 | $0.05 | 150047 |
| 53 | $0.06 | 152130 |
| 54 | $0.05 | 152725 |
| 55 | $0.07 | 156096 |
| 56 | $0.11 | 164316 |
| 57 | $0.06 | 165772 |
| 58 | $0.05 | 166851 |
| 59 | $0.06 | 167956 |
| 60 | $0.05 | 168357 |
| 61 | $0.05 | 169082 |
| 62 | $0.06 | 171455 |
| 63 | $0.06 | 172154 |
| 64 | $0.06 | 174152 |
| 65 | $0.06 | 175010 |
| 66 | $0.05 | 176364 |
| 67 | $0.06 | 177801 |
| 68 | $0.06 | 178459 |
| 69 | $0.05 | 179527 |
| 70 | $0.06 | 180626 |
| 71 | $0.07 | 182792 |
| 72 | $0.06 | 183909 |
| 73 | $0.05 | 184814 |
| 74 | $0.06 | 185604 |
| 75 | $0.06 | 186759 |
| 76 | $0.06 | 188345 |
| 77 | $0.06 | 189206 |
| 78 | $0.09 | 194375 |
| 79 | $0.06 | 195451 |
| 80 | $0.07 | 196685 |
| 81 | $0.57 | 87634 |
| 82 | $0.04 | 88724 |
| 83 | $0.04 | 90591 |
| 84 | $0.03 | 91378 |
| 85 | $0.06 | 94591 |
| 86 | $0.06 | 98402 |
| 87 | $0.03 | 98859 |
| 88 | $0.03 | 99279 |
| 89 | $0.03 | 99607 |
| 90 | $0.03 | 99931 |
| 91 | $0.05 | 101698 |
| 92 | $0.04 | 103282 |
| 93 | $0.06 | 107373 |
| 94 | $0.04 | 108384 |
| 95 | $0.05 | 109761 |
| 96 | $0.04 | 111033 |
| 97 | $0.58 | 88004 |
| 98 | $0.03 | 88347 |
| 99 | $0.04 | 89678 |
| 100 | $0.04 | 91681 |
| 101 | $0.04 | 92031 |
| 102 | $0.03 | 92402 |
| 103 | $0.03 | 92778 |
| 104 | $0.04 | 93106 |
| 105 | $0.03 | 93768 |
| 106 | $0.04 | 95059 |
| 107 | $0.05 | 96938 |
| 108 | $0.06 | 100904 |
| 109 | $0.06 | 103640 |
| 110 | $0.05 | 105985 |
| 111 | $0.03 | 106429 |
| 112 | $0.04 | 107008 |
| 113 | $0.04 | 107570 |
| 114 | $0.04 | 108121 |
| 115 | $0.03 | 108727 |
| 116 | $0.15 | 122837 |
| 117 | $0.04 | 123252 |
| 118 | $0.04 | 124020 |
| 119 | $0.04 | 124658 |
| 120 | $0.04 | 124944 |
| 121 | $0.05 | 125653 |
| 122 | $0.04 | 126312 |
| 123 | $0.05 | 127779 |
| 124 | $0.05 | 129158 |
| 125 | $0.04 | 130024 |
| 126 | $0.10 | 137872 |
| 127 | $0.05 | 138810 |
| 128 | $0.04 | 139480 |
| 129 | $0.06 | 141551 |
| 130 | $0.05 | 142414 |
| 131 | $0.04 | 143327 |
| 132 | $0.05 | 143963 |
| 133 | $0.05 | 145264 |
| 134 | $0.05 | 146534 |
| 135 | $0.05 | 147934 |
| 136 | $0.06 | 149580 |
| 137 | $0.04 | 150264 |
| 138 | $0.06 | 151929 |
| 139 | $0.05 | 152826 |
| 140 | $0.05 | 153411 |
| 141 | $0.04 | 153774 |
| 142 | $0.05 | 154486 |
| 143 | $0.06 | 156630 |
| 144 | $0.05 | 157720 |
| 145 | $0.06 | 159584 |
| 146 | $0.06 | 161989 |
| 147 | $0.07 | 164316 |
| 148 | $0.05 | 165381 |
| 149 | $0.06 | 167327 |
| 150 | $0.05 | 167700 |
| 151 | $0.05 | 168956 |
| 152 | $0.06 | 169940 |
| 153 | $0.07 | 174031 |
| 154 | $0.06 | 175005 |
| 155 | $0.05 | 175865 |
| 156 | $0.57 | 88111 |
| 157 | $0.03 | 89632 |
| 158 | $0.03 | 91537 |
| 159 | $0.02 | 91886 |
| 160 | $0.12 | 104365 |
| 161 | $0.05 | 108203 |
| 162 | $0.03 | 108749 |
| 163 | $0.03 | 109241 |
| 164 | $0.02 | 109538 |
| 165 | $0.02 | 109829 |
| 166 | $0.03 | 110543 |
| 167 | $0.03 | 111610 |
| 168 | $0.03 | 112241 |
| 169 | $0.03 | 112853 |
| 170 | $0.03 | 113634 |
| 171 | $0.03 | 114831 |
| 172 | $0.03 | 115844 |
| 173 | $0.03 | 117110 |
| 174 | $0.03 | 117793 |
| 175 | $0.03 | 118737 |
| 176 | $0.03 | 119035 |
| 177 | $0.03 | 120119 |
| 178 | $0.03 | 120629 |
| 179 | $0.04 | 122260 |
| 180 | $0.03 | 123200 |
| 181 | $0.03 | 124127 |
| 182 | $0.03 | 124993 |
| 183 | $0.03 | 125824 |
| 184 | $0.03 | 126734 |
| 185 | $0.03 | 127412 |
| 186 | $0.03 | 128465 |
| 187 | $0.04 | 129709 |
| 188 | $0.05 | 132145 |
| 189 | $0.03 | 132948 |
| 190 | $0.03 | 133165 |
| 191 | $0.03 | 133803 |
| 192 | $0.03 | 134423 |
| 193 | $0.04 | 135634 |
| 194 | $0.03 | 136460 |
| 195 | $0.05 | 139172 |
| 196 | $0.03 | 139923 |
| 197 | $0.09 | 147813 |
| 198 | $0.04 | 149357 |
| 199 | $0.04 | 150534 |
| 200 | $0.04 | 151481 |
| 201 | $0.03 | 151999 |
| 202 | $0.04 | 153608 |
| 203 | $0.04 | 154852 |
| 204 | $0.04 | 155504 |
| 205 | $0.04 | 156807 |
| 206 | $0.06 | 160879 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 13 | 1 | 2 | 1095 | 0 | 31754 | 0.09 |
| red | 11 | 4 | 2 | 0 | 651 | 316 | 78 | 152 | 34405 | 2961026 | 325104 | 1.89 |
| green | 13 | 1 | 4 | 0 | 1708 | 602 | 121 | 238 | 55920 | 4675489 | 360743 | 2.91 |
| red-supersede | 1 | 0 | 0 | 0 | 76 | 54 | 6 | 12 | 6626 | 863294 | 178717 | 0.60 |
| exhausted | 2 | 0 | 0 | 0 | 47 | 43 | 6 | 10 | 2963 | 123932 | 30883 | 0.24 |
| diff | 2 | 1 | 0 | 0 | 106 | 34 | 11 | 22 | 3849 | 328931 | 73869 | 0.26 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 2 | 4 | 312 | 48594 | 14853 | 0.05 |
| pin | 1 | 1 | 0 | 0 | 15 | 11 | 4 | 8 | 1343 | 108106 | 15030 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 8 | 6 | 0 | 850 | 186 | 54 | 108 | 19673 | 1450760 | 270668 | 1.02 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 1263 | 608 | 128 | 248 | 61829 | 5812331 | 595235 | 3.51 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 512 | 283 | 47 | 92 | 25011 | 1846281 | 165050 | 1.57 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 1012 | 3.17 | 99 | 0.18 |
| green | 762 | 1.39 | 694 | 0.74 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 26 | 0.11 |
| diff | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When run-conductor's pre-launch fetch of issue <n>'s body yields no answer (gh refuses or errors), run-conductor.sh writes exactly one stderr line naming the skip, `run-conductor.sh: issue body unavailable, Requirements row IDs unchecked`, and still goes on to launch the conductor; a small in-process case faking only the gh boundary ⟦criterion 2⟧ | 18 | 4 | 3 | 0 | 0 | 0 | 787 | 150 | 292 | 75823 | 6701622 | 729096 | 4.52 | 260 | green 2/2, red 1/2 | 0/5 | nothing-left |  |  | full |
| skills/tdd/scripts/tests/py/test_run_conductor.py: the existing launch cases answer run_conductor's pre-launch issue-body gh call through one shared in-process fake of the gh boundary (one seam, one fake — not an edit per case, not a gh stub on PATH) that returns an empty body, so the row-ID check finds no rows, the launch proceeds and nothing new lands on the stderr those cases compare exactly; the fake is scoped so a case that exercises the fetch itself can still reach the real boundary (not a module-wide autouse fake nothing opts out of); every case keeps asserting exactly what it asserts today; test file only, no production change ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 11 | 22 | 3849 | 328931 | 73869 | 0.26 | 144 | n/a | n/a | n/a |  |  | full |
| When the pre-launch issue-body fetch yields no answer, the launch goes ahead exactly as it did before this issue: the conductor is launched and run-conductor exits with the conductor's own code, never 2 for the missing body; a small in-process case faking only the gh boundary ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 13 | 26 | 4661 | 427281 | 39577 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| When the fetched issue body's `## Requirements` table has a row whose ID is bare `<next>`, run-conductor.sh exits 2 in preflight, before any conductor or leaf is launched, with a stderr line naming `<next>`, applying the same row-ID rule skill_edit_step.py applies (neither `<prefix><digits>` nor `<prefix><next>`); a small in-process case faking only the gh boundary ⟦criterion 1⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 204 | 54 | 106 | 21085 | 1651538 | 156657 | 1.04 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When run-conductor's pre-launch fetch of issue <n>'s body yields no answer (gh refuses or errors), run-conductor.sh writes exactly one stderr line naming the skip, `run-conductor.sh: issue body unavailable, Requirements row IDs unchecked`, and still goes on to launch the conductor; a small in-process case faking only the gh boundary ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 17 | 17 | 16 | 19 | 16 | 17 | 16 | 15 | 20 | 15 | 17 | 17 | 2 | 18 | 16 | 15 | 16 | 14 | 15 | 15 | 14 | 85 | 13 | 81 | 15 | 84 |
| target | 16 | 1 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 18 | 18 | 21 | 18 | 19 | 20 | 19 | 19 | 18 | 17 | 17 | 18 | 18 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 229 | 448 | 106513 | 9109372 | 1030953 | 6.09 |
