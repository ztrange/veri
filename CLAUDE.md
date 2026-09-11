# veri — working notes for agents

A Claude Code skill suite that solves one GitHub issue under strict TDD. The whole
product is `skills/solve-issue/`: a procedure in English (`SKILL.md`) that Claude
follows, plus eleven bash scripts it calls. Read `CONTEXT.md` for the glossary — the terms
there (conductor, leaf, supervisor, verdict, ledger, bail) are used precisely everywhere.

## Commands

| | |
|---|---|
| `make test` | The shell unit suites. **This is also the command veri detects when run against its own repo**, so it must stay green — a red baseline makes the conductor refuse to start. |
| `make docs` | Regenerate `docs/walkthrough.html` from the scripts. |
| `make docs-check` | Two phases: the docs build guards still fire, then the committed page still matches a fresh build — and still agrees with the phases `build-verify-prompt.sh` accepts and the revise budget `SKILL.md` sets. |

`docs-check` is deliberately **not** part of `test`, for the reason in the row above:
documentation drifting behind code must never block a TDD run.

## The one trap

**`docs/walkthrough.html` is generated. Never edit it by hand** — `make docs-check` will
fail, and your edit is lost on the next `make docs`. To change that page:

- prose, per-script commentary → `docs/wt/commentary.py` (chunks keyed by line range)
- the bash reference entries → `docs/wt/primer.py`
- styling / the tooltip layer → `docs/wt/style.css`, `docs/wt/app.js`
- then `make docs`

The build **fails rather than emitting a wrong page** if a script's commentary chunks
stop covering lines 1..N exactly once, or if a `{{p-id|…}}` names an entry that does not
exist. So editing a script means running `make docs` and fixing what it reports.

## Exit codes are the API

Every script speaks the same four codes, and the conductor branches on them. Preserve this
when touching any script:

| | |
|---|---|
| `0` | success, or `PASS` |
| `1` | a clean negative — the leaf ran and failed, the verifier said `REJECT`. A real answer. |
| `2` | **no answer could be obtained** — killed-stuck, unparseable verdict, bad arguments |
| `3` | nothing to do — no unchecked step, no matching checkbox. Not an error. |

The gap between `1` and `2` is the load-bearing one: it is the difference between a
**process** failure (the methodology spoke) and a **system** failure (the plumbing broke),
which `classify-bail.sh` turns into the label a human reads. Never collapse them.

## Versions are tags, and nothing else

A version is an annotated git tag `vN.M` whose **message is the capability**, in the issue's
own words. There is no `VERSION` file, no changelog, and nothing to keep in sync: the
walkthrough's capability index is computed from the tags and the `feat:`/`fix:` commits in
each tag's range. One merged issue is one capability is one minor bump; documentation, test
and refactor PRs get no tag, because a version means what veri can *do* changed.

The tag is cut when a PR lands (the `merge` skill does it), not in a separate release step.
Two traps, both already cost something once:

- **`git tag --sort=-v:refname`, never plain `sort`** — lexically `v0.9` outranks `v0.10`.
- **Backfilling needs `GIT_COMMITTER_DATE`** — an annotated tag's date is the *tagger's*,
  so retro-cut tags otherwise all claim to have shipped today.

## Invariants worth not breaking

- **Every leaf is launched through `supervise.sh`** — never `run-leaf.sh` or `claude`
  directly. Stuck-detection policy lives in exactly one place only because nothing
  bypasses it.
- **The verifier is blind by construction.** `build-verify-prompt.sh` takes only a phase,
  the spec file, the test path and a test id. There is no parameter for the developer's
  rationale, so it cannot leak. Adding one would silently end the guarantee.
- **The committed ledger is the source of truth** for which steps are done, ticked
  atomically with each step's green commit. The GitHub issue only mirrors it.
- Two retry budgets, deliberately separate: `VERI_STUCK_RETRIES` (liveness — the leaf
  never answered) and `REVISE_BUDGET` (verdict — it answered and was rejected).

## Testing idiom

Plain-shell asserts, zero dependencies, under
`skills/solve-issue/scripts/tests/` — thirteen files for twelve scripts
(`supervise.sh` has a second suite for its retry axis). All thirteen keep `pass`/`fail`
counters, print `FAIL - <name>` with a diff, and end with a count. Match that style
rather than introducing a framework.

Where a test would otherwise need a real model or a real clock, it injects instead:
`CLAUDE_BIN` swaps in a stub binary, and `VERI_HEARTBEAT` / `VERI_TIMEOUT` /
`VERI_STUCK_RETRIES` shrink the supervisor's windows so nothing waits on wall time. That
is why every tunable is read as `${VAR:-default}`.

A guard or a failure path that has never been watched to fail is not tested. Break it on
purpose, see the test go red, put it back.
