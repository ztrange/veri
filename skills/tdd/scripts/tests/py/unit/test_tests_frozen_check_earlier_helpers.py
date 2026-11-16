"""In-process check-earlier cases on a case's helpers: lines between cases, the helpers a case calls and their assertion
lines, on a history committed through fed_commits (PRD 017.7)."""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# Names, not literals, in calls: a literal suite path reads as a nested run.
SUITE = "tests/test_suite.py"
OLDER = "def test_older_case():\n    assert True\n"


@pytest.fixture
def based(tmp_path, fed_commits):
    """tmp_path holding tests/ and .tdd/, the suite holding OLDER committed as "base"; returns the fed_commits log."""
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / SUITE).write_text(OLDER)
    repo = fed_commits()
    repo.add("tests")
    repo.commit("base")
    return repo


def test_check_earlier_exits_0_printing_nothing_when_a_module_level_helper_is_inserted_between_two_recorded_cases_2177(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds two cases", "step two adds another"
    (tmp_path / SUITE).write_text(
        "def test_first_2177():\n    assert 1 == 2\n\n\ndef test_second_2177():\n    assert 3 == 4\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(
        "def test_first_2177():\n    assert 1 == 2\n\n\n# shared between the cases\nLIMIT = 3\n\n\n"
        "def _helper():\n    return LIMIT\n\n\ndef test_second_2177():\n    assert 3 == 4\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


# The plan repository of the rerecord-refactored cases: ledger .tdd/issue-9.md (VERI_ISSUE=9) over STEPS.
STEPS = ["step Z adds an early case", "step A adds the cases", "step B adds a later case"]
CASE = "def test_%s():\n    assert %d\n"
ROOT_SUITE = "test_suite.py"
GO_SUITE = "suite_test.go"
PLAN_LEDGER = ".tdd/issue-9.md"


def _ledger(root, **state):
    """The ledger in its real shapes: open, pending (ticked, ledger.PENDING_MARK appended) and done."""
    marks = {"open": "- [ ] %s", "pending": "- [x] %s ⟂ refactor pending", "done": "- [x] %s"}
    (root / PLAN_LEDGER).write_text("".join(
        marks[state.get(name, "open")] % text + "\n" for name, text in zip("ZAB", STEPS)))


def _plan_repo(root, monkeypatch, fed_commits):
    """root holding test_suite.py and the ledgers of issues 9 and 8, committed as "plan"; returns the fed_commits log."""
    monkeypatch.setenv("VERI_ISSUE", "9")
    (root / ".tdd").mkdir()
    (root / ROOT_SUITE).write_text(CASE % ("base", 0))
    _ledger(root)
    (root / ".tdd/issue-8.md").write_text("- [x] %s\n" % STEPS[1])
    repo = fed_commits(root=root)
    repo.add(ROOT_SUITE, PLAN_LEDGER, ".tdd/issue-8.md")
    repo.commit("plan")
    return repo


def _refactored(root, run_cli, tests_frozen, repo, path, recorded, refactored, message="A refactor"):
    """Step A records `recorded` in `path` (red, green), a verified refactor then rewrites it to `refactored`, and
    rerecord-refactored runs over it from green."""
    (root / path).write_text(recorded)
    repo.add(path)
    run_cli(tests_frozen, ["record", "--step", STEPS[1], path], cwd=root)
    repo.commit("A red", all=True)
    _ledger(root, A="done")
    repo.commit("A green", all=True)
    green = repo.head
    (root / path).write_text(refactored)
    repo.commit(message, all=True)
    (root / ".tdd/verdict-refactor.exit").write_text("0")
    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=root)


def test_check_earlier_exits_1_for_a_go_case_whose_unchanged_named_asserting_helper_gained_an_assertion_in_the_same_refactor_3077(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    build_green = 'func build(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatalf("build failed")\n\t}\n}\n'
    build_head = 'func build(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatalf("build failed")\n\t}\n\tif 2 != 2 {\n\t\tt.Fatalf("build twice")\n\t}\n}\n'
    inline = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
              '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build_green)
    extracted = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
                 '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build_head)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, extracted)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked[0] == 1


def test_check_earlier_exits_0_for_a_go_case_whose_unchanged_asserting_helper_holds_a_duplicated_assertion_line_3077(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    build_green = 'func build(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatalf("build failed")\n\t}\n\tif 1 != 1 {\n\t\tt.Fatalf("build failed")\n\t}\n}\n'
    build_head = 'func build(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatalf("build failed")\n\t}\n\tif 1 != 1 {\n\t\tt.Fatalf("build failed")\n\t}\n}\n'
    inline = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
              '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build_green)
    extracted = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
                 '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build_head)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, extracted)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked[0] == 0


GO_INLINE = 'func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n'
GO_EXTRACTED = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n')


def test_check_earlier_exits_0_for_a_go_case_after_a_helper_is_appended_at_eof_following_the_rerecord_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, GO_INLINE, GO_EXTRACTED)
    suite.write_text(GO_EXTRACTED + '\nfunc later(t *testing.T) {\n\tt.Fatal("z")\n}\n')
    repo.commit("later helper", all=True)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_check_earlier_exits_1_for_a_go_case_after_an_assertion_is_deleted_from_it_with_a_trailing_helper_following_the_rerecord_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, GO_INLINE, GO_EXTRACTED)
    healed = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]
    suite.write_text(GO_EXTRACTED.replace('\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n', ''))
    repo.commit("assertion deleted from the case", all=True)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (healed, checked) == (0, 1)


GO_X = "func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n"
GO_CHECK_X = "func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
GO_CALLS_CHECK_X = "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n"


def test_check_earlier_exits_1_for_a_go_case_after_a_t_fatal_line_is_deleted_from_its_helper_above_it_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE,
                "func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n",
                "func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n\n" + GO_CALLS_CHECK_X,
                "A refactor moves the checks into a helper")
    suite.write_text(GO_CHECK_X + GO_CALLS_CHECK_X)
    repo.commit("later commit drops a check from the helper", all=True)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


def test_check_earlier_exits_1_for_a_python_case_after_an_assert_line_is_deleted_from_its_helper_above_it_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, ROOT_SUITE,
                "def test_one():\n    x = 1\n    assert x == 1\n    assert x < 2\n",
                "def check_one(x):\n    assert x == 1\n    assert x < 2\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n",
                "A refactor moves the asserts into a helper")
    suite.write_text("def check_one(x):\n    assert x == 1\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n")
    repo.commit("later commit drops an assert from the helper", all=True)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "test_one (%s)\n" % step)


def test_check_earlier_exits_0_for_a_go_case_after_a_helper_it_does_not_call_is_added_above_it_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, GO_X, GO_CHECK_X + GO_CALLS_CHECK_X,
                "A refactor moves the check into a helper")
    suite.write_text("func otherX(t *testing.T) {\n\tt.Fatal(\"unrelated\")\n}\n\n" + GO_CHECK_X + GO_CALLS_CHECK_X)
    repo.commit("later commit adds a helper the case does not call", all=True)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_check_earlier_exits_0_for_a_go_case_after_an_assertion_line_is_deleted_from_a_helper_it_does_not_call_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    other = "func otherX(t *testing.T) {\n\tt.Fatal(\"first\")\n\tt.Fatal(\"second\")\n}\n\n"
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, other + GO_X, other + GO_CHECK_X + GO_CALLS_CHECK_X,
                "A refactor moves the check into a helper")
    suite.write_text(suite.read_text().replace("\tt.Fatal(\"second\")\n", ""))
    repo.commit("later commit deletes an assertion line from a helper the case does not call", all=True)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_check_earlier_exits_0_for_a_go_case_after_a_helper_it_calls_changes_keeping_every_assertion_line_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, GO_X, GO_CHECK_X + GO_CALLS_CHECK_X,
                "A refactor moves the check into a helper")
    suite.write_text("func checkX(t *testing.T, x int) {\n\tt.Log(\"checking\")\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     + GO_CALLS_CHECK_X)
    repo.commit("later commit changes the helper but keeps its assertion line", all=True)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")
