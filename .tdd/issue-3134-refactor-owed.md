### With the merge lock taken by `take --pid <pid> --owner <token A>`, a `release --pid <same pid>` given no `--owner` exits 1 and leaves the lock held ⟦criterion 1⟧
- test-only | the three tests in test_merge_lock_owner.py repeat the same setup (`_start_time` patch, `me`, `lock`, `record`, taking the lock under token-a); a fixture would remove that
