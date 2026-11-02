### `suite-red-resume.sh flake <at> <red-file> <alone-red-file>`, with a red file that names no test file (empty), exits 1 and writes no `suite-flake` event (small case, run in-process with `run_cli`) ⟦criterion 3⟧
- test-only | the new flake tests repeat the same setup (importlib import, `.git` mkdir, red/alone file writes); a shared helper or fixture would remove it
- out-of-scope | `USAGE` omits the `flake` form (SC48 documents it); adding it changes visible output, so it is a behaviour change and not a tidy-up
not-done | transform-rejected | `USAGE` omits the `flake` form (SC48 documents it); adding it changes visible output, so it is a behaviour change and not a tidy-up
