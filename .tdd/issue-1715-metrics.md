### 📊 Metrics — issue 1715

Wall time for the issue: 3922 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1739.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 1 | 2 | 1183 | 17088 | 14439 | 0.07 |
| red | 9 | 4 | 0 | 0 | 370 | 177 | 52 | 104 | 20545 | 1626091 | 270427 | 1.16 |
| green | 13 | 2 | 3 | 0 | 964 | 231 | 81 | 156 | 21902 | 2426756 | 220583 | 1.57 |
| refactor | 4 | 2 | 0 | 0 | 93 | 28 | 14 | 26 | 2213 | 350927 | 59126 | 0.25 |
| exhausted | 2 | 0 | 0 | 0 | 713 | 69 | 8 | 18 | 3897 | 251952 | 18418 | 0.44 |
| diff | 6 | 3 | 0 | 0 | 1853 | 188 | 66 | 132 | 20772 | 2818732 | 217313 | 1.03 |
| pin | 1 | 1 | 0 | 0 | 14 | 8 | 3 | 6 | 859 | 61640 | 32241 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 13 | 3 | 0 | 1226 | 195 | 71 | 140 | 19078 | 1920505 | 313926 | 1.29 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 1560 | 305 | 99 | 198 | 34827 | 3964192 | 365625 | 1.77 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 1233 | 211 | 55 | 106 | 17466 | 1668489 | 152996 | 1.57 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 191 | 0.52 |
| green | 0 | 0.00 | 642 | 1.24 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 713 | 0.44 |
| diff | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `unreachable.sh` reads the promises of `skills/tdd/SCRIPTS.md` as well as SKILL.md and CLAUDE.md: a `VERI_*` knob or a `<name>.sh` named only in SCRIPTS.md, which no script reads or which does not exist, is printed `promised-unread: <name>` exactly as one named in SKILL.md is ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 29 | 56 | 7364 | 814455 | 99409 | 0.55 | 250 | unknown | 0/5 | nothing-left |  |  | full |
| `affected-suites.sh` places an edit to `skills/tdd/SCRIPTS.md` on the suites that read that file (the bash suites naming it and the pytest suites reading it), never raising Unplaced and never widening to every suite ⟦criterion 3⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 124 | 33 | 66 | 11035 | 1061557 | 100990 | 1.04 | unknown | 2/2 | unknown | unknown |  |  | full |
| `affected-suites.sh` places an edit to `skills/tdd/SCRIPTS.md` on the suites that read that file (the bash suites naming it and the pytest suites reading it), never raising Unplaced and never widening to every suite. The expected output lists the placed suites in affected-suites.sh's own `sorted(set(...))` order, so `py/…` paths come before `*.test.sh` names; the case asserts that order or compares the lines as a set ⟦criterion 3⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 189 | 57 | 110 | 17444 | 1699138 | 188742 | 1.15 | unknown | 2/2 | unknown | unknown |  |  | full |
| `affected-suites.sh` places an edit to `skills/tdd/SCRIPTS.md` on the suites that read that file (the bash suites naming it and the pytest suites reading it), never raising Unplaced and never widening to every suite. The rule: an edit to `skills/tdd/SCRIPTS.md` places the bash suites whose text names `SCRIPTS.md` plus the pytest files that mention it. Pinned by a case over a fixture tree holding exactly two such suites, a bash suite `catalogue.test.sh` naming `SCRIPTS.md` and a pytest file `py/unit/test_catalogue.py` mentioning it, both under the suite directory affected-suites.sh scans, whose expected output is exactly those two suites; the case makes no claim about their order: it compares the placed suites as a set, or sorts both the expected and the actual lines before comparing ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 85 | 28 | 56 | 8972 | 825697 | 139426 | 0.52 | 553 | unknown | 0/5 | nothing-left |  |  | full |
| The catalogue's `- `$S/<script>`` entries move out of SKILL.md's `## The scripts` section, unchanged, into a new `skills/tdd/SCRIPTS.md` beside SKILL.md; SKILL.md keeps in their place a pointer naming `<base directory>/SCRIPTS.md` and when to read it (before calling a script whose arguments, output or exit codes the step at hand does not spell out); in the same commit every suite that read the catalogue out of SKILL.md (test_skill_commit, test_skill_refactor_pending, test_skill_stopping, test_skill_reference_usage, test_skill_green_split, test_skill_leaf_launch, issue-worktree.test.sh, affected-suites.test.sh) reads it from SCRIPTS.md, so the fast tier and those suites stay green ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 132 | 43 | 86 | 14740 | 2201142 | 100248 | 0.62 | 1173 | n/a | n/a | n/a |  |  | full |
| Every suite that read the catalogue reads `skills/tdd/SCRIPTS.md` and keeps its outcome, and `test_skill_reference_usage.py` checks as many synopses against the real tree on HEAD as it did at the branch point, not zero ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 11 | 22 | 2905 | 290836 | 69751 | 0.23 | 706 | n/a | n/a | n/a |  |  | full |
| `unreachable.sh` over the real tree prints the same lines on HEAD as at the branch point, `promised-unread: ledger.sh` included ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 12 | 24 | 3127 | 326754 | 47314 | 0.18 | 127 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/add-ledger-step.test.sh — FAIL - #1579: SKILL.md's add-ledger-step.sh entry documents --planned (no ⟦added⟧, not counted toward VERI_STEP_GROWTH) and its exit-2 refusals: no --criterion, an already-served criterion, no readable spec file, a k not unticked in the issue body; and skills/tdd/scripts/tests/prose-drift-red.test.sh — FAIL - `make test` is red over a tree whose VERI_REFACTOR_BUDGET default has moved and whose two prose statements of it have not, naming both (want the red to name 'SKILL.md', the statement the plant left behind). Both suites still read the scripts catalogue out of SKILL.md; it now lives in skills/tdd/SCRIPTS.md. Verified against the full command `make test` ⟦suite-repair⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 11 | 22 | 4601 | 316519 | 72228 | 0.26 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `unreachable.sh` reads the promises of `skills/tdd/SCRIPTS.md` as well as SKILL.md and CLAUDE.md: a `VERI_*` knob or a `<name>.sh` named only in SCRIPTS.md, which no script reads or which does not exist, is printed `promised-unread: <name>` exactly as one named in SKILL.md is ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 41 | 0.15 |
| `affected-suites.sh` places an edit to `skills/tdd/SCRIPTS.md` on the suites that read that file (the bash suites naming it and the pytest suites reading it), never raising Unplaced and never widening to every suite. The rule: an edit to `skills/tdd/SCRIPTS.md` places the bash suites whose text names `SCRIPTS.md` plus the pytest files that mention it. Pinned by a case over a fixture tree holding exactly two such suites, a bash suite `catalogue.test.sh` naming `SCRIPTS.md` and a pytest file `py/unit/test_catalogue.py` mentioning it, both under the suite directory affected-suites.sh scans, whose expected output is exactly those two suites; the case makes no claim about their order: it compares the placed suites as a set, or sorts both the expected and the actual lines before comparing ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 3 | 0 | 3 | 18 | 18 | 18 | 18 | 18 | 0 | 19 | 18 | 18 | 290 | 294 | 293 | 294 |
| fast | 17 | 16 | 16 | 17 | 16 | 16 | 16 | 16 | 16 | 16 | 17 |  |  |  |  |  |  |  |  |
| target | 3 | 18 | 35 | 0 | 0 | 33 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 225 | 444 | 71371 | 7553186 | 832547 | 4.63 |
