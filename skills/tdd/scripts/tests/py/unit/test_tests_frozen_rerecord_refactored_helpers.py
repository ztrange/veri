"""In-process rerecord-refactored cases on a case's helpers, on a history committed through fed_commits (PRD 017.12).

A process case built the plan repository with git, committed step A's red and green, a verified refactor that moved
assertions into helpers on top, and ran `tests-frozen.sh rerecord-refactored <ledger> <green>`. Here every commit goes
through fed_commits, so case_history answers the green's and HEAD's text, the step's own commits and their subjects
from the fed log.
"""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# The plan repository: ledger .tdd/issue-9.md (VERI_ISSUE=9) over STEPS. Names, not literals, in calls: a literal
# suite path reads as a nested run.
STEPS = ["step Z adds an early case", "step A adds the cases", "step B adds a later case"]
CASE = "def test_%s():\n    assert %d\n"
BODY = "def test_%s():\n    x = %d\n    assert x\n"
ROOT_SUITE = "test_suite.py"
PY_SAMPLE = "test_sample.py"
GO_SUITE = "suite_test.go"
TS_SUITE = "suite.test.ts"
PLAN_LEDGER = ".tdd/issue-9.md"
VERDICT = ".tdd/verdict-refactor.exit"


def _skip_lines(err, what):
    return sum(1 for l in err.splitlines() if l == "skipped: " + what or l.startswith("skipped: " + what + " ("))


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


def _refactored(tmp_path, run_cli, tests_frozen, repo, path, recorded, refactored, edit_record=None,
                message="A refactor"):
    """Step A records `recorded` in `path` (red, green; `edit_record` then rewrites its record before the red
    commit), a verified refactor (`message`) rewrites it to `refactored`; returns the green revision."""
    suite = tmp_path / path
    suite.write_text(recorded)
    repo.add(path)
    run_cli(tests_frozen, ["record", "--step", STEPS[1], path], cwd=tmp_path)
    if edit_record:
        edit_record()
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(refactored)
    repo.commit(message, all=True)
    (tmp_path / VERDICT).write_text("0")
    return green


def test_rerecord_refactored_re_records_an_earlier_steps_case_whose_body_the_refactor_moved_into_a_shared_helper_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    green = repo.commit("B green", all=True)
    helper = "def _value(n):\n    return n\n\n\n"
    suite.write_text(helper + suite.read_text().replace("x = 1\n", "x = _value(1)\n"))
    repo.commit("B refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", "step C"], cwd=tmp_path)[:2]

    assert checked == (0, "")


GO_INLINE = 'func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n'


def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_a_check_into_a_helper_after_the_last_case_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n')
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, GO_INLINE, extracted)

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_a_check_into_a_helper_between_two_cases_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    two = 'func TestTwo(t *testing.T) {\n\tif 2 != 2 {\n\t\tt.Fatal("c")\n\t}\n}\n'
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n\n' + two)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, GO_INLINE + "\n" + two, extracted)

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_checks_into_a_new_helper_while_it_also_calls_an_asserting_helper_green_had_3077(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    build = 'func build(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatalf("build failed")\n\t}\n}\n'
    inline = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
              '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build)
    extracted = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
                 '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, extracted)

    rerecorded = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (rerecorded, checked) == ((0, "", ""), (0, ""))


SHORT_CHECKS = '\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n'
SHORT_INLINE = ''.join('func %s(t *testing.T) {\n\tx := 1\n%s}\n\n' % (n, SHORT_CHECKS) for n in ("TestOne", "TestTwo"))
SHORT_CALLERS = ''.join('func %s(t *testing.T) {\n\tx := 1\n\tcheckShort(t, x)\n}\n\n' % n for n in ("TestOne", "TestTwo"))


def test_rerecord_refactored_re_records_two_go_cases_whose_refactor_moved_the_same_checks_verbatim_into_one_new_shared_helper_3332(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    extracted = SHORT_CALLERS + 'func checkShort(t *testing.T, x int) {\n%s}\n' % SHORT_CHECKS
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, SHORT_INLINE, extracted)

    rerecorded = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (rerecorded, checked) == ((0, "", ""), (0, ""))


def test_rerecord_refactored_skips_two_go_cases_whose_refactor_moved_the_checks_into_one_new_shared_helper_but_changed_one_3332(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    changed = SHORT_CHECKS.replace('t.Fatal("b")', 't.Fatal("c")')
    extracted = SHORT_CALLERS + 'func checkShort(t *testing.T, x int) {\n%s}\n' % changed
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, SHORT_INLINE, extracted)
    recorded = (tmp_path / PLAN_LEDGER).read_text()

    _, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (_skip_lines(err, "suite_test.go TestOne"), _skip_lines(err, "suite_test.go TestTwo"),
            (tmp_path / PLAN_LEDGER).read_text() == recorded) == (1, 1, True), err


def test_rerecord_refactored_leaves_the_record_and_check_earlier_exits_1_for_a_go_case_whose_refactor_moved_checks_into_a_helper_after_it_and_dropped_one_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + chk("c") + '}\n'
    dropped = ('func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '\tcheck(t, x)\n}\n\n'
               'func check(t *testing.T, x int) {\n' + chk("a") + '}\n')
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, dropped)

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, checked) == (1, 1)


GO_X = "func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n"
CHECK_X = "func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"


def test_rerecord_refactored_re_records_a_go_case_whose_t_fatal_lines_a_refactor_moved_into_a_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, GO_X,
                        CHECK_X + "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n",
                        message="A refactor moves the check into a helper")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_rerecord_refactored_re_records_a_python_case_whose_assert_line_a_refactor_moved_into_a_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, ROOT_SUITE, "def test_one():\n    x = 1\n    assert x == 1\n",
                        "def check_one(x):\n    assert x == 1\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n",
                        message="A refactor moves the assert into a helper")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_rerecord_refactored_leaves_a_go_cases_record_when_a_later_commit_deleted_a_t_fatal_line_from_the_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE,
                        "func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                        "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n",
                        "func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                        "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n\nfunc TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n",
                        message="A refactor moves the checks into a helper")
    suite.write_text(CHECK_X + "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    repo.commit("A refactor drops a check from the helper", all=True)

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_deleted_one_of_two_identical_t_fatal_lines_while_moving_the_other_into_a_helper_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE,
                        "func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"bad\")\n\tt.Error(\"mid\")\n\tt.Fatal(\"bad\")\n}\n",
                        "func checkX(t *testing.T) {\n\tt.Fatal(\"bad\")\n}\n\n"
                        "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t)\n\tt.Error(\"mid\")\n}\n",
                        message="A refactor moves one check into a helper and drops the other")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)
