"""In-process cases for veri/suite_red_resume.py, the module suite-red-resume.sh is a shim over."""
import importlib
import json


def test_check_lets_a_resume_after_a_suite_red_bail_go_on_unless_a_suite_is_red_on_the_default_branch_too_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    events = [{"ts": 1, "issue": "7", "event": "bail", "cause": "suite-red", "phase": ""}]
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\ntest_b.py\n")
    default = tmp_path / "default-red"
    default.write_text("test_c.py — FAIL c\n")
    overlap = tmp_path / "default-overlap"
    overlap.write_text("test_b.py — FAIL other text\n")

    clean = run_cli(module, ["check", str(ledger), str(branch), str(default)])
    shared = run_cli(module, ["check", str(ledger), str(branch), str(overlap)])

    assert clean == (0, "test_a.py — FAIL a\ntest_b.py\n", "")
    assert shared[0] == 1 and "test_b.py" in shared[2] and "test_a.py" not in shared[2]


def test_check_exits_2_on_bad_usage_or_an_unreadable_file_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\n")
    default = tmp_path / "default-red"
    default.write_text("none\n")
    events = tmp_path / "events.jsonl"

    events.write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    unreadable = run_cli(module, ["check", str(ledger), str(tmp_path / "missing"), str(default)])
    no_args = run_cli(module, [])
    default.write_text("")
    empty_default = run_cli(module, ["check", str(ledger), str(branch), str(default)])
    missing_default = run_cli(module, ["check", str(ledger), str(branch), str(tmp_path / "no-default")])
    default.write_text("none\n")
    none_default = run_cli(module, ["check", str(ledger), str(branch), str(default)])

    assert empty_default[0] == 2 and empty_default[1] == "" and str(default) in empty_default[2]
    assert missing_default[0] == 2 and missing_default[1] == "" and str(tmp_path / "no-default") in missing_default[2]
    assert none_default == (0, "test_a.py — FAIL a\n", "")
    assert unreadable[0] == 2 and unreadable[1] == ""
    assert no_args[0] == 2 and "usage" in no_args[2]


def test_check_names_an_unreadable_branch_red_file_and_exits_2_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\n")
    default = tmp_path / "default-red"
    default.write_text("none\n")

    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    unreadable = run_cli(module, ["check", str(ledger), str(tmp_path / "missing"), str(default)])

    assert unreadable[0] == 2 and unreadable[1] == "" and str(tmp_path / "missing") in unreadable[2]

def test_insert_adds_one_suite_repair_step_before_the_first_unchecked_step_through_add_ledger_step_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 2⟧\n- [ ] c ⟦criterion 3⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\ntest_b.py\n")
    step = "- [ ] fix the full-suite failure: test_a.py — FAIL a; test_b.py ⟦suite-repair⟧ ⟦criterion 2⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert ledger.read_text().split("\n")[2:6] == ["- [x] a ⟦criterion 1⟧", step, "- [ ] b ⟦criterion 2⟧", "- [ ] c ⟦criterion 3⟧"]
    assert (tmp_path / "issue-7-added.md").read_text() == step + "\n"
    logged = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert [e["step"] for e in logged if e["event"] == "step-added"] == [step]


def test_insert_with_no_unchecked_step_adds_the_suite_repair_step_after_the_last_done_step_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [x] b ⟦criterion 2⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py\n")
    step = "- [ ] fix the full-suite failure: test_a.py ⟦suite-repair⟧ ⟦criterion 2⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert ledger.read_text().split("\n")[2:5] == ["- [x] a ⟦criterion 1⟧", "- [x] b ⟦criterion 2⟧", step]
    assert (tmp_path / "issue-7-added.md").read_text() == step + "\n"
    logged = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert [e["step"] for e in logged if e["event"] == "step-added"] == [step]


def test_check_on_an_empty_branch_red_file_exits_2_naming_that_file_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("")
    default = tmp_path / "default-red"
    default.write_text("test_c.py — FAIL c\n")

    code, out, err = run_cli(module, ["check", str(ledger), str(branch), str(default)])

    assert (code, out) == (2, "")
    assert str(branch) in err


def test_insert_on_an_empty_or_unreadable_branch_red_file_exits_2_naming_it_and_adds_no_step_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 2⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    (tmp_path / "issue-7-added.md").write_text("- [ ] earlier ⟦suite-repair⟧\n")
    before = (ledger.read_bytes(), (tmp_path / "issue-7-added.md").read_bytes())
    empty = tmp_path / "branch-red"
    empty.write_text("")
    missing = tmp_path / "no-such-branch-red"

    for branch in (empty, missing):
        code, _, err = run_cli(module, ["insert", str(ledger), str(branch)])

        assert code == 2
        assert str(branch) in err
        assert (ledger.read_bytes(), (tmp_path / "issue-7-added.md").read_bytes()) == before


def test_check_with_an_empty_branch_red_file_and_an_unreadable_default_red_file_exits_2_naming_the_branch_file_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("")
    missing = tmp_path / "no-such-default-red"

    code, out, err = run_cli(module, ["check", str(ledger), str(branch), str(missing)])

    assert (code, out) == (2, "")
    assert str(branch) in err
    assert str(missing) not in err


def test_check_on_an_empty_or_unreadable_default_red_file_exits_2_naming_it_while_none_means_no_suite_red_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\n")
    empty = tmp_path / "default-empty"
    empty.write_text("")
    none = tmp_path / "default-none"
    none.write_text("none\n")
    missing = tmp_path / "no-such-default-red"

    for default in (empty, missing):
        code, out, err = run_cli(module, ["check", str(ledger), str(branch), str(default)])

        assert (code, out) == (2, "")
        assert str(default) in err
    assert run_cli(module, ["check", str(ledger), str(branch), str(none)]) == (0, "test_a.py — FAIL a\n", "")


def test_usage_names_the_insert_verb_beside_check_on_stderr_with_exit_2_for_no_arguments_or_an_unknown_verb_2226(run_cli):
    module = importlib.import_module("veri.suite_red_resume")

    for argv in ([], ["bogus", "a", "b"]):
        code, out, err = run_cli(module, argv)

        assert (code, out) == (2, "")
        assert "suite-red-resume.sh check <ledger-file> <branch-red-file> <default-red-file>" in err
        assert "suite-red-resume.sh insert <ledger-file> <branch-red-file>" in err


def test_check_goes_on_whatever_the_last_bail_was_when_every_branch_red_suite_is_green_on_the_default_branch_2470(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\n")
    default = tmp_path / "default-red"
    default.write_text("test_c.py — FAIL c\n")
    outcomes = {}
    for name, events in {
        "revise-exhausted": [{"ts": 1, "issue": "7", "event": "bail", "cause": "revise-exhausted", "phase": ""}],
        "no-bail": [{"ts": 1, "issue": "7", "event": "start"}],
        "no-log": None,
    }.items():
        run = tmp_path / name
        run.mkdir()
        ledger = run / "issue-7-ledger.md"
        ledger.write_text("- [ ] step\n")
        if events is not None:
            (run / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
        outcomes[name] = run_cli(module, ["check", str(ledger), str(branch), str(default)])

    assert outcomes == {name: (0, "test_a.py — FAIL a\n", "") for name in outcomes}


def test_check_still_refuses_naming_each_suite_red_on_the_default_branch_too_after_a_revise_exhausted_bail_2470(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    events = [{"ts": 1, "issue": "7", "event": "bail", "cause": "revise-exhausted", "phase": ""}]
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\ntest_b.py\ntest_d.py\n")
    default = tmp_path / "default-red"
    default.write_text("test_b.py — FAIL b\ntest_d.py — FAIL d\n")

    code, out, err = run_cli(module, ["check", str(ledger), str(branch), str(default)])

    assert (code, out) == (1, "")
    assert "test_b.py" in err and "test_d.py" in err and "test_a.py" not in err


def test_flake_at_resume_writes_one_suite_flake_event_naming_each_red_file_and_exits_0_2906(run_cli, events, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    (tmp_path / ".git").mkdir()
    red = tmp_path / "red"
    red.write_text("backend/a.test.ts — FAIL a\nscripts/b.test.mjs\n")
    alone = tmp_path / "alone-red"
    alone.write_text("none\n")

    code, _, _ = run_cli(module, ["flake", "resume", str(red), str(alone)], cwd=tmp_path)

    flakes = [e for e in events.records(tmp_path) if e["event"] == "suite-flake"]
    assert code == 0 and len(flakes) == 1
    assert "at=resume" in flakes[0].values() or flakes[0].get("at") == "resume"
    assert "backend/a.test.ts" in json.dumps(flakes[0]) and "scripts/b.test.mjs" in json.dumps(flakes[0])


def test_flake_at_suite_repair_writes_one_suite_flake_event_carrying_that_call_site_and_naming_each_red_file_2906(run_cli, events, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    (tmp_path / ".git").mkdir()
    red = tmp_path / "red"
    red.write_text("src/c.test.tsx — FAIL c\nscripts/d.test.mjs\n")
    alone = tmp_path / "alone-red"
    alone.write_text("none\n")

    code, _, _ = run_cli(module, ["flake", "suite-repair", str(red), str(alone)], cwd=tmp_path)

    flakes = [e for e in events.records(tmp_path) if e["event"] == "suite-flake"]
    assert code == 0 and len(flakes) == 1
    assert "at=suite-repair" in flakes[0].values() or flakes[0].get("at") == "suite-repair"
    assert "src/c.test.tsx" in json.dumps(flakes[0]) and "scripts/d.test.mjs" in json.dumps(flakes[0])


def test_flake_with_a_file_still_red_alone_exits_1_names_it_on_stderr_and_writes_no_event_2906(run_cli, events, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    (tmp_path / ".git").mkdir()
    red = tmp_path / "red"
    red.write_text("backend/a.test.ts — FAIL a\nscripts/b.test.mjs\n")
    alone = tmp_path / "alone-red"
    alone.write_text("scripts/b.test.mjs\n")

    code, _, err = run_cli(module, ["flake", "resume", str(red), str(alone)], cwd=tmp_path)

    flakes = [e for e in events.records(tmp_path) if e["event"] == "suite-flake"]
    assert code == 1 and flakes == []
    assert "scripts/b.test.mjs" in err and "backend/a.test.ts" not in err


def test_flake_with_a_red_file_naming_no_test_file_exits_1_and_writes_no_event_2906(run_cli, events, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    (tmp_path / ".git").mkdir()
    red = tmp_path / "red"
    red.write_text("")
    alone = tmp_path / "alone-red"
    alone.write_text("none\n")

    code, _, _ = run_cli(module, ["flake", "resume", str(red), str(alone)], cwd=tmp_path)

    flakes = [e for e in events.records(tmp_path) if e["event"] == "suite-flake"]
    assert code == 1 and flakes == []


def test_insert_adds_no_suite_repair_step_when_the_red_is_only_a_stale_grade_of_the_unit_the_first_unchecked_skill_edit_step_names_3004(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", unit)], []))
    ledger = tmp_path / "issue-7.md"
    text = f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] ⟦skill-edit⟧ regrade `{unit}` against SC48\n- [ ] c ⟦criterion 3⟧\n"
    ledger.write_text(text)
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_015_prose_signed.py\ntest_prd_016_short_names.py\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert "⟦suite-repair⟧" not in ledger.read_text()
    assert [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")][0] == f"- [ ] ⟦skill-edit⟧ regrade `{unit}` against SC48"


def test_insert_still_adds_the_suite_repair_step_before_the_skill_edit_step_when_a_branch_red_suite_is_red_for_another_reason_3004(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", unit)], []))
    ledger = tmp_path / "issue-7.md"
    skill_edit = f"- [ ] ⟦skill-edit⟧ regrade `{unit}` against SC48"
    ledger.write_text(f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n{skill_edit}\n- [ ] c ⟦criterion 3⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_015_prose_signed.py\ntest_unrelated_parser.py — FAIL parser broke\n")
    step = "- [ ] fix the full-suite failure: test_prd_015_prose_signed.py; test_unrelated_parser.py — FAIL parser broke ⟦suite-repair⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")][:2] == [step, skill_edit]


def test_insert_still_adds_the_suite_repair_step_when_the_stale_graded_unit_has_no_pending_skill_edit_step_3004(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", unit)], []))
    ledger = tmp_path / "issue-7.md"
    ledger.write_text(f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [x] ⟦skill-edit⟧ regrade `{unit}` against SC48\n- [ ] c ⟦criterion 3⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_015_prose_signed.py\ntest_prd_016_short_names.py\n")
    step = "- [ ] fix the full-suite failure: test_prd_015_prose_signed.py; test_prd_016_short_names.py ⟦suite-repair⟧ ⟦criterion 3⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")][0] == step


def test_insert_still_adds_the_suite_repair_step_when_the_first_unchecked_skill_edit_step_names_a_different_unit_3004(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    stale = "skills/tdd/SCRIPTS.md"
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", stale)], []))
    ledger = tmp_path / "issue-7.md"
    skill_edit = "- [ ] ⟦skill-edit⟧ regrade `skills/tdd/RESUME.md` against RS28"
    ledger.write_text(f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n{skill_edit}\n- [ ] c ⟦criterion 3⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_015_prose_signed.py\ntest_prd_016_short_names.py\n")
    step = "- [ ] fix the full-suite failure: test_prd_015_prose_signed.py; test_prd_016_short_names.py ⟦suite-repair⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")][:2] == [step, skill_edit]


def test_flake_with_the_wrong_argument_count_exits_2_and_its_usage_line_names_flake_2946(run_cli):
    module = importlib.import_module("veri.suite_red_resume")

    code, out, err = run_cli(module, ["flake", "only-one-arg"])

    assert (code, out) == (2, "")
    assert "suite-red-resume.sh flake" in err


def test_usage_names_flake_beside_check_and_insert_each_with_its_arguments_for_a_no_argument_call_2946(run_cli):
    module = importlib.import_module("veri.suite_red_resume")

    code, out, err = run_cli(module, [])

    assert (code, out) == (2, "")
    assert "suite-red-resume.sh check <ledger-file> <branch-red-file> <default-red-file>" in err
    assert "suite-red-resume.sh insert <ledger-file> <branch-red-file>" in err
    assert "suite-red-resume.sh flake <at> <red-file> <alone-red-file>" in err
    assert "suite-red-resume.sh rebased-tip <ledger-file> <red-file> <pre-rebase-sha>" in err


def test_insert_with_a_red_naming_a_case_no_graded_unit_pins_alongside_cases_that_do_adds_the_suite_repair_step_and_no_skill_edit_step_3009(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_015_prose_signed.py — FAIL SCRIPTS.md synopsis\ntest_unrelated_parser.py — FAIL parser broke\n")
    step = "- [ ] fix the full-suite failure: test_prd_015_prose_signed.py — FAIL SCRIPTS.md synopsis; test_unrelated_parser.py — FAIL parser broke ⟦suite-repair⟧ ⟦criterion 1⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")] == [step]
    assert "⟦skill-edit⟧" not in ledger.read_text()


def test_insert_with_a_red_whose_every_case_pins_one_graded_unit_adds_one_skill_edit_step_naming_it_and_no_suite_repair_step_3009(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", unit)], []))
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text(f"test_prd_015_prose_signed.py — FAIL {unit} synopsis\ntest_prd_016_short_names.py — FAIL {unit} name\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    unchecked = [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")]
    assert code == 0
    assert len(unchecked) == 1 and "⟦skill-edit⟧" in unchecked[0] and f"`{unit}`" in unchecked[0]
    assert "⟦suite-repair⟧" not in ledger.read_text()


def test_insert_with_a_red_pinned_by_two_listed_units_at_once_adds_one_skill_edit_step_naming_one_of_them_and_no_suite_repair_step_3009(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    units = ["skills/tdd/SCRIPTS.md", "skills/tdd/SKILL.md"]
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", u) for u in units], []))
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text(f"test_prd_015_prose_signed.py — FAIL {units[0]} and {units[1]} agree\ntest_prd_016_short_names.py — FAIL {units[0]} and {units[1]} name\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    unchecked = [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")]
    assert code == 0
    assert len(unchecked) == 1 and "⟦skill-edit⟧" in unchecked[0]
    assert any(f"`{u}`" in unchecked[0] for u in units)
    assert "⟦suite-repair⟧" not in ledger.read_text()



def test_insert_with_graded_reds_where_only_one_names_the_stale_unit_adds_the_suite_repair_step_and_no_skill_edit_step_3009(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", unit)], []))
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text(f"test_prd_015_prose_signed.py — FAIL {unit} synopsis\ntest_prd_016_short_names.py — FAIL some other reason\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    unchecked = [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")]
    assert code == 0
    assert len(unchecked) == 1 and "⟦suite-repair⟧" in unchecked[0]
    assert "⟦skill-edit⟧" not in ledger.read_text()

def test_insert_after_a_done_repair_skill_edit_step_with_a_red_naming_a_case_no_graded_unit_pins_exits_1_and_adds_no_suite_repair_step_3009(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7.md"
    ledger.write_text(
        "# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure by editing `skills/tdd/SCRIPTS.md`: test_prd_015_prose_signed.py — FAIL synopsis ⟦skill-edit⟧\n"
    )
    before = ledger.read_text()
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_unrelated_parser.py — FAIL parser broke\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 1
    assert "⟦suite-repair⟧" not in ledger.read_text()
    assert ledger.read_text() == before


def test_insert_after_a_done_repair_skill_edit_step_with_a_second_red_pinning_that_same_graded_unit_exits_1_and_adds_no_second_skill_edit_step_3009(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", unit)], []))
    ledger = tmp_path / "issue-7.md"
    ledger.write_text(
        "# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n"
        f"- [x] fix the full-suite failure by editing `{unit}`: test_prd_015_prose_signed.py — FAIL {unit} synopsis ⟦skill-edit⟧\n"
    )
    before = ledger.read_text()
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text(f"test_prd_016_short_names.py — FAIL {unit} name\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 1
    assert ledger.read_text().count("⟦skill-edit⟧") == 1
    assert ledger.read_text() == before


def test_insert_appends_a_step_that_ledger_steps_has_mark_skill_edit_finds_so_graded_changed_does_not_bail_it_3009(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", unit)], []))
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text(f"test_prd_015_prose_signed.py — FAIL {unit} synopsis\n")

    run_cli(module, ["insert", str(ledger), str(branch)])
    records = importlib.import_module("veri.ledger").ledger_steps(ledger.read_text())
    code = importlib.import_module("veri.ledger_steps").has_mark(records, "skill-edit")

    assert code == 0


def test_usage_names_the_test_only_verb_beside_the_others_with_its_arguments_for_a_no_argument_call_3113(run_cli):
    module = importlib.import_module("veri.suite_red_resume")

    code, out, err = run_cli(module, [])

    assert (code, out) == (2, "")
    assert "suite-red-resume.sh test-only <base-sha> <alone-cmd> <suite>..." in err


def test_the_test_only_exit_0_branch_in_suite_repair_md_ticks_the_step_with_a_ledger_and_a_step_title_3113():
    import pathlib
    import re

    skill = (pathlib.Path(__file__).resolve().parents[4] / "SUITE-REPAIR.md").read_text()
    branch = skill.split("suite-red-resume.sh test-only", 1)[1].split("**Exit 1:**", 1)[0]

    tick = re.search(r"\$S/tick-ledger\.sh([^\n]*)", branch).group(1)

    assert '.tdd/issue-<n>.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"' in tick, tick


def test_insert_with_a_red_from_suites_outside_the_grade_suites_naming_one_listed_unit_adds_a_skill_edit_step_and_a_red_naming_none_keeps_the_suite_repair_step_3107(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("requirements", "veri.requirements"):
        required = importlib.import_module(name)
        monkeypatch.setattr(required, "lists", lambda path="REQUIREMENTS.md": [path])
        monkeypatch.setattr(required, "listed_units", lambda path: [unit])
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    named = tmp_path / "issue-7.md"
    named.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n")
    unnamed = tmp_path / "issue-8.md"
    unnamed.write_text("# Plan for #8\n\n- [x] a ⟦criterion 1⟧\n")
    branch = tmp_path / "branch-red"
    branch.write_text(f"test_other_a.py — FAIL `{unit}` synopsis\ntest_other_b.py — FAIL {unit} name\n")
    stray = tmp_path / "stray-red"
    stray.write_text(f"test_other_a.py — FAIL {unit} synopsis\ntest_other_b.py — FAIL parser broke\n")

    named_code, _, _ = run_cli(module, ["insert", str(named), str(branch)])
    unnamed_code, _, _ = run_cli(module, ["insert", str(unnamed), str(stray)])

    named_steps = [l for l in named.read_text().split("\n") if l.startswith("- [ ]")]
    unnamed_steps = [l for l in unnamed.read_text().split("\n") if l.startswith("- [ ]")]
    assert named_code == 0 and len(named_steps) == 1
    assert named_steps[0].startswith(f"- [ ] fix the full-suite failure by editing `{unit}`: ")
    assert "⟦skill-edit⟧" in named_steps[0] and "⟦suite-repair⟧" not in named.read_text()
    assert unnamed_code == 0 and len(unnamed_steps) == 1 and "⟦suite-repair⟧" in unnamed_steps[0]
    assert "⟦skill-edit⟧" not in unnamed.read_text()


def test_insert_with_reds_outside_the_grade_suites_naming_two_different_listed_units_across_the_reds_adds_the_suite_repair_step_and_no_skill_edit_step_3107(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    units = ["skills/tdd/SCRIPTS.md", "skills/tdd/SKILL.md"]
    for name in ("requirements", "veri.requirements"):
        required = importlib.import_module(name)
        monkeypatch.setattr(required, "lists", lambda path="REQUIREMENTS.md": [path])
        monkeypatch.setattr(required, "listed_units", lambda path: units)
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n")
    branch = tmp_path / "branch-red"
    branch.write_text(f"test_other_a.py — FAIL `{units[0]}` synopsis\ntest_other_b.py — FAIL {units[1]} sentence\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    steps = [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")]
    assert code == 0 and len(steps) == 1 and "⟦suite-repair⟧" in steps[0]
    assert "⟦skill-edit⟧" not in ledger.read_text()


def test_insert_with_reds_outside_the_grade_suites_all_naming_one_listed_unit_while_the_first_unchecked_step_is_a_skill_edit_step_naming_it_adds_no_step_and_leaves_the_ledger_3107(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("requirements", "veri.requirements"):
        required = importlib.import_module(name)
        monkeypatch.setattr(required, "lists", lambda path="REQUIREMENTS.md": [path])
        monkeypatch.setattr(required, "listed_units", lambda path: [unit])
    ledger = tmp_path / "issue-7.md"
    text = f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] fix the full-suite failure by editing `{unit}`: test_other_a.py — FAIL {unit} synopsis ⟦skill-edit⟧\n- [ ] c ⟦criterion 3⟧\n"
    ledger.write_text(text)
    branch = tmp_path / "branch-red"
    branch.write_text(f"test_other_a.py — FAIL `{unit}` synopsis\ntest_other_b.py — FAIL {unit} name\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert ledger.read_text() == text


def test_insert_with_reds_outside_the_grade_suites_not_naming_the_listed_unit_of_the_first_unchecked_skill_edit_step_adds_the_suite_repair_step_before_it_3107(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("requirements", "veri.requirements"):
        required = importlib.import_module(name)
        monkeypatch.setattr(required, "lists", lambda path="REQUIREMENTS.md": [path])
        monkeypatch.setattr(required, "listed_units", lambda path: [unit])
    ledger = tmp_path / "issue-7.md"
    skill_edit = f"- [ ] fix the full-suite failure by editing `{unit}`: test_older.py — FAIL {unit} synopsis ⟦skill-edit⟧"
    ledger.write_text(f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n{skill_edit}\n- [ ] c ⟦criterion 3⟧\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_other_a.py — FAIL parser broke\ntest_other_b.py — FAIL lexer broke\n")
    step = "- [ ] fix the full-suite failure: test_other_a.py — FAIL parser broke; test_other_b.py — FAIL lexer broke ⟦suite-repair⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")][:2] == [step, skill_edit]


def test_insert_with_a_red_mixing_a_grade_suite_with_an_outside_suite_both_naming_one_listed_unit_adds_the_suite_repair_step_and_no_skill_edit_step_3107(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SCRIPTS.md"
    for name in ("requirements", "veri.requirements"):
        required = importlib.import_module(name)
        monkeypatch.setattr(required, "lists", lambda path="REQUIREMENTS.md": [path])
        monkeypatch.setattr(required, "listed_units", lambda path: [unit])
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n")
    branch = tmp_path / "branch-red"
    branch.write_text(f"test_prd_015_prose_signed.py — FAIL `{unit}` synopsis\ntest_other_b.py — FAIL {unit} name\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    steps = [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")]
    assert code == 0 and len(steps) == 1 and "⟦suite-repair⟧" in steps[0]
    assert "⟦skill-edit⟧" not in ledger.read_text().replace("⟦suite-repair⟧", "")


def test_insert_leaves_the_ledger_untouched_and_exits_0_when_the_one_stale_graded_unit_is_named_by_the_first_unchecked_skill_edit_step_3306(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    unit = "skills/tdd/SUITE-REPAIR.md"
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", unit)], []))
    ledger = tmp_path / "issue-7.md"
    text = f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] ⟦skill-edit⟧ sign `{unit}`\n- [ ] c ⟦criterion 3⟧\n"
    ledger.write_text(text)
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_016_short_names.py — FAIL stale GRADED\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert ledger.read_text() == text


def test_insert_still_adds_the_suite_repair_step_before_two_pending_skill_edit_steps_when_a_branch_red_suite_beside_the_graded_ones_is_red_for_another_reason_3306(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    units = ["skills/tdd/SUITE-REPAIR.md", "skills/tdd/SKILL.md"]
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", u) for u in units], []))
    ledger = tmp_path / "issue-7.md"
    first = f"- [ ] ⟦skill-edit⟧ sign `{units[0]}`"
    second = f"- [ ] ⟦skill-edit⟧ sign `{units[1]}`"
    ledger.write_text(f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n{first}\n{second}\n- [ ] c ⟦criterion 3⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_016_short_names.py\ntest_unrelated_parser.py — FAIL parser broke\n")
    step = "- [ ] fix the full-suite failure: test_prd_016_short_names.py; test_unrelated_parser.py — FAIL parser broke ⟦suite-repair⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")][:3] == [step, first, second]


def test_insert_leaves_the_ledger_untouched_and_exits_0_when_two_consecutive_pending_skill_edit_steps_together_name_the_two_stale_graded_units_3306(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    units = ["skills/tdd/SUITE-REPAIR.md", "skills/tdd/SKILL.md"]
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", u) for u in units], []))
    ledger = tmp_path / "issue-7.md"
    text = f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] ⟦skill-edit⟧ sign `{units[0]}`\n- [ ] ⟦skill-edit⟧ sign `{units[1]}`\n- [ ] c ⟦criterion 3⟧\n"
    ledger.write_text(text)
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_016_short_names.py — FAIL stale GRADED\n")

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert ledger.read_text() == text


def test_insert_still_adds_the_suite_repair_step_before_the_first_of_two_separated_pending_skill_edit_steps_when_a_branch_red_suite_is_red_for_another_reason_3378(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    units = ["skills/tdd/SUITE-REPAIR.md", "skills/tdd/SKILL.md"]
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", u) for u in units], []))
    ledger = tmp_path / "issue-7.md"
    first = f"- [ ] ⟦skill-edit⟧ sign `{units[0]}`"
    middle = "- [ ] b ⟦criterion 2⟧"
    second = f"- [ ] ⟦skill-edit⟧ sign `{units[1]}`"
    ledger.write_text(f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n{first}\n{middle}\n{second}\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_015_prose_signed.py\ntest_prd_016_short_names.py\ntest_unrelated_parser.py — FAIL parser broke\n")
    step = "- [ ] fix the full-suite failure: test_prd_015_prose_signed.py; test_prd_016_short_names.py; test_unrelated_parser.py — FAIL parser broke ⟦suite-repair⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert [l for l in ledger.read_text().split("\n") if l.startswith("- [ ]")] == [step, first, middle, second]


def test_insert_adds_no_step_and_exits_2_naming_both_skill_edit_steps_and_reorder_ledger_steps_when_a_plain_step_separates_the_two_stale_graded_units_steps_3378(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    units = ["skills/tdd/SUITE-REPAIR.md", "skills/tdd/SKILL.md"]
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", u) for u in units], []))
    ledger = tmp_path / "issue-7.md"
    text = f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] ⟦skill-edit⟧ sign `{units[0]}`\n- [ ] b ⟦criterion 2⟧\n- [ ] ⟦skill-edit⟧ sign `{units[1]}`\n"
    ledger.write_text(text)
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_015_prose_signed.py\ntest_prd_016_short_names.py — FAIL stale GRADED\n")

    code, _, err = run_cli(module, ["insert", str(ledger), str(branch)])

    assert ledger.read_text() == text
    assert not list(tmp_path.glob("*-added.md"))
    assert code == 2
    lines = err.strip().splitlines()
    assert len(lines) == 1
    assert all(unit in lines[0] for unit in units)
    assert "reorder-ledger-steps.sh" in lines[0]


def test_insert_leaves_the_ledger_untouched_and_exits_0_when_two_adjacent_pending_skill_edit_steps_together_explain_a_red_of_both_stale_graded_suites_3378(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    units = ["skills/tdd/SUITE-REPAIR.md", "skills/tdd/SKILL.md"]
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", u) for u in units], []))
    ledger = tmp_path / "issue-7.md"
    text = f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] ⟦skill-edit⟧ sign `{units[0]}`\n- [ ] ⟦skill-edit⟧ sign `{units[1]}`\n- [ ] b ⟦criterion 2⟧\n"
    ledger.write_text(text)
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_015_prose_signed.py\ntest_prd_016_short_names.py — FAIL stale GRADED\n")

    code, _, err = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert ledger.read_text() == text
    assert not list(tmp_path.glob("*-added.md"))


def test_rebased_tip_returns_insert_exit_2_unchanged_and_writes_no_rebase_lease_when_a_plain_step_separates_the_two_stale_graded_units_steps_3378(run_cli, tmp_path, monkeypatch):
    module = importlib.import_module("veri.suite_red_resume")
    units = ["skills/tdd/SUITE-REPAIR.md", "skills/tdd/SKILL.md"]
    for name in ("prose_owed", "veri.prose_owed"):
        monkeypatch.setattr(importlib.import_module(name), "owed_listed", lambda path="REQUIREMENTS.md": ([("REQUIREMENTS.md", u) for u in units], []))
    ledger = tmp_path / "issue-7.md"
    text = f"# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] ⟦skill-edit⟧ sign `{units[0]}`\n- [ ] b ⟦criterion 2⟧\n- [ ] ⟦skill-edit⟧ sign `{units[1]}`\n"
    ledger.write_text(text)
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "revise-impossible"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_prd_015_prose_signed.py\ntest_prd_016_short_names.py — FAIL stale GRADED\n")

    code, _, err = run_cli(module, ["rebased-tip", str(ledger), str(branch), "abc1234"])

    assert code == 2
    assert "reorder-ledger-steps.sh" in err
    assert ledger.read_text() == text
    assert not (tmp_path / "rebase-lease").exists()
