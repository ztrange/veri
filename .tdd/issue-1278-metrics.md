### 📊 Metrics — issue 1278

Wall time for the issue: 3904 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1476.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 1080 | 12489 | 34229 | 0.15 |
| red | 3 | 0 | 0 | 0 | 230 | 132 | 32 | 62 | 17355 | 1868297 | 181168 | 1.09 |
| pin | 3 | 3 | 0 | 0 | 70 | 57 | 15 | 30 | 6518 | 647835 | 126780 | 0.64 |
| green | 6 | 3 | 0 | 0 | 571 | 105 | 46 | 86 | 13323 | 2090909 | 272626 | 1.43 |
| refactor | 6 | 3 | 0 | 0 | 867 | 83 | 34 | 68 | 10164 | 1593129 | 265172 | 1.32 |
| diff | 2 | 1 | 0 | 0 | 152 | 32 | 11 | 20 | 3771 | 444678 | 86318 | 0.43 |
| rebase | 2 | 1 | 0 | 0 | 598 | 27 | 12 | 22 | 3023 | 489550 | 84144 | 0.42 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 12 | 0 | 0 | 1119 | 176 | 58 | 110 | 21200 | 2358759 | 499749 | 2.45 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 1380 | 268 | 93 | 180 | 34034 | 4788128 | 550688 | 3.02 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A launch is refused, exit 2 and its command not run, with stderr naming the live leaf's name and its supervisor's pid, while a leaf supervised under another name or under the same name is alive in the same worktree — still after the pre-launch rm -f .tdd/<name>.exit .tdd/<name>.pid — pinned through run_cli in tests/py/test_supervise.py by medium cases marked @pytest.mark.process where the assertion depends on a live process: replaces '#471: a launch under one name is refused while a leaf supervised under another name is alive in the same worktree', '#471: a launch is refused while a leaf supervised under the same name is alive in the same worktree', '#471: a launch is still refused after the pre-launch rm -f .tdd/<name>.exit .tdd/<name>.pid while the first leaf is alive' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 122 | 46 | 86 | 15339 | 2127850 | 283701 | 1.50 | 908 | unknown | 1/5 | nothing-structural |  |  | already-satisfied |
| A launch is not refused when the owner record names a supervised leaf whose process is gone, when the previous supervised leaf finished (under the same name and a different one, the record naming '<pid> <name>'), or when a verify-green launch is made from inside a live verdict-green supervision — each runs its command and exits 0 — pinned through run_cli in tests/py/test_supervise.py: replaces '#471: a record left by a supervised leaf whose process is gone does not refuse the next launch', '#471: a launch after the previous supervised leaf finished runs as today, under the same name and a different one', '#471: a verify-green launch made from inside a live verdict-green supervision is not refused' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 131 | 38 | 76 | 16892 | 1900649 | 273893 | 1.45 | 510 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| A refused launch's completion record (#618) — refused for a live leaf of the same name it writes no .exit for that name and the live leaf's own code lands there when it finishes; refused for a leaf under another name it exits 2, writes 2 to .tdd/<refused-name>.exit and wait-leaf.sh <refused-name> then exits 2, not 3; it never runs its command and leaves .tdd/leaf.owner unchanged; and it is still refused, naming the live leaf and its pid, when the recorded leaf is alive and .tdd/<owner-name>.exit does not exist — pinned through run_cli in tests/py/test_supervise.py, small where a recorded pid can stand in for a live leaf: replaces '#618: a launch refused because a leaf of the same name is alive writes no .exit for that name, and the live leaf's own code lands there when it finishes', '#618: a launch refused because a leaf under another name is alive exits 2 and writes 2 to .tdd/<refused-name>.exit', '#618: after a launch refused because a leaf under another name is alive, wait-leaf.sh <refused-name> exits 2, not 3', '#618: a refused launch does not run its command and leaves .tdd/leaf.owner naming the live leaf, unchanged', '#618: a launch is still refused, naming the live leaf and its pid, when the recorded leaf is alive and .tdd/<owner-name>.exit does not exist' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 124 | 43 | 84 | 15129 | 2171671 | 288152 | 1.52 | 792 | unknown | 1/5 | nothing-left |  |  | already-satisfied |
| supervise.test.sh's remaining cases still pass and the file stays for the other C4d groups, since cases remain after this group's removal; tests/real-clock-audit.sh and its rows, CLAUDE.md's Testing idiom and ci.yml's comment keep every reference they still need, and CLAUDE.md's suite count matches the tree ⟦diff-checked⟧ ⟦criterion 2⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 59 | 23 | 42 | 6794 | 934228 | 170462 | 0.84 | 174 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A launch is refused, exit 2 and its command not run, with stderr naming the live leaf's name and its supervisor's pid, while a leaf supervised under another name or under the same name is alive in the same worktree — still after the pre-launch rm -f .tdd/<name>.exit .tdd/<name>.pid — pinned through run_cli in tests/py/test_supervise.py by medium cases marked @pytest.mark.process where the assertion depends on a live process: replaces '#471: a launch under one name is refused while a leaf supervised under another name is alive in the same worktree', '#471: a launch is refused while a leaf supervised under the same name is alive in the same worktree', '#471: a launch is still refused after the pre-launch rm -f .tdd/<name>.exit .tdd/<name>.pid while the first leaf is alive' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 400 | 0.45 |
| A launch is not refused when the owner record names a supervised leaf whose process is gone, when the previous supervised leaf finished (under the same name and a different one, the record naming '<pid> <name>'), or when a verify-green launch is made from inside a live verdict-green supervision — each runs its command and exits 0 — pinned through run_cli in tests/py/test_supervise.py: replaces '#471: a record left by a supervised leaf whose process is gone does not refuse the next launch', '#471: a launch after the previous supervised leaf finished runs as today, under the same name and a different one', '#471: a verify-green launch made from inside a live verdict-green supervision is not refused' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 76 | 0.38 |
| A refused launch's completion record (#618) — refused for a live leaf of the same name it writes no .exit for that name and the live leaf's own code lands there when it finishes; refused for a leaf under another name it exits 2, writes 2 to .tdd/<refused-name>.exit and wait-leaf.sh <refused-name> then exits 2, not 3; it never runs its command and leaves .tdd/leaf.owner unchanged; and it is still refused, naming the live leaf and its pid, when the recorded leaf is alive and .tdd/<owner-name>.exit does not exist — pinned through run_cli in tests/py/test_supervise.py, small where a recorded pid can stand in for a live leaf: replaces '#618: a launch refused because a leaf of the same name is alive writes no .exit for that name, and the live leaf's own code lands there when it finishes', '#618: a launch refused because a leaf under another name is alive exits 2 and writes 2 to .tdd/<refused-name>.exit', '#618: after a launch refused because a leaf under another name is alive, wait-leaf.sh <refused-name> exits 2, not 3', '#618: a refused launch does not run its command and leaves .tdd/leaf.owner naming the live leaf, unchanged', '#618: a launch is still refused, naming the live leaf and its pid, when the recorded leaf is alive and .tdd/<owner-name>.exit does not exist' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 391 | 0.49 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 17 | 17 | 16 | 30 | 30 | 16 | 14 | 306 | 28 | 17 | 0 | 16 | 16 | 27 | 314 | 17 | 12 | 25 | 12 |
| target | 0 | 1 | 0 | 1 | 1 | 1 | 1 | 2 | 1 | 0 | 0 | 0 |  |  |  |  |  |  |  |
| fast | 25 | 27 | 25 | 26 | 25 | 24 | 23 | 25 | 26 | 25 | 26 | 25 |  |  |  |  |  |  |  |
| all | 283 | 281 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 151 | 290 | 55234 | 7146887 | 1050437 | 5.47 |
