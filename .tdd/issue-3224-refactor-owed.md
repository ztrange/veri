### `role-state.sh <role> show` with no state file for the role and lane exits 3 and prints nothing ⟦criterion 5⟧
- extract a `read(path)` helper that returns the file's text or None, replacing the repeated open/FileNotFoundError reads in `append`, `add` and `show`. Most of that duplication is older code, so I did not apply it.
### `role-state.sh <role> set` with a field other than `n` or `lane` exits 2 with its usage line on stderr and writes nothing ⟦criterion 5⟧
- the "read file, parse the next id" logic in the `add` branch and the `append` read-modify-write both open the state file separately; a shared read helper would remove that duplication
### `role-state.sh <role> set n <value>` with a value that is not a whole number ≥ 0 exits 2 with its usage line on stderr and leaves the state file unchanged ⟦criterion 5⟧
- `drop` opens the file directly instead of using `read()`; routing it through `read()` would change how a missing file behaves, so it needs a test that demands it
### `role-state.sh <role> drop <list> <id>` of an id the list does not hold exits 3 and leaves the state file unchanged ⟦criterion 5⟧
- `drop` reads the file with its own `open()`, which duplicates `read()`. Swapping it to `(read(path) or "").splitlines(True)` would turn a missing state file from a traceback into exit 3. That changes behaviour, so I did not apply it.
- `main` repeats the `argv[1] == ...` and `len(argv) == 4` checks across the validation and dispatch ladders. Folding them into one dispatch by verb would remove that. It goes beyond removing duplication against code this cycle wrote, so I left it.
### `status.sh --recover <role>` lists under `Runs` a taken run held by a live conductor with its issue, its title and that conductor's pid ⟦criterion 6⟧
- test-only | extract the duplicated fake `subprocess.run` and the `lines` and Runs-slice parsing in `test_status_recover.py` into helpers
### `status.sh --recover <role>` lists under `Runs` a taken run no live conductor holds with its issue, its title and `dead` in place of a pid ⟦criterion 6⟧
- test-only | extract the repeated `run` stub and the tmp-tree setup in `test_status_recover.py` into a shared helper or fixture
### `status.sh --recover <role>` prints under `State` each timed N change from the role's state file with its id and time ⟦criterion 6⟧
- test-only | the `monkeypatch` setup and the stub `run` function are repeated across the `test_status_recover.py` cases; a shared fixture could replace them, but the cases are frozen, so I left it.
### `status.sh --recover <role> --lane <lane>` reads the named lane's state file `.tdd/role-<role>-<lane>.state`, not the default lane's ⟦criterion 6⟧
- out-of-scope | share the `.tdd/role-<role>[-<lane>].state` path building between `status.py` and `role_state.py` once the latter gains `--lane`
not-done | transform-rejected | extract a `read(path)` helper that returns the file's text or None, replacing the repeated open/FileNotFoundError reads in `append`, `add` and `show`. Most of that duplication is older code, so I did not apply it.
not-done | transform-rejected | the "read file, parse the next id" logic in the `add` branch and the `append` read-modify-write both open the state file separately; a shared read helper would remove that duplication
not-done | uncovered | `drop` opens the file directly instead of using `read()`; routing it through `read()` would change how a missing file behaves, so it needs a test that demands it
applied | fff98f8fa0f8c35de50f46dcd796af9888905ac2 | `drop` reads the file with its own `open()`, which duplicates `read()`. Swapping it to `(read(path) or "").splitlines(True)` would turn a missing state file from a traceback into exit 3. That changes behaviour, so I did not apply it.	refactor: drop reads the state file through read() (#3224)
applied | 190d0479bc934a1276444a90911c35c5ebebdb6a | `main` repeats the `argv[1] == ...` and `len(argv) == 4` checks across the validation and dispatch ladders. Folding them into one dispatch by verb would remove that. It goes beyond removing duplication against code this cycle wrote, so I left it.	refactor: dispatch role-state verbs through one table (#3224)
applied | 7f44cca19d17c0fb8036d59825ada34f3107c16b | share the `.tdd/role-<role>[-<lane>].state` path building between `status.py` and `role_state.py` once the latter gains `--lane`	refactor: share the role state path building between status and role_state (#3224)
