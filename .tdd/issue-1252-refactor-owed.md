### strip_session_env given a session id keeps PATH, dropping only the PATH entries that carry the session id and keeping the rest in their order ⟦criterion 1⟧
- out-of-scope | delete skills/tdd/scripts/lib/session-env.sh, whose strip_session_env no non-test code sources any more (only veri/session_env.py is called, from run_leaf.py and run_conductor.py), or bring it in line with the Python rule
