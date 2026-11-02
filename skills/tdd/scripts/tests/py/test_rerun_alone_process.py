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
