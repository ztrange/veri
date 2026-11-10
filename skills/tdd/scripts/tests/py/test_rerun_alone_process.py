"""Cases for rerun-alone.sh that start the real entry point."""
import subprocess

import pytest

from conftest import SCRIPTS

RERUN = str(SCRIPTS / "rerun-alone.sh")


@pytest.mark.process("rerun-alone.sh run on red output that names no test file")
def test_red_output_naming_no_test_file_exits_1_and_runs_no_alone_command_2905(tmp_path):
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone"
    alone.write_text(f"#!/bin/sh\necho \"$@\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("Error: connection refused\n2 failed\n")

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 1
    assert not ran_log.exists()


@pytest.mark.process("rerun-alone.sh run on red output naming two files, one still red alone")
def test_a_file_still_red_alone_exits_1_and_writes_no_suite_flake_event_2905(tmp_path):
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$@\" >> {ran_log}\ncase \"$1\" in *b.test.ts) exit 1;; esac\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("FAIL src/a.test.ts\nFAIL src/b.test.ts\n2 failed\n")

    ran = subprocess.run([RERUN, f'{alone} "$1"', str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 1
    assert sorted(ran_log.read_text().split()) == ["src/a.test.ts", "src/b.test.ts"]
    assert not list(tmp_path.rglob("*events*"))


@pytest.mark.process("rerun-alone.sh run on red output naming two files, both passing alone")
def test_every_file_passing_alone_exits_0_and_writes_a_suite_flake_event_naming_each_2905(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("FAIL src/a.test.ts\nFAIL src/b.test.ts\n2 failed\n")

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    events = (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
    flakes = [e for e in events if "suite-flake" in e]
    assert len(flakes) == 1
    assert "src/a.test.ts" in flakes[0] and "src/b.test.ts" in flakes[0]


@pytest.mark.process("rerun-alone.sh run with an alone command that places \"$1\" itself")
def test_alone_command_placing_its_own_file_argument_receives_the_file_once_as_written_2905(tmp_path):
    (tmp_path / ".git").mkdir()
    argv_log = tmp_path / "runner-argv"
    runner = tmp_path / "runner.sh"
    runner.write_text(f"#!/bin/sh\necho \"$@\" >> {argv_log}\nexit 0\n")
    runner.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("FAIL src/a.test.ts\n1 failed\n")

    ran = subprocess.run([RERUN, f'{runner} TESTS="$1"', str(red)], cwd=tmp_path, capture_output=True, text=True)
    usage = subprocess.run([RERUN], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert argv_log.read_text().splitlines() == ["TESTS=src/a.test.ts"]
    assert "<alone-cmd> <red-output-file>" in usage.stderr


@pytest.mark.process("rerun-alone.sh run on pytest red output naming a test_<x>.py file, passing alone")
def test_pytest_failed_summary_file_passing_alone_exits_0_and_writes_a_suite_flake_event_naming_it_2883(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("FAILED skills/tdd/scripts/tests/py/test_foo.py::test_bar - Failed: Timeout >30.0s\n1 failed\n")

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert ran_log.read_text().splitlines() == ["skills/tdd/scripts/tests/py/test_foo.py"]
    events = (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
    flakes = [e for e in events if "suite-flake" in e]
    assert len(flakes) == 1
    assert "skills/tdd/scripts/tests/py/test_foo.py" in flakes[0]


@pytest.mark.process("rerun-alone.sh run on pytest red output whose only red case ERRORed, passing alone")
def test_pytest_error_summary_file_passing_alone_exits_0_and_writes_a_suite_flake_event_naming_it_2883(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("ERROR skills/tdd/scripts/tests/py/test_foo.py::test_bar - Failed: Timeout >30.0s\n1 error\n")

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert ran_log.read_text().splitlines() == ["skills/tdd/scripts/tests/py/test_foo.py"]
    events = (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
    flakes = [e for e in events if "suite-flake" in e]
    assert len(flakes) == 1
    assert "skills/tdd/scripts/tests/py/test_foo.py" in flakes[0]


@pytest.mark.process("rerun-alone.sh run on pytest red output with several summary lines naming one file")
def test_several_summary_lines_naming_one_file_run_it_alone_once_and_name_it_once_2883(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text(
        "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_a - Failed: Timeout >30.0s\n"
        "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_b - Failed: Timeout >30.0s\n"
        "ERROR skills/tdd/scripts/tests/py/test_foo.py::test_c - Failed: Timeout >30.0s\n"
        "3 failed\n"
    )

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert ran_log.read_text().splitlines() == ["skills/tdd/scripts/tests/py/test_foo.py"]
    events = (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
    flakes = [e for e in events if "suite-flake" in e]
    assert len(flakes) == 1
    assert flakes[0].count("skills/tdd/scripts/tests/py/test_foo.py") == 1


@pytest.mark.process("rerun-alone.sh run on pytest red output whose summary names no test file")
def test_pytest_red_output_naming_no_file_on_a_summary_line_exits_1_runs_no_alone_command_and_writes_no_event_2883(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text(
        "skills/tdd/scripts/tests/py/test_foo.py ....                [ 50%]\n"
        "skills/tdd/scripts/tests/py/test_bar.py ....                [100%]\n"
        "!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!\n"
        "no tests ran in 3.21s\n"
    )

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 1
    assert not ran_log.exists()
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


@pytest.mark.process("rerun-alone.sh run on pytest red output naming two files, one still red alone")
def test_pytest_red_output_naming_two_files_one_still_red_alone_exits_1_and_writes_no_suite_flake_event_2883(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\ncase \"$1\" in *test_bar.py) exit 1;; esac\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text(
        "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_a - Failed: Timeout >30.0s\n"
        "FAILED skills/tdd/scripts/tests/py/test_bar.py::test_b - AssertionError\n"
        "2 failed\n"
    )

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 1
    assert ran_log.read_text().splitlines() == [
        "skills/tdd/scripts/tests/py/test_foo.py",
        "skills/tdd/scripts/tests/py/test_bar.py",
    ]
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


@pytest.mark.process("rerun-alone.sh run on a pytest FAILED line naming a unit test_x.py, passing alone")
def test_pytest_failed_line_naming_a_unit_file_reruns_it_alone_once_and_writes_one_suite_flake_event_2933(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("FAILED skills/tdd/scripts/tests/py/unit/test_x.py::test_a - assert 0\n")

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert ran_log.read_text().splitlines() == ["skills/tdd/scripts/tests/py/unit/test_x.py"]
    events = (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
    flakes = [e for e in events if "suite-flake" in e]
    assert len(flakes) == 1
    assert "skills/tdd/scripts/tests/py/unit/test_x.py" in flakes[0]


@pytest.mark.process("rerun-alone.sh run on red output naming a test_x.py file only as a bare path, passing alone")
def test_bare_test_py_path_without_a_pytest_summary_line_reruns_it_alone_once_and_writes_one_suite_flake_event_2933(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("timed out waiting in\nskills/tdd/scripts/tests/py/unit/test_x.py\n1 failed\n")

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert ran_log.read_text().splitlines() == ["skills/tdd/scripts/tests/py/unit/test_x.py"]
    events = (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
    flakes = [e for e in events if "suite-flake" in e]
    assert len(flakes) == 1
    assert "skills/tdd/scripts/tests/py/unit/test_x.py" in flakes[0]


@pytest.mark.process("rerun-alone.sh run on red output naming a test_x.py file only as a bare path, still red alone")
def test_bare_test_py_path_still_red_alone_exits_1_and_writes_no_suite_flake_event_2933(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 1\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("timed out waiting in\nskills/tdd/scripts/tests/py/unit/test_x.py\n1 failed\n")

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 1
    assert ran_log.read_text().splitlines() == ["skills/tdd/scripts/tests/py/unit/test_x.py"]
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


@pytest.mark.process("rerun-alone.sh run on several pytest FAILED lines naming one unit test_x.py, passing alone")
def test_several_failed_lines_naming_one_unit_file_rerun_it_alone_once_and_list_it_once_in_the_event_2933(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text(
        "FAILED skills/tdd/scripts/tests/py/unit/test_x.py::test_a - assert 0\n"
        "FAILED skills/tdd/scripts/tests/py/unit/test_x.py::test_b - assert 0\n"
        "FAILED skills/tdd/scripts/tests/py/unit/test_x.py::test_c - assert 0\n"
        "3 failed\n"
    )

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert ran_log.read_text().splitlines() == ["skills/tdd/scripts/tests/py/unit/test_x.py"]
    events = (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
    flakes = [e for e in events if "suite-flake" in e]
    assert len(flakes) == 1
    assert flakes[0].count("skills/tdd/scripts/tests/py/unit/test_x.py") == 1


@pytest.mark.process("rerun-alone.sh run on red output listing one x.test.ts file twice, passing alone")
def test_a_test_ext_file_listed_twice_reruns_alone_once_and_is_listed_once_in_the_event_2933(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("FAIL src/a.test.ts\nFAIL src/a.test.ts\n2 failed\n")

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert ran_log.read_text().splitlines() == ["src/a.test.ts"]
    events = (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
    flakes = [e for e in events if "suite-flake" in e]
    assert len(flakes) == 1
    assert flakes[0].count("src/a.test.ts") == 1


@pytest.mark.process("rerun-alone.sh run on pytest red output whose body also carries a foo.test.ts path")
def test_pytest_failed_line_wins_over_a_test_path_in_the_output_body_3537(tmp_path):
    (tmp_path / ".git").mkdir()
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text(f"#!/bin/sh\necho \"$1\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text(
        "assert 'foo.test.ts::x' in out\n"
        "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_bar - Failed: Timeout >30.0s\n"
        "1 failed\n"
    )

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert ran_log.read_text().splitlines() == ["skills/tdd/scripts/tests/py/test_foo.py"]
