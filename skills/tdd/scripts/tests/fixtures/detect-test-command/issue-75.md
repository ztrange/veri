## Parent

Follow-up to #69 (the pitch section). Not blocked by any open issue.

## What to build

`gitmeta.solved_by_itself()` counts `plan: scope #<n>` commits reachable from `HEAD`. #69's
first verify-refactor rejected on exactly this and the objection stands: every veri run's
first commit on its branch is a plan commit, so on every future veri PR the figure is one
higher than the committed page says, and `make docs-check` — which rebuilds and demands a
byte-identical page — goes red on that PR until it also carries a `make docs` commit it had
no other reason to make. That is the per-commit treadmill `gitmeta.py`'s own header rules
out. The revise to counting on `main` was rejected too, correctly, as a behaviour change
inside a refactor — and it would only move the window to the merge: `main` red after every
veri-solved PR lands, with no tag to hang the regen on.

Count at the **latest tag** instead: `plan: scope` commits reachable from the newest
`vN.M` tag (git version sort, never lexical). Then the figure moves only when a tag is
cut, which already leaves `docs/walkthrough.html` behind and is already closed by the
post-tag regen recipe in CLAUDE.md — one window instead of two, and every PR builds a page
byte-identical to `main`'s. The cost is that an untagged issue (docs, tests, refactor) is
not counted until the next tag contains it; that is consistent with "a version is a
capability" and with the capability index, which already attributes work to the tag that
shipped it.

## Behaviour

- `solved_by_itself(root)` counts on `<latest tag>^{commit}`, reading the tag list the
  module already sorts with `--sort=v:refname`; a tree with no tags answers None (no
  figure), exactly as a tree with no git does today.
- A plan commit on the current branch, or on `main` past the latest tag, does not change
  the figure.
- The pitch's sentence stays as it is; only the number's basis changes. The
  `docs/wt/gitmeta.py` header's anti-treadmill note names the tag as the basis.

## Acceptance criteria

- [ ] in a sandbox repo with a tag, `plan: scope` commits before the tag are counted and
      ones after it (on `main` or on a branch) are not — a guard in
      `docs/tests/build-guards.test.sh` in the suite's own idiom
- [ ] a sandbox repo with commits but no tag builds with the "built with itself" sentence
      present and no `class="solved-n"` figure (the existing case 13 keeps passing)
- [ ] the committed `docs/walkthrough.html` on this branch is byte-identical to a fresh
      build on `main` at the same tag — i.e. the branch's own plan commit does not move the
      figure
- [ ] `make docs`, `make docs-test` and `make docs-check` pass

## Notes

`docs/wt/gitmeta.py` (`solved_by_itself`, `read`), `docs/tests/build-guards.test.sh`.
Test command: `make docs-test`. `docs/walkthrough.html` is GENERATED — never hand-edit it.

## Blocked by

Nothing — but it edits the function #69 added, so take it after PR #74 lands.
