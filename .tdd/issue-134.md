# Plan for #134 — Walkthrough: every script on disk is on the page — one with no commentary renders verbatim as owed, and docs-owed.sh lists it

- [ ] projects/docs/build-walkthrough.py renders a skills/tdd/scripts/*.sh that has no commentary.SCRIPTS entry in a sandbox build: exit 0, a section whose id is derived from the filename, and the script's source verbatim ⟦criterion 1⟧
- [ ] that unlisted script's whole file sits under the existing "commentary owed" mark, and the build's stderr `owed:` summary names it (owed: <script> L1–<last>) ⟦criterion 1⟧
- [ ] the masthead and table-of-contents counts (script count, total source lines, the upkeep table and rail) include the unlisted script, and an unlisted script adds no git question beyond the one-per-script budget ⟦criterion 1⟧
- [ ] projects/docs/check-walkthrough.py passes on a page built from a sandbox carrying an unlisted script ⟦criterion 1⟧
- [ ] projects/docs/docs-owed.sh lists a script present on disk but absent from commentary.SCRIPTS as `unlisted: <script>`, whether or not the page has been rebuilt since ⟦criterion 2⟧
- [ ] projects/docs/docs-owed.sh still exits 3 with no output when every script is listed and covered ⟦criterion 2⟧
- [ ] `make docs-check` passes on this repo with leaf-timeout.sh (and the other unlisted scripts) rendered as owed, the committed projects/docs/walkthrough.html regenerated to match — a docs-lane step, run by the docs regen recipe ⟦criterion 3⟧
- [ ] `make docs-check` passes on this repo with leaf-timeout.sh rendered as owed: regenerate projects/docs/walkthrough.html with `make -C projects/docs docs` from a human shell, then run `make docs-check` ⟦human-owed⟧ ⟦criterion 3⟧
