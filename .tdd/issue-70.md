# Plan for #70 — Walkthrough: "since vX" reading mode

- [x] `gitmeta.py`'s `hunks()` returns each hunk's last line as well as its first, so a hunk has an extent
- [x] the build emits an inverted map `window.__VERI_HUNKS__` (tag to script, first line, last line, description) with one entry per `.hunk` span, and `docs/tests/build-guards.test.sh` guards that the counts agree
- [x] `docs/wt/style.css` styles `.l.hunk` with a gutter chip carrying the tag text and a faint left rule spanning the hunk's extent
- [x] with no version chosen and nothing stored, the page renders as it does today plus the visible marks, with no dimming
- [x] choosing a version dims every hunk not tagged later than it and lights every hunk that is, ordered by git's version sort so `v0.10` ranks after `v0.9`, and a hunk tagged X itself is not lit
- [x] choosing a version collapses the capability index to the versions after it, and each remaining version row links to every hunk that version touched
- [x] `n` and `p`, and two buttons in the crumb bar, walk the lit hunks in page order
- [x] the URL hash carries `since=vX`, and reloading that URL restores the mode
- [x] the "mark read up to vX" button persists the choice in `localStorage` and the next load opens in since-mode; a browser that blocks storage still renders the plain page
- [x] one sentence next to the control says since-mode answers which capabilities changed, not which bytes changed
- [ ] pressing `n` or `p`, or clicking the next/previous buttons the crumb bar carries, scrolls the reader to the next or previous stop of the since-mode walk, and the buttons are absent from the crumb bar when no version is chosen
- [ ] `make docs` regenerates the page, and `make docs-check` and `make docs-test` pass
