## Parent

Walkthrough polish thread. Follows https://github.com/ztrange/veri/issues/70 (since-mode), which lights up *source* hunks by
version and leaves the commentary — the half of the page that actually explains veri's
internals — untracked.

## What to build

`docs/wt/commentary.py` is a git-tracked file whose per-script chunks are keyed by line
range. Blame it the way `gitmeta.hunks()` blames the scripts: for each chunk, the newest
`feat:`/`fix:` commit that last touched any of the chunk's prose lines, ranked to the
first tag containing it. A chunk whose commentary shipped in a version later than the
script's own `since` gets a mark — a chip on the commentary column (`.ann-text`), mirroring
the source-side chip from https://github.com/ztrange/veri/issues/70 — and participates in since-mode: dimmed or lit by the same
tag-order rule, walked by the same `n` / `p` keys, listed under the version row as
`supervise.sh · commentary for L44–57`.

Non-behaviour commits (`docs:`, `refactor:`) hide what they sat on, same rule as the scripts:
a prose tidy is not a new explanation. This will under-report wording-only rewrites; that is
the same trade the source side already makes, and stays consistent with "a version is a
capability".

## Behaviour

- Blame runs on `docs/wt/commentary.py` itself, mapping chunk dict line ranges in that file
  (not the script line ranges they describe) to commits. The build needs to know each
  chunk's own line span in `commentary.py` — record it when the `SCRIPTS` structure is
  loaded (e.g. via `inspect`/`ast` on the module source), or accept a small explicit
  marker per chunk if that is simpler and guarded.
- Degrades like everything else: no git or no tags → no commentary marks, page still builds.

## Acceptance criteria

- [x] a commentary chunk last changed by a `feat:`/`fix:` commit that shipped after its
      script's `since` renders with a version chip on the commentary column; a chunk whose
      only history is `docs:` / `refactor:` commits renders none
- [ ] since-mode from https://github.com/ztrange/veri/issues/70 dims/lights commentary chunks by the same tag-order rule and the
      version rows list them
- [x] `docs/tests/build-guards.test.sh` gains a guard that a tree with no tags builds with
      zero commentary marks
- [ ] `make docs` regenerates the page, `make docs-check` and `make docs-test` pass

## Notes

`docs/wt/gitmeta.py` (blame + ranking already exist for scripts), `docs/build-walkthrough.py`,
`docs/wt/app.js`, `docs/wt/style.css`. Test command: `make docs-test`.
`docs/walkthrough.html` is GENERATED — never hand-edit it.

## Blocked by

- https://github.com/ztrange/veri/issues/70
