# Plan for #1376 — PRD 009 C7-6: a pytest case that reaches push-branch's retry backoff without VERI_PUSH_BACKOFF fails, named

- [ ] A pytest case that drives push_branch in-process (a direct call or run_cli) into its retry backoff without setting VERI_PUSH_BACKOFF fails, the failure naming that case's node id, instead of sleeping the default backoff; a case that sets VERI_PUSH_BACKOFF still backs off as it sets it — the guard lives in tests/py/conftest.py, no source scan ⟦criterion 1⟧
- [ ] A pytest case that starts push-branch.sh as a real process into its retry backoff without setting VERI_PUSH_BACKOFF fails, the failure naming that case's node id, instead of sleeping the default backoff; a process case that sets VERI_PUSH_BACKOFF still backs off as it sets it — native in pytest, no source scan ⟦criterion 1⟧
- [ ] The full suite is green with the guard in place ⟦full-suite⟧ ⟦criterion 1⟧
