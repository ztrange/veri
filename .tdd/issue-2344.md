# Plan for #2344 — merge-lock.sh take sees a reused holder pid as stale and leaves no staging directory behind

- [x] `merge-lock.sh take` treats a lock as stale when its recorded pid is alive but the live process's start time differs from the one in the record, and reports it on stderr as `stale lock: <record>` exactly as it reports a dead holder today; pinned by a case whose faked holder pid is alive with a different recorded start time ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `merge-lock.sh take` leaves no `.tdd/.merge.lock.*` staging directory behind on any exit, its exit 2 for a missing, unreadable or malformed holder record included; pinned by a broken-record case that checks no staging directory remains ⟦criterion 2⟧
