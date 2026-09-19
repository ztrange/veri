### 📊 Metrics — issue 340

Wall time for the issue: 5953 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/368.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 11 | 4 | 0 | 0 | 569 | 481 | 74 | 142 | 47751 | 3266004 | 483640 | 7.66 |
| green | 8 | 4 | 0 | 0 | 2078 | 213 | 57 | 110 | 19826 | 2420053 | 322186 | 4.93 |
| refactor | 8 | 4 | 0 | 0 | 985 | 184 | 43 | 84 | 18151 | 1713038 | 305077 | 4.36 |
| pin | 3 | 3 | 0 | 0 | 91 | 56 | 16 | 32 | 4934 | 631257 | 111377 | 1.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `make -n watch` exists as its own `.PHONY` target, separate from `test`, `unit`, and `merge-gates` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 143 | 34 | 66 | 14098 | 1337519 | 225788 | 3.28 | 973 | unknown | 1/5 | nothing-left |
| A malformed `VERI_WATCH_INTERVAL` exits 2 with a diagnostic naming the variable; unset, it defaults to `1` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 162 | 34 | 66 | 15983 | 1350194 | 231989 | 3.39 | 790 | unknown | 1/5 | nothing-left |
| With an injected poll-iteration count and a fabricated file-change signal on a fixture tracked file, the watch loop reruns `make unit` exactly once per detected change and zero times between changes ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 39 | 78 | 19426 | 1795793 | 261488 | 4.00 | 1061 | unknown | 2/5 | structural-owed |
| One poll pass over the tracked files calls its stat wrapper exactly once whatever the number of tracked files (in-process spy), so the polling path is taken rather than the fswatch/entr fallback ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 210 | 38 | 70 | 19339 | 1514281 | 244967 | 3.69 | 832 | unknown | 1/5 | nothing-left |
| The watch loop never runs any make target besides `unit` — a fixture fails if `test`, `merge-gates` or any other target runs ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 99 | 18 | 36 | 9927 | 858032 | 89941 | 1.58 | unknown | unknown | unknown | unknown |
| The Makefile's comment header documents `make watch` as low priority / a developer convenience, in the style of the `profile` and `docs` comments ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 15 | 28 | 6539 | 674110 | 89388 | 1.39 | unknown | unknown | unknown | unknown |
| `watch.test.sh` is run by `make test`'s glob and is not run by `make unit` ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 12 | 24 | 5350 | 500423 | 78719 | 1.17 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 190 | 368 | 90662 | 8030352 | 1222280 | 18.51 |
