"""Small cases for veri.status --report: Waiting lists the bails since status-last."""
import importlib
import json
import subprocess


def test_2750_report_waiting_lists_each_bail_since_status_last_with_its_cause(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "status-last").write_text(json.dumps({"time": "2026-11-02T10:00:00Z", "queue": {}}))

    def journal(number, ts, cause):
        events = [{"ts": ts - 50, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
                  {"ts": ts, "awake": 50, "event": "bail", "cause": cause}]
        (runs / ("%d.jsonl" % number)).write_text("".join(json.dumps(e) + "\n" for e in events))
    journal(2750, 1793700000, "needs-user")
    journal(2751, 1793500000, "stuck")
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    waiting = lines[lines.index("Waiting") + 1:]
    assert (code, [l.split()[:2] for l in waiting if l]) == (0, [["#2750", "needs-user"]]), waiting


def test_2750_report_waiting_lists_every_bail_when_there_is_no_status_last(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()

    def journal(number, ts, cause):
        events = [{"ts": ts - 50, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
                  {"ts": ts, "awake": 50, "event": "bail", "cause": cause}]
        (runs / ("%d.jsonl" % number)).write_text("".join(json.dumps(e) + "\n" for e in events))
    journal(2750, 1793700000, "needs-user")
    journal(2751, 1793500000, "stuck")
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)

    code, out, err = run_cli(status, ["--report"])

    assert code == 0, err

    lines = [line.strip() for line in out.splitlines()]
    waiting = lines[lines.index("Waiting") + 1:]
    assert (code, [l.split()[:2] for l in waiting if l]) == (0, [["#2750", "needs-user"], ["#2751", "stuck"]]), waiting


def test_2750_report_waiting_lists_each_pr_ready_to_merge(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()

    def journal(number, pr, merged):
        events = [{"ts": 1793600000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
                  {"ts": 1793600050, "awake": 50, "event": "done", "pr": pr}]
        if merged:
            events.append({"ts": 1793600100, "awake": 100, "event": "merged"})
        (runs / ("%d.jsonl" % number)).write_text("".join(json.dumps(e) + "\n" for e in events))
    journal(2750, 99, False)
    journal(2751, 98, True)
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    waiting = [l for l in lines[lines.index("Waiting") + 1:] if l.startswith("#")]
    assert (code, [(l.split()[0], "99" in l) for l in waiting]) == (0, [("#2750", True)]), (waiting, err)


def test_2750_report_waiting_names_the_latest_pr_after_the_last_merged_and_skips_done_without_pr(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    events = [{"event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
              {"event": "done", "pr": 41},
              {"event": "merged"},
              {"event": "done", "pr": 42},
              {"event": "done"}]
    lines = [dict(e, ts=1793600000 + 10 * i, awake=10 * i) for i, e in enumerate(events)]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in lines))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)

    code, out, err = run_cli(status, ["--report"])

    out_lines = [line.strip() for line in out.splitlines()]
    waiting = [l for l in out_lines[out_lines.index("Waiting") + 1:] if l.startswith("#")]
    assert (code, [(l.split()[0], "42" in l, "41" in l) for l in waiting]) == (0, [("#2750", True, False)]), (waiting, err)


def test_3250_report_waiting_skips_a_pr_whose_issue_subject_is_on_local_main_without_a_merged_event(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    events = [{"ts": 1793600000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
              {"ts": 1793600050, "awake": 50, "event": "done", "pr": 99}]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    def fake_run(argv, *a, **k):
        out = "fix: something (#2750)\n" if argv[0] == "git" and "main" in argv else ""
        return subprocess.CompletedProcess(argv, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", fake_run)

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    waiting = [l for l in lines[lines.index("Waiting") + 1:] if l.startswith("#")]
    assert (code, waiting) == (0, []), (waiting, err)


def test_3250_report_waiting_lists_a_pr_whose_issue_subject_is_not_on_local_main(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    events = [{"ts": 1793600000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
              {"ts": 1793600050, "awake": 50, "event": "done", "pr": 99}]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    def fake_run(argv, *a, **k):
        out = "fix: something else (#2751)\nchore: mentions #2750 mid-subject\nfix: x (#2750) tail\n" if argv[0] == "git" and "main" in argv else ""
        return subprocess.CompletedProcess(argv, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", fake_run)

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    waiting = [l for l in lines[lines.index("Waiting") + 1:] if l.startswith("#")]
    assert (code, [(l.split()[0], "99" in l) for l in waiting]) == (0, [("#2750", True)]), (waiting, err)


def test_3250_report_waiting_skips_a_pr_whose_own_number_subject_is_on_local_main_without_a_merged_event(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    events = [{"ts": 1793600000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
              {"ts": 1793600050, "awake": 50, "event": "done", "pr": "https://github.com/acme/widgets/pull/2911"}]
    (runs / "2826.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    def fake_run(argv, *a, **k):
        out = "fix: something (#2911)\n" if argv[0] == "git" and "main" in argv else ""
        return subprocess.CompletedProcess(argv, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", fake_run)

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    waiting = [l for l in lines[lines.index("Waiting") + 1:] if l.startswith("#")]
    assert (code, waiting) == (0, []), (waiting, err)


def _waiting_calls(tmp_path, monkeypatch, main_log):
    """Run waiting_lines() for a journal with a done PR; return (lines, argv of every process it ran)."""
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    events = [{"ts": 1793600000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
              {"ts": 1793600050, "awake": 50, "event": "done", "pr": 99}]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    calls = []

    def spy(argv, *a, **k):
        calls.append(list(argv))
        out = main_log if argv[0] == "git" and "main" in argv else ""
        return subprocess.CompletedProcess(argv, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", spy)
    return status.waiting_lines(), calls


def test_3250_waiting_runs_no_gh_when_the_issue_subject_is_on_local_main(tmp_path, monkeypatch):
    lines, calls = _waiting_calls(tmp_path, monkeypatch, "fix: something (#2750)\n")

    assert (lines, [c for c in calls if c[0] == "gh"], len(calls) > 0) == ("none", [], True), calls


def test_3250_waiting_runs_no_gh_when_the_issue_subject_is_not_on_local_main(tmp_path, monkeypatch):
    lines, calls = _waiting_calls(tmp_path, monkeypatch, "fix: unrelated (#1)\n")

    assert ("PR 99 ready to merge" in lines, [c for c in calls if c[0] == "gh"], len(calls) > 0) == (True, [], True), calls
