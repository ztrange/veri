### 📊 Metrics — issue 1471

Wall time for the issue: 7555 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1479.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 954 | 12193 | 36934 | 0.16 |
| red | 14 | 5 | 1 | 0 | 1243 | 420 | 92 | 180 | 42382 | 4954090 | 739120 | 6.48 |
| green | 10 | 5 | 0 | 0 | 2566 | 307 | 70 | 136 | 29763 | 3492064 | 487469 | 4.04 |
| refactor | 10 | 5 | 0 | 0 | 974 | 177 | 50 | 98 | 16382 | 2319898 | 468697 | 3.49 |
| pin | 1 | 1 | 0 | 0 | 87 | 13 | 4 | 8 | 1456 | 173401 | 46565 | 0.22 |
| diff | 2 | 1 | 0 | 0 | 295 | 47 | 18 | 34 | 5086 | 883728 | 96308 | 0.78 |
| predicate | 1 | 0 | 0 | 0 | 11 | 6 | 2 | 4 | 480 | 65434 | 41314 | 0.35 |
| structural | 1 | 0 | 0 | 0 | 74 | 18 | 7 | 14 | 1974 | 343190 | 45285 | 0.47 |
| transform | 1 | 1 | 0 | 0 | 81 | 12 | 6 | 10 | 1240 | 223697 | 43345 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 20 | 19 | 1 | 0 | 2562 | 291 | 97 | 186 | 31131 | 4254018 | 897083 | 4.33 |
| developer | claude-opus-5-5 | 21 | 0 | 0 | 0 | 2779 | 717 | 153 | 300 | 68586 | 8213677 | 1107954 | 11.88 |

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

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Under make unit and make test, a pytest case run by the leg finds the stdlib's and installed packages' bytecode resolved to their own existing __pycache__ (importlib.util.cache_from_source on a stdlib module and on pytest's own module names a path beside that module's source), never a per-run empty cache directory ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 121 | 0.61 |
| Two consecutive runs of the pytest leg over the same tree leave one cache directory, under a root the caller can point elsewhere, holding the bytecode of veri's modules and of the test files (pytest's assertion-rewrite output included), and the second run reuses that directory rather than starting an empty one; the directory's name changes when the content of any .py under skills/tdd/scripts changes ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 144 | 0.68 |
| After runs over more distinct contents than the bound, the cache root holds no more than a bounded number of cache directories, the oldest pruned and the current one kept ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 139 | 0.66 |
| A VERI_PYCACHE_KEEP that is not a whole number of at least 1 makes make unit and make test refuse with exit 2 before any suite runs, naming the variable and the value, so the prune can never remove the current run's own cache directory ⟦added⟧ ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 431 | 0.84 |
| With PYTHONDONTWRITEBYTECODE set in the caller's environment, a run of the pytest leg still writes its cache directory ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 139 | 0.70 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 49 | 117 | 0 | 0 | 98 | 0 | 31 | 34 | 35 | 150 | 36 | 38 | 41 | 42 | 42 | 0 | 147 | 43 | 46 | 111 | 0 | 139 | 0 | 0 | 46 | 46 | 125 | 41 | 43 | 42 | 10 | 67 |
| fast | 66 | 63 | 61 | 60 | 61 | 62 | 71 | 65 | 65 | 62 | 71 | 71 | 70 | 64 | 57 | 58 | 55 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 33 | 36 | 36 | 35 | 42 | 43 | 46 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 250 | 486 | 99717 | 12467695 | 2005037 | 16.20 |
