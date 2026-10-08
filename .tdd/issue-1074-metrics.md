### 📊 Metrics — issue 1074

Wall time for the issue: 8921 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 17 of 17 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1176.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 24 | 19 | 1 | 2 | 2124 | 11966 | 55532 | 0.25 |
| red | 17 | 6 | 0 | 0 | 652 | 526 | 88 | 172 | 44019 | 5025148 | 964855 | 8.38 |
| pin | 5 | 5 | 0 | 0 | 839 | 133 | 24 | 48 | 9093 | 1304924 | 275717 | 1.45 |
| green | 11 | 5 | 0 | 0 | 1159 | 338 | 66 | 132 | 28168 | 3887293 | 576042 | 4.76 |
| refactor | 10 | 5 | 0 | 0 | 616 | 226 | 48 | 96 | 15582 | 2657640 | 568983 | 4.26 |
| diff | 8 | 4 | 0 | 0 | 1609 | 252 | 46 | 90 | 15249 | 2534504 | 446883 | 3.43 |
| predicate | 2 | 0 | 0 | 0 | 44 | 34 | 6 | 12 | 2209 | 277838 | 105111 | 0.94 |
| structural | 1 | 0 | 0 | 0 | 45 | 25 | 7 | 12 | 2758 | 340851 | 56176 | 0.57 |
| transform | 1 | 1 | 0 | 0 | 1027 | 24 | 8 | 16 | 1971 | 475657 | 67679 | 0.39 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 27 | 27 | 0 | 0 | 3830 | 625 | 114 | 228 | 44329 | 6057900 | 1451779 | 7.46 |
| developer | claude-opus-5-5 | 29 | 0 | 0 | 0 | 2185 | 952 | 180 | 352 | 76844 | 10457921 | 1665199 | 16.95 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 44 | 0.94 |
| structural | 0 | 0.00 | 45 | 0.57 |
| transform | 0 | 0.00 | 1027 | 0.39 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| wait-leaf.sh run with an empty first argument (`wait-leaf.sh ""`) exits 2 with nothing on stdout and stderr exactly "usage: wait-leaf.sh <name> [max-seconds]\n" — a new case in tests/wait-leaf.test.sh, written against the bash script ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 9 | 18 | 4407 | 499262 | 113543 | 0.87 | unknown | unknown | unknown | unknown |  |  | pin |
| wait-leaf.sh run through a symlink to the skill's scripts directory, from another working directory holding .tdd/<name>.exit with 1 (and the scripts directory holding no .tdd/<name>.exit), exits 1 — it reads the working directory's .tdd/<name>.exit and .tdd/<name>.pid, never ones beside the skill — a new case in tests/wait-leaf.test.sh, written against the bash script ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 76 | 11 | 22 | 4840 | 645607 | 116563 | 0.92 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.wait_leaf.main(argv), with the working directory a tmp_path and subprocess.run faked, returns 2 with nothing on stdout and stderr exactly "usage: wait-leaf.sh <name> [max-seconds]\n" and no process call for [] and [""]; returns 0, 1, 2 and 3 for ["x"] over .tdd/x.exit holding "0\n", "1\n", "2\n" and "3\n", and 2 for "5\n"; returns 3 for ["x", "0"] with no exit file and no pid file: replaces 'migration slice 10 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh — only wait-leaf.sh leaves slice 10's list, verify.sh staying on it and the case staying ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 167 | 35 | 70 | 14042 | 2053213 | 347533 | 2.76 | 492 | unknown | 0/5 | structural-owed |  |  | full |
| veri.wait_leaf.main's refusal for [] and [""] touches no file under tmp_path (no .tdd created); a recorded code is mapped as text: "3" returns 3, and "4", "00", "01" and a 20-digit code return 2; an exit file holding "-1", "7x", nothing, or a directory at .tdd/x.exit is "not yet" and the wait runs on to the deadline, returning 3 — pytest cases in tests/py/test_wait_leaf.py ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 79 | 13 | 26 | 5986 | 759126 | 115391 | 0.93 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.wait_leaf.main runs `date +%s` exactly once before the first round, then per round in this order: the exit-file read, the pid-file read and (when it holds a number) `ps` for that pid, the exit-file recheck only after a dead supervisor, `date +%s`, then `sleep <poll>`; no sleep before the first round and none after the round that answers; a recorded code that lands between the pid check and the recheck (written by the faked `ps`) is returned instead of the dead-supervisor 2 — pytest cases in tests/py/test_wait_leaf.py recording the order of every faked subprocess.run call ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 176 | 31 | 64 | 14210 | 1820092 | 346264 | 2.70 | 447 | unknown | 1/5 | nothing-structural |  |  | full |
| veri.wait_leaf.main reads `max` as wait-leaf.sh does: absent or empty is 540 (the deadline is the first `date` reading plus 540, compared with >=); "0" and "-5" run one full round (exit-file and pid checks) then return 3; "010" is 8 and "0x10" is 16; arguments past `max` are ignored — pytest cases in tests/py/test_wait_leaf.py over a faked `date` returning scripted readings ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 147 | 27 | 54 | 11878 | 1472007 | 340017 | 2.55 | 487 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.wait_leaf.main, given a `max` that is not an integer form (sign, decimal, leading-0 octal, 0x hex), answers as the bash script was observed to: a bare identifier ("abc") returns 1 after the first `date` reading and before any round, with one line on stderr naming it; any other text ("08", "1.5", "10+5") runs round 1's exit-file and pid checks and its `date` reading — a recorded code there still answering — then returns 1 with one line on stderr naming it; nothing on stdout either way — pytest cases in tests/py/test_wait_leaf.py ⟦criterion 5⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 234 | 53 | 104 | 20641 | 3167479 | 429442 | 3.76 | 563 | 1/2 | 1/5 | structural-owed |  |  | full |
| veri.wait_leaf.main hands VERI_POLL to `sleep` as text: unset or empty runs `sleep 1`, "0.02" runs `sleep 0.02`; a `sleep` that exits non-zero does not end the wait, the next round still runs — pytest cases in tests/py/test_wait_leaf.py ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 11 | 20 | 5265 | 567531 | 115663 | 0.91 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.wait_leaf.main treats a pid file that is missing or holds no number as no verdict (no `ps` call, the wait runs on to 3); for a pid file holding "007" whose faked `ps` reports no supervisor it returns 2 with nothing on stdout and stderr exactly "wait-leaf.sh: supervisor for leaf 'x' (pid 007) exited without recording a status\n", `ps` having been asked for "007" — pytest cases in tests/py/test_wait_leaf.py ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 9 | 16 | 3802 | 424083 | 115599 | 0.85 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.wait_leaf.main treats an empty `date` reading (date failing, missing from PATH, or printing nothing) as bash does: before the loop it counts as 0, so the deadline is `max` itself; in a round it never reaches the deadline, so the round goes on to `sleep` and the next round — pytest cases in tests/py/test_wait_leaf.py ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 203 | 27 | 54 | 11791 | 1466605 | 345582 | 2.59 | 479 | unknown | 0/5 | nothing-structural |  |  | full |
| the port: wait-leaf.sh becomes a /bin/sh shim `exec python3 "$(dirname "$0")/veri/wait_leaf.py" "$@"` whose header keeps the lowercase line "usage: wait-leaf.sh <name> [max-seconds]" and cites no issue number; veri/wait_leaf.py gains its __main__ entry, imports number_in and supervising from pid_file and defines neither, and holds no `supervise` match text; every contract case of tests/wait-leaf.test.sh (the two written above included) and tests/unit/emitted-text.test.sh:95, tests/unit/missing-argument-exit.test.sh:30-33, tests/supervise.test.sh:960-984 and :999-1005, tests/verify.test.sh:661-679 and tests/run-conductor.test.sh:1156-1202 pass with their assertions unmodified against it, in a commit that precedes any cut ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 16 | 32 | 5651 | 966109 | 115949 | 0.97 | 965 | n/a | n/a | n/a |  |  | full |
| after the port commit, tests/wait-leaf.test.sh's case "exits 3, never 0, when there is no completion file and no leaf running" (:79-84) is deleted and nothing else in that suite changes, its replacement being the tests/py/test_wait_leaf.py case returning 3 for ["x", "0"] with no exit file and no pid file; the suite's other contract cases and :86-109 stay unmodified ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 10 | 20 | 2764 | 538295 | 107835 | 0.80 | 205 | n/a | n/a | n/a |  |  | full |
| tests/py/test_wait_leaf.py calls veri.wait_leaf.main(argv) in every case, fakes only process boundaries (subprocess.run for date, ps and sleep, files under tmp_path, the captured streams, the environment), never patches a function of veri.wait_leaf or a name bound inside it, and asserts main's return code wherever the bash suite asserts an exit code ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 70 | 11 | 22 | 3625 | 621134 | 116268 | 0.87 | 241 | n/a | n/a | n/a |  |  | full |
| SKILL.md, lib/pid-file.sh, lib/number-in.sh, lib/exit-contract.sh, stop-run.sh and supervise.sh are unchanged by the branch; tests/skill-leaf-launch.test.sh, tests/skill-revise-exhausted.test.sh, tests/skill-stopping.test.sh, tests/py/test_comment_class.py, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh, tests/no-python-in-ported-scripts.test.sh, tests/stop-run.test.sh and tests/py/test_pid_file.py are unchanged, and tests/unit/missing-argument-exit.test.sh differs only by wait-leaf.sh leaving slice 10's line ⟦diff-checked⟧ ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 78 | 9 | 16 | 3209 | 408966 | 106831 | 0.78 | 271 | n/a | n/a | n/a |  |  | full |
| SKILL.md's wait-leaf readers and the source-reading suites (test_comment_class.py, exit-contract.test.sh, scratch-copy-libs.test.sh, no-python-in-ported-scripts.test.sh, missing-argument-exit.test.sh) pass against the shim ⟦full-suite⟧ ⟦criterion 6⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 83 | 21 | 40 | 6938 | 1094346 | 228966 | 1.90 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.wait_leaf.main(argv), with the working directory a tmp_path and subprocess.run faked, returns 2 with nothing on stdout and stderr exactly "usage: wait-leaf.sh <name> [max-seconds]\n" and no process call for [] and [""]; returns 0, 1, 2 and 3 for ["x"] over .tdd/x.exit holding "0\n", "1\n", "2\n" and "3\n", and 2 for "5\n"; returns 3 for ["x", "0"] with no exit file and no pid file: replaces 'migration slice 10 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh — only wait-leaf.sh leaves slice 10's list, verify.sh staying on it and the case staying ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 122 | 0.81 |
| veri.wait_leaf.main runs `date +%s` exactly once before the first round, then per round in this order: the exit-file read, the pid-file read and (when it holds a number) `ps` for that pid, the exit-file recheck only after a dead supervisor, `date +%s`, then `sleep <poll>`; no sleep before the first round and none after the round that answers; a recorded code that lands between the pid check and the recheck (written by the faked `ps`) is returned instead of the dead-supervisor 2 — pytest cases in tests/py/test_wait_leaf.py recording the order of every faked subprocess.run call ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 118 | 0.90 |
| veri.wait_leaf.main reads `max` as wait-leaf.sh does: absent or empty is 540 (the deadline is the first `date` reading plus 540, compared with >=); "0" and "-5" run one full round (exit-file and pid checks) then return 3; "010" is 8 and "0x10" is 16; arguments past `max` are ignored — pytest cases in tests/py/test_wait_leaf.py over a faked `date` returning scripted readings ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 106 | 0.80 |
| veri.wait_leaf.main, given a `max` that is not an integer form (sign, decimal, leading-0 octal, 0x hex), answers as the bash script was observed to: a bare identifier ("abc") returns 1 after the first `date` reading and before any round, with one line on stderr naming it; any other text ("08", "1.5", "10+5") runs round 1's exit-file and pid checks and its `date` reading — a recorded code there still answering — then returns 1 with one line on stderr naming it; nothing on stdout either way — pytest cases in tests/py/test_wait_leaf.py ⟦criterion 5⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 140 | 0.95 |
| veri.wait_leaf.main treats an empty `date` reading (date failing, missing from PATH, or printing nothing) as bash does: before the loop it counts as 0, so the deadline is `max` itself; in a round it never reaches the deadline, so the round goes on to `sleep` and the next round — pytest cases in tests/py/test_wait_leaf.py ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 130 | 0.80 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 5 | 2 | 1 | 12 | 1 | 1 | 2 | 1 | 1 | 2 | 3 | 0 | 2 | 1 | 0 | 3 | 1 | 1 | 1 | 1 | 2 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 3 | 1 | 2 | 2 | 1 | 38 | 14 | 1005 |
| target | 2 | 541 | 0 | 0 | 1 | 4 | 1 | 2 | 0 | 0 | 0 | 1 | 0 | 65 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 62 | 61 | 65 | 62 | 61 | 61 | 65 | 66 | 64 | 64 | 63 | 66 | 67 | 64 | 64 | 62 | 64 | 67 | 65 | 63 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 294 | 580 | 121173 | 16515821 | 3116978 | 24.41 |
