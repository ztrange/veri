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
TWO_ASSERTS = "def test_%s():\n    x = %d\n    assert x\n    assert x > 0\n"
ROOT_SUITE = "test_suite.py"
GO_SUITE = "suite_test.go"
JS_SUITE = "suite.test.js"
PLAN_LEDGER = ".tdd/issue-9.md"
VERDICT = ".tdd/verdict-refactor.exit"


def _skip_lines(err, what):
    return sum(1 for line in err.splitlines() if line == "skipped: " + what or line.startswith("skipped: " + what + " ("))


def _ledger(root, **state):
    """The ledger in its real shapes: open, pending (ticked, ledger.PENDING_MARK appended) and done."""
    marks = {"open": "- [ ] %s", "pending": "- [x] %s ⟂ refactor pending", "done": "- [x] %s"}
    (root / PLAN_LEDGER).write_text("".join(
        marks[state.get(name, "open")] % text + "\n" for name, text in zip("ZAB", STEPS, strict=True)))


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

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    refused = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]
    skips = (_skip_lines(err, "%s test_one" % ROOT_SUITE), _skip_lines(
        err, "%s test_two (body digest matches neither green nor HEAD)" % ROOT_SUITE))

    assert (code, skips, refused[0]) == (1, (0, 1), 1)


def _tidied_and_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    """Step A's record over test_one, which the refactor tidies, and test_two, stale at green: returns the green."""
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    suite.write_text(suite.read_text().replace("x = 2\n    assert x\n", "x = 3\n    assert x\n"))
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")
    return green


def _records(tmp_path):
    return sorted((tmp_path / ".tdd").glob("tests-frozen-*.record"))


def test_rerecord_refactored_whose_closing_check_earlier_exits_1_leaves_every_frozen_record_byte_identical_4554(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    green = _tidied_and_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    records = _records(tmp_path)
    before = [r.read_bytes() for r in records]

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]

    assert (code, len(records), [r.read_bytes() for r in records]) == (1, 1, before)


def test_rerecord_refactored_whose_closing_check_earlier_exits_2_leaves_every_frozen_record_byte_identical_4554(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    green = _tidied_and_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    records = _records(tmp_path)
    before = [r.read_bytes() for r in records]
    monkeypatch.setattr(tests_frozen, "_check_earlier", lambda *args, **kwargs: 2)

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]

    assert (code, len(records), [r.read_bytes() for r in records]) == (2, 1, before)


def test_rerecord_refactored_whose_closing_check_earlier_fails_restores_two_earlier_steps_records_byte_identical_4554(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, zed = tmp_path / ROOT_SUITE, tmp_path / "test_zed.py"
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    zed.write_text(BODY % ("zero", 5))
    run_cli(tests_frozen, ["record", "--step", STEPS[0], zed.name], cwd=tmp_path)
    repo.add(zed.name)
    repo.commit("Z red", all=True)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    suite.write_text(suite.read_text().replace("x = 2\n    assert x\n", "x = 3\n    assert x\n"))
    _ledger(tmp_path, Z="done", A="done")
    green = repo.commit("A green", all=True)
    zed.write_text(zed.read_text().replace("x = 5\n", "x = 6 - 1\n"))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")
    records = _records(tmp_path)
    before = [r.read_bytes() for r in records]

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]

    assert (code, len(records), [r.read_bytes() for r in records]) == (1, 2, before)


def test_rerecord_refactored_exits_2_when_a_restored_record_cannot_be_written_4554(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    green = _tidied_and_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    monkeypatch.setattr(tests_frozen, "write_record", lambda path, out: False)

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]

    assert code == 2


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
    ('if x != 1 {\n\t\tt.Fatalf("got %d", x)', 'if x != 5 {\n\t\tt.Fatalf("got %d", x)'),
    ('if x != 1 {\n\t\tt.Errorf("got %d", x)', 'if x != 5 {\n\t\tt.Errorf("got %d", x)'),
    ('if x != 1 {\n\t\tt.Fail()', 'if x != 1 {\n\t\tt.FailNow()'),
    ('if x != 1 {\n\t\trequire.Equal(t, 1, x)', 'if x != 1 {\n\t\trequire.Equal(t, 5, x)'),
])
def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_changed_its_check_line_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, before, after):
    step = STEPS[1]
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("func TestOne(t *testing.T) {\n\tx := 1\n\t%s\n\t}\n}\n" % before)
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
    def chk(m):
        return '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
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
    def fn(name, body):
        return 'func %s(t *testing.T) {\n%s}\n\n' % (name, body)
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

    assert (code, sorted(line.split(" (")[0] for line in err.splitlines() if line.startswith("skipped:"))) == (1, [
        "skipped: suite_test.go TestBare", "skipped: suite_test.go TestGone", "skipped: suite_test.go TestMismatch"])


def test_rerecord_refactored_heals_a_format_2_go_record_cut_with_the_body_running_past_the_closing_brace_so_check_earlier_exits_0_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    def chk(m):
        return '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
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


def test_rerecord_refactored_still_re_records_the_other_cases_when_the_refactor_renamed_one_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("def test_one():\n", "def test_uno():\n")
                     .replace("x = 2\n", "x = 3 - 1\n"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]
    spared = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2], "--except", "test_one"],
                     cwd=tmp_path)[:2]

    assert (code, spared) == (0, (0, ""))


def test_rerecord_refactored_still_re_records_the_other_cases_when_an_earlier_refactor_renamed_one_before_green_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("def test_one():\n", "def test_uno():\n"))
    repo.commit("A refactor renames a case", all=True)
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    green = repo.commit("B green", all=True)
    suite.write_text(suite.read_text().replace("x = 2\n", "x = 3 - 1\n"))
    repo.commit("B refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]
    spared = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", "step C", "--except", "test_one"],
                     cwd=tmp_path)[:2]

    assert (code, spared) == (0, (0, ""))


def test_rerecord_refactored_re_records_nothing_and_exits_3_unless_verdict_refactor_exit_holds_0_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    repo.commit("A refactor", all=True)
    verdict = tmp_path / VERDICT

    def records():
        return {str(p): p.read_bytes() for p in sorted((tmp_path / ".tdd").rglob("*"))
                if p.is_file() and p != verdict}
    before, outcomes = records(), []
    for held in (None, "1"):
        if held is not None:
            verdict.write_text(held)
        outcomes.append((run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0],
                         records() == before))

    assert outcomes == [(3, True), (3, True)]


def test_rerecord_refactored_run_outside_any_git_repository_exits_2_and_re_records_nothing_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    # Outside any repository case_history.toplevel answers None, as `git rev-parse --show-toplevel` failing makes it.
    monkeypatch.setattr(tests_frozen.case_history, "toplevel", lambda: None)
    (tmp_path / ".tdd").mkdir()
    ledger, record = tmp_path / PLAN_LEDGER, tmp_path / ".tdd/record"
    ledger.write_text("- [x] step one\n")
    record.write_text("kept\n")

    code, out, _ = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, "deadbeef"], cwd=tmp_path)

    assert (code, out, record.read_text()) == (2, "", "kept\n")


def test_rerecord_refactored_unreadable_ledger_exits_2_and_re_records_nothing_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    _plan_repo(tmp_path, monkeypatch, fed_commits)
    (tmp_path / PLAN_LEDGER).unlink(missing_ok=True)
    (tmp_path / PLAN_LEDGER).mkdir()
    record = tmp_path / ".tdd/record"
    record.write_text("kept\n")

    code, out, _ = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, "deadbeef"], cwd=tmp_path)

    assert (code, out, record.read_text()) == (2, "", "kept\n")


def test_rerecord_refactored_exits_2_naming_the_record_when_writing_it_raises_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, capfd, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    repo.commit("A refactor", all=True)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()
    (tmp_path / VERDICT).write_text("0")

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record.name):
            raise OSError(28, "No space left on device", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(tmp_path)

    code = tests_frozen.rerecord_refactored(PLAN_LEDGER, green)

    assert (code, record.name in capfd.readouterr().err, record.read_bytes() == old) == (2, True, True)


def test_rerecord_refactored_re_records_a_case_with_no_assertion_line_when_the_refactor_only_changed_whitespace_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), "def test_one():\n    x = 1\n    check(x)\n"]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("check(x)\n", "check( x )\n"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


ASSERT_REFUSED_CHECK = '\tif v != "x" {\n\t\tt.Fatal("%s")\n\t}\n'
ASSERT_REFUSED_INLINE = ('func TestOne(t *testing.T) {\n\tv := "x"\n' + ASSERT_REFUSED_CHECK % "a"
                         + ASSERT_REFUSED_CHECK % "b" + '}\n')


def test_rerecord_refactored_names_a_go_case_on_a_skipped_line_and_check_earlier_exits_1_when_a_refactor_moved_its_assertions_into_assert_refused_and_dropped_one_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    def chk(m):
        return ASSERT_REFUSED_CHECK % m
    moved = ('func assertRefused(t *testing.T, v string) {\n' + chk("a") + '}\n\n'
             'func TestOne(t *testing.T) {\n\tv := "x"\n\tassertRefused(t, v)\n}\n')
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, ASSERT_REFUSED_INLINE, moved)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "suite_test.go TestOne"), checked) == (1, 1, 1)


def test_rerecord_refactored_names_a_go_case_on_a_skipped_line_and_check_earlier_exits_1_when_a_refactor_moved_its_assertions_into_assert_refused_and_deleted_the_call_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    def chk(m):
        return ASSERT_REFUSED_CHECK % m
    moved = ('func assertRefused(t *testing.T, v string) {\n' + chk("a") + chk("b") + '}\n\n'
             'func TestOne(t *testing.T) {\n\tv := "x"\n\t_ = v\n}\n')
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, ASSERT_REFUSED_INLINE, moved)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "suite_test.go TestOne"), checked) == (1, 1, 1)


def test_rerecord_refactored_exits_3_and_check_earlier_exits_1_when_a_refactor_moved_a_go_cases_assertions_into_assert_refused_and_the_verdict_is_not_0_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    def chk(m):
        return ASSERT_REFUSED_CHECK % m
    moved = ('func assertRefused(t *testing.T, v string) {\n' + chk("a") + chk("b") + '}\n\n'
             'func TestOne(t *testing.T) {\n\tv := "x"\n\tassertRefused(t, v)\n}\n')
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, ASSERT_REFUSED_INLINE, moved)
    (tmp_path / VERDICT).write_text("1")

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, checked) == (3, 1)


def test_rerecord_refactored_re_records_a_go_case_without_a_skipped_line_and_check_earlier_exits_0_when_a_refactor_moved_its_assertions_into_assert_refused_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    def chk(m):
        return ASSERT_REFUSED_CHECK % m
    moved = ('func assertRefused(t *testing.T, v string) {\n' + chk("a") + chk("b") + '}\n\n'
             'func TestOne(t *testing.T) {\n\tv := "x"\n\tassertRefused(t, "x")\n}\n')
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, ASSERT_REFUSED_INLINE, moved)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "suite_test.go TestOne"), checked) == (0, 0, 0)


def test_rerecord_refactored_leaves_check_earlier_at_exit_1_when_an_assertion_is_deleted_from_assert_refused_after_a_successful_re_record_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    def chk(m):
        return ASSERT_REFUSED_CHECK % m
    case = 'func TestOne(t *testing.T) {\n\tv := "x"\n\tassertRefused(t, "x")\n}\n'
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, ASSERT_REFUSED_INLINE,
                           'func assertRefused(t *testing.T, v string) {\n' + chk("a") + chk("b") + '}\n\n' + case)
    first = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    suite.write_text('func assertRefused(t *testing.T, v string) {\n' + chk("a") + '}\n\n' + case)
    repo.commit("A refactor drops an assertion from the helper", all=True)

    second = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (first[0], _skip_lines(first[2], "suite_test.go TestOne"), second[0], checked) == (
        0, 0, 1, 1)


def test_rerecord_refactored_re_records_a_python_case_without_a_skipped_line_and_check_earlier_exits_0_when_a_refactor_moved_its_assert_into_assert_refused_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    suite = tmp_path / ROOT_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("class TestSuite:\n    def test_one(self):\n        x = 1\n        assert x == 1\n")
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text("class TestSuite:\n    def test_one(self):\n        x = 1\n        assert_refused(x)\n\n\ndef assert_refused(x):\n    assert x == 1\n")
    repo.commit("A refactor moves the assert into assert_refused", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (0, 0, 0)


GO_X = "func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n"


def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_deleted_its_t_fatal_line_without_moving_it_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, GO_X,
                           "func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t}\n}\n")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


def test_rerecord_refactored_leaves_a_go_cases_record_when_its_t_fatal_lines_moved_into_another_test_function_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, GO_X,
                           "func TestShared(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                           "func TestX(t *testing.T) {\n\tx := 1\n\tTestShared(t, x)\n}\n")

    run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


def _record_of(tmp_path):
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    return record


def _body_line_reads(record, digest):
    record.write_text("".join(
        "body: suite_test.go\tTestX\t%s\n" % digest if line.startswith("body: ") else line
        for line in record.read_text().splitlines(keepends=True)))


def test_rerecord_refactored_skips_a_go_case_whose_body_record_digest_is_neither_greens_nor_heads_and_leaves_its_record_untouched_2973(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite = tmp_path / GO_SUITE
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    recorded = ("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")

    def foreign_digest():
        record = _record_of(tmp_path)
        _body_line_reads(record, "f" * 64)
        with record.open("a") as handle:
            handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
                suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))

    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, recorded, recorded.replace("x := 1", "x := 1 // one"),
                           edit_record=foreign_digest)
    record = _record_of(tmp_path)
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (b"\nhelpers: " in before, code, _skip_lines(err, "suite_test.go TestX"),
            record.read_bytes() == before) == (True, 1, 1, True)


def test_rerecord_refactored_names_the_body_digest_guard_in_parentheses_on_the_skipped_line_of_a_case_whose_body_digest_is_neither_greens_nor_heads_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, GO_X, GO_X.replace("x := 1", "x := 1 // one"),
                           edit_record=lambda: _body_line_reads(_record_of(tmp_path), "f" * 64))

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    lines = [line for line in err.splitlines() if line.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [line.startswith("skipped: suite_test.go TestX (") and line.endswith(")")
                               and len(line) > len("skipped: suite_test.go TestX ()") for line in lines]) == (
        1, 1, [True])


def test_rerecord_refactored_names_the_assertionless_shape_guard_in_parentheses_on_the_skipped_line_of_a_case_with_no_assertion_lines_whose_body_changed_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    green = _go_refactored(tmp_path, run_cli, tests_frozen, repo, "func TestX(t *testing.T) {\n\tx := 1\n}\n",
                           "func TestX(t *testing.T) {\n\tx := 2\n}\n")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    lines = [line for line in err.splitlines() if line.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [line.startswith("skipped: suite_test.go TestX (") and line.endswith(")")
                               and len(line) > len("skipped: suite_test.go TestX ()") for line in lines]) == (
        1, 1, [True])


def test_rerecord_refactored_exits_0_having_skipped_a_case_whose_record_is_already_at_heads_body_3051(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), TWO_ASSERTS % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("    assert x > 0\n", ""))
    repo.commit("A refactor", all=True)
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (0, 1, (0, ""))


def test_rerecord_refactored_exits_1_naming_a_case_whose_assertion_line_the_refactor_removed_and_check_earlier_still_refuses_3051(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), TWO_ASSERTS % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("    assert x > 0\n", ""))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (1, 1, 1), err


def test_rerecord_refactored_exits_2_not_1_when_check_earlier_cannot_obtain_an_answer_after_the_re_record_3051(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    _ledger(tmp_path, A="done")
    green = repo.commit("A green", all=True)
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")
    monkeypatch.setattr(tests_frozen, "_check_earlier", lambda ledger, step, exempt=(), sanctioned=(): 2)
    monkeypatch.chdir(tmp_path)

    assert tests_frozen.rerecord_refactored(PLAN_LEDGER, green) == 2


def _step_a_red(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    """The plan repository with step A's red recorded over BODY % ("one", 1), not committed yet; returns the log."""
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    return repo


def test_rerecord_refactored_re_records_a_case_a_later_suite_repair_green_rewrote_with_the_same_assertion_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _step_a_red(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    repo.commit("A red", all=True)
    repair = STEPS[2] + " ⟦suite-repair⟧"
    (tmp_path / PLAN_LEDGER).write_text("- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, repair))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    green = repo.commit("B green", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", "step C"], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (0, 0, (0, ""))


def test_rerecord_refactored_suite_repair_guard_skips_a_ledgers_header_and_blank_lines_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _step_a_red(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    repo.commit("A red", all=True)
    repair = STEPS[2] + " ⟦suite-repair⟧"
    (tmp_path / PLAN_LEDGER).write_text(
        "# Plan\n\n- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, repair))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    green = repo.commit("B green", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", "step C"], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (0, 0, (0, ""))


def test_rerecord_refactored_still_refuses_a_case_an_ordinary_green_rewrote_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _step_a_red(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    repo.commit("A red", all=True)
    (tmp_path / PLAN_LEDGER).write_text("- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, STEPS[2]))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    green = repo.commit("B green", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (1, 1)


def test_rerecord_refactored_refuses_a_case_an_ordinary_green_rewrote_while_an_unrelated_earlier_suite_repair_step_is_ticked_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repair = STEPS[0] + " ⟦suite-repair⟧"
    repo = _step_a_red(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    (tmp_path / PLAN_LEDGER).write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (repair, step, STEPS[2]))
    repo.commit("A red, the suite-repair step ticked", all=True)
    (tmp_path / PLAN_LEDGER).write_text("- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (repair, step, STEPS[2]))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    green = repo.commit("B ordinary green", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (1, 1)


def test_rerecord_refactored_refuses_a_case_the_green_of_an_unticked_suite_repair_step_rewrote_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _step_a_red(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    repair = STEPS[2] + " ⟦suite-repair⟧"
    (tmp_path / PLAN_LEDGER).write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (STEPS[0], step, repair))
    repo.commit("A red, the suite-repair step listed but not ticked", all=True)
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    green = repo.commit("B green of the unticked step, the ledger untouched", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (1, 1)


def _repair_green_fixture(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, committed_repair):
    """The ledger passed to rerecord-refactored ticks a suite-repair step 3 whose green rewrote step A's case; the
    committed ledger holds that line only when `committed_repair`. Returns (fed log, green revision)."""
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _step_a_red(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    repo.commit("A red", all=True)
    repair = STEPS[2] + " ⟦suite-repair⟧"
    ticked = "# Plan\n\n- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, repair)
    if committed_repair:
        (tmp_path / PLAN_LEDGER).write_text(ticked)
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    green = repo.commit("B green", all=True)
    (tmp_path / PLAN_LEDGER).write_text(ticked)
    (tmp_path / VERDICT).write_text("0")
    return repo, green


def test_rerecord_refactored_refuses_a_green_when_the_committed_ledger_never_held_the_suite_repair_line_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    _, green = _repair_green_fixture(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, False)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (1, 1)


def test_rerecord_refactored_skips_an_unmapped_suite_repair_line_and_accepts_a_later_valid_one_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _step_a_red(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    repo.commit("A red", all=True)
    repair = STEPS[2] + " ⟦suite-repair⟧"
    (tmp_path / PLAN_LEDGER).write_text("- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, repair))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    green = repo.commit("B green", all=True)
    # A ticked suite-repair line the committed ledger never held, ahead of the valid one (uncommitted).
    (tmp_path / PLAN_LEDGER).write_text("- [x] ghost step ⟦suite-repair⟧\n" + (tmp_path / PLAN_LEDGER).read_text())
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (0, 0)


def test_rerecord_refactored_refuses_a_case_a_later_commit_rewrote_again_after_a_suite_repair_green_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo, green = _repair_green_fixture(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, True)
    suite = tmp_path / ROOT_SUITE
    suite.write_text(suite.read_text().replace("    assert x\n", "    assert x == 1\n"))
    repo.commit("C later rewrite that changes the assertion", all=True)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)
    kept = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", "step C"], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "test_suite.py test_one"), kept) == (1, 1, 1)


def test_rerecord_refactored_exits_0_for_a_case_a_later_replaces_case_step_names_in_a_pytest_suite_3624(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _step_a_red(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    repo.commit("A red", all=True)
    replacing = "step B reverses it, replaces 'test_one' in test_suite.py ⟦replaces-case⟧"
    (tmp_path / PLAN_LEDGER).write_text(
        "- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, replacing))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 7\n"))
    green = repo.commit("B green", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (0, 0)


def test_rerecord_refactored_exits_1_for_an_unnamed_case_a_green_rewrote_beside_a_case_a_replaces_case_step_names_3624(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    suite, step = tmp_path / ROOT_SUITE, STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, ROOT_SUITE], cwd=tmp_path)
    repo.commit("A red", all=True)
    replacing = "step B reverses it, replaces 'test_one' in test_suite.py ⟦replaces-case⟧"
    (tmp_path / PLAN_LEDGER).write_text(
        "- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, replacing))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 7\n").replace("x = 2\n", "x = 8\n"))
    green = repo.commit("B green", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one"), _skip_lines(err, "test_suite.py test_two")) == (1, 0, 1)


A_SUITE, B_SUITE = "test_a.py", "test_b.py"


def test_rerecord_refactored_exits_1_for_a_same_named_case_in_another_suite_than_the_replaces_case_marker_names_3624(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    step = STEPS[1]
    repo = _plan_repo(tmp_path, monkeypatch, fed_commits)
    for suite in (A_SUITE, B_SUITE):
        (tmp_path / suite).write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, A_SUITE, B_SUITE], cwd=tmp_path)
    repo.add(A_SUITE, B_SUITE)
    repo.commit("A red", all=True)
    replacing = "step B reverses it, replaces 'test_one' in test_a.py ⟦replaces-case⟧"
    (tmp_path / PLAN_LEDGER).write_text(
        "- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, replacing))
    for suite in (A_SUITE, B_SUITE):
        (tmp_path / suite).write_text((tmp_path / suite).read_text().replace("x = 1\n", "x = 7\n"))
    green = repo.commit("B green", all=True)
    (tmp_path / VERDICT).write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_a.py test_one"), _skip_lines(err, "test_b.py test_one")) == (1, 0, 1)


def test_rerecord_refactored_exit_0_leaves_no_check_earlier_pass_marker_it_did_not_find_4296(
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

    code = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]

    assert (code, sorted((tmp_path / ".tdd").glob("check-earlier-*.pass"))) == (0, [])
