### 📊 Metrics — issue 1471

Wall time for the issue: 6754 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 13 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1479.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 954 | 12193 | 36934 | 0.16 |
| red | 28 | 11 | 1 | 0 | 3431 | 1047 | 185 | 366 | 110090 | 10485662 | 1535117 | 12.50 |
| green | 22 | 11 | 0 | 0 | 7820 | 817 | 179 | 352 | 82015 | 9628132 | 1132880 | 9.21 |
| refactor | 21 | 10 | 0 | 0 | 2221 | 365 | 109 | 212 | 34129 | 5193214 | 1014028 | 7.30 |
| pin | 2 | 2 | 0 | 0 | 318 | 30 | 9 | 18 | 3138 | 418349 | 98061 | 0.47 |
| diff | 2 | 1 | 0 | 0 | 295 | 47 | 18 | 34 | 5086 | 883728 | 96308 | 0.78 |
| predicate | 1 | 0 | 0 | 0 | 11 | 6 | 2 | 4 | 480 | 65434 | 41314 | 0.35 |
| structural | 1 | 0 | 0 | 0 | 74 | 18 | 7 | 14 | 1974 | 343190 | 45285 | 0.47 |
| transform | 1 | 1 | 0 | 0 | 81 | 12 | 6 | 10 | 1240 | 223697 | 43345 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 38 | 37 | 1 | 0 | 6384 | 578 | 191 | 370 | 62467 | 8691031 | 1755969 | 8.52 |
| developer | claude-opus-5-5 | 33 | 0 | 0 | 0 | 5474 | 1407 | 264 | 522 | 132210 | 14907635 | 1836724 | 20.32 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 2403 | 365 | 61 | 120 | 44429 | 3654933 | 450579 | 2.61 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 285 | 1.51 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Under make unit and make test, a pytest case run by the leg finds the stdlib's and installed packages' bytecode resolved to their own existing __pycache__ (importlib.util.cache_from_source on a stdlib module and on pytest's own module names a path beside that module's source), never a per-run empty cache directory ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 194 | 45 | 88 | 18482 | 2243717 | 343230 | 2.91 | 1091 | 1/2 | 0/5 | nothing-structural |  |  | full |
| Two consecutive runs of the pytest leg over the same tree leave one cache directory, under a root the caller can point elsewhere, holding the bytecode of veri's modules and of the test files (pytest's assertion-rewrite output included), and the second run reuses that directory rather than starting an empty one; the directory's name changes when the content of any .py under skills/tdd/scripts changes ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 224 | 39 | 76 | 22026 | 2178304 | 323390 | 2.82 | 1004 | unknown | 0/5 | structural-owed |  |  | full |
| A module under skills/tdd/scripts run by the leg, then rewritten to different content of the same size with its mtime restored, is run from its new source on the next leg run, never from the cached bytecode of the first: a case that goes red if the cache is keyed by anything but content (#1127) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 13 | 26 | 6781 | 676282 | 101327 | 0.86 | unknown | unknown | unknown | unknown |  |  | pin |
| After runs over more distinct contents than the bound, the cache root holds no more than a bounded number of cache directories, the oldest pruned and the current one kept ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 170 | 42 | 82 | 17485 | 1991657 | 382148 | 2.94 | 1026 | 1/2 | 0/5 | nothing-structural |  |  | full |
| A VERI_PYCACHE_KEEP that is not a whole number of at least 1 makes make unit and make test refuse with exit 2 before any suite runs, naming the variable and the value, so the prune can never remove the current run's own cache directory ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 41 | 80 | 14329 | 2053636 | 298222 | 2.42 | 1075 | unknown | 1/5 | nothing-structural |  |  | full |
| With PYTHONDONTWRITEBYTECODE set in the caller's environment, a run of the pytest leg still writes its cache directory ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 116 | 36 | 70 | 10880 | 1795857 | 293534 | 2.29 | 849 | unknown | 0/5 | nothing-structural |  |  | full |
| CLAUDE.md's pytest-leg paragraph describes the content-keyed cache, its pruning and its PYTHONDONTWRITEBYTECODE override in place of the fresh PYTHONPYCACHEPREFIX ⟦diff-checked⟧ ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 83 | 33 | 62 | 8780 | 1516049 | 226252 | 1.81 | 317 | unknown | unknown | unknown |  |  | full |
| After `make unit` or `make test` the worktree holds no `.pyc` the run did not find there, and a fresh `python3` started afterwards outside the leg under `PYTHONDONTWRITEBYTECODE=1` runs a module's current source; pinned by a case that makes a same-size mutation of a `veri/` module with its mtime pinned, runs `make unit`, reverts with the same mtime and reads the reverted value from a fresh `python3`, red against PR #1479's head bfadedcd7 ⟦added⟧ ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 187 | 42 | 84 | 17772 | 2299702 | 314892 | 2.66 | 1163 | unknown | 1/5 | nothing-structural |  |  | full |
| A cache entry never holds bytecode for source other than the content its key names: a `.py` under test changed during the leg and then restored leaves the next two runs on the unchanged tree passing as on `main`, and a truncated or empty entry is not reused (the run passes and the entry is replaced); pinned by a case red against PR #1479's head bfadedcd7 ⟦added⟧ ⟦criterion 6⟧ | 11 | 5 | 0 | 0 | 0 | 0 | 405 | 78 | 156 | 40689 | 4309694 | 608586 | 5.32 | 2481 | unknown | 1/5 | nothing-structural |  |  | full |
| The suites that exercise the cache never read, write or evict entries under the real cache root (`~/.veri-tools/pycache`, or `$VERI_PYCACHE_ROOT` as the caller set it) — its listing is the same before and after `make test` apart from the run's own entry — and CLAUDE.md's description of the cache claims only what these cases pin ⟦added⟧ ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 276 | 47 | 94 | 24863 | 2784118 | 332270 | 3.03 | 1306 | unknown | 0/5 | nothing-left |  |  | full |
| A pytest leg killed partway (SIGINT, SIGTERM or SIGKILL to the leg's process group) leaves no `.pyc` in the worktree, and a fresh `python3` under `PYTHONDONTWRITEBYTECODE=1` after a same-size, same-mtime revert runs the reverted source; pinned by a case red against PR #1479's head 02fb31a0a (which left 144 `.pyc` after a kill) ⟦added⟧ ⟦criterion 8⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 242 | 47 | 92 | 28827 | 2567612 | 376141 | 2.05 | 2075 | 1/2 | 0/5 | nothing-left |  |  | full |
| A `tests/py` file mutated before collection and restored during a leg (same size, same mtime) leaves the next two runs on the unchanged tree passing, its assertion-rewrite bytecode included; and dropping the re-hash check before the copy-back turns a case red ⟦added⟧ ⟦criterion 9⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 156 | 23 | 46 | 19589 | 1578829 | 130494 | 0.88 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: no-sigpipe-pipelines.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ that declares pipefail ends a pipeline in a reader that leaves before EOF (pytest-leg.test.sh:1177 pipes printf into head -n 1) ⟦suite-repair⟧ ⟦criterion 9⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 29 | 54 | 7649 | 1245949 | 275852 | 1.30 | 1288 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Under make unit and make test, a pytest case run by the leg finds the stdlib's and installed packages' bytecode resolved to their own existing __pycache__ (importlib.util.cache_from_source on a stdlib module and on pytest's own module names a path beside that module's source), never a per-run empty cache directory ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 121 | 0.61 |
| Two consecutive runs of the pytest leg over the same tree leave one cache directory, under a root the caller can point elsewhere, holding the bytecode of veri's modules and of the test files (pytest's assertion-rewrite output included), and the second run reuses that directory rather than starting an empty one; the directory's name changes when the content of any .py under skills/tdd/scripts changes ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 144 | 0.68 |
| After runs over more distinct contents than the bound, the cache root holds no more than a bounded number of cache directories, the oldest pruned and the current one kept ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 139 | 0.66 |
| A VERI_PYCACHE_KEEP that is not a whole number of at least 1 makes make unit and make test refuse with exit 2 before any suite runs, naming the variable and the value, so the prune can never remove the current run's own cache directory ⟦added⟧ ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 431 | 0.84 |
| With PYTHONDONTWRITEBYTECODE set in the caller's environment, a run of the pytest leg still writes its cache directory ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 139 | 0.70 |
| After `make unit` or `make test` the worktree holds no `.pyc` the run did not find there, and a fresh `python3` started afterwards outside the leg under `PYTHONDONTWRITEBYTECODE=1` runs a module's current source; pinned by a case that makes a same-size mutation of a `veri/` module with its mtime pinned, runs `make unit`, reverts with the same mtime and reads the reverted value from a fresh `python3`, red against PR #1479's head bfadedcd7 ⟦added⟧ ⟦criterion 5⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 296 | 0.79 |
| A cache entry never holds bytecode for source other than the content its key names: a `.py` under test changed during the leg and then restored leaves the next two runs on the unchanged tree passing as on `main`, and a truncated or empty entry is not reused (the run passes and the entry is replaced); pinned by a case red against PR #1479's head bfadedcd7 ⟦added⟧ ⟦criterion 6⟧ | 2 | 1/5 | nothing-structural | PASS | 0 | 392 | 1.46 |
| The suites that exercise the cache never read, write or evict entries under the real cache root (`~/.veri-tools/pycache`, or `$VERI_PYCACHE_ROOT` as the caller set it) — its listing is the same before and after `make test` apart from the run's own entry — and CLAUDE.md's description of the cache claims only what these cases pin ⟦added⟧ ⟦criterion 7⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 180 | 0.71 |
| A pytest leg killed partway (SIGINT, SIGTERM or SIGKILL to the leg's process group) leaves no `.pyc` in the worktree, and a fresh `python3` under `PYTHONDONTWRITEBYTECODE=1` after a same-size, same-mtime revert runs the reverted source; pinned by a case red against PR #1479's head 02fb31a0a (which left 144 `.pyc` after a kill) ⟦added⟧ ⟦criterion 8⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 186 | 0.42 |
| fix the full-suite failure: no-sigpipe-pipelines.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ that declares pipefail ends a pipeline in a reader that leaves before EOF (pytest-leg.test.sh:1177 pipes printf into head -n 1) ⟦suite-repair⟧ ⟦criterion 9⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 193 | 0.42 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 49 | 117 | 0 | 0 | 98 | 0 | 31 | 34 | 35 | 150 | 36 | 38 | 41 | 42 | 42 | 0 | 147 | 43 | 46 | 111 | 0 | 139 | 0 | 0 | 46 | 46 | 125 | 41 | 43 | 42 | 10 | 67 | 45 | 49 | 0 | 118 | 38 | 0 | 36 | 1 | 18 | 1 | 1 | 2 | 11 | 2 | 11 | 2 | 1 | 44 | 5 | 2 | 4 | 0 | 2 | 43 | 49 | 47 | 0 | 142 | 0 | 15 | 10 | 4 | 9 | 0 | 2 | 1 | 59 | 58 | 141 | 0 | 156 | 0 | 165 | 69 | 69 | 76 | 141 | 136 | 0 | 0 | 1 | 82 | 76 | 165 | 101 | 103 | 105 | 105 | 105 | 8 | 104 |
| fast | 66 | 63 | 61 | 60 | 61 | 62 | 71 | 65 | 65 | 62 | 71 | 71 | 70 | 64 | 57 | 58 | 55 | 66 | 78 | 61 | 59 | 61 | 63 | 63 | 61 | 65 | 62 | 60 | 63 | 66 | 56 | 56 | 55 | 56 | 55 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 33 | 36 | 36 | 35 | 42 | 43 | 46 | 50 | 50 | 69 | 73 | 100 | 105 | 104 | 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 516 | 1012 | 239106 | 27253599 | 4043272 | 31.45 |
