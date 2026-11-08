### Every case under `projects/dashboard/tests/` runs with `VERI_HOME` pointing at a copy of `fixtures/journal/` inside its own `tmp_path` (the copy holds `3277.jsonl` under `runs/`), never the real `~/.veri`; pinned by a case in a test file other than `projects/dashboard/tests/conftest.py`, which supplies the copy ⟦guard-subject: projects/dashboard/tests/conftest.py⟧ ⟦criterion 5⟧
- test-only | Remove the duplicated `FIXTURE` path constant by having `conftest.py` expose it as a fixture that `test_veri_home_fixture.py` takes.
### `serve.py` listens on `127.0.0.1` only: the page is reachable at `127.0.0.1` and the listening socket is bound to no other address ⟦criterion 2⟧
- test-only | extract the duplicated `subprocess.Popen([sys.executable, SERVE, ...])` launch and terminate/wait teardown in `test_serve_answers_get_root_with_200_html` and `test_serve_listens_on_loopback_only` into one helper
### `serve.py --repo <path>` with no `--port` still serves the page, on a default port ⟦criterion 2⟧
- test-only | extract the repeated `subprocess.Popen([... SERVE ...])` launch and terminate/wait teardown in `test_serve_get_root.py` into one helper
### The page's Running entry for a run shows its current phase (the last `launch` event's phase) and that phase's attempt count, as `status.sh --report` prints them ⟦criterion 4⟧
- extract the per-run parsing in `running_lines` (minutes, steps, phase) into helper functions
### The page's Running entry for a run shows its PASS and REJECT verdict counts, as `status.sh --report` prints them ⟦criterion 4⟧
- extract the repeated "if events of kind X: build a field string" blocks in `running_lines` (steps, phase, verdict counts) into small per-field helpers
- test-only | factor the repeated Popen/serve-start and wait-for-ready loop in `tests/test_serve_get_root.py` into a helper
### The page's Running entry for a run shows its model split (the model per role: developer, verifier, revise), as `status.sh --report` prints it ⟦criterion 4⟧
- extract the per-run body of `running_lines` in `projects/dashboard/serve.py` into a function, with a small helper for the repeated "empty string unless the events exist" field pattern
