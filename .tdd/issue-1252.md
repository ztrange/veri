# Plan for #1252 — strip_session_env deletes all of PATH when one entry holds the session id, so a stub dir on PATH can let the real claude run

- [x] strip_session_env given a session id keeps PATH, dropping only the PATH entries that carry the session id and keeping the rest in their order ⟦criterion 1⟧
