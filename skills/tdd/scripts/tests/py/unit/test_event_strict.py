"""VERI_EVENT_STRICT=1: event.sh and event.mark refuse an event veri/event_table.py does not allow (PRD 030.1, ET3, ET4), and a
value its key's declared format rejects (PRD 030.6, FS1, FS2)."""
import pytest
from veri import event


@pytest.fixture
def clone(tmp_path):
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text('[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n')
    return clone


def journals(clone, tmp_path):
    return [clone / ".tdd" / "events.jsonl", tmp_path / "runs" / "acme-widgets" / "7.jsonl"]


def write(how, clone, monkeypatch, run_cli, name, fields):
    """Writes one event through event.mark or event.sh's main, issue 7; returns (exit, stderr)."""
    if how == "mark":
        code = event.mark(str(clone), {"issue": "7"}, name, fields)
        return code, None
    code, _, err = run_cli(event, [name, *fields], env={"VERI_ISSUE": "7"}, cwd=clone)
    return code, err


@pytest.mark.parametrize("how", ["mark", "sh"])
def test_strict_refuses_an_event_name_the_table_does_not_hold(how, clone, tmp_path, monkeypatch, run_cli, capfd):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    code, err = write(how, clone, monkeypatch, run_cli, "no-such-event", ["pr=1"])
    err = capfd.readouterr().err if err is None else err

    assert code == 2
    assert [path for path in journals(clone, tmp_path) if path.exists() and path.read_bytes()] == []
    assert "no-such-event" in err


@pytest.mark.parametrize("how", ["mark", "sh"])
def test_strict_refuses_a_key_the_table_does_not_declare_for_the_event(how, clone, tmp_path, monkeypatch, run_cli, capfd):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    code, err = write(how, clone, monkeypatch, run_cli, "comment", ["kind=red", "url=u", "colour=blue"])
    err = capfd.readouterr().err if err is None else err

    assert code == 2
    assert [path for path in journals(clone, tmp_path) if path.exists() and path.read_bytes()] == []
    assert "comment" in err and "colour" in err


@pytest.mark.parametrize("how", ["mark", "sh"])
def test_strict_refuses_an_event_missing_a_key_the_table_marks_required(how, clone, tmp_path, monkeypatch, run_cli, capfd):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    code, err = write(how, clone, monkeypatch, run_cli, "comment", ["kind=red"])
    err = capfd.readouterr().err if err is None else err

    assert code == 2
    assert [path for path in journals(clone, tmp_path) if path.exists() and path.read_bytes()] == []
    assert "comment" in err and "url" in err


@pytest.mark.parametrize("how", ["mark", "sh"])
def test_strict_refuses_a_value_its_key_s_declared_format_rejects_naming_event_key_and_format(
        how, clone, tmp_path, monkeypatch, run_cli, capfd):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    code, err = write(how, clone, monkeypatch, run_cli, "plan", ["steps=three"])
    err = capfd.readouterr().err if err is None else err

    assert code == 2
    assert [path for path in journals(clone, tmp_path) if path.exists() and path.read_bytes()] == []
    assert "plan" in err and "steps" in err and "whole" in err


@pytest.mark.parametrize("how", ["mark", "sh"])
def test_strict_refuses_an_empty_value_of_a_key_the_table_does_not_allow_empty_naming_event_key_and_format(
        how, clone, tmp_path, monkeypatch, run_cli, capfd):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    code, err = write(how, clone, monkeypatch, run_cli, "merged", ["pr=", "tag=", "message="])
    err = capfd.readouterr().err if err is None else err

    assert code == 2
    assert [path for path in journals(clone, tmp_path) if path.exists() and path.read_bytes()] == []
    assert "merged" in err and "key pr " in err and "url" in err


@pytest.mark.parametrize("how", ["mark", "sh"])
@pytest.mark.parametrize("name, fields", [("no-such-event", ["pr=1"]), ("comment", ["kind=red", "url=u", "colour=blue"]),
                                          ("comment", ["kind=red"]), ("plan", ["steps=three"]),
                                          ("merged", ["pr=", "tag=", "message="])])
def test_without_strict_each_refused_call_writes_its_line_and_exits_0_saying_nothing(
        how, name, fields, clone, tmp_path, monkeypatch, run_cli, capfd):
    monkeypatch.delenv("VERI_EVENT_STRICT", raising=False)

    code, err = write(how, clone, monkeypatch, run_cli, name, fields)
    err = capfd.readouterr().err if err is None else err

    assert code == 0
    assert [len(path.read_bytes().splitlines()) for path in journals(clone, tmp_path)] == [1, 1]
    assert err == ""


def test_a_case_emitting_an_undeclared_key_through_event_mark_gets_exit_2_with_no_strict_setting_of_its_own(clone):
    assert event.mark(str(clone), {"issue": "7"}, "comment", ["kind=red", "url=u", "colour=blue"]) == 2


def test_4221_strict_writes_a_verdict_naming_the_sha_of_the_tree_it_judged_and_refuses_one_whose_tree_is_not_a_sha(
        clone, tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")
    judged = event.mark(str(clone), {"issue": "7"}, "verdict", ["verdict=PASS", "reason=fine", "tree=" + "a" * 40])
    refused = event.mark(str(clone), {"issue": "7"}, "verdict", ["verdict=PASS", "reason=fine", "tree=the-tree"])
    err = capfd.readouterr().err

    assert (judged, refused) == (0, 2)
    assert [len(path.read_bytes().splitlines()) for path in journals(clone, tmp_path)] == [1, 1]
    assert "verdict" in err and "tree" in err and "sha" in err


def test_4224_strict_writes_an_exit_retry_usage_and_verdict_line_naming_its_leaf(clone, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")
    usage = ["duration_ms=1", "duration_api_ms=1", "num_turns=1", "total_cost_usd=0.1", "input_tokens=1",
             "output_tokens=1", "cache_read_input_tokens=1", "cache_creation_input_tokens=1", "model="]
    lines = [("exit", ["status=0", "secs=3"]), ("retry", ["cause=stuck"]), ("usage", usage),
             ("verdict", ["verdict=PASS", "reason=fine"])]

    codes = [event.mark(str(clone), {"issue": "7"}, name, fields + ["name=verify-green-2"]) for name, fields in lines]

    assert codes == [0, 0, 0, 0]


def test_4226_strict_writes_a_step_reworded_line_naming_both_texts_and_refuses_one_without_its_new_text(clone):
    written = event.mark(str(clone), {"issue": "7"}, "step-reworded", ["from=old text", "to=new text"])
    refused = event.mark(str(clone), {"issue": "7"}, "step-reworded", ["from=old text"])

    assert (written, refused) == (0, 2)


def test_4228_strict_writes_a_stage_start_and_end_of_a_listed_stage_and_refuses_an_unlisted_stage(clone):
    started = event.mark(str(clone), {"issue": "7"}, "stage-start", ["stage=preflight"])
    ended = event.mark(str(clone), {"issue": "7"}, "stage-end", ["stage=baseline", "status=1", "secs=12"])
    unlisted = event.mark(str(clone), {"issue": "7"}, "stage-start", ["stage=lunch"])

    assert (started, ended, unlisted) == (0, 0, 2)


@pytest.mark.parametrize("stage", ["push", "draft-pr", "full-suite", "ready", "ci-wait"])
def test_4230_strict_writes_a_stage_start_and_end_of_each_stage_push_readying_and_the_ci_wait_add(clone, stage):
    started = event.mark(str(clone), {"issue": "7"}, "stage-start", ["stage=" + stage])
    ended = event.mark(str(clone), {"issue": "7"}, "stage-end", ["stage=" + stage, "status=0", "secs=3"])

    assert (started, ended) == (0, 0)


@pytest.mark.parametrize("stage", ["plan", "refactor-loop", "structural", "rebase", "merge", "release"])
def test_4232_strict_writes_a_stage_start_and_end_of_each_stage_the_plan_rebase_merge_and_release_add(clone, stage):
    started = event.mark(str(clone), {"issue": "7"}, "stage-start", ["stage=" + stage])
    ended = event.mark(str(clone), {"issue": "7"}, "stage-end", ["stage=" + stage, "status=1", "secs=3"])

    assert (started, ended) == (0, 0)


@pytest.mark.parametrize("how", ["mark", "sh"])
def test_strict_accepts_a_bail_with_cause_branch_rejected(how, clone, tmp_path, monkeypatch, run_cli, capfd):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    code, err = write(how, clone, monkeypatch, run_cli, "bail", ["cause=branch-rejected"])
    err = capfd.readouterr().err if err is None else err

    assert code == 0, err


@pytest.mark.parametrize("how", ["mark", "sh"])
def test_4719_strict_accepts_a_bail_with_cause_go_red_probe_unresolvable(how, clone, tmp_path, monkeypatch, run_cli, capfd):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    code, err = write(how, clone, monkeypatch, run_cli, "bail", ["cause=go-red-probe-unresolvable"])
    err = capfd.readouterr().err if err is None else err

    assert code == 0, err


def test_4712_strict_event_sh_refuses_a_deviated_event_without_its_rule_and_writes_one_that_names_it(
    clone, tmp_path, monkeypatch, run_cli
):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    missing, _ = write("sh", clone, monkeypatch, run_cli, "deviated", ["step=3", "reason=x"])
    named, _ = write("sh", clone, monkeypatch, run_cli, "deviated", ["rule=graded-edit", "step=3", "reason=x"])

    assert (missing, named) == (2, 0)


def test_4741_strict_event_sh_refuses_a_pin_retired_event_and_the_table_declares_no_mutation_record_restored(
        clone, tmp_path, monkeypatch, run_cli):
    from veri import event_table
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    code, _, err = run_cli(event, ["pin-retired", "reason=x"], env={"VERI_ISSUE": "7"}, cwd=clone)

    assert (code, sorted({"pin-retired", "mutation-record-restored"} & set(event_table.EVENTS))) == (2, []), err
