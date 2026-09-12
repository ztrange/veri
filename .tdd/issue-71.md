# Plan for #71 — Walkthrough: version the commentary too — a chunk whose prose changed after version X lights up in since-mode beside its source

- [x] `gitmeta` blames `docs/wt/commentary.py` itself: given a chunk's own line span in that file, it answers the version the newest `feat:`/`fix:` commit that last touched any line of the span shipped in, and answers nothing for a span whose only history is `docs:`/`refactor:` commits
- [ ] the build records each chunk's own line span in `commentary.py` when `SCRIPTS` is loaded, and a chunk last changed by a `feat:`/`fix:` commit that shipped after its script's `since` renders with a version chip on the commentary column (`.ann-text`), while a chunk with only `docs:`/`refactor:` history renders none
- [ ] a tree with no tags, or no git, builds with zero commentary marks and the page still builds (guard in `docs/tests/build-guards.test.sh`)
- [ ] since-mode dims or lights commentary marks by the same tag-order rule as source hunks, and `n`/`p` and the crumb-bar buttons walk them in page order together with the source stops
- [ ] a version row in the collapsed capability index lists the commentary chunks that version touched as `<script> · commentary for L<first>–L<last>`, beside the source hunks it already lists
- [ ] `make docs` regenerates the page, and `make docs-check` and `make docs-test` pass
