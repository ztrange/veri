## The skill-edit step

Run `$S/run-step.sh <n>` (on a step whose text names a prose change, `$S/skill-edit-half.sh <n> --change "<change>"` in its place), again on exit 3, and on 1 or 2 go on by the paragraph its last line names.
skill-edit-half by hand ends `$S/step-tick.sh <n>`

Read the issue body into `.tdd/issue-<n>-body` first, with `gh api repos/{owner}/{repo}/issues/<n> -q .body > .tdd/issue-<n>-body`.

Then run `$S/skill-edit-step.sh` on the issue body, `.tdd/issue-<n>-body`, the step's unit, and then every pin file the step names.

On exit 0 or 3, tick the step and commit the ticked ledger, with the subject `chore: skill-edit — <step summary> (#<n>)`.

On exit 1, bail with `cause=revise-exhausted`, as an exhausted revise, unless the runner printed a `skill-edit-step.sh: row-untraced:` line (under `$S/run-step.sh`, it is in `.tdd/skill-edit-<n>.out`): then bail with `cause=row-untraced`, naming the row.

On exit 2 (a bad argument, budget or heading, or no answer), bail at once, and never relaunch the runner or spend `VERI_STUCK_RETRIES` on it. `$S/run-step.sh` prints `out=.tdd/skill-edit-<n>.out refusal=yes|no` on the line before its `seam=skill-edit-half code=2` line: `refusal=yes` means the runner printed a refusal message, and that file holds it. When the runner printed a refusal message, the bail is a process failure with `cause=skill-edit-refused`, naming the refusal; a bare exit 2 with no refusal message bails as a system failure with `cause=no-verdict`.

A killed or stuck author leaf is still retried under `VERI_STUCK_RETRIES` by the `supervise.sh` launch inside the runner, before that exit 2 reaches the conductor.

A resumed run redoes an unfinished skill-edit step from its start, with its budget reset.

For a skill-edit step whose ledger line carries `⟦added⟧`, run `$S/skill-edit-step.sh` with `--added` and the step's text, before the issue body and the unit.

The refusal holds only for the rest: an added step bringing rows new to an already-passing unit's list is committed with its regrade and no author (exit 3, ticked), one whose text names a prose change runs with `--change`, and any other whose grade passes before any author ran, or that has nothing left to commit, gets exit 2 and is bailed, never ticked.

The step's own text never reaches the author or the grader.

When a skill-edit step's text names a change to the prose, a sentence to delete or reword, run `$S/skill-edit-step.sh` with `--change` and that change, so an author runs even on a unit that already grades PASS.

A skill-edit step's unit may be a heading unit, `<file>#<heading>`: a section of a file that a `REQUIREMENTS.md` claims with a `## <file>#<heading>` heading. The issue's `## Requirements` then names that unit under `### <file>#<heading>`, never under the whole-file `### <file>`, and the step's unit you pass to `$S/skill-edit-step.sh` is that `<file>#<heading>`.

`skill-edit-step.sh` runs the `trace-rows` leaf after the author's exit 0, and on the added-rows path that runs no author, in both cases before the grade. The leaf gets the rows and sentences the step changed, never the step's text or the author's report.

When every line of the trace's answer is `TRACED` or `NOT-CODE`, the step goes on to the grade. An `UNTRACED` row bails `row-untraced`, exit 1. Otherwise an `UNTRACED` sentence goes back to the author with its line, spending one attempt of `VERI_SKILL_EDIT_BUDGET`. A missing or unparseable answer takes the no-verdict route.
