"""In-process cases for veri/wait_leaf.py, the module wait-leaf.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: wait-leaf.sh <name> [max-seconds]\n"


@pytest.fixture
def wait_leaf():
    return importlib.import_module("veri.wait_leaf")


def fake_processes(monkeypatch, answer):
    """subprocess.run recording each command as one line, its program by basename;
    <answer>(line) -> (exit code, stdout, stderr)."""
    calls = []

    def fake_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        calls.append(line)
        code, out, err = answer(line)
        return subprocess.CompletedProcess(args, code, out, err)

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_refuses_a_missing_name_answers_a_recorded_code_and_times_out_with_3(
        monkeypatch, capsys, tmp_path, wait_leaf):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(monkeypatch, lambda line: (0, "1000\n", "") if line == "date +%s" else (0, "", ""))

    refusals = []
    for argv in ([], [""]):
        code = wait_leaf.main(argv)
        captured = capsys.readouterr()
        refusals.append((code, captured.out, captured.err))
    assert refusals == [(2, "", USAGE), (2, "", USAGE)]
    assert calls == []

    (tmp_path / ".tdd").mkdir()
    recorded = []
    for text in ("0\n", "1\n", "2\n", "3\n", "5\n"):
        (tmp_path / ".tdd" / "x.exit").write_text(text)
        recorded.append(wait_leaf.main(["x"]))
    assert recorded == [0, 1, 2, 3, 2]

    (tmp_path / ".tdd" / "x.exit").unlink()
    assert wait_leaf.main(["x", "0"]) == 3


def test_main_refusal_touches_no_file_maps_a_recorded_code_as_text_and_waits_out_a_code_that_is_not_one(
        monkeypatch, capsys, tmp_path, wait_leaf):
    monkeypatch.chdir(tmp_path)
    readings = []

    def answer(line):
        if line == "date +%s":
            readings.append(1000 + len(readings))
            return (0, f"{readings[-1]}\n", "")
        return (0, "", "")

    fake_processes(monkeypatch, answer)

    for argv in ([], [""]):
        assert wait_leaf.main(argv) == 2
    assert list(tmp_path.iterdir()) == []

    (tmp_path / ".tdd").mkdir()
    exit_file = tmp_path / ".tdd" / "x.exit"
    mapped = []
    for text in ("3\n", "4\n", "00\n", "01\n", "12345678901234567890\n"):
        exit_file.write_text(text)
        mapped.append(wait_leaf.main(["x"]))
    assert mapped == [3, 2, 2, 2, 2]

    waited = []
    for text in ("-1\n", "7x\n", "", None):
        exit_file.unlink(missing_ok=True)
        if text is None:
            exit_file.mkdir()
        else:
            exit_file.write_text(text)
        readings.clear()
        waited.append((wait_leaf.main(["x", "5"]), readings[-1] >= readings[0] + 5))
    assert waited == [(3, True)] * 4
    capsys.readouterr()


def test_main_reads_the_clock_once_then_per_round_checks_the_pid_rechecks_after_a_dead_supervisor_and_sleeps_between_rounds(
        monkeypatch, capsys, tmp_path, wait_leaf):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_POLL", "0.5")
    (tmp_path / ".tdd").mkdir()
    readings = []

    def answer(line):
        if line == "date +%s":
            if len(readings) > 20:
                raise RuntimeError("runaway wait: more than 20 clock readings")
            readings.append(next(clock))
            return (0, f"{readings[-1]}\n", "")
        if line == "ps -p 42 -o args=":
            if len(calls) > 6:
                (tmp_path / ".tdd" / "x.exit").write_text("1\n")
                return (1, "", "")
            return (0, "bash supervise.sh x develop-red\n", "")
        return (0, "", "")

    calls = fake_processes(monkeypatch, answer)

    (tmp_path / ".tdd" / "y.pid").write_text("abc\n")
    clock = iter([1000, 1000, 1001] + [1001] * 20)
    timed_out = wait_leaf.main(["y", "1"])
    assert (timed_out, calls) == (3, ["date +%s", "date +%s", "sleep 0.5", "date +%s"])

    calls.clear()
    readings.clear()
    (tmp_path / ".tdd" / "x.pid").write_text("42\n")
    clock = iter([1000] * 21)
    answered = wait_leaf.main(["x"])
    assert (answered, calls) == (1, [
        "date +%s",
        "ps -p 42 -o args=", "date +%s", "sleep 0.5",
        "ps -p 42 -o args=", "date +%s", "sleep 0.5",
        "ps -p 42 -o args=",
    ])
    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("", "")


def test_main_reads_max_as_bash_arithmetic_defaulting_to_540_and_ignores_arguments_past_it(
        monkeypatch, capsys, tmp_path, wait_leaf):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "x.pid").write_text("42\n")
    readings = []

    def answer(line):
        if line == "date +%s":
            if len(readings) > 600:
                raise RuntimeError("runaway wait: more than 600 clock readings")
            readings.append(1000 + len(readings))
            return (0, f"{readings[-1]}\n", "")
        if line == "ps -p 42 -o args=":
            return (0, "bash supervise.sh x develop-red\n", "")
        return (0, "", "")

    calls = fake_processes(monkeypatch, answer)

    rounds = {}
    for argv in (["x"], ["x", ""], ["x", "0"], ["x", "-5"], ["x", "010"], ["x", "0x10"], ["x", "3", "9"]):
        calls.clear()
        readings.clear()
        code = wait_leaf.main(argv)
        rounds[tuple(argv[1:])] = (code, calls.count("ps -p 42 -o args="), readings[-1] - readings[0])
    assert rounds == {
        (): (3, 540, 540),
        ("",): (3, 540, 540),
        ("0",): (3, 1, 1),
        ("-5",): (3, 1, 1),
        ("010",): (3, 8, 8),
        ("0x10",): (3, 16, 16),
        ("3", "9"): (3, 3, 3),
    }
    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("", "")
