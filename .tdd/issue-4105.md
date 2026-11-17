# Plan for #4105 — PRD 031.4: affected-suite selection works in a repo that is not veri

- [x] outside veri's own tree, a changed test path that exists prints itself ⟦criterion 1⟧
- [x] outside veri's own tree, a changed non-test path selects every non-ignored test file naming its stem as a whole word, `-` and `_` alike, skipping `.git`, `.tdd`, `.venv` and `node_modules` ⟦criterion 2⟧
- [x] outside veri's own tree, a `.tdd/` path selects nothing and a range of only such paths exits 3 ⟦criterion 3⟧
- [ ] outside veri's own tree, a non-test path no test names widens to every test file with one stderr line; no test file at all exits 3 with that line ⟦criterion 4⟧
- [ ] the affected-run line and the single-suite lead render from a placeholder: the repo's one-test-file command per path (the all tier when undeclared) outside veri, today's text in veri ⟦criterion 6⟧
- [ ] the placeholder is computed in-process from the tree's CLAUDE.md, and a `.tdd/` marker never reaches the prompt ⟦criterion 7⟧
- [ ] a process case in a scratch foreign repo pins criteria 1, 2 and 4 on stdout, stderr and exit, watched red with the foreign rules removed ⟦criterion 8⟧ ⟦criterion 9⟧
- [ ] SCRIPTS.md gains an affected-suites.sh entry and `_run-suite-lead.md` states its rendered runner, graded ⟦criterion 10⟧
