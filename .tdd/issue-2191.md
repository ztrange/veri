# Plan for #2191 — #1977's event_log move changed dashboard.record_lines and stop_reason's blank-log failure, and left two dead except branches

- [ ] dashboard.record_lines returns, byte for byte, every line of the events log it kept before #1977 (each line that parses as JSON, raw bytes unchanged, invalid UTF-8 replaced only at decode), including a JSON line that is not an object and a line holding non-ASCII text, still reading the log through event_log rather than opening it in dashboard.py; pinned by a small unit case ⟦criterion 1⟧
- [ ] stop-reason.sh given an events log of only blank lines exits as it did before #1977 (exit 2, a refusal on stderr, nothing on stdout), pinned by a process case driving the stop-reason.sh entry point ⟦criterion 2⟧
- [ ] The unreachable except UnicodeDecodeError in supervise.py's red_awaits_pass and in wrong_test_route.py's _rerouted are removed, each keeping its except OSError ⟦diff-checked⟧ ⟦criterion 3⟧
