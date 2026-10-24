### `merge-lock.sh take` creates `.tdd/merge.lock` in the repository's main working tree (also when run from a linked worktree) atomically, as a directory, recording inside it the holder's pid (the caller's: the parent process of `merge-lock.sh`, or the pid `--pid <pid>` names), the host and the start time, and exits 0; `merge-lock.sh holder` then prints that pid, host and start time and exits 0 while that pid is live ⟦criterion 1⟧
- test-only | extract the repeated scratch repo and linked-worktree setup in test_merge_lock.py into a fixture
### `merge-lock.sh holder` exits 1 when the lock's recorded pid is dead on this host, printing the record marked as a stale lock ⟦criterion 1⟧
- merge_lock.py: split main() into per-verb functions once release is added (no duplication to remove yet)
- test-only | extract the repeated repo+linked-worktree setup (init, empty commit, worktree add) in test_merge_lock.py into a fixture
### `merge-lock.sh release` removes `.tdd/merge.lock` and exits 0 only when the caller (identified as `take` identifies it) is the recorded holder; a caller who is not the holder gets exit 1 with the lock left in place, and `release --force` removes the lock whoever holds it ⟦criterion 1⟧
- test-only | extract the repeated repo+worktree setup in test_merge_lock.py into a fixture
applied | eee894e88df7b08f26a2dc05dc6864ffbe1d8e27 | merge_lock.py: split main() into per-verb functions once release is added (no duplication to remove yet)	refactor: split merge_lock.py main() into per-verb functions (#2173)
### `merge-lock.sh take` with no `--pid <pid>`, and `merge-lock.sh release` with neither `--pid <pid>` nor `--force`, exit 2 with a stderr line naming `--pid`, creating no lock and removing none ⟦criterion 4⟧
- drop the now-unreachable `os.getppid()` fallback in `_caller_pid` (merge_lock.py); dead code, not duplication removal, so not applied here
