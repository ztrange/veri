"""In-process cases for veri/preflight.py, the module preflight.sh is a shim over."""
import importlib
import os


def test_3771_a_no_arguments_exit_2_with_the_usage_line_and_make_no_inner_call(monkeypatch, run_cli):
    preflight = importlib.import_module("veri.preflight")
    calls = []

    def run_script(name, *args, **kwargs):
        calls.append((name, args))
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, [])

    assert code == 2
    assert "preflight.sh <n> <slug>" in err
    assert calls == []
    assert os.path.exists(os.path.join(os.path.dirname(preflight.__file__), "..", "preflight.sh"))
