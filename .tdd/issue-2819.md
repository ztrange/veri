# Plan for #2819 — A case's child process with a hand-built env never reaches a real gh or curl

- [x] A child process started by a case with a hand-built env whose PATH includes a directory holding gh gets the refusal, not that gh, pinned by a process case whose stand-in gh lives in a temporary directory outside the pytest basetemp so it holds on macOS and Linux alike and fails on the current code ⟦criterion 1⟧
- [x] A child process started by a case with a hand-built env whose PATH includes a directory holding curl gets the refusal, not that curl, pinned by a process case whose stand-in curl lives in a temporary directory outside the pytest basetemp ⟦criterion 1⟧
- [x] Removing the guard reddens the case, watched going red and restored ⟦human-owed⟧ ⟦criterion 2⟧ — discharged at review: network_guard.py:53 disabled, gh+curl cases 2 failed, restored 2 passed (PR #2823 body)
