"""In-process cases for veri/run_suite.py, the module run-suite.sh is a shim over."""
import errno
import importlib
import importlib.util
import os
import shutil
import subprocess
import sys

import pytest

from conftest import SCRIPTS


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
    for name in [k for k in os.environ if k.startswith(("VERI_", "CLAUDE_")) and k != "VERI_VENV"]:
        monkeypatch.delenv(name)
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


def stub_python(path):
    path.parent.mkdir(parents=True)
    path.write_text(
        "#!/bin/sh\n"
        "printf '%s %s\\n' \"$0\" \"$*\" >> \"$STUB_LOG\"\n"
        "[ \"$3\" = --version ] && exit \"$STUB_VERSION_CODE\"\n"
        "cat >> \"$STUB_LOG\"\n"
        "echo 'no tally here'\n"
        "exit \"$STUB_RUN_CODE\"\n"
    )
    path.chmod(0o755)
    return str(path)


def test_main_runs_a_pytest_suite_under_the_venv_python_and_maps_its_exit_code_without_a_count_line_check(tmp_path, capfd, monkeypatch, run_suite):
    suite = tmp_path / "tests" / "py" / "test_fake.py"
    suite.parent.mkdir(parents=True)
    suite.write_text("def test_nothing():\n    pass\n")
    venv_py = stub_python(tmp_path / "venv" / "bin" / "python3")
    home_py = stub_python(tmp_path / "home" / ".veri-tools" / "venv" / "bin" / "python3")
    path_py = stub_python(tmp_path / "pathbin" / "python3")
    log = tmp_path / "stub.log"
    monkeypatch.setenv("STUB_LOG", str(log))
    monkeypatch.setenv("PATH", str(tmp_path / "pathbin") + os.pathsep + os.environ["PATH"])
    leaked = tmp_path / "stdin.txt"
    leaked.write_text("leaked stdin\n")
    saved_stdin = os.dup(0)
    answers = []
    try:
        with open(leaked) as f:
            os.dup2(f.fileno(), 0)
        for venv, home, version_code, run_code in (
            (str(tmp_path / "venv"), str(tmp_path / "home"), "0", "0"),
            (None, str(tmp_path / "home"), "0", "0"),
            (None, str(tmp_path / "nohome"), "0", "0"),
            (str(tmp_path / "venv"), str(tmp_path / "home"), "1", "0"),
            *((str(tmp_path / "venv"), str(tmp_path / "home"), "0", code) for code in "12345"),
        ):
            if venv is None:
                monkeypatch.delenv("VERI_VENV", raising=False)
            else:
                monkeypatch.setenv("VERI_VENV", venv)
            monkeypatch.setenv("HOME", home)
            monkeypatch.setenv("STUB_VERSION_CODE", version_code)
            monkeypatch.setenv("STUB_RUN_CODE", run_code)
            log.write_text("")
            code = run_suite.main([str(suite)])
            out, err = capfd.readouterr()
            answers.append((code, log.read_text().splitlines(), err, "never reached its count line" in out))
    finally:
        os.dup2(saved_stdin, 0)
        os.close(saved_stdin)

    def ran(py, code):
        return (code, ["%s -m pytest --version" % py, "%s -m pytest %s" % (py, suite)], "", False)

    assert answers == [
        ran(venv_py, 0),
        ran(home_py, 0),
        ran(path_py, 0),
        (2, ["%s -m pytest --version" % venv_py],
         "run-suite.sh: pytest cannot be imported by %s; run make install-dev\n" % venv_py, False),
        ran(venv_py, 1),
        ran(venv_py, 2),
        ran(venv_py, 3),
        ran(venv_py, 2),
        ran(venv_py, 2),
    ]


def test_main_refuses_a_pytest_suite_with_no_venv_python_and_no_python3_on_path_naming_an_empty_interpreter(tmp_path, capfd, monkeypatch, run_suite):
    suite = tmp_path / "tests" / "py" / "test_fake.py"
    suite.parent.mkdir(parents=True)
    suite.write_text("def test_nothing():\n    pass\n")
    (tmp_path / "emptybin").mkdir()
    monkeypatch.setenv("VERI_VENV", str(tmp_path / "novenv"))
    monkeypatch.setenv("HOME", str(tmp_path / "nohome"))
    monkeypatch.setenv("PATH", str(tmp_path / "emptybin"))
    started = []

    def start(real):
        def fake(args, *a, **k):
            started.append(list(args))
            if args[0] == "":
                raise FileNotFoundError(errno.ENOENT, "No such file or directory", "")
            return real(args, *a, **k)
        return fake

    monkeypatch.setattr(run_suite.subprocess, "run", start(run_suite.subprocess.run))
    monkeypatch.setattr(run_suite.subprocess, "Popen", start(run_suite.subprocess.Popen))
    code = run_suite.main([str(suite)])
    out, err = capfd.readouterr()
    ran_suite = [args for args in started if str(suite) in args]
    assert (code, out, err, ran_suite) == (
        2, "", "run-suite.sh: pytest cannot be imported by ; run make install-dev\n", []
    )


def test_the_module_run_as_the_shim_hands_off_ends_with_exit_2_when_sigterm_reaches_it_mid_suite(tmp_path):
    suite = fake_suite(tmp_path, "terminates-its-runner.test.sh", 'kill -TERM "$PPID"\necho "1 passed, 0 failed"\n')
    code = subprocess.run([sys.executable, str(SCRIPTS / "veri" / "run_suite.py"), suite],
                          stdin=subprocess.DEVNULL, capture_output=True, timeout=10).returncode
    assert code == 2


def test_the_module_run_as_the_shim_hands_off_exits_128_plus_n_for_a_suite_killed_by_signal_n_after_its_count_line_1167(tmp_path):
    suite = fake_suite(tmp_path, "killed.test.sh", 'echo "1 passed, 0 failed"\nkill -KILL "$$"\n')
    code = subprocess.run([sys.executable, str(SCRIPTS / "veri" / "run_suite.py"), suite],
                          stdin=subprocess.DEVNULL, capture_output=True, timeout=10).returncode
    assert code == 128 + 9


def test_the_module_run_as_the_shim_hands_off_names_a_missing_suite_on_stderr_without_a_traceback_and_exits_1_1167(tmp_path):
    suite = tmp_path / "missing.test.sh"
    run = subprocess.run([sys.executable, str(SCRIPTS / "veri" / "run_suite.py"), str(suite)],
                         stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
    err = run.stderr.decode()
    assert (run.returncode, "Traceback" in err, err.splitlines()[-2:]) == (
        1, False, ["missing.test.sh: never reached its count line", "missing.test.sh: its output was empty"]
    )


def test_the_module_run_as_the_shim_hands_off_names_a_non_executable_suite_on_stderr_without_a_traceback_and_exits_1_1167(tmp_path):
    suite = tmp_path / "not-executable.test.sh"
    suite.write_text('#!/bin/sh\necho "1 passed, 0 failed"\n')
    run = subprocess.run([sys.executable, str(SCRIPTS / "veri" / "run_suite.py"), str(suite)],
                         stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
    err = run.stderr.decode()
    assert (run.returncode, "Traceback" in err, err.splitlines()[-2:]) == (
        1, False, ["not-executable.test.sh: never reached its count line", "not-executable.test.sh: its output was empty"]
    )


def test_main_hands_a_bash_suite_no_ambient_veri_or_claude_variable_but_veri_venv_and_lets_the_suite_set_one_on_a_command_1258(tmp_path, capfd, monkeypatch, run_suite):
    for name in [k for k in os.environ if k.startswith(("VERI_", "CLAUDE_", "GIT_CONFIG_"))]:
        monkeypatch.delenv(name)
    monkeypatch.setenv("VERI_MODEL", "ambient-model")
    monkeypatch.setenv("VERI_ISSUE", "954")
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    monkeypatch.setenv("CLAUDE_BIN", "/ambient/claude")
    monkeypatch.setenv("VERI_VENV", "/caller/venv")
    monkeypatch.setenv("PATH", "/caller/bin:" + os.environ["PATH"])
    monkeypatch.setenv("OFFLINE_REACH_LOG", "/caller/reach.log")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:1")
    seen_env = tmp_path / "suite.env"
    seen_child = tmp_path / "child.out"
    suite = fake_suite(tmp_path, "ambient.test.sh",
                       'env > "%s"\n'
                       'VERI_MODEL=set-by-suite sh -c \'printf %%s "$VERI_MODEL"\' > "%s"\n'
                       'echo "1 passed, 0 failed"\n' % (seen_env, seen_child))
    code = run_suite.main([suite])
    capfd.readouterr()
    env = dict(line.split("=", 1) for line in seen_env.read_text().splitlines() if "=" in line)
    leaked = sorted(k for k in env if k.startswith(("VERI_", "CLAUDE_")) and k != "VERI_VENV")
    kept = {k: env.get(k) for k in ("VERI_VENV", "PATH", "OFFLINE_REACH_LOG", "HTTPS_PROXY",
                                    "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0")}
    assert (code, leaked, kept, seen_child.read_text()) == (0, [], {
        "VERI_VENV": "/caller/venv",
        "PATH": os.environ["PATH"],
        "OFFLINE_REACH_LOG": "/caller/reach.log",
        "HTTPS_PROXY": "http://127.0.0.1:1",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "maintenance.auto",
        "GIT_CONFIG_VALUE_0": "false",
    }, "set-by-suite")


def test_main_hands_a_pytest_suite_no_ambient_veri_or_claude_variable_but_veri_venv_and_still_finds_the_caller_venv_1258(tmp_path, capfd, monkeypatch, run_suite):
    for name in [k for k in os.environ if k.startswith(("VERI_", "CLAUDE_"))]:
        monkeypatch.delenv(name)
    suite = tmp_path / "tests" / "py" / "test_fake.py"
    suite.parent.mkdir(parents=True)
    suite.write_text("def test_nothing():\n    pass\n")
    venv = tmp_path / "venv"
    (venv / "bin").mkdir(parents=True)
    venv_py = venv / "bin" / "python3"
    seen_env = tmp_path / "suite.env"
    venv_py.write_text(
        "#!/bin/sh\n"
        "[ \"$3\" = --version ] && exit 0\n"
        "printf '%%s\\n' \"$0\" > \"%s\"\n"
        "env >> \"%s\"\n" % (seen_env, seen_env)
    )
    venv_py.chmod(0o755)
    monkeypatch.setenv("VERI_MODEL", "ambient-model")
    monkeypatch.setenv("VERI_ISSUE", "954")
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    monkeypatch.setenv("CLAUDE_BIN", "/ambient/claude")
    monkeypatch.setenv("VERI_VENV", str(venv))
    code = run_suite.main([str(suite)])
    capfd.readouterr()
    ran_by, *lines = seen_env.read_text().splitlines()
    env = dict(line.split("=", 1) for line in lines if "=" in line)
    leaked = sorted(k for k in env if k.startswith(("VERI_", "CLAUDE_")) and k != "VERI_VENV")
    assert (code, ran_by, leaked, env.get("VERI_VENV")) == (0, str(venv_py), [], str(venv))
