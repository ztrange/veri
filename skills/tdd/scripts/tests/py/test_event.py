"""In-process cases for veri/event.py, the module event.sh is a shim over."""
import importlib
import json
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: event.sh <event> [key=value …]\n".encode()
REASONS = b"candidates-done, budget-spent, nothing-structural"


@pytest.fixture
def event():
    return importlib.import_module("veri.event")


def test_main_refuses_a_missing_event_and_each_bad_structural_pass_with_exit_2_creating_no_tdd_and_accepts_a_plain_mark(
        monkeypatch, tmp_path, capsysbinary, event):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)

    refusals = []
    for argv in ([], [""],
                 ["structural-pass", "stopped=test-files-only"],
                 ["structural-pass", "transforms=0"],
                 ["structural-pass", "transforms=0", "budget=10", "stopped=budget-spent"]):
        code = event.main(argv)
        refusals.append((argv, code, capsysbinary.readouterr(), sorted(os.listdir(tmp_path))))

    assert refusals == [
        ([], 2, (b"", USAGE), []),
        ([""], 2, (b"", USAGE), []),
        (["structural-pass", "stopped=test-files-only"], 2,
         (b"", b"event.sh: structural-pass stopped=test-files-only is not one of " + REASONS + b"\n"), []),
        (["structural-pass", "transforms=0"], 2,
         (b"", b"event.sh: structural-pass needs stopped=, one of " + REASONS + b"\n"), []),
        (["structural-pass", "transforms=0", "budget=10", "stopped=budget-spent"], 2,
         (b"", b"event.sh: structural-pass stopped=budget-spent needs transforms equal to budget,"
               b" got transforms=0 budget=10\n"), []),
    ]
    assert event.main(["x"]) == 0


CONTEXT = ("VERI_ISSUE", "VERI_ACTOR", "VERI_PHASE", "VERI_STEP", "VERI_ATTEMPT", "VERI_SKILL_COMMIT")


def test_main_appends_the_nine_fixed_keys_then_one_key_per_argument_in_argument_order(
        monkeypatch, tmp_path, event):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)
    monkeypatch.setattr("time.time", lambda: 1700000000.9)
    monkeypatch.setattr("time.clock_gettime", lambda clock: 4242.7)

    def context(values):
        for name, value in zip(CONTEXT, values):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)

    for values, argv in (
            (("12", "conductor", "red", "3", "2", "abc123"),
             ["launch", "z=1", "a=2", "a=3", "issue=9", "bare", "a=b=c", "=x", "k="]),
            ((None,) * 6, ["-h"]),
            (("",) * 6, ["mark"]),
    ):
        context(values)
        assert event.main(argv) == 0

    assert (tmp_path / ".tdd" / "events.jsonl").read_bytes() == (
        b'{"ts": 1700000000, "awake": 4242, "issue": "12", "actor": "conductor", "phase": "red",'
        b' "step": "3", "event": "launch", "attempt": "2", "skill_commit": "abc123",'
        b' "z": "1", "a": "2", "a": "3", "issue": "9", "bare": "", "a": "b=c", "": "x", "k": ""}\n'
        b'{"ts": 1700000000, "awake": 4242, "issue": "", "actor": "", "phase": "", "step": "",'
        b' "event": "-h", "attempt": "", "skill_commit": ""}\n'
        b'{"ts": 1700000000, "awake": 4242, "issue": "", "actor": "", "phase": "", "step": "",'
        b' "event": "mark", "attempt": "", "skill_commit": ""}\n'
    )


def test_main_escapes_every_string_by_the_bash_table_over_the_argument_and_variable_bytes(
        monkeypatch, tmp_path, event):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)
    monkeypatch.setattr("time.time", lambda: 1700000000.9)
    monkeypatch.setattr("time.clock_gettime", lambda clock: 4242.7)
    for name in CONTEXT:
        monkeypatch.delenv(name, raising=False)

    well = "\"\\\b\f\n\r\t\x01\x1f\x7fAé€\U0001F600"
    well_escaped = b'\\"\\\\\\b\\f\\n\\r\\t\\u0001\\u001f\\u007fA\\u00e9\\u20ac\\ud83d\\ude00'
    malformed = os.fsdecode(b"\x80|\xe2\x82Z")
    malformed_escaped = b"\\u0080|\\u209a"
    monkeypatch.setenv("VERI_ACTOR", well)
    monkeypatch.setenv("VERI_PHASE", malformed)

    assert well_escaped == json.dumps(well, ensure_ascii=True)[1:-1].encode()
    assert event.main([well, "w=" + well, "m=" + malformed, 'q"k=v']) == 0

    assert (tmp_path / ".tdd" / "events.jsonl").read_bytes() == (
        b'{"ts": 1700000000, "awake": 4242, "issue": "", "actor": "' + well_escaped
        + b'", "phase": "' + malformed_escaped + b'", "step": "", "event": "' + well_escaped
        + b'", "attempt": "", "skill_commit": "", "w": "' + well_escaped
        + b'", "m": "' + malformed_escaped + b'", "q\\"k": "v"}\n'
    )


def test_main_appends_the_whole_line_in_one_os_write_on_an_o_append_descriptor_relative_to_the_working_directory_and_raises_oserror_when_tdd_or_the_log_is_not_writable(
        monkeypatch, tmp_path, event):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)
    monkeypatch.setattr("time.time", lambda: 1700000000.9)
    monkeypatch.setattr("time.clock_gettime", lambda clock: 4242.7)
    for name in CONTEXT:
        monkeypatch.delenv(name, raising=False)

    calls = []
    real_open, real_write = os.open, os.write

    def spy_open(path, flags, mode=0o777, **kwargs):
        fd = real_open(path, flags, mode, **kwargs)
        calls.append(("open", os.fspath(path), flags, mode, fd))
        return fd

    def spy_write(fd, data):
        calls.append(("write", fd, bytes(data)))
        return real_write(fd, data)

    monkeypatch.setattr("os.open", spy_open)
    monkeypatch.setattr("os.write", spy_write)

    first = (b'{"ts": 1700000000, "awake": 4242, "issue": "", "actor": "", "phase": "", "step": "",'
             b' "event": "one", "attempt": "", "skill_commit": "", "k": "' + b"v" * 9000 + b'"}\n')
    second = (b'{"ts": 1700000000, "awake": 4242, "issue": "", "actor": "", "phase": "", "step": "",'
              b' "event": "two", "attempt": "", "skill_commit": ""}\n')
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
    for argv, text in ((["one", "k=" + "v" * 9000], first), (["two"], second)):
        calls.clear()
        assert event.main(argv) == 0
        fd = calls[0][-1] if calls else None
        assert [call for call in calls if call[0] == "write"] == [("write", fd, text)]
        assert [call[:4] for call in calls if call[0] == "open"] == [("open", ".tdd/events.jsonl", flags, 0o666)]
    assert (work / ".tdd" / "events.jsonl").read_bytes() == first + second
    assert sorted(os.listdir(tmp_path)) == ["work"]

    blocked = tmp_path / "blocked"
    blocked.mkdir()
    (blocked / ".tdd").write_bytes(b"not a directory")
    monkeypatch.chdir(blocked)
    with pytest.raises(OSError):
        event.main(["three"])
    assert (blocked / ".tdd").read_bytes() == b"not a directory"

    shadowed = tmp_path / "shadowed"
    (shadowed / ".tdd" / "events.jsonl").mkdir(parents=True)
    monkeypatch.chdir(shadowed)
    with pytest.raises(OSError):
        event.main(["four"])
    assert os.listdir(shadowed / ".tdd" / "events.jsonl") == []


def test_main_runs_veri_awake_clock_as_one_argv_word_on_path_writing_its_stdout_raw_and_maps_its_status_after_creating_tdd(
        monkeypatch, tmp_path, capfd, event):
    monkeypatch.setattr("time.time", lambda: 1700000000.9)
    monkeypatch.setattr("time.clock_gettime", lambda clock: 4242.7)
    for name in CONTEXT:
        monkeypatch.delenv(name, raising=False)

    bin_dir, spaced = tmp_path / "bin", tmp_path / "a b"
    bin_dir.mkdir()
    spaced.mkdir()
    (tmp_path / "notexec").mkdir()
    log = tmp_path / "starts"
    clocks = {
        bin_dir / "myclock": '#!/bin/sh\nread line\necho "$line" >> "$LOG"\necho clock-err >&2\nprintf \'abc\\n\\n\'\n',
        spaced / "empty": '#!/bin/sh\necho start >> "$LOG"\n',
        bin_dir / "noshebang": "printf '9\\n'\n",
        bin_dir / "fails": "#!/bin/sh\necho 5\nexit 1\n",
        bin_dir / "nothing": "#!/bin/sh\necho 5\nexit 3\n",
        bin_dir / "outofrange": "#!/bin/sh\necho 5\nexit 4\n",
        bin_dir / "killed": "#!/bin/sh\necho 5\nkill -TERM $$\n",
    }
    for path, text in clocks.items():
        path.write_text(text)
        path.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    monkeypatch.setenv("LOG", str(log))

    stdin = tmp_path / "stdin"
    stdin.write_bytes(b"fed\n")
    saved = os.dup(0)
    results = []
    try:
        for clock in ("myclock", str(spaced / "empty"), "noshebang", "fails", "nothing", "outofrange", "killed", "nosuchclock",
                      str(tmp_path / "notexec")):
            work = tmp_path / ("work-" + pathlib.Path(clock).name)
            work.mkdir()
            (work / "noshebang").write_text("printf '7\\n'\n")
            monkeypatch.chdir(work)
            monkeypatch.setenv("VERI_AWAKE_CLOCK", clock)
            log.write_bytes(b"")
            with open(stdin, "rb") as feed:
                os.dup2(feed.fileno(), 0)
            code = event.main(["mark"])
            out, err = capfd.readouterr()
            logged = (work / ".tdd" / "events.jsonl").read_bytes() if (work / ".tdd" / "events.jsonl").exists() else None
            results.append((pathlib.Path(clock).name, code, logged, sorted(os.listdir(work / ".tdd")),
                            log.read_bytes(), out, "clock-err" in err))
    finally:
        os.dup2(saved, 0)
        os.close(saved)

    def line(awake):
        return (b'{"ts": 1700000000, "awake": ' + awake + b', "issue": "", "actor": "", "phase": "",'
                b' "step": "", "event": "mark", "attempt": "", "skill_commit": ""}\n')

    assert results == [
        ("myclock", 0, line(b"abc"), ["events.jsonl"], b"fed\n", "", True),
        ("empty", 0, line(b""), ["events.jsonl"], b"start\n", "", False),
        ("noshebang", 0, line(b"9"), ["events.jsonl"], b"", "", False),
        ("fails", 1, None, [], b"", "", False),
        ("nothing", 3, None, [], b"", "", False),
        ("outofrange", 2, None, [], b"", "", False),
        ("killed", 2, None, [], b"", "", False),
        ("nosuchclock", 2, None, [], b"", "", False),
        ("notexec", 2, None, [], b"", "", False),
    ]


def test_main_reads_awake_in_process_from_clock_uptime_raw_where_time_has_it_and_clock_monotonic_where_it_does_not_starting_no_process(
        monkeypatch, tmp_path, event):
    monkeypatch.setattr("time.time", lambda: 1700000000.9)
    monkeypatch.setattr("time.CLOCK_UPTIME_RAW", "uptime-raw", raising=False)
    monkeypatch.setattr("time.CLOCK_MONOTONIC", "monotonic")
    readings = {"uptime-raw": 111.9, "monotonic": 222.9}
    monkeypatch.setattr("time.clock_gettime", lambda clock: readings[clock])
    for name in CONTEXT:
        monkeypatch.delenv(name, raising=False)

    started = []

    def refuse(*args, **kwargs):
        started.append(args)
        raise AssertionError("a default mark started a process")

    for name in ("Popen", "run", "call", "check_call", "check_output"):
        monkeypatch.setattr(f"subprocess.{name}", refuse)

    awake = []
    for platform in ("uptime-raw", "monotonic"):
        if platform == "monotonic":
            monkeypatch.delattr("time.CLOCK_UPTIME_RAW")
        for clock in (None, ""):
            work = tmp_path / f"{platform}-{clock is None}"
            work.mkdir()
            monkeypatch.chdir(work)
            if clock is None:
                monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)
            else:
                monkeypatch.setenv("VERI_AWAKE_CLOCK", clock)
            code = event.main(["mark"])
            awake.append((platform, clock, code, json.loads((work / ".tdd" / "events.jsonl").read_bytes())["awake"]))

    assert (awake, started) == ([
        ("uptime-raw", None, 0, 111),
        ("uptime-raw", "", 0, 111),
        ("monotonic", None, 0, 222),
        ("monotonic", "", 0, 222),
    ], [])


def test_main_checks_structural_pass_only_for_that_event_in_argument_order_comparing_transforms_and_budget_as_strings_before_tdd_or_the_clock(
        monkeypatch, tmp_path, capsysbinary, event):
    monkeypatch.setattr("time.time", lambda: 1700000000.9)
    monkeypatch.setenv("VERI_AWAKE_CLOCK", "spyclock")
    started = []

    def clock(args, **kwargs):
        started.append(args)
        return subprocess.CompletedProcess(args, 0, b"5\n")

    monkeypatch.setattr("subprocess.run", clock)

    def refused(text):
        return (2, b"event.sh: structural-pass " + text + b"\n", [], 0)

    accepted = (0, b"", [".tdd"], 1)
    cases = [
        (["structural-passx", "stopped=bogus"], accepted),
        (["x", "stopped=bogus", "transforms=1"], accepted),
        (["structural-pass", "stopped=bogus", "stopped=candidates-done"],
         refused(b"stopped=bogus is not one of " + REASONS)),
        (["structural-pass", "stopped=candidates-done", "stopped=bogus"],
         refused(b"stopped=bogus is not one of " + REASONS)),
        (["structural-pass", "stopped=candidates-done", "stopped=budget-spent", "transforms=1", "budget=2"],
         refused(b"stopped=budget-spent needs transforms equal to budget, got transforms=1 budget=2")),
        (["structural-pass", "stopped=budget-spent", "stopped=nothing-structural", "transforms=1", "budget=2"], accepted),
        (["structural-pass", "transforms=1", "budget=2", "transforms=2", "stopped=budget-spent"], accepted),
        (["structural-pass", "transforms=3", "budget=3", "budget=4", "stopped=budget-spent"],
         refused(b"stopped=budget-spent needs transforms equal to budget, got transforms=3 budget=4")),
        (["structural-pass", "stopped="], refused(b"stopped= is not one of " + REASONS)),
        (["structural-pass", "stopped=budget-spent", "transforms=10", "budget=010"],
         refused(b"stopped=budget-spent needs transforms equal to budget, got transforms=10 budget=010")),
        (["structural-pass", "stopped=budget-spent"], accepted),
    ]

    observed = []
    for index, (argv, _) in enumerate(cases):
        work = tmp_path / str(index)
        work.mkdir()
        monkeypatch.chdir(work)
        del started[:]
        code = event.main(argv)
        observed.append((argv, (code, capsysbinary.readouterr().err, sorted(os.listdir(work)), len(started))))

    assert observed == cases
