### 📊 Metrics — issue 3500

Wall time for the issue: 4311 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 8 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $11.21 over 226 turns, in 4 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78412 tokens, largest 145045 tokens
Conductor context: first turn 78411 tokens, largest 149404 tokens
Conductor context: first turn 78413 tokens, largest 153046 tokens
Conductor context: first turn 78412 tokens, largest 176169 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 78412 |
| 2 | $0.08 | 84424 |
| 3 | $0.04 | 85892 |
| 4 | $0.05 | 87805 |
| 5 | $0.04 | 88280 |
| 6 | $0.03 | 88675 |
| 7 | $0.04 | 88997 |
| 8 | $0.03 | 89331 |
| 9 | $0.04 | 89620 |
| 10 | $0.04 | 90030 |
| 11 | $0.03 | 90584 |
| 12 | $0.04 | 91442 |
| 13 | $0.04 | 92153 |
| 14 | $0.08 | 97256 |
| 15 | $0.07 | 102192 |
| 16 | $0.05 | 103891 |
| 17 | $0.08 | 108992 |
| 18 | $0.10 | 117343 |
| 19 | $0.07 | 120690 |
| 20 | $0.07 | 125471 |
| 21 | $0.05 | 125929 |
| 22 | $0.05 | 126785 |
| 23 | $0.04 | 127340 |
| 24 | $0.06 | 129666 |
| 25 | $0.05 | 130437 |
| 26 | $0.11 | 139951 |
| 27 | $0.05 | 140611 |
| 28 | $0.05 | 140999 |
| 29 | $0.05 | 141752 |
| 30 | $0.06 | 143977 |
| 31 | $0.05 | 144529 |
| 32 | $0.05 | 145045 |
| 33 | $0.49 | 78411 |
| 34 | $0.08 | 84422 |
| 35 | $0.03 | 85917 |
| 36 | $0.03 | 86376 |
| 37 | $0.04 | 88176 |
| 38 | $0.09 | 95319 |
| 39 | $0.03 | 95718 |
| 40 | $0.03 | 96355 |
| 41 | $0.03 | 96640 |
| 42 | $0.03 | 97171 |
| 43 | $0.03 | 97456 |
| 44 | $0.03 | 97844 |
| 45 | $0.03 | 98207 |
| 46 | $0.04 | 99278 |
| 47 | $0.03 | 100000 |
| 48 | $0.04 | 100662 |
| 49 | $0.03 | 100885 |
| 50 | $0.03 | 101235 |
| 51 | $0.08 | 107382 |
| 52 | $0.05 | 109722 |
| 53 | $0.03 | 110180 |
| 54 | $0.03 | 110594 |
| 55 | $0.07 | 115306 |
| 56 | $0.04 | 115820 |
| 57 | $0.03 | 116175 |
| 58 | $0.04 | 116674 |
| 59 | $0.03 | 117156 |
| 60 | $0.04 | 117762 |
| 61 | $0.04 | 118285 |
| 62 | $0.03 | 118842 |
| 63 | $0.04 | 119172 |
| 64 | $0.04 | 119858 |
| 65 | $0.03 | 120461 |
| 66 | $0.04 | 121161 |
| 67 | $0.04 | 121826 |
| 68 | $0.04 | 122378 |
| 69 | $0.03 | 122967 |
| 70 | $0.04 | 123675 |
| 71 | $0.04 | 124313 |
| 72 | $0.10 | 133186 |
| 73 | $0.05 | 134133 |
| 74 | $0.04 | 135276 |
| 75 | $0.04 | 135825 |
| 76 | $0.05 | 137115 |
| 77 | $0.04 | 138509 |
| 78 | $0.06 | 140869 |
| 79 | $0.04 | 141659 |
| 80 | $0.04 | 142406 |
| 81 | $0.05 | 143385 |
| 82 | $0.04 | 143669 |
| 83 | $0.04 | 144354 |
| 84 | $0.06 | 146925 |
| 85 | $0.04 | 147503 |
| 86 | $0.05 | 148390 |
| 87 | $0.04 | 148904 |
| 88 | $0.04 | 149404 |
| 89 | $0.50 | 78413 |
| 90 | $0.07 | 84655 |
| 91 | $0.04 | 86159 |
| 92 | $0.04 | 87762 |
| 93 | $0.05 | 90573 |
| 94 | $0.03 | 91168 |
| 95 | $0.04 | 91667 |
| 96 | $0.03 | 91993 |
| 97 | $0.03 | 92363 |
| 98 | $0.03 | 92670 |
| 99 | $0.03 | 92960 |
| 100 | $0.03 | 93329 |
| 101 | $0.04 | 93798 |
| 102 | $0.03 | 94092 |
| 103 | $0.03 | 94958 |
| 104 | $0.07 | 99469 |
| 105 | $0.04 | 100620 |
| 106 | $0.03 | 101233 |
| 107 | $0.04 | 101663 |
| 108 | $0.03 | 101887 |
| 109 | $0.04 | 102577 |
| 110 | $0.03 | 103201 |
| 111 | $0.10 | 112138 |
| 112 | $0.04 | 112711 |
| 113 | $0.04 | 113417 |
| 114 | $0.04 | 113928 |
| 115 | $0.03 | 114388 |
| 116 | $0.04 | 114857 |
| 117 | $0.04 | 115865 |
| 118 | $0.05 | 117451 |
| 119 | $0.04 | 118340 |
| 120 | $0.04 | 119008 |
| 121 | $0.04 | 119892 |
| 122 | $0.04 | 120602 |
| 123 | $0.04 | 121844 |
| 124 | $0.05 | 122816 |
| 125 | $0.04 | 123688 |
| 126 | $0.05 | 125326 |
| 127 | $0.06 | 128903 |
| 128 | $0.04 | 129795 |
| 129 | $0.05 | 130980 |
| 130 | $0.04 | 132091 |
| 131 | $0.05 | 132864 |
| 132 | $0.04 | 133500 |
| 133 | $0.05 | 135788 |
| 134 | $0.04 | 136278 |
| 135 | $0.05 | 137162 |
| 136 | $0.04 | 137808 |
| 137 | $0.05 | 139308 |
| 138 | $0.05 | 140121 |
| 139 | $0.04 | 140484 |
| 140 | $0.04 | 141407 |
| 141 | $0.06 | 143947 |
| 142 | $0.04 | 144364 |
| 143 | $0.11 | 152494 |
| 144 | $0.04 | 153046 |
| 145 | $0.49 | 78412 |
| 146 | $0.06 | 84423 |
| 147 | $0.03 | 85914 |
| 148 | $0.02 | 86319 |
| 149 | $0.04 | 89699 |
| 150 | $0.06 | 95283 |
| 151 | $0.02 | 95671 |
| 152 | $0.02 | 96331 |
| 153 | $0.02 | 96746 |
| 154 | $0.02 | 97198 |
| 155 | $0.02 | 97582 |
| 156 | $0.02 | 98033 |
| 157 | $0.03 | 98831 |
| 158 | $0.03 | 99612 |
| 159 | $0.03 | 100285 |
| 160 | $0.02 | 100888 |
| 161 | $0.02 | 101433 |
| 162 | $0.02 | 101901 |
| 163 | $0.03 | 103249 |
| 164 | $0.02 | 103666 |
| 165 | $0.03 | 105047 |
| 166 | $0.02 | 105496 |
| 167 | $0.03 | 106260 |
| 168 | $0.03 | 107061 |
| 169 | $0.02 | 107499 |
| 170 | $0.03 | 108515 |
| 171 | $0.02 | 108884 |
| 172 | $0.03 | 109669 |
| 173 | $0.03 | 110108 |
| 174 | $0.03 | 110901 |
| 175 | $0.03 | 112337 |
| 176 | $0.05 | 115909 |
| 177 | $0.03 | 116772 |
| 178 | $0.03 | 117417 |
| 179 | $0.03 | 118694 |
| 180 | $0.03 | 119552 |
| 181 | $0.03 | 120078 |
| 182 | $0.03 | 120712 |
| 183 | $0.03 | 121135 |
| 184 | $0.03 | 121911 |
| 185 | $0.03 | 122429 |
| 186 | $0.03 | 123208 |
| 187 | $0.03 | 123922 |
| 188 | $0.03 | 124695 |
| 189 | $0.04 | 126743 |
| 190 | $0.03 | 127672 |
| 191 | $0.03 | 128704 |
| 192 | $0.04 | 130316 |
| 193 | $0.03 | 131179 |
| 194 | $0.03 | 132219 |
| 195 | $0.03 | 133256 |
| 196 | $0.03 | 134019 |
| 197 | $0.03 | 134608 |
| 198 | $0.04 | 135752 |
| 199 | $0.04 | 137729 |
| 200 | $0.04 | 138672 |
| 201 | $0.04 | 140737 |
| 202 | $0.03 | 141503 |
| 203 | $0.03 | 142083 |
| 204 | $0.03 | 142486 |
| 205 | $0.03 | 143034 |
| 206 | $0.04 | 143885 |
| 207 | $0.04 | 145801 |
| 208 | $0.04 | 146724 |
| 209 | $0.04 | 147547 |
| 210 | $0.10 | 156483 |
| 211 | $0.04 | 157016 |
| 212 | $0.04 | 157890 |
| 213 | $0.05 | 159599 |
| 214 | $0.04 | 160551 |
| 215 | $0.05 | 162560 |
| 216 | $0.04 | 163080 |
| 217 | $0.04 | 164350 |
| 218 | $0.05 | 166330 |
| 219 | $0.04 | 166749 |
| 220 | $0.04 | 167325 |
| 221 | $0.05 | 168997 |
| 222 | $0.04 | 169410 |
| 223 | $0.04 | 170327 |
| 224 | $0.04 | 171422 |
| 225 | $0.07 | 176169 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 8 | 1507 | $0.03 |
| 🟢 Green | 9 | 1967 | $0.04 |
| 🛠️ Refactor | 4 | 1052 | $0.02 |
| 🔎 verify-green | 7 | 1939 | $0.04 |
| 🔎 verify-refactor | 4 | 1052 | $0.02 |
| 🔎 verify-<phase> (revised) | 1 | 3 | $0.00 |
| 🗺️ Plan | 1 | 755 | $0.02 |
| 🗺️ verify-plan | 4 | 1701 | $0.03 |
| ▶️ Resuming | 3 | 940 | $0.02 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 3 | 1685 | $0.03 |
| Total | 32 | 9607 | $0.19 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 4 | 4 | 0 | 0 | 68 | 50 | 4 | 8 | 5460 | 0 | 81205 | 0.26 |
| diff | 4 | 2 | 0 | 0 | 902 | 97 | 25 | 48 | 11200 | 428044 | 101800 | 0.41 |
| red | 14 | 6 | 1 | 0 | 1574 | 337 | 77 | 140 | 28433 | 1367661 | 335189 | 1.40 |
| green | 19 | 4 | 3 | 0 | 4108 | 448 | 102 | 202 | 34184 | 1761542 | 384004 | 1.76 |
| red-missing | 3 | 0 | 0 | 0 | 155 | 69 | 15 | 28 | 6917 | 405605 | 111039 | 0.39 |
| pin | 4 | 4 | 0 | 0 | 165 | 82 | 14 | 28 | 4971 | 205482 | 59421 | 0.22 |
| refactor | 5 | 1 | 0 | 0 | 171 | 47 | 17 | 34 | 3068 | 237470 | 90807 | 0.28 |
| red-contradicted | 1 | 0 | 0 | 0 | 43 | 24 | 5 | 8 | 2711 | 70760 | 20881 | 0.09 |
| exhausted | 1 | 0 | 0 | 0 | 181 | 16 | 3 | 6 | 1367 | 41459 | 13966 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 25 | 21 | 4 | 0 | 4078 | 470 | 95 | 184 | 33260 | 1341126 | 474934 | 1.65 |
| developer | claude-sonnet-5-5 | 23 | 0 | 0 | 0 | 2594 | 485 | 128 | 244 | 46087 | 2463005 | 561351 | 2.22 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 695 | 215 | 39 | 74 | 18964 | 713892 | 162027 | 1.04 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 476 | 0.56 |
| green | 3291 | 1.06 | 414 | 0.57 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 43 | 0.09 |
| exhausted | 0 | 0.00 | 181 | 0.11 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Test-only, no production change: the `scenario` fixture in skills/tdd/scripts/tests/py/unit/test_queued_merge.py answers the PR read `gh api repos/o/r/pulls/7` with `{"state": "open", "merged": false, "head": {"sha": "9999999"}}` until a merge call (`gh pr merge` or the REST PUT to `pulls/7/merge`) has exited 0, and with its configured `merged` answer (and `gh_code`) only after; every `git merge-base --is-ancestor` call naming `origin/main` exits 1 (not an ancestor); the case test_2585_queued_merge_by_default_exits_1_with_no_tag_branch_delete_or_worktree_removal_when_the_rest_merge_is_refused_because_the_head_moved runs with VERI_MERGE_SETTLE_SLEEP=0 and drops its two assertions that no `pulls/7 ` read follows the refused PUT and that the PUT is not gated `--keep`, keeping exit 1 and nothing cleaned up; every existing case stays green against the unchanged script ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 13 | 24 | 4904 | 221964 | 48950 | 0.19 | 487 | n/a | n/a | n/a |  |  | full |
| Test-only, no production change: every fake `gh` in skills/tdd/scripts/tests/py/test_queued_merge_process.py answers a `/pulls/` read made before a merge call (`gh pr merge`, or `gh api -X PUT …/merge`) has exited 0 with `"state": "open"` and `"merged": false`, its current record only after (tracked by a marker file in the case's own tmp dir), and every fake `git` exits 1 on a `merge-base --is-ancestor` call naming `origin/main`; every existing case stays green against the unchanged script ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 12 | 24 | 6296 | 206080 | 52850 | 0.22 | 791 | n/a | n/a | n/a |  |  | full |
| When the merge call exits non-zero and the PR still reads open (`state: open`, `merged: false`) on every re-read of the settle window (VERI_MERGE_SETTLE_READS re-reads, default 10, spaced VERI_MERGE_SETTLE_SLEEP seconds, default 3, both read as tunables so tests set the sleep to 0 and never wait), queued-merge exits non-zero with the merge lock released and no tag, branch delete or worktree removal; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 2⟧ | 10 | 3 | 1 | 0 | 0 | 0 | 221 | 49 | 96 | 17778 | 980760 | 267835 | 1.05 | 4807 | 1/2 | 0/5 | nothing-structural |  |  | already-satisfied |
| When the merge call exits non-zero and the PR reads merged (`merged: true`) on the first re-read after it, queued-merge treats the PR as merged: it exits 0 and runs the tag, branch delete and worktree removal as on a clean merge; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli with VERI_MERGE_SETTLE_SLEEP=0 ⟦criterion 1⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 182 | 40 | 80 | 13987 | 679003 | 187779 | 0.68 | 1804 | unknown | 0/5 | nothing-structural |  |  | already-satisfied |
| When the merge call exits non-zero and the PR reads open on the first re-read but merged on a later re-read still within VERI_MERGE_SETTLE_READS, queued-merge keeps re-reading (waiting VERI_MERGE_SETTLE_SLEEP between reads) and treats the PR as merged: exit 0 with tag, branch delete and worktree removal; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli with VERI_MERGE_SETTLE_SLEEP=0 ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 11 | 20 | 4044 | 198764 | 37788 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| When the PR already reads merged (`merged: true`) on a read of `gh api repos/<o>/<r>/pulls/<n>` made after the fetch of origin, queued-merge refuses with exit 2 naming it on stderr, before any rebase or push; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 3⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 169 | 45 | 86 | 12554 | 763666 | 176880 | 0.64 | 1746 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| When the PR already reads closed and unmerged (`state: closed`, `merged: false`) on that read after the fetch, queued-merge refuses with exit 2 naming it on stderr, before any rebase or push; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 29 | 56 | 7770 | 479607 | 105498 | 0.39 | 1014 | unknown | 1/5 | nothing-structural |  |  | full |
| When the PR's head (the pull record's `head.sha`) is already an ancestor of origin/main (`git merge-base --is-ancestor <head.sha> origin/main` exits 0; any other exit is not an ancestor), queued-merge refuses with exit 2 naming it on stderr, before any rebase or push; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 3⟧ | 11 | 2 | 1 | 0 | 0 | 0 | 317 | 59 | 108 | 25518 | 988179 | 239527 | 1.32 | unknown | red 1/2, green 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When the merge call exits non-zero and the PR still reads open (`state: open`, `merged: false`) on every re-read of the settle window (VERI_MERGE_SETTLE_READS re-reads, default 10, spaced VERI_MERGE_SETTLE_SLEEP seconds, default 3, both read as tunables so tests set the sleep to 0 and never wait), queued-merge exits non-zero with the merge lock released and no tag, branch delete or worktree removal; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | skipped | 0 | 15 | 0.06 |
| When the merge call exits non-zero and the PR reads merged (`merged: true`) on the first re-read after it, queued-merge treats the PR as merged: it exits 0 and runs the tag, branch delete and worktree removal as on a clean merge; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli with VERI_MERGE_SETTLE_SLEEP=0 ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | skipped | 0 | 12 | 0.06 |
| When the PR already reads merged (`merged: true`) on a read of `gh api repos/<o>/<r>/pulls/<n>` made after the fetch of origin, queued-merge refuses with exit 2 naming it on stderr, before any rebase or push; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 15 | 0.06 |
| When the PR already reads closed and unmerged (`state: closed`, `merged: false`) on that read after the fetch, queued-merge refuses with exit 2 naming it on stderr, before any rebase or push; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 129 | 0.10 |

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| When the merge call exits non-zero and the PR still reads open (`state: open`, `merged: false`) on every re-read of the settle window (VERI_MERGE_SETTLE_READS re-reads, default 10, spaced VERI_MERGE_SETTLE_SLEEP seconds, default 3, both read as tunables so tests set the sleep to 0 and never wait), queued-merge exits non-zero with the merge lock released and no tag, branch delete or worktree removal; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-structural 1 |
| When the merge call exits non-zero and the PR reads merged (`merged: true`) on the first re-read after it, queued-merge treats the PR as merged: it exits 0 and runs the tag, branch delete and worktree removal as on a clean merge; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli with VERI_MERGE_SETTLE_SLEEP=0 ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-structural 1 |
| When the PR already reads merged (`merged: true`) on a read of `gh api repos/<o>/<r>/pulls/<n>` made after the fetch of origin, queued-merge refuses with exit 2 naming it on stderr, before any rebase or push; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 3⟧ | 1 | 0 | 1 | nothing-left 1 |
| When the PR already reads closed and unmerged (`state: closed`, `merged: false`) on that read after the fetch, queued-merge refuses with exit 2 naming it on stderr, before any rebase or push; a small case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through run_cli ⟦criterion 3⟧ | 1 | 1 | 0 | nothing-structural 1 |
| issue | 4 | 1 | 3 | nothing-left 1, nothing-structural 3 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 46 | 78 | 161 | 122 | 0 | 195 | 118 | 89 | 109 | 69 | 100 | 86 | 178 | 153 | 138 | 67 | 164 | 140 | 123 | 106 | 79 | 80 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 7 | 9 | 122 | 73 | 14 | 19 | 20 | 19 | 12 | 9 | 13 | 16 | 15 | 17 | 11 | 3 | 19 | 67 | 8 | 15 | 14 | 10 | 15 | 15 | 10 | 15 | 14 | 11 | 10 | 11 | 9 | 9 | 9 | 14 | 14 | 14 | 15 | 12 |
| target | 4 | 10 | 6 | 7 | 0 | 5 | 14 | 14 | 7 | 7 | 8 | 2 | 9 | 9 | 8 | 10 | 9 | 5 | 5 | 4 | 5 | 6 | 2 | 7 | 6 | 6 | 17 | 21 | 9 | 8 | 8 | 3 | 6 | 6 | 4 | 2 | 4 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 262 | 502 | 98311 | 4518023 | 1198312 | 16.12 (estimate) |
