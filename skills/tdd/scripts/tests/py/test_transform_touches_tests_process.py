"""Process cases for veri/transform_touches_tests.py: the ones that start a real process; the small cases are in unit/test_transform_touches_tests.py."""
import importlib
import subprocess
from pathlib import Path

import pytest

from repo_builder import commit_all, new_repo

USAGE = "usage: transform-touches-tests.sh <base-sha> [<bound>] [--touched <list>]\n"


SKILL_DIR = Path(__file__).resolve().parents[3]


def git(repo, *args):
    done = subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test",
                           *args], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


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


@pytest.mark.process("git rev-parse and git log over a scratch repository per Go, JS spec and Python test path")
def test_2893_a_range_changing_a_go_js_spec_or_python_test_file_exits_1_naming_it_and_a_production_file_exits_0(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "paths")
    commit_all(repo, "base", README="x\n")
    for path in ("pkg/x_test.go", "src/foo.spec.ts", "src/test_foo.py", "pkg/foo_test.py"):
        base = git(repo, "rev-parse", "HEAD")
        commit_all(repo, f"edit {path}", **{path.replace("/", "__"): "changed\n"})
        assert run_cli(transform_touches_tests, [base], cwd=repo) == (
            1, f"transform changed a test file: {path}\n", ""), path
    base = git(repo, "rev-parse", "HEAD")
    commit_all(repo, "edit production", pkg__x_go="package pkg\n")
    assert run_cli(transform_touches_tests, [base], cwd=repo) == (0, "", "")


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range changes only a file outside --touched")
def test_3237_touched_option_exits_1_when_the_range_changed_only_a_file_outside_the_list_but_inside_the_bound(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "touched")
    base = commit_all(repo, "feat: seed", **{"src__a.sh": "a\n", "src__b.sh": "b\n"})
    commit_all(repo, "refactor: b only", **{"src__b.sh": "b2\n"})

    assert run_cli(transform_touches_tests, [base, "src/a.sh,src/b.sh", "--touched", "src/a.sh"], cwd=repo) == (
        1, "transform changed no file the issue touched\n", "")


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range changes a file in --touched")
def test_3237_touched_option_exits_0_when_the_range_changed_a_file_in_the_list_inside_the_bound(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "touched-ok")
    base = commit_all(repo, "feat: seed", **{"src__a.sh": "a\n", "src__b.sh": "b\n"})
    commit_all(repo, "refactor: a and b", **{"src__a.sh": "a2\n", "src__b.sh": "b2\n"})

    assert run_cli(transform_touches_tests, [base, "src/a.sh,src/b.sh", "--touched", "src/a.sh"], cwd=repo) == (
        0, "", "")


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range changes a file in --touched, with no bound")
def test_3280_touched_option_with_no_bound_is_the_flag_and_exits_0_when_the_range_changed_a_listed_file(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "touched-unbound")
    base = commit_all(repo, "feat: seed", **{"src__a.py": "a\n"})
    commit_all(repo, "refactor: a", **{"src__a.py": "a2\n"})

    assert run_cli(transform_touches_tests, [base, "--touched", "src/a.py"], cwd=repo) == (0, "", "")


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range changes only a file outside --touched, with no bound")
def test_3280_touched_option_with_no_bound_exits_1_when_the_range_changed_no_listed_file(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "touched-unbound-miss")
    base = commit_all(repo, "feat: seed", **{"src__a.py": "a\n", "src__b.py": "b\n"})
    commit_all(repo, "refactor: b only", **{"src__b.py": "b2\n"})

    assert run_cli(transform_touches_tests, [base, "--touched", "src/a.py"], cwd=repo) == (
        1, "transform changed no file the issue touched\n", "")


@pytest.mark.process("git rev-parse and git log over a scratch repository, with --touched as the last argument and no value")
def test_3280_touched_option_with_no_value_exits_2_with_the_usage_line_and_no_traceback(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "touched-novalue")
    base = commit_all(repo, "feat: seed", **{"src__a.py": "a\n"})
    commit_all(repo, "refactor: a", **{"src__a.py": "a2\n"})

    assert run_cli(transform_touches_tests, [base, "", "--touched"], cwd=repo) == (
        2, "", "usage: transform-touches-tests.sh <base-sha> [<bound>] [--touched <list>]\n")


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range changed a non-test file, with an empty --touched list")
def test_3280_touched_option_with_an_empty_list_exits_2_naming_the_empty_list(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "touched-empty")
    base = commit_all(repo, "feat: seed", **{"src__a.py": "a\n"})
    commit_all(repo, "refactor: a", **{"src__a.py": "a2\n"})

    code, out, err = run_cli(transform_touches_tests, [base, "", "--touched", ""], cwd=repo)

    assert (code, out) == (2, "")
    assert "empty" in err


@pytest.mark.process("git rev-parse and git log over a scratch repository whose range changed a non-test file, with a --touched list ending in a comma")
def test_3280_touched_option_with_a_trailing_comma_in_the_list_exits_2_like_the_empty_list(
        tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "touched-trailing-comma")
    base = commit_all(repo, "feat: seed", **{"src__a.py": "a\n"})
    commit_all(repo, "refactor: a", **{"src__a.py": "a2\n"})

    code, out, err = run_cli(transform_touches_tests, [base, "", "--touched", "nonexistent.py,"], cwd=repo)

    assert (code, out) == (2, "")


@pytest.mark.process("git rev-parse and git log over a scratch veri tree whose range changes only the pytest leg")
def test_a_range_changing_only_the_pytest_leg_in_veris_own_tree_exits_0_4262(tmp_path, transform_touches_tests, run_cli):
    repo = new_repo(tmp_path / "veri-tree")
    leg = "skills/tdd/scripts/tests/leg/pytest_leg.py"
    commit_all(repo, "feat: leg", **{leg.replace("/", "__"): "one\n",
                                     "skills__tdd__scripts__tests__py__test_x.py": "def test_x(): pass\n"})
    base = git(repo, "rev-parse", "HEAD")
    commit_all(repo, "refactor: touch the leg", **{leg.replace("/", "__"): "two\n"})

    assert run_cli(transform_touches_tests, [base], cwd=repo) == (0, "", "")
