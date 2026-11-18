# Plan for #4304 — run_conductor takes and releases its claim through a context manager, with no claim globals

- [x] main, ending by a return of 0, 1, 2 or 3 or by an exception, removes its own conductor.pid claim and the directories it made deepest first, keeping directories that existed before ⟦criterion 3⟧
- [x] a conductor.pid the launched conductor recorded is never removed as the launcher's claim, even when it reads back the launcher's own bytes ⟦criterion 3⟧
- [x] the stubs standing in for preflight_and_launch accept the claim main hands it
- [x] main takes the claim with a `with` over a claim context manager owning the made directories and the claim bytes, its `finally` holding no release code ⟦criterion 2⟧
- [x] no claim globals: the CLAIM and CLAIM_DIRS grep over run_conductor.py prints 0 ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] conduct hands the launcher's claim off through the claim context manager's API, mutating no shared state ⟦diff-checked⟧ ⟦criterion 4⟧
