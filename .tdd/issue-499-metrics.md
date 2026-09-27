### 📊 Metrics — issue 499

Wall time for the issue: 11712 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 15 of 15 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/519.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 25 | 21 | 3 | 6 | 1968 | 105200 | 38179 | 0.37 |
| red | 30 | 15 | 0 | 0 | 1254 | 1027 | 228 | 446 | 96611 | 10675351 | 1340049 | 14.79 |
| green | 44 | 15 | 7 | 0 | 8082 | 1660 | 413 | 810 | 162791 | 19224317 | 1775043 | 21.30 |
| refactor | 30 | 15 | 0 | 0 | 1139 | 629 | 175 | 348 | 59220 | 7507004 | 1228094 | 12.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 6337 | 13.94 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| capture-spec.sh appends a `## Refactor` section naming the refactor run kind when the issue carries the `refactor` label, and emits no such section for an issue without it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 206 | 46 | 88 | 19756 | 2009644 | 251707 | 2.81 | 345 | unknown | 2/5 | structural-owed |
| build-develop-prompt.sh accepts the `cover` and `transform` phases and prints a prompt for each from its own template, while an unknown phase is still refused with exit 2 and no stdout ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 206 | 50 | 96 | 18780 | 2387095 | 285321 | 3.14 | 321 | unknown | 0/5 | nothing-left |
| build-verify-prompt.sh accepts a `transform` phase that takes the step's predicate record in the test-path slot and a hex base sha, and prints a prompt telling the verifier to judge `git diff <base-sha>..HEAD` rather than the files a green commit touched, while an unknown phase is still refused with exit 2 ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 191 | 49 | 96 | 18669 | 2290929 | 264517 | 2.95 | 376 | unknown | 0/5 | nothing-left |
| build-verify-prompt.sh plan, given a spec carrying the `## Refactor` section, tells the verifier to REJECT a plan whose steps do not each name one refactoring and state its smell as a runnable shell predicate, and a spec without that section gets no such instruction ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 288 | 65 | 130 | 28273 | 3075569 | 356323 | 4.03 | 1035 | 1/2 | 0/5 | nothing-left |
| SKILL.md tells a refactor-kind run to plan each step as one named refactoring whose criterion is a shell predicate false before the step and true after it ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 49 | 96 | 19293 | 2265844 | 267442 | 2.98 | 982 | unknown | 0/5 | nothing-left |
| cover-outcome.sh reads a cover leaf's report and exits 0 printing the catching test on `COVERED: yes` with a `CAUGHT_BY:` line, exits 1 on `COVERED: no`, and exits 2 on a report with neither ⟦criterion 4⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 246 | 59 | 118 | 24838 | 2749818 | 307423 | 3.51 | 1090 | 1/2 | 0/5 | structural-owed |
| the develop-cover template instructs the leaf to mutate the code the step will move, run the suite, expect red, restore the edit, prove the tree unchanged, and end with `COVERED:` and `CAUGHT_BY:` lines; SKILL.md refuses to continue past Cover when `git status --porcelain` is non-empty afterwards ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 247 | 66 | 124 | 24155 | 3095155 | 277401 | 3.32 | 580 | unknown | 1/5 | structural-owed |
| classify-bail.sh classifies the `uncovered` cause as `process` ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 118 | 39 | 76 | 10784 | 1597030 | 229430 | 2.37 | 198 | unknown | 0/5 | nothing-structural |
| a coverage-blocker script files an unlabelled coverage issue for the refactor issue and adds that new issue under the refactor issue's `## Blocked by` heading, replacing a `None` line, so solvable-issues.sh no longer lists the refactor issue ⟦criterion 5⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 392 | 85 | 168 | 38552 | 4036703 | 416394 | 4.91 | 1761 | 2/2 | 2/5 | structural-owed |
| coverage-blocker.sh blocks the refactor issue on the new coverage issue when its `## Blocked by` section already lists blockers (no `None` line), appending the new issue there ⟦added⟧ ⟦criterion 5⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 276 | 67 | 134 | 26150 | 2966846 | 327305 | 3.74 | 1345 | 2/2 | 1/5 | nothing-structural |
| SKILL.md's Cover step on `COVERED: no` bails with cause `uncovered`, narrates the remedy (find a seam, surround the behaviour) and runs the coverage-blocker script ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 189 | 49 | 98 | 17774 | 2320552 | 266884 | 2.96 | 506 | unknown | 1/5 | nothing-structural |
| transform-touches-tests.sh exits 1 naming the file when any commit in `<base-sha>..HEAD` changes a test file, and exits 0 when none does ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 253 | 59 | 118 | 24192 | 2695342 | 337826 | 3.73 | 1424 | 1/2 | 0/5 | nothing-structural |
| transform-touches-tests.sh exits 2 with a diagnostic, never 0, when `<base-sha>` does not resolve to a commit ⟦added⟧ ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 131 | 37 | 74 | 11815 | 1552893 | 231710 | 2.40 | 230 | unknown | 0/5 | nothing-structural |
| SKILL.md's refactor-kind cycle runs Cover → Transform → Verify, rejects a transform whose commits touch a test file via transform-touches-tests.sh, and abandons a step by resetting to its base sha ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 181 | 47 | 90 | 17311 | 2110826 | 267695 | 2.91 | 510 | unknown | 0/5 | nothing-structural |
| SKILL.md's Draft PR step titles a run on an issue labelled `refactor` with the `refactor:` prefix, beside `fix:` and `feat:` ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 192 | 49 | 98 | 18280 | 2252426 | 255808 | 2.86 | 496 | unknown | 0/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 6 | 0 | 1 | 0 | 0 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 74 | 3 | 3 | 2 | 3 | 3 | 3 | 115 | 0 | 3 | 0 | 1 | 0 | 105 | 168 | 167 | 0 | 165 | 1 | 0 | 0 | 82 | 44 | 0 | 82 | 0 | 83 | 2 | 2 | 0 | 106 | 0 | 106 | 2 | 1 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 82 | 0 | 78 | 0 | 84 | 0 | 84 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 2 | 2 | 1 | 0 | 43 | 0 | 1 | 0 | 1 | 2 | 2 | 0 | 106 | 0 | 107 | 3 | 2 | 0 | 0 | 2 | 0 | 83 | 84 | 0 | 1 | 0 | 2 | 1 | 8 | 1 | 3 | 3 | 108 | 0 | 108 | 4 | 3 | 4 | 0 | 89 | 0 | 109 | 4 |
| fast | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 4 | 3 | 3 | 4 | 4 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 4 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 3 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 432 | 435 | 438 | 439 | 435 | 436 | 439 | 440 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 819 | 1610 | 320590 | 37511872 | 4381365 | 48.97 |
