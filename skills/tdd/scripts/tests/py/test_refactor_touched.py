"""In-process cases for veri/refactor_touched.py, the module refactor-touched.sh is a shim over."""
import importlib
import subprocess
import sys
from pathlib import Path

import pytest

USAGE = "usage: refactor-touched.sh <commit> | --issue <base>\n"
SKILL_DIR = Path(__file__).resolve().parents[3]
MISSING = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"


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


@pytest.fixture
def refactor_touched():
    return importlib.import_module("veri.refactor_touched")


def test_main_with_no_commit_or_no_base_returns_2_with_the_usage_line_alone_and_no_process(
        monkeypatch, capsys, refactor_touched, fake_processes):
    calls = fake_processes()

    for argv in ([], ["--issue"]):
        code = refactor_touched.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)

    assert calls == []


def test_main_with_an_unresolvable_commit_returns_2_naming_it_then_the_usage_line_and_runs_no_diff(
        monkeypatch, capsys, refactor_touched):
    sha = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    calls = []

    def fake(args, *rest, **kwargs):
        calls.append(list(args))
        code = 1 if list(args)[:4] == ["git", "rev-parse", "--verify", "--quiet"] else 0
        return subprocess.CompletedProcess(args, code, "", "")

    for entry in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, entry, fake)

    code = refactor_touched.main([sha])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (
        2, "", f"refactor-touched: cannot resolve commit '{sha}'\n" + USAGE)
    assert [c for c in calls if c[:2] == ["git", "diff"]] == []


def test_main_prints_the_commits_paths_outside_tdd_comma_joined_or_returns_3_when_only_tdd_changed(
        monkeypatch, capsys, refactor_touched):
    sha = "0123456789abcdef0123456789abcdef01234567"
    answers = {}

    def fake(args, *rest, **kwargs):
        args = list(args)
        if args == ["git", "diff", "--name-only", f"{sha}^", sha]:
            out = answers["diff"]
            if not kwargs.get("text") and not kwargs.get("universal_newlines") \
                    and not kwargs.get("encoding"):
                out = out.encode()
            return subprocess.CompletedProcess(args, 0, out, "")
        return subprocess.CompletedProcess(args, 0, "", "")

    for entry in ("run", "Popen", "call", "check_call"):
        monkeypatch.setattr(subprocess, entry, fake)
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: fake(*a, **k).stdout)

    answers["diff"] = "skills/b.sh\n.tdd/issue-1-plan.md\nsub/.tdd/x\na.py\n"
    code = refactor_touched.main([sha])
    captured = capsys.readouterr()
    assert (code, captured.out) == (0, "skills/b.sh,sub/.tdd/x,a.py\n")

    answers["diff"] = ".tdd/issue-1-plan.md\n.tdd/issue-1-skill-commit\n"
    code = refactor_touched.main([sha])
    captured = capsys.readouterr()
    assert (code, captured.out) == (3, "")


def test_main_with_issue_diffs_base_against_head_and_ignores_trailing_and_non_first_issue_arguments(
        monkeypatch, capsys, refactor_touched):
    base = "fedcba9876543210fedcba9876543210fedcba98"
    sha = "0123456789abcdef0123456789abcdef01234567"
    answers = {"resolves": True}
    calls = []

    def fake(args, *rest, **kwargs):
        args = list(args)
        calls.append(args)
        if args[:4] == ["git", "rev-parse", "--verify", "--quiet"]:
            return subprocess.CompletedProcess(args, 0 if answers["resolves"] else 1, "", "")
        if args == ["git", "diff", "--name-only", base, "HEAD"]:
            out = answers["diff"]
        elif args == ["git", "diff", "--name-only", f"{sha}^", sha]:
            out = "c.sh\n"
        else:
            out = ""
        if not kwargs.get("text") and not kwargs.get("universal_newlines") \
                and not kwargs.get("encoding"):
            out = out.encode()
        return subprocess.CompletedProcess(args, 0, out, "")

    for entry in ("run", "Popen", "call", "check_call"):
        monkeypatch.setattr(subprocess, entry, fake)
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: fake(*a, **k).stdout)

    def answer(argv):
        code = refactor_touched.main(argv)
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    answers["diff"] = "a.py\n.tdd/issue-1-plan.md\nb.sh\n"
    assert answer(["--issue", base]) == (0, "a.py,b.sh\n", "")
    assert ["git", "diff", "--name-only", base, "HEAD"] in calls
    assert answer(["--issue", base, "extra"]) == (0, "a.py,b.sh\n", "")

    answers["diff"] = ".tdd/issue-1-plan.md\n"
    assert answer(["--issue", base]) == (3, "", "")

    assert answer([sha, "extra"]) == (0, "c.sh\n", "")
    assert answer([sha, "--issue", base]) == (0, "c.sh\n", "")

    answers["resolves"] = False
    assert answer(["--issue", base]) == (
        2, "", f"refactor-touched: cannot resolve commit '{base}'\n" + USAGE)


def test_main_refuses_an_empty_commit_or_base_and_filters_only_paths_starting_tdd_printed_as_git_prints_them(
        monkeypatch, capsys, refactor_touched, fake_processes):
    sha = "0123456789abcdef0123456789abcdef01234567"
    calls = fake_processes()

    for argv in ([""], ["--issue", ""]):
        code = refactor_touched.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)
    assert calls == []

    diff = 'sub/.tdd/x\n".tdd/\\303\\244.sh"\n.tdd/issue-1-plan.md\na,b.sh\n'

    def fake(args, *rest, **kwargs):
        args = list(args)
        out = diff if args == ["git", "diff", "--name-only", f"{sha}^", sha] else ""
        if not kwargs.get("text") and not kwargs.get("universal_newlines") \
                and not kwargs.get("encoding"):
            out = out.encode()
        return subprocess.CompletedProcess(args, 0, out, "")

    for entry in ("run", "Popen", "call", "check_call"):
        monkeypatch.setattr(subprocess, entry, fake)
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: fake(*a, **k).stdout)

    code = refactor_touched.main([sha])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (
        0, 'sub/.tdd/x,".tdd/\\303\\244.sh",a,b.sh\n', "")


def test_main_runs_git_in_the_callers_directory_letting_its_stderr_through_on_a_failed_rev_parse_or_diff(
        monkeypatch, capsys, tmp_path, refactor_touched):
    root = "0123456789abcdef0123456789abcdef01234567"
    answers = {}
    calls = []

    def fake(args, *rest, **kwargs):
        args = list(args)
        calls.append((args, kwargs))
        if args[:2] == ["git", "rev-parse"]:
            code, err = answers["rev-parse"]
        elif args[:2] == ["git", "diff"]:
            code, err = answers["diff"]
        else:
            code, err = 0, ""
        if err and kwargs.get("stderr") not in (subprocess.PIPE, subprocess.DEVNULL,
                                                 subprocess.STDOUT):
            print(err, file=sys.stderr, end="")
        out = ""
        if not kwargs.get("text") and not kwargs.get("universal_newlines") \
                and not kwargs.get("encoding"):
            out = out.encode()
        return subprocess.CompletedProcess(args, code, out, None)

    for entry in ("run", "Popen", "call", "check_call"):
        monkeypatch.setattr(subprocess, entry, fake)
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: fake(*a, **k).stdout)
    monkeypatch.chdir(tmp_path)

    fatal = "fatal: not a git repository (or any of the parent directories): .git\n"
    answers["rev-parse"] = (128, fatal)
    code = refactor_touched.main(["HEAD"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (
        2, "", fatal + "refactor-touched: cannot resolve commit 'HEAD'\n" + USAGE)

    ambiguous = f"fatal: ambiguous argument '{root}^': unknown revision or path not in the working tree.\n"
    answers["rev-parse"] = (0, "")
    answers["diff"] = (128, ambiguous)
    code = refactor_touched.main([root])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (3, "", ambiguous)

    assert all(args[0] == "git" and "-C" not in args and "cwd" not in kwargs
               for args, kwargs in calls)


@pytest.mark.process("git over a scratch repository holding a green commit with a ledger and two source files")
def test_green_commit_with_ledger_and_two_source_files_prints_only_the_two_in_diff_order(
        tmp_path, refactor_touched, run_cli):
    repo = new_repo(tmp_path / "green")
    commit_all(repo, "plan: scope #7", **{".tdd__issue-7.md": "- [ ] a step\n"})
    green = commit_all(repo, "feat: a step (#7)", **{
        "src__zeta.sh": "zeta\n", "lib__alpha.test.sh": "alpha\n",
        ".tdd__issue-7.md": "- [x] a step \u27c2 refactor pending\n"})
    assert run_cli(refactor_touched, [green], cwd=repo) == (0, "lib/alpha.test.sh,src/zeta.sh\n", "")


@pytest.mark.process("git rev-parse over a scratch repository that lacks the commit")
def test_unresolvable_commit_returns_2_with_a_stderr_diagnostic_naming_it(tmp_path, refactor_touched, run_cli):
    repo = new_repo(tmp_path / "unresolvable")
    commit_all(repo, "feat: alpha", **{"alpha.sh": "alpha\n"})
    code, out, err = run_cli(refactor_touched, [MISSING], cwd=repo)
    assert (code, out) == (2, "")
    assert f"refactor-touched: cannot resolve commit '{MISSING}'" in err


@pytest.mark.process("git diff over a scratch repository whose commit touched only .tdd/")
def test_commit_touching_only_tdd_returns_3_and_prints_nothing(tmp_path, refactor_touched, run_cli):
    repo = new_repo(tmp_path / "ledger-only")
    commit_all(repo, "feat: alpha", **{"alpha.sh": "alpha\n"})
    ledger_only = commit_all(repo, "chore: tick the ledger (#9)",
                             **{".tdd__issue-9.md": "- [x] a step \u27c2 refactor pending\n"})
    assert run_cli(refactor_touched, [ledger_only], cwd=repo)[:2] == (3, "")


@pytest.mark.process("git diff base..HEAD over a scratch repository with three commits past the base")
def test_issue_base_prints_base_to_head_files_outside_tdd_comma_joined_3_when_none_2_when_unresolvable(
        tmp_path, refactor_touched, run_cli):
    repo = new_repo(tmp_path / "issue-range")
    base = commit_all(repo, "plan: scope #11", **{".tdd__issue-11.md": "- [ ] a step\n"})
    commit_all(repo, "feat: a step (#11)", **{"src__zeta.sh": "zeta\n", ".tdd__issue-11.md": "- [x] a step\n"})
    last_code = commit_all(repo, "refactor: alpha (#11)", **{"lib__alpha.test.sh": "alpha\n"})
    commit_all(repo, "chore: tick the ledger (#11)", **{".tdd__issue-11.md": "- [x] a step \u27c2 done\n"})
    assert run_cli(refactor_touched, ["--issue", base], cwd=repo) == (0, "lib/alpha.test.sh,src/zeta.sh\n", "")
    assert run_cli(refactor_touched, ["--issue", last_code], cwd=repo)[:2] == (3, "")
    code, out, err = run_cli(refactor_touched, ["--issue", MISSING], cwd=repo)
    assert (code, out) == (2, "")
    assert f"refactor-touched: cannot resolve commit '{MISSING}'" in err


@pytest.mark.process("the usage refusal run inside a scratch repository")
def test_issue_with_no_base_returns_2_with_the_usage_and_nothing_on_stdout(tmp_path, refactor_touched, run_cli):
    repo = new_repo(tmp_path / "issue-range")
    commit_all(repo, "plan: scope #11", **{".tdd__issue-11.md": "- [ ] a step\n"})
    code, out, err = run_cli(refactor_touched, ["--issue"], cwd=repo)
    assert (code, out) == (2, "")
    assert "usage: refactor-touched.sh" in err


@pytest.mark.process("refactor-touched.sh run through a symlink to the skill directory from another working directory")
def test_a_shim_run_through_a_symlink_and_from_another_cwd_answers_as_in_place(tmp_path):
    repo = new_repo(tmp_path / "linked")
    commit_all(repo, "plan: scope #13", **{".tdd__issue-13.md": "- [ ] a step\n", "elsewhere__keep": "here\n"})
    code_commit = commit_all(repo, "feat: a step (#13)", **{"src__zeta.sh": "zeta\n", "lib__alpha.test.sh": "alpha\n"})
    ledger_only = commit_all(repo, "chore: tick the ledger (#13)", **{".tdd__issue-13.md": "- [x] a step\n"})
    (tmp_path / "linked-skill").symlink_to(SKILL_DIR, target_is_directory=True)
    in_place = SKILL_DIR / "scripts" / "refactor-touched.sh"
    linked = tmp_path / "linked-skill" / "scripts" / "refactor-touched.sh"

    def run(script, commit, cwd):
        done = subprocess.run([str(script), commit], cwd=cwd, capture_output=True, text=True)
        return done.returncode, done.stdout

    assert run(in_place, code_commit, repo) == (0, "lib/alpha.test.sh,src/zeta.sh\n")
    assert run(linked, code_commit, repo / "elsewhere") == (0, "lib/alpha.test.sh,src/zeta.sh\n")
    assert run(linked, ledger_only, repo / "elsewhere") == (3, "")
