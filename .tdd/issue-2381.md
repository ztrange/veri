# Plan for #2381 — A merge-lock waiter takes the lock after a slow release, and the race case never flakes under load

- [ ] A merge-lock.sh taker waiting on a held lock exits 0 holding the lock once the holder releases, however long the holder waited before releasing and even when the release removes the lock while the waiter is reading its holder record: pinned by a delayed-release two-takers race case in skills/tdd/scripts/tests/py/test_merge_lock_process.py (a process case, a real merge-lock.sh shim), whose outcome does not depend on machine load ⟦criterion 1⟧
