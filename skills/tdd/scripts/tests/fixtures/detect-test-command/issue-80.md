## Parent

Walkthrough diagrams thread. Follows https://github.com/ztrange/veri/issues/77, https://github.com/ztrange/veri/issues/78 and https://github.com/ztrange/veri/issues/79, which add the per-stage diagrams this one points at.

## What to build

The orientation map (`INTRO_HTML`, `<h3 id="map">Map of the seventeen scripts</h3>`, `docs/wt/commentary.py` ~line 260, SVG at ~271-308) draws five stages and names eleven scripts. Six are absent — `issue-worktree.sh`, `ensure-run-state-ignored.sh`, `detect-test-command.sh`, `build-develop-prompt.sh`, `refactor-budget.sh`, `solvable-issues.sh` — so the heading is false and a reader counting boxes concludes the page is stale. Do **not** cram them into the map; it is the one picture that has to stay readable at a glance. Instead:

- retitle the map for what it is — the eleven scripts of one cycle — and have the count computed, not typed (the masthead already computes `n_scripts`; the map's own count is the number of scripts it names, which the build can assert against the SVG's text)
- add one sentence under it naming what the map leaves out and linking each of the three groups to the stage intro that draws it: stage 0 (setup), stage 3 (the developer-side builder), stage 5 (budgets and rung 2)

## Behaviour

- The heading no longer states a number the figure does not match; the number it states is derived at build time from the scripts the SVG names, and the build fails if a script name in the SVG is not one of the seventeen (the same fail-rather-than-emit rule the commentary coverage check follows).
- The sentence under the map links to `#s0`, `#s3` and `#s5`.

## Acceptance criteria

- [ ] the map's heading count equals the number of distinct script names inside the map SVG, computed by the build; a guard in `docs/tests/build-guards.test.sh` renames one script inside the SVG and watches the build refuse
- [ ] the paragraph under the map links to `#s0`, `#s3` and `#s5` and names the six scripts the map omits
- [ ] `make docs`, `make docs-test` and `make docs-check` pass

## Notes

`docs/wt/commentary.py` (`INTRO_HTML`), `docs/build-walkthrough.py` (the count and the guard). Test command: `make docs-test`. `docs/walkthrough.html` is GENERATED — never hand-edit it.

## Blocked by

- https://github.com/ztrange/veri/issues/77
- https://github.com/ztrange/veri/issues/78
- https://github.com/ztrange/veri/issues/79
