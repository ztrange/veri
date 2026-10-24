### 📊 Metrics — issue 2173

Wall time for the issue: 1412 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 12 of 21 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $9.26 over 182 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88838 |
| 2 | $0.04 | 90751 |
| 3 | $0.05 | 92844 |
| 4 | $0.03 | 93166 |
| 5 | $0.03 | 93573 |
| 6 | $0.03 | 93864 |
| 7 | $0.03 | 94187 |
| 8 | $0.03 | 94801 |
| 9 | $0.03 | 95167 |
| 10 | $0.06 | 98092 |
| 11 | $0.04 | 99838 |
| 12 | $0.03 | 100409 |
| 13 | $0.04 | 101921 |
| 14 | $0.04 | 102615 |
| 15 | $0.04 | 103920 |
| 16 | $0.06 | 107360 |
| 17 | $0.03 | 107922 |
| 18 | $0.04 | 108556 |
| 19 | $0.04 | 109142 |
| 20 | $0.03 | 110199 |
| 21 | $0.05 | 111719 |
| 22 | $0.04 | 113118 |
| 23 | $0.04 | 113508 |
| 24 | $0.04 | 114391 |
| 25 | $0.03 | 114736 |
| 26 | $0.04 | 115410 |
| 27 | $0.04 | 116277 |
| 28 | $0.03 | 116829 |
| 29 | $0.04 | 117680 |
| 30 | $0.04 | 118277 |
| 31 | $0.04 | 119227 |
| 32 | $0.04 | 119928 |
| 33 | $0.04 | 120357 |
| 34 | $0.04 | 120909 |
| 35 | $0.03 | 121327 |
| 36 | $0.04 | 121797 |
| 37 | $0.04 | 122975 |
| 38 | $0.04 | 123568 |
| 39 | $0.05 | 124735 |
| 40 | $0.04 | 125397 |
| 41 | $0.04 | 126351 |
| 42 | $0.04 | 127790 |
| 43 | $0.04 | 128211 |
| 44 | $0.04 | 128611 |
| 45 | $0.05 | 130416 |
| 46 | $0.04 | 130647 |
| 47 | $0.05 | 132527 |
| 48 | $0.04 | 133164 |
| 49 | $0.04 | 133652 |
| 50 | $0.04 | 134518 |
| 51 | $0.04 | 134913 |
| 52 | $0.10 | 142385 |
| 53 | $0.04 | 143483 |
| 54 | $0.05 | 144180 |
| 55 | $0.04 | 144859 |
| 56 | $0.04 | 145573 |
| 57 | $0.05 | 146284 |
| 58 | $0.06 | 148580 |
| 59 | $0.04 | 148991 |
| 60 | $0.04 | 149860 |
| 61 | $0.05 | 150509 |
| 62 | $0.04 | 151208 |
| 63 | $0.05 | 151718 |
| 64 | $0.04 | 152284 |
| 65 | $0.04 | 152652 |
| 66 | $0.05 | 153332 |
| 67 | $0.04 | 153806 |
| 68 | $0.05 | 154422 |
| 69 | $0.05 | 155205 |
| 70 | $0.04 | 155645 |
| 71 | $0.05 | 156331 |
| 72 | $0.05 | 157469 |
| 73 | $0.05 | 158712 |
| 74 | $0.04 | 159339 |
| 75 | $0.05 | 160356 |
| 76 | $0.05 | 160817 |
| 77 | $0.04 | 161155 |
| 78 | $0.05 | 162003 |
| 79 | $0.05 | 162598 |
| 80 | $0.04 | 162964 |
| 81 | $0.05 | 163905 |
| 82 | $0.05 | 164774 |
| 83 | $0.05 | 165398 |
| 84 | $0.04 | 165992 |
| 85 | $0.05 | 166354 |
| 86 | $0.05 | 167172 |
| 87 | $0.05 | 167719 |
| 88 | $0.04 | 168183 |
| 89 | $0.05 | 169036 |
| 90 | $0.05 | 169416 |
| 91 | $0.05 | 170183 |
| 92 | $0.05 | 170797 |
| 93 | $0.05 | 171481 |
| 94 | $0.05 | 172346 |
| 95 | $0.04 | 172835 |
| 96 | $0.05 | 173542 |
| 97 | $0.05 | 174185 |
| 98 | $0.05 | 174567 |
| 99 | $0.05 | 175691 |
| 100 | $0.05 | 176568 |
| 101 | $0.05 | 177220 |
| 102 | $0.05 | 177811 |
| 103 | $0.06 | 178932 |
| 104 | $0.05 | 179902 |
| 105 | $0.05 | 180409 |
| 106 | $0.05 | 181557 |
| 107 | $0.05 | 182009 |
| 108 | $0.05 | 182258 |
| 109 | $0.05 | 182869 |
| 110 | $0.06 | 184118 |
| 111 | $0.05 | 185239 |
| 112 | $0.05 | 185686 |
| 113 | $0.05 | 186244 |
| 114 | $0.06 | 187117 |
| 115 | $0.05 | 187468 |
| 116 | $0.05 | 188011 |
| 117 | $0.05 | 188695 |
| 118 | $0.05 | 189417 |
| 119 | $0.05 | 189713 |
| 120 | $0.06 | 190623 |
| 121 | $0.05 | 191608 |
| 122 | $0.05 | 191858 |
| 123 | $0.06 | 192362 |
| 124 | $0.05 | 192921 |
| 125 | $0.05 | 193600 |
| 126 | $0.05 | 193987 |
| 127 | $0.05 | 194524 |
| 128 | $0.06 | 195312 |
| 129 | $0.05 | 195787 |
| 130 | $0.05 | 196276 |
| 131 | $0.06 | 197327 |
| 132 | $0.05 | 197884 |
| 133 | $0.06 | 198557 |
| 134 | $0.05 | 199259 |
| 135 | $0.06 | 200061 |
| 136 | $0.06 | 201223 |
| 137 | $0.05 | 201696 |
| 138 | $0.06 | 202293 |
| 139 | $0.05 | 202850 |
| 140 | $0.05 | 203347 |
| 141 | $0.06 | 203922 |
| 142 | $0.05 | 204432 |
| 143 | $0.06 | 204849 |
| 144 | $0.06 | 205988 |
| 145 | $0.05 | 207037 |
| 146 | $0.06 | 207496 |
| 147 | $0.57 | 89063 |
| 148 | $0.04 | 91536 |
| 149 | $0.02 | 92290 |
| 150 | $0.03 | 93391 |
| 151 | $0.06 | 98576 |
| 152 | $0.02 | 98892 |
| 153 | $0.02 | 99303 |
| 154 | $0.02 | 99588 |
| 155 | $0.02 | 99867 |
| 156 | $0.02 | 100483 |
| 157 | $0.03 | 101382 |
| 158 | $0.04 | 103654 |
| 159 | $0.04 | 106422 |
| 160 | $0.03 | 107729 |
| 161 | $0.03 | 108896 |
| 162 | $0.02 | 109294 |
| 163 | $0.03 | 110801 |
| 164 | $0.07 | 116908 |
| 165 | $0.03 | 117388 |
| 166 | $0.03 | 117833 |
| 167 | $0.03 | 118607 |
| 168 | $0.03 | 119455 |
| 169 | $0.11 | 129998 |
| 170 | $0.03 | 130670 |
| 171 | $0.03 | 131131 |
| 172 | $0.04 | 132471 |
| 173 | $0.09 | 140936 |
| 174 | $0.04 | 142007 |
| 175 | $0.04 | 142854 |
| 176 | $0.03 | 143600 |
| 177 | $0.04 | 145129 |
| 178 | $0.03 | 145584 |
| 179 | $0.03 | 146195 |
| 180 | $0.03 | 146906 |
| 181 | $0.03 | 147526 |
| 182 | $0.06 | 151542 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 10 | 1 | 2 | 1212 | 0 | 32084 | 0.09 |
| red | 18 | 8 | 0 | 0 | 683 | 298 | 90 | 174 | 32816 | 2528906 | 370676 | 1.51 |
| green | 22 | 8 | 2 | 0 | 2138 | 281 | 98 | 190 | 28234 | 2681446 | 332706 | 1.58 |
| refactor | 16 | 8 | 0 | 0 | 415 | 109 | 47 | 90 | 9006 | 1131352 | 238123 | 0.80 |
| red-missing | 1 | 0 | 0 | 0 | 47 | 14 | 3 | 6 | 1651 | 82704 | 17081 | 0.07 |
| pin | 3 | 3 | 0 | 0 | 98 | 39 | 11 | 22 | 3886 | 291080 | 44277 | 0.18 |
| prose | 6 | 0 | 0 | 0 | 80 | 50 | 6 | 12 | 7623 | 7570 | 54055 | 0.21 |
| skill-edit | 2 | 0 | 0 | 0 | 23 | 14 | 5 | 10 | 1178 | 117268 | 19716 | 0.07 |
| cover | 1 | 0 | 0 | 0 | 32 | 9 | 4 | 8 | 972 | 90656 | 31352 | 0.10 |
| predicate | 2 | 0 | 0 | 1 | 16 | 11 | 4 | 8 | 718 | 105820 | 12630 | 0.05 |
| structural | 1 | 0 | 0 | 0 | 30 | 15 | 4 | 8 | 1603 | 108684 | 14030 | 0.06 |
| transform | 1 | 1 | 0 | 0 | 28 | 11 | 4 | 8 | 1003 | 90299 | 31439 | 0.10 |
| diff | 3 | 0 | 0 | 0 | 169 | 40 | 10 | 20 | 2932 | 241625 | 64051 | 0.33 |
| exhausted | 1 | 0 | 0 | 0 | 978 | 28 | 3 | 6 | 1435 | 46825 | 42532 | 0.25 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 32 | 29 | 2 | 0 | 1929 | 328 | 106 | 208 | 31452 | 2693998 | 474283 | 1.77 |
| developer | claude-sonnet-5-5 | 32 | 0 | 0 | 1 | 1419 | 443 | 153 | 294 | 47610 | 4245199 | 603846 | 2.51 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 1300 | 94 | 20 | 40 | 6406 | 460200 | 152852 | 0.84 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 548 | 0.75 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 169 | 0.33 |
| exhausted | 0 | 0.00 | 978 | 0.25 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `skills/tdd/scripts/merge-lock.sh` exists as a `/bin/sh` shim over `skills/tdd/scripts/veri/merge_lock.py` (the port convention, `status.sh` its example): with no argument, or a verb other than `take`, `release` or `holder`, it prints a usage line naming the three verbs on stderr and exits 2; `skills/tdd/SCRIPTS.md` carries its entry as an operator script the conductor does not call (veri-merge's and veri-handoff's), so `unreachable.sh` does not list it as unreached ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 63 | 25 | 48 | 6926 | 657246 | 111203 | 0.41 | 397 | unknown | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh holder` exits 3 and prints nothing on stdout when no `.tdd/merge.lock` exists in the main working tree of the repository it is run in, also when run from a linked worktree of it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 70 | 28 | 54 | 7299 | 765886 | 90890 | 0.38 | 343 | unknown | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh take` creates `.tdd/merge.lock` in the repository's main working tree (also when run from a linked worktree) atomically, as a directory, recording inside it the holder's pid (the caller's: the parent process of `merge-lock.sh`, or the pid `--pid <pid>` names), the host and the start time, and exits 0; `merge-lock.sh holder` then prints that pid, host and start time and exits 0 while that pid is live ⟦criterion 1⟧ | 11 | 4 | 1 | 0 | 0 | 0 | 122 | 39 | 76 | 12935 | 1026954 | 173257 | 0.76 | 654 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| `merge-lock.sh holder` exits 1 when the lock's recorded pid is dead on this host, printing the record marked as a stale lock ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 89 | 28 | 54 | 7863 | 715935 | 122934 | 0.56 | 538 | 1/2 | 0/5 | structural-owed |  |  | full |
| `merge-lock.sh holder` exits 2 when `.tdd/merge.lock` exists but its record is missing, unreadable or malformed ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 11 | 22 | 3845 | 324273 | 33162 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `merge-lock.sh release` removes `.tdd/merge.lock` and exits 0 only when the caller (identified as `take` identifies it) is the recorded holder; a caller who is not the holder gets exit 1 with the lock left in place, and `release --force` removes the lock whoever holds it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 82 | 27 | 52 | 7874 | 738856 | 95763 | 0.39 | 409 | unknown | 1/5 | nothing-left |  |  | full |
| `merge-lock.sh take` waits while another live holder has the lock, polling at an interval read as `${VERI_MERGE_LOCK_POLL:-30}` seconds, and takes it once it is released: two takers racing for a free lock end with exactly one holding it while the other is still waiting, and the waiter takes it after the winner's release (a medium case with real processes, `@pytest.mark.process`) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 86 | 24 | 46 | 8742 | 644609 | 94720 | 0.39 | 379 | unknown | 0/5 | nothing-left |  |  | full |
| A stale lock (recorded pid dead on this host) is never removed silently: `merge-lock.sh take` on it reports the stale holder on stderr and keeps waiting with the lock left in place, and only `merge-lock.sh release --force` clears it, after which a waiting `take` gets it ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 25 | 50 | 7613 | 704485 | 93654 | 0.38 | 439 | unknown | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh release` and `merge-lock.sh take` exit 2 when `.tdd/merge.lock` exists but its record is missing, unreadable or malformed, as `holder` does, leaving the lock in place ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 12 | 24 | 4567 | 367254 | 36745 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/veri-merge/REQUIREMENTS.md`'s M4 is replaced by the issue's M4 row exactly as the issue states it, `skills/veri-merge/SKILL.md` states it in its prose (taking the lock with `$S/merge-lock.sh take` before its first write, releasing it with `$S/merge-lock.sh release` on every exit path, and leaving it held and saying so on a conflict or a refused push), the unit grades PASS against its whole list and `GRADED` carries a line whose signature matches its current text ⟦skill-edit⟧ ⟦criterion 3⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 26 | 5 | 10 | 3851 | 75152 | 29581 | 0.12 | 70 | unknown | unknown | unknown |  |  | full |
| `skills/veri-handoff/REQUIREMENTS.md`'s H2 is replaced by the issue's H2 row exactly as the issue states it, `skills/veri-handoff/SKILL.md` states it in its prose (for the dev role, refusing while `$S/merge-lock.sh holder` names a live holder, or a launch is half done), the unit grades PASS against its whole list and `GRADED` carries a line whose signature matches its current text ⟦skill-edit⟧ ⟦criterion 3⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 23 | 4 | 8 | 2723 | 47469 | 25555 | 0.10 | 60 | unknown | unknown | unknown |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_tunable_reads.py — FAILED test_no_module_but_the_reader_and_the_exempt_ones_reads_a_veri_name_from_the_environment (and test_run_leaf_run_verdict_and_stop_run_take_their_veri_values_from_the_one_reader_and_no_module_is_exempt): AssertionError: assert [`.../skills/tdd/scripts/veri/merge_lock.py:43`] == [] (merge_lock.py reads a VERI_ name from the environment outside the one reader); skills/tdd/scripts/tests/py/test_github_sh.py — FAILED test_the_gh_function_reads_a_fast_wait_of_015_as_15_decimal_seconds_sleeping_the_retry_interval_until_then_issue_2132 - AssertionError: gh: not found on PATH, retrying in 2s ⟦suite-repair⟧ ⟦criterion 3⟧ | 12 | 4 | 0 | 1 | 0 | 0 | 126 | 46 | 88 | 12225 | 1165449 | 239986 | 0.84 | 3061 | unknown | 0/5 | nothing-left |  |  | full |
| the case `test_take_without_pid_records_the_parent_process_of_the_caller_and_holder_prints_it` is deleted from `skills/tdd/scripts/tests/py/test_merge_lock.py`, since it pins `take` without `--pid` recording the caller parent process, the behaviour criterion 4 removes; no other test and no production file changes ⟦diff-checked⟧ ⟦criterion 4⟧ | 4 | 0 | 0 | 0 | 0 | 0 | 68 | 13 | 26 | 4367 | 288450 | 106583 | 0.58 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `skills/tdd/scripts/merge-lock.sh` exists as a `/bin/sh` shim over `skills/tdd/scripts/veri/merge_lock.py` (the port convention, `status.sh` its example): with no argument, or a verb other than `take`, `release` or `holder`, it prints a usage line naming the three verbs on stderr and exits 2; `skills/tdd/SCRIPTS.md` carries its entry as an operator script the conductor does not call (veri-merge's and veri-handoff's), so `unreachable.sh` does not list it as unreached ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 44 | 0.09 |
| `merge-lock.sh holder` exits 3 and prints nothing on stdout when no `.tdd/merge.lock` exists in the main working tree of the repository it is run in, also when run from a linked worktree of it ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 46 | 0.09 |
| `merge-lock.sh take` creates `.tdd/merge.lock` in the repository's main working tree (also when run from a linked worktree) atomically, as a directory, recording inside it the holder's pid (the caller's: the parent process of `merge-lock.sh`, or the pid `--pid <pid>` names), the host and the start time, and exits 0; `merge-lock.sh holder` then prints that pid, host and start time and exits 0 while that pid is live ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 47 | 0.09 |
| `merge-lock.sh holder` exits 1 when the lock's recorded pid is dead on this host, printing the record marked as a stale lock ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 65 | 0.10 |
| `merge-lock.sh release` removes `.tdd/merge.lock` and exits 0 only when the caller (identified as `take` identifies it) is the recorded holder; a caller who is not the holder gets exit 1 with the lock left in place, and `release --force` removes the lock whoever holds it ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 70 | 0.11 |
| `merge-lock.sh take` waits while another live holder has the lock, polling at an interval read as `${VERI_MERGE_LOCK_POLL:-30}` seconds, and takes it once it is released: two takers racing for a free lock end with exactly one holding it while the other is still waiting, and the waiter takes it after the winner's release (a medium case with real processes, `@pytest.mark.process`) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.09 |
| A stale lock (recorded pid dead on this host) is never removed silently: `merge-lock.sh take` on it reports the stale holder on stderr and keeps waiting with the lock left in place, and only `merge-lock.sh release --force` clears it, after which a waiting `take` gets it ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 48 | 0.10 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_tunable_reads.py — FAILED test_no_module_but_the_reader_and_the_exempt_ones_reads_a_veri_name_from_the_environment (and test_run_leaf_run_verdict_and_stop_run_take_their_veri_values_from_the_one_reader_and_no_module_is_exempt): AssertionError: assert [`.../skills/tdd/scripts/veri/merge_lock.py:43`] == [] (merge_lock.py reads a VERI_ name from the environment outside the one reader); skills/tdd/scripts/tests/py/test_github_sh.py — FAILED test_the_gh_function_reads_a_fast_wait_of_015_as_15_decimal_seconds_sleeping_the_retry_interval_until_then_issue_2132 - AssertionError: gh: not found on PATH, retrying in 2s ⟦suite-repair⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.13 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 10 | 11 | 27 | 10 | 12 | 9 | 11 | 9 | 11 | 11 | 10 | 11 | 12 | 12 | 13 | 12 | 3 | 12 | 3 | 7 | 16 | 26 | 13 | 13 | 13 | 15 | 9 | 10 | 11 | 4 | 10 | 10 | 10 | 10 | 10 | 11 | 12 | 12 | 11 | 11 | 0 | 13 | 11 | 23 | 23 | 18 | 9 | 8 | 11 | 11 | 10 | 0 | 13 | 18 | 12 | 10 | 20 | 10 | 13 | 4 | 3 | 3 |
| fast | 16 | 17 | 18 | 16 | 18 | 16 | 18 | 20 | 31 | 19 | 20 | 39 | 27 | 20 | 17 | 22 | 21 | 19 | 18 | 17 | 16 | 16 | 18 | 37 | 60 | 17 | 104 | 25 | 15 | 13 | 50 | 15 | 35 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 10 | 10 | 13 | 12 | 14 | 12 | 4 | 12 | 3 | 3 | 10 | 12 | 12 | 4 | 4 | 3 | 10 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 290 | 564 | 94269 | 7524235 | 1304752 | 5.40 |
