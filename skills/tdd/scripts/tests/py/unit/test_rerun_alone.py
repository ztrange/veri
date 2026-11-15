"""Cases for veri/rerun_alone.py, the logic behind rerun-alone.sh."""
import importlib


def test_main_with_no_argument_prints_a_usage_line_naming_rerun_alone_sh_on_stderr_and_exits_2_2905(run_cli):
    rerun_alone = importlib.import_module("veri.rerun_alone")

    code, out, err = run_cli(rerun_alone, [])

    assert (code, out) == (2, "")
    assert "usage: rerun-alone.sh" in err


def test_main_with_a_red_file_holding_an_invalid_utf8_fragment_answers_exit_1_not_a_decode_error_2936(run_cli, tmp_path):
    rerun_alone = importlib.import_module("veri.rerun_alone")
    red = tmp_path / "red.txt"
    red.write_bytes(b"x" * 10 + "€".encode()[:2])

    code, out, err = run_cli(rerun_alone, ["true", str(red)])

    assert (code, out) == (1, "")
    assert "UnicodeDecodeError" not in err


def test_rerun_answers_0_and_records_a_suite_flake_when_every_named_file_passes_alone_and_1_when_one_stays_red(
        monkeypatch, capsys, tmp_path):
    rerun_alone = importlib.import_module("veri.rerun_alone")
    red = tmp_path / "red.txt"
    red.write_text("FAILED tests/a.py::t1 - boom\nFAILED tests/b.py::t2\n")
    ran, recorded = [], []

    class Done:
        def __init__(self, code):
            self.returncode = code

    monkeypatch.setattr(rerun_alone.subprocess, "run", lambda cmd, **kw: ran.append(cmd[-1]) or Done(int(cmd[-1].startswith("tests/b"))))
    monkeypatch.setattr(rerun_alone.event, "append", lambda *a: recorded.append(a) or 0)

    still_red = rerun_alone.rerun("alone-cmd", str(red))
    monkeypatch.setattr(rerun_alone.subprocess, "run", lambda cmd, **kw: ran.append(cmd[-1]) or Done(0))
    flaked = rerun_alone.rerun("alone-cmd", str(red))

    assert (still_red, flaked) == (1, 0)
    assert recorded == [("", {}, "suite-flake", ["files=tests/a.py::t1,tests/b.py::t2"])]
    assert capsys.readouterr() == ("", "")
