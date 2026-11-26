"""In-process cases for veri/run_records.py: a run's records on origin's refs/veri/runs/<n>, every git call faked."""
import importlib
import json
import os
import re

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


def test_a_token_or_a_listed_value_in_a_journal_value_or_key_is_carried_redacted_issue_3960(tmp_path, monkeypatch, run_records):
    token = "ghp_" + "FAKEfake0123" * 3
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")
    (tmp_path / ".tdd").mkdir()
    line = {"issue": "7", "event": "bail", "failed": "leaf said %s\\n and fake-gh-token-value" % token, token: "k"}
    (tmp_path / ".tdd" / "events.jsonl").write_text(json.dumps(line) + "\n")

    carried = run_records.records(str(tmp_path), "7")["events.jsonl"].decode()

    assert json.loads(carried) == {"issue": "7", "event": "bail", "failed": "leaf said [redacted]\\n and [redacted]",
                                   "[redacted]": "k"}


def test_the_ref_carries_what_a_reader_restores_the_journal_lines_the_skill_pin_and_the_timeout_pin(tmp_path, run_records):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text('{"issue": "7", "event": "start"}\n')
    (tmp_path / ".tdd" / "issue-7-skill-commit").write_text("abc1234\n")
    (tmp_path / ".tdd" / "issue-7-timeout").write_text("3600\n")

    (tmp_path / ".tdd" / "issue-7-preflight").write_text("ok\n")

    assert sorted(run_records.records(str(tmp_path), "7")) == ["events.jsonl", "issue-7-skill-commit", "issue-7-timeout"]


def test_the_ref_carries_the_branch_base_the_main_working_tree_recorded_byte_for_byte_4374(tmp_path, run_records):
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    sha = "0123456789abcdef0123456789abcdef01234567"
    (tmp_path / ".tdd" / "issue-7-branch-base").write_text(sha + "\n")

    assert run_records.records(str(run), "7").get("issue-7-branch-base") == (sha + "\n").encode()


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
    """A path as a journal may hold it: as is, JSON-escaped slashes, URL-encoded both ways, with lower-case hex, encoded
    two and three times, in mixed case, and under the macOS prefixes."""
    import urllib.parse
    forms = set()
    for base in {path, "/private" + path, "/System/Volumes/Data" + path}:
        once = urllib.parse.quote(base, safe="")
        forms |= {base, base.replace("/", "\\/"), once, urllib.parse.quote(base, safe="/"),
                  re.sub(r"%[0-9A-F]{2}", lambda m: m.group().lower(), once),
                  urllib.parse.quote(once, safe=""), urllib.parse.quote(urllib.parse.quote(once, safe=""), safe=""),
                  base.swapcase()}
    return sorted(forms)


def _normalized(text):
    """<text> as the fail-closed layer reads it: URL-decoded until it stops changing, escaped slashes and backslashes
    read as `/`, case-folded."""
    import urllib.parse
    for _ in range(6):
        decoded = urllib.parse.unquote(text)
        if decoded == text:
            break
        text = decoded
    return text.replace("\\\\/", "/").replace("\\/", "/").replace("\\\\", "/").casefold()


BONJOUR = ("Plum-Studio", "Studio de Pl\u00fcm")  # names that do not hold the account name, so <user> cannot mask them


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
    import plistlib
    preferences = tmp_path / "preferences.plist"
    preferences.write_bytes(plistlib.dumps({"System": {"Network": {"HostNames": {"LocalHostName": BONJOUR[0]}},
                                                       "System": {"ComputerName": BONJOUR[1]}}}))
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "PREFERENCES", str(preferences), raising=False)
    return home, run, temp


def test_no_carried_byte_holds_a_path_the_account_name_or_a_host_form_in_any_spelling_or_position(
        tmp_path, monkeypatch, run_records):
    import random
    import re
    home, run, temp = _an_account(tmp_path, monkeypatch)
    sensitive = (_spellings(str(home)) + _spellings(str(run)) + _spellings(str(temp))
                 + ["mariox", "MARIOX", HOST, "MacBook-Pro-de-Mariox", "MacBook Pro de Mariox", "macbook-pro-de-mariox.local",
                    "%2Fmariox", "%2fMARIOX", "%252Fmariox", "/x/mariox%2F", *BONJOUR, "mariox-studio.local"])
    pick = random.Random(4079)

    def mixed():
        return "x " + pick.choice(sensitive) + pick.choice(FOLLOWERS) + " y"

    lines = []
    for _n in range(60):
        lines.append({"issue": "7", "event": "launch", "cmd": mixed(), mixed(): mixed(),
                      "detail": {"nested": [mixed(), {"deeper": mixed(), mixed(): "v"}]},
                      "tail": pick.choice(sensitive)})
    (run / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))

    carried = run_records.records(str(run), "7")["events.jsonl"].decode()

    seen = _normalized(carried)
    paths = [_normalized(p) for p in (str(home), str(temp), str(run))]
    leaked = sorted({p for p in paths if re.search(re.escape(p) + r"(?![a-z0-9_-])", seen)})
    words = [w for w in ("mariox", "macbook-pro-de-mariox", "macbook pro de mariox", *[b.casefold() for b in BONJOUR])
             if re.search(r"(?<![a-z0-9<])%s(?![a-z0-9>])" % re.escape(w), seen)]
    parsed = [json.loads(line) for line in carried.splitlines()]
    assert (leaked, words, len(parsed), all({"issue", "event", "cmd", "detail", "tail"} <= set(p) for p in parsed)) == (
        [], [], 60, True)


def test_another_users_path_and_paths_that_only_contain_tmp_are_left_alone(tmp_path, monkeypatch, run_records):
    home, run, temp = _an_account(tmp_path, monkeypatch)
    others = ["%s2/x" % home, "/tmpfoo/y", "/usr/tmp/z", "%s_old" % home]
    (run / ".tdd" / "events.jsonl").write_text(json.dumps({"issue": "7", "event": "note", "paths": others}) + "\n")

    carried = json.loads(run_records.records(str(run), "7")["events.jsonl"])

    assert carried["paths"][1:3] == ["/tmpfoo/y", "/usr/tmp/z"] and carried["paths"][0].endswith("mariox2/x") \
        and not carried["paths"][0].startswith("~")


def test_keys_that_redact_to_the_same_text_are_all_kept_suffixed_so_no_value_is_lost(tmp_path, monkeypatch, run_records):
    home, run, temp = _an_account(tmp_path, monkeypatch)
    line = {"issue": "7", "event": "note", "~": 1, str(home): 2, "/System/Volumes/Data" + str(home): 3}
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(line) + "\n")

    carried = json.loads(run_records.records(str(run), "7")["events.jsonl"])

    assert sorted((k, v) for k, v in carried.items() if k not in ("issue", "event")) == [("~", 1), ("~-2", 2), ("~-3", 3)]


def test_a_value_encoded_seven_times_is_decoded_until_it_stops_changing_and_one_past_fifty_passes_is_replaced_whole(
        tmp_path, monkeypatch, run_records):
    import urllib.parse
    home, run, temp = _an_account(tmp_path, monkeypatch)
    seven = "/mariox"
    for _ in range(7):
        seven = urllib.parse.quote(seven, safe="")
    endless = "%" + "25" * 60 + "x"
    line = {"issue": "7", "event": "note", "seven": "at " + seven, "endless": endless, "plain": "plain"}
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(line) + "\n")

    carried = json.loads(run_records.records(str(run), "7")["events.jsonl"])

    assert (carried["seven"], carried["endless"], carried["plain"]) == ("<redacted>", "<redacted>", "plain")


@pytest.mark.parametrize("spelled", ["Studio+de+Pl%C3%BCm", "Studio de Plüm", "Studio de Pl​üm"])
def test_a_computer_name_form_encoded_decomposed_or_split_by_a_zero_width_character_is_replaced_whole(
        tmp_path, monkeypatch, run_records, spelled):
    home, run, temp = _an_account(tmp_path, monkeypatch)
    line = {"issue": "7", "event": "note", "where": "on " + spelled + " today", "plain": "plain"}
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(line) + "\n")

    carried = json.loads(run_records.records(str(run), "7")["events.jsonl"])

    assert (carried["where"], carried["plain"]) == ("<redacted>", "plain")


def test_a_value_only_the_fail_closed_layer_catches_is_replaced_whole_while_its_siblings_survive(tmp_path, monkeypatch,
                                                                                               run_records):
    home, run, temp = _an_account(tmp_path, monkeypatch)
    hidden = "see %25252F" + "mariox" + " there"
    line = {"issue": "7", "event": "note", "a": hidden, "b": "plain words", "c": 3, hidden: "keyed", "<redacted>": "kept"}
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(line) + "\n")

    carried = json.loads(run_records.records(str(run), "7")["events.jsonl"])

    assert carried == {"issue": "7", "event": "note", "a": "<redacted>", "b": "plain words", "c": 3,
                       "<redacted-2>": "keyed", "<redacted>": "kept"}


def test_redacting_twice_equals_redacting_once_even_for_an_account_named_user_on_a_host_named_host(tmp_path, monkeypatch,
                                                                                                    run_records):
    home, run, temp = _an_account(tmp_path, monkeypatch, host="host")
    monkeypatch.setattr(importlib.import_module("getpass"), "getuser", lambda: "user")
    line = {"issue": "7", "event": "note", "who": "user on host in %s/x and %s" % (home, temp), "user": "host"}
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(line) + "\n")
    once = run_records.records(str(run), "7")["events.jsonl"]
    (run / ".tdd" / "events.jsonl").write_bytes(once)

    twice = run_records.records(str(run), "7")["events.jsonl"]

    assert (twice, b"<<" in once) == (once, False)


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
