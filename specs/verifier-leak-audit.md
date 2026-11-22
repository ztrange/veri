# Verifier-leak audit: the hand-fix commits of PRs #4405, #4436 and #4478

Each hand-fix commit of ztrange/veri PRs #4405 (run #4391), #4436 (run #4432) and #4478 (run #4471) is
traced to the ledger step that wrote or omitted the fixed lines and to the per-step check that passed it.
This file changes no prompt, script or `specs/prd-040.md` row.

## Method and limits

- Commits were read with `gh pr view <n> -R ztrange/veri --json commits`; the ledgers with
  `git show <fix-commit>:.tdd/issue-<run>.md`; each fix's message and diff with `git show`.
- Scope: the commits after the run's closing `metrics:` commit (the run's own last commit), as the issue names
  them (PR #4405 from `test: bail.sh refuses another flag…`, PR #4478 from `fix: queued-merge reads the veri: ci on pr: line…`),
  plus, on PR #4405 and PR #4436, the commits after that point that tick no step. Commits before it are the
  run's own, each a plan, a test, a feature, a tick, a refactor or a regrade, and are not audited here.
- Verifier verdicts were read on issue #4391's comments (comments #22-#33, #51, #84) only. For runs #4432 and
  #4471 the check is named from the ledger, the fix commit's message and the prompt's text, not from a verdict
  comment, so those rows carry `inferred` in the Evidence column.
- A fix commit that holds more than one finding gets one row and one primary class (the first finding the commit
  message names); its other classes are in the *Also* column and counted separately under the class table.
- The leaking check is the one that read the fixed lines (or should have read the omitted ones) and passed them.
  `none` means no per-step check reads that kind of line.
- Hashes are the PR's own commit hashes.

## Rows: one per hand-fix commit

Classes: **A** surviving-mutant (a guard a step wrote, no test requires it); **B** unhandled-outcome (a failing call's
exit code ignored, or an outcome with no branch); **C** omitted-contract (behaviour the criterion or SCRIPTS.md states that no
step built or tested); **D** ambient-cwd (reads the launch directory, not the tree it judges); **E** prose-drift (a doc, row or
hint that disagrees with the code or with its sibling sites: stale, left out or deleted); **G** faked-observable (the tests fake
the very thing the criterion observes).

### Findings

| # | PR | Fix commit subject | Ledger step that wrote or omitted the lines | Per-step check that passed it | Class | Also | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | #4405 | `6beba9edf1` test: bail.sh refuses another flag in place of --note-file or --attempt, and non-ASCII digits | step 6, "an unknown `<cause>` … exits 2" (`56a88d8fa4`): its diff wrote `_valid`'s `argv[3] != "--note-file"`, `argv[5] == "--attempt"` and `isdigit` guards | `prompts/verify-green.md` check 4 (probe every guard the diff added) | A | | verdicts #22 (REJECT on the `argv[3]` guard), #24 (PASS naming `.returncode != 0` unrequired, and the `_valid` probes caught), #33 (PASS whose body names `len(rest) == 2` and `rest[0] == "--attempt"` as required by no test) |
| 2 | #4405 | `ea66ca8c8d` fix: bail.sh takes `<n>` and `<k>` as ASCII whole numbers only, through entry.whole_number | step 4, "bail.sh refuses the other bad arguments (a non-numeric `<n>` …)" (`37d48a46e2`), a test-only step over a bail.py that was a stub returning 2 (`git show 37d48a46e2:skills/tdd/scripts/veri/bail.py`); the `isdigit` that took `٣` was written by step 6 | `prompts/verify-pin.md` for step 4 (the pin passed with no production code to probe); `verify-green.md` check 4 for step 6 | C | A | `git show`; verdict #24 |
| 3 | #4405 | `7a38325c5c` fix: bail.sh names an unopenable note and goes on, prints a call line for every call, and hands ledger-steps.sh the ledger | no step: the plan had a "non-zero → still runs" step for `metrics.sh`, `skill-drift.sh`, `preserve-attempt.sh`, `push-branch.sh` and both `comment.sh` calls, and none for a failed `git reset`, `event.sh`, `git add`/`commit`, the note write or `ledger-steps.sh` (its input); the call-line step is `0a460f0cd7`, the ledger call was written by `12e0b448e4` | `prompts/verify-plan.md` (the plan passed with those calls unplanned; criterion 2 is "never refusing") | B | C | commit diff; ledger |
| 4 | #4405 | `7e8ee952b7` docs: SCRIPTS.md and SC588 say bail.sh prints a line per call, goes past a failed reset, event, commit or note write … | step 1, the `⟦skill-edit⟧` step that catalogued bail.sh before the script existed | the grader, `veri/grade_prose.py` (it compares prose to the step's rows with no tools); no later step re-read SCRIPTS.md against the code | E | | commit diff; PRD facts: the grader "compares prose to rows, never rows to code" |
| 5 | #4405 | `13187e22f1` fix: bail.sh reads the ledger path from run_dir.ledger, so only ledger.py spells the file name | step 6 / `12e0b448e4`, which wrote `os.path.join(".tdd", "issue-%s.md")` in bail.py | none: the repo audit that refuses the spelling runs in the full suite, once per PR, not in any step's fast tier or `changed` run | E | | commit diff; CLAUDE.md, *Per step* |
| 6 | #4436 | `d28f439db4` fix: run-pr.sh stops at a late stage's non-zero exit, honours --hand past the title seam, refuses a missing ledger | step 7, "at the first stage exiting 1 or 2 it stops … calls no later stage" (`a19d4653ff`): its test drove the early stages only, and `run_late` never read `fused.call`'s exit code; `e838413408` wrote the discarded `_, out, _ = fused.call(...)` loop in `main`, and refactor `54ad0d74e9` ("split main in run_pr.py into run_late and run_early") moved it into `run_late` | `prompts/verify-green.md` check 4 sees only code a step added, never the read of an exit code that was never written; `verify-plan.md` passed a step naming no late-stage side | B | C | commit message; ledger |
| 7 | #4436 | `32b3972856` docs: restore the DP52 (dropped) row and regrade DRAFT-PR.md | step 2, the `⟦skill-edit⟧` step on DRAFT-PR.md (`470ef10331`, "requirements for DRAFT-PR.md, graded", deleted the row) | the grader, `veri/grade_prose.py` (a deleted `(dropped)` row holds no claim to grade) | E | | commit message |
| 8 | #4436 | `6ffdd8fd87` fix: run-pr.sh prints each stage once and resumes any stage's exit 3 at that stage | step 18, "it prints each stage's call line with its exit code …" (`b22855d8a8`): its cases spied `fused.call`, which is the thing that prints | `prompts/verify-red.md` check 3 (quality of the test) | G | A, C | commit message: "The tests that spied on fused.call now print through a printing() wrapper"; ledger; inferred |
| 9 | #4436 | `ea09d9d410` fix: run-pr.sh never resumes on an empty ledger sha, and a stacked run's current seam calls no stage | `ledger_sha`'s `"--"` argv: step 5, "called again after the title seam, which it records … with the sha of the ledger's last commit" (`e838413408`); the empty-sha and `and not stacked` lines were written by hand-fix `6ffdd8fd87`, not by a step | `prompts/verify-green.md` check 4 | A | B | commit message ("deleted with every case green, since the fakes returned one constant sha"); `git log -S` |
| 10 | #4436 | `ce4f54beed` docs: SCRIPTS.md names run-pr.sh's hand seam in exit 1 and the resume after a 3; regraded | step 1, the `⟦skill-edit⟧` step that wrote run-pr.sh's catalogue entry before the script existed | the grader, `veri/grade_prose.py`; no later step re-read SCRIPTS.md against the code | E | | commit message |
| 11 | #4478 | `14d8fe9443` fix: queued-merge reads the veri: ci on pr: line from the merge worktree's CLAUDE.md | step 10, "With a `veri: ci on pr: 0` line in the merge worktree's CLAUDE.md … `queued_merge.py` re-runs the local full suite" (`be205b4fe9`); its case put the line in the launch directory, which was also the process cwd | `prompts/verify-red.md` check 3 | D | | commit message: "The earlier cwd-based 0 case…"; inferred |
| 12 | #4478 | `f2c8e03d5b` fix: queued-merge runs wait-ci in the merge worktree, so it reads that worktree's veri: ci on pr: line | step 9, the `wait-ci.sh` step (`e9051f0326` is its test); the `wait-ci` gate in `queued_merge.py` was never given a cwd | `prompts/verify-red.md` check 3 for step 9; step 10's `verify-green.md` | D | | commit message; inferred |
| 13 | #4478 | `0ed61f8c75` fix: queued-merge runs the rebased tree's full suite in the merge worktree | no step wrote the unchanged `_gate` call (pre-existing since #2886); step 10 (`be205b4fe9`) widened who reaches it | none: no per-step check reads an unchanged caller of a function the step changed (`verify-refactor.md` sees only the step's own diff, #4577) | D | | commit message |
| 14 | #4478 | `ac704de6d8` fix: ready-check's failing pull_request row names the veri: ci on pr: line as a fix | step 8, "`ready-check.sh`'s `pull_request` row passes with a `veri: ci on pr: 0` line" (`cac24121c8`): it wrote the pass and not the row's fix hint | none: `verify-green.md` check 4 rejects unrequired code, it does not read a string the step left unchanged | E | | commit message |
| 15 | #4478 | `7e2cfa3d43` docs: DRAFT-PR.md, SCRIPTS.md and veri/README.md name the veri: ci on pr: line beside VERI_CI_ON_PR | steps 17 and 18, the `⟦skill-edit⟧` steps for SCRIPTS.md and DRAFT-PR.md, which named the sites by row id (SC38, SC63, SC130, SC136, DP88, DP99) while the criterion says "wherever" | `prompts/verify-plan.md` (passed the narrowed step) and the grader, `veri/grade_prose.py` (graded only the listed rows) | E | | commit message; ledger |

### Not a review finding

| PR | Commit | Reason |
|---|---|---|
| #4405 | `12e52b96de` docs: GRADED re-signs BAIL.md and SCRIPTS.md after the rebase onto main | rebase conflict in GRADED; mechanical regrade, no defect of the run |
| #4405 | `24b6bc6649` test: bail.sh names an unopenable note, prints a call line for every call … | the test half of row 3's finding, not a separate one |
| #4405 | `d22c309b26` docs: GRADED re-signs SCRIPTS.md for bail.sh's call lines and exit codes | the regrade owed by row 4's edit |
| #4436 | `b4f630edeb` fix: run_pr.py declares USAGE at module level again … | made inside the run, between its two bail `metrics:` commits, to repair the structural pass's refactor `ef41fd225f`, which `e217e8459b` then reverted (inferred from order and subjects) |
| #4436 | `e217e8459b` revert: put USAGE, TITLE and BODY back at module level | the run's own revert of a transform |
| #4436 | `ad6f97aab2` chore: re-mark the structural candidate not-done, transform-rejected | the run's own ledger record |
| #4436 | `e533fe2ace` docs: renumber the run-pr.sh DRAFT-PR row DP360 and regrade … after the rebase | main gave DP357 to another row: an id collision from the rebase, not a defect of the run |
| #4478 | `74afbab248` docs: regrade DRAFT-PR.md and SCRIPTS.md after the veri: ci on pr: wording | the regrade owed by row 15's edit |
| #4478 | `eb21f85190` docs: veri/README.md's ci_on_pr section matches the module | CI went red on the README edit of row 15's own hand fix; a defect of a hand fix, not of the run |

Rows 1-15 are the 15 findings; 9 commits are not a finding.

## Leak classes

| Class | #4405 | #4436 | #4478 | Total |
|---|---|---|---|---|
| A surviving-mutant | 1 | 1 | 0 | 2 |
| B unhandled-outcome | 1 | 1 | 0 | 2 |
| C omitted-contract | 1 | 0 | 0 | 1 |
| D ambient-cwd | 0 | 0 | 3 | 3 |
| E prose-drift | 2 | 2 | 2 | 6 |
| G faked-observable | 0 | 1 | 0 | 1 |
| **Total** | 5 | 5 | 5 | **15** |

The totals sum to the 15 finding rows. The class with the highest total is **E prose-drift** (6 of 15), then D ambient-cwd (3).

Classes named in the *Also* column, uncounted above: A 2 (rows 2, 8), B 1 (row 9), C 3 (rows 3, 6, 8).

The 15 rows are commits, not the operator's 22 findings: one commit often fixes several (row 3 fixes three). The operator's
count by PR (7, 11, 4) is not reproduced; the commit count by PR is 5, 5 and 5.

## Each class against `specs/prd-040.md`

| Class | Row that would have caught it | Why |
|---|---|---|
| A surviving-mutant | none | OM, RTR and SG rows leave 040.5 (the mutation pass, an outline) to catch it, and verify-green check 4 already exists; no OM, RTR or SG row changes check 4 |
| B unhandled-outcome | OM4 (row 6, whose `run_late` discarded a `fused.call` exit code; and row 3's bare `subprocess.run` for `event.sh`) and OM10 (row 6's late-stage outcome); not row 3's `git.git(...)` calls, which OM4's list (`subprocess.run`, `subprocess.call`, `os.system`, `fused.call`) omits | OM4 reads added `.py` lines for a discarded exit |
| C omitted-contract | none | OM10 asks for a residual outcome of a dispatch; a SCRIPTS.md statement (row 2's non-ASCII input, row 3's failing git calls, row 6's missing ledger) no step tests is not a dispatch |
| D ambient-cwd | none | no OM, RTR or SG row names the working directory a read depends on |
| E prose-drift | none | RTR8 judges a sentence the diff adds or changes; rows 4, 10 and 15 are stale or left-out sites, row 7 a deleted row, row 14 an unchanged hint, row 5 a repo audit; D15 leaves them to 040.1 |
| G faked-observable | OM1 | row 8's cases spied `fused.call`, the observable the criterion names (the printed call line) |

### Surviving-mutant findings: written by a step, or never written

| Row | Mutated lines | Added by a step? |
|---|---|---|
| 1 (#4405) | `_valid`'s `argv[3] != "--note-file"`, `argv[5] == "--attempt"` and `isdigit` guards | yes, step 6 (`56a88d8fa4`), so verify-green's check 4 should have probed them; verdicts #22-#24 show it probed some, and verdict #33 (PASS) names two `_valid` guards no test requires |
| 9 (#4436) | `ledger_sha`'s `"--"` argument | yes, step 5 (`e838413408`), so check 4 should have probed it |
| 9 (#4436) | the empty-sha match and the `and not stacked` clause | no: written by hand-fix `6ffdd8fd87`, so no check 4 could have probed them |
| 8 (#4436) | `run_stages`'s LATE-only guard, `if code == 3 and stage in LATE:`, and `main`'s `resume if resume in LATE else None` ("the LATE-only guard, which no case pinned", removed by `6ffdd8fd87`) | no: written by hand-fix `d28f439db4` (row 6; `git log -S'in LATE'`), so no check 4 could have probed them |

None of the surviving-mutant findings was code nobody wrote: row 1 and the `ledger_sha` argument were lines a step added,
row 9's empty-sha lines and row 8's LATE-only guard lines a hand fix added.
The omitted code (rows 3, 6, 11-13) is a different class from the mutants and has no mutant to flip (the 0 of 4 figure of PR #4462).

## Proposed fixes for the classes marked `none`

- A surviving-mutant: "verify-green check 4: a PASS whose REASON names code no test requires is a REJECT" (verdict #33 passed while naming two unrequired guards)
- C omitted-contract: "verify-plan: a behaviour the issue or SCRIPTS.md states needs a step that tests it, not only the dispatch's residual outcome"
- D ambient-cwd: "verify-red check 3: a test places the input where the criterion names it and a contrary one in the launch directory"
- E prose-drift: "verify-diff and the grader: a site the issue says 'wherever' is found by search, not by the plan's row list, and a diff that changes behaviour re-reads the doc sites that name it" (per step, ahead of #4472 "PRD 040.1: verify-branch, a blind verifier judges the whole branch before readying", which D15 hands the whole branch's stale-doc drift to once, before readying)
