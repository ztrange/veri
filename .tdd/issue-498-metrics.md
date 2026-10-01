### 📊 Metrics — issue 498

Wall time for the issue: 24270 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 9 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/616.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 14 | 2 | 4 | 1295 | 57900 | 36016 | 0.33 |
| red | 19 | 9 | 0 | 0 | 976 | 644 | 145 | 286 | 56907 | 6920113 | 841837 | 9.26 |
| green | 36 | 8 | 10 | 0 | 14759 | 1705 | 344 | 674 | 148545 | 17049169 | 1289631 | 17.98 |
| exhausted | 1 | 0 | 0 | 0 | 33 | 28 | 6 | 12 | 1857 | 262799 | 42250 | 0.43 |
| refactor | 18 | 8 | 1 | 0 | 2835 | 528 | 124 | 248 | 47906 | 5594676 | 757195 | 8.14 |
| pin | 1 | 1 | 0 | 0 | 125 | 20 | 5 | 10 | 1683 | 201088 | 38010 | 0.38 |
| rebase | 3 | 1 | 0 | 0 | 1348 | 74 | 20 | 40 | 5660 | 931575 | 89133 | 1.01 |
| structural | 11 | 0 | 0 | 0 | 628 | 150 | 38 | 74 | 14049 | 1364269 | 397726 | 3.74 |
| transform | 2 | 2 | 0 | 0 | 252 | 52 | 12 | 24 | 4570 | 496119 | 75678 | 0.80 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 90 | 1.01 |
| green | 11935 | 15.68 | 3608 | 3.25 |
| exhausted | 0 | 0.00 | 33 | 0.43 |
| refactor | 1452 | 1.90 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `skills/tdd/scripts/unreachable.sh <repo-root>` lists, one per line, each script under `skills/tdd/scripts/` reachable from none of the declared entry points, including one whose only callers are other scripts inside the same orphaned subtree ⟦criterion 1⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 430 | 92 | 180 | 38963 | 4702581 | 370443 | 4.68 | unknown | 2/2 | unknown | unknown |  | exhausted | full |
| `skills/tdd/scripts/unreachable.sh <repo-root>` lists, one per line, each script under `skills/tdd/scripts/` reachable from none of the declared entry points, including one whose only callers are other scripts inside the same orphaned subtree ⟦added⟧ ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 489 | 105 | 204 | 46560 | 5488954 | 437623 | 5.53 | 4413 | 2/2 | 2/5 | structural-owed |  |  | full |
| unreachable.sh matches a script name as a whole name, not a substring: an orphan whose name is the tail of a reached script's name (e.g. `leaf.sh` beside a reached `run-leaf.sh`) is still listed ⟦added⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 281 | 62 | 124 | 25916 | 2889959 | 306793 | 3.55 | 1304 | 1/2 | 1/5 | structural-owed |  |  | full |
| `skills/tdd/scripts/unreachable.sh` run with no `<repo-root>` argument exits 2 with a usage line on stderr and prints nothing on stdout, and it is on the list of scripts `skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh` checks ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 40 | 80 | 12952 | 1755541 | 241475 | 2.54 | 259 | unknown | 0/5 | nothing-left |  |  | full |
| a script reached from exactly one kind of entry point — only SKILL.md (or a procedure file it reads), only a Makefile recipe, or only a git hook — directly or through a chain of other scripts or sourced `lib/` files, is not listed by unreachable.sh ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 353 | 53 | 108 | 23165 | 2541787 | 272574 | 3.86 | 2307 | 1/2 | 0/5 | nothing-left |  |  | full |
| unreachable.sh counts a dynamically constructed invocation as reaching its target — a script or prompt template named only through a built path such as `"$S/build-$kind-prompt.sh"` or `prompts/develop-$phase.md` is not listed, on a fixture where a literal `grep -F` for the target's name finds no caller ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 256 | 60 | 116 | 25001 | 2669755 | 305414 | 3.48 | 1279 | 1/2 | 0/5 | nothing-left |  |  | full |
| a script whose only caller is its own test suite is listed by unreachable.sh as test-only, apart from the unreachable ones, and running the check deletes and modifies no file ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 206 | 53 | 104 | 18406 | 2498048 | 268000 | 3.01 | 424 | unknown | 1/5 | structural-owed |  |  | full |
| a `VERI_*` knob or a script name that SKILL.md or CLAUDE.md promises and that no script reads, or that does not exist, is listed by unreachable.sh as promised-unread ⟦criterion 5⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 394 | 74 | 148 | 34392 | 3504445 | 322828 | 4.54 | 2473 | 2/2 | 1/5 | nothing-structural |  |  | full |
| `make unreachable` runs unreachable.sh over this repository and exits 0, so the check is itself reached from a declared entry point | 8 | 3 | 1 | 0 | 0 | 0 | 302 | 71 | 138 | 25816 | 3299787 | 354958 | 4.02 | 2631 | 1/2 | 0/5 | structural-owed |  |  | full |
| every script unreachable.sh lists as unreachable in this repository is removed together with any suite whose every assertion is about it, and the check then lists no unreachable script ⟦criterion 3⟧ | 17 | 4 | 0 | 0 | 0 | 0 | 342 | 84 | 166 | 30006 | 3468951 | 651352 | 6.51 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `skills/tdd/scripts/unreachable.sh <repo-root>` lists, one per line, each script under `skills/tdd/scripts/` reachable from none of the declared entry points, including one whose only callers are other scripts inside the same orphaned subtree ⟦added⟧ ⟦criterion 1⟧ | 1 | 2/5 | structural-owed | PASS | 0 | 794 | 0.99 |
| unreachable.sh matches a script name as a whole name, not a substring: an orphan whose name is the tail of a reached script's name (e.g. `leaf.sh` beside a reached `run-leaf.sh`) is still listed ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 78 | 0.89 |
| `skills/tdd/scripts/unreachable.sh` run with no `<repo-root>` argument exits 2 with a usage line on stderr and prints nothing on stdout, and it is on the list of scripts `skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh` checks ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 57 | 0.77 |
| a script reached from exactly one kind of entry point — only SKILL.md (or a procedure file it reads), only a Makefile recipe, or only a git hook — directly or through a chain of other scripts or sourced `lib/` files, is not listed by unreachable.sh ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 88 | 0.87 |
| unreachable.sh counts a dynamically constructed invocation as reaching its target — a script or prompt template named only through a built path such as `"$S/build-$kind-prompt.sh"` or `prompts/develop-$phase.md` is not listed, on a fixture where a literal `grep -F` for the target's name finds no caller ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 118 | 0.90 |
| a script whose only caller is its own test suite is listed by unreachable.sh as test-only, apart from the unreachable ones, and running the check deletes and modifies no file ⟦criterion 4⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 171 | 0.99 |
| a `VERI_*` knob or a script name that SKILL.md or CLAUDE.md promises and that no script reads, or that does not exist, is listed by unreachable.sh as promised-unread ⟦criterion 5⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 77 | 0.83 |
| `make unreachable` runs unreachable.sh over this repository and exits 0, so the check is itself reached from a declared entry point | 1 | 0/5 | structural-owed | PASS | 1 | 1452 | 1.90 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 2/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 0 | 1 | 0 | 1 | 237 | 0 | 232 | 0 | 243 | 2 | 0 | 12 | 12 | 230 | 0 | 0 | 227 | 0 | 237 | 0 | 235 | 0 | 162 | 233 | 230 | 232 | 0 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | 4 | 0 | 2 | 2 | 2 | 2 | 3 | 2 | 4 | 0 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 0 | 3 | 3 | 192 | 0 | 15 | 116 | 1 | 2 | 9 | 14 | 1 | 5 | 15 | 4 | 2 | 4 | 0 | 177 | 30 | 38 | 37 | 39 | 70 | 36 | 32 | 34 | 35 | 33 | 33 | 35 |
| fast | 13 | 12 | 12 | 12 | 12 | 12 | 13 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 14 | 12 | 13 | 12 | 13 | 16 | 14 | 14 | 15 | 14 | 14 | 15 | 14 | 13 | 13 | 13 | 13 | 14 | 13 | 15 | 13 | 14 | 14 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 4 | 3 | 2 | 3 | 3 | 0 | 3 | 3 | 3 | 3 | 33 | 35 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 817 | 821 | 812 | 816 | 811 | 825 | 819 | 926 | 863 | 920 | 870 | 604 | 625 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 696 | 1372 | 282472 | 32877708 | 3567476 | 42.05 |
