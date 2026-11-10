### with several stall-window-old run dirs of closed issues over several polls, dispatch reads issue states at most once per poll, never once per run dir, pinned by a small in-process case counting `dispatch.issue_states` calls through a spy ⟦criterion 3⟧
- test-only | extract the shared stall-window-old run-dir and monkeypatch setup repeated across the three new #3551 cases into a helper
