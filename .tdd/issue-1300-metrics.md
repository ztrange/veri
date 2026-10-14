### 📊 Metrics — issue 1300

Wall time for the issue: 3525 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1559.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 3 | 6 | 1452 | 119346 | 44972 | 0.21 |
| red | 18 | 8 | 1 | 0 | 784 | 422 | 105 | 210 | 41632 | 5392205 | 837111 | 4.54 |
| green | 17 | 7 | 1 | 0 | 4104 | 433 | 135 | 254 | 43543 | 6750535 | 799328 | 4.55 |
| refactor | 14 | 7 | 0 | 0 | 728 | 144 | 52 | 102 | 12384 | 2225454 | 630695 | 2.87 |
| predicate | 2 | 0 | 0 | 0 | 30 | 20 | 7 | 14 | 1618 | 302594 | 87930 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 25 | 23 | 2 | 0 | 2211 | 462 | 131 | 254 | 42655 | 6142271 | 1075214 | 5.34 |
| developer | claude-sonnet-5-5 | 23 | 0 | 0 | 0 | 2914 | 449 | 140 | 272 | 47106 | 7074140 | 1127451 | 5.69 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 537 | 120 | 31 | 60 | 10868 | 1573723 | 197371 | 1.53 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 117 | 1.02 | 124 | 0.51 |
| green | 737 | 1.12 | 70 | 0.25 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A new conductor check, `suite-reported.sh <leaf-name>`, run from a worktree after a developer leaf launched through `supervise.sh` with a stub `claude` (`CLAUDE_BIN`) whose final result carries no `SUITE:` line has exited 0, exits 2 — never 0 or 1 — reading that leaf's captured `.tdd/<leaf-name>.out` ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 195 | 49 | 94 | 18256 | 2455714 | 348397 | 2.06 | 1018 | 1/2 | 0/5 | nothing-left |  |  | full |
| With the stub `claude`'s final result carrying a `SUITE: GREEN — <summary>` line, `suite-reported.sh <leaf-name>` exits 0 for that leaf, so the check tells a reported leaf from an unreported one ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 94 | 31 | 60 | 8716 | 1420334 | 273461 | 1.32 | 388 | unknown | 0/5 | nothing-left |  |  | full |
| When `suite-reported.sh <leaf-name>` exits 2 it appends one event to the worktree's `.tdd/events.jsonl` named `report-missing`, carrying the leaf's name and the missing line (`missing=SUITE`) — an event distinct from `killed-stuck` — and writes none when it exits 0 ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 142 | 45 | 88 | 13398 | 2189654 | 328681 | 1.91 | 444 | 1/2 | 0/5 | nothing-left |  |  | full |
| `classify-bail.sh report-missing` prints `system`, so a bail on a developer leaf that ended without its `SUITE:` report has a cause token of its own, distinct from `killed-stuck` | 6 | 3 | 0 | 0 | 0 | 0 | 96 | 35 | 68 | 8679 | 1652119 | 285871 | 1.40 | 381 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md` says, at every phase that launches a developer leaf whose prompt requires a `SUITE:` line — Green's develop-green, a revise of green, a `⟦diff-checked⟧` step's develop-diff and its revise, a refactor-kind step's transform, a `⟦phases: …⟧` step's phase leaf, and the structural pass's develop-structural — that `suite-reported.sh <leaf-name>` runs after the leaf's wait exits 0 and before its verifier is launched, and that its exit 2 launches no verifier and bails with cause `report-missing` ⟦criterion 2⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 179 | 50 | 96 | 20599 | 2621631 | 351475 | 1.87 | 1398 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md` runs `suite-reported.sh` only after a leaf whose built prompt asks for a `SUITE:` line — develop-green, develop-diff, the `diff` revise (develop-revise-diff), develop-structural, develop-transform and the develop-expand, develop-migrate, develop-contract-a and develop-contract-b phase leaves — and never after the refactor leaf (*Refactor loop* step 1) or a revise of red, green or refactor (*Revising on a REJECT*, built from develop-revise, which asks for no `SUITE:` line); a prose case over `SKILL.md` goes red if either of those two sections runs the check after a leaf whose prompt has no `SUITE:` requirement, and red if a phase whose prompt does require it loses the check ⟦added⟧ ⟦criterion 3⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 71 | 17 | 34 | 7267 | 860833 | 149181 | 0.76 | unknown | unknown | unknown | unknown |  | green-conflict | full |
| `SKILL.md` runs `suite-reported.sh` only after a leaf whose built prompt asks for a `SUITE:` line — develop-green, develop-diff, the `diff` revise (develop-revise-diff), develop-structural, develop-transform and the develop-expand, develop-migrate, develop-contract-a and develop-contract-b phase leaves — and never after the refactor leaf (*Refactor loop* step 1) or a revise of red, green or refactor (built from develop-revise, which asks for no `SUITE:` line). The step's Red owns every test edit: the older #1300 case in `skills/tdd/scripts/tests/skill-suite-runs.test.sh` ("runs suite-reported.sh before the verifier at every phase…") requires the check in *Refactor loop* and *Revising on a REJECT*, which criterion 3 reverses, so Red drops those two `check_report_section` lines from it in the same change, since Green may not edit a test. Because the `diff` revise does ask for a `SUITE:` line, its check is stated in *A `⟦diff-checked⟧` step* (beside develop-diff's), not in *Revising on a REJECT*, and the case requires it there. The prose case goes red if *Refactor loop* or *Revising on a REJECT* runs the check, and red if Green, the diff-checked step (develop-diff and its revise), the phases step or the structural pass loses it ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 32 | 64 | 11565 | 1610616 | 291661 | 1.44 | 994 | unknown | 0/5 | nothing-left |  |  | full |
| The `diff` revise's check in *A `⟦diff-checked⟧` step* names the leaf the conductor actually launches, `$S/suite-reported.sh revise-diff-<k>` (it reads `.tdd/revise-diff-<k>.out`), never `develop-revise-diff`, which names no leaf and so would find no `.out`, exit 2 and bail `report-missing` on every diff revise; the #1300 prose case in `skills/tdd/scripts/tests/skill-suite-runs.test.sh` requires `suite-reported.sh revise-diff-<k>` there in place of the `suite-reported.sh develop-revise-diff` literal it requires now — Red changes that literal, since Green may not edit a test ⟦added⟧ ⟦criterion 3⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 125 | 40 | 76 | 10697 | 1859887 | 326337 | 1.60 | 1407 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A new conductor check, `suite-reported.sh <leaf-name>`, run from a worktree after a developer leaf launched through `supervise.sh` with a stub `claude` (`CLAUDE_BIN`) whose final result carries no `SUITE:` line has exited 0, exits 2 — never 0 or 1 — reading that leaf's captured `.tdd/<leaf-name>.out` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 92 | 0.41 |
| With the stub `claude`'s final result carrying a `SUITE: GREEN — <summary>` line, `suite-reported.sh <leaf-name>` exits 0 for that leaf, so the check tells a reported leaf from an unreported one ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 90 | 0.40 |
| When `suite-reported.sh <leaf-name>` exits 2 it appends one event to the worktree's `.tdd/events.jsonl` named `report-missing`, carrying the leaf's name and the missing line (`missing=SUITE`) — an event distinct from `killed-stuck` — and writes none when it exits 0 ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 81 | 0.39 |
| `classify-bail.sh report-missing` prints `system`, so a bail on a developer leaf that ended without its `SUITE:` report has a cause token of its own, distinct from `killed-stuck` | 1 | 0/5 | nothing-left | PASS | 0 | 97 | 0.42 |
| `SKILL.md` says, at every phase that launches a developer leaf whose prompt requires a `SUITE:` line — Green's develop-green, a revise of green, a `⟦diff-checked⟧` step's develop-diff and its revise, a refactor-kind step's transform, a `⟦phases: …⟧` step's phase leaf, and the structural pass's develop-structural — that `suite-reported.sh <leaf-name>` runs after the leaf's wait exits 0 and before its verifier is launched, and that its exit 2 launches no verifier and bails with cause `report-missing` ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 109 | 0.41 |
| `SKILL.md` runs `suite-reported.sh` only after a leaf whose built prompt asks for a `SUITE:` line — develop-green, develop-diff, the `diff` revise (develop-revise-diff), develop-structural, develop-transform and the develop-expand, develop-migrate, develop-contract-a and develop-contract-b phase leaves — and never after the refactor leaf (*Refactor loop* step 1) or a revise of red, green or refactor (built from develop-revise, which asks for no `SUITE:` line). The step's Red owns every test edit: the older #1300 case in `skills/tdd/scripts/tests/skill-suite-runs.test.sh` ("runs suite-reported.sh before the verifier at every phase…") requires the check in *Refactor loop* and *Revising on a REJECT*, which criterion 3 reverses, so Red drops those two `check_report_section` lines from it in the same change, since Green may not edit a test. Because the `diff` revise does ask for a `SUITE:` line, its check is stated in *A `⟦diff-checked⟧` step* (beside develop-diff's), not in *Revising on a REJECT*, and the case requires it there. The prose case goes red if *Refactor loop* or *Revising on a REJECT* runs the check, and red if Green, the diff-checked step (develop-diff and its revise), the phases step or the structural pass loses it ⟦added⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 120 | 0.41 |
| The `diff` revise's check in *A `⟦diff-checked⟧` step* names the leaf the conductor actually launches, `$S/suite-reported.sh revise-diff-<k>` (it reads `.tdd/revise-diff-<k>.out`), never `develop-revise-diff`, which names no leaf and so would find no `.out`, exit 2 and bail `report-missing` on every diff revise; the #1300 prose case in `skills/tdd/scripts/tests/skill-suite-runs.test.sh` requires `suite-reported.sh revise-diff-<k>` there in place of the `suite-reported.sh develop-revise-diff` literal it requires now — Red changes that literal, since Green may not edit a test ⟦added⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 139 | 0.44 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 3 | 4 | 42 | 7 | 1 | 3 | 0 | 0 | 0 | 2 | 0 | 3 | 3 | 3 | 3 | 3 | 3 | 1 | 0 | 0 | 0 | 0 | 1 | 5 | 2 | 5 | 27 | 27 | 255 | 257 | 32 | 0 | 0 | 0 | 31 | 0 | 27 |
| fast | 56 | 57 | 58 | 59 | 57 | 58 | 55 | 59 | 59 | 57 | 59 | 56 | 56 | 55 | 61 | 60 | 61 | 56 | 55 | 56 | 55 | 74 | 60 | 64 | 69 | 68 | 54 | 52 |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 2 | 3 | 1 | 26 | 32 | 27 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 302 | 586 | 100629 | 14790134 | 2400036 | 12.56 |
