## What to build

### The defect

Open https://ztrange.github.io/veri/#since=v0.10 and press `n`. The first stop is `ensure-run-state-ignored.sh`'s v0.12 edits. `issue-worktree.sh`, which sits before it on the page and arrived whole in v0.18, is never a stop, never lit, and never listed: neither is `wait-leaf.sh`, `extract-result.sh`, `verify.sh` or any other script newer than the version the reader chose.

The cause is the floor in `docs/wt/gitmeta.py`'s `hunks()`: a run tagged at or below the file's own `since` is dropped (`tags.index(tag) <= floor → continue`), on the reasoning that the header badge already says "since v0.18". That is right for the badge. It is wrong for since-mode, which knows only the hunk map (`window.__VERI_HUNKS__`) and so cannot tell a script the reader has already read from one that did not exist when they read. The mode answers "which lines of scripts you knew changed" and never "which scripts are new to you", which is most of the answer for a reader more than a few versions behind. `chunk_marks` in `docs/build-walkthrough.py` copied the same floor for #71's commentary chips.

Keep the floor in `hunks()` (a hunk inside a new script is redundant with its header). Fix the mode: a script whose `since` ranks after the chosen version is one whole-script stop.

### Two smaller gaps, same layer

#70 built the decision layer (`window.__VERI_SINCE__`: `lit`, `index`, `walk`, `since`, `choose`, `markRead`) and pinned it through the page's JS, because the guard harness had no DOM to click. Nothing was ever pinned as a DOM fact, so nothing renders it: there is no version picker and no "mark read up to vX" button anywhere in the markup, `lit()` paints nothing (no `lit`/`dim` class, no CSS), and `index(since)` is called by nothing, so the capability index never collapses. The only visible sign of the mode is the pair of `↑`/`↓` buttons in the crumb bar.

## Behaviour

- The build already renders each script's `since` badge; emit it to the page too (e.g. `data-since` on the script's header, or a `window.__VERI_SINCE_OF__` map), so the client can rank a script against the chosen version.
- A script whose `since` ranks after the chosen version: its header is a mark lit for that reader; `n`/`p` and the crumb-bar buttons reach it in page order before any hunk inside it; every line of its listing and every commentary chunk beside it counts as lit; the index row of the version it arrived in lists it as `<script> · new`.
- Choosing a version paints the answer in the DOM: every hunk mark, commentary chip and new-script header carries class `lit` or `dim`; index rows that `index(since)` does not return are hidden; at rest (no hash, nothing stored) nothing is dimmed and every row shows.
- The capability index carries the control: a `<select>` whose options are the versions newest first plus a none option, wired to `choose(tag)`, showing `since()`'s answer at load and after `hashchange`; beside it a `<button>` reading "mark read up to vX" (X the newest version) wired to `markRead()`. Both found by their visible text or accessible label, never by class.
- Degrades like the rest of the layer: no git or no tags → no control, no paint, page still builds.

Test through the wired-DOM stub #70 built (`VERI_ASK_WIRED` in `docs/tests/build-guards.test.sh`); it needs `change` and `hashchange` delivery added. The sandbox needs a script added at a later tag than the one the case opens at.

## Acceptance criteria

- [x] a sandbox with a script added at v0.3, opened at `#since=v0.2`, walks to that script's header before any hunk inside it, and its v0.3 index row lists `<script> · new`; at `#since=v0.3` the same script is neither a stop nor listed
- [x] choosing a version applies `lit`/`dim` to every hunk mark, commentary chip and new-script header per the tag-order rule and hides the index rows `index(since)` does not return; at rest nothing is dimmed or hidden
- [x] the capability index carries the version `<select>` and the "mark read up to vX" button, wired so that changing the select updates the hash and the paint without a reload, and the select reflects the hash at load
- [x] `make docs` regenerates the page, and `make docs-check` and `make docs-test` pass

## Notes

`docs/wt/app.js` (since layer, stepper), `docs/build-walkthrough.py` (`render_order_json`, `chunk_marks`, the badge renderer near `vbadge`), `docs/wt/style.css`, `docs/tests/build-guards.test.sh` (cases 23, 27 and the `dom_stub`/`ask_page` harness). Test command: `make docs-test`. `docs/walkthrough.html` is GENERATED — never hand-edit it.

Not blocked by #71, but #71's open branch (`tdd/71-walkthrough-version-the-commentary-too`, 4 of 6 steps) touches the same layer and must be rebased over this once it lands.

## Blocked by

none
