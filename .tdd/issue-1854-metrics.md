### 📊 Metrics — issue 1854

Wall time for the issue: 3626 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1863.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 12 | 1 | 2 | 1382 | 0 | 33723 | 0.10 |
| red | 5 | 1 | 0 | 0 | 171 | 146 | 27 | 52 | 12624 | 827853 | 127341 | 0.53 |
| green | 2 | 1 | 0 | 0 | 51 | 25 | 11 | 20 | 2360 | 297987 | 32584 | 0.13 |
| refactor | 2 | 1 | 0 | 0 | 27 | 15 | 6 | 12 | 956 | 163613 | 30423 | 0.10 |
| diff | 8 | 4 | 0 | 0 | 1649 | 266 | 77 | 152 | 23192 | 2801025 | 202566 | 1.02 |
| pin | 3 | 3 | 0 | 0 | 63 | 54 | 12 | 22 | 3405 | 308839 | 49209 | 0.19 |
| rebase | 2 | 1 | 0 | 0 | 619 | 56 | 13 | 26 | 3429 | 406074 | 38086 | 0.17 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 12 | 0 | 0 | 1205 | 242 | 60 | 118 | 17818 | 1747091 | 251446 | 0.98 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 1389 | 332 | 87 | 168 | 29530 | 3058300 | 262486 | 1.26 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `affected-suites.sh` places an edit to `skills/tdd/RESUME.md` on the suites that read that file (the bash suites whose text names `RESUME.md` plus the pytest files that mention it), never raising Unplaced and never widening to every suite. Pinned by a case over a fixture tree holding exactly two such suites, a bash suite naming `RESUME.md` and a pytest file under `py/unit/` mentioning it, whose expected output is exactly those two suites ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 84 | 25 | 48 | 6920 | 686727 | 120548 | 0.44 | 224 | unknown | 0/5 | nothing-left |  |  | full |
| The `## Resume` section moves out of SKILL.md, its text unchanged save where a pointer requires, into a new `skills/tdd/RESUME.md` directly beside SKILL.md; in the same commit every suite that read `## Resume` or its lines out of SKILL.md (test_skill_refactor_pending.py, test_skill_draft_pr.py, test_skill_criterion_finished.py, test_skill_preflight.py, test_skill_refactor_touched.py, test_skill_verify_step.py, test_skill_leaf_env.py's resume-mark case, test_skill_event_marks.py's resume mark case, test_run_conductor.py's launch-lines case, test_affected_suites.py's `## Resume` REAL_EDITS row, and any other suite the fast tier or the affected suites show reading it) reads them from RESUME.md, so the fast tier and those suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 152 | 35 | 68 | 12201 | 1483524 | 88051 | 0.49 | 764 | n/a | n/a | n/a |  |  | full |
| Step 1.5's resume check carries a pointer naming `<base directory>/RESUME.md` and saying to `Read` it when the check finds `.tdd/issue-<n>.md`, replacing its summary of the procedure; the Draft PR step's sub-step-1 branch carries a pointer naming `<base directory>/RESUME.md` and saying to `Read` it when it finds a dirty tree or a pending refactor; no pointer names `VERI_SKILL_CLONE`, `~/.claude/skills` or any path outside the base directory; the five other lines that name *Resume* (SKILL.md's preflight `$stray` line and worktree-guard line, BAIL.md's re-run line, SCRIPTS.md's `issue-worktree.sh` entry, and `solvable-issues.sh`'s comment) name `RESUME.md`; any suite pinning those lines verbatim or by checksum moves in the same commit, so the fast tier and the affected suites stay green ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 13 | 26 | 3483 | 403908 | 37348 | 0.17 | 380 | n/a | n/a | n/a |  |  | full |
| Every suite that read `## Resume` or its lines out of SKILL.md reads RESUME.md and keeps its outcome, and none of them passes by finding nothing to check: each case that slices the section or finds a line still finds a non-empty section or the line it ran before the move ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 15 | 30 | 4045 | 494977 | 45102 | 0.20 | 393 | n/a | n/a | n/a |  |  | full |
| `unreachable.sh` over the real tree prints the same lines on HEAD as at the branch point ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 14 | 28 | 3463 | 418616 | 32065 | 0.16 | 235 | n/a | n/a | n/a |  |  | full |
| A case pins the RESUME.md pointers: SKILL.md's step 1.5 resume check and its Draft PR sub-step 1 each carry a line naming `<base directory>/RESUME.md` and saying to `Read` it, no line of SKILL.md, SCRIPTS.md, BAIL.md, STOPPING.md or RECONCILE.md naming RESUME.md names `VERI_SKILL_CLONE` or `~/.claude/skills`, and no line of those files or of `solvable-issues.sh` names *Resume* without naming `RESUME.md` (a small case reading the files as text) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 67 | 13 | 22 | 5981 | 352694 | 40725 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| A case pins the move: SKILL.md carries no `## Resume` heading and none of the lines `$S/event.sh resume`, `left=$(( ${VERI_REFACTOR_BUDGET:-5} - count ))` or `add-ledger-step.sh --planned --criterion`, while `skills/tdd/RESUME.md` carries all three (a small case reading the files as text) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 9 | 18 | 3303 | 280128 | 38084 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| A case pins the walk: `unreachable.sh` follows a mention made only in `skills/tdd/RESUME.md`, so a script named there and nowhere else in the skill's markdown is not listed unreachable (a case over a fixture tree, or a tree_audit case over this repository) ⟦criterion 3⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 99 | 22 | 44 | 6570 | 684817 | 78286 | 0.33 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `affected-suites.sh` places an edit to `skills/tdd/RESUME.md` on the suites that read that file (the bash suites whose text names `RESUME.md` plus the pytest files that mention it), never raising Unplaced and never widening to every suite. Pinned by a case over a fixture tree holding exactly two such suites, a bash suite naming `RESUME.md` and a pytest file under `py/unit/` mentioning it, whose expected output is exactly those two suites ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 27 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 4 | 3 | 3 | 158 | 1 | 155 | 154 | 154 | 149 | 152 | 0 | 1 | 0 |
| fast | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 4 | 5 |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |
| all | 275 | 282 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 147 | 286 | 47348 | 4805391 | 513932 | 2.24 |
