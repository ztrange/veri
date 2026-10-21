# Plan for #1905 — test_metrics.py: the two cases that read the recorded conductor log share one loader

- [x] The two cases in test_metrics.py that read conductor-opus-5-5-recorded.log (test_issue_1859_the_opus_5_5_price_entry_matches_… and test_issue_1868_a_finished_conductor_sessions_per_turn_dollars_…) load the fixture's text and its result record through one shared helper in test_metrics.py, the fixture path spelled once; every assertion unchanged, no production change, no file outside tests/ changed ⟦diff-checked⟧ ⟦criterion 1⟧
