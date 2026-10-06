### 📊 Metrics — issue 928

Wall time for the issue: 3980 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 19 of 21 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1028.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 44 | 41 | 1 | 2 | 4451 | 11866 | 44397 | 0.22 |
| red | 21 | 8 | 0 | 0 | 711 | 619 | 123 | 236 | 59310 | 6383217 | 1156820 | 9.99 |
| pin | 5 | 5 | 0 | 0 | 103 | 79 | 22 | 44 | 7578 | 1028772 | 242138 | 1.25 |
| green | 16 | 8 | 0 | 0 | 765 | 430 | 108 | 216 | 40238 | 5808165 | 819914 | 6.79 |
| refactor | 16 | 8 | 0 | 0 | 405 | 236 | 72 | 140 | 20609 | 3378359 | 804432 | 5.89 |
| diff | 6 | 3 | 0 | 0 | 271 | 124 | 33 | 66 | 11957 | 1636325 | 293674 | 2.27 |
| predicate | 1 | 0 | 0 | 0 | 17 | 15 | 2 | 4 | 940 | 64211 | 45661 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 33 | 33 | 0 | 0 | 984 | 556 | 150 | 298 | 54793 | 7063297 | 1614314 | 8.42 |
| developer | claude-opus-5-5 | 33 | 0 | 0 | 0 | 1332 | 988 | 211 | 410 | 90290 | 11247618 | 1792722 | 18.40 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| preserve-attempt.sh, run through a symlink to the skill directory and from a subdirectory of another repository, preserves that repository's worktree to the same ref, with the same tree and exit code, as when run in place — a case in tests/preserve-attempt.test.sh, written against the bash script ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 11 | 20 | 6277 | 520665 | 106416 | 0.88 | unknown | unknown | unknown | unknown |  |  | pin |
| preserve-attempt.sh exits exactly 1, with `preserve-attempt.sh: could not preserve issue 409 step 3 develop-green attempt 1 to refs/veri/attempts/409/3/develop-green-1` as its last stderr line, when an existing refs/veri/attempts/409/3 refuses the ref write — a case in tests/preserve-attempt.test.sh, written against the bash script ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 11 | 22 | 4204 | 589841 | 105589 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| preserve-attempt.sh called with three arguments exits 2 with exactly `usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]` on stderr and nothing on stdout — a case in tests/preserve-attempt.test.sh, written against the bash script ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 11 | 22 | 3517 | 564510 | 99683 | 0.78 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.preserve_attempt.main returns 2 with nothing on stdout and stderr exactly `usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]` for [], ["409", "3", "develop-green"] and ["409", "3", "develop-green", ""], making no git call; preserve-attempt.sh leaves slice 5's list, the slice's other scripts staying: replaces 'migration slice 5 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 146 | 39 | 78 | 13306 | 2083557 | 304130 | 2.50 | 297 | unknown | 0/5 | structural-owed |  |  | full |
| veri.preserve_attempt.main returns 2 when the faked `git commit-tree` exits 128, the scratch directory it made gone afterwards and no `update-ref` call made ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 131 | 31 | 60 | 12674 | 1492230 | 301154 | 2.32 | 243 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.preserve_attempt.main returns exactly 1, nothing on stdout, and stderr ending `preserve-attempt.sh: could not preserve issue 409 step 3 develop-green attempt 1 to refs/veri/attempts/409/3/develop-green-1` when the faked `git update-ref` exits 128, with no `.tdd/attempts` copy made although a mark and both leaf files are given ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 95 | 25 | 50 | 9172 | 1176535 | 299697 | 2.20 | 205 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.preserve_attempt.main over a ledger holding the step argument's text on a prose line, on a `* [ ] ` line and on one `- [ ] ` step that is the ledger's second returns 0 and passes `refs/veri/attempts/409/2/develop-green-1` to the faked `git update-ref`, the index being the one veri.ledger.ledger_steps gives that step, the module importing ledger_steps and spelling no box or step pattern of its own: replaces 'finds the step through lib/ledger.sh's ledger_steps' in skills/tdd/scripts/tests/preserve-attempt.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 156 | 44 | 84 | 14503 | 2338786 | 325007 | 2.71 | 270 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.preserve_attempt.main takes the index of the first ledger step whose text contains the step argument as a literal substring when two steps both contain it, keeps the argument itself when no step matches, when there is no ledger, when the ledger path is a directory, and when reading the ledger raises OSError (printing the plan's stated stderr line), and drops NUL bytes from the ledger before matching ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 156 | 33 | 66 | 15022 | 1755007 | 318331 | 2.55 | 271 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.preserve_attempt.main sanitises the step ref by the plan's locale rule: `a—b ⟦x⟧/c'd` (no ledger) gives the ref part `a---b----x----c-d` with LC_ALL=C and `a-b--x--c-d` with LC_ALL=en_US.UTF-8, LC_ALL beating LC_CTYPE beating LANG, and per byte with none of the three set ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 119 | 30 | 60 | 11417 | 1488758 | 305118 | 2.33 | 234 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.preserve_attempt.main runs git from the top level `git rev-parse --show-toplevel` printed, so `.tdd/` paths are read there when called from a subdirectory; runs `git add -A` and `git write-tree` with GIT_INDEX_FILE set to a path inside a fresh directory that does not exist when `git add` runs, and every other git call without GIT_INDEX_FILE added, every call inheriting the rest of the environment; and passes `-m "attempt: issue <issue> step <raw step> <phase> attempt <attempt>"` to `git commit-tree <tree> -p HEAD` with the raw step argument, never the sanitised ref part ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 11 | 20 | 6044 | 524924 | 111173 | 0.90 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.preserve_attempt.main returns 1 with no `git add` call when the faked `git rev-parse --show-toplevel` exits 128 (printing the plan's stated stderr line), and maps a failing `git add -A` or `git write-tree` as 0–3 kept, anything else 2 — 1 stays 1, 128 becomes 2 — with the scratch directory removed and no later git call ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 145 | 35 | 66 | 12550 | 1744437 | 317320 | 2.50 | 260 | unknown | 1/5 | nothing-structural |  |  | full |
| veri.preserve_attempt.main with a non-empty mark creates `.tdd/attempts` even when neither `.tdd/<phase>.log` nor `.tdd/<phase>.out` exists; copies each that is a regular file to `.tdd/attempts/<step ref>-<phase>-<attempt>-<mark>.<ext>`, overwriting an earlier copy and keeping its mode bits; with an empty fifth argument copies nothing and makes no `.tdd/attempts`; ignores arguments past the fifth; and returns 1 when a copy fails because the destination is a directory holding a directory of the source's name ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 32 | 64 | 14316 | 1653541 | 317634 | 2.51 | 301 | unknown | 1/5 | nothing-structural |  |  | full |
| veri.preserve_attempt.main writes nothing on stdout on any path: preserved, refused arguments, update-ref refused, git failure ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 12 | 24 | 4733 | 665722 | 112052 | 0.91 | unknown | unknown | unknown | unknown |  |  | pin |
| preserve-attempt.sh becomes a /bin/sh shim that execs python3 on "$(dirname "$0")/veri/preserve_attempt.py" once per invocation, as status.sh does, holding no Python source, its header carrying the lowercase `usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]` line and no issue number; veri/preserve_attempt.py gains its `if __name__ == "__main__"` block, has no wrapper turning an uncaught exception into exit 2, and starts no process but git; the commit touches no test suite ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 12 | 24 | 4132 | 614823 | 99402 | 0.79 | 104 | n/a | n/a | n/a |  |  | full |
| tests/preserve-attempt.test.sh differs from the branch point only by the cut of the case at `:198-216` and the three cases this plan adds; tests/supervise.test.sh and tests/verify.test.sh change at most in copy lines; tests/unit/missing-argument-exit.test.sh changes only by preserve-attempt.sh's removal from slice 5's list; and no case in tests/py/test_preserve_attempt.py patches a function of veri.preserve_attempt or veri.ledger ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 9 | 18 | 3366 | 427190 | 99506 | 0.73 | 88 | n/a | n/a | n/a |  |  | full |
| lib/ledger.sh, lib/preserve.sh, lib/exit-contract.sh, supervise.sh, verify.sh, veri/ledger.py, tests/py/test_ledger.py, tests/skill-leaf-env.test.sh, tests/skill-preserve-attempt.test.sh, tests/py/test_comment_class.py, tests/unit/exit-contract.test.sh, tests/unit/scratch-copy-libs.test.sh, tests/unit/pending-mark-literal.test.sh and tests/no-python-in-ported-scripts.test.sh are unchanged by the branch ⟦diff-checked⟧ ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 12 | 24 | 4459 | 594312 | 94766 | 0.75 | 120 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.preserve_attempt.main returns 2 with nothing on stdout and stderr exactly `usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]` for [], ["409", "3", "develop-green"] and ["409", "3", "develop-green", ""], making no git call; preserve-attempt.sh leaves slice 5's list, the slice's other scripts staying: replaces 'migration slice 5 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 40 | 0.66 |
| veri.preserve_attempt.main returns 2 when the faked `git commit-tree` exits 128, the scratch directory it made gone afterwards and no `update-ref` call made ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 45 | 0.68 |
| veri.preserve_attempt.main returns exactly 1, nothing on stdout, and stderr ending `preserve-attempt.sh: could not preserve issue 409 step 3 develop-green attempt 1 to refs/veri/attempts/409/3/develop-green-1` when the faked `git update-ref` exits 128, with no `.tdd/attempts` copy made although a mark and both leaf files are given ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 47 | 0.70 |
| veri.preserve_attempt.main over a ledger holding the step argument's text on a prose line, on a `* [ ] ` line and on one `- [ ] ` step that is the ledger's second returns 0 and passes `refs/veri/attempts/409/2/develop-green-1` to the faked `git update-ref`, the index being the one veri.ledger.ledger_steps gives that step, the module importing ledger_steps and spelling no box or step pattern of its own: replaces 'finds the step through lib/ledger.sh's ledger_steps' in skills/tdd/scripts/tests/preserve-attempt.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 41 | 0.74 |
| veri.preserve_attempt.main takes the index of the first ledger step whose text contains the step argument as a literal substring when two steps both contain it, keeps the argument itself when no step matches, when there is no ledger, when the ledger path is a directory, and when reading the ledger raises OSError (printing the plan's stated stderr line), and drops NUL bytes from the ledger before matching ⟦criterion 7⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 42 | 0.71 |
| veri.preserve_attempt.main sanitises the step ref by the plan's locale rule: `a—b ⟦x⟧/c'd` (no ledger) gives the ref part `a---b----x----c-d` with LC_ALL=C and `a-b--x--c-d` with LC_ALL=en_US.UTF-8, LC_ALL beating LC_CTYPE beating LANG, and per byte with none of the three set ⟦criterion 7⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 51 | 0.75 |
| veri.preserve_attempt.main returns 1 with no `git add` call when the faked `git rev-parse --show-toplevel` exits 128 (printing the plan's stated stderr line), and maps a failing `git add -A` or `git write-tree` as 0–3 kept, anything else 2 — 1 stays 1, 128 becomes 2 — with the scratch directory removed and no later git call ⟦criterion 7⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 81 | 0.86 |
| veri.preserve_attempt.main with a non-empty mark creates `.tdd/attempts` even when neither `.tdd/<phase>.log` nor `.tdd/<phase>.out` exists; copies each that is a regular file to `.tdd/attempts/<step ref>-<phase>-<attempt>-<mark>.<ext>`, overwriting an earlier copy and keeping its mode bits; with an empty fifth argument copies nothing and makes no `.tdd/attempts`; ignores arguments past the fifth; and returns 1 when a copy fails because the destination is a directory holding a directory of the source's name ⟦criterion 7⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 58 | 0.79 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| target | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 2 | 1 | 2 | 1 | 0 | 1 | 1 | 5 | 2 | 0 | 0 | 1 | 2 | 0 | 0 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 2 | 1 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 1 | 0 | 1 | 15 | 2 | 1 | 1 | 0 | 0 | 2 | 2 | 25 | 1 | 2 | 2 | 0 |
| fast | 15 | 15 | 14 | 15 | 15 | 14 | 15 | 14 | 15 | 15 | 14 | 15 | 15 | 15 | 14 | 15 | 14 | 15 | 14 | 15 | 14 | 15 | 14 | 15 | 15 | 15 | 14 | 15 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 361 | 708 | 145083 | 18310915 | 3407036 | 26.82 |
