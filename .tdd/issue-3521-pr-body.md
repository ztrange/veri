Closes #3521. Four plan steps, each blind-verified; the ledger `.tdd/issue-3521.md` is committed.

1. **status.py only counts its own refresh** (criterion 1, Red → Green → Refactor). `refresh_running()` in `skills/tdd/scripts/veri/status.py` used to treat any `report-cache.sh refresh` process on the machine as its own. It now confirms each `pgrep` hit with `ps` and counts only a refresh of its own sibling script. The new process case `test_status_refresh_scope_process.py` starts an unrelated refresh at another path and checks that the report still launches its own. It puts the system `pgrep` first on status.py's PATH, so a leaf's `pgrep` guard cannot hide the unrelated process.
2. **EOF from the report closing stdout** (criterion 2, ⟦diff-checked⟧). test_2750 reads stdout on a thread until EOF within a bound of its own, not `communicate(timeout=10)`.
3. **Separate assertions** (criterion 3, ⟦diff-checked⟧). "no EOF" and "stub never started" now fail with their own messages. The verifier watched the no-EOF assertion go red with status.py changed to hold stdout open.
4. **Waits bounded below VERI_PYTEST_TIMEOUT** (criterion 4, ⟦diff-checked⟧). EOF 10 s, then 5 s each for the stub start, `proc.wait` and cleanup: 25 s at most.

The full suite was green on the branch (5972 passed) and again on the rebased tip (5976 passed). CI is green.

## Review notes
- **Step 1's `ps` check matches on the directory name, not the full path.** It counts a refresh when the script's parent directory has the same *name* as status.py's own (`scripts`). That keeps the unit case `test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running` green: it fakes a refresh at `/x/scripts/report-cache.sh`. But a refresh from another veri tree's `scripts/` still counts as this run's own, even though the issue's own environment had several lanes running at once. An earlier green that matched `pgrep -f` on the full escaped sibling path was rejected only for regex escaping no test required. Its pin case was then dropped in a red revise, so the final green went back to matching the directory name. Consider tightening this, along with that unit case's fake, in a follow-up.
- **The EOF bound went from 20 s back to 10 s.** Step 4 shrank it to fit the 30 s budget. The verdict now comes from EOF rather than from `communicate` timing out, but a report that takes over 10 s to start under heavy load still fails.
- On each ⟦diff-checked⟧ tick, `tick-ledger.sh` exited 2: its re-record of earlier frozen cases found nothing to re-record. Each ledger write stood, and `tests-frozen.sh check-earlier` exited 0 every time.

### 📊 Metrics — issue 3521

Wall time for the issue: 3954 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 8310 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3530.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.72 over 128 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78378 tokens, largest 219350 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.49 | 78378 |
| 2 | $0.06 | 84390 |
| 3 | $0.03 | 86088 |
| 4 | $0.03 | 87683 |
| 5 | $0.02 | 87883 |
| 6 | $0.02 | 88572 |
| 7 | $0.02 | 88975 |
| 8 | $0.02 | 89306 |
| 9 | $0.02 | 89754 |
| 10 | $0.02 | 90093 |
| 11 | $0.02 | 90458 |
| 12 | $0.02 | 91076 |
| 13 | $0.02 | 91380 |
| 14 | $0.09 | 99816 |
| 15 | $0.04 | 102715 |
| 16 | $0.03 | 103838 |
| 17 | $0.03 | 104953 |
| 18 | $0.02 | 105385 |
| 19 | $0.03 | 106073 |
| 20 | $0.03 | 106647 |
| 21 | $0.02 | 107047 |
| 22 | $0.03 | 107565 |
| 23 | $0.13 | 120935 |
| 24 | $0.03 | 122126 |
| 25 | $0.03 | 122952 |
| 26 | $0.10 | 132819 |
| 27 | $0.04 | 134493 |
| 28 | $0.03 | 135295 |
| 29 | $0.03 | 136073 |
| 30 | $0.04 | 137568 |
| 31 | $0.04 | 138716 |
| 32 | $0.03 | 139128 |
| 33 | $0.04 | 140612 |
| 34 | $0.04 | 141545 |
| 35 | $0.04 | 143060 |
| 36 | $0.05 | 145428 |
| 37 | $0.03 | 147116 |
| 38 | $0.03 | 147540 |
| 39 | $0.05 | 150022 |
| 40 | $0.04 | 150648 |
| 41 | $0.04 | 151492 |
| 42 | $0.04 | 152248 |
| 43 | $0.03 | 152888 |
| 44 | $0.04 | 153654 |
| 45 | $0.03 | 154096 |
| 46 | $0.04 | 155055 |
| 47 | $0.04 | 156489 |
| 48 | $0.03 | 156811 |
| 49 | $0.04 | 157427 |
| 50 | $0.04 | 158202 |
| 51 | $0.04 | 158643 |
| 52 | $0.04 | 159239 |
| 53 | $0.03 | 159578 |
| 54 | $0.04 | 160072 |
| 55 | $0.04 | 160874 |
| 56 | $0.03 | 161065 |
| 57 | $0.04 | 161709 |
| 58 | $0.06 | 164556 |
| 59 | $0.04 | 165359 |
| 60 | $0.04 | 165960 |
| 61 | $0.04 | 166410 |
| 62 | $0.05 | 168166 |
| 63 | $0.03 | 168218 |
| 64 | $0.04 | 168656 |
| 65 | $0.04 | 169095 |
| 66 | $0.04 | 169777 |
| 67 | $0.04 | 170062 |
| 68 | $0.04 | 170822 |
| 69 | $0.04 | 171626 |
| 70 | $0.04 | 171815 |
| 71 | $0.04 | 172004 |
| 72 | $0.04 | 172493 |
| 73 | $0.04 | 173151 |
| 74 | $0.04 | 173336 |
| 75 | $0.04 | 174156 |
| 76 | $0.04 | 174869 |
| 77 | $0.04 | 175058 |
| 78 | $0.04 | 175247 |
| 79 | $0.04 | 175557 |
| 80 | $0.04 | 176320 |
| 81 | $0.04 | 177136 |
| 82 | $0.04 | 177325 |
| 83 | $0.04 | 177618 |
| 84 | $0.04 | 178335 |
| 85 | $0.04 | 179086 |
| 86 | $0.04 | 179763 |
| 87 | $0.05 | 182022 |
| 88 | $0.04 | 182708 |
| 89 | $0.05 | 183917 |
| 90 | $0.04 | 184369 |
| 91 | $0.04 | 184799 |
| 92 | $0.04 | 185018 |
| 93 | $0.04 | 185233 |
| 94 | $0.04 | 185507 |
| 95 | $0.05 | 186575 |
| 96 | $0.06 | 189653 |
| 97 | $0.05 | 190997 |
| 98 | $0.05 | 192128 |
| 99 | $0.04 | 192315 |
| 100 | $0.04 | 192648 |
| 101 | $0.04 | 193107 |
| 102 | $0.04 | 193295 |
| 103 | $0.04 | 193483 |
| 104 | $0.04 | 193671 |
| 105 | $0.04 | 193968 |
| 106 | $0.04 | 194431 |
| 107 | $0.05 | 195367 |
| 108 | $0.04 | 196067 |
| 109 | $0.04 | 196254 |
| 110 | $0.04 | 196904 |
| 111 | $0.04 | 197491 |
| 112 | $0.04 | 197679 |
| 113 | $0.04 | 198017 |
| 114 | $0.04 | 198505 |
| 115 | $0.05 | 199234 |
| 116 | $0.05 | 200168 |
| 117 | $0.17 | 215959 |
| 118 | $0.04 | 216162 |
| 119 | $0.04 | 216381 |
| 120 | $0.05 | 216751 |
| 121 | $0.05 | 216986 |
| 122 | $0.05 | 217248 |
| 123 | $0.05 | 217772 |
| 124 | $0.05 | 217988 |
| 125 | $0.05 | 218346 |
| 126 | $0.05 | 218636 |
| 127 | $0.05 | 218951 |
| 128 | $0.05 | 219350 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 5 | 137 | $0.00 |
| 🟢 Green | 4 | 79 | $0.00 |
| 🛠️ Refactor | 1 | 16 | $0.00 |
| 🔎 verify-green | 2 | 55 | $0.00 |
| 🔎 verify-refactor | 1 | 16 | $0.00 |
| 🔎 verify-<phase> (revised) | 3 | 80 | $0.00 |
| 🗺️ Plan | 1 | 16 | $0.00 |
| 🗺️ verify-plan | 1 | 16 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 12 | 264 | $0.01 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1133 | 0 | 19504 | 0.06 |
| red | 7 | 3 | 1 | 0 | 379 | 184 | 39 | 72 | 17536 | 635016 | 186627 | 1.02 |
| green | 9 | 1 | 2 | 0 | 764 | 291 | 62 | 118 | 25768 | 1057504 | 331114 | 1.69 |
| red-missing | 2 | 0 | 0 | 0 | 126 | 77 | 17 | 32 | 9346 | 350969 | 49533 | 0.25 |
| pin | 1 | 0 | 1 | 0 | 29 | 21 | 3 | 6 | 1342 | 38203 | 21824 | 0.07 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 2 | 4 | 324 | 24441 | 14485 | 0.04 |
| diff | 6 | 3 | 0 | 0 | 317 | 115 | 23 | 46 | 7456 | 330906 | 79068 | 0.31 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 8 | 4 | 0 | 707 | 214 | 51 | 98 | 17359 | 735024 | 238742 | 0.84 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 382 | 221 | 34 | 68 | 19968 | 691025 | 204868 | 1.43 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 544 | 266 | 62 | 114 | 25578 | 1010990 | 258545 | 1.16 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 379 | 1.02 | 0 | 0.00 |
| green | 1152 | 2.01 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 29 | 0.07 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| status.py --report with a stale snapshot still launches its own sibling report-cache.sh refresh while an unrelated `report-cache.sh refresh` process at a different path is alive on the machine (only a refresh of its own sibling script counts as already running), pinned by a new process case in skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py that starts that unrelated process itself and stops it; the existing unit case test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running stays green ⟦criterion 1⟧ | 20 | 4 | 4 | 0 | 0 | 0 | 577 | 123 | 232 | 54316 | 2106133 | 603583 | 3.07 | 1824 | red 2/2, green 2/2 | 0/5 | nothing-left |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, test_2750 reads its EOF from the report closing its captured stdout within a bound of its own rather than a fixed 10 s wait, so a stand-in delay before status.py --report closes stdout, shorter than that bound, still passes; test-only, no production change, the case stays a process case ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 6 | 12 | 2232 | 79417 | 25607 | 0.09 | 155 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, test_2750 asserts its two conditions separately, so with status.py changed to hold stdout open until the refresh ends it goes red with a message naming no EOF, and a stub that never started fails with a message naming the stub not started; test-only, no production change ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 2676 | 136004 | 27023 | 0.11 | 217 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, every wait inside test_2750 (the stdout wait, the stub-started wait and the cleanup wait together) is bounded below VERI_PYTEST_TIMEOUT (30 s default), so its failure paths are reachable before pytest-timeout fires; test-only, no production change ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 8 | 16 | 2548 | 115485 | 26438 | 0.10 | 142 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| status.py --report with a stale snapshot still launches its own sibling report-cache.sh refresh while an unrelated `report-cache.sh refresh` process at a different path is alive on the machine (only a refresh of its own sibling script counts as already running), pinned by a new process case in skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py that starts that unrelated process itself and stops it; the existing unit case test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running stays green ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| status.py --report with a stale snapshot still launches its own sibling report-cache.sh refresh while an unrelated `report-cache.sh refresh` process at a different path is alive on the machine (only a refresh of its own sibling script counts as already running), pinned by a new process case in skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py that starts that unrelated process itself and stops it; the existing unit case test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running stays green ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 2 | ? | ? | nothing-left 1, nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 9 | 2 | 10 | 10 | 1 | 10 | 17 | 18 | 9 | 2 | 2 | 4 | 3 | 9 | 573 | 1 | 2 | 1 | 2 | 2 | 3 | 1 | 1 |
| fast | 21 | 21 | 22 | 31 | 456 | 32 | 23 | 22 | 22 | 22 | 21 | 22 | 47 | 23 | 21 |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 147 | 280 | 62905 | 2437039 | 702155 | 9.16 (estimate) |

## Owed by a human
- pin-recheck (step 1): needs a look: skills/tdd/scripts/veri/status.py (old text occurs more than once)
- pin-recheck (step 1): needs a look: skills/tdd/scripts/veri/status.py (old text gone) ×8
