"""Cases for veri/tunables.py, the one reader of VERI_* tunables."""
import importlib
import os

import pytest

ENTRY_POINTS = {
    "VERI_CONDUCTOR_CTX_BUDGET": ("veri.parallel_conductors", [], {}),
    "VERI_RESET_GROWTH_CONDUCTOR": ("veri.restart_conductor", ["7"], {}),
    "REVISE_BUDGET": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_REBASED_TIP_SUITE": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_BRANCH_SUITE": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_BASELINE_FULL_TIER": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_FULL_TIER_MAX_AGE_DAYS": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_CI_FLAKE_RERUNS": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_TEST_QUALITY_FIXES": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_BRANCH_REPAIRS": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_COMMENT_CHUNK": ("veri.report_cache", ["refresh"], {}),
    "VERI_SURROUND_MUTANTS": ("veri.surround_mutants", ["develop-surround.out", "--", "true"], {}),
    "VERI_KILL_POLL": ("veri.supervise", ["develop-red", "true"], {"VERI_TIMEOUT": "900"}),
}
CANDIDATES = ("abc", "-1", "0", "1.5.5", "1e3", "1e12", "nan", "inf", " 7")


def test_1313_every_tunable_in_the_readers_table_refuses_a_malformed_or_out_of_bounds_value_with_exit_2_one_line_naming_it_and_its_value_starting_nothing(
        monkeypatch, tmp_path, run_cli, fake_processes):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)

    refusals = {}
    assert tunables.TABLE["REVISE_BUDGET"].default == "2"
    for name, parse in tunables.TABLE.items():
        module, argv, env = ENTRY_POINTS[name]
        rejected = []
        for value in CANDIDATES:
            try:
                parse(value)
            except ValueError:
                rejected.append(value)
        assert rejected, "%s: no candidate value is refused by its parser" % name
        for value in rejected:
            for other in tunables.TABLE:
                monkeypatch.delenv(other, raising=False)
            calls = fake_processes()
            code, out, err = run_cli(importlib.import_module(module), argv, env=dict(env, **{name: value}), cwd=tmp_path)
            refusals[(name, value)] = (code, out, len(err.splitlines()), name in err, value in err,
                                       "Traceback" in err, tuple(calls))

    assert refusals
    assert set(refusals.values()) == {(2, "", 1, True, True, False, ())}


def test_2705_revise_budget_unset_resolves_to_the_default_of_2_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("REVISE_BUDGET", raising=False)

    assert tunables.resolve("REVISE_BUDGET") == (2, None)


def test_2841_rebased_tip_suite_set_to_a_value_but_local_or_ci_makes_run_conductor_exit_2_naming_it_and_the_value(
        monkeypatch, tmp_path, run_cli, fake_processes):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)
    module, argv, env = ENTRY_POINTS["VERI_REBASED_TIP_SUITE"]
    calls = fake_processes()

    code, out, err = run_cli(importlib.import_module(module), argv,
                             env=dict(env, VERI_REBASED_TIP_SUITE="bogus"), cwd=tmp_path)

    assert "VERI_REBASED_TIP_SUITE" in tunables.TABLE
    assert (code, out, len(err.splitlines()), "VERI_REBASED_TIP_SUITE" in err, "bogus" in err, tuple(calls)) == (
        2, "", 1, True, True, ())


def test_2841_rebased_tip_suite_unset_resolves_to_local_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("VERI_REBASED_TIP_SUITE", raising=False)

    assert tunables.resolve("VERI_REBASED_TIP_SUITE") == ("local", None)


def test_2841_rebased_tip_suite_set_to_ci_resolves_to_ci_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setenv("VERI_REBASED_TIP_SUITE", "ci")

    assert tunables.resolve("VERI_REBASED_TIP_SUITE") == ("ci", None)


def test_branch_suite_set_to_a_value_but_local_or_ci_makes_run_conductor_exit_2_naming_it_and_the_value(
        monkeypatch, tmp_path, run_cli, fake_processes):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)
    module, argv, env = ENTRY_POINTS["VERI_BRANCH_SUITE"]
    calls = fake_processes()

    code, out, err = run_cli(importlib.import_module(module), argv,
                             env=dict(env, VERI_BRANCH_SUITE="bogus"), cwd=tmp_path)

    assert "VERI_BRANCH_SUITE" in tunables.TABLE
    assert (code, out, len(err.splitlines()), "VERI_BRANCH_SUITE" in err, "bogus" in err, tuple(calls)) == (
        2, "", 1, True, True, ())


def test_branch_suite_unset_resolves_to_local_with_no_error_and_ci_resolves_to_ci(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("VERI_BRANCH_SUITE", raising=False)
    assert tunables.resolve("VERI_BRANCH_SUITE") == ("local", None)
    monkeypatch.setenv("VERI_BRANCH_SUITE", "ci")
    assert tunables.resolve("VERI_BRANCH_SUITE") == ("ci", None)


def test_2847_baseline_full_tier_set_to_a_value_but_run_or_reuse_makes_run_conductor_exit_2_naming_it_and_the_value(
        monkeypatch, tmp_path, run_cli, fake_processes):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)
    module, argv, env = ENTRY_POINTS["VERI_BASELINE_FULL_TIER"]
    calls = fake_processes()

    code, out, err = run_cli(importlib.import_module(module), argv,
                             env=dict(env, VERI_BASELINE_FULL_TIER="bogus"), cwd=tmp_path)

    assert "VERI_BASELINE_FULL_TIER" in tunables.TABLE
    assert (code, out, len(err.splitlines()), "VERI_BASELINE_FULL_TIER" in err, "bogus" in err, tuple(calls)) == (
        2, "", 1, True, True, ())


@pytest.mark.parametrize("value", ["abc", "1.5", "-3"])
def test_4018_ci_flake_reruns_not_a_whole_number_makes_run_conductor_exit_2_naming_it_and_the_value(
        monkeypatch, tmp_path, run_cli, fake_processes, value):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)
    module, argv, env = ENTRY_POINTS["VERI_CI_FLAKE_RERUNS"]
    calls = fake_processes()

    assert "VERI_CI_FLAKE_RERUNS" in tunables.TABLE
    assert tunables.resolve("VERI_CI_FLAKE_RERUNS") == (1, None)
    assert tunables.TABLE["VERI_CI_FLAKE_RERUNS"].refusal == "a whole number"
    assert tunables.parses("VERI_CI_FLAKE_RERUNS", "0")
    code, out, err = run_cli(importlib.import_module(module), argv,
                             env=dict(env, VERI_CI_FLAKE_RERUNS=value), cwd=tmp_path)

    assert (code, out, len(err.splitlines()), "VERI_CI_FLAKE_RERUNS" in err, "'%s'" % value in err,
            tuple(calls)) == (2, "", 1, True, True, ())


@pytest.mark.parametrize("value", ["abc", "1.5", "-3"])
def test_4120_test_quality_fixes_not_a_whole_number_makes_run_conductor_exit_2_naming_it_and_the_value(
        monkeypatch, tmp_path, run_cli, fake_processes, value):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)
    module, argv, env = ENTRY_POINTS["VERI_TEST_QUALITY_FIXES"]
    calls = fake_processes()
    entry = tunables.TABLE["VERI_TEST_QUALITY_FIXES"]
    unset = tunables.resolve("VERI_TEST_QUALITY_FIXES")

    code, out, err = run_cli(importlib.import_module(module), argv,
                             env=dict(env, VERI_TEST_QUALITY_FIXES=value), cwd=tmp_path)

    assert ((entry.default, entry.refusal, unset, tunables.parses("VERI_TEST_QUALITY_FIXES", "0")),
            (code, out, len(err.splitlines()), "VERI_TEST_QUALITY_FIXES" in err, "'%s'" % value in err,
             tuple(calls))) == (("1", "a whole number", (1, None), True), (2, "", 1, True, True, ()))


@pytest.mark.parametrize("value", ["0", "abc", "1.5", "-3"])
def test_4017_full_tier_max_age_days_of_0_or_not_a_whole_number_makes_run_conductor_exit_2_naming_it_and_the_value(
        monkeypatch, tmp_path, run_cli, fake_processes, value):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)
    module, argv, env = ENTRY_POINTS["VERI_FULL_TIER_MAX_AGE_DAYS"]
    calls = fake_processes()

    assert "VERI_FULL_TIER_MAX_AGE_DAYS" in tunables.TABLE
    assert tunables.resolve("VERI_FULL_TIER_MAX_AGE_DAYS") == (7, None)
    code, out, err = run_cli(importlib.import_module(module), argv,
                             env=dict(env, VERI_FULL_TIER_MAX_AGE_DAYS=value), cwd=tmp_path)

    assert tunables.TABLE["VERI_FULL_TIER_MAX_AGE_DAYS"].refusal == "a whole number of days >= 1"
    assert (code, out, len(err.splitlines()), "VERI_FULL_TIER_MAX_AGE_DAYS" in err, "'%s'" % value in err,
            tuple(calls)) == (2, "", 1, True, True, ())


def test_2847_baseline_full_tier_unset_resolves_to_reuse_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("VERI_BASELINE_FULL_TIER", raising=False)

    assert tunables.resolve("VERI_BASELINE_FULL_TIER") == ("reuse", None)


def test_2847_baseline_full_tier_set_to_reuse_resolves_to_reuse_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setenv("VERI_BASELINE_FULL_TIER", "reuse")

    assert tunables.resolve("VERI_BASELINE_FULL_TIER") == ("reuse", None)


@pytest.mark.parametrize("raw", ["x", "Run", "reuse ", " run", "REUSE", "skip", "none", "auto", "always", "1"])
def test_2847_baseline_full_tier_set_to_any_value_but_run_or_reuse_is_refused_naming_the_value(
        monkeypatch, raw):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setenv("VERI_BASELINE_FULL_TIER", raw)

    value, error = tunables.resolve("VERI_BASELINE_FULL_TIER")

    assert (value, error[0]) == (None, raw)


def test_2847_baseline_full_tier_set_empty_resolves_to_the_default_reuse(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setenv("VERI_BASELINE_FULL_TIER", "")

    assert tunables.resolve("VERI_BASELINE_FULL_TIER") == ("reuse", None)


def test_3223_reset_growth_conductor_is_in_the_readers_table_defaulting_to_30000_and_refusing_zero():
    tunables = importlib.import_module("veri.tunables")

    entry = tunables.TABLE["VERI_RESET_GROWTH_CONDUCTOR"]

    assert (entry.default, entry("1"), entry("30000")) == ("30000", 1, 30000)
    with pytest.raises(ValueError):
        entry("0")


DEFAULTED = {
    "VERI_REFACTOR_BUDGET": ("5", "0", "x"),
    "VERI_ISSUE_REFACTOR_BUDGET": ("10", "0", "-1"),
    "VERI_STEP_GROWTH_PERCENT": ("50", "0", "1.5"),
    "VERI_NO_VERDICT_RETRIES": ("1", "010", None),
    "VERI_SKILL_EDIT_BUDGET": ("3", "1", "0"),
    "VERI_ADJUDICATE_BUDGET": ("2", "0", "-1"),
    "VERI_DEVIATION_BUDGET": ("1", "0", "-1"),
    "VERI_STUCK_RETRIES": ("1", "0", "x"),
    "VERI_HEARTBEAT": ("180", "1", "1.5"),
    "VERI_TOOL_IDLE": ("600", "1", "1e3"),
    "VERI_TIMEOUT": ("900", "1", " 7"),
    "VERI_DISPATCH_RETRY_SLEEP": ("5", "0", "x"),
    "VERI_GH_REFUSAL_RETRIES": ("3", "0", "-1"),
    "VERI_LABEL": ("ready-for-agent", "ready-for-agent:mu", None),
    "VERI_TOOL_RETRY_SLEEP": ("15", "15", None),
    "VERI_TOOL_FAST_WAIT": ("900", "900", None),
    "VERI_TOOL_SLOW_SLEEP": ("900", "900", None),
    "VERI_TOOL_WAIT": ("3600", "3600", None),
    "VERI_GH_REFUSAL_SLEEP": ("60", "60", None),
    "VERI_GH_DRIVER": ("rest", "graphql", "x"),
    "VERI_MERGE_LOCK_POLL": ("30", "30", None),
    "VERI_MERGE_LOCK_WAIT": ("1800", "0", "-1"),
    "VERI_FETCH_RETRY_SLEEP": ("1", "1", None),
    "VERI_MERGE_SETTLE_READS": ("10", "10", None),
    "VERI_MERGE_SETTLE_SLEEP": ("3", "3", None),
    "VERI_CI_RETRY_BACKOFF": ("1", "1", None),
    "VERI_CI_NO_RUN_WAIT": ("600", "600", None),
    "VERI_CI_QUEUE_WAIT": ("3600", "3600", None),
    "VERI_PRIORITY_LABEL": ("priority", "priority", None),
    "VERI_AUTHOR_LABEL": ("author-read", "author-read", None),
    "VERI_PAGE_RETRIES": ("3", "3", None),
    "VERI_PAGE_RETRY_SLEEP": ("2", "2", None),
    "VERI_WORKQUEUE_LOCK_WAIT": ("30", "30", None),
    "VERI_MIN_FREE_GB": ("20", "20", None),
    "VERI_SKIP_VERIFY": ("", "x", None),
    "VERI_STOP_KILL_GRACE": ("5", "5", None),
    "VERI_CALLER_DIR": (".", ".", None),
    "VERI_SLEEP_GAP": ("900", "900", None),
    "VERI_SNAPSHOT_MAX_AGE": ("60", "60", None),
    "VERI_WATCH_QUEUE_INTERVAL": ("60", "60", None),
    "VERI_DISPATCH_STALL": ("3600", "3600", None),
    "VERI_DISPATCH_OVERLAP_POLL": ("60", "60", None),
    "VERI_STEP_BUDGET": ("12", "12", None),
    "VERI_RUN_BUDGET": ("120", "120", None),
    "VERI_UNIT_BUDGET": ("10", "10", None),
    "VERI_TIME_WARN_RATIO": ("1.5", "1.5", None),
    "VERI_PROFILE_THRESHOLD": ("1", "1", None),
    "VERI_MODEL": ("", "opus", None),
    "VERI_MODEL_DEVELOPER": ("sonnet", "opus", None),
    "VERI_MODEL_VERIFIER": ("sonnet", "opus", None),
    "VERI_MODEL_REVISE": ("opus", "sonnet", None),
    "VERI_MODEL_REVISE_GREEN": ("", "sonnet", None),
    "VERI_EFFORT_VERIFIER": ("", "low", "minimal"),
    "VERI_MODEL_ADJUDICATOR": ("opus", "sonnet", None),
    "VERI_MODEL_CONDUCTOR": ("opus", "sonnet", None),
}


@pytest.mark.parametrize("name", sorted(DEFAULTED))
def test_a_defaulted_tunable_states_its_one_default_and_its_parse_in_the_tunables_module(name):
    tunables = importlib.import_module("veri.tunables")
    default, good, bad = DEFAULTED[name]

    assert tunables.default(name) == default
    assert tunables.parses(name, good)
    if bad is not None:
        assert not tunables.parses(name, bad)


@pytest.mark.parametrize("name", sorted(DEFAULTED))
def test_get_reads_the_environment_and_falls_back_to_the_default_only_when_unset(monkeypatch, name):
    tunables = importlib.import_module("veri.tunables")
    default = DEFAULTED[name][0]
    monkeypatch.delenv(name, raising=False)
    assert tunables.get(name) == default
    monkeypatch.setenv(name, "")
    assert tunables.get(name) == ""
    assert tunables.get(name, unless_empty=True) == default
    monkeypatch.setenv(name, "7")
    assert tunables.get(name) == tunables.get(name, unless_empty=True) == "7"


def test_a_name_in_the_refusing_table_keeps_its_default_through_the_same_function():
    tunables = importlib.import_module("veri.tunables")

    assert (tunables.default("REVISE_BUDGET"), tunables.default("VERI_BASELINE_FULL_TIER")) == ("2", "reuse")


def test_one_table_holds_every_tunable_and_each_entry_states_a_default_a_parse_and_a_refusal_or_none():
    tunables = importlib.import_module("veri.tunables")

    assert {"REVISE_BUDGET", "VERI_REFACTOR_BUDGET", "VERI_MODEL_CONDUCTOR"} <= set(tunables.TUNABLES)
    assert tunables.TUNABLES["REVISE_BUDGET"].refusal == "a whole number"
    assert tunables.TUNABLES["VERI_REFACTOR_BUDGET"].refusal is None
    for entry in tunables.TUNABLES.values():
        assert isinstance(entry.default, str) and callable(entry.parse)


def test_the_refusing_table_is_exactly_the_entries_that_state_a_refusal():
    tunables = importlib.import_module("veri.tunables")

    assert tunables.TABLE == {n: e for n, e in tunables.TUNABLES.items() if e.refusal}
    assert set(tunables.TABLE) == {
        "VERI_CONDUCTOR_CTX_BUDGET", "VERI_RESET_GROWTH_CONDUCTOR",
        "VERI_KILL_POLL", "REVISE_BUDGET", "VERI_COMMENT_CHUNK", "VERI_REBASED_TIP_SUITE",
        "VERI_BRANCH_SUITE", "VERI_BASELINE_FULL_TIER", "VERI_FULL_TIER_MAX_AGE_DAYS",
        "VERI_CI_FLAKE_RERUNS", "VERI_TEST_QUALITY_FIXES", "VERI_SURROUND_MUTANTS",
        "VERI_BRANCH_REPAIRS"}


def test_resolve_refuses_nothing_for_a_name_that_states_no_refusal_and_get_reads_it(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setenv("VERI_REFACTOR_BUDGET", "x")

    assert tunables.get("VERI_REFACTOR_BUDGET") == "x"
    with pytest.raises(KeyError):
        tunables.resolve("VERI_REFACTOR_BUDGET")


@pytest.mark.parametrize("value,expected", [(None, "claude"), ("", "claude"), ("/opt/stub", "/opt/stub")])
def test_claude_bin_is_the_environment_value_and_claude_when_unset_or_empty(monkeypatch, value, expected):
    tunables = importlib.import_module("veri.tunables")
    if value is None:
        monkeypatch.delenv("CLAUDE_BIN", raising=False)
    else:
        monkeypatch.setenv("CLAUDE_BIN", value)
    assert tunables.claude_bin() == expected


@pytest.mark.parametrize("unless_empty, empty_reads", [(False, b""), (True, b"ready-for-agent")])
def test_get_bytes_reads_a_tunable_as_bytes_with_the_defaults_of_get(monkeypatch, unless_empty, empty_reads):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("VERI_LABEL", raising=False)
    assert tunables.get_bytes("VERI_LABEL", unless_empty=unless_empty) == b"ready-for-agent"
    monkeypatch.setenv("VERI_LABEL", "")
    assert tunables.get_bytes("VERI_LABEL", unless_empty=unless_empty) == empty_reads
    monkeypatch.setenv("VERI_LABEL", "x:mu")
    assert tunables.get_bytes("VERI_LABEL", unless_empty=unless_empty) == b"x:mu"


def test_get_bytes_returns_the_bytes_of_the_environment_undecoded(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setitem(os.environb, b"VERI_LABEL", b"\xff1")
    assert tunables.get_bytes("VERI_LABEL") == b"\xff1"


def test_4047_the_six_knobs_claude_md_documents_are_keys_of_tunables_with_their_readers_unset_defaults():
    tunables = importlib.import_module("veri.tunables")
    six = ("VERI_MISSING_REROUTE_BUDGET", "VERI_TEST_LOCK", "VERI_PYTEST_WORKERS", "VERI_PYTEST_LEGS",
           "VERI_PYCACHE", "VERI_NEW_SKILL")

    assert {name: tunables.default(name) for name in six if name in tunables.TUNABLES} == {
        "VERI_MISSING_REROUTE_BUDGET": "3", "VERI_TEST_LOCK": "", "VERI_PYTEST_WORKERS": "",
        "VERI_PYTEST_LEGS": "", "VERI_PYCACHE": "", "VERI_NEW_SKILL": ""}


def test_4047_the_other_knobs_an_operator_sets_are_keys_of_tunables_with_their_readers_unset_defaults():
    tunables = importlib.import_module("veri.tunables")
    knobs = ("VERI_PARALLEL", "VERI_RUN_TIMEOUT", "VERI_MAX_ISSUES", "VERI_SELF_UPDATE",
             "VERI_MUTATION_ADDRESS_DOMAIN", "VERI_SESSION_TRANSCRIPTS")

    assert {name: tunables.default(name) for name in knobs if name in tunables.TUNABLES} == {
        "VERI_PARALLEL": "1", "VERI_RUN_TIMEOUT": "14400", "VERI_MAX_ISSUES": "", "VERI_SELF_UPDATE": "",
        "VERI_MUTATION_ADDRESS_DOMAIN": "", "VERI_SESSION_TRANSCRIPTS": ""}


def test_4013_veri_effort_verifier_parses_exactly_the_five_effort_levels_the_cli_accepts():
    tunables = importlib.import_module("veri.tunables")

    accepted = [value for value in ("low", "medium", "high", "xhigh", "max", "", "LOW", " low", "minimal", "maximum")
                if tunables.parses("VERI_EFFORT_VERIFIER", value)]
    assert accepted == ["low", "medium", "high", "xhigh", "max"]


def test_4760_quality_repairs_unset_reads_1_and_its_entry_states_no_refusal_so_preflight_refuses_in_its_own_words(
        monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("VERI_QUALITY_REPAIRS", raising=False)

    assert (tunables.get("VERI_QUALITY_REPAIRS"), tunables.TUNABLES["VERI_QUALITY_REPAIRS"].refusal,
            "VERI_QUALITY_REPAIRS" in tunables.TABLE) == ("1", None, False)
