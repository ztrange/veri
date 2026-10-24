# Plan for #2272 — report-cache.sh's first refresh writes a partial cache as complete when over 100 issues share one updatedAt second

- [ ] With no existing cache, when 101 or more issues share one `updatedAt` second and older issues sit behind them, a `report-cache.sh refresh` either writes a cache holding every issue or exits 2 leaving no cache file — it never exits 0 with a partial cache; a page that brings nothing new while issues may remain is not taken as the end of the list (a small unit case, `gh issue list` faked in-process) ⟦criterion 1⟧
- [ ] The existing pagination cases in `skills/tdd/scripts/tests/py/unit/test_report_cache.py` are left unchanged by the branch's diff and still pass ⟦diff-checked⟧ ⟦criterion 2⟧
