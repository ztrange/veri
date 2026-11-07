### `role-state.sh <role> show` with no state file for the role and lane exits 3 and prints nothing ⟦criterion 5⟧
- extract a `read(path)` helper that returns the file's text or None, replacing the repeated open/FileNotFoundError reads in `append`, `add` and `show`. Most of that duplication is older code, so I did not apply it.
