### 📊 Metrics — issue 1632

Wall time for the issue: 4228 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1640.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 1 | 2 | 934 | 12193 | 43687 | 0.19 |
| red | 19 | 9 | 0 | 0 | 564 | 468 | 94 | 184 | 32276 | 4430172 | 904179 | 4.38 |
| green | 18 | 9 | 0 | 0 | 1054 | 411 | 93 | 180 | 27552 | 4273162 | 815974 | 3.97 |
| refactor | 18 | 9 | 0 | 0 | 685 | 326 | 83 | 160 | 23094 | 3678883 | 818549 | 3.87 |
| predicate | 2 | 0 | 0 | 0 | 42 | 33 | 8 | 16 | 1485 | 346517 | 84995 | 0.39 |
| structural | 2 | 0 | 0 | 0 | 54 | 18 | 6 | 10 | 1289 | 191061 | 79979 | 0.35 |
| transform | 1 | 1 | 0 | 0 | 25 | 20 | 4 | 8 | 997 | 174680 | 42749 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 29 | 29 | 0 | 0 | 1252 | 569 | 118 | 232 | 38408 | 5118064 | 1297563 | 6.09 |
| developer | claude-sonnet-5-5 | 32 | 0 | 0 | 0 | 1188 | 719 | 171 | 328 | 49219 | 7988604 | 1492549 | 7.26 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A planted test_*.py file whose own source starts a process through `subprocess` (e.g. `subprocess.run`) is reported by the fast-tier guard as an offence naming `<file>:<line>` of that call, judged by reading the file's source with no timing and no process started, while a clean planted test_*.py file (no process, sleep, socket or nested suite) yields no offence; pinned by small in-process pytest cases (no process mark) over files planted in tmp_path ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 129 | 30 | 52 | 8471 | 1200486 | 275823 | 1.31 | 344 | unknown | 0/5 | nothing-left |  |  | full |
| A planted test_*.py file that starts a process through a name imported from subprocess (`from subprocess import run` then `run(...)`) or through an aliased module (`import subprocess as sp` then `sp.run(...)`) is reported by the fast-tier guard as a process-start offence naming `<file>:<line>` of the call; pinned by small in-process pytest cases over files planted in tmp_path ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 108 | 25 | 50 | 7893 | 1125187 | 270532 | 1.27 | 278 | unknown | 0/5 | nothing-left |  |  | full |
| A planted test_*.py file whose own source calls `os.system`, an `os.exec*` function (e.g. `os.execv`), an `os.spawn*` function (e.g. `os.spawnl`) or uses `pty` (e.g. `pty.spawn`) is each reported by the fast-tier guard as a process-start offence naming `<file>:<line>`; one planted offender per form, each turning the guard red, pinned by small in-process pytest cases over files planted in tmp_path ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 173 | 28 | 56 | 9320 | 1304015 | 275479 | 1.33 | 334 | unknown | 1/5 | nothing-structural |  |  | full |
| A planted test_*.py file whose own source calls `time.sleep` is reported by the fast-tier guard as a sleep offence naming `<file>:<line>`; pinned by a small in-process pytest case over a file planted in tmp_path ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 109 | 31 | 60 | 8045 | 1419982 | 273995 | 1.32 | 267 | unknown | 1/5 | nothing-structural |  |  | full |
| A planted test_*.py file whose own source opens a socket (e.g. `socket.socket(...)` or `socket.create_connection(...)`) is reported by the fast-tier guard as a socket offence naming `<file>:<line>`; pinned by a small in-process pytest case over a file planted in tmp_path ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 94 | 23 | 46 | 6557 | 1025570 | 271739 | 1.26 | 255 | unknown | 0/5 | structural-owed |  |  | full |
| A planted test_*.py file whose own source runs another suite — calls `pytest.main(...)`, or names another suite file (a `test_*.py` or `*.test.sh` path) as what it runs — is reported by the fast-tier guard as a nested-suite offence naming `<file>:<line>`; pinned by a small in-process pytest case over a file planted in tmp_path ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 126 | 37 | 74 | 11844 | 1795663 | 326861 | 1.61 | 279 | unknown | 1/5 | nothing-left |  |  | full |
| A planted test_*.py file that opens a socket or sleeps through an imported name or an aliased module (`from socket import socket` then `socket(...)`, `import socket as s` then `s.socket(...)`, `from time import sleep` then `sleep(...)`) is reported by the fast-tier guard as a socket or sleep offence naming `<file>:<line>` of the call; pinned by small in-process pytest cases over files planted in tmp_path ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 146 | 32 | 62 | 10471 | 1495725 | 279901 | 1.37 | 310 | unknown | 1/5 | nothing-left |  |  | full |
| The fast-tier guard works against an exemption table in which every entry carries a reason: an offence whose `<file>:<line>` the table exempts is not reported, while the same offence absent from the table is, and a table entry with an empty reason is refused (the guard fails, naming that entry); pinned by small in-process pytest cases ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 167 | 33 | 64 | 10540 | 1564023 | 282047 | 1.39 | 330 | unknown | 1/5 | structural-owed |  |  | full |
| `make test` runs the fast-tier guard over every `test_*.py` under `skills/tdd/scripts/tests/py/unit/` with the real exemption table, and a run with an offending file there fails, naming `<file>:<line>`; the sweeping case carries `@pytest.mark.tree_audit(...)` and passes over the tree as committed ⟦criterion 1⟧ | 11 | 4 | 0 | 0 | 0 | 0 | 224 | 49 | 94 | 13552 | 2163824 | 490048 | 2.31 | 327 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A planted test_*.py file whose own source starts a process through `subprocess` (e.g. `subprocess.run`) is reported by the fast-tier guard as an offence naming `<file>:<line>` of that call, judged by reading the file's source with no timing and no process started, while a clean planted test_*.py file (no process, sleep, socket or nested suite) yields no offence; pinned by small in-process pytest cases (no process mark) over files planted in tmp_path ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 72 | 0.39 |
| A planted test_*.py file that starts a process through a name imported from subprocess (`from subprocess import run` then `run(...)`) or through an aliased module (`import subprocess as sp` then `sp.run(...)`) is reported by the fast-tier guard as a process-start offence naming `<file>:<line>` of the call; pinned by small in-process pytest cases over files planted in tmp_path ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 65 | 0.41 |
| A planted test_*.py file whose own source calls `os.system`, an `os.exec*` function (e.g. `os.execv`), an `os.spawn*` function (e.g. `os.spawnl`) or uses `pty` (e.g. `pty.spawn`) is each reported by the fast-tier guard as a process-start offence naming `<file>:<line>`; one planted offender per form, each turning the guard red, pinned by small in-process pytest cases over files planted in tmp_path ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 78 | 0.44 |
| A planted test_*.py file whose own source calls `time.sleep` is reported by the fast-tier guard as a sleep offence naming `<file>:<line>`; pinned by a small in-process pytest case over a file planted in tmp_path ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 78 | 0.45 |
| A planted test_*.py file whose own source opens a socket (e.g. `socket.socket(...)` or `socket.create_connection(...)`) is reported by the fast-tier guard as a socket offence naming `<file>:<line>`; pinned by a small in-process pytest case over a file planted in tmp_path ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 68 | 0.39 |
| A planted test_*.py file that opens a socket or sleeps through an imported name or an aliased module (`from socket import socket` then `socket(...)`, `import socket as s` then `s.socket(...)`, `from time import sleep` then `sleep(...)`) is reported by the fast-tier guard as a socket or sleep offence naming `<file>:<line>` of the call; pinned by small in-process pytest cases over files planted in tmp_path ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 92 | 0.46 |
| A planted test_*.py file whose own source runs another suite — calls `pytest.main(...)`, or names another suite file (a `test_*.py` or `*.test.sh` path) as what it runs — is reported by the fast-tier guard as a nested-suite offence naming `<file>:<line>`; pinned by a small in-process pytest case over a file planted in tmp_path ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 76 | 0.45 |
| The fast-tier guard works against an exemption table in which every entry carries a reason: an offence whose `<file>:<line>` the table exempts is not reported, while the same offence absent from the table is, and a table entry with an empty reason is refused (the guard fails, naming that entry); pinned by small in-process pytest cases ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 80 | 0.46 |
| `make test` runs the fast-tier guard over every `test_*.py` under `skills/tdd/scripts/tests/py/unit/` with the real exemption table, and a run with an offending file there fails, naming `<file>:<line>`; the sweeping case carries `@pytest.mark.tree_audit(...)` and passes over the tree as committed ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 76 | 0.42 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 29 | 1 |
| fast | 31 | 31 | 31 | 31 | 30 | 30 | 30 | 30 | 30 | 29 | 30 | 30 | 29 | 30 | 30 | 29 | 29 | 30 | 30 | 29 | 30 | 29 | 30 | 30 | 29 | 29 | 35 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 289 | 560 | 87627 | 13106668 | 2790112 | 13.35 |
