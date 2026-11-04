### 📊 Metrics — issue 2952

Wall time for the issue: 7356 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3031.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.69 over 81 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90189 tokens, largest 188117 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90189 |
| 2 | $0.08 | 97341 |
| 3 | $0.04 | 99411 |
| 4 | $0.04 | 101322 |
| 5 | $0.02 | 101578 |
| 6 | $0.02 | 102034 |
| 7 | $0.02 | 102339 |
| 8 | $0.02 | 102655 |
| 9 | $0.02 | 102906 |
| 10 | $0.03 | 103519 |
| 11 | $0.04 | 106286 |
| 12 | $0.05 | 109633 |
| 13 | $0.04 | 112026 |
| 14 | $0.03 | 112492 |
| 15 | $0.03 | 113255 |
| 16 | $0.03 | 113758 |
| 17 | $0.03 | 114166 |
| 18 | $0.03 | 114977 |
| 19 | $0.03 | 116280 |
| 20 | $0.03 | 117153 |
| 21 | $0.03 | 117973 |
| 22 | $0.03 | 118631 |
| 23 | $0.03 | 119246 |
| 24 | $0.03 | 120453 |
| 25 | $0.03 | 121265 |
| 26 | $0.09 | 129774 |
| 27 | $0.04 | 131537 |
| 28 | $0.03 | 132407 |
| 29 | $0.03 | 133265 |
| 30 | $0.03 | 133813 |
| 31 | $0.03 | 134357 |
| 32 | $0.03 | 135056 |
| 33 | $0.03 | 135920 |
| 34 | $0.03 | 136746 |
| 35 | $0.03 | 137644 |
| 36 | $0.04 | 138864 |
| 37 | $0.03 | 139688 |
| 38 | $0.04 | 141237 |
| 39 | $0.03 | 142074 |
| 40 | $0.04 | 143299 |
| 41 | $0.04 | 144138 |
| 42 | $0.04 | 145793 |
| 43 | $0.05 | 148739 |
| 44 | $0.04 | 149409 |
| 45 | $0.03 | 149785 |
| 46 | $0.04 | 151372 |
| 47 | $0.04 | 152566 |
| 48 | $0.04 | 153358 |
| 49 | $0.04 | 155015 |
| 50 | $0.04 | 155804 |
| 51 | $0.05 | 157549 |
| 52 | $0.04 | 158366 |
| 53 | $0.04 | 159691 |
| 54 | $0.04 | 160362 |
| 55 | $0.04 | 161471 |
| 56 | $0.04 | 162709 |
| 57 | $0.04 | 163471 |
| 58 | $0.08 | 169082 |
| 59 | $0.05 | 170551 |
| 60 | $0.04 | 171594 |
| 61 | $0.04 | 172419 |
| 62 | $0.05 | 173885 |
| 63 | $0.04 | 174842 |
| 64 | $0.04 | 175270 |
| 65 | $0.05 | 176666 |
| 66 | $0.04 | 177535 |
| 67 | $0.05 | 179195 |
| 68 | $0.04 | 179830 |
| 69 | $0.04 | 180888 |
| 70 | $0.05 | 182218 |
| 71 | $0.05 | 183587 |
| 72 | $0.04 | 184365 |
| 73 | $0.04 | 184597 |
| 74 | $0.04 | 185022 |
| 75 | $0.04 | 185398 |
| 76 | $0.04 | 185904 |
| 77 | $0.04 | 186119 |
| 78 | $0.04 | 186440 |
| 79 | $0.04 | 187009 |
| 80 | $0.04 | 187534 |
| 81 | $0.04 | 188117 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1159 | 0 | 33011 | 0.09 |
| red | 11 | 4 | 0 | 0 | 621 | 271 | 57 | 110 | 18270 | 1640275 | 326990 | 1.16 |
| green | 14 | 4 | 3 | 0 | 1434 | 332 | 64 | 124 | 18804 | 1836236 | 248745 | 1.22 |
| refactor | 5 | 1 | 0 | 0 | 161 | 69 | 18 | 34 | 3677 | 447805 | 118567 | 0.38 |
| pin | 4 | 2 | 2 | 0 | 149 | 80 | 15 | 30 | 6173 | 365333 | 116069 | 0.39 |
| red-missing | 1 | 0 | 0 | 0 | 37 | 23 | 3 | 6 | 2278 | 84286 | 17929 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 17 | 12 | 5 | 0 | 1369 | 390 | 66 | 130 | 23028 | 1781204 | 339223 | 1.26 |
| developer | claude-sonnet-5-5 | 15 | 0 | 0 | 0 | 661 | 320 | 73 | 140 | 21950 | 2081946 | 415266 | 1.47 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 384 | 74 | 19 | 36 | 5383 | 510785 | 106822 | 0.60 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 97 | 0.29 |
| green | 1283 | 1.09 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 70 | 0.21 |
| red-missing | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tick-ledger.sh on an open step whose text names its go-red control as a file at a hex commit (the wording "the go-red control is", a path, "at", a 7-40 hex sha), with no .tdd/issue-<n>-mutations.md beside the ledger, exits 2, names the missing mutation record on stderr and leaves the ledger file byte-for-byte unchanged ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 128 | 26 | 50 | 7936 | 675911 | 157827 | 0.65 | 1092 | 1/2 | 0/5 | nothing-left |  |  | full |
| tick-ledger.sh on an open step whose text holds the wording "mutation-probe.sh --before" followed by a 7-40 hex sha, with no mutation record file beside the ledger, exits 2, names the missing record on stderr and leaves the ledger unchanged ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 88 | 20 | 38 | 4598 | 519743 | 123427 | 0.41 | 720 | unknown | 0/5 | nothing-left |  |  | full |
| tick-ledger.sh on a step naming a before-sha control exits 0 and ticks the step once the mutation record file beside the ledger holds a before record for that same sha ⟦criterion 2⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 57 | 10 | 20 | 3879 | 273201 | 71390 | 0.24 | unknown | unknown | unknown | unknown |  |  | full |
| tick-ledger.sh on a step naming a before-sha control still exits 2 with the ledger unchanged when the mutation record file holds only a before record for a different sha ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 238 | 40 | 78 | 12103 | 1163999 | 164765 | 0.77 | 1307 | 1/2 | 1/5 | nothing-structural |  |  | full |
| tick-ledger.sh on a step naming its go-red control as a file at a hex commit exits 0 and ticks the step once the mutation record file holds a file/old/new record for that file ⟦criterion 2⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 44 | 10 | 20 | 3786 | 291616 | 74738 | 0.25 | unknown | unknown | unknown | unknown |  |  | full |
| tick-ledger.sh on a step naming its go-red control as a file at a hex commit still exits 2 with the ledger unchanged when the mutation record file holds only a file/old/new record for a different file and no before record ⟦added⟧ ⟦criterion 1⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 170 | 38 | 74 | 12444 | 1095897 | 159733 | 0.63 | 1157 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| tick-ledger.sh on a step whose text mentions "go-red control" bare, with neither wording and no mutation record file, ticks the step and exits 0 as before ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 13 | 24 | 4456 | 353568 | 76420 | 0.27 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tick-ledger.sh on an open step whose text names its go-red control as a file at a hex commit (the wording "the go-red control is", a path, "at", a 7-40 hex sha), with no .tdd/issue-<n>-mutations.md beside the ledger, exits 2, names the missing mutation record on stderr and leaves the ledger file byte-for-byte unchanged ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.09 |
| tick-ledger.sh on an open step whose text holds the wording "mutation-probe.sh --before" followed by a 7-40 hex sha, with no mutation record file beside the ledger, exits 2, names the missing record on stderr and leaves the ledger unchanged ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 14 | 0.06 |
| tick-ledger.sh on a step naming a before-sha control still exits 2 with the ledger unchanged when the mutation record file holds only a before record for a different sha ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 121 | 0.18 |
| tick-ledger.sh on a step naming its go-red control as a file at a hex commit still exits 2 with the ledger unchanged when the mutation record file holds only a file/old/new record for a different file and no before record ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 16 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s | run 146 s | run 147 s | run 148 s | run 149 s | run 150 s | run 151 s | run 152 s | run 153 s | run 154 s | run 155 s | run 156 s | run 157 s | run 158 s | run 159 s | run 160 s | run 161 s | run 162 s | run 163 s | run 164 s | run 165 s | run 166 s | run 167 s | run 168 s | run 169 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 4 | 4 | 5 | 4 | 4 | 9 | 7 | 5 | 4 | 4 | 5 | 6 | 6 | 7 | 11 | 6 | 6 | 6 | 8 | 5 | 4 | 5 | 4 | 7 | 7 | 8 | 5 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 42 | 48 | 41 | 52 | 39 | 38 | 64 | 63 | 53 | 36 | 46 | 42 | 52 | 60 | 56 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 4 | 5 | 4 | 4 | 3 | 4 | 4 | 4 | 7 | 6 | 7 | 6 | 8 | 4 | 5 | 6 | 5 | 4 | 5 | 6 | 6 | 5 | 7 | 5 | 5 | 6 | 5 | 4 | 4 | 8 | 7 | 7 | 5 | 5 | 5 | 4 | 5 | 7 | 6 | 0 | 3 | 6 | 7 | 6 | 4 | 5 | 5 | 5 | 5 | 5 | 6 | 4 | 6 | 6 | 4 | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 5 | 5 | 4 | 5 | 5 | 6 | 9 | 6 | 6 | 4 | 5 | 5 | 5 | 4 | 5 | 6 | 4 | 4 | 5 | 4 | 6 | 7 | 7 | 4 | 6 | 5 | 5 | 6 | 6 | 6 | 5 | 7 | 6 | 8 | 7 | 6 | 5 | 5 | 5 | 7 | 5 | 8 | 7 | 7 | 6 | 4 | 3 | 5 | 7 | 6 | 7 | 6 | 5 | 5 | 4 | 4 | 4 | 4 | 3 | 4 | 6 | 6 | 1 | 7 | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 6 | 5 | 6 | 7 | 5 | 5 | 5 | 4 | 6 | 6 | 6 | 5 | 7 | 5 | 5 | 4 | 4 | 9 | 7 | 6 | 5 | 6 | 5 | 4 | 4 | 6 | 6 | 5 | 5 | 6 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 158 | 306 | 50361 | 4373935 | 861311 | 7.01 (estimate) |
