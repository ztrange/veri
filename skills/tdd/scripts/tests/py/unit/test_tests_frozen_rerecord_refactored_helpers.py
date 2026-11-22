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


def _record_of(tmp_path):
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    return record


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
    changed = SHORT_CHECKS.replace('if x != 1 {\n\t\tt.Fatal("b")', 'if x != 2 {\n\t\tt.Fatal("b")')
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


SETUP_INLINE = "func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"setup\")\n\tt.Error(\"later\")\n}\n"
SETUP_EXTRACTED = ("func setupX(t *testing.T) {\n\tt.Fatal(\"setup\")\n}\n\n"
                   "func TestX(t *testing.T) {\n\tx := 1\n\tsetupX(t)\n\tt.Error(\"later\")\n}\n")


def test_rerecord_refactored_re_records_a_go_case_whose_setup_t_fatal_lines_a_refactor_moved_into_a_helper_ahead_of_later_assertions_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, SETUP_INLINE, SETUP_EXTRACTED,
                        message="A refactor extracts the setup check into a helper")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_rerecord_refactored_re_records_a_go_case_whose_helper_lines_sort_before_its_own_remaining_assertion_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE,
                        "func TestX(t *testing.T) {\n\tt.Fatal(\"a setup\")\n\tt.Fatal(\"z later\")\n}\n",
                        "func setupX(t *testing.T) {\n\tt.Fatal(\"a setup\")\n}\n\n"
                        "func TestX(t *testing.T) {\n\tsetupX(t)\n\tt.Fatal(\"z later\")\n}\n",
                        message="A refactor extracts the setup check into a helper")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_rerecord_refactored_run_again_with_the_same_green_sha_heals_an_order_changing_helper_extractions_stale_record_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, SETUP_INLINE, SETUP_EXTRACTED,
                        message="A refactor extracts the setup check into a helper")
    verdict = tmp_path / VERDICT
    verdict.write_text("1")
    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    verdict.write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def _append_helpers_line(tmp_path, tests_frozen):
    """As the process cases did after `record`: append TestX's helpers line, its digest over the suite as it reads."""
    suite = tmp_path / GO_SUITE
    with _record_of(tmp_path).open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))


def test_rerecord_refactored_skips_a_go_case_at_heads_body_whose_refactor_lost_a_helper_assertion_line_2973(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    recorded = ("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                "\tif x < 0 {\n\t\tt.Error(\"negative\")\n\t}\n}\n\n"
                "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, recorded,
                        recorded.replace("\tif x < 0 {\n\t\tt.Error(\"negative\")\n\t}\n", ""),
                        edit_record=lambda: _append_helpers_line(tmp_path, tests_frozen))
    record = _record_of(tmp_path)
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (b"body: suite_test.go\tTestX\td3354d8e746c7e77dfa4825bd1bbf69069b22ead3ac8bd0ed4592ef68c20f344\n" in before,
            b"\nhelpers: " in before, code, _skip_lines(err, "suite_test.go TestX"),
            record.read_bytes() == before) == (True, True, 1, 1, True)


def test_rerecord_refactored_refreshes_the_helpers_line_of_a_go_case_already_recorded_at_heads_body_so_check_earlier_exits_0_2973(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    recorded = CHECK_X + "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n"
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, recorded,
                        recorded.replace("x := 1", "x := 1 // one").replace('"bad"', '"bad value"'),
                        edit_record=lambda: _append_helpers_line(tmp_path, tests_frozen))
    record = _record_of(tmp_path)
    green_body = tests_frozen._bodies_of(recorded, "TestX")[0]
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    record.write_text(record.read_text().replace(
        tests_frozen.body_line("suite_test.go", "TestX", green_body),
        tests_frozen.body_line("suite_test.go", "TestX", head_body)))
    held = tests_frozen._helper_digest(suite.read_text(), head_body)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "suite_test.go TestX") > 0,
            "helpers: suite_test.go\tTestX\t%s\n" % held in record.read_text(), checked) == (
        0, False, True, (0, ""))


THREE = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
TWO = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2))
REQUIRE_ALL = ("func requireAll(t *testing.T, x int) {\n" + THREE + "}\n\n"
               "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")


def test_rerecord_refactored_re_records_a_go_case_at_heads_body_whose_helpers_digest_is_neither_greens_nor_heads_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, "func TestX(t *testing.T) {\n\tx := 1\n" + THREE + "}\n",
                        REQUIRE_ALL, edit_record=lambda: _append_helpers_line(tmp_path, tests_frozen),
                        message="A refactor moves the assertions into a helper")
    record = _record_of(tmp_path)
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    older = "helpers: suite_test.go\tTestX\t%s\n" % ("6" * 64)
    record.write_text("".join(
        tests_frozen.body_line("suite_test.go", "TestX", head_body) + "\n"
        if line.startswith("body: ") else older if line.startswith("helpers: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    held = tests_frozen._helper_digest(suite.read_text(), head_body)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "suite_test.go TestX") > 0,
            "helpers: suite_test.go\tTestX\t%s\n" % held in record.read_text(), checked) == (
        0, False, True, (0, ""))


def _heads_with_foreign_helpers(tmp_path, tests_frozen):
    """Rewrites each body line of the record to the case's body at HEAD, followed by a helpers line no tree holds;
    returns the TestX lines and TestY's helpers line as HEAD holds it."""
    suite, record = tmp_path / GO_SUITE, _record_of(tmp_path)
    heads = {case: tests_frozen._bodies_of(suite.read_text(), case)[0] for case in ("TestX", "TestY")}
    record.write_text("".join(
        "%s\nhelpers: suite_test.go\t%s\t%s\n" % (tests_frozen.body_line(
            "suite_test.go", line.split("\t")[1], heads[line.split("\t")[1]]), line.split("\t")[1], "6" * 64)
        if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    x_lines = [line for line in record.read_text().splitlines() if "\tTestX\t" in line]
    held = "helpers: suite_test.go\tTestY\t%s" % tests_frozen._helper_digest(suite.read_text(), heads["TestY"])
    return x_lines, held


def test_rerecord_refactored_skips_a_go_case_at_heads_body_whose_helpers_digest_is_neither_greens_nor_heads_when_the_refactor_lost_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE,
                        "func TestX(t *testing.T) {\n\tx := 1\n" + THREE + "}\n\n"
                        "func TestY(t *testing.T) {\n\tx := 1\n" + THREE + "}\n",
                        "func requireTwo(t *testing.T, x int) {\n" + TWO + "}\n\n"
                        "func requireAll(t *testing.T, x int) {\n" + THREE + "}\n\n"
                        "func TestX(t *testing.T) {\n\tx := 1\n\trequireTwo(t, x)\n}\n\n"
                        "func TestY(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n",
                        message="A refactor moves the assertions into helpers; TestX's loses one")
    record = _record_of(tmp_path)
    x_lines, held = _heads_with_foreign_helpers(tmp_path, tests_frozen)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    after = record.read_text().splitlines()

    assert (code, _skip_lines(err, "suite_test.go TestX"),
            _skip_lines(err, "suite_test.go TestY"),
            [line for line in after if "\tTestX\t" in line] == x_lines, held in after) == (
        1, 1, 0, True, False)


def test_rerecord_refactored_skips_a_go_case_at_heads_body_whose_helpers_digest_is_neither_greens_nor_heads_when_the_refactor_added_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE,
                        "func TestX(t *testing.T) {\n\tx := 1\n" + TWO + "}\n\n"
                        "func TestY(t *testing.T) {\n\tx := 1\n" + THREE + "}\n",
                        "func requireAll(t *testing.T, x int) {\n" + THREE + "}\n\n"
                        "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n\n"
                        "func TestY(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n",
                        message="A refactor moves the assertions into a helper; TestX's gains one")
    record = _record_of(tmp_path)
    x_lines, held = _heads_with_foreign_helpers(tmp_path, tests_frozen)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    after = record.read_text().splitlines()

    assert (code, _skip_lines(err, "suite_test.go TestX"),
            _skip_lines(err, "suite_test.go TestY"),
            [line for line in after if "\tTestX\t" in line] == x_lines, held in after) == (
        1, 1, 0, True, False)


def test_rerecord_refactored_skips_a_go_case_whose_body_digest_is_neither_greens_nor_heads_while_its_helpers_digest_is_greens_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    recorded = CHECK_X + "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n"

    def foreign_body():
        record = _record_of(tmp_path)
        record.write_text("".join(
            "body: suite_test.go\tTestX\t%s\n" % ("f" * 64) if line.startswith("body: ") else line
            for line in record.read_text().splitlines(keepends=True)))
        _append_helpers_line(tmp_path, tests_frozen)

    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, recorded,
                        recorded.replace("x := 1", "x := 1 // one"), edit_record=foreign_body)
    record = _record_of(tmp_path)
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (b"\nhelpers: " in before, code, _skip_lines(err, "suite_test.go TestX"),
            record.read_bytes() == before) == (True, 1, 1, True)


def test_rerecord_refactored_names_the_helpers_digest_guard_in_parentheses_on_the_skipped_line_of_a_record_at_greens_body_whose_helpers_digest_differs_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    recorded = CHECK_X + "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n"

    def foreign_helpers():
        with _record_of(tmp_path).open("a") as handle:
            handle.write("helpers: suite_test.go\tTestX\t%s\n" % ("0" * 64))

    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, recorded, recorded + "\n// tidied\n",
                        edit_record=foreign_helpers)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        1, 1, [True])


def test_rerecord_refactored_names_the_assertion_lines_guard_in_parentheses_on_the_skipped_line_of_a_head_body_record_whose_case_and_helpers_lost_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, "func TestX(t *testing.T) {\n\tx := 1\n" + THREE + "}\n",
                        "func requireTwo(t *testing.T, x int) {\n" + TWO + "}\n\n"
                        "func TestX(t *testing.T) {\n\tx := 1\n\trequireTwo(t, x)\n}\n",
                        message="A refactor moves the assertions into a helper and loses one")
    record = _record_of(tmp_path)
    head = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    record.write_text("".join(
        "%s\nhelpers: suite_test.go\tTestX\t%s\n" % (tests_frozen.body_line("suite_test.go", "TestX", head), "6" * 64)
        if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        1, 1, [True])


def test_rerecord_refactored_names_the_helper_assertion_count_guard_in_parentheses_on_the_skipped_line_of_a_record_whose_case_body_is_unchanged_but_whose_helper_gained_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    one = "\tif x != 1 {\n\t\tt.Fatal(\"bad 1\")\n\t}\n"
    two = one + "\tif x != 2 {\n\t\tt.Fatal(\"bad 2\")\n\t}\n"
    case = "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n"
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE,
                        "func checkX(t *testing.T, x int) {\n" + one + "}\n\n" + case,
                        "func checkX(t *testing.T, x int) {\n" + two + "}\n\n" + case,
                        message="A refactor adds an assertion to the helper")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        0, 1, [True])


def test_rerecord_refactored_leaves_one_helpers_line_from_head_for_a_go_case_whose_record_held_two_stale_ones_so_check_earlier_exits_0_2998(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, "func TestX(t *testing.T) {\n\tx := 1\n" + THREE + "}\n",
                        REQUIRE_ALL, message="A refactor moves the assertions into a helper")
    record = _record_of(tmp_path)
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    stale = "".join("helpers: suite_test.go\tTestX\t%s\n" % (digit * 64) for digit in "67")
    record.write_text("".join(
        line for line in record.read_text().splitlines(keepends=True) if not line.startswith("body: ")
    ).replace("case: TestX\n", "case: TestX\n" + tests_frozen.body_line("suite_test.go", "TestX", head_body)
              + "\n" + stale))
    held = tests_frozen._helper_digest(suite.read_text(), head_body)

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert ([l for l in record.read_text().splitlines() if l.startswith("helpers: ")], checked) == (
        ["helpers: suite_test.go\tTestX\t%s" % held], (0, ""))


def test_rerecord_refactored_leaves_a_record_with_two_helpers_lines_byte_identical_for_a_case_it_skips_2998(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, "func TestX(t *testing.T) {\n\tx := 1\n}\n",
                        "func TestX(t *testing.T) {\n\tx := 2\n}\n")
    record = _record_of(tmp_path)
    stale = "".join("helpers: suite_test.go\tTestX\t%s\n" % (digit * 64) for digit in "67")
    record.write_text("".join(
        line + stale if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, "skipped: suite_test.go TestX" in err, record.read_bytes()) == (1, True, before)


def test_rerecord_refactored_keeps_a_helpers_line_of_a_later_case_that_does_not_follow_a_rewritten_body_2998(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, "func TestX(t *testing.T) {\n\tx := 1\n" + THREE + "}\n",
                        REQUIRE_ALL, message="A refactor moves the assertions into a helper")
    record = _record_of(tmp_path)
    later = "case: TestY\nhelpers: suite_test.go\tTestY\t%s\n" % ("8" * 64)
    record.write_text(record.read_text() + later)

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert record.read_text().endswith(later)


def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_go_cases_sharing_a_helper_the_refactor_introduced_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    checks = "".join('\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m for m in "abc")
    inline = "".join('func Test%s(t *testing.T) {\n\tx := 1\n%s}\n\n' % (n, checks)
                     for n in ("One", "Two", "Three"))
    shared = "".join('func Test%s(t *testing.T) {\n\tx := 1\n\tsharedBase(t, x)\n}\n\n' % n for n in ("One", "Two", "Three"))
    helper = ('func sharedBase(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n'
              '\tif x != 1 {\n\t\tt.Fatal("c")\n\t}\n}\n')
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, shared + helper)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, err, checked) == (0, "", (0, ""))


TS_NAMES = ("one", "two", "three")
TS_INLINE = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n});\n\n" % n
                    for n in TS_NAMES)


def _ts_rerecorded(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, inline, refactored):
    """Three TS cases recorded as `inline`, refactored to `refactored`; returns (rerecord code, its stderr,
    check-earlier's (code, stdout))."""
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, TS_SUITE, inline, refactored)
    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]
    return code, err, checked


def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_typescript_cases_sharing_a_function_helper_the_refactor_introduced_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in TS_NAMES)
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"

    code, err, checked = _ts_rerecorded(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, TS_INLINE,
                                        shared + helper)

    assert (code, err, checked) == (0, "", (0, ""))


def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_typescript_cases_sharing_a_function_helper_named_test_helper_the_refactor_introduced_2931(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    shared = "".join("it('%s', () => {\n  const x = 1;\n  testHelper();\n});\n\n" % n for n in TS_NAMES)
    helper = "function testHelper() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"

    code, err, checked = _ts_rerecorded(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, TS_INLINE,
                                        shared + helper)

    assert (code, err, checked) == (0, "", (0, ""))


def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_typescript_cases_sharing_an_arrow_function_helper_the_refactor_introduced_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in TS_NAMES)
    helper = "const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"

    code, err, checked = _ts_rerecorded(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, TS_INLINE,
                                        shared + helper)

    assert (code, err, checked) == (0, "", (0, ""))


def test_rerecord_refactored_then_check_earlier_exits_1_naming_the_cases_when_the_refactor_adds_an_assertion_line_to_the_shared_typescript_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(%d);\n});\n\n" % (n, i)
                     for i, n in enumerate(TS_NAMES, 1))
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in TS_NAMES)
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n  expect(x).toBe(4);\n}\n"

    _, err, (checked, _) = _ts_rerecorded(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, inline,
                                          shared + helper)

    skipped = [line for line in err.splitlines() if line.startswith("skipped: suite.test.ts ")]
    assert (bool(skipped), checked) == (True, 1)


def test_rerecord_refactored_skips_only_the_go_case_whose_own_lines_the_shared_helper_exceeds_and_check_earlier_exits_1_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)

    def check(m):
        return '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m

    inline = ("func TestX(t *testing.T) {\n\tx := 1\n" + check("a") + check("b") + "}\n\n"
              "func TestY(t *testing.T) {\n\tx := 1\n" + check("a") + check("b") + check("c") + "}\n\n")
    shared = "".join("func Test%s(t *testing.T) {\n\tx := 1\n\tsharedBase(t, x)\n}\n\n" % n for n in ("X", "Y"))
    helper = "func sharedBase(t *testing.T, x int) {\n" + check("a") + check("b") + check("c") + "}\n"
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, shared + helper)

    err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[2]
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    skipped = [l.split(" (")[0] for l in err.splitlines() if l.startswith("skipped: ")]
    assert (skipped, checked) == (["skipped: suite_test.go TestX"], 1)


def _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper, shared=None):
    """Three TS cases with inline expects, refactored into `shared` + `helper`; returns (skipped lines, check-earlier code)."""
    shared = shared or "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in TS_NAMES)
    _, err, (checked, _) = _ts_rerecorded(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, TS_INLINE,
                                          shared + helper)
    return [l.split(" (")[0] for l in err.splitlines() if l.startswith("skipped: ")], checked


@pytest.mark.parametrize("opener", ["let sharedBase = () => {", "return sharedBase = () => {"])
def test_rerecord_refactored_does_not_take_a_let_or_return_line_for_a_typescript_helper_definition_and_check_earlier_exits_1_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, opener):
    helper = opener + "\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper)

    assert (len(skipped), checked) == (3, 1)


def test_rerecord_refactored_does_not_count_the_assertions_of_a_function_following_the_shared_typescript_helper_as_the_helpers_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    helper = ("function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
              "function unrelated() {\n  expect(x).toBe(9);\n}\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper)

    assert (skipped, checked) == ([], 0)


def test_rerecord_refactored_skips_every_case_and_check_earlier_exits_1_when_the_refactor_deletes_an_assertion_from_the_shared_typescript_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n}\n"

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper)

    assert (len(skipped), checked) == (3, 1)


def test_rerecord_refactored_skips_only_the_case_whose_helper_call_line_the_refactor_deleted_and_check_earlier_exits_1_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
    shared = "".join("it('%s', () => {\n  const x = 1;\n%s});\n\n" % (n, "  sharedBase();\n" if n != "two" else "")
                     for n in ("one", "two", "three"))

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper, shared)

    assert (skipped, checked) == (["skipped: suite.test.ts two"], 1)


def test_rerecord_refactored_does_not_let_a_non_arrow_const_before_the_shared_typescript_arrow_helper_swallow_it_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    helper = ("const y = 2;\n"
              "const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper)

    assert (skipped, checked) == ([], 0)


def test_rerecord_refactored_does_not_count_the_assertions_of_a_non_arrow_const_following_the_shared_typescript_helper_as_the_helpers_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    helper = ("const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"
              "const unrelated = 3;\nexpect(x).toBe(9);\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper)

    assert (skipped, checked) == ([], 0)


def test_rerecord_refactored_does_not_take_a_non_arrow_const_the_cases_call_for_a_typescript_helper_definition_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    helper = ("function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
              "const other = wrap(() => {\n  expect(x).toBe(9);\n});\n")
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n  other();\n});\n\n" % n
                     for n in ("one", "two", "three"))

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper, shared)

    assert (skipped, checked) == ([], 0)


@pytest.mark.parametrize("opener", ["const sharedBase = async () => {", "const sharedBase = x => {"])
def test_rerecord_refactored_takes_an_async_or_single_parameter_typescript_arrow_const_for_the_shared_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, opener):
    helper = opener + "\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.parametrize("word", ["constants", "functional"])
def test_rerecord_refactored_does_not_end_the_shared_typescript_helper_at_a_column_0_line_merely_starting_with_a_keyword_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, word):
    helper = ("const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n%s\n  expect(x).toBe(3);\n};\n" % word)

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper)

    assert (skipped, checked) == ([], 0)


def test_rerecord_refactored_does_not_take_a_typescript_arrow_const_the_cases_do_not_call_for_their_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    helper = ("function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
              "const other = () => {\n  expect(x).toBe(9);\n};\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, helper)

    assert (skipped, checked) == ([], 0)


def test_rerecord_refactored_then_check_earlier_exits_0_for_a_python_case_whose_refactor_moved_assertions_into_a_module_level_helper_before_a_second_case_2931(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    test_b = 'def test_b():\n    y = 2\n    assert y == 2\n    assert y != 3\n'
    inline = ('def test_a():\n    x = 1\n    assert x == 1\n    assert x != 2\n\n\n' + test_b)
    extracted = ('def assert_refused(x):\n    assert x == 1\n    assert x != 2\n\n\n'
                 'def test_a():\n    x = 1\n    assert_refused(x)\n\n\n' + test_b)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, PY_SAMPLE, inline, extracted)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, "skipped:" in err, checked) == (0, False, (0, ""))


def test_rerecord_refactored_skips_a_go_case_whose_refactor_weakened_a_t_fatal_message_without_moving_it_4533(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    inline = "func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatalf(\"setup: %v\", x)\n\tt.Fatalf(\"bad: %v\", x)\n}\n"
    weakened = "func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatalf(\"setup: %v\", x)\n\tt.Fatalf(\"ok\")\n}\n"
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, weakened)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, GO_SUITE + " TestX")) == (1, 1)


def test_rerecord_refactored_re_records_a_go_case_whose_setup_t_fatalf_lines_a_refactor_moved_into_an_existing_helper_worded_differently_4533(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    helper = "func h(t *testing.T, n int) {\n\tif n < 0 {\n\t\tt.Fatalf(\"h got %d\", n)\n\t}\n}\n\n"
    inline = helper + "func TestX(t *testing.T) {\n\terr := start()\n\tif err != nil {\n\t\tt.Fatalf(\"start: %v\", err)\n\t}\n}\n"
    moved = helper.replace("n int) {\n", "n int) {\n\terr := start()\n\tif err != nil {\n\t\tt.Fatalf(\"start: %v\", err)\n\t}\n") \
        + "func TestX(t *testing.T) {\n\th(t, 1)\n}\n"
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, moved)
    before = _record_of(tmp_path).read_text()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, GO_SUITE + " TestX"), _record_of(tmp_path).read_text() != before) == (0, 0, True)


def test_rerecord_refactored_re_records_a_go_case_whose_setup_t_fatalf_lines_a_refactor_moved_into_a_method_helper_with_a_receiver_4533(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    setup = "\terr := start()\n\tif err != nil {\n\t\tt.Fatalf(\"start: %v\", err)\n\t}\n"
    inline = "func TestX(t *testing.T) {\n\tf := &fx{}\n" + setup + "\tf.use()\n}\n"
    moved = ("func (f *fx) seed(t *testing.T) {\n" + setup + "}\n\n"
             "func TestX(t *testing.T) {\n\tf := &fx{}\n\tf.seed(t)\n\tf.use()\n}\n")
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, moved)
    before = _record_of(tmp_path).read_text()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, GO_SUITE + " TestX"), _record_of(tmp_path).read_text() != before) == (0, 0, True)


def test_rerecord_refactored_re_records_a_go_case_whose_setup_t_fatalf_lines_a_refactor_moved_into_a_new_helper_4533(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    setup = "\terr := start()\n\tif err != nil {\n\t\tt.Fatalf(\"start: %v\", err)\n\t}\n"
    inline = "func TestX(t *testing.T) {\n" + setup + "\tuse()\n}\n"
    moved = "func boot(t *testing.T) {\n" + setup + "}\n\nfunc TestX(t *testing.T) {\n\tboot(t)\n\tuse()\n}\n"
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, moved)
    before = _record_of(tmp_path).read_text()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, GO_SUITE + " TestX"), _record_of(tmp_path).read_text() != before) == (0, 0, True)


def test_rerecord_refactored_skips_a_go_case_whose_refactor_moved_a_guarded_t_fatalf_into_a_helper_under_a_changed_condition_4545(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    check = "\tif err != nil {\n\t\tt.Fatalf(\"get %s: %v\", url, err)\n\t}\n"
    inline = "func TestX(t *testing.T) {\n\turl := \"/x\"\n\terr := get(url)\n" + check + "}\n"
    moved = ("func mustGet(t *testing.T, url string) {\n\terr := get(url)\n" + check.replace("err != nil", "false") + "}\n\n"
             "func TestX(t *testing.T) {\n\turl := \"/x\"\n\tmustGet(t, url)\n}\n")
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, moved)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, GO_SUITE + " TestX")) == (1, 1)


def test_rerecord_refactored_re_records_a_go_case_whose_refactor_moved_a_guarded_t_fatalf_into_a_helper_under_the_same_condition_with_a_reworded_message_4545(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    inline = ("func TestX(t *testing.T) {\n\turl := \"/x\"\n\tresp, err := get(url)\n"
              "\tif err != nil {\n\t\tt.Fatalf(\"GET: %v\", err)\n\t}\n\tuse(resp)\n}\n")
    moved = ("func mustGet(t *testing.T, url string) {\n\t_, err := get(url)\n"
             "\tif err != nil {\n\t\tt.Fatalf(\"GET %s: %v\", url, err)\n\t}\n}\n\n"
             "func TestX(t *testing.T) {\n\turl := \"/x\"\n\tmustGet(t, url)\n\tuse(nil)\n}\n")
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, GO_SUITE, inline, moved)
    before = _record_of(tmp_path).read_text()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, GO_SUITE + " TestX"), _record_of(tmp_path).read_text() != before) == (0, 0, True)


def test_rerecord_refactored_re_records_a_go_case_a_refactor_moved_byte_identical_with_its_helper_to_a_sibling_file_while_the_recorded_file_stays_4601(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    sibling = "b_test.go"
    moved = ('func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("bad")\n\t}\n}\n\n'
             'func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n')
    stays = "func TestY(t *testing.T) {\n}\n"
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    (tmp_path / sibling).write_text("package a\n")
    repo.add(sibling)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, "a_test.go", moved + "\n" + stays, stays)
    (tmp_path / sibling).write_text(moved)
    repo.commit("the refactor moves TestX and its helper to a sibling file", all=True)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    bodies = [l for l in _record_of(tmp_path).read_text().splitlines() if l.startswith("body: ")]
    assert (code, "skipped:" in err, any(sibling + "\tTestX\t" in l for l in bodies)) == (0, False, True), err


def test_rerecord_refactored_writes_the_helpers_record_of_a_go_case_moved_to_a_sibling_file_naming_it_with_the_digest_of_its_text_4601(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    sibling = "b_test.go"
    moved = ('func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("bad")\n\t}\n}\n\n'
             'func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n')
    stays = "func TestY(t *testing.T) {\n}\n"
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    (tmp_path / sibling).write_text("package a\n")
    repo.add(sibling)
    green = _refactored(tmp_path, run_cli, tests_frozen, repo, "a_test.go", moved + "\n" + stays, stays)
    (tmp_path / sibling).write_text(moved)
    repo.commit("the refactor moves TestX and its helper to a sibling file", all=True)
    expected = "f0780c48381da294935f07291e399ed7dd7ad1cb153e2e4961ce361062e4404b"

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]

    held = [l.split("\t") for l in _record_of(tmp_path).read_text().splitlines()
            if l.startswith("helpers: " + sibling + "\t") and l.split("\t")[1] == "TestX"]
    assert (code, [h[2] for h in held]) == (0, [expected]), held


SIBLING_CASE, SIBLING_HELPERS = "cmd/x/a_test.go", "cmd/x/b_test.go"
GUARDED_GET = "\tresp, err := http.Get(url)\n\tif err != nil {\n\t\tt.Fatalf(\"GET %s: %v\", url, err)\n\t}\n"


def _moved_to_sibling(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, moved=GUARDED_GET, others=None):
    """Step A records a Go case holding GUARDED_GET in SIBLING_CASE; a verified refactor moves `moved` into
    getPage in a new SIBLING_HELPERS of the same directory, the case calling it, and adds `others` ({path: text});
    returns the green revision."""
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    (tmp_path / "cmd/x").mkdir(parents=True)
    case = tmp_path / SIBLING_CASE
    case.write_text("func TestPage(t *testing.T) {\n\turl := \"/x\"\n" + GUARDED_GET + "\tuse(resp)\n}\n")
    repo.add(SIBLING_CASE)
    run_cli(tests_frozen, ["record", "--step", STEPS[1], SIBLING_CASE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    case.write_text("func TestPage(t *testing.T) {\n\turl := \"/x\"\n\tuse(getPage(t, url))\n}\n")
    (tmp_path / SIBLING_HELPERS).write_text(
        "func getPage(t *testing.T, url string) string {\n" + moved + "\treturn read(resp)\n}\n")
    for path, text in (others or {}).items():
        (tmp_path / path).write_text(text)
    repo.add(SIBLING_HELPERS, *(others or {}))
    repo.commit("A refactor moves the GET into a helper in a sibling file", all=True)
    (tmp_path / VERDICT).write_text("0")
    return green


def test_rerecord_refactored_re_records_a_go_case_whose_guarded_http_get_lines_a_refactor_moved_into_a_helper_in_a_new_sibling_test_file_4606(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    green = _moved_to_sibling(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    before = _record_of(tmp_path).read_text()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, SIBLING_CASE + " TestPage"), _record_of(tmp_path).read_text() != before) == (0, 0, True)


def test_check_earlier_exits_0_for_a_go_case_re_recorded_after_a_refactor_moved_its_guarded_get_into_a_sibling_test_file_4606(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    green = _moved_to_sibling(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_rerecord_refactored_still_skips_a_sibling_move_that_dropped_the_t_fatalf_another_siblings_uncalled_helper_holds_4606(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    dropped = GUARDED_GET.replace("\t\tt.Fatalf(\"GET %s: %v\", url, err)\n", "")
    uncalled = "func mustGet(t *testing.T, url string) {\n" + GUARDED_GET + "}\n"
    green = _moved_to_sibling(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, moved=dropped,
                              others={"cmd/x/c_test.go": uncalled})
    before = _record_of(tmp_path).read_text()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, SIBLING_CASE + " TestPage"), _record_of(tmp_path).read_text()) == (1, 1, before)
