"""In-process cases for veri/run_suite.py, the module run-suite.sh is a shim over."""
import importlib
import importlib.util
import pathlib
import shutil
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def run_suite():
    return importlib.import_module("veri.run_suite")


def staged_module(scripts):
    (scripts / "veri").mkdir(parents=True)
    (scripts / "lib").mkdir()
    copy = scripts / "veri" / "run_suite.py"
    shutil.copy(SCRIPTS / "veri" / "run_suite.py", copy)
    spec = importlib.util.spec_from_file_location("staged_run_suite", copy)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_suite(tmp_path, name, body):
    suite = tmp_path / name
    suite.write_text("#!/bin/sh\n" + body)
    suite.chmod(0o755)
    return str(suite)


def test_main_refuses_a_countless_suite_quoting_its_last_line_or_naming_its_empty_output(tmp_path, capfd, run_suite):
    answers = []
    for name, body in (("partial.test.sh", "echo partial\nexit 0\n"), ("silent.test.sh", "exit 0\n")):
        code = run_suite.main([fake_suite(tmp_path, name, body)])
        out, _ = capfd.readouterr()
        answers.append((code, out.splitlines()[-2:]))
    assert answers == [
        (1, ["partial.test.sh: never reached its count line", "partial.test.sh: its last line was: partial"]),
        (1, ["silent.test.sh: never reached its count line", "silent.test.sh: its output was empty"]),
    ]


def test_main_reads_a_suite_output_over_one_mebibyte_to_its_count_line(tmp_path, capfd, run_suite):
    output = tmp_path / "output.txt"
    output.write_text(("y" * 79 + "\n") * 13200 + "13 passed, 0 failed\n")
    assert output.stat().st_size > 1024 * 1024
    code = run_suite.main([fake_suite(tmp_path, "big.test.sh", 'cat "%s"\nexit 0\n' % output)])
    out, _ = capfd.readouterr()
    assert (code, "never reached its count line" in out) == (0, False)


def test_main_refuses_a_missing_suite_argument_with_its_usage_line(capfd, monkeypatch, run_suite):
    started = []
    monkeypatch.setattr(run_suite.subprocess, "Popen", lambda *a, **k: started.append(a))
    code = run_suite.main([])
    out, err = capfd.readouterr()
    assert (code, out, err, started) == (2, "", "usage: run-suite.sh <suite>\n", [])


def test_main_passes_a_counted_suite_code_through_raw_and_quotes_a_blank_last_line(tmp_path, capfd, run_suite):
    answers = []
    for name, body in (
        ("seven.test.sh", "echo '3 passed, 0 failed'\nexit 7\n"),
        ("piped.test.sh", "echo '3 passed, 0 failed'\nexit 141\n"),
        ("noisy.test.sh", "echo '3 passed, 0 failed'\necho trailing >&2\nexit 0\n"),
        ("blank.test.sh", "echo partial\necho\nexit 0\n"),
        ("blanks.test.sh", "echo\necho '  '\nexit 0\n"),
    ):
        code = run_suite.main([fake_suite(tmp_path, name, body)])
        out, _ = capfd.readouterr()
        answers.append((code, out.splitlines()[-1]))
    assert answers == [
        (7, "3 passed, 0 failed"),
        (141, "3 passed, 0 failed"),
        (0, "3 passed, 0 failed"),
        (1, "blank.test.sh: its last line was: "),
        (1, "blanks.test.sh: its output was empty"),
    ]


def test_main_reads_the_count_line_guard_from_lib_count_line_guard_sh_beside_it(tmp_path, capfd, monkeypatch):
    scripts = tmp_path / "scripts"
    run_suite = staged_module(scripts)
    guard = scripts / "lib" / "count-line-guard.sh"
    guard.write_text(
        "COUNT_LINE='^[0-9]+ passed, [0-9]+ failed$'\n"
        "COUNTLESS='%s: reworded, no tally\\nsecond line of the refusal\\n'\n"
    )
    code = run_suite.main([fake_suite(tmp_path, "partial.test.sh", "echo partial\nexit 0\n")])
    out, _ = capfd.readouterr()
    answers = [(code, out.splitlines()[-3:])]
    started = []
    monkeypatch.setattr(run_suite.subprocess, "Popen", lambda *a, **k: started.append(a))
    guard.unlink()
    for state in ("missing", "unreadable"):
        if state == "unreadable":
            guard.mkdir()
        code = run_suite.main([fake_suite(tmp_path, "green.test.sh", "echo '1 passed, 0 failed'\n")])
        out, err = capfd.readouterr()
        answers.append((code, out, len(err.splitlines()), "lib/count-line-guard.sh" in err))
    assert (answers, started) == ([
        (1, ["partial.test.sh: reworded, no tally", "second line of the refusal",
             "partial.test.sh: its last line was: partial"]),
        (2, "", 1, True),
        (2, "", 1, True),
    ], [])


def test_main_renders_the_countless_refusal_as_bash_printf_does_with_the_suite_name_its_one_argument(tmp_path, capfd):
    scripts = tmp_path / "scripts"
    run_suite = staged_module(scripts)
    (scripts / "lib" / "count-line-guard.sh").write_text(
        "COUNT_LINE='^[0-9]+ passed, [0-9]+ failed$'\n"
        "COUNTLESS='%s: 100%% sure\\ttab\\\\back %s end\\n'\n"
    )
    code = run_suite.main([fake_suite(tmp_path, "partial.test.sh", "echo partial\nexit 0\n")])
    out, _ = capfd.readouterr()
    assert (code, out.splitlines()[-2:]) == (
        1, ["partial.test.sh: 100% sure\ttab\\back  end", "partial.test.sh: its last line was: partial"]
    )


def test_main_renders_the_countless_refusal_escapes_and_an_argless_conversion_as_bash_printf_does(tmp_path, capfdbinary):
    scripts = tmp_path / "scripts"
    run_suite = staged_module(scripts)
    (scripts / "lib" / "count-line-guard.sh").write_text(
        "COUNT_LINE='^[0-9]+ passed, [0-9]+ failed$'\n"
        "COUNTLESS='%s: cr\\rbell\\a\\0101oct %d end\\n'\n"
    )
    code = run_suite.main([fake_suite(tmp_path, "partial.test.sh", "echo partial\nexit 0\n")])
    out, _ = capfdbinary.readouterr()
    assert (code, out.split(b"\n")[-3:]) == (
        1, [b"partial.test.sh: cr\rbell\a\b1oct 0 end", b"partial.test.sh: its last line was: partial", b""]
    )
