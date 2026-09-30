### 📊 Metrics — issue 568

Wall time for the issue: 24709 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 14 of 17 planned.
Outcome: the run was stopped — mode at-ledger, at step-done.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 25 | 19 | 3 | 6 | 1787 | 102027 | 35013 | 0.34 |
| red | 35 | 17 | 0 | 0 | 2902 | 1596 | 307 | 598 | 154554 | 16249679 | 1769688 | 20.50 |
| green | 62 | 16 | 15 | 0 | 17029 | 2762 | 605 | 1194 | 247738 | 31872360 | 2432463 | 32.55 |
| refactor | 35 | 15 | 2 | 0 | 3564 | 1101 | 260 | 512 | 104845 | 12577092 | 1564375 | 17.13 |
| exhausted | 1 | 0 | 0 | 0 | 33 | 27 | 7 | 14 | 2440 | 322997 | 46283 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 270 | 2.69 |
| green | 14396 | 26.03 | 2814 | 6.06 |
| refactor | 2444 | 3.81 | 498 | 1.39 |
| exhausted | 0 | 0.00 | 33 | 0.48 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A helper sourced from skills/tdd/scripts/lib/ marks a draft PR ready for review through the ordinary `gh pr ready` route when the `gh` on PATH answers GraphQL ⟦criterion 3⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 260 | 62 | 122 | 24228 | 2648650 | 383504 | 4.08 | 1536 | 2/2 | 1/5 | nothing-structural |  |  | full |
| With a `gh` stub that refuses every `issue`/`pr`/`repo` subcommand and `api graphql` with the GraphQL-403 message, the helper's ready-for-review marks the PR ready by calling `pulls/{n}/ccr/ready_for_review` over `gh api` ⟦criterion 3⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 282 | 65 | 132 | 24002 | 3056458 | 307528 | 3.99 | 1825 | 2/2 | 1/5 | nothing-structural |  |  | full |
| The helper's ready-for-review returns exit 2 when GitHub fails for a reason other than the GraphQL refusal (network error, 404, 5xx), on either route ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 144 | 41 | 82 | 13824 | 1845681 | 249026 | 2.64 | 253 | unknown | 1/5 | structural-owed |  |  | full |
| capture-spec.sh prints the same spec and exit code under the GraphQL-refusing stub as it does today against a working `gh`, reading the issue over REST ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 344 | 69 | 136 | 29942 | 3479931 | 295491 | 4.22 | 1407 | 1/2 | 1/5 | structural-owed |  |  | full |
| solvable-issues.sh prints the same issue numbers and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 439 | 88 | 174 | 42605 | 4485725 | 423499 | 5.14 | unknown | 2/2 | unknown | unknown |  | exhausted | full |
| solvable-issues.sh, run with no arguments under the GraphQL-refusing gh stub (which answers only `gh api` REST calls under `repos/{owner}/{repo}/`), prints the same issue numbers and exit code as it does against a working `gh` ⟦added⟧ ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 504 | 81 | 162 | 39053 | 4374790 | 400626 | 5.62 | 2180 | 2/2 | 0/5 | structural-owed |  |  | full |
| solvable-issues.sh --repo owner/name, run under the GraphQL-refusing gh stub, reads that named repository's issues and pull requests over REST (the stub answers only `repos/owner/name/...` paths) and prints the same issue numbers and exit code as it does against a working `gh` ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 196 | 50 | 96 | 17589 | 2366606 | 275547 | 3.03 | 416 | unknown | 1/5 | structural-owed |  |  | full |
| solvable-issues.sh writes nothing to stderr under the GraphQL-refusing gh stub, the same as against a working `gh`: the GraphQL-403 refusal message is not passed through to the caller ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 196 | 51 | 102 | 19004 | 2509116 | 274477 | 3.08 | 520 | unknown | 1/5 | structural-owed |  |  | full |
| workqueue.sh produces the same stdout and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 338 | 69 | 134 | 32477 | 3482113 | 358680 | 4.22 | 1383 | 1/2 | 1/5 | structural-owed |  |  | full |
| tick-issue-criterion.sh ticks the issue body's criterion and exits as today under the GraphQL-refusing stub, reading and writing the body over REST ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 316 | 64 | 128 | 29940 | 3185736 | 336024 | 3.92 | 1367 | 1/2 | 1/5 | structural-owed |  |  | full |
| coverage-blocker.sh files the coverage issue and records the block, with the same stdout and exit code, under the GraphQL-refusing stub ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 283 | 61 | 120 | 27412 | 2938685 | 333157 | 3.80 | 1251 | 1/2 | 0/5 | structural-owed |  |  | full |
| parallel-conductors.sh produces the same stdout and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 411 | 96 | 188 | 39566 | 4976489 | 422408 | 5.17 | 2833 | 2/2 | 0/5 | structural-owed |  |  | full |
| wait-ci.sh reads a PR's head sha and check state and exits 0/1/2/3 as today under the GraphQL-refusing stub ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 222 | 50 | 96 | 22046 | 2400438 | 288539 | 3.23 | 947 | unknown | 2/5 | structural-owed |  |  | full |
| invisible-work.sh produces the same stdout and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 403 | 93 | 180 | 39165 | 4752527 | 429497 | 5.17 | 2485 | 2/2 | 1/5 | structural-owed |  |  | full |
| Each converted script still exits 2, never 1, when its REST call to GitHub fails for a reason other than the GraphQL refusal (network error, 404, 5xx) ⟦criterion 5⟧ | 12 | 5 | 0 | 0 | 0 | 0 | 692 | 144 | 280 | 64050 | 7847845 | 628251 | 7.88 | 2467 | 1/2 | 1/5 | structural-owed |  |  | full |
| SKILL.md's steps that read the default branch, read or comment on the issue, and create, view, edit, ready or comment on the PR do it through the helper or `gh api`, and the `skill-*` suites pinning those steps still pass ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 456 | 95 | 186 | 44674 | 6671338 | 406555 | 5.48 | unknown | unknown | 3/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A helper sourced from skills/tdd/scripts/lib/ marks a draft PR ready for review through the ordinary `gh pr ready` route when the `gh` on PATH answers GraphQL ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 2 | 1251 | 2.36 |
| With a `gh` stub that refuses every `issue`/`pr`/`repo` subcommand and `api graphql` with the GraphQL-403 message, the helper's ready-for-review marks the PR ready by calling `pulls/{n}/ccr/ready_for_review` over `gh api` ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 94 | 0.89 |
| The helper's ready-for-review returns exit 2 when GitHub fails for a reason other than the GraphQL refusal (network error, 404, 5xx), on either route ⟦criterion 5⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 58 | 0.83 |
| capture-spec.sh prints the same spec and exit code under the GraphQL-refusing stub as it does today against a working `gh`, reading the issue over REST ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 88 | 1.00 |
| solvable-issues.sh, run with no arguments under the GraphQL-refusing gh stub (which answers only `gh api` REST calls under `repos/{owner}/{repo}/`), prints the same issue numbers and exit code as it does against a working `gh` ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 85 | 1.02 |
| solvable-issues.sh --repo owner/name, run under the GraphQL-refusing gh stub, reads that named repository's issues and pull requests over REST (the stub answers only `repos/owner/name/...` paths) and prints the same issue numbers and exit code as it does against a working `gh` ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 108 | 1.00 |
| solvable-issues.sh writes nothing to stderr under the GraphQL-refusing gh stub, the same as against a working `gh`: the GraphQL-403 refusal message is not passed through to the caller ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 107 | 1.04 |
| workqueue.sh produces the same stdout and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 132 | 1.08 |
| tick-issue-criterion.sh ticks the issue body's criterion and exits as today under the GraphQL-refusing stub, reading and writing the body over REST ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 96 | 0.94 |
| coverage-blocker.sh files the coverage issue and records the block, with the same stdout and exit code, under the GraphQL-refusing stub ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 88 | 0.99 |
| parallel-conductors.sh produces the same stdout and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 164 | 0.91 |
| wait-ci.sh reads a PR's head sha and check state and exits 0/1/2/3 as today under the GraphQL-refusing stub ⟦criterion 1⟧ | 1 | 2/5 | structural-owed | PASS | 0 | 292 | 1.00 |
| invisible-work.sh produces the same stdout and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 156 | 1.00 |
| Each converted script still exits 2, never 1, when its REST call to GitHub fails for a reason other than the GraphQL refusal (network error, 404, 5xx) ⟦criterion 5⟧ | 2 | 1/4 | structural-owed | PASS | 0 | 347 | 1.67 |
| Each converted script still exits 2, never 1, when its REST call to GitHub fails for a reason other than the GraphQL refusal (network error, 404, 5xx) ⟦criterion 5⟧ | 1 | 1/5 | structural-owed |  | 0 | 0 | 0.00 |
| SKILL.md's steps that read the default branch, read or comment on the issue, and create, view, edit, ready or comment on the PR do it through the helper or `gh api`, and the `skill-*` suites pinning those steps still pass ⟦criterion 4⟧ | 1 | 3/5 | structural-owed | PASS | 0 | 498 | 1.39 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 0 | 1 | 0 | 189 | 190 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 5 | 1 | 1 | 5 | 4 | 5 | 5 | 0 | 118 | 65 | 6 | 4 | 5 | 5 | 4 | 101 | 4 | 5 | 0 | 5 | 5 | 5 | 5 | 51 | 0 | 5 | 5 | 5 | 0 | 6 | 5 | 0 | 66 | 1 | 103 | 6 | 5 | 7 | 7 | 8 | 19 | 0 | 57 | 15 | 0 | 0 | 15 | 0 | 1 | 0 | 56 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 41 | 43 | 42 | 46 | 43 | 45 | 42 | 43 | 48 | 50 | 52 | 53 | 50 | 50 | 52 | 51 | 20 | 20 | 19 | 20 | 20 | 19 | 30 | 22 | 22 | 23 | 23 | 0 | 78 | 83 | 24 | 24 | 24 | 0 | 0 | 30 | 62 | 86 | 23 | 24 | 1 | 3 | 3 | 0 | 102 | 0 | 129 | 130 | 125 | 123 | 3 |
| fast | 10 | 10 | 9 | 10 | 10 | 9 | 9 | 11 | 9 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 9 | 9 | 10 | 9 | 10 | 9 | 10 | 10 | 10 | 10 | 9 | 9 | 10 | 10 | 9 | 9 | 10 | 9 | 10 | 9 | 10 | 11 | 11 | 11 | 12 | 12 | 11 | 11 | 11 | 11 | 10 | 10 | 10 | 11 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 11 | 11 | 11 | 10 | 11 | 10 | 10 | 11 | 10 | 10 | 10 | 11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 5 | 5 | 4 | 5 | 0 | 5 | 5 | 5 | 7 | 8 | 0 | 1 | 1 | 1 | 43 | 42 | 42 | 52 | 20 | 20 | 21 | 24 | 24 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 669 | 658 | 669 | 659 | 658 | 659 | 647 | 649 | 651 | 810 | 805 | 697 | 690 | 714 | 714 | 716 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 1182 | 2324 | 511364 | 61124155 | 5847822 | 71.00 |
