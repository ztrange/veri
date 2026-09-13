# Plan for #125 — Docs catch up on their own cadence: the build tolerates uncovered lines, a script PR owes no page, and a catch-up job files the docs debt into the docs pool

- [x] a script line no commentary chunk covers builds instead of failing: it renders plain with a visible "commentary owed" mark, and the build's stderr summary lists it as `owed: <script> L<a>–<b>`
- [x] a `{{p-id|…}}` reference that names no entry still fails the build — a typo is not debt
- [x] an uncovered run of lines between two chunks, mid-file, is owed the same way as one at the end of the file: rendered plain and marked, and listed as `owed: <script> L<a>–<b>` with the interior range
- [x] `docs/merge-gates.sh` owes `docs-fresh` for nothing under `skills/`, still owes both gates for a change under `docs/wt/`, `build-walkthrough.py` or `docs/tests/`, and its header, its tests and CLAUDE.md say so
- [ ] `docs/docs-owed.sh` lists the committed page's debt — uncovered script lines, scripts whose blame is newer than the page's build, tags the index does not list — one item per line, and exits 3 with nothing on stdout when there is none
- [ ] `docs/docs-owed.sh --file` opens one issue in the `ready-for-agent:docs` pool titled `Docs: catch the walkthrough up to <sha>` whose body is that list, and updates the open one on a later run rather than opening a second — testable without the network through `VERI_GH_JSON` fixtures
- [ ] an ADR in `docs/adr/` records the reversal: why the build once failed on a gap, what changed, and the page's new promise — source always verbatim, prose may lag and says so
