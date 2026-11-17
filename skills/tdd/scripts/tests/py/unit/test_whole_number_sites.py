"""Each site that hand-wrote "ASCII digits, then decimal int >= 0" accepts exactly what entry.whole_number(text, 0)
accepts: the same probes through every site's own refusal path, so a site that moves onto the shared check cannot
shift what it takes."""
import importlib
import json
import os

import pytest

BIG = "9" * 30
# probe -> the int an accepting site reads from it, None when the site refuses it
PROBES = {"0": 0, "7": 7, "007": 7, "-1": None, "+1": None, " 7": None, "7\n": None, "1.5": None, "": None,
          "²": None, "١": None, BIG: int(BIG)}
ids = [repr(p) for p in PROBES]
probes = pytest.mark.parametrize("probe, value", list(PROBES.items()), ids=ids)


def module(name):
    return importlib.import_module("veri." + name)


@probes
def test_ledger_growth_takes_a_veri_step_growth_percent_only_of_ascii_digits(tmp_path, run_cli, probe, value):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    ledger.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n")
    code, out, err = run_cli(module("ledger_growth"), [str(plan), str(ledger)], env={"VERI_STEP_GROWTH_PERCENT": probe})
    assert (code, "must be a whole number >= 0" in err) == ((0, False) if value is not None else (2, True))


@probes
def test_push_branch_takes_a_push_tunable_only_of_ascii_digits_and_an_empty_one_is_its_default(
        monkeypatch, capsys, probe, value):
    monkeypatch.setenv("VERI_PUSH_RETRIES", probe)
    got = module("push_branch").tunable("VERI_PUSH_RETRIES", "3")
    err = capsys.readouterr().err
    expected = "3" if probe == "" else (probe if value is not None else None)
    assert (got, "must be a non-negative integer" in err) == (expected, expected is None)


@probes
def test_run_affordable_takes_steps_remaining_only_of_ascii_digits(monkeypatch, capsys, probe, value):
    run_affordable = module("run_affordable")
    monkeypatch.setattr(run_affordable.step_budget, "budgets", lambda: (3, None, None))
    code = run_affordable.main([probe])
    assert (code, "is not a whole number" in capsys.readouterr().err) == ((3, False) if value is not None else (2, True))


@probes
def test_workqueue_takes_a_lock_wait_only_of_ascii_digits_and_an_empty_one_is_its_default(
        monkeypatch, capsys, probe, value):
    monkeypatch.setenv("VERI_WORKQUEUE_LOCK_WAIT", probe)
    workqueue = module("workqueue")
    if probe == "":
        assert workqueue.lock_tries() == 600
    elif value is None:
        with pytest.raises(SystemExit) as stopped:
            workqueue.lock_tries()
        assert (stopped.value.code, "must be a whole number >= 0" in capsys.readouterr().err) == (2, True)
    else:
        assert workqueue.lock_tries() == value * 20


@probes
def test_supervise_takes_a_numeric_variable_only_of_ascii_digits(capsys, probe, value):
    refused = module("supervise").not_a_number("VERI_X", probe)
    assert (refused, "is not a number" in capsys.readouterr().err) == ((None, False) if value is not None else (2, True))


@probes
def test_refactor_candidates_takes_an_issue_number_only_of_ascii_digits(tmp_path, run_cli, probe, value):
    code, out, err = run_cli(module("refactor_candidates"), [probe, str(tmp_path / "no-such-owed.md")])
    assert code == (3 if value is not None else 2)


@probes
def test_tunables_tokens_reads_ascii_digits_as_an_int_and_refuses_anything_else(probe, value):
    tunables = module("tunables")
    if value is None:
        with pytest.raises(ValueError):
            tunables.tokens(probe)
    else:
        assert tunables.tokens(probe) == value


@probes
def test_leaf_timeout_is_whole_only_of_ascii_digits(probe, value):
    assert module("leaf_timeout").is_whole(probe) is (value is not None)


@probes
def test_refactor_budget_refuses_a_value_that_is_not_ascii_digits(capsys, probe, value):
    assert module("refactor_budget")._refused("VERI_X", probe) is (value is None)


@probes
def test_ledger_steps_criterion_takes_its_number_only_of_ascii_digits(run_cli, probe, value):
    code, out, err = run_cli(module("ledger_steps"), ["criterion", probe], stdin="")
    assert ((code == 2 and "usage: ledger-steps.sh" in err)) is (value is None)


@probes
def test_full_tier_time_takes_a_stored_time_only_of_ascii_digits(tmp_path, run_cli, probe, value):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "full-tier-time.json").write_text(json.dumps({"make test": probe}))
    code, out, err = run_cli(module("full_tier_time"), ["make test"], cwd=tmp_path)
    assert (code, out) == ((0, probe + "\n") if value is not None else (2, ""))


@pytest.mark.parametrize("probe, value", [(p, v) for p, v in PROBES.items() if p.strip() == p],
                         ids=[repr(p) for p in PROBES if p.strip() == p])
def test_restart_marker_takes_a_pid_only_of_ascii_digits(tmp_path, monkeypatch, probe, value):
    # the marker's text is stripped before the check, so the two probes padded with whitespace are not probes of it
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "restart-pending").write_text(probe)
    probed = []

    def gone(pid, sig):
        probed.append(pid)
        raise ProcessLookupError

    monkeypatch.setattr(os, "kill", gone)
    answer = module("restart_marker").in_flight(str(tmp_path), unreadable="refused")
    assert (answer, probed) == (("refused", []) if value is None else (False, [value]))
