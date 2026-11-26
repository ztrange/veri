"""In-process cases for veri/transform_touches_tests.py, the module transform-touches-tests.sh is a shim over."""
import importlib
import subprocess
import sys

import pytest

USAGE = "usage: transform-touches-tests.sh <base-sha> [<bound>] [--touched <list>]\n"


@pytest.fixture
def transform_touches_tests():
    return importlib.import_module("veri.transform_touches_tests")


@pytest.fixture
def git_fakes(fake_processes):
    """git log and sort -u answered from the returned script; git rev-parse answers 0; every other command refuses."""
    script = {"log_code": 0, "log_text": "", "raise": None, "sorted_out": None, "calls": [], "sorts": []}

    def answer(line, **kwargs):
        args = list(fake.argvs[-1])
        script["calls"].append((args, kwargs))
        if args[:2] == ["git", "log"]:
            if script["raise"]:
                raise script["raise"]
            return script["log_code"], script["log_text"], None
        if args[:1] == ["sort"]:
            given = kwargs.get("input") or ""
            given = given.decode() if isinstance(given, bytes) else given
            script["sorts"].append((args, given))
            if script["sorted_out"] is not None:
                joined = script["sorted_out"]
            else:
                lines = sorted(set(line for line in given.split("\n") if line))
                joined = "".join(line + "\n" for line in lines)
            return 0, joined, None
        return 0, None, None

    fake = fake_processes.answers({"git rev-parse": answer, "git log": answer, "sort": answer})
    return script


def test_main_refuses_a_missing_or_unresolvable_base_sha_with_exit_2_and_the_usage_line(
        fake_processes, capsys, transform_touches_tests):
    fake = fake_processes.answers({"git rev-parse": (1, "", "")})
    calls = fake.calls

    for argv in ([], [""]):
        code = transform_touches_tests.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)
    assert calls == []

    code = transform_touches_tests.main(["nosuch"])
    captured = capsys.readouterr()
    assert code in range(0, 4)
    assert (code, captured.out, captured.err) == (
        2, "",
        "transform-touches-tests.sh: base-sha does not resolve to a commit: nosuch\n" + USAGE)


def test_main_asks_git_to_resolve_the_base_then_reads_the_range_and_names_its_test_files(
        git_fakes, capsys, transform_touches_tests):
    calls = git_fakes["calls"]
    answers = {}
    for name, text, argv in (
            ("clean", "src/a.sh\n\nsrc/b.py\n", ["HEAD~1"]),
            ("touched", "tests/widget.test.sh\nsrc/a.sh\n", ["HEAD~1"]),
            ("extra", "tests/widget.test.sh\nsrc/a.sh\n", ["HEAD~1", "extra"])):
        calls.clear()
        git_fakes["log_text"] = text
        code = transform_touches_tests.main(argv)
        captured = capsys.readouterr()
        answers[name] = (code, captured.out, captured.err, list(calls))

    for name, (_, _, _, made) in answers.items():
        resolve_args, resolve_kwargs = made[0]
        assert (name, resolve_args, resolve_kwargs.get("stdout"), resolve_kwargs.get("stderr"),
                bool(resolve_kwargs.get("capture_output")), resolve_kwargs.get("cwd")) == (
            name, ["git", "rev-parse", "--verify", "--quiet", "HEAD~1^{commit}"],
            subprocess.DEVNULL, None, False, None)
        git_calls = [(args, kwargs.get("cwd")) for args, kwargs in made if args[:1] == ["git"]]
        assert (name, git_calls) == (name, [
            (["git", "rev-parse", "--verify", "--quiet", "HEAD~1^{commit}"], None),
            (["git", "log", "--format=", "--name-only", "HEAD~1..HEAD"], None)])

    assert answers["clean"][:3] == (0, "", "")
    assert answers["touched"][:3] == (1, "transform changed a test file: tests/widget.test.sh\n", "")
    assert answers["extra"][:3] == answers["touched"][:3]


def test_main_counts_a_path_as_a_test_file_by_the_case_sensitive_ere_on_the_path_as_git_prints_it(
        git_fakes, capsys, transform_touches_tests):
    counted = ("pkg/tests/x", "x.test.js", "my.test.dir", "a.test.d/x",
               r'"pkg/tests/\303\251.sh"', r'"\303\251.test.sh"')
    ignored = ("pkg/contests/x", "Tests/c", "test/d", r'"tests/\303\251.sh"')
    expected, observed = {}, {}
    for path in counted + ignored:
        git_fakes["log_text"] = f"src/a.sh\n{path}\n"
        code = transform_touches_tests.main(["HEAD~1"])
        captured = capsys.readouterr()
        observed[path] = (code, captured.out, captured.err)
        expected[path] = ((1, f"transform changed a test file: {path}\n", "") if path in counted
                          else (0, "", ""))

    assert observed == expected


def test_main_reports_what_sort_u_on_path_prints_with_the_prefix_on_the_first_name_only(
        git_fakes, capsys, transform_touches_tests):
    git_fakes["sorted_out"] = "my.test.dir\npkg/tests/a.sh\ntests/b.sh\nx.test.js\n"
    git_fakes["log_text"] = "x.test.js\ntests/b.sh\n\nsrc/a.sh\npkg/tests/a.sh\nmy.test.dir\n\ntests/b.sh\n"
    code = transform_touches_tests.main(["HEAD~1"])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (
        1,
        "transform changed a test file: my.test.dir\npkg/tests/a.sh\ntests/b.sh\nx.test.js\n",
        "")
    assert git_fakes["sorts"] == [(["sort", "-u"],
                      "x.test.js\ntests/b.sh\npkg/tests/a.sh\nmy.test.dir\ntests/b.sh\n")]


def test_main_ports_the_failure_paths_as_they_are_swallowed_git_log_closed_stdout_and_exceptions(
        monkeypatch, capsys, git_fakes, transform_touches_tests):
    script, calls = git_fakes, git_fakes["calls"]
    script.update(log_code=128, log_text="")
    code = transform_touches_tests.main(["HEAD~1"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", "")
    log_kwargs = [kwargs for args, kwargs in calls if args[:2] == ["git", "log"]]
    assert [(kwargs.get("stderr"), bool(kwargs.get("capture_output"))) for kwargs in log_kwargs] == [
        (None, False)]

    open_stdout = sys.stdout
    monkeypatch.setattr(sys, "stdout", None)
    closed = {}
    for name, text in (("touched", "tests/b.sh\nsrc/a.sh\n"), ("clean", "src/a.sh\n")):
        script.update(log_code=0, log_text=text)
        closed[name] = transform_touches_tests.main(["HEAD~1"])
    monkeypatch.setattr(sys, "stdout", open_stdout)
    assert closed == {"touched": 1, "clean": 0}

    script["raise"] = RuntimeError("unexpected failure inside main")
    with pytest.raises(RuntimeError, match="unexpected failure inside main"):
        transform_touches_tests.main(["HEAD~1"])


def test_2893_a_spec_file_is_a_test_file_only_with_a_js_or_ts_extension(
        git_fakes, capsys, transform_touches_tests):
    observed = {}
    for path in ("docs/a.spec.md", "web/a.spec.ts", "web/b.spec.js"):
        git_fakes["log_text"] = f"src/a.sh\n{path}\n"
        code = transform_touches_tests.main(["HEAD~1"])
        captured = capsys.readouterr()
        observed[path] = (code, captured.out, captured.err)

    assert observed == {
        "docs/a.spec.md": (0, "", ""),
        "web/a.spec.ts": (1, "transform changed a test file: web/a.spec.ts\n", ""),
        "web/b.spec.js": (1, "transform changed a test file: web/b.spec.js\n", ""),
    }


def test_2893_a_go_file_is_a_test_file_only_when_named_with_the_test_go_suffix(
        git_fakes, capsys, transform_touches_tests):
    observed = {}
    for path in ("pkg/x.go", "pkg/x_test.go"):
        git_fakes["log_text"] = f"src/a.sh\n{path}\n"
        code = transform_touches_tests.main(["HEAD~1"])
        captured = capsys.readouterr()
        observed[path] = (code, captured.out, captured.err)

    assert observed == {
        "pkg/x.go": (0, "", ""),
        "pkg/x_test.go": (1, "transform changed a test file: pkg/x_test.go\n", ""),
    }
