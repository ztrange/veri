"""In-process rerecord-refactored cases without helpers, on a history committed through fed_commits (PRD 017.11).

A process case built the plan repository with git, committed step A's red and green, a verified refactor on top, and
ran `tests-frozen.sh rerecord-refactored <ledger> <green>`. Here every commit goes through fed_commits, so
case_history answers the green's and HEAD's cases, the step's own commits and their subjects from the fed log.
"""
import hashlib
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
GO_SUITE = "suite_test.go"
JS_SUITE = "suite.test.js"
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


def test_rerecord_refactored_re_records_a_case_the_verified_refactor_tidied_and_leaves_one_already_stale_at_green_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    suite.write_text(suite.read_text().replace("x = 2\n    assert x\n", "x = 3\n    assert x\n"))
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]
    spared = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2], "--except", "test_two"],
                     cwd=tmp_path)[:2]
    refused = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, spared, refused) == (1, (0, ""), (1, "test_two (%s)\n" % step))


def test_rerecord_refactored_re_records_an_earlier_steps_case_whose_assertion_line_the_refactor_only_reformatted_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), "def test_one():\n    x = 1\n    assert x == 1\n"]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    green = repo.commit("B green", all=True)
    suite.write_text(suite.read_text().replace("assert x == 1\n", "assert x==1\n"))
    repo.commit("B refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", "step C"], cwd=tmp_path)[:2]

    assert checked == (0, "")


def test_rerecord_refactored_leaves_a_python_cases_record_when_the_refactor_changed_an_assertion_line_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("x = 1\n    assert x\n", "x = 1\n    assert x > 5\n"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "test_one (%s)\n" % step)


def test_rerecord_refactored_leaves_a_javascript_cases_record_when_the_refactor_changed_an_expect_line_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    suite = tmp_path / JS_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("it('one', () => {\n  const x = 1;\n  expect(x).toBe(1);\n});\n")
    repo.add(JS_SUITE)
    run_cli(tests_frozen, ["record", "--step", step, JS_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("expect(x).toBe(1)", "expect(x).toBeGreaterThan(5)"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "one (%s)\n" % step)


@pytest.mark.parametrize("before, after", [
    ('t.Fatalf("got %d", x)', 't.Fatalf("got %d, want 5", x+1)'),
    ('t.Errorf("got %d", x)', 't.Errorf("got %d, want 5", x+1)'),
    ('t.Fail()', 't.FailNow()'),
    ('require.Equal(t, 1, x)', 'require.Equal(t, 5, x)'),
])
def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_changed_its_check_line_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, before, after):
    step = STEPS[1]
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\t%s\n\t}\n}\n" % before)
    repo.add(GO_SUITE)
    run_cli(tests_frozen, ["record", "--step", step, GO_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace(before, after))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestOne (%s)\n" % step)


def _go_refactored(tmp_path, run_cli, tests_frozen, repo, recorded, refactored, edit_record=None):
    """Step A records `recorded` in suite_test.go (red, green; `edit_record` then rewrites its record), a verified
    refactor rewrites it to `refactored`; returns the green revision."""
    suite = tmp_path / GO_SUITE
    suite.write_text(recorded)
    repo.add(GO_SUITE)
    run_cli(tests_frozen, ["record", "--step", STEPS[1], GO_SUITE], cwd=tmp_path)
    if edit_record:
        edit_record()
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(refactored)
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")
    return green


def test_rerecord_refactored_prints_one_stderr_line_naming_each_case_it_left_unrecorded_and_still_exits_0_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + '}\n'
    dropped = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '}\n'
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, inline, dropped)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "suite_test.go TestOne")) == (1, 1)


def test_rerecord_refactored_names_a_case_gone_at_head_a_digest_mismatch_and_an_assertionless_shape_change_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    chk = '\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
    fn = lambda name, body: 'func %s(t *testing.T) {\n%s}\n\n' % (name, body)
    suite.write_text(fn("TestGone", "\tx := 1\n" + chk) + fn("TestMismatch", "\tx := 1\n" + chk) + fn("TestBare", "\tx := 1\n"))
    repo.add(GO_SUITE)
    run_cli(tests_frozen, ["record", "--step", step, GO_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    suite.write_text(fn("TestGone", "\tx := 1\n" + chk) + fn("TestMismatch", "\tx := 1\n\ty := 2\n" + chk) + fn("TestBare", "\tx := 1\n"))
    green = repo.commit("A green", all=True)
    suite.write_text(fn("TestMismatch", "\tx := 1\n\ty := 2\n" + chk) + fn("TestBare", "\tx := 2\n"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, sorted(l.split(" (")[0] for l in err.splitlines() if l.startswith("skipped:"))) == (1, [
        "skipped: suite_test.go TestBare", "skipped: suite_test.go TestGone", "skipped: suite_test.go TestMismatch"])


def test_rerecord_refactored_heals_a_format_2_go_record_cut_with_the_body_running_past_the_closing_brace_so_check_earlier_exits_0_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    other = '\nfunc other(t *testing.T) {\n\tt.Fatal("z")\n}\n'
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + '}\n' + other
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n' + chk("a") + '}\n' + other)

    def format_2():
        record = tmp_path / run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()
        old_digest = hashlib.sha256(inline.rstrip().encode()).hexdigest()
        record.write_text("".join(
            "body: suite_test.go\tTestOne\t%s\n" % old_digest if line.startswith("body: ") else line
            for line in record.read_text().splitlines(keepends=True)))

    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, inline, extracted, edit_record=format_2)

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


def test_rerecord_refactored_leaves_the_record_of_a_case_with_no_assertion_line_when_the_refactor_changed_its_body_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    recorded = "func TestOne(t *testing.T) {\n\tx := 1\n\tpanic(x)\n}\n"
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, recorded, recorded.replace("panic(x)", "panic(x + 1)"))

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestOne (%s)\n" % step)


def test_rerecord_refactored_leaves_a_cases_record_when_the_refactor_changed_its_title_and_body_together_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("def test_one():\n    x = 1\n", "def test_uno():\n    x = 2 - 1\n"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "test_one (%s)\n" % step)
