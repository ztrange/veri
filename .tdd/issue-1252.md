# Plan for #1252 — strip_session_env deletes all of PATH when one entry holds the session id, so a stub dir on PATH can let the real claude run

- [x] strip_session_env given a session id keeps PATH, dropping only the PATH entries that carry the session id and keeping the rest in their order ⟦criterion 1⟧
- [x] strip_session_env exempts PATH from the session-id value scan altogether (superseding the step above's entry dropping), so PATH reaches the child unchanged: a stub claude in a PATH directory whose path holds the session id runs ahead of a later claude on PATH, and PATH is never left empty (in-process pytest in tests/py/test_session_env.py) ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending
