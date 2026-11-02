"""Cases for the machine-wide run journal under $VERI_HOME."""
import os


def test_hermetic_environment_points_veri_home_at_the_cases_tmp_path(tmp_path):
    assert os.environ.get("VERI_HOME") == str(tmp_path)


def test_event_line_is_appended_byte_for_byte_to_the_journal_while_events_jsonl_keeps_its_path(tmp_path):
    import importlib
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text(
        '[core]\n\tbare = false\n[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n')

    code = event.append(str(clone), {"issue": "42"}, "done", ["pr=https://x/pull/1"], ts=1700000000)

    per_run = (clone / ".tdd" / "events.jsonl").read_bytes()
    journal = tmp_path / "runs" / "acme-widgets" / "42.jsonl"
    assert (code, per_run.count(b"\n")) == (0, 1)
    assert journal.read_bytes() == per_run


def test_journal_defaults_to_dot_veri_and_skips_a_clone_without_origin_url_or_an_event_without_issue(
        tmp_path, monkeypatch):
    import importlib
    event = importlib.import_module("veri.event")
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("VERI_HOME", raising=False)

    def clone_with(name, config):
        clone = tmp_path / name
        (clone / ".git").mkdir(parents=True)
        (clone / ".git" / "config").write_text(config)
        return clone

    origin = ('[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n'
              '[remote "fork"]\n\turl = https://github.com/other/forked.git\n')
    with_origin = clone_with("a", origin)
    without_url = clone_with("b", "[core]\n\tbare = false\n")

    codes = (
        event.append(str(with_origin), {"issue": "42"}, "done", [], ts=1700000000),
        event.append(str(with_origin), {}, "done", [], ts=1700000001),
        event.append(str(without_url), {"issue": "42"}, "done", [], ts=1700000002),
    )

    written = sorted(str(p.relative_to(home)) for p in (home / ".veri").rglob("*") if p.is_file())
    assert (codes, written) == ((0, 0, 0), [".veri/runs/acme-widgets/42.jsonl"])


def test_clone_without_readable_git_config_writes_no_journal_and_a_url_word_without_equals_is_skipped(tmp_path):
    import importlib
    event = importlib.import_module("veri.event")
    no_config = tmp_path / "noconfig"
    (no_config / ".git").mkdir(parents=True)
    keyless = tmp_path / "keyless"
    (keyless / ".git").mkdir(parents=True)
    (keyless / ".git" / "config").write_text(
        '[remote "origin"]\n\turlish\n\turl = https://github.com/acme/widgets.git\n')

    codes = (
        event.append(str(no_config), {"issue": "7"}, "done", [], ts=1700000000),
        event.append(str(keyless), {"issue": "8"}, "done", [], ts=1700000001),
    )

    written = sorted(str(p.relative_to(tmp_path)) for p in (tmp_path / "runs").rglob("*") if p.is_file())
    assert (codes, written) == ((0, 0), ["runs/acme-widgets/8.jsonl"])


def test_journal_path_is_named_from_origins_url_when_another_remotes_url_comes_first(tmp_path):
    import importlib
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text(
        '[remote "upstream"]\n\turl = https://github.com/other/forked.git\n'
        '[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n')

    code = event.append(str(clone), {"issue": "42"}, "done", [], ts=1700000000)

    written = sorted(str(p.relative_to(tmp_path)) for p in (tmp_path / "runs").rglob("*") if p.is_file())
    assert (code, written) == (0, ["runs/acme-widgets/42.jsonl"])


def test_event_with_an_empty_issue_creates_nothing_under_veri_home_and_prints_nothing_on_stderr(tmp_path, capfd):
    import importlib
    event = importlib.import_module("veri.event")
    home = tmp_path / "home"
    home.mkdir()
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text(
        '[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n')

    with_home = os.environ.get("VERI_HOME")
    os.environ["VERI_HOME"] = str(home)
    try:
        code = event.append(str(clone), {"issue": ""}, "done", [], ts=1700000000)
    finally:
        os.environ["VERI_HOME"] = with_home

    err = capfd.readouterr().err
    assert (code, list(home.iterdir()), err) == (0, [], "")


def test_event_in_a_clone_with_no_origin_remote_creates_nothing_under_veri_home_and_prints_nothing_on_stderr(
        tmp_path, capfd):
    import importlib
    event = importlib.import_module("veri.event")
    home = tmp_path / "home"
    home.mkdir()
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text("[core]\n\tbare = false\n")

    with_home = os.environ.get("VERI_HOME")
    os.environ["VERI_HOME"] = str(home)
    try:
        code = event.append(str(clone), {"issue": "42"}, "done", [], ts=1700000000)
    finally:
        os.environ["VERI_HOME"] = with_home

    err = capfd.readouterr().err
    assert (code, list(home.iterdir()), err) == (0, [], "")


def test_linked_worktree_names_the_journal_from_the_common_dirs_config(tmp_path):
    import importlib
    event = importlib.import_module("veri.event")
    common = tmp_path / "main" / ".git"
    admin = common / "worktrees" / "wt"
    admin.mkdir(parents=True)
    (admin / "commondir").write_text("../..\n")
    (common / "config").write_text(
        '[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n')
    linked = tmp_path / "linked"
    linked.mkdir()
    (linked / ".git").write_text("gitdir: " + str(admin) + "\n")

    code = event.append(str(linked), {"issue": "42"}, "done", [], ts=1700000000)

    per_run = (linked / ".tdd" / "events.jsonl").read_bytes()
    journal = tmp_path / "runs" / "acme-widgets" / "42.jsonl"
    assert (code, journal.read_bytes() if journal.exists() else None) == (0, per_run)


def test_scp_form_origin_names_the_same_journal_path_as_its_https_form(tmp_path):
    import importlib
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text(
        '[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')

    code = event.append(str(clone), {"issue": "42"}, "done", [], ts=1700000000)

    written = sorted(str(p.relative_to(tmp_path)) for p in (tmp_path / "runs").rglob("*") if p.is_file())
    assert (code, written) == (0, ["runs/acme-widgets/42.jsonl"])


def test_with_veri_home_unset_the_journal_is_written_under_dot_veri_in_home(tmp_path, monkeypatch):
    import importlib
    event = importlib.import_module("veri.event")
    monkeypatch.delenv("VERI_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text(
        '[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n')

    code = event.append(str(clone), {"issue": "42"}, "done", [], ts=1700000000)

    per_run = (clone / ".tdd" / "events.jsonl").read_bytes()
    journal = tmp_path / ".veri" / "runs" / "acme-widgets" / "42.jsonl"
    assert (code, journal.read_bytes() if journal.exists() else None) == (0, per_run)


def test_failed_journal_write_prints_one_stderr_line_naming_the_path_and_still_writes_events_jsonl(tmp_path, capfd):
    import importlib
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text(
        '[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n')
    journal = tmp_path / "runs" / "acme-widgets" / "42.jsonl"
    journal.mkdir(parents=True)

    code = event.append(str(clone), {"issue": "42"}, "done", [], ts=1700000000)

    err = capfd.readouterr().err
    per_run = (clone / ".tdd" / "events.jsonl").read_bytes()
    assert (code, per_run.count(b"\n"), len(err.splitlines()), str(journal) in err) == (0, 1, 1, True)


def test_one_journal_write_starts_no_process_and_is_one_os_write_on_an_o_append_descriptor(tmp_path, monkeypatch):
    import importlib
    import subprocess
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text(
        '[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n')
    journal = tmp_path / "runs" / "acme-widgets" / "42.jsonl"
    started, opened, written = [], {}, []
    real_open, real_write = os.open, os.write

    def spy_open(path, flags, *rest, **kw):
        fd = real_open(path, flags, *rest, **kw)
        opened[fd] = (os.fspath(path), flags)
        return fd

    def spy_write(fd, data):
        written.append((fd, bytes(data), opened[fd]))
        return real_write(fd, data)

    def spy_process(*args, **kw):
        started.append(args)
        raise AssertionError("a process was started")

    monkeypatch.setattr(os, "open", spy_open)
    monkeypatch.setattr(os, "write", spy_write)
    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, spy_process)
    for name in ("fork", "forkpty", "posix_spawn", "posix_spawnp", "system", "execv", "execve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, spy_process)

    code = event.append(str(clone), {"issue": "42"}, "done", [], ts=1700000000)

    to_journal = [(data, target[1]) for _, data, target in written if target[0] == str(journal)]
    flags = [flag for _, flag in to_journal]
    expected = (clone / ".tdd" / "events.jsonl").read_bytes()
    assert (code, started, [data for data, _ in to_journal], [bool(f & os.O_APPEND) for f in flags]) == (
        0, [], [expected], [True])


def test_done_records_pr_and_wall_seconds_capped_by_the_awake_span_counted_from_the_last_resume(
        tmp_path, monkeypatch):
    import importlib
    import json
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".tdd").mkdir()
    (clone / ".tdd" / "events.jsonl").write_text(
        '{"ts": 1000, "awake": 100, "event": "conductor-start"}\n'
        '{"ts": 2000, "awake": 500, "event": "resume"}\n')
    monkeypatch.setattr(event, "awake_reading", lambda: b"540")

    code = event.append(str(clone), {"issue": "42"}, "done", ["pr=https://x/pull/1"], ts=2100)

    done = json.loads((clone / ".tdd" / "events.jsonl").read_text().splitlines()[-1])
    assert (code, done.get("pr"), done.get("wall_seconds"), done.get("awake_seconds")) == (
        0, "https://x/pull/1", "40", "40")


def test_done_without_a_resume_skips_unparseable_lines_and_leaves_out_awake_seconds_when_a_mark_lacks_an_awake_reading(
        tmp_path, monkeypatch):
    import importlib
    import json
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".tdd").mkdir()
    (clone / ".tdd" / "events.jsonl").write_text(
        'not json\n'
        '[1, 2]\n'
        '{"ts": 1000, "awake": 100, "event": "conductor-start"}\n'
        '{"ts": 1500, "event": "step"}\n')
    monkeypatch.setattr(event, "awake_reading", lambda: b"540")

    code = event.append(str(clone), {"issue": "42"}, "done", ["pr=https://x/pull/1"], ts=2100)

    done = json.loads((clone / ".tdd" / "events.jsonl").read_text().splitlines()[-1])
    assert (code, done.get("wall_seconds"), "awake_seconds" in done) == (0, "1100", False)


def test_done_figures_for_a_ts_less_mark_an_opening_without_ts_or_awake_an_unreadable_ending_and_a_missing_or_empty_log(
        tmp_path, monkeypatch):
    import importlib
    import json
    event = importlib.import_module("veri.event")
    reading = {}
    monkeypatch.setattr(event, "awake_reading", lambda: reading["value"])

    def done(name, log, now):
        clone = tmp_path / name
        (clone / ".git").mkdir(parents=True)
        (clone / ".tdd").mkdir()
        if log is not None:
            (clone / ".tdd" / "events.jsonl").write_text(log)
        reading["value"] = now
        assert event.append(str(clone), {"issue": "42"}, "done", ["pr=https://x/pull/1"], ts=2100) == 0
        last = json.loads((clone / ".tdd" / "events.jsonl").read_text().splitlines()[-1])
        return last.get("wall_seconds"), last.get("awake_seconds")

    first = '{"ts": 1000, "awake": 100, "event": "conductor-start"}\n'
    assert {
        "ts_less_mark": done("a", first + '{"event": "note"}\n', b"540"),
        "opening_without_ts": done("b", '{"awake": 100, "event": "conductor-start"}\n', b"540"),
        "opening_without_ts_or_awake": done("c", '{"event": "resume"}\n' + first, b"540"),
        "ending_unreadable": done("d", first, b"-5"),
        "missing_log": done("e", None, b"540"),
        "empty_log": done("f", "", b"540"),
    } == {
        "ts_less_mark": ("440", "440"),
        "opening_without_ts": ("440", "440"),
        "opening_without_ts_or_awake": (None, None),
        "ending_unreadable": ("1100", None),
        "missing_log": ("0", "0"),
        "empty_log": ("0", "0"),
    }


def test_done_still_records_wall_and_awake_seconds_when_the_log_holds_a_line_of_non_utf8_bytes(
        tmp_path, monkeypatch):
    import importlib
    import json
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".tdd").mkdir()
    (clone / ".tdd" / "events.jsonl").write_bytes(
        b'\xff\xfe not utf-8\n'
        b'{"ts": 1000, "awake": 100, "event": "conductor-start"}\n')
    monkeypatch.setattr(event, "awake_reading", lambda: b"540")

    code = event.append(str(clone), {"issue": "42"}, "done", ["pr=https://x/pull/1"], ts=2100)

    done = json.loads((clone / ".tdd" / "events.jsonl").read_bytes().splitlines()[-1])
    assert (code, done.get("wall_seconds"), done.get("awake_seconds")) == (0, "440", "440")


def test_done_records_lane_equal_to_the_veri_label_metrics_prints_on_its_lane_line(tmp_path, monkeypatch):
    import importlib
    import json
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    monkeypatch.setattr(event, "awake_reading", lambda: b"540")
    monkeypatch.setenv("VERI_LABEL", "needs-agent")

    code = event.append(str(clone), {"issue": "42"}, "done", ["pr=https://x/pull/1"], ts=2100)

    done = json.loads((clone / ".tdd" / "events.jsonl").read_text().splitlines()[-1])
    assert (code, done.get("lane")) == (0, "needs-agent")


def test_done_records_lane_ready_for_agent_when_veri_label_is_set_to_an_empty_string(tmp_path, monkeypatch):
    import importlib
    import json
    event = importlib.import_module("veri.event")
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    monkeypatch.setattr(event, "awake_reading", lambda: b"540")
    monkeypatch.setenv("VERI_LABEL", "")

    code = event.append(str(clone), {"issue": "42"}, "done", ["pr=https://x/pull/1"], ts=2100)

    done = json.loads((clone / ".tdd" / "events.jsonl").read_text().splitlines()[-1])
    assert (code, done.get("lane")) == (0, "ready-for-agent")
