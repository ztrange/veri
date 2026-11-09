"""In-process cases for veri/restart_conductor.py, the module restart-conductor.sh is a shim over."""
import importlib
import json
import os
import subprocess


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


def test_3223_a_run_with_no_live_conductor_when_it_starts_exits_3_printing_nothing(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    now = [0.0]

    def nap(seconds):
        now[0] += seconds

    class FakeClock:
        sleep = staticmethod(nap)
        time = staticmethod(lambda: now[0])
        monotonic = staticmethod(lambda: now[0])

    monkeypatch.setattr(restart_conductor, "sleep", nap, raising=False)
    monkeypatch.setattr(restart_conductor, "time", FakeClock, raising=False)

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


def test_3346_a_conductor_log_with_a_leading_plain_text_line_is_measured_from_its_json_records_alone(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text(
        "update-veri.sh: already current\n" + "".join(json.dumps(r) + "\n" for r in records))
    alive = iter([True, True, False])
    calls = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, calls) == (0, [("stop", "at-ledger", "7")])


def test_3346_a_conductor_log_whose_every_line_is_plain_text_measures_no_growth_and_keeps_watching_stopping_nothing(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "conductor-7.log").write_text(
        "update-veri.sh: already current\nc0b101862952205cdffbd5a839c271fe1e72044b -> 57b4449cfe552641\n")
    alive = iter([True, True, False])
    calls = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), calls) == (0, "restarts 7 0", [])


def test_3346_a_conductor_log_that_exists_but_cannot_be_read_exits_2_with_a_stderr_line_naming_conductor_7_log(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd" / "conductor-7.log").mkdir(parents=True)
    alive = iter([True, True, False])
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, "conductor-7.log" in err) == (2, True)


def test_3223_a_live_conductor_whose_growth_is_59499_with_the_default_knob_is_not_stopped(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60499)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    alive = iter([True, True, False])
    calls = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert calls == []


def test_3223_before_it_stops_the_conductor_it_writes_restart_pending_holding_its_own_pid(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    pending = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    alive = iter([True, True, False])
    seen = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: seen.append(pending.read_text().strip() if pending.exists() else None), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert seen == [str(os.getpid())]


def test_3223_after_the_stop_once_the_conductor_has_exited_and_the_run_is_stopped_it_relaunches_the_conductor_exactly_once(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    alive = iter([True, True, False])
    calls = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "stopped", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert calls == [("stop", "at-ledger", "7"), ("launch", "7")]


def test_3223_started_from_a_linked_worktree_it_reads_the_conductor_log_and_writes_restart_pending_under_the_main_working_tree(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    main = tmp_path / "main"
    gitdir = main / ".git" / "worktrees" / "7"
    gitdir.mkdir(parents=True)
    (gitdir / "commondir").write_text("../..\n")
    start = main / ".tdd" / "wt" / "7"
    start.mkdir(parents=True)
    (start / ".git").write_text(f"gitdir: {gitdir}\n")
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (main / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    pending = main / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    alive = iter([True, True, False])
    seen = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: seen.append(pending.exists()), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    run_cli(restart_conductor, ["7"], cwd=start)

    assert seen == [True]


def test_3223_the_stop_wrapper_requests_mode_at_ledger_leaving_the_run_stop_file_holding_at_ledger(tmp_path, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    tdd = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    tdd.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    restart_conductor.stop_run("at-ledger", "7")

    stop = tdd / "stop"
    assert (stop.read_text().strip() if stop.exists() else None) == "at-ledger"


def test_3223_the_stop_wrapper_started_from_a_linked_worktree_writes_the_at_ledger_stop_file_under_the_main_working_tree(tmp_path, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    main = tmp_path / "main"
    gitdir = main / ".git" / "worktrees" / "7"
    gitdir.mkdir(parents=True)
    (gitdir / "commondir").write_text("../..\n")
    start = main / ".tdd" / "wt" / "7"
    (start / ".tdd").mkdir(parents=True)
    (start / ".git").write_text(f"gitdir: {gitdir}\n")
    monkeypatch.chdir(start)

    restart_conductor.stop_run("at-ledger", "7")

    stop = main / ".tdd" / "wt" / "7" / ".tdd" / "stop"
    assert (stop.read_text().strip() if stop.exists() else None) == "at-ledger"


def test_3223_the_run_state_of_a_run_whose_last_end_is_a_stop_reads_stopped(tmp_path, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    tdd = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    tdd.mkdir(parents=True)
    events = [{"ts": 1, "event": "launch", "issue": 7, "phase": "red"}, {"ts": 2, "event": "stop", "issue": 7, "mode": "at-ledger"}]
    (tdd / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    monkeypatch.chdir(tmp_path)

    assert restart_conductor.run_state("7") == "stopped"


def test_3223_the_detach_wrapper_launches_detach_leaf_on_run_conductor_for_the_run_appending_stdout_to_the_main_trees_conductor_log(tmp_path, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    main = tmp_path / "main"
    gitdir = main / ".git" / "worktrees" / "7"
    gitdir.mkdir(parents=True)
    (gitdir / "commondir").write_text("../..\n")
    start = main / ".tdd" / "wt" / "7"
    start.mkdir(parents=True)
    (start / ".git").write_text(f"gitdir: {gitdir}\n")
    log = main / ".tdd" / "conductor-7.log"
    log.write_text("earlier launch\n")
    launches = []

    class FakePopen:
        pid = 4242

        def __init__(self, argv, stdin=None, stdout=None, stderr=None, **kwargs):
            launches.append([os.path.basename(a) for a in argv])
            stdout.write("new launch\n")
            stdout.flush()

    monkeypatch.setattr(subprocess, "Popen", FakePopen)
    monkeypatch.chdir(start)

    restart_conductor.detach_leaf("7")

    assert (launches, log.read_text()) == ([["detach-leaf.sh", "run-conductor.sh", "7"]], "earlier launch\nnew launch\n")


def test_3223_a_run_is_live_when_pid_files_live_conductor_check_names_a_conductor_for_its_worktree_under_the_main_tree(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    pid_file = importlib.import_module("pid_file")
    worktree = str(tmp_path / ".tdd" / "wt" / "7")
    asked = []
    state = {"gone": False}

    def live_conductor(path):
        asked.append(path)
        return None if state["gone"] else "4242"

    monkeypatch.setattr(pid_file, "live_conductor", live_conductor)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: state.update(gone=True), raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), set(asked)) == (0, "restarts 7 0", {worktree})


def test_3223_a_relaunch_records_exactly_one_conductor_restart_event_with_the_growth_and_the_knob_in_the_runs_events_log(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    events = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl"
    alive = iter([True, True, False])
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "stopped", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    run_cli(restart_conductor, ["7"], cwd=tmp_path)

    lines = [json.loads(l) for l in events.read_text().splitlines()] if events.exists() else []
    restarts = [(e.get("growth"), e.get("knob")) for e in lines if e.get("event") == "conductor-restart"]
    assert restarts == [("59500", "70000")]


def test_3223_after_the_relaunch_the_restart_pending_file_is_removed(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    pending = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    alive = iter([True, True, False])
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "stopped", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert pending.exists() is False


def test_3223_after_a_relaunch_it_goes_on_watching_and_when_the_new_launch_ends_with_the_run_not_stopped_it_prints_restarts_7_1_and_exits_0(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    log = tmp_path / ".tdd" / "conductor-7.log"
    log.write_text("".join(json.dumps(r) + "\n" for r in [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]))
    alive = iter([True, True, False, False, False, True, False, False, False])
    states = iter(["stopped", "✅ Done"])
    calls = []

    def detach_leaf(run):
        calls.append(("launch", run))
        with open(log, "a") as f:
            f.write("".join(json.dumps(r) + "\n" for r in [{"type": "system", "subtype": "init"}, usage(2000)]))

    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: next(states, "✅ Done"), raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", detach_leaf, raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), calls) == (0, "restarts 7 1", [("stop", "at-ledger", "7"), ("launch", "7")])


def test_3223_a_live_conductor_is_stopped_at_85_percent_of_a_knob_the_caller_sets_not_at_the_default_threshold(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(9500)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    alive = iter([True, True, False])
    calls = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    run_cli(restart_conductor, ["7"], env={"VERI_RESET_GROWTH_CONDUCTOR": "10000"}, cwd=tmp_path)

    assert calls == [("stop", "at-ledger", "7")]


def test_3223_when_the_conductor_exits_after_its_own_stop_and_the_run_is_not_stopped_it_relaunches_nothing_removes_restart_pending_and_prints_restarts_7_0(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    pending = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    alive = iter([True, True, False])
    calls = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), pending.exists(), calls) == (0, "restarts 7 0", False, [("stop", "at-ledger", "7")])


def _relaunch_setup(tmp_path, monkeypatch, alive_script, states):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    (tmp_path / ".tdd").mkdir()
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    alive = iter(alive_script)
    states = iter(states)
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: next(states, "✅ Done"), raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: None, raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)
    return restart_conductor, alive


def test_3223_when_the_new_conductor_is_not_yet_recorded_right_after_the_relaunch_the_watch_waits_for_it_and_goes_on_watching(tmp_path, run_cli, monkeypatch):
    # initial check, watch, exit, then two empty polls after the relaunch, the new conductor, its end
    restart_conductor, alive = _relaunch_setup(
        tmp_path, monkeypatch, [True, True, False, False, False, False, False, True], ["stopped", "✅ Done"])

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), list(alive)) == (0, "restarts 7 1", [])


def test_3223_when_no_conductor_is_recorded_within_the_bound_after_the_relaunch_it_exits_2_naming_it_on_stderr_and_removes_restart_pending(tmp_path, run_cli, monkeypatch):
    restart_conductor, alive = _relaunch_setup(tmp_path, monkeypatch, [True, True, False], ["stopped"])
    pending = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out, "7" in err and "conductor" in err, pending.exists()) == (2, "", True, False)


def test_3369_a_relaunched_conductor_whose_init_record_is_not_yet_written_is_not_stopped_for_the_growth_its_predecessor_accrued(tmp_path, run_cli, monkeypatch):
    restart_conductor, alive = _relaunch_setup(
        tmp_path, monkeypatch, [True, True, False, False, False, True, True, False, False, False], ["stopped", "✅ Done"])
    pending = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    calls = []
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run, pending.exists())), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, calls) == (0, [("stop", "at-ledger", "7", True), ("launch", "7")])


def test_3369_a_relaunched_conductor_whose_own_session_growth_reaches_85_percent_of_the_knob_is_stopped_again(tmp_path, run_cli, monkeypatch):
    # initial check, watch, exit, the new conductor, its watch (growth reached), its exit
    restart_conductor, alive = _relaunch_setup(
        tmp_path, monkeypatch, [True, True, False, False, False, True, True, False, False, False], ["stopped", "✅ Done"])
    usage = lambda n: {"type": "assistant", "message": {"id": f"n{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    log = tmp_path / ".tdd" / "conductor-7.log"
    calls = []

    def detach_leaf(run):
        calls.append(("launch", run))
        with open(log, "a") as f:
            f.write("".join(json.dumps(r) + "\n" for r in [{"type": "system", "subtype": "init"}, usage(1000), usage(60500)]))

    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", detach_leaf, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, calls) == (0, [("stop", "at-ledger", "7"), ("launch", "7"), ("stop", "at-ledger", "7")])


def test_3389_a_conductor_log_ending_in_an_init_record_after_a_usage_record_keeps_watching_with_no_restart_pending_and_no_stop(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    usage = {"type": "assistant", "message": {"id": "a", "usage": {"input_tokens": 80000, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "conductor-7.log").write_text(
        "".join(json.dumps(r) + "\n" for r in [usage, {"type": "system", "subtype": "init"}]))
    alive = iter([True, True, False])
    calls = []
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "stop_run", lambda mode, run: calls.append(("stop", mode, run)), raising=False)
    monkeypatch.setattr(restart_conductor, "detach_leaf", lambda run: calls.append(("launch", run)), raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    pending = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    assert (code, out.strip(), calls, pending.exists()) == (0, "restarts 7 0", [], False)


def test_3389_once_the_new_sessions_usage_records_land_after_an_init_record_growth_is_computed_again_and_the_conductor_is_stopped_with_mode_at_ledger(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    usage = lambda n: {"type": "assistant", "message": {"id": f"m{n}", "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    records = [usage(80000), {"type": "system", "subtype": "init"}, usage(1000), usage(60500)]
    (tmp_path / ".tdd").mkdir()
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


def test_3384_a_watcher_armed_before_the_conductor_is_recorded_waits_for_it_and_goes_on_watching_instead_of_exiting_3(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    alive = iter([False, False, True, True])
    now = [0.0]

    def nap(seconds):
        now[0] += seconds

    class FakeClock:
        sleep = staticmethod(nap)
        time = staticmethod(lambda: now[0])
        monotonic = staticmethod(lambda: now[0])

    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", nap, raising=False)
    monkeypatch.setattr(restart_conductor, "time", FakeClock, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), err) == (0, "restarts 7 0", "")


def test_3384_a_watcher_armed_when_no_conductor_is_ever_recorded_exits_3_only_after_waiting_the_launch_bound_on_the_fake_clock(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    now = [0.0]

    def nap(seconds):
        now[0] += seconds

    class FakeClock:
        sleep = staticmethod(nap)
        time = staticmethod(lambda: now[0])
        monotonic = staticmethod(lambda: now[0])

    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: False, raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", nap, raising=False)
    monkeypatch.setattr(restart_conductor, "time", FakeClock, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out, err, now[0]) == (3, "", "", restart_conductor.LAUNCH_WAIT)


def test_3384_a_live_conductor_that_reads_not_live_for_one_poll_and_live_again_is_still_watched_until_three_consecutive_not_live_reads(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    # arm, a watched poll, one not-live blip, two more live polls, then three consecutive not-live reads
    alive = iter([True, True, False, True, True, False, False, False])
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), list(alive)) == (0, "restarts 7 0", [])


def test_3384_the_watch_sleeps_after_each_not_live_read_before_the_next_poll(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    events = []
    reads = iter([True, False, False, False])

    def alive(run):
        read = next(reads, False)
        events.append("live" if read else "not-live")
        return read

    monkeypatch.setattr(restart_conductor, "conductor_alive", alive, raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: events.append("sleep"), raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), events[1:6]) == (0, "restarts 7 0", ["not-live", "sleep", "not-live", "sleep", "not-live"])


def test_3384_a_conductor_that_never_asked_for_a_stop_and_stays_not_live_for_three_consecutive_reads_ends_the_watch_with_restarts_7_0_and_exit_0(tmp_path, run_cli, monkeypatch):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    # arm live, then three consecutive not-live reads; the trailing live read must never be taken
    alive = iter([True, False, False, False, True])
    monkeypatch.setattr(restart_conductor, "conductor_alive", lambda run: next(alive, False), raising=False)
    monkeypatch.setattr(restart_conductor, "run_state", lambda run: "✅ Done", raising=False)
    monkeypatch.setattr(restart_conductor, "sleep", lambda seconds: None, raising=False)

    code, out, err = run_cli(restart_conductor, ["7"], cwd=tmp_path)

    assert (code, out.strip(), list(alive)) == (0, "restarts 7 0", [True])
