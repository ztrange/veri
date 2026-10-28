"""Cases for conftest's meets_floor(), the floor check the process-case shim guard calls."""
import subprocess

import conftest


def test_two_calls_for_the_same_interpreter_path_start_that_interpreter_once(tmp_path, monkeypatch):
    python = tmp_path / "python3"
    python.write_text("")
    launches = []

    def spy(args, *rest, **kwargs):
        launches.append(list(args))
        return subprocess.CompletedProcess(args, 0, stdout="3.12.0\n", stderr="")

    monkeypatch.setattr(conftest, "REAL_RUN", spy)

    first = conftest.meets_floor(str(python))
    second = conftest.meets_floor(str(python))

    assert (first, second) == (True, True)
    assert len(launches) == 1, "meets_floor started the same interpreter %d times, wanted 1" % len(launches)


def test_two_calls_for_the_same_interpreter_path_read_the_floor_once(tmp_path, monkeypatch):
    python = tmp_path / "python3"
    python.write_text("")
    reads = []

    class CountingPath(type(tmp_path)):
        def read_text(self, *args, **kwargs):
            reads.append(str(self))
            return "VENV_FLOOR=3.12\n"

    monkeypatch.setattr(conftest, "SCRIPTS", CountingPath(tmp_path))
    monkeypatch.setattr(conftest, "REAL_RUN", lambda args, *rest, **kwargs: subprocess.CompletedProcess(args, 0, stdout="3.12.0\n", stderr=""))

    first = conftest.meets_floor(str(python))
    second = conftest.meets_floor(str(python))

    assert (first, second) == (True, True)
    assert len(reads) == 1, "meets_floor read VENV_FLOOR %d times, wanted 1" % len(reads)


def test_a_call_for_a_different_interpreter_path_starts_that_other_interpreter_again(tmp_path, monkeypatch):
    first_python = tmp_path / "one" / "python3"
    second_python = tmp_path / "two" / "python3"
    for python in (first_python, second_python):
        python.parent.mkdir()
        python.write_text("")
    launches = []

    def spy(args, *rest, **kwargs):
        launches.append(args[0])
        return subprocess.CompletedProcess(args, 0, stdout="3.12.0\n", stderr="")

    monkeypatch.setattr(conftest, "REAL_RUN", spy)

    conftest.meets_floor(str(first_python))
    conftest.meets_floor(str(second_python))

    assert launches == [str(first_python), str(second_python)], "meets_floor started %r, wanted each interpreter once" % launches
