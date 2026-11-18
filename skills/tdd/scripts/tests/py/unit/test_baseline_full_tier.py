"""In-process cases for veri/baseline_full_tier.py, the module baseline-full-tier.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def baseline_full_tier():
    return importlib.import_module("veri.baseline_full_tier")


def test_main_called_with_no_argument_prints_the_usage_line_to_stderr_and_exits_2_3436(
        tmp_path, run_cli, baseline_full_tier):
    code, out, err = run_cli(baseline_full_tier, [], cwd=tmp_path)

    assert (code, out) == (2, "")
    assert "baseline-full-tier.sh" in err
    assert "usage" in err


def test_main_with_baseline_full_tier_unset_prints_run_and_exits_0_3436(
        tmp_path, run_cli, baseline_full_tier):
    code, out, err = run_cli(baseline_full_tier, ["3436", "make test"], cwd=tmp_path)

    assert (code, out.strip()) == (0, "run")


def test_main_with_reuse_and_a_recorded_time_prints_reuse_and_the_seconds_and_exits_0_3436(
        tmp_path, run_cli, baseline_full_tier):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    (tmp_path / ".git").mkdir()
    code, _, _ = run_cli(full_tier_time, ["--record", "727", "make test"], cwd=tmp_path)
    assert code == 0

    code, out, err = run_cli(baseline_full_tier, ["3436", "make test"],
                             env={"VERI_BASELINE_FULL_TIER": "reuse"}, cwd=tmp_path)

    assert (code, out.strip()) == (0, "reuse 727")


def test_main_prints_reuse_when_unset_with_a_recorded_time_and_run_when_set_to_run_or_none_is_recorded_3436(
        tmp_path, run_cli, baseline_full_tier):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    (tmp_path / ".git").mkdir()
    code, _, _ = run_cli(full_tier_time, ["--record", "727", "make test"], cwd=tmp_path)
    assert code == 0

    unset = run_cli(baseline_full_tier, ["3436", "make test"], cwd=tmp_path)
    unset_unrecorded = run_cli(baseline_full_tier, ["3436", "make other"], cwd=tmp_path)
    run_recorded = run_cli(baseline_full_tier, ["3436", "make test"],
                           env={"VERI_BASELINE_FULL_TIER": "run"}, cwd=tmp_path)

    assert (unset[0], unset[1].strip()) == (0, "reuse 727")
    assert (unset_unrecorded[0], unset_unrecorded[1].strip()) == (0, "run")
    assert (run_recorded[0], run_recorded[1].strip()) == (0, "run")


def test_main_with_reuse_and_no_recorded_time_for_the_command_prints_run_and_exits_0_3436(
        tmp_path, run_cli, baseline_full_tier):
    (tmp_path / ".git").mkdir()

    code, out, err = run_cli(baseline_full_tier, ["3436", "make test"],
                             env={"VERI_BASELINE_FULL_TIER": "reuse"}, cwd=tmp_path)

    assert (code, out.strip()) == (0, "run")


def test_main_takes_a_pinned_reuse_over_an_unset_environment_and_prints_reuse_and_the_seconds_3436(
        tmp_path, run_cli, baseline_full_tier):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    (tmp_path / ".git").mkdir()
    code, _, _ = run_cli(full_tier_time, ["--record", "727", "make test"], cwd=tmp_path)
    assert code == 0
    (tmp_path / ".tdd" / "issue-3436-baseline-full-tier").write_text("reuse\n")

    code, out, err = run_cli(baseline_full_tier, ["3436", "make test"], cwd=tmp_path)

    assert (code, out.strip()) == (0, "reuse 727")


def test_main_takes_a_pinned_run_over_an_environment_set_to_reuse_and_prints_run_3436(
        tmp_path, run_cli, baseline_full_tier):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    (tmp_path / ".git").mkdir()
    code, _, _ = run_cli(full_tier_time, ["--record", "727", "make test"], cwd=tmp_path)
    assert code == 0
    (tmp_path / ".tdd" / "issue-3436-baseline-full-tier").write_text("run\n")

    code, out, err = run_cli(baseline_full_tier, ["3436", "make test"],
                             env={"VERI_BASELINE_FULL_TIER": "reuse"}, cwd=tmp_path)

    assert (code, out.strip()) == (0, "run")


def test_main_takes_a_pinned_reuse_over_an_environment_set_to_run_and_prints_reuse_and_the_seconds_3436(
        tmp_path, run_cli, baseline_full_tier):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    (tmp_path / ".git").mkdir()
    code, _, _ = run_cli(full_tier_time, ["--record", "727", "make test"], cwd=tmp_path)
    assert code == 0
    (tmp_path / ".tdd" / "issue-3436-baseline-full-tier").write_text("reuse\n")

    code, out, err = run_cli(baseline_full_tier, ["3436", "make test"],
                             env={"VERI_BASELINE_FULL_TIER": "run"}, cwd=tmp_path)

    assert (code, out.strip()) == (0, "reuse 727")


@pytest.mark.parametrize("mode", ["run", "reuse"])
def test_main_called_with_only_the_issue_prints_the_usage_line_to_stderr_and_exits_2_3436(
        tmp_path, run_cli, baseline_full_tier, mode):
    (tmp_path / ".git").mkdir()

    code, out, err = run_cli(baseline_full_tier, ["3436"],
                             env={"VERI_BASELINE_FULL_TIER": mode}, cwd=tmp_path)

    assert (code, out) == (2, "")
    assert "usage: baseline-full-tier.sh <issue> <full-tier-command>" in err
    assert "Traceback" not in err


def _recorded(tmp_path, stamps):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "full-tier-time.json").write_text('{"make test": "727"}')
    if stamps is not None:
        (tmp_path / ".tdd" / "full-tier-time-at.json").write_text(stamps)


@pytest.mark.parametrize("stamps", [None, '{"make unit": 1763300000}', "{not json"],
                         ids=["no-recorded-at-file", "no-entry-for-the-command", "unreadable"])
def test_4017_reuse_with_a_recorded_time_but_no_recorded_at_prints_run_and_one_stderr_line_naming_the_command_unknown_and_the_knob(
        tmp_path, run_cli, baseline_full_tier, stamps):
    _recorded(tmp_path, stamps)

    code, out, err = run_cli(baseline_full_tier, ["4017", "make test"],
                             env={"VERI_BASELINE_FULL_TIER": "reuse"}, cwd=tmp_path)

    assert (code, out.strip(), len(err.splitlines())) == (0, "run", 1)
    assert ("'make test'" in err, "unknown" in err, "VERI_FULL_TIER_MAX_AGE_DAYS=7" in err) == (True, True, True)


def test_4017_reuse_with_an_unreadable_record_exits_2_naming_the_error_and_with_none_prints_run(
        tmp_path, run_cli, baseline_full_tier):
    (tmp_path / ".git").mkdir()
    env = {"VERI_BASELINE_FULL_TIER": "reuse"}
    absent = run_cli(baseline_full_tier, ["4017", "make test"], env=env, cwd=tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "full-tier-time.json").write_text("{not json")

    code, out, err = run_cli(baseline_full_tier, ["4017", "make test"], env=env, cwd=tmp_path)

    assert (absent[0], absent[1].strip()) == (0, "run")
    assert (code, out, len(err.splitlines()), "JSONDecodeError" in err, "Traceback" in err) == (2, "", 1, True, False)


@pytest.mark.parametrize("value", ["0", "abc", "1.5", "-2"])
def test_4017_a_bad_max_age_exits_2_naming_it_and_its_value_under_reuse_and_changes_nothing_under_run(
        tmp_path, run_cli, baseline_full_tier, monkeypatch, value):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    monkeypatch.setattr(full_tier_time, "now", lambda: 1763300000)
    _recorded(tmp_path, '{"make test": 1763300000}')

    reuse = run_cli(baseline_full_tier, ["4017", "make test"],
                    env={"VERI_BASELINE_FULL_TIER": "reuse", "VERI_FULL_TIER_MAX_AGE_DAYS": value}, cwd=tmp_path)
    run = run_cli(baseline_full_tier, ["4017", "make test"],
                  env={"VERI_BASELINE_FULL_TIER": "run", "VERI_FULL_TIER_MAX_AGE_DAYS": value}, cwd=tmp_path)

    code, out, err = reuse
    assert (code, out, len(err.splitlines()), "VERI_FULL_TIER_MAX_AGE_DAYS" in err, "'%s'" % value in err,
            "Traceback" in err) == (2, "", 1, True, True, False)
    assert run == (0, "run\n", "")


def test_4017_reuse_times_again_a_full_tier_time_recorded_in_the_future_naming_its_age_unknown(
        tmp_path, run_cli, baseline_full_tier, monkeypatch):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    monkeypatch.setattr(full_tier_time, "now", lambda: 1763300000)
    _recorded(tmp_path, '{"make test": %d}' % (1763300000 + 3600))

    code, out, err = run_cli(baseline_full_tier, ["4017", "make test"], env={"VERI_BASELINE_FULL_TIER": "reuse"},
                             cwd=tmp_path)

    assert (code, out.strip(), len(err.splitlines()), "unknown" in err) == (0, "run", 1, True)


def test_4017_after_a_stale_run_recording_new_seconds_makes_the_next_call_print_reuse_with_the_new_seconds(
        tmp_path, run_cli, baseline_full_tier, monkeypatch):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    monkeypatch.setattr(full_tier_time, "now", lambda: 1763300000)
    _recorded(tmp_path, '{"make test": %d}' % (1763300000 - 30 * 86400))
    env = {"VERI_BASELINE_FULL_TIER": "reuse"}

    stale = run_cli(baseline_full_tier, ["4017", "make test"], env=env, cwd=tmp_path)
    recorded = run_cli(full_tier_time, ["--record", "801", "make test"], cwd=tmp_path)
    fresh = run_cli(baseline_full_tier, ["4017", "make test"], env=env, cwd=tmp_path)

    assert (stale[0], stale[1].strip(), recorded[0], fresh[0], fresh[1].strip(), fresh[2]) == (
        0, "run", 0, 0, "reuse 801", "")


@pytest.mark.parametrize("age, knob, verdict, days", [
    (7 * 86400, None, "reuse 727", None),
    (7 * 86400 + 1, None, "run", "7"),
    (3 * 86400 + 5, "2", "run", "3"),
    (86400, "1", "reuse 727", None),
], ids=["exactly-the-default-age", "a-second-older-than-the-default", "older-than-a-set-knob", "exactly-a-set-knob"])
def test_4017_reuse_reuses_a_time_recorded_at_most_the_max_age_ago_and_times_an_older_one_again_naming_its_age_in_days(
        tmp_path, run_cli, baseline_full_tier, monkeypatch, age, knob, verdict, days):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    monkeypatch.setattr(full_tier_time, "now", lambda: 1763300000)
    _recorded(tmp_path, '{"make test": %d}' % (1763300000 - age))
    env = {"VERI_BASELINE_FULL_TIER": "reuse"}
    if knob is not None:
        env["VERI_FULL_TIER_MAX_AGE_DAYS"] = knob

    code, out, err = run_cli(baseline_full_tier, ["4017", "make test"], env=env, cwd=tmp_path)

    assert (code, out.strip()) == (0, verdict)
    if days is None:
        assert err == ""
    else:
        assert (len(err.splitlines()), "'make test'" in err, "%s days" % days in err,
                "VERI_FULL_TIER_MAX_AGE_DAYS=%s" % (knob or "7") in err) == (1, True, True, True)


TREE_4337 = "e" * 40


def _green_4337(run_cli, module, flag, root, tree=TREE_4337, fast="make unit", full="make test"):
    return run_cli(module, [flag, "4337", tree, fast, full], cwd=root)


def test_4337_a_green_recorded_for_the_tree_commands_pin_and_lock_answers_skip_and_none_recorded_answers_run(
        tmp_path, run_cli, baseline_full_tier):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-4337-skill-commit").write_text("f" * 40 + "\n")
    (tmp_path / "requirements-dev.txt").write_text("pytest==8 --hash=sha256:00\n")

    before = _green_4337(run_cli, baseline_full_tier, "--green", tmp_path)
    recorded = _green_4337(run_cli, baseline_full_tier, "--record-green", tmp_path)
    after = _green_4337(run_cli, baseline_full_tier, "--green", tmp_path)

    assert (before[0], before[1].strip()) == (0, "run")
    assert recorded[0] == 0
    assert (after[0], after[1].strip()) == (0, "skip")


@pytest.mark.parametrize("flag", ["--green", "--record-green"])
@pytest.mark.parametrize("count", [4, 6])
def test_4337_green_flags_with_a_wrong_argument_count_exit_2_with_the_usage_and_record_nothing(
        tmp_path, run_cli, baseline_full_tier, flag, count):
    (tmp_path / ".git").mkdir()

    code, out, err = run_cli(baseline_full_tier, [flag, "4337", TREE_4337, "make unit", "make test", "x"][:count],
                             cwd=tmp_path)

    assert (code, out) == (2, "")
    assert "--record-green" in err
    assert not (tmp_path / ".tdd" / "baseline-green.json").exists()


@pytest.mark.parametrize("part", ["tree", "fast", "full", "pin", "lock", "lock-removed"])
def test_4337_a_change_to_any_key_part_after_a_recorded_green_answers_run(
        tmp_path, run_cli, baseline_full_tier, part):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    pin = tmp_path / ".tdd" / "issue-4337-skill-commit"
    lock = tmp_path / "requirements-dev.txt"
    pin.write_text("f" * 40 + "\n")
    lock.write_text("pytest==8 --hash=sha256:00\n")
    assert _green_4337(run_cli, baseline_full_tier, "--record-green", tmp_path)[0] == 0
    args = {"tree": TREE_4337, "fast": "make unit", "full": "make test"}
    if part in args:
        args[part] = "changed"
    elif part == "pin":
        pin.write_text("0" * 40 + "\n")
    elif part == "lock":
        lock.write_text("pytest==9 --hash=sha256:11\n")
    else:
        lock.unlink()

    code, out, err = _green_4337(run_cli, baseline_full_tier, "--green", tmp_path, **args)

    assert (code, out.strip()) == (0, "run")


@pytest.mark.parametrize("corrupt", ["not json", "keys as a list", "absent"])
def test_4337_a_corrupt_or_absent_record_answers_run_and_a_green_recorded_over_it_counts(
        tmp_path, run_cli, baseline_full_tier, corrupt):
    import json
    (tmp_path / ".git").mkdir()
    record = tmp_path / ".tdd" / "baseline-green.json"
    assert _green_4337(run_cli, baseline_full_tier, "--record-green", tmp_path)[0] == 0
    if corrupt == "not json":
        record.write_text("{not json")
    elif corrupt == "keys as a list":
        record.write_text(json.dumps(list(json.loads(record.read_text()))))
    else:
        record.unlink()

    answered = _green_4337(run_cli, baseline_full_tier, "--green", tmp_path)
    recorded = _green_4337(run_cli, baseline_full_tier, "--record-green", tmp_path)
    after = _green_4337(run_cli, baseline_full_tier, "--green", tmp_path)

    assert (answered[0], answered[1].strip()) == (0, "run")
    assert recorded[0] == 0
    assert (after[0], after[1].strip()) == (0, "skip")


@pytest.mark.parametrize("verdict", ["red", "", None, True])
def test_4337_a_recorded_entry_that_is_not_green_answers_run(tmp_path, run_cli, baseline_full_tier, verdict):
    import json
    (tmp_path / ".git").mkdir()
    record = tmp_path / ".tdd" / "baseline-green.json"
    assert _green_4337(run_cli, baseline_full_tier, "--record-green", tmp_path)[0] == 0
    record.write_text(json.dumps({key: verdict for key in json.loads(record.read_text())}))

    code, out, err = _green_4337(run_cli, baseline_full_tier, "--green", tmp_path)

    assert (code, out.strip()) == (0, "run")
