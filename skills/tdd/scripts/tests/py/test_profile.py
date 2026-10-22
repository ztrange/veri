"""In-process cases for veri/profile.py, the module profile.sh is a shim over."""
import ast
import importlib
import os
import re
import shutil
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.fixture
def profile():
    return importlib.import_module("veri.profile")


def traced(trace=""):
    """An answer for the shared fake: a traced bash that writes <trace> to the fd 9 it is handed,
    and a sort that hands its input back."""
    def answer(line, **kwargs):
        program = line.split()[0]
        if program == "bash":
            if trace and 9 in kwargs.get("pass_fds", ()):
                os.write(9, trace.encode())
            return 0, "", ""
        if program == "sort":
            return 0, kwargs.get("input") or "", ""
        raise AssertionError("unexpected command: %s" % line)
    return answer


def test_main_refuses_a_bad_threshold_answers_nothing_for_no_suite_and_refuses_a_suite_with_no_counter(tmp_path, monkeypatch, capsys, profile, fake_processes):
    suite = tmp_path / "a.test.sh"
    suite.write_text("pass=0\n")

    calls = fake_processes(traced())
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "abc")
    code = profile.main([str(suite)])
    captured = capsys.readouterr()
    assert calls == []
    assert (code, captured.out, captured.err) == (
        2, "", "profile.sh: VERI_PROFILE_THRESHOLD must be a number of seconds, got 'abc'\n")

    monkeypatch.delenv("VERI_PROFILE_THRESHOLD")
    code = profile.main([])
    captured = capsys.readouterr()
    assert calls == ["sort -rn"]
    assert (code, captured.out) == (0, "")

    del calls[:]
    code = profile.main([str(suite)])
    captured = capsys.readouterr()
    assert calls[0].startswith("bash ") and calls[0].endswith(" " + str(suite))
    assert (code, captured.out, captured.err) == (
        2, "", "profile.sh: %s: no pass=/fail= increment in its trace\n" % suite)


@pytest.mark.parametrize("threshold", ["1.", ".5", "1e3", " 1"])
def test_main_refuses_a_threshold_that_is_not_digits_with_an_optional_fraction(threshold, tmp_path, monkeypatch, capsys, profile, fake_processes):
    suite = tmp_path / "a.test.sh"
    suite.write_text("pass=0\n")
    calls = fake_processes(traced())
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", threshold)
    code = profile.main([str(suite)])
    captured = capsys.readouterr()
    assert calls == []
    assert (code, captured.out, captured.err) == (
        2, "", "profile.sh: VERI_PROFILE_THRESHOLD must be a number of seconds, got '%s'\n" % threshold)


def test_main_prints_each_case_as_secs_suite_case_n_and_its_line_range(tmp_path, monkeypatch, capsys, profile, fake_processes):
    (tmp_path / "format.test.sh").write_text("pass=0\n")
    monkeypatch.chdir(tmp_path)
    fake_processes(traced((
        "++10.000000 2 pass=0\n"
        "++10.000000 2 fail=0\n"
        "++10.000000 3 EPOCHREALTIME=10.000000\n"
        "++10.000000 4 pass=1\n"
        "++10.000000 5 EPOCHREALTIME=11.000000\n"
        "++11.000000 6 x=1\n"
        "++11.000000 7 EPOCHREALTIME=13.000000\n"
        "++13.000000 8 pass=2\n")))
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "0")
    code = profile.main(["format.test.sh"])
    captured = capsys.readouterr()
    assert (code, captured.out) == (
        0, "0.000000 format.test.sh case 1 L2-4\n3.000000 format.test.sh case 2 L5-8\n")


def test_main_prints_a_case_when_its_seconds_reach_the_threshold_default_1(tmp_path, monkeypatch, capsys, profile, fake_processes):
    def trace(*secs):
        lines, stamp = [], 10.0
        for n, d in enumerate(secs, 1):
            lines.append("++%.6f %d x=%d\n" % (stamp, 2 * n, n))
            stamp += d
            lines.append("++%.6f %d pass=%d\n" % (stamp, 2 * n + 1, n))
        return "".join(lines)

    def printed(threshold):
        monkeypatch.setenv("VERI_PROFILE_THRESHOLD", threshold)
        code = profile.main(["t.test.sh"])
        out = capsys.readouterr().out
        ordered = sorted(out.splitlines(), key=lambda line: float(line.split()[0]), reverse=True)
        return code, [int(line.split()[3]) for line in ordered]

    (tmp_path / "t.test.sh").write_text("pass=0\n")
    monkeypatch.chdir(tmp_path)

    fake_processes(traced(trace(1.0, 0.9)))
    assert printed("") == (0, [1])

    fake_processes(traced(trace(0.25, 2.0, 5.0, 3.0)))
    assert printed("0") == (0, [3, 4, 2, 1])
    assert printed("1") == (0, [3, 4, 2])
    assert printed("2.5") == (0, [3, 4])
    assert printed("4") == (0, [3])


def test_main_runs_each_suite_under_a_traced_bash_and_every_line_through_one_sort(tmp_path, monkeypatch, capsys, profile):
    import tempfile

    traces = {"a.test.sh": "++10.000000 2 x=1\n++11.000000 3 x=2\n++12.000000 4 pass=1\n",
              "b.test.sh": "++20.000000 2 pass=1\n"}
    for suite in traces:
        (tmp_path / suite).write_text("pass=0\n")
    scratch = tmp_path / "tmp"
    scratch.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    monkeypatch.delenv("BASH_XTRACEFD", raising=False)
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "0")
    devnull = os.stat("/dev/null")

    def is_devnull(handle):
        if handle == subprocess.DEVNULL:
            return True
        fd = handle if isinstance(handle, int) and handle >= 0 else getattr(handle, "fileno", lambda: -1)()
        if fd < 0:
            return False
        st = os.fstat(fd)
        return (st.st_dev, st.st_ino) == (devnull.st_dev, devnull.st_ino)

    def fake(sort_status):
        seen = {"calls": [], "env": [], "devnull": [], "trace": [], "sort_input": []}

        def fake_run(args, **kwargs):
            program = os.path.basename(str(args[0]))
            seen["calls"].append([program] + [str(a) for a in args[1:]])
            if program == "bash":
                env = kwargs.get("env")
                seen["env"].append((os.environ if env is None else env).get("BASH_XTRACEFD"))
                seen["devnull"].append([is_devnull(kwargs.get(k)) for k in ("stdin", "stdout", "stderr")])
                inherited = 9 in kwargs.get("pass_fds", ()) or kwargs.get("close_fds") is False
                if inherited:
                    st = os.fstat(9)
                    held = [os.stat(scratch / name).st_ino for name in os.listdir(scratch)]
                    seen["trace"].append((st.st_size, held == [st.st_ino]))
                    os.write(9, traces[str(args[-1])].encode())
                else:
                    seen["trace"].append(None)
                return subprocess.CompletedProcess(args, 1 if args[-1] == "a.test.sh" else 0, None, None)
            if program == "sort":
                text = kwargs.get("input") or ""
                seen["sort_input"].append(text.decode() if isinstance(text, bytes) else text)
                out = "printed as it is\n"
                return subprocess.CompletedProcess(args, sort_status, out.encode() if isinstance(text, bytes) else out, None)
            raise AssertionError("unexpected command: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        return seen

    traced = 'PS4=\'+${EPOCHREALTIME} ${LINENO} \'; set -x; . "$0"'
    seen = fake(0)
    code = profile.main(["a.test.sh", "b.test.sh"])
    captured = capsys.readouterr()
    assert seen["calls"] == [["bash", "-c", traced, "a.test.sh"], ["bash", "-c", traced, "b.test.sh"], ["sort", "-rn"]]
    assert seen["env"] == ["9", "9"]
    assert seen["devnull"] == [[True, True, True], [True, True, True]]
    assert seen["trace"] == [(0, True), (0, True)]
    assert sorted(seen["sort_input"][0].splitlines()) == [
        "0.000000 b.test.sh case 1 L2-2", "2.000000 a.test.sh case 1 L2-4"]
    assert (code, captured.out) == (0, "printed as it is\n")
    assert os.listdir(scratch) == []

    for status, answer in ((3, 3), (1, 1), (5, 2), (141, 2)):
        seen = fake(status)
        code = profile.main(["a.test.sh", "b.test.sh"])
        captured = capsys.readouterr()
        assert (status, code, captured.out) == (status, answer, "printed as it is\n")
        assert os.listdir(scratch) == []


def test_main_reads_only_double_plus_lines_and_cuts_a_case_where_a_three_field_counter_rises_above_its_last_value(tmp_path, monkeypatch, capsys, profile, fake_processes):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "grammar.test.sh").write_text("pass=0\n")
    monkeypatch.chdir(tmp_path)
    fake_processes(traced((
        "++ 2 x=0\n"
        "+10.000000 3 pass=1\n"
        "++10.000000 4 x=1\n"
        "+++10.500000 5 pass=9\n"
        "++11.000000 6 pass=7\n"
        "++12.000000 7 pass=3\n"
        "++13.000000 8 pass=5 extra\n"
        "++14.000000 9 pass=4\n")))
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "0")
    code = profile.main(["sub/grammar.test.sh"])
    captured = capsys.readouterr()
    assert (code, captured.out) == (
        0, "1.000000 sub/grammar.test.sh case 1 L2-6\n3.000000 sub/grammar.test.sh case 2 L7-9\n")


def test_main_ends_the_run_at_a_suite_with_no_counter_still_sorting_the_lines_before_it(tmp_path, monkeypatch, capsys, profile):
    traces = {"a.test.sh": "++10.000000 2 x=1\n++12.000000 3 pass=1\n",
              "none.test.sh": "++20.000000 2 x=1\n",
              "c.test.sh": "++30.000000 2 pass=1\n"}
    for suite in traces:
        (tmp_path / suite).write_text("pass=0\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "0")
    calls = []

    def fake_run(args, **kwargs):
        program = os.path.basename(str(args[0]))
        calls.append([program, str(args[-1])])
        if program == "bash":
            if 9 in kwargs.get("pass_fds", ()):
                os.write(9, traces.get(str(args[-1]), "").encode())
            return subprocess.CompletedProcess(args, 0, "", "")
        if program == "sort":
            text = kwargs.get("input") or ""
            return subprocess.CompletedProcess(args, 0, text.decode() if isinstance(text, bytes) else text, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    code = profile.main(["a.test.sh", "none.test.sh", "c.test.sh"])
    captured = capsys.readouterr()
    assert calls == [["bash", "a.test.sh"], ["bash", "none.test.sh"], ["sort", "-rn"]]
    assert (code, captured.out, captured.err) == (
        2, "2.000000 a.test.sh case 1 L2-3\n",
        "profile.sh: none.test.sh: no pass=/fail= increment in its trace\n")

    del calls[:]
    code = profile.main(["missing.test.sh"])
    captured = capsys.readouterr()
    assert calls == [["bash", "missing.test.sh"], ["sort", "-rn"]]
    assert (code, captured.out, captured.err) == (
        2, "", "profile.sh: missing.test.sh: no pass=/fail= increment in its trace\n")


FORMAT_SUITE = """unset EPOCHREALTIME
pass=0; fail=0
EPOCHREALTIME=10.000000
pass=$((pass + 1))
EPOCHREALTIME=11.000000
x=1
EPOCHREALTIME=13.000000
pass=$((pass + 1))
echo "${pass:-0} passed, $fail failed"
"""

ROOT = SCRIPTS.parents[2]
SUITE_PATH = r"skills/tdd/scripts/tests/[^ ;\"]+\.test\.sh"


def make_n(target):
    ran = subprocess.run(["make", "--no-print-directory", "-n", "-C", str(ROOT), target],
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout + ran.stderr


def suites_named(recipe):
    return sorted(set(re.findall(SUITE_PATH, recipe)))


@pytest.mark.process("a bash that takes no PS4 from its environment, started by the profiler")
@pytest.mark.parametrize("mode", ["unset", "override"])
def test_main_stamps_lines_under_a_traced_bash_that_takes_no_ps4_from_its_environment(mode, tmp_path, run_cli, profile):
    fixture = tmp_path / "format.test.sh"
    fixture.write_text(FORMAT_SUITE)
    shim = tmp_path / "shim"
    shim.mkdir()
    ps4_line = "unset PS4" if mode == "unset" else 'PS4="+ "; export PS4'
    (shim / "bash").write_text('#!/bin/sh\n%s\nexec "%s" "$@"\n' % (ps4_line, shutil.which("bash")))
    (shim / "bash").chmod(0o755)

    code, out, _ = run_cli(profile, [str(fixture)], env={
        "PATH": "%s:%s" % (shim, os.environ["PATH"]), "VERI_PROFILE_THRESHOLD": "1"}, cwd=tmp_path)

    secs, _, rest = out.partition(" ")
    assert (code, float(secs), rest) == (0, 3.0, "%s case 2 L5-8\n" % fixture)


@pytest.mark.process("profile.sh run through a symlink to the skills directory, from another cwd")
def test_the_shim_run_through_a_symlink_from_another_directory_reads_a_relative_suite_there_and_prints_it_as_given(tmp_path):
    (tmp_path / "format.test.sh").write_text(FORMAT_SUITE)
    link = tmp_path / "skill-link"
    link.symlink_to(SCRIPTS.parent, target_is_directory=True)

    ran = subprocess.run([str(link / "scripts" / "profile.sh"), "format.test.sh"], cwd=tmp_path,
                         env=dict(os.environ, VERI_PROFILE_THRESHOLD="1"),
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)

    secs, _, rest = ran.stdout.partition(" ")
    assert (ran.returncode, float(secs), rest) == (0, 3.0, "format.test.sh case 2 L5-8\n")


@pytest.mark.process("make -n test and make -n profile, read from the real Makefile")
def test_make_n_profile_names_the_same_suites_as_make_n_test_in_the_same_offline_environment():
    test_code, test_recipe = make_n("test")
    profile_code, profile_recipe = make_n("profile")
    pytest_files = lambda recipe: sorted(set(re.findall(r"skills/tdd/scripts/tests/py/[\w/]*test_\w+\.py", recipe)))

    assert (test_code, profile_code) == (0, 0)
    assert suites_named(test_recipe) == [] and suites_named(profile_recipe) == []
    assert pytest_files(test_recipe) != []
    assert pytest_files(profile_recipe) == pytest_files(test_recipe)
    assert "--durations=0" in profile_recipe
    assert "VERI_PROFILE_THRESHOLD" in profile_recipe
    assert "scripts/profile.sh" not in profile_recipe
    for fragment in ("xcrun -f git",
                     "GIT_CONFIG_KEY_0=http.proxy GIT_CONFIG_VALUE_0=http://127.0.0.1:1",
                     "GIT_CONFIG_KEY_1=protocol.allow GIT_CONFIG_VALUE_1=never",
                     "GIT_CONFIG_KEY_2=protocol.file.allow GIT_CONFIG_VALUE_2=always",
                     "HTTP_PROXY=http://127.0.0.1:1", "HTTPS_PROXY=http://127.0.0.1:1",
                     "NO_PROXY=127.0.0.1,localhost", "LC_ALL=C", "< /dev/null"):
        assert (fragment, fragment in test_recipe, fragment in profile_recipe) == (fragment, True, True)


@pytest.mark.process("make -n test and make -n profile, read from the real Makefile")
def test_make_n_test_never_runs_profile_and_make_n_profile_never_runs_test():
    test_code, test_recipe = make_n("test")
    profile_code, profile_recipe = make_n("profile")

    assert (test_code, profile_code) == (0, 0)
    assert "all suites green" in test_recipe
    assert "--durations=0" in profile_recipe
    assert "--durations=0" not in test_recipe
    assert "all suites green" not in profile_recipe
    assert not re.search(r"(^|[^[:alnum:]_.-])make[^;]*[ \t]profile([ \t;]|$)".replace("[:alnum:]", "A-Za-z0-9"),
                         test_recipe, re.M)
    assert not re.search(r"(^|[^A-Za-z0-9_.-])make[^;]*[ \t]test([ \t;]|$)", profile_recipe, re.M)


@pytest.mark.process("make -n test, read from the real Makefile")
def test_this_file_runs_no_clock_and_profiles_only_fixtures_under_tmp_path_and_make_n_test_names_it():
    source = open(__file__).read()
    nap = "sl" + "eep"
    clocks = [node.lineno for node in ast.walk(ast.parse(source))
              if isinstance(node, ast.Attribute) and node.attr in (nap, "time", "monotonic", "perf_counter")
              or isinstance(node, ast.Name) and node.id == nap]
    def under_tmp_path(node):
        while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            node = node.left
        return isinstance(node, ast.Name) and node.id == "tmp_path"

    unfixtured = []
    calls = 0
    for fn in ast.parse(source).body:
        if not isinstance(fn, ast.FunctionDef):
            continue
        fixtures = {target.id for node in ast.walk(fn) if isinstance(node, ast.Assign) and under_tmp_path(node.value)
                    for target in node.targets if isinstance(target, ast.Name)}
        in_tmp_path = any(isinstance(node, ast.Call) and ast.unparse(node.func) == "monkeypatch.chdir"
                          and node.args and under_tmp_path(node.args[0]) for node in ast.walk(fn))

        def fixture(arg, cwd_tmp):
            if isinstance(arg, ast.Call) and ast.unparse(arg.func) == "str" and len(arg.args) == 1:
                inner = arg.args[0]
                return isinstance(inner, ast.Name) and inner.id in fixtures or under_tmp_path(inner)
            return isinstance(arg, ast.Constant) and isinstance(arg.value, str) and cwd_tmp \
                and not os.path.isabs(arg.value) and ".." not in arg.value.split("/")

        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            func = ast.unparse(node.func)
            if func == "profile.main" and node.args:
                argv = node.args[0]
            elif func == "run_cli" and len(node.args) > 1 and ast.unparse(node.args[0]) == "profile":
                argv = node.args[1]
            elif func == "subprocess.run" and node.args and isinstance(node.args[0], ast.List) \
                    and node.args[0].elts and "profile.sh" in ast.unparse(node.args[0].elts[0]):
                argv = ast.List(elts=node.args[0].elts[1:])
            else:
                continue
            calls += 1
            cwd_tmp = in_tmp_path or any(k.arg == "cwd" and under_tmp_path(k.value) for k in node.keywords)
            if not isinstance(argv, ast.List) or not all(fixture(arg, cwd_tmp) for arg in argv.elts):
                unfixtured.append(node.lineno)
    code, test_recipe = make_n("test")

    assert (clocks, unfixtured) == ([], [])
    assert calls > 0
    assert (code, "skills/tdd/scripts/tests/py/test_profile.py" in test_recipe) == (0, True)


@pytest.mark.process("make profile run on the real Makefile over a pytest fixture file")
def test_make_profile_reports_a_pytest_case_at_or_above_the_threshold(tmp_path):
    fixture = tmp_path / "test_fx.py"
    fixture.write_text("def test_quick():\n    assert True\n")

    def profiled(threshold):
        return subprocess.run(["make", "--no-print-directory", "-C", str(ROOT), "profile", "TESTS=%s" % fixture],
                              env=dict(os.environ, VERI_PROFILE_THRESHOLD=threshold, VERI_PYTEST_WORKERS="1"),
                              stdin=subprocess.DEVNULL, capture_output=True, text=True)

    reported = profiled("0")
    skipped = profiled("1000")

    assert reported.returncode == 0, reported.stdout + reported.stderr
    assert "test_fx.py::test_quick" in reported.stdout
    assert (skipped.returncode, "test_fx.py::test_quick" in skipped.stdout) == (0, False)
