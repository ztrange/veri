### stop_reason runs on an events.jsonl holding one step-added record with no ts and no awake among timed records: it does not raise, skips that record when computing gaps, and still reports the gaps between the timed records; pinned by a small in-process case ⟦criterion 1⟧
- test-only | the new test's run-dir and events.jsonl setup could share a helper with the neighbouring stop_reason tests
