"""Small cases for veri.status --report: Running's live runs."""
import importlib
import json
import os


def test_2750_report_running_lists_a_block_for_each_journal_whose_conductor_start_pid_is_alive_with_matching_start(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"

    def journal(number, pid):
        events = [{"event": "conductor-start", "ts": "2026-11-02T10:00:00Z", "awake": 60,
                   "pid": pid, "started": started},
                  {"event": "step-start", "ts": "2026-11-02T10:04:00Z", "awake": 240}]
        (runs / ("%d.jsonl" % number)).write_text("".join(json.dumps(e) + "\n" for e in events))
    journal(2750, os.getpid())
    journal(2751, 2 ** 22 + 12345)
    fake_processes.answers({"ps ": (0, started + "\n", "")}, default=(0, "", ""))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    listed = [x for x in running if x.startswith("#")]
    assert (code, [x.split()[0] for x in listed], ["3m" in x.split() for x in listed]) == (0, ["#2750"], [True]), running


def test_2750_report_running_omits_a_journal_whose_conductor_start_pid_is_alive_but_started_at_another_time(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (runs / "2750.jsonl").write_text(json.dumps(
        {"event": "conductor-start", "ts": "2026-11-02T10:00:00Z", "awake": 0,
         "pid": os.getpid(), "started": "Mon Nov  2 10:00:00 2026"}) + "\n")
    fake_processes.answers({"ps ": (0, "Tue Nov  3 09:30:00 2026\n", "")}, default=(0, "", ""))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    assert (code, [x for x in running if x.startswith("#")]) == (0, []), running


def test_3996_report_running_omits_a_journal_whose_conductor_start_records_no_start_time_though_its_pid_answers_and_ps_gives_none(tmp_path, monkeypatch, run_cli, fake_processes):
    """No start time on either side is not an observed match: a live pid alone may be a reused one."""
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (runs / "2750.jsonl").write_text(json.dumps(
        {"event": "conductor-start", "ts": "2026-11-02T10:00:00Z", "awake": 0, "pid": os.getpid(), "started": ""}) + "\n")
    fake_processes.answers({"ps ": (0, "\n", "")}, default=(0, "", ""))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    assert (code, [x for x in running if x.startswith("#")]) == (0, []), running
