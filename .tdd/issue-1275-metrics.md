### 📊 Metrics — issue 1275

Wall time for the issue: 3868 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1394.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1284 | 12489 | 34343 | 0.15 |
| red | 4 | 0 | 0 | 0 | 251 | 226 | 53 | 104 | 30340 | 3263431 | 247473 | 1.62 |
| pin | 4 | 4 | 0 | 0 | 78 | 61 | 23 | 46 | 7666 | 1031868 | 172511 | 0.87 |
| green | 12 | 4 | 2 | 0 | 815 | 201 | 74 | 146 | 25485 | 3417164 | 531049 | 2.72 |
| refactor | 8 | 4 | 0 | 0 | 647 | 135 | 45 | 86 | 15196 | 1994704 | 356974 | 1.78 |
| diff | 4 | 2 | 0 | 0 | 502 | 81 | 29 | 54 | 9228 | 1243840 | 171698 | 0.90 |
| predicate | 1 | 0 | 0 | 0 | 13 | 10 | 4 | 8 | 1195 | 167764 | 43716 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 17 | 15 | 2 | 0 | 1297 | 280 | 97 | 184 | 33147 | 4135230 | 726900 | 3.65 |
| developer | claude-sonnet-5-5 | 17 | 0 | 0 | 0 | 1021 | 443 | 132 | 262 | 57247 | 6996030 | 830864 | 4.60 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 445 | 1.75 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A leaf's outcome — success with its captured output, failure with its output, a slow-but-alive leaf surviving the heartbeat, and the .tdd/<name>.exit record of 0, 1 and 2 — is pinned through run_cli in tests/py/test_supervise.py: replaces 'exit-0 leaf → success + captured output', 'exit-nonzero leaf → failure + output', 'slow-but-alive leaf survives heartbeat → success', '.tdd/<name>.exit records the supervisor's own final code, killed-stuck included' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 136 | 42 | 82 | 17607 | 2093302 | 281580 | 1.51 | 436 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| A hung or runaway leaf is killed-stuck by the heartbeat or the hard timeout, on the default 180s or an explicit window, runs once under an ambient VERI_STUCK_RETRIES the suite overrides to 0, and leaves no usage event while exiting and recording 2 — pinned through run_cli in tests/py/test_supervise.py: replaces 'hung leaf → killed-stuck via heartbeat', 'runaway leaf → killed-stuck via hard timeout', 'ambient VERI_STUCK_RETRIES=3 → hung leaf still runs exactly once', 'VERI_HEARTBEAT unset → a 180s window, explicit VERI_HEARTBEAT=5 → a 5s window', 'a killed leaf leaves no usage event and the supervisor still exits 2 and records 2' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 184 | 50 | 98 | 22918 | 2642950 | 294564 | 1.67 | 828 | unknown | 1/5 | nothing-left |  |  | already-satisfied |
| A relaunched killed-stuck leaf's retry event carries the kill cause, and every supervised leaf's exit event carries its 0/1/2 status, the kill cause and the attempt's wall seconds — pinned through run_cli in tests/py/test_supervise.py: replaces 'a relaunched killed-stuck leaf appends one retry event carrying the kill cause', 'a supervised leaf appends one exit event carrying the 0/1/2 status, the kill cause and the attempt's wall seconds' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 165 | 53 | 106 | 20406 | 2662575 | 371769 | 1.96 | 415 | 1/2 | 1/5 | nothing-structural |  |  | already-satisfied |
| A killed-stuck leaf that succeeds on its retry ends the supervision in success with the retry's output — pinned through run_cli in tests/py/test_supervise.py: replaces 'killed-stuck-then-succeeds leaf is retried → success' in skills/tdd/scripts/tests/supervise-retry.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 138 | 50 | 96 | 17756 | 2308340 | 360094 | 1.85 | 456 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| supervise-retry.test.sh is deleted, and nothing outside .tdd/ and docs/ names it: its slices in tests/hermetic/hermetic-suites.test.sh are dropped or updated, the CLAUDE.md Testing idiom sentence "supervise.sh has a second suite for its retry axis" is removed, and CLAUDE.md's suite-file count matches the tree ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 15 | 28 | 4849 | 648463 | 86597 | 0.46 | 299 | n/a | n/a | n/a |  |  | full |
| supervise.test.sh's remaining cases still pass and the file stays for the other C4d groups; no guard table, roster or workflow comment loses a reference it still needs ⟦diff-checked⟧ ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 48 | 18 | 34 | 5574 | 763141 | 128817 | 0.65 | 262 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A leaf's outcome — success with its captured output, failure with its output, a slow-but-alive leaf surviving the heartbeat, and the .tdd/<name>.exit record of 0, 1 and 2 — is pinned through run_cli in tests/py/test_supervise.py: replaces 'exit-0 leaf → success + captured output', 'exit-nonzero leaf → failure + output', 'slow-but-alive leaf survives heartbeat → success', '.tdd/<name>.exit records the supervisor's own final code, killed-stuck included' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 73 | 0.39 |
| A hung or runaway leaf is killed-stuck by the heartbeat or the hard timeout, on the default 180s or an explicit window, runs once under an ambient VERI_STUCK_RETRIES the suite overrides to 0, and leaves no usage event while exiting and recording 2 — pinned through run_cli in tests/py/test_supervise.py: replaces 'hung leaf → killed-stuck via heartbeat', 'runaway leaf → killed-stuck via hard timeout', 'ambient VERI_STUCK_RETRIES=3 → hung leaf still runs exactly once', 'VERI_HEARTBEAT unset → a 180s window, explicit VERI_HEARTBEAT=5 → a 5s window', 'a killed leaf leaves no usage event and the supervisor still exits 2 and records 2' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 451 | 0.47 |
| A relaunched killed-stuck leaf's retry event carries the kill cause, and every supervised leaf's exit event carries its 0/1/2 status, the kill cause and the attempt's wall seconds — pinned through run_cli in tests/py/test_supervise.py: replaces 'a relaunched killed-stuck leaf appends one retry event carrying the kill cause', 'a supervised leaf appends one exit event carrying the 0/1/2 status, the kill cause and the attempt's wall seconds' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 71 | 0.50 |
| A killed-stuck leaf that succeeds on its retry ends the supervision in success with the retry's output — pinned through run_cli in tests/py/test_supervise.py: replaces 'killed-stuck-then-succeeds leaf is retried → success' in skills/tdd/scripts/tests/supervise-retry.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.41 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 25 | 22 | 0 | 1 | 1 | 23 | 22 | 0 | 371 | 1 | 1 | 0 | 0 | 22 | 22 | 1 | 1 | 1 | 0 | 42 | 23 | 2 | 27 | 76 | 2 | 0 | 1 | 6 | 20 | 40 |
| target | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 23 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |
| fast | 23 | 23 | 24 | 22 | 24 | 22 | 23 | 24 | 24 | 24 | 23 | 24 | 23 | 24 | 22 | 22 | 22 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 229 | 446 | 90394 | 11131260 | 1557764 | 8.25 |
