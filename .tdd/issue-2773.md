# Plan for #2773 — A verifier leaf refused for an unreadable file leaves its edits in the tree

- [x] After a refusal for an unreadable file left by a verifier leaf, a tracked file the leaf edited holds its before-snapshot content and the exit is still 2: a process case in `skills/tdd/scripts/tests/py/test_verify.py` with a stub `CLAUDE_BIN` in a real git scratch repository, failing on the current code ⟦criterion 1⟧
- [x] The refusal for an unreadable file left by a verifier leaf names that file on stderr: a process case in `skills/tdd/scripts/tests/py/test_verify.py` with a stub `CLAUDE_BIN` in a real git scratch repository ⟦criterion 2⟧ ⟂ refactor pending
