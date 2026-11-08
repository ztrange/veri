### `role-state.sh <role> show` with no state file for the role and lane exits 3 and prints nothing ⟦criterion 5⟧
- extract a `read(path)` helper that returns the file's text or None, replacing the repeated open/FileNotFoundError reads in `append`, `add` and `show`. Most of that duplication is older code, so I did not apply it.
### `role-state.sh <role> set` with a field other than `n` or `lane` exits 2 with its usage line on stderr and writes nothing ⟦criterion 5⟧
- the "read file, parse the next id" logic in the `add` branch and the `append` read-modify-write both open the state file separately; a shared read helper would remove that duplication
### `role-state.sh <role> set n <value>` with a value that is not a whole number ≥ 0 exits 2 with its usage line on stderr and leaves the state file unchanged ⟦criterion 5⟧
- `drop` opens the file directly instead of using `read()`; routing it through `read()` would change how a missing file behaves, so it needs a test that demands it
