"""In-process cases for veri/run_suite.py, the module run-suite.sh is a shim over."""
import importlib
import importlib.util
import os
import pathlib
import shutil
import subprocess
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


class FakeSuite:
    def __init__(self, lines, capfd, seen):
        self._lines = list(lines)
        self._capfd = capfd
        self._seen = seen
        self._shown = ""
        self.returncode = None
        self.stdout = self

    def _next(self, *_):
        self._shown += self._capfd.readouterr().out
        self._seen.append(self._shown)
        return self._lines.pop(0) if self._lines else b""

    read = read1 = readline = _next

    def __iter__(self):
        return iter(self._next, b"")

    def close(self):
        pass

    def poll(self):
        return self.wait() if not self._lines else None

    def wait(self, *_):
        self.returncode = 0
        return 0

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.wait()


def test_main_starts_the_suite_alone_on_dev_null_with_maintenance_auto_off_and_streams_its_lines(tmp_path, capfd, monkeypatch, run_suite):
    lines = [b"one\n", b"two\n", b"3 passed, 0 failed\n"]
    answers = []
    for count in ("2", None):
        for n in range(4):
            monkeypatch.delenv("GIT_CONFIG_KEY_%d" % n, raising=False)
            monkeypatch.delenv("GIT_CONFIG_VALUE_%d" % n, raising=False)
        monkeypatch.delenv("TESTS", raising=False)
        if count is None:
            monkeypatch.delenv("GIT_CONFIG_COUNT", raising=False)
        else:
            monkeypatch.setenv("GIT_CONFIG_COUNT", count)
            monkeypatch.setenv("GIT_CONFIG_KEY_0", "user.name")
            monkeypatch.setenv("GIT_CONFIG_VALUE_0", "caller")
            monkeypatch.setenv("GIT_CONFIG_KEY_1", "http.proxy")
            monkeypatch.setenv("GIT_CONFIG_VALUE_1", "")
        caller = dict(os.environ)
        suite = fake_suite(tmp_path, "streamed.test.sh", "exit 0\n")
        started = []
        seen = []

        def popen(args, **kwargs):
            env = dict(kwargs["env"]) if kwargs.get("env") is not None else dict(os.environ)
            stdin = kwargs.get("stdin")
            started.append((
                list(args) if not isinstance(args, str) else args,
                kwargs.get("shell", False),
                stdin is subprocess.DEVNULL or getattr(stdin, "name", None) == os.devnull,
                {k: v for k, v in env.items() if caller.get(k) != v},
                sorted(set(caller) - set(env)),
            ))
            return FakeSuite(lines, capfd, seen)

        monkeypatch.setattr(run_suite.subprocess, "Popen", popen)
        code = run_suite.main([suite])
        streamed = all(b.decode() in seen[i + 1] for i, b in enumerate(lines))
        answers.append((code, started, streamed))
    n_of = {"2": 2, None: 0}
    assert answers == [
        (0, [([suite], False, True, {
            "GIT_CONFIG_KEY_%d" % n_of[count]: "maintenance.auto",
            "GIT_CONFIG_VALUE_%d" % n_of[count]: "false",
            "GIT_CONFIG_COUNT": str(n_of[count] + 1),
        }, [])], True)
        for count in ("2", None)
    ]
