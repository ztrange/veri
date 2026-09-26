### 📊 Metrics — issue 238

Wall time for the issue: 5515 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 18 of 18 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 26 | 21 | 2 | 4 | 2067 | 57021 | 36692 | 0.35 |
| red | 39 | 17 | 1 | 0 | 2472 | 1655 | 324 | 616 | 154086 | 15550433 | 1833855 | 20.87 |
| green | 42 | 16 | 5 | 0 | 5800 | 1772 | 389 | 756 | 158673 | 18599904 | 1752596 | 20.92 |
| refactor | 32 | 16 | 0 | 0 | 1809 | 1026 | 242 | 482 | 97044 | 11309403 | 1377540 | 15.23 |
| pin | 3 | 3 | 0 | 0 | 248 | 91 | 23 | 46 | 8429 | 1029152 | 127544 | 1.39 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 676 | 2.91 | 145 | 1.30 |
| green | 3318 | 7.33 | 77 | 0.99 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| develop-green | 0 | 0.00 | 0 | 0.00 |

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
| push-branch.sh given --force-with-lease=<branch>:<sha> pushes the branch under that lease, replacing a remote copy that still points at <sha> and refusing, without replacing it, one that has moved on; called with no argument it pushes exactly as before, and it never pushes with a bare force ⟦added⟧ ⟦criterion 2⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 431 | 84 | 166 | 40268 | 4083916 | 380832 | 4.67 | 1772 | 2/2 | 3/5 | nothing-structural |
| SKILL.md step 4, after a rebase that changed the tree, runs the full test command once on the rebased tip, bails on a red result without readying the PR, and on green pushes with $S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>, never a bare force ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 291 | 69 | 138 | 26167 | 3693179 | 293300 | 3.61 | 800 | unknown | 1/5 | structural-owed |
| SKILL.md step 4 on rebase-onto-default.sh exit 1 launches a develop-rebase leaf through supervise.sh, then a blind verify-rebase through run-verdict.sh, runs the revise loop on REJECT within REVISE_BUDGET, and readies the PR only after a verify-rebase PASS ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 396 | 77 | 148 | 38337 | 4473502 | 343790 | 4.41 | 899 | unknown | 1/5 | nothing-structural |
| SKILL.md step 4 on a rebase not resolved within budget (REBASE: FAILED, revise-exhausted, or a killed leaf) resets the branch to the pre-rebase sha, leaves the PR a draft, and posts a bail comment naming every conflicting file ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 259 | 58 | 112 | 23743 | 2752017 | 285145 | 3.31 | 858 | unknown | 1/5 | nothing-left |
| CLAUDE.md's script and suite counts include rebase-onto-default.sh and its suite | 2 | 1 | 0 | 0 | 0 | 0 | 75 | 20 | 40 | 6688 | 1065012 | 101111 | 1.16 | unknown | unknown | unknown | unknown |
| no-job-spec-kills.test.sh passes on the branch: its exemption for skill-leaf-env.test.sh's kill %1 step-title fixture still matches that line after this branch's three added lines moved it from 972 to 975 | 6 | 3 | 0 | 0 | 0 | 0 | 163 | 40 | 78 | 15692 | 1691474 | 241760 | 2.59 | 259 | unknown | 1/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 87 | 89 | 0 | 78 | 1 | 80 | 1 | 2 | 2 | 1 | 1 | 1 | 2 | 3 | 3 | 2 | 2 | 3 | 3 | 2 | 3 | 3 | 4 | 3 | 4 | 0 | 4 | 5 | 0 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 6 | 6 | 6 | 6 | 7 | 8 | 8 | 7 | 7 | 7 | 7 | 8 | 0 | 7 | 7 | 9 | 3 | 2 | 2 | 2 | 2 | 0 | 0 | 3 | 2 | 0 | 2 | 2 | 2 | 3 | 0 | 26 | 55 | 1 | 9 | 2 | 3 | 57 | 1 | 0 | 0 | 0 | 0 | 38 | 0 | 0 | 1 | 1 | 0 | 0 | 77 | 97 | 1 | 1 | 1 | 1 | 0 | 1 | 7 | 8 | 7 | 8 | 7 | 8 | 8 | 9 | 8 | 0 | 8 | 1 | 1 | 0 | 96 | 97 | 0 | 97 | 96 | 1 | 1 | 1 | 0 | 97 | 100 | 101 | 1 | 1 | 1 | 1 | 0 | 99 | 101 | 98 | 0 | 99 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| fast | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 2 | 2 | 3 | 4 | 0 | 5 | 6 | 7 | 9 | 9 | 9 | 2 | 3 | 58 | 56 | 0 | 1 | 1 | 7 | 7 | 8 | 1 | 1 | 1 | 2 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 399 | 364 | 365 | 369 | 372 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 980 | 1904 | 420299 | 46545913 | 5128227 | 58.75 |
