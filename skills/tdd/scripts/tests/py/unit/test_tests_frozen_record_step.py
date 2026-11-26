"""In-process `record --step` cases for veri/tests_frozen.py, on a case history fed by fed_history (PRD 017.5)."""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# Names, not literals, in calls: a literal suite path reads as a nested run.
PY_SUITE = "tests/test_suite.py"
NEW, HELPER = "tests/test_new.py", "tests/helper.test.sh"


@pytest.fixture
def committed_once(tmp_path, fed_history):
    """One commit ("base") holding `files`; the work tree is tmp_path, written with the same files."""
    def commit(files):
        (tmp_path / ".tdd").mkdir()
        for name, text in files.items():
            (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / name).write_text(text)
        fed_history(("base", "base", files), root=tmp_path)
    return commit


def recorded(run_cli, tests_frozen, tmp_path, step, name):
    """The record `record --step <step> <name>` writes, as text."""
    run_cli(tests_frozen, ["record", "--step", step, name], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    return (tmp_path / record_path.rstrip("\n")).read_text()


def test_record_step_holds_a_helper_test_file_red_changed_beside_its_test_path_so_check_step_exits_0_1733(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({NEW: "one\n", HELPER: "one\n"})
    step = "step one adds a case"
    (tmp_path / NEW).write_text("one\ntwo\n")
    (tmp_path / HELPER).write_text("one\nred's helper\n")
    run_cli(tests_frozen, ["record", "--step", step, NEW], cwd=tmp_path)

    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_record_step_lists_by_name_the_pytest_function_red_added_to_a_test_file_1765(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "def test_older_case():\n    assert True\n"})
    step = "step one adds a case"
    (tmp_path / PY_SUITE).write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_added_by_red_1765():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert "test_added_by_red_1765" in record


def test_record_step_lists_by_name_the_pytest_function_red_edited_and_not_the_one_it_left_alone_1765(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "def test_edited_by_red_1765():\n    assert 1 == 2\n\n\n"
                              "def test_left_alone_1765():\n    assert True\n"})
    step = "step one edits a case"
    (tmp_path / PY_SUITE).write_text("def test_edited_by_red_1765():\n    assert 1 == 1\n\n\n"
                                     "def test_left_alone_1765():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_edited_by_red_1765\n" in record, "test_left_alone_1765" in record) == (True, False)


def test_record_step_lists_only_the_pytest_function_red_inserted_at_file_start_above_an_older_one_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "\ndef test_older_case_1861():\n    assert True\n"})
    step = "step one inserts a case above the older one"
    (tmp_path / PY_SUITE).write_text("def test_inserted_by_red_1861():\n    assert True\n\n\n"
                                     "def test_older_case_1861():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_pytest_function_red_inserted_above_an_older_one_that_had_one_blank_line_above_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "LIMIT = 1\n\ndef test_older_case_1861():\n    assert True\n"})
    step = "step one inserts a case above the older one"
    (tmp_path / PY_SUITE).write_text("LIMIT = 1\n\n\ndef test_inserted_by_red_1861():\n    assert True\n\n\n"
                                     "def test_older_case_1861():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_pytest_method_red_inserted_above_an_older_method_in_a_class_and_a_wrong_test_naming_the_older_one_routes_red_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "import pytest\n\n\nclass TestSuite:\n    def test_first_1861(self):\n        assert True\n\n"
                              "    def test_older_case_1861(self):\n        assert True\n"})
    step = "step one inserts a method above the older one"
    (tmp_path / PY_SUITE).write_text(
        "import pytest\n\n\nclass TestSuite:\n    def test_first_1861(self):\n        assert True\n\n"
        "    def test_inserted_by_red_1861(self):\n        assert True\n\n"
        "    def test_older_case_1861(self):\n        assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_pytest_function_red_appended_after_an_older_one_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "def test_older_case_1861():\n    assert True\n"})
    step = "step one appends a case after the older one"
    (tmp_path / PY_SUITE).write_text("def test_older_case_1861():\n    assert True\n\n\n"
                                     "def test_appended_by_red_1861():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_appended_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_pytest_function_red_inserted_above_an_older_one_on_the_files_first_line_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "def test_older_case_1861():\n    assert True\n"})
    step = "step one inserts a case above the one on line one"
    (tmp_path / PY_SUITE).write_text("def test_inserted_by_red_1861():\n    assert True\n\n\n"
                                     "def test_older_case_1861():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_pytest_method_red_inserted_above_an_older_method_directly_under_its_class_line_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "class TestSuite:\n    def test_older_case_1861(self):\n        assert True\n"})
    step = "step one inserts a method under the class line"
    (tmp_path / PY_SUITE).write_text("class TestSuite:\n    def test_inserted_by_red_1861(self):\n        assert True\n\n"
                                     "    def test_older_case_1861(self):\n        assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_run_outside_any_git_repository_exits_2_with_stderr_naming_the_missing_repository_and_writes_no_record_1960(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / NEW).write_text("one\n")
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: None)
    step = "step one adds a case"

    code, out, err = run_cli(tests_frozen, ["record", "--step", step, NEW], cwd=tmp_path)

    assert (code, out, "repository" in err,
            [p.name for p in (tmp_path / ".tdd").iterdir() if p.name != "events.jsonl"]) == (2, "", True, [])


def test_record_step_for_a_red_whose_only_test_change_deletes_a_tracked_test_file_records_the_deletion_and_exits_0_1960(
        tmp_path, run_cli, tests_frozen, committed_once):
    old = "tests/test_old.py"
    committed_once({old: "one\n"})
    step = "step one deletes a test file"
    (tmp_path / old).unlink()

    code, out, _ = run_cli(tests_frozen, ["record", "--step", step], cwd=tmp_path)

    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = tmp_path / record_path.strip()
    assert (code, out, record.read_text() if record.exists() else None) == (0, "", "deleted  %s\n" % old)


def test_record_step_lists_the_pytest_function_red_edited_below_a_finish_line_inside_its_multiline_string_1773(
        tmp_path, run_cli, tests_frozen, committed_once):
    body = ('def test_first():\n    assert True\n\n\n'
            'def test_last():\n    text = """\nfinish\n"""\n    assert text == {!r}\n')
    committed_once({PY_SUITE: body.format("one")})
    step = "step one edits a function below a string finish"
    (tmp_path / PY_SUITE).write_text(body.format("two"))

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert [line for line in record.splitlines() if line.startswith("case: ")] == ["case: test_last"]


def test_record_step_again_for_a_case_committed_unchanged_keeps_its_body_entry_at_the_current_digest_2199(
        tmp_path, run_cli, tests_frozen, fed_history, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests").mkdir()
    step = "step one adds a case"
    monkeypatch.setenv("VERI_ISSUE", "9")
    base = {NEW: "def test_one():\n    assert 1\n", ".tdd/issue-9.md": "- [ ] %s\n" % step}
    for path, text in base.items():
        (tmp_path / path).write_text(text)
    fed_history(("base", "base", base), root=tmp_path)
    (tmp_path / NEW).write_text("def test_one():\n    assert 1\n\n\ndef test_two():\n    assert 2\n")
    run_cli(tests_frozen, ["record", "--step", step, NEW], cwd=tmp_path)
    fed_history(("base", "base", base), ("red", "red", {NEW: (tmp_path / NEW).read_text()}), root=tmp_path)
    record = tmp_path / run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()
    first = [l for l in record.read_text().splitlines() if l.startswith("body: ")]

    code, _, err = run_cli(tests_frozen, ["record", "--step", step, NEW], cwd=tmp_path)

    again = [l for l in record.read_text().splitlines() if l.startswith("body: ")]
    assert (code, len(first), again) == (0, 1, first), err


STEPS = ["step Z adds an early case", "step A adds the cases", "step B adds a later case"]
CASE = "def test_%s():\n    assert %d\n"
SUITE, LEDGER, OTHER_LEDGER = "test_suite.py", ".tdd/issue-9.md", ".tdd/issue-8.md"


def _ledger(root, **state):
    """The ledger in its real shapes: open, pending (ticked, ledger.PENDING_MARK appended) and done."""
    marks = {"open": "- [ ] %s", "pending": "- [x] %s ⟂ refactor pending", "done": "- [x] %s"}
    (root / LEDGER).write_text("".join(
        marks[state.get(name, "open")] % text + "\n" for name, text in zip("ZAB", STEPS, strict=True)))


@pytest.fixture
def plan_repo(tmp_path, fed_history, monkeypatch):
    """Issue 9's branch after its plan commit; `plan_repo(name)` commits the suite and both ledgers as they stand
    in tmp_path, one fed revision each (names carry no whitespace: case_history splits revision lists on it)."""
    monkeypatch.setenv("VERI_ISSUE", "9")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / SUITE).write_text(CASE % ("base", 0))
    _ledger(tmp_path)
    (tmp_path / OTHER_LEDGER).write_text("- [x] %s\n" % STEPS[1])
    revisions = []

    def commit(name):
        revisions.append((name, name, {path: (tmp_path / path).read_text() for path in (SUITE, LEDGER, OTHER_LEDGER)}))
        fed_history(*revisions, root=tmp_path)
    commit("plan")
    return commit


def _names(root, tests_frozen, step):
    record = (root / tests_frozen.record_path(step)).read_text()
    return sorted(l[6:] for l in record.splitlines() if l.startswith("case: "))


def test_rerecord_on_head_keeps_a_pin_and_rename_committed_in_green_and_a_successor_a_later_step_renamed_2673(
        tmp_path, run_cli, tests_frozen, plan_repo):
    suite, step = tmp_path / SUITE, STEPS[1]
    suite.write_text("\n\n".join([CASE % ("base", 0), CASE % ("rejects_a_body_that_is_not_valid_json", 3),
                                  CASE % ("one", 1), CASE % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)
    plan_repo("A-red")
    suite.write_text(suite.read_text().replace("rejects_a_body", "rejects_to_a_body"))
    plan_repo("A-renames-in-green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_committed", 5))
    _ledger(tmp_path, A="pending")
    plan_repo("A-green")
    _ledger(tmp_path, A="done")
    plan_repo("A-refactor-verified")
    suite.write_text(suite.read_text().replace("test_one", "test_one_renamed") + "\n\n" + CASE % ("later_step", 9))
    _ledger(tmp_path, A="done", B="pending")
    plan_repo("B-green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_wip", 4))

    code = run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, step)) == (
        0, ["test_one_renamed", "test_pin_committed", "test_pin_wip", "test_rejects_to_a_body_that_is_not_valid_json",
            "test_two"])


def test_rerecord_on_head_mid_step_keeps_a_case_the_current_unticked_step_committed_not_an_earlier_steps_2673(
        tmp_path, run_cli, tests_frozen, plan_repo):
    suite, step = tmp_path / SUITE, STEPS[1]
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("early", 7))
    _ledger(tmp_path, Z="pending")
    plan_repo("Z-green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("one", 1))
    run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)
    plan_repo("A-red")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_committed", 5))
    plan_repo("A-pin-not-ticked-yet")

    code = run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, step)) == (0, ["test_one", "test_pin_committed"])


def test_rerecord_on_head_exits_2_naming_the_step_when_no_committed_ledger_line_of_it_is_found_2673(
        tmp_path, run_cli, tests_frozen, plan_repo):
    suite, step = tmp_path / SUITE, "step C that no ledger names"
    suite.write_text(CASE % ("base", 0) + "\n\n" + CASE % ("one", 1))
    run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)
    before = (tmp_path / tests_frozen.record_path(step)).read_text()
    plan_repo("one")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 2))
    plan_repo("later")

    code, _, err = run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)

    assert (code, step in err, (tmp_path / tests_frozen.record_path(step)).read_text()) == (2, True, before)


PHASED_STEP = STEPS[1] + " ⟦phases: expand, migrate⟧"


def _phased_ledger(root, marks="", **state):
    """The ledger with step A listing its phases: its box stays open whatever `⟂ <phase> done` marks it gains."""
    _ledger(root, **state)
    ledger = root / LEDGER
    ledger.write_text(ledger.read_text().replace(STEPS[1], PHASED_STEP + marks))


def test_rerecord_on_head_keeps_the_pins_and_renames_of_a_step_whose_ledger_line_went_through_phase_marks_2724(
        tmp_path, run_cli, tests_frozen, plan_repo):
    suite = tmp_path / SUITE
    expand, migrate = " ⟂ expand done", " ⟂ expand done ⟂ migrate done"
    _phased_ledger(tmp_path)
    plan_repo("plan-the-phases")
    suite.write_text("\n\n".join([CASE % ("base", 0), CASE % ("one", 1), CASE % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", PHASED_STEP, SUITE], cwd=tmp_path)
    _phased_ledger(tmp_path, expand)
    plan_repo("A-expand")
    suite.write_text(suite.read_text().replace("test_one", "test_one_renamed") + "\n\n" + CASE % ("pin_committed", 5))
    _phased_ledger(tmp_path, migrate)
    plan_repo("A-migrate")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later_step", 9))
    _phased_ledger(tmp_path, migrate, B="pending")
    plan_repo("B-green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_wip", 4))

    code = run_cli(tests_frozen, ["record", "--step", PHASED_STEP, SUITE], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, PHASED_STEP)) == (
        0, ["test_one_renamed", "test_pin_committed", "test_pin_wip", "test_two"])


REPAIR_STEP = "repairs the fixture 'f' in test_suite.py, reproduced by a case ⟦fixture-repair⟧"


def _repair_ledger(root, **state):
    _ledger(root, **state)
    ledger = root / LEDGER
    ledger.write_text(ledger.read_text().replace(STEPS[1], REPAIR_STEP))


def test_rerecord_on_head_keeps_the_pins_and_renames_of_a_fixture_repair_step_whose_ledger_line_ends_in_the_marker_2724(
        tmp_path, run_cli, tests_frozen, plan_repo):
    suite = tmp_path / SUITE
    _repair_ledger(tmp_path)
    plan_repo("plan-the-repair")
    suite.write_text("\n\n".join([CASE % ("base", 0), CASE % ("one", 1), CASE % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", REPAIR_STEP, SUITE], cwd=tmp_path)
    suite.write_text(suite.read_text().replace("test_one", "test_one_renamed") + "\n\n" + CASE % ("pin_committed", 5))
    _repair_ledger(tmp_path, A="pending")
    plan_repo("A-green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later_step", 9))
    _repair_ledger(tmp_path, A="pending", B="pending")
    plan_repo("B-green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_wip", 4))

    code = run_cli(tests_frozen, ["record", "--step", REPAIR_STEP, SUITE], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, REPAIR_STEP)) == (
        0, ["test_one_renamed", "test_pin_committed", "test_pin_wip", "test_two"])


def test_rerecord_on_head_keeps_a_case_the_steps_own_refactor_commit_renamed_before_the_next_step_began_2724(
        tmp_path, run_cli, tests_frozen, plan_repo):
    suite, step = tmp_path / SUITE, STEPS[1]
    suite.write_text("\n\n".join([CASE % ("base", 0), CASE % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_committed", 5))
    _ledger(tmp_path, A="pending")
    plan_repo("A-green")
    suite.write_text(suite.read_text().replace("pin_committed", "pin_tidied"))
    plan_repo("A-refactor-renames-the-pin")
    _ledger(tmp_path, A="done")
    plan_repo("A-refactor-verified")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later_step", 9))
    _ledger(tmp_path, A="done", B="pending")
    plan_repo("B-green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_wip", 4))

    code = run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, step)) == (0, ["test_one", "test_pin_tidied", "test_pin_wip"])


GUARD, GUARD_MORE = "tests/test_guard.py", "tests/test_guard_more.py"


def test_record_step_freezes_only_the_red_case_of_each_of_two_prefix_sharing_guard_subjects_3443(
        tmp_path, run_cli, tests_frozen, committed_once, monkeypatch):
    committed_once({GUARD: "def test_guarded_one():\n    assert True, 'a'\n",
                    GUARD_MORE: "def test_guarded_two():\n    assert True, 'a'\n"})
    monkeypatch.setattr(tests_frozen, "work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "write_pass_marker", lambda step, tree: None)
    earlier, current = "step one ⟦guard-subject: %s⟧ ⟦guard-subject: %s⟧" % (GUARD, GUARD_MORE), "step two"
    (tmp_path / GUARD).write_text(
        "def test_guarded_one():\n    assert True, 'b'\n\n\ndef test_red_one_3443():\n    assert 1 == 2\n")
    (tmp_path / GUARD_MORE).write_text(
        "def test_guarded_two():\n    assert True, 'b'\n\n\ndef test_red_two_3443():\n    assert 1 == 3\n")
    run_cli(tests_frozen, ["record", "--step", earlier, GUARD], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / GUARD).write_text(
        "def test_guarded_one():\n    assert True, 'c'\n\n\ndef test_red_one_3443():\n    assert 1 == 2\n")
    (tmp_path / GUARD_MORE).write_text(
        "def test_guarded_two():\n    assert True, 'c'\n\n\ndef test_red_two_3443():\n    assert 1 == 3\n")
    argv = ["check-earlier", str(ledger), "--step", current]

    guarded_changed = run_cli(tests_frozen, argv, cwd=tmp_path)
    (tmp_path / GUARD).write_text(
        "def test_guarded_one():\n    assert True, 'c'\n\n\ndef test_red_one_3443():\n    assert True\n")
    (tmp_path / GUARD_MORE).write_text(
        "def test_guarded_two():\n    assert True, 'c'\n\n\ndef test_red_two_3443():\n    assert True\n")
    red_changed = run_cli(tests_frozen, argv, cwd=tmp_path)

    assert [guarded_changed[:2], (red_changed[0], sorted(red_changed[1].splitlines()))] == [
        (0, ""), (1, ["test_red_one_3443 (%s)" % earlier, "test_red_two_3443 (%s)" % earlier])]
