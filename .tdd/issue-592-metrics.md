### 📊 Metrics — issue 592

Wall time for the issue: 14623 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 9 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/602.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 12 | 2 | 4 | 1201 | 58360 | 36426 | 0.33 |
| red | 12 | 3 | 0 | 0 | 1907 | 706 | 121 | 234 | 69016 | 6768293 | 664132 | 8.05 |
| green | 10 | 3 | 2 | 0 | 8990 | 544 | 95 | 184 | 39918 | 4713809 | 403005 | 5.26 |
| refactor | 6 | 3 | 0 | 0 | 478 | 149 | 37 | 74 | 14274 | 1706535 | 263706 | 2.74 |
| pin | 6 | 6 | 0 | 0 | 488 | 116 | 30 | 60 | 10975 | 1237454 | 237164 | 2.36 |
| structural | 2 | 0 | 0 | 0 | 235 | 45 | 9 | 18 | 4684 | 379923 | 79433 | 0.81 |
| transform | 1 | 1 | 0 | 0 | 149 | 37 | 7 | 14 | 3499 | 305137 | 40979 | 0.46 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 4344 | 4.02 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With a gh stub that serves a list over three pages on repos/{owner}/{repo}/…?page=N (each page carrying a Link rel="next" pointing at repositories/{id}/…) and refuses any repositories/ path with the proxy's HTTP 403, gh_rest_list prints every item from all three pages and exits 0 ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 427 | 73 | 140 | 33528 | 3520513 | 337530 | 4.08 | 2353 | 1/2 | 1/5 | structural-owed |  |  | full |
| With that same three-page stub, and the gh subcommand route failing, gh_list falls back to REST and prints every item from all three pages and exits 0 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 1 | 0 | 233 | 52 | 104 | 21170 | 2672192 | 292405 | 3.30 | 4980 | unknown | 1/5 | structural-owed |  |  | full |
| With that same stub, invisible-work.sh gives the output it gives against a single-page fixture holding the same issues and PRs ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 114 | 16 | 30 | 11542 | 899389 | 114542 | 1.33 | unknown | unknown | unknown | unknown |  |  | pin |
| With that same stub, workqueue.sh gives the output it gives against a single-page fixture holding the same issues ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 89 | 18 | 34 | 9189 | 890582 | 96283 | 1.13 | unknown | unknown | unknown | unknown |  |  | pin |
| With that same stub, solvable-issues.sh gives the output it gives against a single-page fixture holding the same issues and PRs ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 83 | 14 | 28 | 8479 | 753019 | 99049 | 1.11 | unknown | unknown | unknown | unknown |  |  | pin |
| With that same stub, parallel-conductors.sh gives the output it gives against a single-page fixture holding the same PRs ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 100 | 17 | 32 | 9923 | 854269 | 99457 | 1.17 | unknown | unknown | unknown | unknown |  |  | pin |
| wait-ci.sh reads check-runs spread over more than one page through that stub and reaches the same verdict as with the same check-runs on one page ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 296 | 53 | 106 | 24138 | 2600312 | 328266 | 3.92 | 2772 | 1/2 | 0/5 | nothing-left |  |  | full |
| When a page request after the first fails for a reason other than the proxy refusal (network error, HTTP 5xx), gh_rest_list and gh_list exit 2 ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 14 | 26 | 5493 | 629068 | 91785 | 0.97 | unknown | unknown | unknown | unknown |  |  | pin |
| When a check-runs page request after the first fails for a reason other than the proxy refusal, wait-ci.sh treats it as no answer from GitHub, exactly as it treats a failed single-page read ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 121 | 26 | 52 | 10721 | 1606747 | 108690 | 1.41 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With a gh stub that serves a list over three pages on repos/{owner}/{repo}/…?page=N (each page carrying a Link rel="next" pointing at repositories/{id}/…) and refuses any repositories/ path with the proxy's HTTP 403, gh_rest_list prints every item from all three pages and exits 0 ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 160 | 0.89 |
| With that same three-page stub, and the gh subcommand route failing, gh_list falls back to REST and prints every item from all three pages and exits 0 ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 184 | 0.99 |
| wait-ci.sh reads check-runs spread over more than one page through that stub and reaches the same verdict as with the same check-runs on one page ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 134 | 0.85 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 12 | 0 | 88 | 88 | 87 | 0 | 0 | 0 | 0 | 0 | 0 | 612 | 0 | 1 | 77 | 0 | 101 | 0 | 98 | 0 | 31 | 11 | 9 | 47 | 56 | 55 | 68 | 102 | 104 | 69 | 0 | 69 | 70 | 0 | 167 | 107 |
| fast | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 12 | 13 | 12 | 12 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 31 | 31 | 11 | 11 | 9 | 7 | 50 | 48 | 68 | 71 | 0 | 0 | 69 | 70 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 745 | 876 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 301 | 588 | 143567 | 15169511 | 1724845 | 20.00 |
