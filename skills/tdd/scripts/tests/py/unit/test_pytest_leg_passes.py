"""The passes veri/pytest_leg.py makes, driven in-process on a planted tree with pytest itself."""
import importlib


def test_a_leg_that_collects_no_serial_marked_case_starts_one_pytest_session_and_exits_as_it_decided_2092(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    sessions = tmp_path / "sessions"
    (planted / "conftest.py").write_text(
        "def pytest_sessionstart(session):\n"
        "    with open(%r, 'a') as log:\n"
        "        log.write('session\\n')\n" % str(sessions)
    )
    (planted / "test_planted_unmarked.py").write_text("def test_unmarked():\n    pass\n")
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}

    code, out, _ = run_cli(importlib.import_module("veri.pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)

    assert sessions.read_text().splitlines() == ["session"]
    assert (code, out.count("1 passed")) == (0, 1)
