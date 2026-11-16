"""In-process cases for veri/run_records.py: a run's records on origin's refs/veri/runs/<n>, every git call faked."""
import importlib
import json
import os

import pytest

from process_fakes import HANGS


@pytest.fixture
def run_records():
    return importlib.import_module("veri.run_records")


def _kill_reaches(monkeypatch, fake):
    """os.killpg forwards the bound's kill to the fake children by pid, never to a real group."""
    monkeypatch.setattr(os, "killpg", lambda group, sig: [c.send_signal(sig) for c in fake.popens if c.pid == group])


def test_the_carried_journal_keeps_the_issues_lines_and_those_naming_no_issue_as_the_report_counts_them(tmp_path, run_records):
    (tmp_path / ".tdd").mkdir()
    lines = [{"issue": "7", "event": "start"}, {"issue": "", "event": "usage"}, {"event": "test-run"},
             {"issue": "8", "event": "start"}]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))

    carried = run_records.records(str(tmp_path), "7")["events.jsonl"].decode().splitlines()

    assert [json.loads(line) for line in carried] == lines[:3]


def test_the_ref_carries_only_what_a_reader_restores_the_journal_lines_and_the_skill_pin_not_the_timeout_pin(tmp_path, run_records):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text('{"issue": "7", "event": "start"}\n')
    (tmp_path / ".tdd" / "issue-7-skill-commit").write_text("abc1234\n")
    (tmp_path / ".tdd" / "issue-7-timeout").write_text("3600\n")

    assert sorted(run_records.records(str(tmp_path), "7")) == ["events.jsonl", "issue-7-skill-commit"]


def _a_machine(tmp_path, monkeypatch):
    """A home, a worktree inside it, a temp directory and a host name, each recognisable in a carried byte."""
    home = tmp_path / "home-of-mario"
    run = home / "code" / "repo-of-mario"
    temp = tmp_path / "temp-of-mario"
    (run / ".tdd").mkdir(parents=True)
    temp.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(temp))
    monkeypatch.setattr(importlib.import_module("tempfile"), "tempdir", str(temp))
    monkeypatch.setattr(importlib.import_module("socket"), "gethostname", lambda: "mario-mbp.local")
    return home, run, temp


def test_no_carried_byte_holds_the_home_the_worktree_a_temp_directory_or_the_host_name(tmp_path, monkeypatch, run_records):
    home, run, temp = _a_machine(tmp_path, monkeypatch)
    lines = [
        {"issue": "7", "event": "launch", "cmd": "%s/.tdd/pinned-scripts/run-leaf.sh %s/notes" % (run, home)},
        {"issue": "7", "event": "push-failed", "error": "fatal: could not write %s/git-1/index on mario-mbp" % temp},
        {"issue": "7", "event": "test-run", "detail": {"paths": ["/private/var/folders/ab/cd12ef/T/veri-x/a.py",
                                                                  "/var/folders/ab/cd12ef/T/b", "/tmp/veri-y/c"]}},
    ]
    raw = "".join(json.dumps(line) + "\n" for line in lines) + "not json under %s\n" % home
    (run / ".tdd" / "events.jsonl").write_text(raw)
    (run / ".tdd" / "issue-7-skill-commit").write_text("abc1234\n")

    carried = b"".join(run_records.records(str(run), "7").values()).decode()

    leaked = [word for word in (str(home), str(run), str(temp), "/var/folders", "/tmp/", "mario-mbp") if word in carried]
    parsed = [json.loads(line) for line in carried.splitlines()[:3]]
    assert (leaked, parsed[0]["cmd"]) == ([], "<repo>/.tdd/pinned-scripts/run-leaf.sh ~/notes")


FOLLOWERS = [".", "`", "}", "|", ",", ";", ":", ")", "]", '"', "'", ""]
HOST = "MacBook-Pro-de-Mariox.local"


def _spellings(path):
    """A path as a journal may hold it: as is, JSON-escaped slashes, URL-encoded both ways, and the macOS prefixes."""
    import urllib.parse
    forms = set()
    for base in {path, "/private" + path, "/System/Volumes/Data" + path}:
        forms |= {base, base.replace("/", "\\/"), urllib.parse.quote(base, safe=""), urllib.parse.quote(base, safe="/")}
    return sorted(forms)


def _an_account(tmp_path, monkeypatch, host=HOST):
    """A home named after the account `mariox`, a worktree under it, a temp directory and a host name."""
    home = tmp_path / "Users" / "mariox"
    run = home / "code" / "repo"
    temp = tmp_path / "scratch" / "T"
    (run / ".tdd").mkdir(parents=True)
    temp.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(temp))
    monkeypatch.setattr(importlib.import_module("tempfile"), "tempdir", str(temp))
    monkeypatch.setattr(importlib.import_module("socket"), "gethostname", lambda: host)
    monkeypatch.setattr(importlib.import_module("platform"), "node", lambda: host)
    monkeypatch.setattr(importlib.import_module("getpass"), "getuser", lambda: "mariox")
    return home, run, temp


def test_no_carried_byte_holds_a_path_the_account_name_or_a_host_form_in_any_spelling_or_position(
        tmp_path, monkeypatch, run_records):
    import random
    import re
    home, run, temp = _an_account(tmp_path, monkeypatch)
    sensitive = (_spellings(str(home)) + _spellings(str(run)) + _spellings(str(temp))
                 + ["mariox", "MARIOX", HOST, "MacBook-Pro-de-Mariox", "MacBook Pro de Mariox", "macbook-pro-de-mariox.local"])
    pick = random.Random(4079)

    def mixed():
        return "x " + pick.choice(sensitive) + pick.choice(FOLLOWERS) + " y"

    lines = []
    for n in range(60):
        lines.append({"issue": "7", "event": "launch", "cmd": mixed(), mixed(): mixed(),
                      "detail": {"nested": [mixed(), {"deeper": mixed(), mixed(): "v"}]},
                      "tail": pick.choice(sensitive)})
    (run / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))

    carried = run_records.records(str(run), "7")["events.jsonl"].decode()

    paths = _spellings(str(home)) + _spellings(str(temp))
    leaked = sorted({form for form in paths if form in carried})
    words = [w for w in ("mariox", "MacBook-Pro-de-Mariox", "MacBook Pro de Mariox", "mariox.local")
             if re.search(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(w), carried, re.I)]
    parsed = [json.loads(line) for line in carried.splitlines()]
    assert (leaked, words, len(parsed), all({"issue", "event", "cmd", "detail", "tail"} <= set(p) for p in parsed)) == (
        [], [], 60, True)


def test_an_ip_form_host_is_never_split_so_metrics_over_the_carried_records_equals_metrics_over_the_originals(
        tmp_path, monkeypatch, run_records):
    home, run, temp = _an_account(tmp_path, monkeypatch, host="192.168.68.55")
    metrics = importlib.import_module("veri.metrics")
    monkeypatch.setattr(run_records, "read", lambda issue, name, cwd: None)
    mark = {"issue": "7", "actor": "developer", "phase": "green", "step": "s", "attempt": "1"}
    events = [dict(mark, actor="conductor", attempt="", ts=1000, event="step-start"),
              dict(mark, ts=1010, event="launch", name="develop-green"),
              dict(mark, ts=1202, event="exit", status="0", secs="192"),
              dict(mark, ts=1202, event="usage", input_tokens=192, output_tokens=168, cache_read_input_tokens=55,
                   cache_creation_input_tokens=68, cost_usd="1.92"),
              dict(mark, actor="conductor", attempt="", ts=1300, event="step-done")]
    (run / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    carried = tmp_path / "carried"
    (carried / ".tdd").mkdir(parents=True)
    (carried / ".tdd" / "events.jsonl").write_bytes(run_records.records(str(run), "7")["events.jsonl"])

    original = metrics.report("7", str(run / ".tdd" / "events.jsonl"), str(run / ".tdd" / "issue-7.md"))
    redacted = metrics.report("7", str(carried / ".tdd" / "events.jsonl"), str(carried / ".tdd" / "issue-7.md"))

    assert redacted == original


def test_the_records_commit_is_made_by_veri_with_author_and_committer_dates_in_utc(tmp_path, monkeypatch, fake_processes,
                                                                                    run_records):
    (tmp_path / ".tdd").mkdir()
    fake = fake_processes.answers({
        "git hash-object": (0, "b" * 40 + "\n", ""),
        "git mktree": (0, "c" * 40 + "\n", ""),
        "git commit-tree": (0, "d" * 40 + "\n", ""),
    })

    run_records.commit(str(tmp_path), "7")

    env = next(kwargs.get("env") or {} for argv, kwargs in fake.seen if argv[1:2] == ["commit-tree"])
    assert ({k: env.get(k) for k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL")},
            env.get("GIT_AUTHOR_DATE", "").endswith(" +0000"), env.get("GIT_COMMITTER_DATE", "").endswith(" +0000")) == (
        {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@localhost", "GIT_COMMITTER_NAME": "veri",
         "GIT_COMMITTER_EMAIL": "veri@localhost"}, True, True)


def test_the_local_journal_and_pin_are_byte_identical_after_a_push_of_their_redacted_records(tmp_path, monkeypatch,
                                                                                             fake_processes, run_records):
    home, run, temp = _a_machine(tmp_path, monkeypatch)
    journal = run / ".tdd" / "events.jsonl"
    journal.write_bytes(b'{"issue":"7","event":"launch","cmd":"%s/x"}\nnot json %s\n' % (str(run).encode(), str(home).encode()))
    pin = run / ".tdd" / "issue-7-skill-commit"
    pin.write_bytes(b"abc1234\n")
    before = (journal.read_bytes(), pin.read_bytes())
    monkeypatch.chdir(run)
    fake_processes.answers({
        "git rev-parse --abbrev-ref HEAD": (0, "tdd/7-records\n", ""),
        "git hash-object": (0, "b" * 40 + "\n", ""),
        "git mktree": (0, "c" * 40 + "\n", ""),
        "git commit-tree": (0, "d" * 40 + "\n", ""),
        "git push": (0, "", ""),
    })

    run_records.after_push()

    assert (journal.read_bytes(), pin.read_bytes()) == before


def test_a_records_push_and_fetch_that_never_answer_end_after_veri_git_network_timeout_as_no_answer_on_one_stderr_line(
        tmp_path, monkeypatch, capsys, fake_processes, run_records):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GIT_NETWORK_TIMEOUT", "5")
    fake = fake_processes.answers({
        "git rev-parse --abbrev-ref HEAD": (0, "tdd/7-records\n", ""),
        "git hash-object": (0, "b" * 40 + "\n", ""),
        "git mktree": (0, "c" * 40 + "\n", ""),
        "git commit-tree": (0, "d" * 40 + "\n", ""),
        "git remote get-url origin": (0, "https://example.invalid/r.git\n", ""),
        "git push": HANGS,
        "git fetch": HANGS,
    })
    _kill_reaches(monkeypatch, fake)

    run_records.after_push()
    pushed = capsys.readouterr().err.splitlines()
    read = run_records.read("7", "events.jsonl", str(tmp_path))
    fetched = capsys.readouterr().err.splitlines()

    assert (len(pushed), "VERI_GIT_NETWORK_TIMEOUT" in "".join(pushed), read, len(fetched),
            "VERI_GIT_NETWORK_TIMEOUT" in "".join(fetched)) == (1, True, None, 1, True)
