"""run_case finds detect-test-command.sh in the scripts directory, the parent of veri/."""
import importlib
import os


def test_run_case_looks_up_detect_test_command_in_the_scripts_directory_not_under_veri(fake_processes):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    fake = fake_processes.answers({"": (0, "", "")})
    tick_ledger.run_case("tests/py/unit/test_x.py::test_y")

    scripts = os.path.dirname(os.path.dirname(os.path.realpath(tick_ledger.__file__)))
    assert os.path.isfile(os.path.join(scripts, "detect-test-command.sh"))
    assert fake.seen[0][0][0] == os.path.join(scripts, "detect-test-command.sh")
