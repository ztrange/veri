### A change to any skills/tdd/scripts/prompts/*.md, even one no suite names, prints skills/tdd/scripts/tests/unit/emitted-text.test.sh ⟦criterion 3⟧
- test-only | the four `_1024` cases in test_affected_suites.py (lines 122–165) repeat the same setup: patch `fake_git` for one path, chdir, mkdir `tests/unit`, write an empty `other.test.sh`, write one unit suite, then assert `(main(...),) + readouterr()` against a single unit-suite path. That setup could become one helper.
### A change to skills/tdd/scripts/<name>.sh with no suite of its own does not print a suite whose only mention of it is lib/<name>.sh ⟦criterion 4⟧
- test-only | the four newest `_1024` cases in test_affected_suites.py repeat the same fake_git/chdir/mkdir tests/unit setup, which could become one fixture
- out-of-scope | the harness.sh rule `[s for s in every_suite() if has_line(...)]` is the same scan per line and could fold into a line-wise variant of suites_matching, but that code predates this cycle
