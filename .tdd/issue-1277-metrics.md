### 📊 Metrics — issue 1277

Wall time for the issue: 4073 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1455.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 938 | 12489 | 34825 | 0.15 |
| red | 4 | 0 | 0 | 0 | 455 | 225 | 55 | 108 | 29660 | 3497699 | 248389 | 1.64 |
| pin | 4 | 4 | 0 | 0 | 240 | 67 | 23 | 44 | 8799 | 991737 | 177150 | 0.90 |
| green | 8 | 4 | 0 | 0 | 853 | 155 | 60 | 118 | 18785 | 2890529 | 365654 | 1.94 |
| refactor | 8 | 4 | 0 | 0 | 354 | 119 | 46 | 92 | 13500 | 2169619 | 355355 | 1.77 |
| diff | 2 | 1 | 0 | 0 | 144 | 38 | 12 | 24 | 4848 | 536466 | 83526 | 0.44 |
| predicate | 1 | 0 | 0 | 0 | 9 | 7 | 4 | 8 | 800 | 160069 | 39100 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 14 | 0 | 0 | 926 | 219 | 75 | 148 | 28012 | 3322767 | 602880 | 3.02 |
| developer | claude-sonnet-5-5 | 14 | 0 | 0 | 0 | 1138 | 399 | 126 | 248 | 49318 | 6935841 | 701119 | 3.99 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Signals to a live supervisor — TERM, and INT or HUP alike, write 2 to its completion file, exit 2 and leave no leaf process behind; a supervisor started with SIGINT ignored, as detach-leaf.sh starts one, keeps running its leaf through INT so the leaf's own 0 lands in .exit; and wait-leaf.sh <name> 0 against a live supervisor exits 3 with nothing on stderr — pinned through run_cli in tests/py/test_supervise.py by medium cases marked @pytest.mark.process: replaces 'supervise.sh sent TERM writes 2 to its completion file, exits 2 and leaves no leaf process behind', 'supervise.sh sent INT or HUP does what TERM does: writes 2 to its completion file, exits 2 and leaves no leaf process behind', 'a supervisor started with SIGINT ignored, as detach-leaf.sh starts one, keeps running its leaf when sent INT: the leaf finishes and its own 0 lands in .exit', 'wait-leaf.sh <name> 0 against a live supervisor of that leaf exits 3, not 2, with nothing on stderr' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 166 | 50 | 98 | 20610 | 2688572 | 302947 | 1.69 | 946 | unknown | 1/5 | nothing-structural |  |  | already-satisfied |
| supervise.sh's argument contract — no argument or an empty <name> exits 2 with stderr exactly the usage line, and <name> alone exits 2 with stderr exactly 'supervise: missing <cmd>' then the usage line, nothing on stdout and no .tdd created — pinned through run_cli in tests/py/test_supervise.py by small cases: replaces 'supervise.sh with no argument or an empty <name> exits 2 with stderr exactly the usage line, and with develop-red alone exits 2 with stderr exactly 'supervise: missing <cmd>' then the usage line, nothing on stdout and no .tdd created' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 84 | 31 | 62 | 10400 | 1400153 | 259186 | 1.28 | 353 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| supervise.sh run through a symlink to the skill directory from another working directory answers as in place — events, usage and the preserved attempt land in the caller's .tdd, skill_commit is the skill clone's HEAD, and no .tdd appears beside the skill — pinned in tests/py/test_supervise.py by a medium case marked @pytest.mark.process, covering what of that answer C2's one shim test does not: replaces 'supervise.sh run through a symlink to the skill directory from another working directory answers as in place: events, usage and the preserved attempt land in the caller's .tdd, skill_commit is the skill clone's HEAD, and no .tdd appears beside the skill' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 185 | 62 | 120 | 23618 | 3403545 | 299616 | 1.78 | 715 | unknown | 1/5 | nothing-structural |  |  | already-satisfied |
| Killing a leaf's whole process tree (#1199) — a hung leaf's own recorded background child dies with it at the heartbeat kill; a supervisor started with TERM ignored still leaves no leaf alive after the KILL escalation and exits and records 2; and a group whose leader dies on TERM while the rest ignore it leaves no process of that group alive after the grace period, whether the leaf was killed for silence or for its hard timeout — pinned through run_cli in tests/py/test_supervise.py by medium cases marked @pytest.mark.process: replaces 'a hung leaf that started a background child of its own and recorded its pid leaves neither the leaf nor the child alive after the heartbeat kill', 'a supervisor started with TERM ignored, whose silent leaf is killed for silence, leaves no leaf process alive after the KILL escalation and exits 2 with 2 in .tdd/<name>.exit', '#1199: a leaf killed for silence whose group leader dies on TERM while the rest of its group ignores TERM leaves no process of that group alive after the grace period', '#1199: a leaf killed for its hard timeout whose group leader dies on TERM while the rest of its group ignores TERM leaves no process of that group alive after the grace period' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 131 | 41 | 82 | 16116 | 2057314 | 284799 | 1.51 | 941 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| supervise.test.sh's remaining cases still pass and the file stays for the other C4d groups, since cases remain after this group's removal; tests/real-clock-audit.sh and its rows, CLAUDE.md's Testing idiom and ci.yml's comment keep every reference they still need, and CLAUDE.md's suite count matches the tree ⟦diff-checked⟧ ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 45 | 16 | 32 | 5648 | 696535 | 122626 | 0.62 | 166 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Signals to a live supervisor — TERM, and INT or HUP alike, write 2 to its completion file, exit 2 and leave no leaf process behind; a supervisor started with SIGINT ignored, as detach-leaf.sh starts one, keeps running its leaf through INT so the leaf's own 0 lands in .exit; and wait-leaf.sh <name> 0 against a live supervisor exits 3 with nothing on stderr — pinned through run_cli in tests/py/test_supervise.py by medium cases marked @pytest.mark.process: replaces 'supervise.sh sent TERM writes 2 to its completion file, exits 2 and leaves no leaf process behind', 'supervise.sh sent INT or HUP does what TERM does: writes 2 to its completion file, exits 2 and leaves no leaf process behind', 'a supervisor started with SIGINT ignored, as detach-leaf.sh starts one, keeps running its leaf when sent INT: the leaf finishes and its own 0 lands in .exit', 'wait-leaf.sh <name> 0 against a live supervisor of that leaf exits 3, not 2, with nothing on stderr' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 97 | 0.47 |
| supervise.sh's argument contract — no argument or an empty <name> exits 2 with stderr exactly the usage line, and <name> alone exits 2 with stderr exactly 'supervise: missing <cmd>' then the usage line, nothing on stdout and no .tdd created — pinned through run_cli in tests/py/test_supervise.py by small cases: replaces 'supervise.sh with no argument or an empty <name> exits 2 with stderr exactly the usage line, and with develop-red alone exits 2 with stderr exactly 'supervise: missing <cmd>' then the usage line, nothing on stdout and no .tdd created' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 70 | 0.38 |
| supervise.sh run through a symlink to the skill directory from another working directory answers as in place — events, usage and the preserved attempt land in the caller's .tdd, skill_commit is the skill clone's HEAD, and no .tdd appears beside the skill — pinned in tests/py/test_supervise.py by a medium case marked @pytest.mark.process, covering what of that answer C2's one shim test does not: replaces 'supervise.sh run through a symlink to the skill directory from another working directory answers as in place: events, usage and the preserved attempt land in the caller's .tdd, skill_commit is the skill clone's HEAD, and no .tdd appears beside the skill' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 104 | 0.48 |
| Killing a leaf's whole process tree (#1199) — a hung leaf's own recorded background child dies with it at the heartbeat kill; a supervisor started with TERM ignored still leaves no leaf alive after the KILL escalation and exits and records 2; and a group whose leader dies on TERM while the rest ignore it leaves no process of that group alive after the grace period, whether the leaf was killed for silence or for its hard timeout — pinned through run_cli in tests/py/test_supervise.py by medium cases marked @pytest.mark.process: replaces 'a hung leaf that started a background child of its own and recorded its pid leaves neither the leaf nor the child alive after the heartbeat kill', 'a supervisor started with TERM ignored, whose silent leaf is killed for silence, leaves no leaf process alive after the KILL escalation and exits 2 with 2 in .tdd/<name>.exit', '#1199: a leaf killed for silence whose group leader dies on TERM while the rest of its group ignores TERM leaves no process of that group alive after the grace period', '#1199: a leaf killed for its hard timeout whose group leader dies on TERM while the rest of its group ignores TERM leaves no process of that group alive after the grace period' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 83 | 0.43 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 5 | 17 | 17 | 8 | 7 | 7 | 24 | 23 | 0 | 9 | 9 | 8 | 8 | 9 | 16 | 26 | 3 | 8 | 9 | 15 | 28 | 28 | 0 | 13 | 13 |
| target | 8 | 13 | 6 | 7 | 2 | 1 | 0 | 0 | 0 | 2 | 3 | 2 | 2 | 24 | 5 | 69 | 21 | 5 |  |  |  |  |  |  |  |  |
| fast | 24 | 25 | 24 | 25 | 24 | 24 | 23 | 25 | 26 | 25 | 25 | 23 | 23 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 201 | 396 | 77330 | 10258608 | 1303999 | 7.02 |
