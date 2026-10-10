# Plan for #1289 — Delete lib/session-env.sh: its strip_session_env is dead and disagrees with veri/session_env.py

- [ ] `skills/tdd/scripts/lib/session-env.sh` is deleted, and no file left in the repository references it: `git grep -n 'session-env.sh'` prints nothing, the pytest case in `tests/py/test_session_env.py` that read the bash file's `SESSION_VARS` no longer reads it (its remaining assertions on `veri/session_env.py` kept), and no suite that tested only the bash file remains ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] `make test` stays green after the deletion ⟦full-suite⟧ ⟦criterion 1⟧
