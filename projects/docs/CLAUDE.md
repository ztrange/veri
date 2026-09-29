# docs project — working notes for agents

The walkthrough pipeline: it builds `projects/docs/walkthrough.html` from the scripts under
`skills/tdd/scripts/` and this repo's history. Same repo, same blame, same tags as veri itself;
`docs/adr/` at the repo root stays veri's own record. Read the root `CONTEXT.md` for the glossary.

## Commands

Run from the repo root.

| | |
|---|---|
| `make -C projects/docs docs` | Regenerate `projects/docs/walkthrough.html` from the scripts. **By hand only**: a development run's `VERI_TEST_CMD` makes the target refuse with exit 2. |
| `make -C projects/docs test` | Every suite under `projects/docs/tests/`, globbed, each of which must end in its `<n> passed, <m> failed` count line; a suite that never reaches it fails the target, named. |
| `make -C projects/docs fresh` | Rebuild once and compare to the committed page — the half of `check` that a merge usually owes. |
| `make -C projects/docs check` | `test`, then `fresh`. |

## The one trap

**`projects/docs/walkthrough.html` is generated. Never edit it by hand** — `make -C projects/docs check`
will fail, and your edit is lost on the next `make -C projects/docs docs`. To change that page:

- prose, per-script commentary → `projects/docs/wt/commentary.py` (chunks keyed by line range)
- how the source is coloured → `projects/docs/wt/bashlex.py` (four token classes, no more)
- the bash reference entries → `projects/docs/wt/primer.py`
- styling / the tooltip layer → `projects/docs/wt/style.css`, `projects/docs/wt/app.js`
- then `make -C projects/docs docs`

The build **fails rather than emitting a wrong page** if a `{{p-id|…}}` names an entry that does
not exist, or if a commentary chunk claims lines a script does not have. A line **no** chunk claims
renders with `commentary owed` in its note column, and the build prints `owed: <script> L<a>–<b>`
on stderr and exits 0: prose may lag behind code.

**This is the documentation lane's work, and a development run is not in it.** A leaf or conductor
step whose test command is not a docs target never edits the page or its inputs and never runs
`make -C projects/docs docs`.

## Docs-suite rules

- Plain-shell asserts under `projects/docs/tests/`, zero dependencies, `pass`/`fail` counters, ending
  in `<n> passed, <m> failed`. A suite added there owes no Makefile edit: the target globs.
- **A suite here never reads a path in the generated tree** except the pipeline's own inputs under
  test; a path only written into a fixture as text is not a read.
- **A walkthrough build asks git once per script, once per tag, and eight times besides.**
  `projects/docs/tests/build-guards.test.sh` pins that as a budget; ask the table
  `gitmeta._shipped()` already built instead of a new process per commit.
- **A tag is the one input to the page that changes without a commit**, so cutting one leaves
  `projects/docs/walkthrough.html` behind and `make -C projects/docs check` red until someone runs
  `make -C projects/docs docs`. The hook under `projects/docs/hooks/` only notices.
- **A regen commit built at the tag isn't the fixpoint.** Recipe: `make -C projects/docs docs && git commit`,
  then `make -C projects/docs docs && git commit --amend --no-edit`.
