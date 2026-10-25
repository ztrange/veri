# Plan for #2395 — report-cache reads a page capped at 1000 by the search API as the last page, and writes a truncated cache as complete

- [ ] With `gh_issue_list` faked to cap any `--search` call at 1000 rows whatever `--limit` requests, a refresh over more than 1600 issues sharing one `updatedAt` second either caches every issue in the dataset or exits non-zero without writing a cache, never exiting 0 with a cache short of the dataset; pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_report_cache.py ⟦criterion 1⟧
