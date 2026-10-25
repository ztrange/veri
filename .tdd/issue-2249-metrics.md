### 📊 Metrics — issue 2249

Wall time for the issue: 206 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 12 planned.
Outcome: the run bailed — step-added-off-route, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $13.37 over 267 turns, in 4 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89947 tokens, largest 188642 tokens
Conductor context: first turn 90195 tokens, largest 182201 tokens
Conductor context: first turn 90403 tokens, largest 165327 tokens
Conductor context: first turn 90404 tokens, largest 130187 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 89947 |
| 2 | $0.03 | 90366 |
| 3 | $0.04 | 92040 |
| 4 | $0.05 | 94012 |
| 5 | $0.03 | 94391 |
| 6 | $0.03 | 94780 |
| 7 | $0.03 | 95208 |
| 8 | $0.03 | 95532 |
| 9 | $0.03 | 95850 |
| 10 | $0.04 | 96497 |
| 11 | $0.03 | 96868 |
| 12 | $0.05 | 100202 |
| 13 | $0.05 | 102504 |
| 14 | $0.05 | 104791 |
| 15 | $0.04 | 106138 |
| 16 | $0.04 | 106587 |
| 17 | $0.03 | 107396 |
| 18 | $0.06 | 110011 |
| 19 | $0.04 | 110901 |
| 20 | $0.04 | 112411 |
| 21 | $0.06 | 115838 |
| 22 | $0.07 | 120041 |
| 23 | $0.05 | 122713 |
| 24 | $0.04 | 123224 |
| 25 | $0.04 | 123753 |
| 26 | $0.04 | 124408 |
| 27 | $0.04 | 125715 |
| 28 | $0.04 | 126223 |
| 29 | $0.04 | 127027 |
| 30 | $0.05 | 128420 |
| 31 | $0.04 | 129475 |
| 32 | $0.05 | 130460 |
| 33 | $0.04 | 131959 |
| 34 | $0.05 | 132818 |
| 35 | $0.04 | 133217 |
| 36 | $0.09 | 140628 |
| 37 | $0.04 | 141431 |
| 38 | $0.05 | 142692 |
| 39 | $0.05 | 143466 |
| 40 | $0.04 | 144004 |
| 41 | $0.05 | 145179 |
| 42 | $0.04 | 146003 |
| 43 | $0.06 | 147670 |
| 44 | $0.04 | 148230 |
| 45 | $0.04 | 148964 |
| 46 | $0.05 | 150365 |
| 47 | $0.05 | 151047 |
| 48 | $0.05 | 151758 |
| 49 | $0.04 | 152217 |
| 50 | $0.05 | 153308 |
| 51 | $0.04 | 153914 |
| 52 | $0.05 | 154355 |
| 53 | $0.06 | 156690 |
| 54 | $0.05 | 158184 |
| 55 | $0.04 | 158456 |
| 56 | $0.05 | 159258 |
| 57 | $0.04 | 159673 |
| 58 | $0.05 | 160292 |
| 59 | $0.05 | 160669 |
| 60 | $0.04 | 161175 |
| 61 | $0.05 | 161564 |
| 62 | $0.05 | 162367 |
| 63 | $0.05 | 164196 |
| 64 | $0.06 | 165548 |
| 65 | $0.05 | 166617 |
| 66 | $0.04 | 167258 |
| 67 | $0.06 | 168848 |
| 68 | $0.05 | 169711 |
| 69 | $0.06 | 171266 |
| 70 | $0.06 | 173481 |
| 71 | $0.05 | 173944 |
| 72 | $0.05 | 174455 |
| 73 | $0.04 | 174627 |
| 74 | $0.05 | 174829 |
| 75 | $0.04 | 175033 |
| 76 | $0.06 | 176142 |
| 77 | $0.05 | 176683 |
| 78 | $0.05 | 177500 |
| 79 | $0.05 | 178736 |
| 80 | $0.05 | 179515 |
| 81 | $0.06 | 180299 |
| 82 | $0.04 | 180645 |
| 83 | $0.05 | 181157 |
| 84 | $0.05 | 181528 |
| 85 | $0.06 | 182709 |
| 86 | $0.08 | 186834 |
| 87 | $0.05 | 187377 |
| 88 | $0.05 | 188292 |
| 89 | $0.05 | 188642 |
| 90 | $0.59 | 90195 |
| 91 | $0.04 | 90840 |
| 92 | $0.04 | 92778 |
| 93 | $0.06 | 96241 |
| 94 | $0.04 | 96687 |
| 95 | $0.03 | 97133 |
| 96 | $0.04 | 97643 |
| 97 | $0.03 | 98113 |
| 98 | $0.04 | 98778 |
| 99 | $0.06 | 101979 |
| 100 | $0.04 | 103022 |
| 101 | $0.04 | 103879 |
| 102 | $0.04 | 104589 |
| 103 | $0.03 | 104795 |
| 104 | $0.04 | 106147 |
| 105 | $0.04 | 106960 |
| 106 | $0.04 | 107384 |
| 107 | $0.04 | 108376 |
| 108 | $0.04 | 109279 |
| 109 | $0.04 | 110108 |
| 110 | $0.04 | 110867 |
| 111 | $0.04 | 111203 |
| 112 | $0.04 | 112057 |
| 113 | $0.04 | 112698 |
| 114 | $0.04 | 113013 |
| 115 | $0.04 | 114019 |
| 116 | $0.04 | 114841 |
| 117 | $0.04 | 115715 |
| 118 | $0.05 | 116743 |
| 119 | $0.05 | 118596 |
| 120 | $0.04 | 119842 |
| 121 | $0.05 | 121195 |
| 122 | $0.05 | 122248 |
| 123 | $0.04 | 123413 |
| 124 | $0.04 | 123881 |
| 125 | $0.05 | 124850 |
| 126 | $0.04 | 125760 |
| 127 | $0.04 | 126613 |
| 128 | $0.07 | 130310 |
| 129 | $0.05 | 132245 |
| 130 | $0.05 | 133361 |
| 131 | $0.05 | 135008 |
| 132 | $0.05 | 135669 |
| 133 | $0.05 | 136903 |
| 134 | $0.05 | 138079 |
| 135 | $0.07 | 142308 |
| 136 | $0.05 | 143915 |
| 137 | $0.05 | 144880 |
| 138 | $0.05 | 145949 |
| 139 | $0.05 | 147034 |
| 140 | $0.05 | 147908 |
| 141 | $0.04 | 148335 |
| 142 | $0.05 | 149305 |
| 143 | $0.05 | 149828 |
| 144 | $0.04 | 150269 |
| 145 | $0.05 | 151194 |
| 146 | $0.05 | 152174 |
| 147 | $0.05 | 152963 |
| 148 | $0.05 | 153888 |
| 149 | $0.05 | 154704 |
| 150 | $0.05 | 155540 |
| 151 | $0.05 | 156398 |
| 152 | $0.05 | 157491 |
| 153 | $0.05 | 158256 |
| 154 | $0.05 | 158662 |
| 155 | $0.06 | 160534 |
| 156 | $0.05 | 161679 |
| 157 | $0.05 | 162156 |
| 158 | $0.05 | 163066 |
| 159 | $0.06 | 164148 |
| 160 | $0.05 | 165162 |
| 161 | $0.06 | 167208 |
| 162 | $0.06 | 168509 |
| 163 | $0.05 | 169312 |
| 164 | $0.05 | 170376 |
| 165 | $0.05 | 170844 |
| 166 | $0.06 | 172132 |
| 167 | $0.06 | 173524 |
| 168 | $0.05 | 173941 |
| 169 | $0.05 | 175165 |
| 170 | $0.06 | 176303 |
| 171 | $0.08 | 180326 |
| 172 | $0.05 | 181239 |
| 173 | $0.06 | 182201 |
| 174 | $0.59 | 90403 |
| 175 | $0.05 | 92420 |
| 176 | $0.04 | 93495 |
| 177 | $0.06 | 97751 |
| 178 | $0.05 | 100390 |
| 179 | $0.07 | 104168 |
| 180 | $0.03 | 104792 |
| 181 | $0.04 | 105265 |
| 182 | $0.03 | 105549 |
| 183 | $0.04 | 105874 |
| 184 | $0.04 | 106748 |
| 185 | $0.04 | 107915 |
| 186 | $0.05 | 109821 |
| 187 | $0.05 | 112107 |
| 188 | $0.04 | 112960 |
| 189 | $0.04 | 113834 |
| 190 | $0.04 | 114592 |
| 191 | $0.04 | 114872 |
| 192 | $0.14 | 129193 |
| 193 | $0.05 | 129975 |
| 194 | $0.04 | 130407 |
| 195 | $0.04 | 131302 |
| 196 | $0.04 | 131756 |
| 197 | $0.05 | 132600 |
| 198 | $0.04 | 133387 |
| 199 | $0.04 | 133681 |
| 200 | $0.05 | 134431 |
| 201 | $0.04 | 134999 |
| 202 | $0.04 | 135881 |
| 203 | $0.05 | 136621 |
| 204 | $0.04 | 137300 |
| 205 | $0.05 | 138400 |
| 206 | $0.06 | 141142 |
| 207 | $0.10 | 149037 |
| 208 | $0.06 | 151378 |
| 209 | $0.06 | 153032 |
| 210 | $0.05 | 154166 |
| 211 | $0.06 | 156251 |
| 212 | $0.05 | 157104 |
| 213 | $0.05 | 158758 |
| 214 | $0.08 | 162736 |
| 215 | $0.05 | 163712 |
| 216 | $0.06 | 165327 |
| 217 | $0.58 | 90404 |
| 218 | $0.03 | 92513 |
| 219 | $0.02 | 93208 |
| 220 | $0.06 | 98234 |
| 221 | $0.06 | 103592 |
| 222 | $0.04 | 106543 |
| 223 | $0.03 | 107154 |
| 224 | $0.02 | 107579 |
| 225 | $0.02 | 107917 |
| 226 | $0.03 | 108404 |
| 227 | $0.03 | 108889 |
| 228 | $0.03 | 109538 |
| 229 | $0.03 | 110319 |
| 230 | $0.03 | 111108 |
| 231 | $0.03 | 111878 |
| 232 | $0.02 | 112111 |
| 233 | $0.09 | 121106 |
| 234 | $0.03 | 121793 |
| 235 | $0.03 | 122705 |
| 236 | $0.05 | 125803 |
| 237 | $0.06 | 130187 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 32 | 26 | 2 | 4 | 3226 | 17160 | 48856 | 0.16 |
| red | 24 | 13 | 1 | 0 | 848 | 468 | 110 | 220 | 51211 | 3641221 | 600446 | 2.66 |
| green | 29 | 3 | 7 | 0 | 4420 | 907 | 205 | 396 | 87288 | 6808163 | 748380 | 4.98 |
| refactor | 3 | 0 | 0 | 0 | 25 | 18 | 7 | 14 | 1364 | 161063 | 66016 | 0.19 |
| exhausted | 3 | 0 | 0 | 0 | 100 | 63 | 9 | 18 | 4852 | 236630 | 47532 | 0.38 |
| diff | 8 | 4 | 0 | 0 | 597 | 163 | 46 | 92 | 20247 | 1403202 | 274009 | 1.03 |
| red-supersede | 3 | 0 | 0 | 1 | 118 | 85 | 18 | 36 | 9286 | 680081 | 58477 | 0.31 |
| pin | 1 | 0 | 1 | 0 | 27 | 17 | 7 | 14 | 1822 | 217195 | 19438 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 31 | 21 | 10 | 0 | 1443 | 381 | 113 | 226 | 40680 | 3063865 | 567818 | 2.13 |
| developer | claude-sonnet-5-5 | 15 | 0 | 0 | 1 | 792 | 357 | 88 | 176 | 42951 | 2963257 | 422271 | 1.78 |
| developer | claude-opus-5-5 | 27 | 0 | 0 | 0 | 3932 | 1009 | 203 | 392 | 95665 | 7137593 | 873065 | 5.88 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 442 | 1.67 | 99 | 0.37 |
| green | 6608 | 4.37 | 549 | 1.65 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 71 | 0.24 |
| diff | 0 | 0.00 | 116 | 0.24 |
| red-supersede | 0 | 0.00 | 54 | 0.16 |
| pin | 27 | 0.09 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `issue-worktree.sh <n> <slug>` still cuts a fresh worktree when `.tdd/wt/<n>` holds only the run state `run_conductor.py` seeds before the cut (`.tdd/events.jsonl` and `.tdd/conductor.pid`, either or both): exit 0, the worktree is cut, and both files are kept in its `.tdd/` with their contents unchanged; pinned in `skills/tdd/scripts/tests/py/test_issue_worktree.py` (a medium case, real git) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 106 | 33 | 66 | 11008 | 984618 | 148077 | 0.70 | 517 | 1/2 | 0/5 | nothing-left |  |  | full |
| `issue-worktree.sh <n> <slug>` hands back an existing worktree (exit 0, its path printed) when the live pid in its `.tdd/conductor.pid` is an ancestor of the calling process — the run's own conductor entering its own worktree in preflight — and still refuses it (exit 2, naming the pid) when that live holder is a conductor-shaped process (a `claude` whose parent is `run_conductor.py`) that is not the caller's ancestor; pinned in `skills/tdd/scripts/tests/py/test_issue_worktree.py` ⟦criterion 1⟧ | 10 | 3 | 1 | 0 | 0 | 0 | 234 | 53 | 106 | 25625 | 1692942 | 206696 | 1.08 | 750 | 1/2 | 0/5 | nothing-left |  |  | full |
| `run_conductor.py` records the pid of the `claude -p` process it starts in the run's worktree `.tdd/conductor.pid` (`.tdd/wt/<n>/.tdd/conductor.pid` under the main working tree) before that process runs preflight: with a stubbed `CLAUDE_BIN` that reads the file at its start and reports its own pid, the recorded pid is the stub's and was already on disk when the stub started; pinned in `skills/tdd/scripts/tests/py/test_run_conductor_process.py` (a medium case, a real stub process) ⟦criterion 1⟧ | 28 | 8 | 4 | 1 | 1 | 0 | 816 | 172 | 338 | 81029 | 6026546 | 795848 | 4.43 | 1154 | red 2/2, green 3/2 | 0/5 | structural-owed |  |  | full |
| skills/tdd/scripts/tests/py/test_run_conductor.py: the older cases that block the pid write are rewritten so each keeps pinning what it pins today without forbidding it: `test_main_launches_exactly_one_claude_with_the_fixed_print_mode_argv…` (all 3 parametrizations) still pins the exact `claude -p` argv and that exactly one `claude` is launched, but no longer pins `preexec_fn: None` or the launch's stdin wiring; the `…registered_as_a_worktree…_866` case stands up the run's worktree through `issue-worktree.sh` (or seeds `.tdd/conductor.pid` only after its `git worktree add`) instead of a plain `git worktree add` into a directory the conductor has already seeded; test file only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 8 | 16 | 3646 | 192741 | 69460 | 0.23 | 264 | n/a | n/a | n/a |  |  | full |
| The existing cases that stand a plain live process (the test's own pid, a bare `sleep`) in a run's `.tdd/conductor.pid` as its live holder — in `skills/tdd/scripts/tests/py/test_issue_worktree.py`, `skills/tdd/scripts/tests/py/test_stop_run.py`, `skills/tdd/scripts/tests/py/unit/test_stop_run_cli.py`, `skills/tdd/scripts/tests/py/unit/test_pid_file.py` and any other suite reaching `pid_file.live_conductor` — are moved to a conductor-shaped holder (a process run as `claude` whose parent is `run_conductor.py`), each still asserting what it asserted and staying green against the current code; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 14 | 28 | 7558 | 509164 | 56711 | 0.27 | 246 | n/a | n/a | n/a |  |  | full |
| `pid_file.live_conductor(<run-dir>)` returns the recorded pid only when `kill -0` succeeds on it and that process is a conductor — a `claude` process whose parent is `run_conductor.py` — and returns None when the recorded pid now belongs to a live unrelated process, so a dead run whose pid was reused reads ended; no issue number is read or required ⟦criterion 2⟧ | 18 | 3 | 3 | 0 | 0 | 0 | 402 | 98 | 188 | 38161 | 3040247 | 389668 | 2.41 | unknown | 4/2 | unknown | unknown |  |  | full |
| The five in-process cases in `skills/tdd/scripts/tests/py/test_stop_run.py` that stand a bare live pid (4242) in a run's `.tdd/conductor.pid` with `os.kill` faked to succeed and no `ps` answer for it (`test_main_accepts_a_mode_stop_modes_lists_and_writes_it_to_the_runs_stop_file`, `test_main_prints_each_stopped_run_exactly_answers_3_byte_for_byte_and_lists_all_runs_sorted_skipping_files_and_dot_names`, `test_main_now_terms_only_pids_whose_ps_runs_supervise_sh_of_their_name_ignoring_kill_errors_and_other_modes_signal_nothing`, `test_main_answers_as_stop_run_test_sh_s_refusal_write_overwrite_all_no_main_tree_and_pid_0_cases_do`, `test_main_refuses_no_issue_and_a_non_integer_and_stops_a_live_run_or_answers_3_for_a_dead_one`) are moved to a conductor-shaped holder, their fakes answering `ps` for the recorded pid with a `claude` whose parent is `run_conductor.py`, as 5ed2126aca did for the file's other cases; the step also carries step 6's earlier red-supersede edits to `skills/tdd/scripts/tests/py/unit/test_pid_file.py` and `skills/tdd/scripts/tests/py/unit/test_stop_run_cli.py` (preserved by preserve-attempt.sh); each case still asserts what it asserted and stays green against the current code; no production change ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 14 | 28 | 5530 | 429044 | 76336 | 0.29 | 263 | n/a | n/a | n/a |  |  | full |
| The four unit cases that stand a bare live pid in a run's `.tdd/conductor.pid` with no conductor-shaped `ps` answer for it are moved to a conductor-shaped holder: the `world` fixture in `skills/tdd/scripts/tests/py/unit/test_stop_run_cli.py` answers `ps -o command=` with a `claude` and `ps -o ppid=` with a `run_conductor.py` parent for the recorded pid (covering `test_stop_run_cli_mode_now_writes_now_as_the_only_line_of_the_stop_file_names_the_run_on_stdout_and_exits_0`, `test_stop_run_cli_mode_at_ledger_and_at_leaf_write_the_mode_and_signal_nothing` and `test_stop_run_cli_never_signals_the_pid_in_the_conductor_pid_file`), and `skills/tdd/scripts/tests/py/unit/test_pid_file.py::test_live_conductor_answers_the_digits_as_read_and_never_signals_for_no_pid_file_or_0_or_00` gives pid 4242 the same answers; each case still asserts what it asserted and stays green against the current code; test files only, no production change ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 10 | 20 | 3513 | 272253 | 71502 | 0.24 | unknown | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `issue-worktree.sh <n> <slug>` still cuts a fresh worktree when `.tdd/wt/<n>` holds only the run state `run_conductor.py` seeds before the cut (`.tdd/events.jsonl` and `.tdd/conductor.pid`, either or both): exit 0, the worktree is cut, and both files are kept in its `.tdd/` with their contents unchanged; pinned in `skills/tdd/scripts/tests/py/test_issue_worktree.py` (a medium case, real git) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| `issue-worktree.sh <n> <slug>` hands back an existing worktree (exit 0, its path printed) when the live pid in its `.tdd/conductor.pid` is an ancestor of the calling process — the run's own conductor entering its own worktree in preflight — and still refuses it (exit 2, naming the pid) when that live holder is a conductor-shaped process (a `claude` whose parent is `run_conductor.py`) that is not the caller's ancestor; pinned in `skills/tdd/scripts/tests/py/test_issue_worktree.py` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.06 |
| `run_conductor.py` records the pid of the `claude -p` process it starts in the run's worktree `.tdd/conductor.pid` (`.tdd/wt/<n>/.tdd/conductor.pid` under the main working tree) before that process runs preflight: with a stubbed `CLAUDE_BIN` that reads the file at its start and reports its own pid, the recorded pid is the stub's and was already on disk when the stub started; pinned in `skills/tdd/scripts/tests/py/test_run_conductor_process.py` (a medium case, a real stub process) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 7 | 0.09 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 23 | 19 | 5 | 23 | 12 | 5 | 7 | 5 | 27 | 31 | 26 | 13 | 15 | 7 | 18 | 8 | 4 | 3 | 6 | 6 | 18 | 21 | 19 | 18 | 5 | 6 | 19 | 19 | 18 | 20 | 44 | 37 | 3 | 3 | 17 | 18 | 17 | 16 | 3 | 3 | 69 | 67 | 50 | 32 | 17 | 4 | 3 | 4 | 3 | 4 | 4 | 22 | 3 | 9 | 3 | 4 | 2 |
| fast | 22 | 24 | 22 | 23 | 23 | 26 | 42 | 26 | 23 | 23 | 23 | 22 | 23 | 24 | 26 | 22 | 25 | 46 | 23 | 24 | 23 | 23 | 23 | 22 | 22 | 31 | 23 | 22 | 22 | 48 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 1 | 4 | 4 | 5 | 0 | 6 | 4 | 1 | 4 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 404 | 794 | 179296 | 13164715 | 1863154 | 9.80 |
