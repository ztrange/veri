import pathlib
import shutil
import subprocess

DASHBOARD = pathlib.Path(__file__).resolve().parents[1]


def test_make_test_exits_with_pytests_own_code(tmp_path):
    project = tmp_path / "dashboard"
    (project / "tests").mkdir(parents=True)
    shutil.copy(DASHBOARD / "Makefile", project / "Makefile")
    case = project / "tests" / "test_one.py"
    case.write_text("def test_one():\n    assert False\n")

    failing = subprocess.run(["make", "-C", str(project), "test"], capture_output=True, text=True)
    case.write_text("def test_one():\n    assert True\n")
    passing = subprocess.run(["make", "-C", str(project), "test"], capture_output=True, text=True)

    assert (failing.returncode, passing.returncode) == (1, 0)
