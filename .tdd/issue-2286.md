# Plan for #2286 — report_cache.py's page-size halving has no floor, so a large VERI_PAGE_RETRIES can ask gh for --limit 0

- [x] read_issue_page's page size never drops below 1 whatever VERI_PAGE_RETRIES is: with VERI_PAGE_RETRIES=10, no cache, and a faked gh issue list that fails every --limit (answering [] to --limit 0), refresh makes no --limit 0 call, exits 2, and writes no cache file (a small case in skills/tdd/scripts/tests/py/unit/test_report_cache.py, gh faked in-process) ⟦criterion 1⟧
