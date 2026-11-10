"""The passes veri/pytest_leg.py makes, driven in-process on a planted tree with pytest itself."""
import importlib
import sys


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


def test_a_leg_driven_in_process_on_a_tree_with_its_own_conftest_leaves_the_conftest_module_it_found_in_place_2092(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "conftest.py").write_text("PLANTED = True\n")
    (planted / "test_planted_unmarked.py").write_text("def test_unmarked():\n    pass\n")
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}
    before = sys.modules.get("conftest")

    try:
        run_cli(importlib.import_module("veri.pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)
        after = sys.modules.get("conftest")
    finally:
        if before is None:
            sys.modules.pop("conftest", None)
        else:
            sys.modules["conftest"] = before

    assert after is before


def test_the_serial_probe_collecting_after_its_run_directory_vanished_neither_raises_nor_aborts_the_session_2099(monkeypatch, tmp_path):
    serial_seen = importlib.import_module("veri.serial_seen")
    monkeypatch.setenv("PYTEST_LEG_SERIAL_SEEN", str(tmp_path / "veri-pytest-gone" / "serial-seen"))

    serial_seen.pytest_collection_modifyitems([])

    assert not (tmp_path / "veri-pytest-gone").exists()


def test_a_leg_run_on_a_host_whose_tmpdir_is_elsewhere_gives_its_cases_tmp_as_the_inherited_tmpdir_2354(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    seen = tmp_path / "seen"
    (planted / "conftest.py").write_text(
        "import os\n"
        "def pytest_sessionstart(session):\n"
        "    with open(%r, 'w') as out:\n"
        "        out.write(os.environ.get('TMPDIR', 'unset'))\n" % str(seen)
    )
    (planted / "test_planted_unmarked.py").write_text("def test_unmarked():\n    pass\n")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1",
           "TMPDIR": str(elsewhere)}

    run_cli(importlib.import_module("veri.pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)

    assert seen.read_text() == "/tmp"


def test_a_leg_that_collects_a_serial_case_ends_with_one_line_counting_the_cases_passed_across_both_passes_3554(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "test_planted_both.py").write_text(
        "import pytest\n"
        "def test_unmarked():\n    pass\n"
        "@pytest.mark.serial\n"
        "def test_serial():\n    pass\n"
    )
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}

    code, out, _ = run_cli(importlib.import_module("veri.pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)

    last = [line for line in out.splitlines() if line.strip()][-1]
    assert (code, "2 passed" in last, "deselected" in last) == (0, True, False)


def test_a_subset_leg_whose_mark_expression_excludes_a_named_case_from_both_passes_exits_non_zero_naming_the_count_3554(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "pytest.ini").write_text("[pytest]\nmarkers =\n    slow: a case the mark expression leaves out\n    serial: runs alone\n")
    (planted / "test_planted_unselected.py").write_text(
        "import pytest\n"
        "def test_unmarked():\n    pass\n"
        "@pytest.mark.serial\n"
        "def test_serial():\n    pass\n"
        "@pytest.mark.slow\n"
        "def test_left_out():\n    pass\n"
    )
    module = str(planted / "test_planted_unselected.py")
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}

    code, out, err = run_cli(importlib.import_module("veri.pytest_leg"),
                             ["--subset", "-q", "-p", "no:cacheprovider", "-m", "not slow",
                              module + "::test_unmarked", module + "::test_serial", module + "::test_left_out"], env=env)

    assert (code != 0, "1 unselected" in out + err) == (True, True)


def test_a_subset_leg_whose_own_mark_and_keyword_selection_leaves_cases_of_a_named_file_unrun_exits_zero_3554(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "pytest.ini").write_text("[pytest]\nmarkers =\n    slow: a case the mark expression leaves out\n    serial: runs alone\n")
    (planted / "test_planted_selection.py").write_text(
        "import pytest\n"
        "def test_unmarked():\n    pass\n"
        "def test_other():\n    pass\n"
        "@pytest.mark.serial\n"
        "def test_serial():\n    pass\n"
        "@pytest.mark.slow\n"
        "def test_left_out():\n    pass\n"
    )
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}

    code, out, err = run_cli(importlib.import_module("veri.pytest_leg"),
                             ["--subset", "-q", "-p", "no:cacheprovider", "-m", "not slow", "-k", "not other", str(planted)], env=env)

    assert (code, "unselected" in out + err) == (0, False)


def test_a_two_pass_leg_ends_with_one_line_counting_the_cases_named_run_passed_and_failed_across_both_passes_3554(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "pytest.ini").write_text("[pytest]\nmarkers =\n    slow: a case the mark expression leaves out\n    serial: runs alone\n")
    (planted / "test_planted_counts.py").write_text(
        "import pytest\n"
        "def test_unmarked():\n    pass\n"
        "def test_failing():\n    assert False\n"
        "@pytest.mark.serial\n"
        "def test_serial():\n    pass\n"
        "@pytest.mark.slow\n"
        "def test_left_out():\n    pass\n"
    )
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}

    code, out, _ = run_cli(importlib.import_module("veri.pytest_leg"), ["-q", "-p", "no:cacheprovider", "-m", "not slow", str(planted)], env=env)

    last = [line for line in out.splitlines() if line.strip()][-1]
    assert (code, last) == (1, "4 named, 3 run, 2 passed, 1 failed across both passes")


def test_a_subset_leg_over_named_files_runs_their_process_tree_audit_and_serial_cases_leaving_none_unselected_3554(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "pytest.ini").write_text(
        "[pytest]\nmarkers =\n    process: starts a process\n    tree_audit: sweeps a tree\n    serial: runs alone\n")
    (planted / "test_planted_marks.py").write_text(
        "import pytest\n"
        "def test_unmarked():\n    pass\n"
        "@pytest.mark.process('x')\n"
        "def test_process():\n    pass\n"
        "@pytest.mark.tree_audit('x')\n"
        "def test_tree_audit():\n    pass\n"
        "@pytest.mark.serial\n"
        "def test_serial():\n    pass\n"
    )
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}

    code, out, err = run_cli(importlib.import_module("veri.pytest_leg"),
                             ["--subset", "-q", "-p", "no:cacheprovider", str(planted)], env=env)

    last = [line for line in out.splitlines() if line.strip()][-1]
    assert (code, "4 passed" in last, "unselected" in out + err) == (0, True, False)


def _collected(tmp_path, args, cases):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    collected = pytest_leg.Collected()
    collected.root = str(tmp_path)
    collected.args = [str(tmp_path / arg) if "::" not in arg else str(tmp_path / arg.split("::", 1)[0]) + "::" + arg.split("::", 1)[1] for arg in args]
    collected.cases = [(nodeid, str(tmp_path / nodeid.split("::")[0])) for nodeid in cases]
    return pytest_leg, collected


def test_a_named_file_whose_every_case_went_unrun_is_reported_though_another_named_file_ran_3554(tmp_path):
    pytest_leg, collected = _collected(tmp_path, ["test_dropped.py", "test_ran.py"],
                                       ["test_dropped.py::test_a", "test_ran.py::test_b"])

    unrun, targets = pytest_leg.unrun_targets(collected, {"test_ran.py::test_b"})

    assert (unrun, [target.rsplit("/", 1)[-1] for target in targets]) == (["test_dropped.py::test_a"], ["test_dropped.py"])


def test_a_named_base_node_id_whose_parametrized_cases_all_went_unrun_is_reported_3554(tmp_path):
    pytest_leg, collected = _collected(tmp_path, ["test_param.py::test_p"],
                                       ["test_param.py::test_p[1]", "test_param.py::test_p[2]"])

    unrun, targets = pytest_leg.unrun_targets(collected, set())

    assert (unrun, len(targets)) == (["test_param.py::test_p[1]", "test_param.py::test_p[2]"], 1)


def test_a_named_node_id_deeper_than_a_cases_own_id_names_none_of_its_cases_3554(tmp_path):
    pytest_leg, collected = _collected(tmp_path, ["test_deep.py::test_a::deeper"], ["test_deep.py::test_a"])

    assert pytest_leg.unrun_targets(collected, set()) == ([], [])
