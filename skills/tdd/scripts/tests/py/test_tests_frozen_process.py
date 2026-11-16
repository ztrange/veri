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


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_an_earlier_steps_case_whose_body_the_refactor_moved_into_a_shared_helper_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    helper = "def _value(n):\n    return n\n\n\n"
    suite.write_text(helper + suite.read_text().replace("x = 1\n", "x = _value(1)\n"))
    _commit(tmp_path, "B refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C"], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_a_check_into_a_helper_after_the_last_case_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n'
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_a_check_into_a_helper_between_two_cases_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    two = 'func TestTwo(t *testing.T) {\n\tif 2 != 2 {\n\t\tt.Fatal("c")\n\t}\n}\n'
    inline = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n'
              + two)
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n\n' + two)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_checks_into_a_new_helper_while_it_also_calls_an_asserting_helper_green_had_3077(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    build = 'func build(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatalf("build failed")\n\t}\n}\n'
    inline = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
              '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build)
    extracted = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
                 '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    rerecorded = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (rerecorded, checked) == ((0, "", ""), (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_two_go_cases_whose_refactor_moved_the_same_checks_verbatim_into_one_new_shared_helper_3332(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    checks = '\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n'
    inline = ''.join('func %s(t *testing.T) {\n\tx := 1\n%s}\n\n' % (n, checks) for n in ("TestOne", "TestTwo"))
    extracted = (''.join('func %s(t *testing.T) {\n\tx := 1\n\tcheckShort(t, x)\n}\n\n' % n for n in ("TestOne", "TestTwo"))
                 + 'func checkShort(t *testing.T, x int) {\n%s}\n' % checks)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    rerecorded = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (rerecorded, checked) == ((0, "", ""), (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_two_go_cases_whose_refactor_moved_the_checks_into_one_new_shared_helper_but_changed_one_3332(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    checks = '\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n'
    changed = checks.replace('t.Fatal("b")', 't.Fatal("c")')
    inline = ''.join('func %s(t *testing.T) {\n\tx := 1\n%s}\n\n' % (n, checks) for n in ("TestOne", "TestTwo"))
    extracted = (''.join('func %s(t *testing.T) {\n\tx := 1\n\tcheckShort(t, x)\n}\n\n' % n for n in ("TestOne", "TestTwo"))
                 + 'func checkShort(t *testing.T, x int) {\n%s}\n' % changed)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    recorded = (tmp_path / ".tdd/issue-9.md").read_text()

    _, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (_skip_lines(err, "suite_test.go TestOne"), _skip_lines(err, "suite_test.go TestTwo"),
            (tmp_path / ".tdd/issue-9.md").read_text() == recorded) == (1, 1, True), err


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_the_record_and_check_earlier_exits_1_for_a_go_case_whose_refactor_moved_checks_into_a_helper_after_it_and_dropped_one_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + chk("c") + '}\n'
    dropped = ('func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '\tcheck(t, x)\n}\n\n'
               'func check(t *testing.T, x int) {\n' + chk("a") + '}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(dropped)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, checked) == (1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_whose_t_fatal_lines_a_refactor_moved_into_a_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_python_case_whose_assert_line_a_refactor_moved_into_a_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("def test_one():\n    x = 1\n    assert x == 1\n")
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("def check_one(x):\n    assert x == 1\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n")
    _commit(tmp_path, "A refactor moves the assert into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_a_later_commit_deleted_a_t_fatal_line_from_the_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n\nfunc TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the checks into a helper")
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor drops a check from the helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_deleted_one_of_two_identical_t_fatal_lines_while_moving_the_other_into_a_helper_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"bad\")\n\tt.Error(\"mid\")\n\tt.Fatal(\"bad\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T) {\n\tt.Fatal(\"bad\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t)\n\tt.Error(\"mid\")\n}\n")
    _commit(tmp_path, "A refactor moves one check into a helper and drops the other")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_whose_setup_t_fatal_lines_a_refactor_moved_into_a_helper_ahead_of_later_assertions_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"setup\")\n\tt.Error(\"later\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func setupX(t *testing.T) {\n\tt.Fatal(\"setup\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tsetupX(t)\n\tt.Error(\"later\")\n}\n")
    _commit(tmp_path, "A refactor extracts the setup check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_whose_helper_lines_sort_before_its_own_remaining_assertion_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tt.Fatal(\"a setup\")\n\tt.Fatal(\"z later\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func setupX(t *testing.T) {\n\tt.Fatal(\"a setup\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tsetupX(t)\n\tt.Fatal(\"z later\")\n}\n")
    _commit(tmp_path, "A refactor extracts the setup check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_run_again_with_the_same_green_sha_heals_an_order_changing_helper_extractions_stale_record_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"setup\")\n\tt.Error(\"later\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func setupX(t *testing.T) {\n\tt.Fatal(\"setup\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tsetupX(t)\n\tt.Error(\"later\")\n}\n")
    _commit(tmp_path, "A refactor extracts the setup check into a helper")
    ledger = ".tdd/issue-9.md"
    verdict = tmp_path / ".tdd/verdict-refactor.exit"
    verdict.write_text("1")
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    verdict.write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_a_go_case_at_heads_body_whose_refactor_lost_a_helper_assertion_line_2973(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x < 0 {\n\t\tt.Error(\"negative\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("\tif x < 0 {\n\t\tt.Error(\"negative\")\n\t}\n", ""))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (tests_frozen.body_line("suite_test.go", "TestX", head_body).encode() + b"\n" in before,
            b"\nhelpers: " in before, code, _skip_lines(err, "suite_test.go TestX"),
            record.read_bytes() == before) == (True, True, 1, 1, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_refreshes_the_helpers_line_of_a_go_case_already_recorded_at_heads_body_so_check_earlier_exits_0_2973(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    green_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    suite.write_text(suite.read_text().replace("x := 1", "x := 1 // one").replace('"bad"', '"bad value"'))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    record.write_text(record.read_text().replace(
        tests_frozen.body_line("suite_test.go", "TestX", green_body),
        tests_frozen.body_line("suite_test.go", "TestX", head_body)))
    held = tests_frozen._helper_digest(suite.read_text(), head_body)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "suite_test.go TestX") > 0,
            "helpers: suite_test.go\tTestX\t%s\n" % held in record.read_text(), checked) == (
        0, False, True, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_at_heads_body_whose_helpers_digest_is_neither_greens_nor_heads_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    green_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    older = "helpers: suite_test.go\tTestX\t%s\n" % ("6" * 64)
    record.write_text("".join(
        tests_frozen.body_line("suite_test.go", "TestX", head_body) + "\n"
        if line.startswith("body: ") else older if line.startswith("helpers: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    held = tests_frozen._helper_digest(suite.read_text(), head_body)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "suite_test.go TestX") > 0,
            "helpers: suite_test.go\tTestX\t%s\n" % held in record.read_text(), checked) == (
        0, False, True, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_a_go_case_at_heads_body_whose_helpers_digest_is_neither_greens_nor_heads_when_the_refactor_lost_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    kept = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n\n"
                     "func TestY(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireTwo(t *testing.T, x int) {\n" + kept + "}\n\n"
                     "func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireTwo(t, x)\n}\n\n"
                     "func TestY(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into helpers; TestX's loses one")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    heads = {case: tests_frozen._bodies_of(suite.read_text(), case)[0] for case in ("TestX", "TestY")}
    record.write_text("".join(
        "%s\nhelpers: suite_test.go\t%s\t%s\n" % (tests_frozen.body_line(
            "suite_test.go", line.split("\t")[1], heads[line.split("\t")[1]]), line.split("\t")[1], "6" * 64)
        if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    x_lines = [line for line in record.read_text().splitlines() if "\tTestX\t" in line]
    held = "helpers: suite_test.go\tTestY\t%s" % tests_frozen._helper_digest(suite.read_text(), heads["TestY"])

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    after = record.read_text().splitlines()

    assert (code, _skip_lines(err, "suite_test.go TestX"),
            _skip_lines(err, "suite_test.go TestY"),
            [line for line in after if "\tTestX\t" in line] == x_lines, held in after) == (
        1, 1, 0, True, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_a_go_case_at_heads_body_whose_helpers_digest_is_neither_greens_nor_heads_when_the_refactor_added_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    kept = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + kept + "}\n\n"
                     "func TestY(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n\n"
                     "func TestY(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper; TestX's gains one")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    heads = {case: tests_frozen._bodies_of(suite.read_text(), case)[0] for case in ("TestX", "TestY")}
    record.write_text("".join(
        "%s\nhelpers: suite_test.go\t%s\t%s\n" % (tests_frozen.body_line(
            "suite_test.go", line.split("\t")[1], heads[line.split("\t")[1]]), line.split("\t")[1], "6" * 64)
        if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    x_lines = [line for line in record.read_text().splitlines() if "\tTestX\t" in line]
    held = "helpers: suite_test.go\tTestY\t%s" % tests_frozen._helper_digest(suite.read_text(), heads["TestY"])

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    after = record.read_text().splitlines()

    assert (code, _skip_lines(err, "suite_test.go TestX"),
            _skip_lines(err, "suite_test.go TestY"),
            [line for line in after if "\tTestX\t" in line] == x_lines, held in after) == (
        1, 1, 0, True, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_a_go_case_whose_body_digest_is_neither_greens_nor_heads_while_its_helpers_digest_is_greens_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    record.write_text("".join(
        "body: suite_test.go\tTestX\t%s\n" % ("f" * 64) if line.startswith("body: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x := 1", "x := 1 // one"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (b"\nhelpers: " in before, code, _skip_lines(err, "suite_test.go TestX"),
            record.read_bytes() == before) == (True, 1, 1, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_the_helpers_digest_guard_in_parentheses_on_the_skipped_line_of_a_record_at_greens_body_whose_helpers_digest_differs_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % ("0" * 64))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text() + "\n// tidied\n")
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        1, 1, [True])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_the_assertion_lines_guard_in_parentheses_on_the_skipped_line_of_a_head_body_record_whose_case_and_helpers_lost_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    kept = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireTwo(t *testing.T, x int) {\n" + kept + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireTwo(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper and loses one")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    record.write_text("".join(
        "%s\nhelpers: suite_test.go\tTestX\t%s\n" % (tests_frozen.body_line("suite_test.go", "TestX", head), "6" * 64)
        if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        1, 1, [True])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_the_helper_assertion_count_guard_in_parentheses_on_the_skipped_line_of_a_record_whose_case_body_is_unchanged_but_whose_helper_gained_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    one = "\tif x != 1 {\n\t\tt.Fatal(\"bad 1\")\n\t}\n"
    two = one + "\tif x != 2 {\n\t\tt.Fatal(\"bad 2\")\n\t}\n"
    case = "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n" + one + "}\n\n" + case)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n" + two + "}\n\n" + case)
    _commit(tmp_path, "A refactor adds an assertion to the helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        0, 1, [True])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_one_helpers_line_from_head_for_a_go_case_whose_record_held_two_stale_ones_so_check_earlier_exits_0_2998(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    stale = "".join("helpers: suite_test.go\tTestX\t%s\n" % (digit * 64) for digit in "67")
    record.write_text("".join(
        line for line in record.read_text().splitlines(keepends=True) if not line.startswith("body: ")
    ).replace("case: TestX\n", "case: TestX\n" + tests_frozen.body_line("suite_test.go", "TestX", head_body)
              + "\n" + stale))
    held = tests_frozen._helper_digest(suite.read_text(), head_body)

    run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert ([l for l in record.read_text().splitlines() if l.startswith("helpers: ")], checked) == (
        ["helpers: suite_test.go\tTestX\t%s" % held], (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_record_with_two_helpers_lines_byte_identical_for_a_case_it_skips_2998(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func TestX(t *testing.T) {\n\tx := 2\n}\n")
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    stale = "".join("helpers: suite_test.go\tTestX\t%s\n" % (digit * 64) for digit in "67")
    record.write_text("".join(
        line + stale if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (code, "skipped: suite_test.go TestX" in err, record.read_bytes()) == (1, True, before)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_keeps_a_helpers_line_of_a_later_case_that_does_not_follow_a_rewritten_body_2998(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    later = "case: TestY\nhelpers: suite_test.go\tTestY\t%s\n" % ("8" * 64)
    record.write_text(record.read_text() + later)

    run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert record.read_text().endswith(later)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_go_cases_sharing_a_helper_the_refactor_introduced_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    checks = "".join('\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m for m in "abc")
    inline = "".join('func Test%s(t *testing.T) {\n\tx := 1\n%s}\n\n' % (n, checks)
                     for n in ("One", "Two", "Three"))
    shared = "".join('func Test%s(t *testing.T) {\n\tx := 1\n\tsharedBase(t, x)\n}\n\n' % n for n in ("One", "Two", "Three"))
    helper = ('func sharedBase(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n'
              '\tif x != 1 {\n\t\tt.Fatal("c")\n\t}\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(shared + helper)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, err, checked) == (0, "", (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_typescript_cases_sharing_a_function_helper_the_refactor_introduced_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n});\n\n" % n
                     for n in names)
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in names)
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
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

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, err, checked) == (0, "", (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_typescript_cases_sharing_a_function_helper_named_test_helper_the_refactor_introduced_2931(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n});\n\n" % n
                     for n in names)
    shared = "".join("it('%s', () => {\n  const x = 1;\n  testHelper();\n});\n\n" % n for n in names)
    helper = "function testHelper() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
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

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, err, checked) == (0, "", (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_typescript_cases_sharing_an_arrow_function_helper_the_refactor_introduced_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n});\n\n" % n
                     for n in names)
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in names)
    helper = "const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"
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

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, err, checked) == (0, "", (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_1_naming_the_cases_when_the_refactor_adds_an_assertion_line_to_the_shared_typescript_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(%d);\n});\n\n" % (n, i)
                     for i, n in enumerate(names, 1))
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in names)
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n  expect(x).toBe(4);\n}\n"
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

    skipped = [line for line in err.splitlines() if line.startswith("skipped: suite.test.ts ")]
    assert (bool(skipped), checked) == (True, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_only_the_go_case_whose_own_lines_the_shared_helper_exceeds_and_check_earlier_exits_1_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)

    def check(m):
        return '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m

    inline = ("func TestX(t *testing.T) {\n\tx := 1\n" + check("a") + check("b") + "}\n\n"
              "func TestY(t *testing.T) {\n\tx := 1\n" + check("a") + check("b") + check("c") + "}\n\n")
    shared = "".join("func Test%s(t *testing.T) {\n\tx := 1\n\tsharedBase(t, x)\n}\n\n" % n for n in ("X", "Y"))
    helper = "func sharedBase(t *testing.T, x int) {\n" + check("a") + check("b") + check("c") + "}\n"
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
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

    skipped = [l.split(" (")[0] for l in err.splitlines() if l.startswith("skipped: ")]
    assert (skipped, checked) == (["skipped: suite_test.go TestX"], 1)


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
@pytest.mark.parametrize("opener", ["let sharedBase = () => {", "return sharedBase = () => {"])
def test_rerecord_refactored_does_not_take_a_let_or_return_line_for_a_typescript_helper_definition_and_check_earlier_exits_1_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, opener):
    helper = opener + "\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (len(skipped), checked) == (3, 1)


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
