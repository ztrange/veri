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
