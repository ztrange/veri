### 📊 Metrics — issue 763

Wall time for the issue: 4965 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 10 of 14 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/799.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 30 | 24 | 2 | 4 | 2434 | 68100 | 48041 | 0.45 |
| red | 10 | 2 | 0 | 0 | 726 | 412 | 92 | 176 | 42582 | 5347010 | 525411 | 6.13 |
| pin | 5 | 5 | 0 | 0 | 338 | 115 | 26 | 52 | 11687 | 1253938 | 239893 | 2.40 |
| green | 10 | 2 | 3 | 0 | 1830 | 636 | 124 | 246 | 57360 | 7428275 | 526698 | 6.85 |
| refactor | 4 | 2 | 0 | 0 | 230 | 77 | 17 | 34 | 7162 | 787600 | 196299 | 1.87 |
| diff | 6 | 3 | 0 | 0 | 296 | 136 | 32 | 64 | 13681 | 1537039 | 282082 | 2.84 |
| predicate | 2 | 0 | 0 | 0 | 27 | 19 | 6 | 12 | 1659 | 243518 | 87650 | 0.78 |
| structural | 1 | 0 | 0 | 0 | 130 | 29 | 7 | 14 | 2365 | 358318 | 47885 | 0.50 |
| transform | 1 | 1 | 0 | 0 | 82 | 16 | 5 | 10 | 1638 | 226686 | 45161 | 0.44 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 19 | 16 | 3 | 0 | 1882 | 642 | 129 | 258 | 59865 | 6784615 | 907497 | 9.82 |
| developer | claude-opus-5-5 | 21 | 0 | 0 | 0 | 1807 | 822 | 182 | 354 | 80703 | 10465869 | 1091623 | 12.44 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 2796 | 9.77 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 27 | 0.78 |
| structural | 0 | 0.00 | 130 | 0.50 |
| transform | 0 | 0.00 | 82 | 0.44 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a case in tests/invisible-work.test.sh runs invisible-work.sh in a clone whose origin cannot be reached and asserts exit 2, nothing on stdout and stderr's last line exactly `invisible-work.sh: cannot reach origin`, written against the bash script before the port ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 15 | 30 | 5621 | 815256 | 99045 | 1.07 | unknown | unknown | unknown | unknown |  |  | pin |
| a case in tests/invisible-work.test.sh runs invisible-work.sh with a VERI_GH_JSON directory whose issues.json is not JSON and asserts exit 1 and nothing on stdout, written against the bash script before the port ⟦criterion 4⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 60 | 14 | 28 | 5222 | 761942 | 100655 | 1.06 | unknown | unknown | unknown | unknown |  |  | pin |
| invisible-work.sh, run through a symlink to the skill directory and from a subdirectory of the clone, prints the same report on stdout, the same stderr and the same exit code as when run in place from the clone's root (a case in tests/invisible-work.test.sh) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 76 | 20 | 40 | 7704 | 1212908 | 109619 | 1.27 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_invisible_work.py calls veri.invisible_work.main([]) with `subprocess` faked and asserts, every return code inside 0–3: with `git ls-remote --heads origin` exiting 128, return code 2, nothing on stdout, stderr ending in `invisible-work.sh: cannot reach origin`, and no `gh` call; with `git symbolic-ref --short refs/remotes/origin/HEAD` exiting 128, return code 2 and nothing on stdout; invisible-work.sh is removed from migration slice 3's list in tests/unit/missing-argument-exit.test.sh in the same commit, before the port, the slice's other scripts staying ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 351 | 77 | 148 | 32507 | 4270221 | 429624 | 4.94 | 906 | 1/2 | 0/5 | nothing-structural |  |  | full |
| veri.invisible_work.main([]) against faked `git` answers and a VERI_GH_JSON fixture directory prints the remote branches' invariant-2 findings first, in for-each-ref order, then the local branches' invariant-1 findings, in the exact shapes `invariant 2 (no PR): <name> tip <sha> <n> commits ahead[, issue #<n> <STATE>]` and `invariant 1 (not on origin): <name> tip <sha> <n> commits origin lacks[, worktree <path>]`, returning 0, and returns 3 with empty stdout when there is nothing to report; invisible-work.sh becomes a /bin/sh shim exec'ing python3 on veri/invisible_work.py, and every contract case in tests/invisible-work.test.sh passes with its assertions unmodified, the port commit touching that suite only in copy lines and stub libs ⟦criterion 2⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 527 | 98 | 196 | 49533 | 5764162 | 512464 | 6.24 | 1521 | 2/2 | 0/5 | structural-owed |  |  | full |
| tests/py/test_invisible_work.py pins through veri.invisible_work.main how the module reads issues and PRs, faking only `subprocess`, the environment and files under tmp_path: with VERI_GH_JSON set and non-empty it reads issues.json and prs.json from that directory and starts no `gh`; unset or empty it runs `gh issue list --state all --limit 10000 --json number,state` and `gh pr list --state all --limit 10000 --json headRefName,state` byte-identical, and when one fails reads `gh api 'repos/{owner}/{repo}/issues?state=all&per_page=100&page=N'` (and `…/pulls?…`) page by page until a page is exactly `[]`; a failing page returns 2 with nothing on stdout and stderr ending in `invisible-work.sh: cannot read issues and PRs from gh (unauthenticated?)`; a REST answer of `[]` on page 1 gives an empty list, so a `tdd/<n>-` branch reports `issue #<n> unknown` ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 79 | 15 | 28 | 8528 | 805382 | 117550 | 1.27 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_invisible_work.py pins through veri.invisible_work.main the report rules the port keeps: REST's lowercase `open`/`closed` states read as `OPEN`/`CLOSED` and a REST pull's branch is `head.ref`; a branch any PR of any state names is no invariant-2 finding; a local branch is left out when origin carries the same name or a PR for it is MERGED or CLOSED; `tdd/007-x` names issue `#7`; the default branch and a remote `HEAD` are skipped; a worktree path with spaces is kept whole and a local branch no worktree holds names none; arguments are ignored (`main(["--help"])` runs the sweep); and an issues.json that is not JSON, an issue with no `state` or a prs.json that is an object raises rather than returning 2 ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 91 | 20 | 38 | 9676 | 1186952 | 119344 | 1.39 | unknown | unknown | unknown | unknown |  |  | pin |
| invisible-work.sh is a /bin/sh shim that execs python3 on veri/invisible_work.py once per invocation, holding no Python source (no heredoc, no `python3 -c`), keeping the lowercase header line `usage: invisible-work.sh` with no `<…>` outside `[…]`, citing no issue number in its header comments; veri/invisible_work.py has no wrapper turning an uncaught exception into exit 2, ports neither lib/exit-contract.sh nor lib/github.sh, and the port commit comes before any cut ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 12 | 24 | 5906 | 595831 | 97002 | 1.01 | 118 | unknown | unknown | unknown |  |  | full |
| tests/invisible-work.test.sh removes no case — every case running invisible-work.sh reads git's own output from a real clone and origin, or a gh PATH stub, which ADR 0027's survival rule keeps — and gains only the floor's stderr case, the exit-1 case and the symlink case; `refusing_gh_stub` and tests/unit/comment-class.test.sh:263 stay as they are ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 10 | 20 | 3910 | 473427 | 92720 | 0.91 | 145 | unknown | unknown | unknown |  |  | full |
| tests/unit/comment-class.test.sh, tests/unit/exit-contract.test.sh, tests/no-python-in-ported-scripts.test.sh, tests/no-gh-json-argv.test.sh, tests/no-graphql-gh-calls.test.sh and tests/claude-md-counts.test.sh are unchanged by the branch, tests/unit/missing-argument-exit.test.sh is changed only by the removal of invisible-work.sh from migration slice 3's list, and no suite other than tests/invisible-work.test.sh runs invisible-work.sh through its entry point ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 10 | 20 | 3865 | 467781 | 92360 | 0.91 | 77 | unknown | unknown | unknown |  |  | full |
| make test is green, tests/unit/comment-class.test.sh, tests/unit/exit-contract.test.sh, tests/no-python-in-ported-scripts.test.sh, tests/no-gh-json-argv.test.sh, tests/no-graphql-gh-calls.test.sh and tests/claude-md-counts.test.sh among its suites ⟦full-suite⟧ ⟦criterion 5⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 64 | 18 | 36 | 5662 | 828522 | 180696 | 1.72 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tests/py/test_invisible_work.py calls veri.invisible_work.main([]) with `subprocess` faked and asserts, every return code inside 0–3: with `git ls-remote --heads origin` exiting 128, return code 2, nothing on stdout, stderr ending in `invisible-work.sh: cannot reach origin`, and no `gh` call; with `git symbolic-ref --short refs/remotes/origin/HEAD` exiting 128, return code 2 and nothing on stdout; invisible-work.sh is removed from migration slice 3's list in tests/unit/missing-argument-exit.test.sh in the same commit, before the port, the slice's other scripts staying ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 110 | 0.91 |
| veri.invisible_work.main([]) against faked `git` answers and a VERI_GH_JSON fixture directory prints the remote branches' invariant-2 findings first, in for-each-ref order, then the local branches' invariant-1 findings, in the exact shapes `invariant 2 (no PR): <name> tip <sha> <n> commits ahead[, issue #<n> <STATE>]` and `invariant 1 (not on origin): <name> tip <sha> <n> commits origin lacks[, worktree <path>]`, returning 0, and returns 3 with empty stdout when there is nothing to report; invisible-work.sh becomes a /bin/sh shim exec'ing python3 on veri/invisible_work.py, and every contract case in tests/invisible-work.test.sh passes with its assertions unmodified, the port commit touching that suite only in copy lines and stub libs ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 120 | 0.96 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 30 | 32 | 30 | 31 | 1 | 4 | 7 | 32 | 42 | 0 | 3 | 33 | 1 | 4 | 0 | 34 | 0 | 1 | 1 | 2 | 36 | 1 | 34 | 0 | 39 | 39 | 36 | 32 | 31 | 1 | 1 | 31 | 25 | 12 | 61 | 31 | 32 |
| target | 31 | 31 | 32 | 31 | 31 | 34 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 38 | 38 | 37 | 37 | 34 | 32 | 33 | 34 | 36 | 38 | 36 | 32 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 311 | 612 | 140568 | 17250484 | 1999120 | 22.26 |
