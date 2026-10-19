### 📊 Metrics — issue 1853

Wall time for the issue: 2750 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1858.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 29 | 25 | 2 | 4 | 2959 | 34926 | 31534 | 0.11 |
| red | 5 | 1 | 0 | 0 | 136 | 102 | 28 | 56 | 11169 | 888968 | 97529 | 0.44 |
| green | 2 | 1 | 0 | 0 | 76 | 42 | 16 | 30 | 3599 | 466179 | 34373 | 0.17 |
| refactor | 2 | 1 | 0 | 0 | 26 | 11 | 5 | 10 | 755 | 130390 | 29502 | 0.09 |
| diff | 8 | 4 | 0 | 0 | 1311 | 265 | 73 | 144 | 23232 | 2664008 | 186528 | 0.97 |
| pin | 3 | 3 | 0 | 0 | 51 | 42 | 11 | 22 | 3756 | 303416 | 46278 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 11 | 1 | 0 | 826 | 247 | 57 | 114 | 19121 | 1744386 | 210706 | 0.89 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 803 | 240 | 78 | 152 | 26349 | 2743501 | 215038 | 1.08 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `affected-suites.sh` places an edit to `skills/tdd/BAIL.md` on the suites that read that file (the bash suites whose text names `BAIL.md` plus the pytest files that mention it), never raising Unplaced and never widening to every suite. Pinned by a case over a fixture tree holding exactly two such suites, a bash suite naming `BAIL.md` and a pytest file under `py/unit/` mentioning it, whose expected output is exactly those two suites ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 85 | 29 | 56 | 7380 | 838875 | 102464 | 0.41 | 242 | unknown | 0/5 | nothing-left |  |  | full |
| The `## Bailing` section moves out of SKILL.md, its text unchanged save where a pointer requires, into a new `skills/tdd/BAIL.md` directly beside SKILL.md; in the same commit every suite that read `## Bailing` or its lines out of SKILL.md (test_skill_green_split.py, test_skill_metrics.py, test_skill_draft_pr.py, test_skill_preserve_attempt.py, test_skill_red_untestable.py, test_skill_stopping.py, test_skill_verify_step.py, test_classify_bail.py, test_skill_leaf_env.py's bail-lines case, test_skill_event_marks.py's bail mark case, test_affected_suites.py's `## Bailing` REAL_EDITS row and its doc list, and any other suite the fast tier or the affected suites show reading it) reads them from BAIL.md, so the fast tier and those suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 98 | 31 | 62 | 11741 | 1343839 | 70952 | 0.43 | 477 | n/a | n/a | n/a |  |  | full |
| SKILL.md gains one standing rule in the core, beside *Launching a leaf*'s stop check, stated once: whenever this procedure says **bail**, `Read` `<base directory>/BAIL.md` and run it with the cause the bailing line names; every line in SKILL.md, SCRIPTS.md, STOPPING.md and RECONCILE.md that names *Bailing* (`see *Bailing*`, `*Bailing*'s push`, `*Bailing* step 1`, the *Bailing* step) names `<base directory>/BAIL.md` instead; any suite pinning those lines verbatim or by checksum moves in the same commit, so the fast tier and the affected suites stay green ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 14 | 26 | 3572 | 405966 | 38460 | 0.17 | 412 | n/a | n/a | n/a |  |  | full |
| Every suite that read `## Bailing` or its lines out of SKILL.md reads BAIL.md and keeps its outcome, and none of them passes by finding nothing to check: each case that slices the section or finds a line still finds a non-empty section or the line it ran before the move ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 16 | 32 | 4820 | 562884 | 46415 | 0.22 | 433 | n/a | n/a | n/a |  |  | full |
| `unreachable.sh` over the real tree prints the same lines on HEAD as at the branch point, `skill-drift.sh` not listed test-only ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 12 | 24 | 3099 | 351319 | 30701 | 0.14 | 103 | n/a | n/a | n/a |  |  | full |
| A case pins SKILL.md's standing bail rule: SKILL.md holds exactly one line saying a bail is carried out by reading `<base directory>/BAIL.md`, and no line of SKILL.md, SCRIPTS.md, STOPPING.md or RECONCILE.md names *Bailing* without naming `<base directory>/BAIL.md` (a small case reading the four files as text) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 10 | 20 | 4596 | 309730 | 35413 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| A case pins the move: SKILL.md carries no `## Bailing` heading and none of the lines `preserve-attempt.sh <n> … bail`, `event.sh bail cause=<cause>` (the Bailing sub-step's generic mark; the Draft PR step's own `event.sh bail cause=suite-red|ci-timeout|ci-conflict|ci-red` lines, which name their cause and are not part of the section, stay), or `metrics: what bailing on`, while `skills/tdd/BAIL.md` carries all three (a small case reading the files as text) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 9 | 18 | 3509 | 272090 | 34953 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| A case pins the walk: `unreachable.sh` over this repository does not list `test-only: skill-drift.sh`, reached through BAIL.md (a tree_audit case like #1716's stop-run.sh one) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 12 | 24 | 3794 | 368258 | 34852 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `affected-suites.sh` places an edit to `skills/tdd/BAIL.md` on the suites that read that file (the bash suites whose text names `BAIL.md` plus the pytest files that mention it), never raising Unplaced and never widening to every suite. Pinned by a case over a fixture tree holding exactly two such suites, a bash suite naming `BAIL.md` and a pytest file under `py/unit/` mentioning it, whose expected output is exactly those two suites ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 26 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 4 | 4 | 4 | 4 | 163 | 164 | 162 | 165 | 160 | 0 | 0 | 1 | 1 | 3 |
| fast | 6 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 5 | 5 | 5 |  |  |  |  |
| target | 0 | 4 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 135 | 266 | 45470 | 4487887 | 425744 | 1.97 |
