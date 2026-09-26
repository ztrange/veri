### 📊 Metrics — issue 238

Wall time for the issue: unknown s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 12 of 16 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 26 | 21 | 2 | 4 | 2067 | 57021 | 36692 | 0.35 |
| red | 28 | 12 | 1 | 0 | 1917 | 1185 | 221 | 418 | 110473 | 10296168 | 1283846 | 14.54 |
| green | 28 | 11 | 3 | 0 | 2867 | 1014 | 236 | 454 | 88631 | 10544899 | 1152947 | 13.11 |
| refactor | 22 | 11 | 0 | 0 | 1033 | 664 | 158 | 316 | 62174 | 7216339 | 923623 | 10.08 |
| pin | 2 | 2 | 0 | 0 | 216 | 66 | 15 | 30 | 6059 | 672386 | 85181 | 0.94 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 676 | 2.91 | 145 | 1.30 |
| green | 1494 | 3.47 | 77 | 0.99 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| rebase-onto-default.sh, run in a worktree whose branch already contains origin/<default>, exits 3 with empty stdout and leaves HEAD and the working tree unchanged ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 330 | 61 | 118 | 24754 | 2716902 | 342743 | 3.78 | 1310 | 1/2 | 0/5 | nothing-left |
| rebase-onto-default.sh, run on a branch behind origin/<default> with no conflict, rebases onto it, exits 0, prints the pre-rebase sha and the onto sha, and leaves HEAD containing origin/<default> with the branch's own commits on top ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 230 | 55 | 106 | 21292 | 2394357 | 293256 | 3.25 | 729 | 1/2 | 1/5 | nothing-left |
| rebase-onto-default.sh on a rebase that conflicts aborts it, exits 1, leaves HEAD at the pre-rebase sha with a clean tree and no rebase in progress, and prints the conflicting files one per line ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 152 | 34 | 66 | 14682 | 1417128 | 245186 | 2.54 | 270 | unknown | 2/5 | nothing-left |
| rebase-onto-default.sh exits 2, not 1, with nothing on stdout and HEAD unchanged when git rebase fails for a reason other than a conflict, such as a dirty working tree ⟦added⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 37 | 74 | 14697 | 1595294 | 242322 | 2.55 | 269 | unknown | 0/5 | nothing-left |
| rebase-onto-default.sh, in a repo configured with rebase.backend=apply, still aborts a conflicted rebase, exits 1 and prints the conflicting files, leaving no rebase in progress ⟦added⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 225 | 47 | 92 | 17868 | 2106677 | 251197 | 2.79 | 375 | unknown | 3/5 | nothing-left |
| rebase-onto-default.sh exits 2 with nothing on stdout when origin/<default> cannot be fetched or named, and never rebases onto a stale local branch ⟦criterion 1⟧ | 14 | 6 | 1 | 0 | 0 | 0 | 543 | 112 | 214 | 49682 | 4941787 | 603873 | 6.81 | 1279 | 1/2 | 4/5 | nothing-left |
| rebase-onto-default.sh exits 2 with nothing on stdout and HEAD unchanged when, after a successful fetch, origin/HEAD still names no branch ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 91 | 17 | 32 | 8586 | 758636 | 92074 | 1.06 | unknown | unknown | unknown | unknown |
| build-develop-prompt.sh rebase renders prompts/develop-rebase.md naming the onto sha, the pre-rebase sha, every conflicting file and the test command, tells the leaf to resolve by rebasing onto the onto sha and to leave the ledger's ticks and marks untouched, ends with a REBASE: RESOLVED | FAILED report line, and exits 2 with no stdout on a missing argument ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 248 | 53 | 104 | 23127 | 2600475 | 281414 | 3.23 | 343 | unknown | 1/5 | structural-owed |
| build-verify-prompt.sh rebase <spec-file> <onto-sha> <pre-rebase-sha> renders a blind verify-rebase prompt from the spec and the two shas alone, telling the verifier to run the full test command on HEAD and to judge that both the branch's changes and the default branch's changes survive the resolution; either sha that is not ^[0-9a-f]{7,40}$ exits 2 with no stdout ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 227 | 50 | 96 | 22472 | 2315335 | 271543 | 3.09 | 417 | unknown | 1/5 | nothing-structural |
| verify.sh and run-verdict.sh accept the rebase phase and return the verdict of a verify-rebase leaf launched through supervise.sh under the name verify-rebase: 0 PASS, 1 REJECT, 2 malformed ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 96 | 21 | 40 | 9419 | 1143786 | 106088 | 1.27 | unknown | unknown | unknown | unknown |
| classify-bail.sh rebase-unresolved prints process and exits 0 ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 136 | 40 | 80 | 11963 | 1694645 | 231249 | 2.43 | 251 | unknown | 0/5 | nothing-left |
| SKILL.md step 4 runs rebase-onto-default.sh after the dirty-tree and pending-refactor check and before the done mark, metrics commit and gh pr ready; exit 3 continues unchanged, exit 2 bails with no-verdict ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 298 | 66 | 126 | 30657 | 3217684 | 289131 | 3.57 | 566 | unknown | 2/5 | nothing-left |
| SKILL.md step 4, after a rebase that changed the tree, runs the full test command once on the rebased tip, bails on a red result without readying the PR, and on green pushes with --force-with-lease=<branch>:<pre-rebase-sha>, never a bare force ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 195 | 37 | 70 | 18138 | 1827086 | 195521 | 2.29 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 87 | 89 | 0 | 78 | 1 | 80 | 1 | 2 | 2 | 1 | 1 | 1 | 2 | 3 | 3 | 2 | 2 | 3 | 3 | 2 | 3 | 3 | 4 | 3 | 4 | 0 | 4 | 5 | 0 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 6 | 6 | 6 | 6 | 7 | 8 | 8 | 7 | 7 | 7 | 7 | 8 | 0 | 7 | 7 | 9 | 3 | 2 | 2 | 2 | 2 | 0 | 0 | 3 | 2 | 0 | 2 | 2 | 2 | 3 | 0 | 26 | 55 | 1 | 9 | 2 | 3 | 57 | 1 | 0 | 0 | 0 | 0 | 38 | 0 | 0 | 1 | 1 | 0 | 0 | 77 | 97 | 1 | 1 | 1 | 1 | 0 | 1 |
| fast | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 2 | 2 | 3 | 4 | 0 | 5 | 6 | 7 | 9 | 9 | 9 | 2 | 3 | 58 | 56 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 399 | 364 | 365 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 632 | 1222 | 269404 | 28786813 | 3482289 | 39.01 |
