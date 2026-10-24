"""In-process cases for veri/transform_touches_tests.py, the module transform-touches-tests.sh is a shim over."""
import importlib
import subprocess
import sys
from pathlib import Path

import pytest

USAGE = "usage: transform-touches-tests.sh <base-sha>\n"
SKILL_DIR = Path(__file__).resolve().parents[3]


def git(repo, *args):
    done = subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test",
                           *args], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def new_repo(path):
    path.mkdir()
    git(path, "init", "-q", "-b", "main")
    return path


def commit_all(repo, message, **files):
    for name, text in files.items():
        target = repo / name.replace("__", "/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def widget_repo(path):
    repo = new_repo(path)
    commit_all(repo, "feat: widget", **{"src__widget.sh": "widget() { echo 1; }\n",
                                        "tests__widget.test.sh": "widget | grep 1\n"})
    base = git(repo, "rev-parse", "HEAD")
    commit_all(repo, "refactor: reformat widget", **{"src__widget.sh": "widget() {\n  echo 1\n}\n"})
    commit_all(repo, "refactor: loosen the widget test", **{"tests__widget.test.sh": "widget | grep -F 1\n"})
    commit_all(repo, "refactor: printf in widget", **{"src__widget.sh": 'widget() {\n  printf "1\\n"\n}\n'})
    return repo, base


@pytest.fixture
def transform_touches_tests():
    return importlib.import_module("veri.transform_touches_tests")


def as_requested(text, kwargs):
    wants_str = kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")
    return text if wants_str else text.encode()


def refused(*args, **kwargs):
    raise AssertionError(f"unexpected subprocess entry: {args!r}")


@pytest.fixture
def git_fakes(monkeypatch):
    """subprocess.run answering git log and sort -u from the returned script; every other entry refuses."""
    script = {"log_code": 0, "log_text": "", "raise": None, "sorted_out": None, "calls": [], "sorts": []}

    def fake_run(args, *rest, **kwargs):
        args = list(args)
        script["calls"].append((args, kwargs))
        if args[:2] == ["git", "log"]:
            if script["raise"]:
                raise script["raise"]
            return subprocess.CompletedProcess(
                args, script["log_code"], as_requested(script["log_text"], kwargs), None)
        if args[:1] == ["sort"]:
            given = kwargs.get("input") or ""
            given = given.decode() if isinstance(given, bytes) else given
            script["sorts"].append((args, given))
            if script["sorted_out"] is not None:
                joined = script["sorted_out"]
            else:
                lines = sorted(set(line for line in given.split("\n") if line))
                joined = "".join(line + "\n" for line in lines)
            return subprocess.CompletedProcess(args, 0, as_requested(joined, kwargs), None)
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", fake_run)
    for entry in ("Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, entry, refused)
    return script


def test_main_refuses_a_missing_or_unresolvable_base_sha_with_exit_2_and_the_usage_line(
        monkeypatch, capsys, transform_touches_tests):
    calls = []

    def fake(args, *rest, **kwargs):
        calls.append(list(args))
        code = 1 if list(args)[:2] == ["git", "rev-parse"] else 0
        return subprocess.CompletedProcess(args, code, "", "")

    for entry in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, entry, fake)

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
    ignored = ("pkg/contests/x", "Tests/c", "test/d", "foo_test.go", r'"tests/\303\251.sh"')
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


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range holds a test file")
def test_transform_range_production_only_exits_0_and_a_changed_test_file_exits_1_naming_it(
        tmp_path, transform_touches_tests, run_cli):
    repo, base = widget_repo(tmp_path / "transform")
    assert run_cli(transform_touches_tests, [base], cwd=repo) == (
        1, "transform changed a test file: tests/widget.test.sh\n", "")
    assert run_cli(transform_touches_tests, [git(repo, "rev-parse", "HEAD~1")], cwd=repo) == (0, "", "")


@pytest.mark.process("git rev-parse over a scratch repository that lacks the base commit")
def test_unresolvable_base_sha_exits_2_with_a_diagnostic_naming_it(tmp_path, transform_touches_tests, run_cli):
    repo, _ = widget_repo(tmp_path / "transform")
    bogus = "0123456789abcdef0123456789abcdef01234567"
    code, out, err = run_cli(transform_touches_tests, [bogus], cwd=repo)
    assert (code, out) == (2, "")
    assert bogus in err


@pytest.mark.process("git rev-parse over a scratch repository for a name that is no revision")
def test_base_sha_nosuch_exits_2_with_nothing_on_stdout_and_the_refusal_then_the_usage_on_stderr(
        tmp_path, transform_touches_tests, run_cli):
    repo, _ = widget_repo(tmp_path / "transform")
    assert run_cli(transform_touches_tests, ["nosuch"], cwd=repo) == (
        2, "", "transform-touches-tests.sh: base-sha does not resolve to a commit: nosuch\n" + USAGE)


@pytest.mark.process("transform-touches-tests.sh run through a symlink to the skill directory from another repository")
def test_a_shim_run_through_a_symlink_and_from_another_repository_answers_as_in_place(tmp_path):
    repo, base = widget_repo(tmp_path / "transform")
    (tmp_path / "linked-skill").symlink_to(SKILL_DIR, target_is_directory=True)
    in_place = SKILL_DIR / "scripts" / "transform-touches-tests.sh"
    linked = tmp_path / "linked-skill" / "scripts" / "transform-touches-tests.sh"

    def run(script, sha):
        done = subprocess.run([str(script), sha], cwd=repo, capture_output=True, text=True)
        return done.returncode, done.stdout, done.stderr

    dirty = run(linked, base)
    clean = run(linked, git(repo, "rev-parse", "HEAD~1"))
    assert dirty[0] == 1 and "tests/widget.test.sh" in dirty[1]
    assert clean == (0, "", "")
    assert dirty == run(in_place, base)
    assert clean == run(in_place, git(repo, "rev-parse", "HEAD~1"))


@pytest.mark.process("git log over scratch repositories, read against refactor-owed's own test-path rule")
def test_transform_touches_tests_and_refactor_owed_append_agree_on_what_a_test_file_is(
        tmp_path, transform_touches_tests, run_cli):
    owed = importlib.import_module("veri.refactor_owed")
    repo = new_repo(tmp_path / "agree")
    commit_all(repo, "chore: seed", README="seed\n")
    problems = []
    for path, want in (("pkg/tests/fixture.sh", "test"), ("pkg/contests/entry.sh", "not-test")):
        base = git(repo, "rev-parse", "HEAD")
        commit_all(repo, f"refactor: touch {path}", **{path.replace("/", "__"): "x\n"})
        touches_code = run_cli(transform_touches_tests, [base], cwd=repo)[0]
        touches_says = "test" if touches_code == 1 else "not-test"

        owed_file = tmp_path / f"owed-{want}.md"
        run_cli(owed, ["append", str(owed_file), "a step", path],
                stdin="CANDIDATES: structural | fold the two walks into one\n")
        list_code = run_cli(owed, ["list", str(owed_file)])[0]
        owed_says = "test" if list_code == 3 else "not-test"
        if touches_says != want or owed_says != want:
            problems.append(f"{path}: want {want} from both; transform-touches-tests.sh says {touches_says}"
                            f" (exit {touches_code}), refactor-owed.sh append says {owed_says}"
                            f" (list exit {list_code})")
    assert problems == []


@pytest.mark.process("git log failing on a commit object deleted from a scratch repository")
def test_base_sha_resolves_but_git_log_fails_on_a_missing_commit_object_exits_2_never_0(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "broken")
    base = commit_all(repo, "feat: a", src__a_sh="a\n")
    middle = commit_all(repo, "refactor: b", src__a_sh="b\n")
    commit_all(repo, "refactor: c", src__a_sh="c\n")
    (repo / ".git" / "objects" / middle[:2] / middle[2:]).unlink()
    code, out, _ = run_cli(transform_touches_tests, [base], cwd=repo)
    assert (code, out) == (2, "")


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range changes two files")
def test_bound_argument_exits_1_naming_each_file_changed_outside_it_and_0_when_all_are_inside(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "bounded")
    base = commit_all(repo, "feat: seed", **{"src__a.sh": "a\n", "src__b.sh": "b\n", "src__c.sh": "c\n"})
    commit_all(repo, "refactor: a and b", **{"src__a.sh": "a2\n", "src__b.sh": "b2\n"})
    commit_all(repo, "refactor: c", **{"src__c.sh": "c2\n"})

    code, out, err = run_cli(transform_touches_tests, [base, "src/a.sh"], cwd=repo)
    assert (code, err) == (1, "")
    assert "src/b.sh" in out and "src/c.sh" in out and "src/a.sh" not in out

    assert run_cli(transform_touches_tests, [base, "src/a.sh,src/b.sh,src/c.sh"], cwd=repo) == (0, "", "")


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range sweeps in the refactor-owed file")
def test_2027_a_commit_sweeping_in_the_refactor_owed_file_is_not_outside_the_bound_but_any_other_file_is(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "owed")
    base = commit_all(repo, "feat: seed", **{"src__a.sh": "a\n", "src__b.sh": "b\n"})
    commit_all(repo, "refactor: a, with the owed file swept in by commit -a",
               **{"src__a.sh": "a2\n", ".tdd__issue-2027-refactor-owed.md": "| fold | budget-spent |\n"})

    assert run_cli(transform_touches_tests, [base, "src/a.sh"], cwd=repo) == (0, "", "")

    commit_all(repo, "refactor: b", **{"src__b.sh": "b2\n"})
    code, out, err = run_cli(transform_touches_tests, [base, "src/a.sh"], cwd=repo)
    assert (code, err) == (1, "")
    assert "src/b.sh" in out and ".tdd/" not in out


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range touches a .tdd/ file other than the refactor-owed one")
def test_2027_a_commit_touching_any_other_tdd_file_is_still_outside_the_bound(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "other-tdd")
    base = commit_all(repo, "feat: seed", **{"src__a.sh": "a\n"})
    commit_all(repo, "refactor: a, with the ledger swept in",
               **{"src__a.sh": "a2\n", ".tdd__issue-7.md": "- [x] step\n"})

    code, out, err = run_cli(transform_touches_tests, [base, "src/a.sh"], cwd=repo)
    assert (code, err) == (1, "")
    assert ".tdd/issue-7.md" in out and "src/a.sh" not in out


@pytest.mark.process("git over a scratch repository whose bound is the green commit's files plus a file the candidate names")
def test_2305_a_covered_candidates_transform_is_inside_the_bound_on_the_files_it_names_and_refused_on_a_planted_one(
        tmp_path, transform_touches_tests, run_cli):
    refactor_touched = importlib.import_module("veri.refactor_touched")
    repo = new_repo(tmp_path / "covered")
    commit_all(repo, "feat: seed", **{"src__a.sh": "a\n", "src__b.sh": "b\n", "src__c.sh": "c\n"})
    green = commit_all(repo, "feat: green", **{"src__a.sh": "a2\n"})
    code, bound, _ = run_cli(refactor_touched, [green, "--candidate", "move the helper in b.sh"], cwd=repo)
    assert (code, bound.strip()) == (0, "src/a.sh,src/b.sh")

    commit_all(repo, "refactor: the candidate", **{"src__b.sh": "b2\n"})
    assert run_cli(transform_touches_tests, [green, bound.strip()], cwd=repo) == (0, "", "")

    commit_all(repo, "refactor: planted", **{"src__c.sh": "c2\n"})
    code, out, err = run_cli(transform_touches_tests, [green, bound.strip()], cwd=repo)
    assert (code, err) == (1, "")
    assert "src/c.sh" in out and "src/b.sh" not in out
