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


def _refactored(root, run_cli, tests_frozen, repo, path, recorded, refactored, message="A refactor", moved=None):
    """Step A records `recorded` in `path` (red, green), a verified refactor then rewrites it to `refactored` and writes
    each `moved` file (path: text, a new sibling), and rerecord-refactored runs over it from green."""
    (root / path).write_text(recorded)
    repo.add(path)
    run_cli(tests_frozen, ["record", "--step", STEPS[1], path], cwd=root)
    repo.commit("A red", all=True)
    _ledger(root, A="done")
    repo.commit("A green", all=True)
    green = repo.head
    (root / path).write_text(refactored)
    for sibling, text in (moved or {}).items():
        (root / sibling).write_text(text)
        repo.add(sibling)
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


def _green(root, run_cli, tests_frozen, repo, path, recorded):
    """Step A records `recorded` in `path` (red, green); returns the green revision."""
    (root / path).write_text(recorded)
    repo.add(path)
    run_cli(tests_frozen, ["record", "--step", STEPS[1], path], cwd=root)
    repo.commit("A red", all=True)
    _ledger(root, A="done")
    repo.commit("A green", all=True)
    return repo.head


def test_check_earlier_passes_a_record_written_without_helper_data_when_nothing_changed_and_exits_1_when_the_case_body_changes_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    source = GO_CHECK_X + GO_CALLS_CHECK_X
    _green(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, source)
    unchanged = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    suite.write_text(source.replace("x := 1\n\tcheckX", "x := 2\n\tcheckX"))
    repo.commit("later commit changes the case body", all=True)
    changed = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)

    assert unchanged == (0, "")
    assert changed[0] == 1
    assert "TestX" in changed[1]


def test_check_earlier_exits_1_naming_the_case_when_its_body_changes_after_a_record_without_helper_data_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    source = "func TestX(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n"
    _green(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, source)

    suite.write_text(source.replace("1 != 1", "1 != 2"))
    repo.commit("later commit changes the case body", all=True)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)

    assert checked[0] == 1
    assert "TestX" in checked[1]


def test_check_earlier_exits_1_for_a_go_case_after_a_later_rerecord_refactored_over_a_t_fatal_line_deleted_from_its_helper_2867(
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
    later_green = repo.commit("later commit drops a check from the helper", all=True)
    suite.write_text(suite.read_text().replace("func checkX(t *testing.T, x int) {\n", "func checkX(t *testing.T, x int) {\n\tt.Log(\"checking\")\n"))
    repo.commit("a second refactor touches only the helper", all=True)

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, later_green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


def test_check_earlier_exits_0_for_a_go_case_after_two_rerecord_refactored_each_following_a_verified_refactor_that_changes_its_helpers_assertion_lines_2888(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, GO_X, GO_CHECK_X + GO_CALLS_CHECK_X,
                "A first refactor moves the check into a helper")
    green = repo.head
    suite.write_text(suite.read_text().replace('t.Fatal("bad")', 't.Fatal("bad value")'))
    repo.commit("A second refactor rewords the helper's assertion", all=True)
    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    green = repo.head
    suite.write_text(suite.read_text().replace('t.Fatal("bad value")', 't.Fatal("bad x")'))
    repo.commit("A third refactor rewords the helper's assertion again", all=True)
    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    held = [l for l in record.read_text().splitlines() if l.startswith("helpers:")]

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (len(held), checked) == (1, (0, ""))


PY_INLINE = "def test_one():\n    x = 1\n    assert x == 1\n    assert x < 2\n"
PY_EXTRACTED = "def check_one(x):\n    assert x == 1\n    assert x < 2\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n"


def test_check_earlier_exits_1_for_a_python_case_after_a_later_rerecord_refactored_over_an_assert_line_a_non_refactor_commit_deleted_from_its_helper_2888(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, ROOT_SUITE, PY_INLINE, PY_EXTRACTED,
                "A refactor moves the asserts into a helper")
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    rerecorded = [l for l in record.read_text().splitlines() if l.startswith("helpers:")]
    suite.write_text("def check_one(x):\n    assert x == 1\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n")
    later_green = repo.commit("later commit drops an assert from the helper", all=True)
    suite.write_text(suite.read_text().replace("    assert x == 1\n", "    y = x\n    assert x == 1\n"))
    repo.commit("a second refactor touches only the helper", all=True)

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, later_green], cwd=tmp_path)
    held = [l for l in record.read_text().splitlines() if l.startswith("helpers:")]
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (held, checked) == (rerecorded, (1, "test_one (%s)\n" % step))


def test_check_earlier_exits_0_for_a_python_case_after_the_assert_lines_of_its_helper_are_reordered_following_the_rerecord_2888(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, ROOT_SUITE, PY_INLINE, PY_EXTRACTED,
                "A refactor moves the asserts into a helper")
    suite.write_text("def check_one(x):\n    assert x < 2\n    assert x == 1\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n")
    repo.commit("later commit reorders the helper's asserts", all=True)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_check_earlier_exits_1_for_a_python_case_after_an_assert_line_is_deleted_from_its_helper_whose_remaining_asserts_are_also_reordered_2888(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, ROOT_SUITE,
                "def test_one():\n    x = 1\n    assert x == 1\n    assert x < 2\n    assert x > 0\n",
                "def check_one(x):\n    assert x == 1\n    assert x < 2\n    assert x > 0\n\n\n"
                "def test_one():\n    x = 1\n    check_one(x)\n",
                "A refactor moves the asserts into a helper")
    suite.write_text("def check_one(x):\n    assert x > 0\n    assert x == 1\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n")
    repo.commit("later commit deletes one helper assert and reorders the rest", all=True)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "test_one (%s)\n" % step)


def test_check_earlier_exits_0_for_two_same_named_python_methods_calling_different_asserting_helpers_following_the_rerecord_2888(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, ROOT_SUITE,
                "class TestA:\n    def test_one(self):\n        x = 1\n        assert x == 1\n\n\n"
                "class TestB:\n    def test_one(self):\n        x = 2\n        assert x == 2\n",
                "def check_a(x):\n    assert x == 1\n\n\ndef check_b(x):\n    assert x == 2\n\n\n"
                "class TestA:\n    def test_one(self):\n        x = 1\n        check_a(x)\n\n\n"
                "class TestB:\n    def test_one(self):\n        x = 2\n        check_b(x)\n",
                "A refactor moves the asserts into helpers")

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


SAMPLE = "test_sample.py"
SAMPLE_B = 'def test_b():\n    y = 2\n    assert y == 2\n    assert y != 3\n'
SAMPLE_INLINE = 'def test_a():\n    x = 1\n    assert x == 1\n    assert x != 2\n\n\n' + SAMPLE_B
SAMPLE_EXTRACTED = ('def assert_refused(x):\n    assert x == 1\n    assert x != 2\n\n\n'
                    'def test_a():\n    x = 1\n    assert_refused(x)\n\n\n' + SAMPLE_B)


def test_check_earlier_exits_0_for_a_python_case_whose_module_level_helper_precedes_a_second_case_whose_assertion_is_then_edited_2931(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / SAMPLE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, SAMPLE, SAMPLE_INLINE, SAMPLE_EXTRACTED)
    suite.write_text(SAMPLE_EXTRACTED.replace("assert y != 3", "assert y != 4"))
    repo.commit("B edit", all=True)

    code, out, err = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)

    assert (code, "test_b" in out + err, "test_a" in out + err) == (1, True, False), out + err


def test_check_earlier_exits_1_for_a_python_case_whose_module_level_helper_precedes_a_second_case_after_an_assertion_is_deleted_from_the_helper_2931(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / SAMPLE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _green(tmp_path, run_cli, tests_frozen, repo, SAMPLE, SAMPLE_INLINE)
    suite.write_text(SAMPLE_EXTRACTED)
    repo.commit("A refactor", all=True)
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    rerecorded = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    suite.write_text(SAMPLE_EXTRACTED.replace("    assert x != 2\n\n\ndef test_a", "\n\ndef test_a"))
    repo.commit("helper assertion deleted", all=True)

    code, out, err = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)

    assert rerecorded[0] == 0 and "skipped:" not in rerecorded[2], rerecorded
    assert (code, "test_a" in out + err, "test_b" in out + err) == (1, True, False), out + err


def test_check_earlier_exits_1_naming_the_case_and_leaves_the_record_untouched_when_the_helpers_digest_matches_neither_formula_3164(
        tmp_path, run_cli, tests_frozen, based):
    text = ("def helper():\n    assert 1 == 1\n\n\ndef test_a():\n    helper()\n\n\n"
            "def other():\n    assert 2 == 2\n")
    suite = tmp_path / SUITE
    earlier, current = "step one adds a case", "step two adds nothing"
    suite.write_text(OLDER + "\n\n" + text)
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    legacy = tests_frozen.body_digest("\n".join(sorted(tests_frozen._assertion_lines(text))))
    kept = [l for l in record.read_text().splitlines(keepends=True) if not l.startswith("helpers:")]
    record.write_text("".join(kept) + "helpers: %s\ttest_a\t%s\n" % (SUITE, legacy))
    suite.write_text(OLDER + "\n\n" + text.replace("    assert 1 == 1\n", "    pass\n"))
    before = record.read_text()
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, "test_a" in out, record.read_text()) == (1, True, before)


def test_check_earlier_exits_0_for_a_go_case_moved_with_its_helper_to_a_sibling_file_while_the_recorded_file_stays_4601(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    sibling = "b_test.go"
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    (tmp_path / GO_SUITE).write_text(GO_CHECK_X + GO_CALLS_CHECK_X + "\nfunc TestY(t *testing.T) {\n}\n")
    repo.add(GO_SUITE)
    run_cli(tests_frozen, ["record", "--step", STEPS[1], GO_SUITE], cwd=tmp_path)
    _ledger(tmp_path, A="done")
    repo.commit("step A adds the cases")
    (tmp_path / GO_SUITE).write_text("func TestY(t *testing.T) {\n}\n")
    (tmp_path / sibling).write_text(GO_CHECK_X + GO_CALLS_CHECK_X)
    repo.add(GO_SUITE, sibling)
    repo.commit("a refactor moves TestX and its helper to a sibling file")

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_check_earlier_exits_0_for_a_go_case_a_verified_refactor_moved_with_its_helper_to_a_sibling_file_after_the_rerecord_4601(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE,
                GO_CHECK_X + GO_CALLS_CHECK_X + "\nfunc TestY(t *testing.T) {\n}\n",
                "func TestY(t *testing.T) {\n}\n",
                "A refactor moves TestX and its helper to a sibling file",
                moved={"b_test.go": GO_CHECK_X + GO_CALLS_CHECK_X})

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")
