### 📊 Metrics — issue 568

Wall time for the issue: 6522 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 23 planned.
Outcome: the run bailed — step-too-big, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 13 | 5 | 0 | 0 | 451 | 325 | 79 | 146 | 35720 | 3028453 | 523514 | 3.06 |
| green | 15 | 4 | 3 | 0 | 4851 | 326 | 113 | 206 | 35419 | 4427043 | 520471 | 3.32 |
| pin | 3 | 3 | 0 | 0 | 57 | 44 | 12 | 22 | 4478 | 379406 | 103267 | 0.53 |
| refactor | 8 | 4 | 0 | 0 | 153 | 81 | 34 | 64 | 8122 | 1151664 | 285506 | 1.45 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 50 | 0.48 |
| green | 3818 | 2.75 | 99 | 0.45 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 33 | 0.36 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A suite fails naming `<file>:<line>` for any `gh issue`, `gh pr` or `gh repo` call left in skills/tdd/SKILL.md or skills/tdd/scripts/*.sh, exempting only the helper's ready-for-review route ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 130 | 33 | 56 | 16026 | 1168711 | 197686 | 1.18 | unknown | unknown | unknown | unknown |  |  | pin |
| main-working-tree.test.sh's copy of the scripts carries lib/github.sh, so solvable-issues.sh run from that copy sees the decoy's live lock and prints 6, as it did before lib/github.sh existed (the full suite is red at baseline: FAIL - a shared lib/main-working-tree.sh defines main_working_tree...) ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 11 | 20 | 4233 | 385415 | 73736 | 0.41 | unknown | unknown | unknown | unknown |  |  | pin |
| solvable-issues.sh under the GraphQL-refusing stub does not count a pull request (a /issues REST item carrying pull_request) as a solvable issue, even when it carries the opt-in label ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 36 | 68 | 9716 | 1392654 | 230593 | 1.30 | unknown | unknown | 0/5 | nothing-left |  |  | full |
| `coverage-blocker.sh` files the coverage issue and edits the refactor issue's body through `gh api` only, with `coverage-blocker.test.sh`'s working-`gh` stub answering REST instead of `issue create` and `issue edit`, and the suite's assertions unchanged. ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 134 | 37 | 68 | 13028 | 1391957 | 229729 | 1.33 | 268 | unknown | 0/5 | nothing-left |  |  | full |
| `tick-issue-criterion.sh` writes the ticked body back through `gh api` only, with `tick-issue-criterion.test.sh`'s stub answering the REST PATCH instead of `issue edit`, and the no-`GH_REPO` and with-`GH_REPO` cases unchanged. ⟦added⟧ ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 153 | 49 | 90 | 15906 | 1819386 | 300030 | 1.72 | 1236 | 1/2 | 0/5 | nothing-left |  |  | full |
| `wait-ci.sh` reads the PR head through `gh api` only, with `wait-ci.test.sh`'s stubs serving the REST pull, and the #544 (missing head exits 2 naming the PR) and #550 (a state-less status row exits 2) cases keeping their behaviour. ⟦added⟧ ⟦criterion 2⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 200 | 61 | 114 | 20933 | 2365728 | 324396 | 1.98 | 4350 | 2/2 | 0/5 | nothing-left |  |  | full |
| coverage-blocker.sh writes nothing to stderr under the GraphQL-refusing stub, the same as against a working gh ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 11 | 22 | 3897 | 462715 | 76588 | 0.44 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| solvable-issues.sh under the GraphQL-refusing stub does not count a pull request (a /issues REST item carrying pull_request) as a solvable issue, even when it carries the opt-in label ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 33 | 0.36 |
| `coverage-blocker.sh` files the coverage issue and edits the refactor issue's body through `gh api` only, with `coverage-blocker.test.sh`'s working-`gh` stub answering REST instead of `issue create` and `issue edit`, and the suite's assertions unchanged. ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.37 |
| `tick-issue-criterion.sh` writes the ticked body back through `gh api` only, with `tick-issue-criterion.test.sh`'s stub answering the REST PATCH instead of `issue edit`, and the no-`GH_REPO` and with-`GH_REPO` cases unchanged. ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 35 | 0.38 |
| `wait-ci.sh` reads the PR head through `gh api` only, with `wait-ci.test.sh`'s stubs serving the REST pull, and the #544 (missing head exits 2 naming the PR) and #550 (a state-less status row exits 2) cases keeping their behaviour. ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 51 | 0.35 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 21 | 3 | 0 | 3 | 3 | 0 | 0 | 7 | 1 | 3 | 26 | 0 | 2 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 23 | 7 | 1 | 1 | 1 |
| fast | 5 | 6 | 5 | 5 | 5 | 6 | 6 | 6 | 6 | 6 | 5 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 3 | 0 | 1 | 1 | 1 | 24 | 21 | 0 | 21 | 1 | 2 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 462 | 501 | 474 | 479 | 474 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 238 | 438 | 83739 | 8986566 | 1432758 | 8.37 |
