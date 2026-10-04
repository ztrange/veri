### 📊 Metrics — issue 848

Wall time for the issue: 19193 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 767 s, excluded from it.
Steps done: 16 of 16 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/858.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 15 | 2 | 4 | 1388 | 68561 | 47220 | 0.42 |
| diff | 6 | 3 | 0 | 0 | 3325 | 360 | 81 | 156 | 34389 | 6366724 | 398381 | 5.15 |
| red | 24 | 8 | 1 | 0 | 4306 | 1494 | 269 | 524 | 135898 | 17719624 | 1500428 | 18.27 |
| green | 18 | 8 | 1 | 0 | 4644 | 702 | 172 | 336 | 64380 | 9474480 | 929004 | 10.62 |
| refactor | 16 | 8 | 0 | 0 | 1630 | 352 | 97 | 194 | 33606 | 4992593 | 806200 | 8.12 |
| pin | 6 | 5 | 1 | 0 | 399 | 157 | 35 | 70 | 14986 | 1774806 | 305951 | 3.10 |
| predicate | 4 | 0 | 0 | 0 | 79 | 55 | 16 | 32 | 5284 | 726912 | 184189 | 1.72 |
| structural | 3 | 0 | 0 | 0 | 842 | 138 | 25 | 50 | 10565 | 1347609 | 151594 | 1.69 |
| transform | 3 | 3 | 0 | 0 | 336 | 98 | 20 | 40 | 7241 | 1005903 | 144186 | 1.50 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 39 | 36 | 3 | 0 | 5680 | 1170 | 271 | 536 | 106051 | 14072671 | 1962473 | 20.64 |
| developer | claude-opus-5-5 | 42 | 0 | 0 | 0 | 9901 | 2201 | 446 | 870 | 201686 | 29404541 | 2504680 | 29.96 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 2787 | 4.20 | 0 | 0.00 |
| green | 1265 | 2.22 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 68 | 1.10 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Every existing case in tests/py/test_github.py and tests/unit/github.test.sh that pins the GraphQL-then-REST fallback order, and every other suite whose gh stub answers a twin's call only on the GraphQL route, is changed only to set VERI_GH_DRIVER=auto, and still passes ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 247 | 52 | 100 | 21765 | 4853307 | 190285 | 2.93 | 1969 | unknown | unknown | unknown |  |  | full |
| Python veri/github.py with VERI_GH_DRIVER unset: gh_issue_view, gh_list and gh_json with gh args run only their REST gh api call and no GraphQL gh call; a REST failure raises NoAnswer ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 191 | 49 | 98 | 17459 | 2790641 | 322861 | 3.49 | 634 | unknown | 1/5 | structural-owed |  |  | full |
| Bash lib/github.sh with VERI_GH_DRIVER unset: gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready run only their REST gh api call and no GraphQL gh call; a REST failure returns 2 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 209 | 45 | 88 | 16755 | 2433497 | 314737 | 3.34 | 747 | unknown | 0/5 | nothing-structural |  |  | full |
| Python veri/github.py with VERI_GH_DRIVER=rest: no GraphQL gh command runs whether REST succeeds or fails; gh_issue_view, gh_list and gh_json with gh args answer from REST, and a REST failure raises NoAnswer with gh api's stderr passed through ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 13 | 26 | 6508 | 764635 | 112330 | 1.18 | unknown | unknown | unknown | unknown |  |  | pin |
| Bash lib/github.sh with VERI_GH_DRIVER=rest: no GraphQL gh command runs whether REST succeeds or fails; gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready answer from REST, and a REST failure returns 2 with gh api's stderr passed through ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 83 | 16 | 32 | 9024 | 898696 | 106169 | 1.21 | unknown | unknown | unknown | unknown |  |  | pin |
| Python veri/github.py with VERI_GH_DRIVER=graphql: a GraphQL failure in gh_issue_view, gh_list or gh_json with gh args raises NoAnswer and makes no gh api call; a GraphQL success answers its stdout ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 184 | 43 | 86 | 17189 | 2398907 | 326144 | 3.43 | 394 | unknown | 0/5 | structural-owed |  |  | full |
| Bash lib/github.sh with VERI_GH_DRIVER=graphql: a GraphQL failure in gh_issue_view, gh_list, gh_json with gh args or gh_pr_ready returns 2 and makes no gh api call; a GraphQL success answers its stdout ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 212 | 51 | 100 | 21056 | 2758599 | 313522 | 3.48 | 830 | unknown | 1/5 | structural-owed |  |  | full |
| Python veri/github.py: gh_issue_edit, gh_issue_create, gh_rest_list and gh_json with no gh args run their REST gh api call and no GraphQL call under each of unset, auto, rest and graphql ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 195 | 47 | 92 | 17902 | 2513966 | 312819 | 3.36 | 444 | unknown | 1/5 | structural-owed |  |  | full |
| Bash lib/github.sh: gh_issue_edit, gh_rest_list and gh_json with no gh args run their REST gh api call and no GraphQL call under each of unset, auto, rest and graphql ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 90 | 17 | 34 | 7812 | 965047 | 106746 | 1.20 | unknown | unknown | unknown | unknown |  |  | pin |
| Python veri/github.py with VERI_GH_DRIVER set but empty, or set to an unknown value such as REST or gql: every public function starts no gh process, raises NoAnswer, and prints one stderr line naming VERI_GH_DRIVER and the value; importing the module with a bad value set reads no env var and starts no process ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 202 | 46 | 92 | 17620 | 2513982 | 310904 | 3.34 | 552 | unknown | 0/5 | nothing-structural |  |  | full |
| Bash lib/github.sh with VERI_GH_DRIVER set but empty, or set to an unknown value such as REST or gql: every gh_* function starts no gh process, returns 2, and prints one stderr line naming VERI_GH_DRIVER and the value; solvable-issues.sh exits 2 ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 310 | 68 | 128 | 29604 | 3640941 | 404807 | 4.56 | 1646 | 1/2 | 0/5 | structural-owed |  |  | full |
| With VERI_GH_JSON set, gh_json in veri/github.py and in lib/github.sh answers the fixture file's contents and starts no process under each of unset, auto, rest and graphql ⟦criterion 7⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 271 | 48 | 92 | 25441 | 3295705 | 260171 | 3.25 | unknown | 1/2 | unknown | unknown |  |  | pin |
| With VERI_GH_DRIVER set in the launching environment, a stub claude started through detach-leaf.sh → supervise.sh → run-leaf.sh, and a conductor child started by run-conductor.sh, both observe the same value ⟦criterion 8⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 115 | 26 | 50 | 12193 | 1715551 | 131715 | 1.64 | unknown | unknown | unknown | unknown |  |  | pin |
| hermetic-suites.test.sh pins that the suites give the same result with VERI_GH_DRIVER set to auto, rest or graphql in the caller's environment as with it unset ⟦criterion 9⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 577 | 104 | 206 | 50307 | 7271336 | 518658 | 6.61 | 5009 | 1/2 | 0/5 | nothing-structural |  |  | full |
| skills/tdd/SKILL.md documents VERI_GH_DRIVER beside VERI_GH_JSON — its three values, unset means rest, empty or unknown is exit 2, REST-only operations ignore it, VERI_GH_JSON takes precedence, and a Claude Code cloud session needs nothing set — and the header comments of veri/github.py and lib/github.sh say the same ⟦diff-checked⟧ ⟦criterion 10⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 13 | 24 | 4507 | 613477 | 100995 | 1.02 | 1269 | unknown | unknown | unknown |  |  | full |
| docs/adr/0028-veri-reaches-github-over-rest-through-one-port.md records the decision from the issue's ADR draft, its context, decision and consequences agreeing with what this change implements ⟦diff-checked⟧ ⟦criterion 11⟧ | 12 | 4 | 0 | 0 | 0 | 0 | 363 | 77 | 154 | 31207 | 3980364 | 587070 | 6.12 | 201 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Python veri/github.py with VERI_GH_DRIVER unset: gh_issue_view, gh_list and gh_json with gh args run only their REST gh api call and no GraphQL gh call; a REST failure raises NoAnswer ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 105 | 1.01 |
| Bash lib/github.sh with VERI_GH_DRIVER unset: gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready run only their REST gh api call and no GraphQL gh call; a REST failure returns 2 ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 179 | 0.93 |
| Python veri/github.py with VERI_GH_DRIVER=graphql: a GraphQL failure in gh_issue_view, gh_list or gh_json with gh args raises NoAnswer and makes no gh api call; a GraphQL success answers its stdout ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 96 | 1.01 |
| Bash lib/github.sh with VERI_GH_DRIVER=graphql: a GraphQL failure in gh_issue_view, gh_list, gh_json with gh args or gh_pr_ready returns 2 and makes no gh api call; a GraphQL success answers its stdout ⟦criterion 4⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 303 | 1.02 |
| Python veri/github.py: gh_issue_edit, gh_issue_create, gh_rest_list and gh_json with no gh args run their REST gh api call and no GraphQL call under each of unset, auto, rest and graphql ⟦criterion 5⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 146 | 1.11 |
| Python veri/github.py with VERI_GH_DRIVER set but empty, or set to an unknown value such as REST or gql: every public function starts no gh process, raises NoAnswer, and prints one stderr line naming VERI_GH_DRIVER and the value; importing the module with a bad value set reads no env var and starts no process ⟦criterion 6⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 83 | 0.96 |
| Bash lib/github.sh with VERI_GH_DRIVER set but empty, or set to an unknown value such as REST or gql: every gh_* function starts no gh process, returns 2, and prints one stderr line naming VERI_GH_DRIVER and the value; solvable-issues.sh exits 2 ⟦criterion 6⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 175 | 0.96 |
| hermetic-suites.test.sh pins that the suites give the same result with VERI_GH_DRIVER set to auto, rest or graphql in the caller's environment as with it unset ⟦criterion 9⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 543 | 1.13 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 3/3 | budget-spent |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 12 | 1 | 1 | 6 | 14 | 1 | 1 | 2 | 0 | 0 | 91 | 0 | 0 | 7 | 1 | 39 | 85 | 9 | 0 | 84 | 9 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 102 | 105 | 100 | 98 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 2 | 0 | 1 | 1 | 1 | 2 | 141 | 2 | 1 | 1 | 1 | 90 | 95 | 90 | 91 | 1 | 188 | 92 | 1 | 3 | 86 | 67 | 56 | 57 | 44 | 111 | 119 | 0 | 0 | 213 | 126 | 0 | 207 | 1114 | 87 | 66 | 3 | 57 | 399 | 212 | 2 | 48 | 1 | 2 |
| fast | 39 | 38 | 39 | 37 | 36 | 39 | 37 | 38 | 39 | 41 | 39 | 41 | 38 | 40 | 38 | 41 | 38 | 41 | 41 | 39 | 42 | 40 | 39 | 40 | 39 | 40 | 41 | 40 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 2 | 1 | 69 | 66 | 64 | 115 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 717 | 1406 | 307737 | 43477212 | 4467153 | 50.59 |
