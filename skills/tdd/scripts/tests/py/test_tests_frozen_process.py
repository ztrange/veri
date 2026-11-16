"""Cases for veri/tests_frozen.py that run git in a real repository under tmp_path."""
import importlib
import subprocess
import sys

import pytest

from conftest import receipt_leaver
from repo_builder import new_repo


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


def git(repo, *argv):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True,
                   capture_output=True)


@pytest.mark.process("a real git repository under tmp_path, asked for HEAD and the work tree's content")
def test_check_earlier_pass_marker_differs_after_a_work_tree_edit_and_is_the_same_without_one_2230(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    (tmp_path / "lib.py").write_text("one\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests", "lib.py")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    argv = ["check-earlier", str(ledger), "--step", current]

    def marker():
        code = run_cli(tests_frozen, argv, cwd=tmp_path)[0]
        (path,) = (tmp_path / ".tdd").glob("check-earlier-*.pass")
        return code, path.read_text()

    first = marker()
    again = marker()
    (tmp_path / "lib.py").write_text("two\n")
    edited = marker()
    (tmp_path / "notes.txt").write_text("untracked\n")
    untracked = marker()

    assert [first[0], again[0], edited[0], untracked[0]] == [0, 0, 0, 0]
    assert first[1] == again[1]
    assert len({first[1], edited[1], untracked[1]}) == 3
    assert "step: %s\nhead: " % current in edited[1]


@pytest.mark.process("a real git repository under tmp_path holding a nested repository made by new_repo")
def test_check_earlier_exits_2_naming_the_work_tree_hash_and_writes_no_pass_marker_for_an_untracked_nested_repo_with_no_commits_2230(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "nested").mkdir()
    new_repo(tmp_path / "nested")

    code, out, err = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out, "work-tree hash" in err, list((tmp_path / ".tdd").glob("check-earlier-*.pass"))) == (
        2, "", True, [])


@pytest.mark.process("a real git repository under tmp_path whose .gitignore lists .tdd/")
def test_check_earlier_exits_0_and_writes_a_pass_marker_when_the_repository_gitignores_tdd_2230(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests", ".gitignore")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    code, _, err = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, len(list((tmp_path / ".tdd").glob("check-earlier-*.pass")))) == (0, 1), err


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_for_a_diff_checked_step_rewrites_the_changed_case_so_a_later_check_earlier_names_nothing_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")
    record = tmp_path / run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()
    head = dict(tests_frozen.cut_cases((tmp_path / "tests/test_suite.py").read_text()))["test_pinned_2199"]

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, code, out) == (0, 0, "")
    assert tests_frozen.body_line("tests/test_suite.py", "test_pinned_2199", head) in record.read_text().splitlines()


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_keeps_every_non_body_line_of_the_record_and_rewrites_only_the_body_line_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-m", "step two")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_text().splitlines()
    ledger = repo / ".tdd/ledger.md"

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    new = record.read_text().splitlines()

    assert code == 0
    assert [line for line in new if not line.startswith("body: ")] == [
        line for line in old if not line.startswith("body: ")]
    assert [line for line in new if line.startswith("body: ")] != [
        line for line in old if line.startswith("body: ")]
    assert any(line.startswith("case: ") for line in old)
    assert [line for line in new if line.startswith("body: ")] == [tests_frozen.body_line(
        "tests/test_suite.py", "test_config_2552", dict(tests_frozen.cut_cases(suite.read_text()))["test_config_2552"])]


STEPS = ["step Z adds an early case", "step A adds the cases", "step B adds a later case"]
CASE = "def test_%s():\n    assert %d\n"


def _skip_lines(err, what):
    return sum(1 for l in err.splitlines() if l == "skipped: " + what or l.startswith("skipped: " + what + " ("))


def _ledger(repo, **state):
    """The ledger in its real shapes: open, pending (ticked, ledger.PENDING_MARK appended) and done."""
    marks = {"open": "- [ ] %s", "pending": "- [x] %s ⟂ refactor pending", "done": "- [x] %s"}
    (repo / ".tdd/issue-9.md").write_text("".join(
        marks[state.get(name, "open")] % text + "\n" for name, text in zip("ZAB", STEPS)))


def _commit(repo, message):
    git(repo, "commit", "-q", "-am", message)


def _plan_repo(repo, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "9")
    (repo / ".tdd").mkdir()
    (repo / "test_suite.py").write_text(CASE % ("base", 0))
    _ledger(repo)
    (repo / ".tdd/issue-8.md").write_text("- [x] %s\n" % STEPS[1])
    new_repo(repo)
    git(repo, "add", "test_suite.py", ".tdd/issue-9.md", ".tdd/issue-8.md")
    git(repo, "commit", "-q", "-m", "plan")


def _names(repo, tests_frozen, step):
    record = (repo / tests_frozen.record_path(step)).read_text()
    return sorted(l[6:] for l in record.splitlines() if l.startswith("case: "))


@pytest.mark.process("a real git repository under tmp_path, its history walked after an earlier case's receipt")
def test_rerecord_on_head_walks_the_real_ledger_history_after_an_earlier_case_left_a_receipt_and_first_imported_ledger_3053(
        tmp_path, run_cli, monkeypatch):
    for name in ("ledger", "veri.tests_frozen"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    (tmp_path / "earlier").mkdir()
    with pytest.MonkeyPatch.context() as earlier_case:
        receipt_leaver(earlier_case)(tmp_path / "earlier" / "ledger.md")
        tests_frozen = importlib.import_module("veri.tests_frozen")
    repo, step = tmp_path / "repo", STEPS[1]
    repo.mkdir()
    suite = repo / "test_suite.py"
    _plan_repo(repo, monkeypatch)
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("one", 1))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=repo)
    _commit(repo, "A red")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_committed", 5))
    _commit(repo, "A pin, not ticked yet")

    code, _, err = run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=repo)

    assert (code, _names(repo, tests_frozen, step)) == (0, ["test_one", "test_pin_committed"]), err


BODY = "def test_%s():\n    x = %d\n    assert x\n"


def _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper, shared=None):
    """Three TS cases with inline expects, refactored into `shared` + `helper`; returns (skipped lines, check-earlier code)."""
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n});\n\n" % n
                     for n in names)
    shared = shared or "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in names)
    suite.write_text(inline)
    git(tmp_path, "add", "suite.test.ts")
    run_cli(tests_frozen, ["record", "--step", step, "suite.test.ts"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(shared + helper)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[2]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]
    return [l.split(" (")[0] for l in err.splitlines() if l.startswith("skipped: ")], checked


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_count_the_assertions_of_a_function_following_the_shared_typescript_helper_as_the_helpers_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
              "function unrelated() {\n  expect(x).toBe(9);\n}\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_every_case_and_check_earlier_exits_1_when_the_refactor_deletes_an_assertion_from_the_shared_typescript_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n}\n"

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (len(skipped), checked) == (3, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_only_the_case_whose_helper_call_line_the_refactor_deleted_and_check_earlier_exits_1_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
    shared = "".join("it('%s', () => {\n  const x = 1;\n%s});\n\n" % (n, "  sharedBase();\n" if n != "two" else "")
                     for n in ("one", "two", "three"))

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper, shared)

    assert (skipped, checked) == (["skipped: suite.test.ts two"], 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_let_a_non_arrow_const_before_the_shared_typescript_arrow_helper_swallow_it_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("const y = 2;\n"
              "const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_count_the_assertions_of_a_non_arrow_const_following_the_shared_typescript_helper_as_the_helpers_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"
              "const unrelated = 3;\nexpect(x).toBe(9);\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_take_a_non_arrow_const_the_cases_call_for_a_typescript_helper_definition_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
              "const other = wrap(() => {\n  expect(x).toBe(9);\n});\n")
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n  other();\n});\n\n" % n
                     for n in ("one", "two", "three"))

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper, shared)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
@pytest.mark.parametrize("opener", ["const sharedBase = async () => {", "const sharedBase = x => {"])
def test_rerecord_refactored_takes_an_async_or_single_parameter_typescript_arrow_const_for_the_shared_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, opener):
    helper = opener + "\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
@pytest.mark.parametrize("word", ["constants", "functional"])
def test_rerecord_refactored_does_not_end_the_shared_typescript_helper_at_a_column_0_line_merely_starting_with_a_keyword_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, word):
    helper = ("const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n%s\n  expect(x).toBe(3);\n};\n" % word)

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_take_a_typescript_arrow_const_the_cases_do_not_call_for_their_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
              "const other = () => {\n  expect(x).toBe(9);\n};\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_python_case_whose_refactor_moved_assertions_into_a_module_level_helper_before_a_second_case_2931(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "test_sample.py"
    _plan_repo(tmp_path, monkeypatch)
    test_b = 'def test_b():\n    y = 2\n    assert y == 2\n    assert y != 3\n'
    inline = ('def test_a():\n    x = 1\n    assert x == 1\n    assert x != 2\n\n\n' + test_b)
    extracted = ('def assert_refused(x):\n    assert x == 1\n    assert x != 2\n\n\n'
                 'def test_a():\n    x = 1\n    assert_refused(x)\n\n\n' + test_b)
    suite.write_text(inline)
    git(tmp_path, "add", "test_sample.py")
    run_cli(tests_frozen, ["record", "--step", step, "test_sample.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, "skipped:" in err, checked) == (0, False, (0, ""))
