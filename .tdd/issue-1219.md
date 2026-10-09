# Plan for #1219 — run_conductor.py: SIGINT or SIGHUP while claude runs kills it with a traceback, or orphans it, where run-conductor.sh waited and cleaned up

- [x] With SIGINT sent to the run-conductor.sh launcher alone while its claude runs, the launcher waits for claude to finish, removes the skill snapshot directory, prints no traceback on stderr, and exits with claude's own status ⟦criterion 1⟧
- [x] With SIGHUP sent to the run-conductor.sh launcher alone while its claude runs, the launcher waits for claude to finish, removes the skill snapshot directory, prints no traceback on stderr, and exits with claude's own status ⟦criterion 1⟧ ⟂ refactor pending
- [ ] The SIGINT and SIGHUP behaviour of the bash run-conductor.sh at #1077's base was observed by hand before the change, and that observation is recorded in the PR body ⟦human-owed⟧ ⟦criterion 1⟧
