### Every case under `projects/dashboard/tests/` runs with `VERI_HOME` pointing at a copy of `fixtures/journal/` inside its own `tmp_path` (the copy holds `3277.jsonl` under `runs/`), never the real `~/.veri`; pinned by a case in a test file other than `projects/dashboard/tests/conftest.py`, which supplies the copy ⟦guard-subject: projects/dashboard/tests/conftest.py⟧ ⟦criterion 5⟧
- test-only | Remove the duplicated `FIXTURE` path constant by having `conftest.py` expose it as a fixture that `test_veri_home_fixture.py` takes.
### `serve.py` listens on `127.0.0.1` only: the page is reachable at `127.0.0.1` and the listening socket is bound to no other address ⟦criterion 2⟧
- test-only | extract the duplicated `subprocess.Popen([sys.executable, SERVE, ...])` launch and terminate/wait teardown in `test_serve_answers_get_root_with_200_html` and `test_serve_listens_on_loopback_only` into one helper
### `serve.py --repo <path>` with no `--port` still serves the page, on a default port ⟦criterion 2⟧
- test-only | extract the repeated `subprocess.Popen([... SERVE ...])` launch and terminate/wait teardown in `test_serve_get_root.py` into one helper
