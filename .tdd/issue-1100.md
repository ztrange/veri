# Plan for #1100 — run-leaf: the session strip unsets GIT_CONFIG_GLOBAL, CLAUDE_BIN or VERI_LEAF_MODEL when its value contains the session id

- [ ] With CLAUDE_CODE_SESSION_ID set and a TMPDIR whose path contains that id, run_leaf.main launches the leaf with GIT_CONFIG_GLOBAL still set to its private copy of ~/.gitconfig (the pinning case in tests/py/test_run_leaf.py that expects it unset changes its expectation)
- [ ] With CLAUDE_CODE_SESSION_ID set, a CLAUDE_BIN whose value contains that id is still the binary run_leaf.main launches, not plain claude (the pinning case's expectation changes with it)
- [ ] With CLAUDE_CODE_SESSION_ID set, a VERI_LEAF_MODEL whose value contains that id still reaches the leaf as --model <value> (the pinning case's expectation changes with it)
