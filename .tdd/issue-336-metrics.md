### 📊 Metrics — issue 336

Wall time for the issue: 5596 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/350.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 12 | 5 | 0 | 0 | 442 | 376 | 62 | 118 | 38447 | 2497619 | 512835 | 7.34 |
| green | 10 | 5 | 0 | 0 | 2226 | 270 | 77 | 152 | 25347 | 3339710 | 392157 | 6.23 |
| refactor | 10 | 5 | 0 | 0 | 1062 | 201 | 55 | 108 | 18611 | 2188971 | 378779 | 5.35 |
| pin | 2 | 2 | 0 | 0 | 55 | 42 | 11 | 22 | 4102 | 446855 | 81341 | 1.14 |

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
| `make -n unit` lists only suites matching `skills/tdd/scripts/tests/unit/*.test.sh` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 140 | 32 | 64 | 13076 | 1343950 | 237139 | 3.37 | 845 | unknown | 0/5 | nothing-left |
| `make -n test` lists suites from both `skills/tdd/scripts/tests/*.test.sh` and `skills/tdd/scripts/tests/unit/*.test.sh`, with no suite listed twice ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 139 | 34 | 66 | 12982 | 1323008 | 225406 | 3.24 | 669 | unknown | 1/5 | nothing-left |
| `make unit` applies the same per-suite count-line check and the same `OFFLINE_BIN` network-block guard (reach log) as `make test` ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 74 | 12 | 24 | 7766 | 549117 | 95588 | 1.42 | unknown | unknown | unknown | unknown |
| `make unit` runs each suite with `LC_ALL=C` and stdin from `/dev/null`, as `make test` does | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 14 | 26 | 6163 | 571350 | 84321 | 1.28 | unknown | unknown | unknown | unknown |
| `make unit` shims `git`, `gh`, `curl` and `python3` to exit nonzero naming themselves, while `make test` does not: a unit fixture calling real `git` fails under `make unit` naming `git`, and passes through `make test`'s recipe, as does a sibling fixture mocking `git` as a shell function ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 178 | 38 | 72 | 17377 | 1558273 | 247549 | 3.69 | 1734 | unknown | 1/5 | nothing-left |
| At least five existing suites move into `skills/tdd/scripts/tests/unit/`, each still passing its own cases, each recording in its header comment its git/python3/server/sleep usage count as the reason it qualifies ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 177 | 45 | 88 | 16895 | 1956497 | 251475 | 3.92 | 934 | unknown | 1/5 | nothing-left |
| CLAUDE.md's "Testing idiom" section states the admission bar (~100 ms/case, no git, network, servers, real waits or nested suites) and names `skills/tdd/scripts/tests/unit/` as the fast tier, pinned by a guard suite in the style of `model-knobs-recorded.test.sh` ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 123 | 30 | 60 | 12248 | 1170960 | 223634 | 3.13 | 701 | unknown | 1/5 | nothing-structural |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 205 | 400 | 86507 | 8473155 | 1365112 | 20.05 |
