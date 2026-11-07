"""In-process cases for veri/restart_conductor.py, the module restart-conductor.sh is a shim over."""
import importlib
import json


def test_3223_called_with_no_run_number_exits_2_with_a_usage_line_naming_the_script_and_writes_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")

    code, out, err = run_cli(restart_conductor, [], cwd=tmp_path)

    assert (code, out, "restart-conductor.sh" in err, list(tmp_path.iterdir())) == (2, "", True, [])


def test_3223_called_with_a_run_number_that_is_not_a_positive_integer_exits_2_and_writes_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")

    results = [run_cli(restart_conductor, [n], cwd=tmp_path) for n in ("abc", "0", "-3", "1.5")]

    assert ([code for code, _, _ in results], [out for _, out, _ in results], list(tmp_path.iterdir())) == ([2] * 4, [""] * 4, [])


def test_3223_called_with_a_non_ascii_digit_run_number_exits_2_and_writes_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")

    code, out, err = run_cli(restart_conductor, ["٣"], cwd=tmp_path)

    assert (code, out, list(tmp_path.iterdir())) == (2, "", [])


def test_3223_a_growth_knob_that_is_not_a_whole_number_of_at_least_1_exits_2_naming_the_variable_and_value_and_writes_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    values = ("abc", "0", "-5", "1.5", "")

    results = [run_cli(restart_conductor, ["7"], env={"VERI_RESET_GROWTH_CONDUCTOR": v}, cwd=tmp_path) for v in values]

    assert (
        [code for code, _, _ in results],
        [out for _, out, _ in results],
        [("VERI_RESET_GROWTH_CONDUCTOR" in err, repr(v) in err) for (_, _, err), v in zip(results, values)],
        list(tmp_path.iterdir()),
    ) == ([2] * 5, [""] * 5, [(True, True)] * 5, [])


def test_3223_a_run_with_no_live_conductor_when_it_starts_exits_3_printing_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out, err, list(tmp_path.iterdir())) == (3, "", "", [])


def test_3223_a_live_conductor_below_the_growth_threshold_that_exits_with_the_run_not_stopped_relaunches_nothing_and_prints_restarts_0(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(11000)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    alive = iter([True, True, False])
    calls = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda run: calls.append(("stop", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), calls) == (0, "restarts 7 0", [])


def test_3223_while_the_conductor_is_alive_the_watch_waits_through_the_sleep_wrapper_with_a_positive_interval(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    alive = iter([True, True, True, False])
    naps = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: naps.append(seconds), raising=False)

    run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (len(naps) >= 1, all(s > 0 for s in naps)) == (True, True)


def test_3223_the_sleep_wrapper_waits_by_handing_the_seconds_to_time_sleep(monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    waits = []
    monkeypatch.setattr(restart_conductor.time, "sleep", lambda seconds: waits.append(seconds))

    restart_conductor.sleep(2.5)

    assert waits == [2.5]


def test_3223_a_live_conductor_whose_growth_reaches_85_percent_of_the_default_knob_at_59500_is_stopped_with_mode_at_ledger(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    alive = iter([True, True, False])
    calls = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert calls == [("stop", "at-ledger", "7")]
