"""In-process cases for veri/pid_file.py, the pid-file reader."""
import importlib


def ps_answering(fake_processes, table):
    """Each ps command in <table> ({its words: its output}) answers 0 with that output; any other exits 1, silent."""
    return fake_processes.answers({" ".join(words): (0, out, "") for words, out in table.items()},
                                  default=(1, "", ""), exact=True)


def test_number_in_answers_the_first_lines_digits_as_read(tmp_path):
    pid_file = importlib.import_module("veri.pid_file")
    answers = {}
    for name, content in [
        ("newline", b"12\n"),
        ("padded", b" 12 \t\n"),
        ("no-final-newline", b"12"),
        ("second-line", b"12\nx"),
        ("leading-zeros", b"0012\n"),
    ]:
        path = tmp_path / name
        path.write_bytes(content)
        answers[name] = pid_file.number_in(str(path))

    assert answers == {
        "newline": "12",
        "padded": "12",
        "no-final-newline": "12",
        "second-line": "12",
        "leading-zeros": "0012",
    }


def test_number_in_answers_no_number_for_a_first_line_that_is_not_ascii_digits(tmp_path):
    pid_file = importlib.import_module("veri.pid_file")
    answers = {}
    for name, content in [
        ("empty", b""),
        ("negative", b"-1\n"),
        ("plus", b"+5\n"),
        ("two-numbers", b"1 2\n"),
        ("carriage-return", b"12\r"),
        ("arabic-indic-digit", "١\n".encode()),
        ("digits-on-second-line", b"x\n12\n"),
        ("non-utf8", b"\xff\xfe\n"),
    ]:
        path = tmp_path / name
        path.write_bytes(content)
        try:
            answers[name] = pid_file.number_in(str(path))
        except Exception as error:
            answers[name] = type(error).__name__

    assert answers == {name: None for name in answers}


def test_number_in_answers_no_number_for_a_path_it_cannot_read_as_a_file(tmp_path, monkeypatch):
    import builtins
    import io
    import os

    pid_file = importlib.import_module("veri.pid_file")
    directory = tmp_path / "directory"
    directory.mkdir()
    unreadable = tmp_path / "unreadable"
    unreadable.write_bytes(b"12\n")
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    real_open = builtins.open

    def fake_open(file, *args, **kwargs):
        if os.fspath(file) == str(unreadable):
            raise PermissionError(13, "Permission denied", str(unreadable))
        if os.fspath(file) == str(fifo):
            return io.BytesIO(b"12\n")
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)
    answers = {}
    for name, path in [
        ("missing", tmp_path / "missing"),
        ("directory", directory),
        ("unreadable", unreadable),
        ("fifo", fifo),
    ]:
        try:
            answers[name] = pid_file.number_in(str(path))
        except Exception as error:
            answers[name] = type(error).__name__

    assert answers == {"missing": None, "directory": None, "unreadable": None, "fifo": None}


def test_number_in_follows_a_symlink_to_a_regular_file_and_answers_no_number_for_a_dangling_one(tmp_path):
    pid_file = importlib.import_module("veri.pid_file")
    target = tmp_path / "target"
    target.write_bytes(b"12\n")
    to_file = tmp_path / "to-file"
    to_file.symlink_to(target)
    dangling = tmp_path / "dangling"
    dangling.symlink_to(tmp_path / "nowhere")
    answers = {}
    for name, path in [("to-file", to_file), ("dangling", dangling)]:
        try:
            answers[name] = pid_file.number_in(str(path))
        except Exception as error:
            answers[name] = type(error).__name__

    assert answers == {"to-file": "12", "dangling": None}


def test_live_conductor_answers_the_digits_as_read_and_never_signals_for_no_pid_file_or_0_or_00(tmp_path, monkeypatch, fake_processes):
    import os

    pid_file = importlib.import_module("veri.pid_file")
    kills = []

    def fake_kill(pid, signal):
        kills.append((pid, signal))

    monkeypatch.setattr(os, "kill", fake_kill)
    ps = {
        ("ps", "-o", "command=", "-p", "4242"): "claude -p /tdd 5\n",
        ("ps", "-o", "ppid=", "-p", "4242"): "1004242\n",
        ("ps", "-o", "command=", "-p", "1004242"): "python3 run_conductor.py 5\n",
    }

    ps_answering(fake_processes, ps)
    answers = {}
    calls = {}
    for name, content in [
        ("no-pid-file", None),
        ("live", b"004242\n"),
        ("zero", b"0\n"),
        ("double-zero", b"00\n"),
    ]:
        run_dir = tmp_path / name
        (run_dir / ".tdd").mkdir(parents=True)
        if content is not None:
            (run_dir / ".tdd" / "conductor.pid").write_bytes(content)
        kills.clear()
        answers[name] = pid_file.live_conductor(str(run_dir))
        calls[name] = list(kills)

    assert (answers, calls) == (
        {"no-pid-file": None, "live": "004242", "zero": None, "double-zero": None},
        {"no-pid-file": [], "live": [(4242, 0)], "zero": [], "double-zero": []},
    )


def test_live_conductor_answers_no_pid_and_raises_nothing_when_os_kill_raises(tmp_path, monkeypatch):
    import os

    pid_file = importlib.import_module("veri.pid_file")
    raised = {}

    def fake_kill(pid, signal):
        raise raised["error"]

    monkeypatch.setattr(os, "kill", fake_kill)
    answers = {}
    for name, error in [
        ("permission", PermissionError(1, "Operation not permitted")),
        ("lookup", ProcessLookupError(3, "No such process")),
        ("overflow", OverflowError("signed integer is greater than maximum")),
    ]:
        run_dir = tmp_path / name
        (run_dir / ".tdd").mkdir(parents=True)
        (run_dir / ".tdd" / "conductor.pid").write_bytes(b"4242\n")
        raised["error"] = error
        try:
            answers[name] = pid_file.live_conductor(str(run_dir))
        except Exception as error:
            answers[name] = type(error).__name__

    assert answers == {"permission": None, "lookup": None, "overflow": None}


def test_supervising_runs_ps_for_the_pids_args_and_is_true_only_when_they_name_the_leafs_supervisor(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    answered = {}
    fake = fake_processes.answers({"ps": lambda line, **kwargs: (answered["ps"][0], answered["ps"][1], "")})
    answers = {}
    for name, ps in [
        ("supervisor", (0, "bash /x/supervise.sh develop-red-3 claude -p\n")),
        ("ps-exits-1", (1, "bash /x/supervise.sh develop-red-3 claude -p\n")),
        ("ps-answers-empty", (0, "")),
    ]:
        answered["ps"] = ps
        answers[name] = pid_file.supervising("4242", "develop-red-3")

    assert (answers, fake.argvs) == (
        {"supervisor": True, "ps-exits-1": False, "ps-answers-empty": False},
        [["ps", "-p", "4242", "-o", "args="]] * 3,
    )


def test_supervising_matches_the_literal_text_supervise_sh_name_with_its_trailing_space(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    answered = {}
    fake_processes.answers({"ps": lambda line, **kwargs: (0, answered["ps"], "")})
    answers = {}
    for case, name, ps in [
        ("nothing-after-the-name", "develop-red-3", "supervise.sh develop-red-3\n"),
        ("name-is-a-prefix", "develop-red", "supervise.sh develop-red-3 x\n"),
        ("glob-in-the-name", "a*", "supervise.sh abc x\n"),
    ]:
        answered["ps"] = ps
        answers[case] = pid_file.supervising("4242", name)

    assert answers == {"nothing-after-the-name": False, "name-is-a-prefix": False, "glob-in-the-name": False}


def test_supervising_recognises_a_supervisor_spelled_veri_supervise_py_as_well_as_supervise_sh(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    answered = {}
    fake_processes.answers({"ps": lambda line, **kwargs: (0, answered["ps"], "")})
    answers = {}
    for case, name, ps in [
        ("python-supervisor", "develop-red-3", "python3 /x/veri/supervise.py develop-red-3 claude -p\n"),
        ("bash-supervisor", "develop-red-3", "bash /x/supervise.sh develop-red-3 claude -p\n"),
        ("python-nothing-after-the-name", "develop-red-3", "python3 /x/veri/supervise.py develop-red-3\n"),
        ("python-name-is-a-prefix", "develop-red", "python3 /x/veri/supervise.py develop-red-3 x\n"),
    ]:
        answered["ps"] = ps
        answers[case] = pid_file.supervising("4242", name)

    assert answers == {
        "python-supervisor": True,
        "bash-supervisor": True,
        "python-nothing-after-the-name": False,
        "python-name-is-a-prefix": False,
    }


def test_live_conductor_answers_no_pid_for_a_live_claude_whose_parent_is_not_run_conductor_2249(tmp_path, monkeypatch, fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    ps = {
        ("ps", "-o", "command=", "-p", "4242"): "claude -p /tdd 5\n",
        ("ps", "-o", "ppid=", "-p", "4242"): "1004242\n",
        ("ps", "-o", "command=", "-p", "1004242"): "/Applications/Claude.app/claude-desktop\n",
    }

    ps_answering(fake_processes, ps)
    run_dir = tmp_path / "run"
    (run_dir / ".tdd").mkdir(parents=True)
    (run_dir / ".tdd" / "conductor.pid").write_bytes(b"4242\n")

    assert pid_file.live_conductor(str(run_dir)) is None


def test_live_conductor_answers_no_pid_for_a_live_process_under_run_conductor_that_is_not_a_claude_2249(tmp_path, monkeypatch, fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    ps = {
        ("ps", "-o", "command=", "-p", "4242"): "sleep 600\n",
        ("ps", "-o", "ppid=", "-p", "4242"): "1004242\n",
        ("ps", "-o", "command=", "-p", "1004242"): "python3 run_conductor.py 5\n",
    }

    ps_answering(fake_processes, ps)
    run_dir = tmp_path / "run"
    (run_dir / ".tdd").mkdir(parents=True)
    (run_dir / ".tdd" / "conductor.pid").write_bytes(b"4242\n")

    assert pid_file.live_conductor(str(run_dir)) is None


def test_live_conductor_answers_the_pid_of_a_live_conductor_and_none_once_the_pid_is_reused_by_an_unrelated_process_2249(tmp_path, monkeypatch, fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    ps = {
        ("ps", "-o", "command=", "-p", "4242"): "claude -p /tdd 5\n",
        ("ps", "-o", "ppid=", "-p", "4242"): "1004242\n",
        ("ps", "-o", "command=", "-p", "1004242"): "python3 run_conductor.py 5\n",
        ("ps", "-o", "command=", "-p", "5151"): "vim notes.txt\n",
        ("ps", "-o", "ppid=", "-p", "5151"): "1\n",
        ("ps", "-o", "command=", "-p", "1"): "/sbin/launchd\n",
    }

    ps_answering(fake_processes, ps)
    answers = {}
    for name, recorded in [("conductor", b"4242\n"), ("reused", b"5151\n")]:
        run_dir = tmp_path / name
        (run_dir / ".tdd").mkdir(parents=True)
        (run_dir / ".tdd" / "conductor.pid").write_bytes(recorded)
        answers[name] = pid_file.live_conductor(str(run_dir))

    assert answers == {"conductor": "4242", "reused": None}


def test_live_conductor_answers_the_pid_when_its_own_ps_command_read_fails_or_prints_nothing_2320(tmp_path, monkeypatch, fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    own = {}
    ps = {
        ("ps", "-o", "ppid=", "-p", "4242"): "1004242\n",
        ("ps", "-o", "command=", "-p", "1004242"): "python3 run_conductor.py 5\n",
    }

    fake_processes.answers({
        **{" ".join(words): (0, out, "") for words, out in ps.items()},
        "ps -o command= -p 4242": lambda line, **kwargs: (own["returncode"], own["stdout"], ""),
    }, exact=True)
    run_dir = tmp_path / "run"
    (run_dir / ".tdd").mkdir(parents=True)
    (run_dir / ".tdd" / "conductor.pid").write_bytes(b"4242\n")
    answers = {}
    for name, returncode, stdout in [("ps-fails", 1, ""), ("ps-prints-nothing", 0, "\n")]:
        own.update(returncode=returncode, stdout=stdout)
        answers[name] = pid_file.live_conductor(str(run_dir))

    assert answers == {"ps-fails": "4242", "ps-prints-nothing": "4242"}


def test_live_conductor_answers_the_pid_when_its_ps_ppid_read_fails_or_prints_nothing_2320(tmp_path, monkeypatch, fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    parent = {}

    fake_processes.answers({
        "ps -o ppid= -p 4242": lambda line, **kwargs: (parent["returncode"], parent["stdout"], ""),
        "ps -o command= -p 4242": (0, "claude -p /tdd 5\n", ""),
    }, default=(1, "", ""), exact=True)
    run_dir = tmp_path / "run"
    (run_dir / ".tdd").mkdir(parents=True)
    (run_dir / ".tdd" / "conductor.pid").write_bytes(b"4242\n")
    answers = {}
    for name, returncode, stdout in [("ps-fails", 1, ""), ("ps-prints-nothing", 0, "\n")]:
        parent.update(returncode=returncode, stdout=stdout)
        try:
            answers[name] = pid_file.live_conductor(str(run_dir))
        except Exception as error:
            answers[name] = type(error).__name__

    assert answers == {"ps-fails": "4242", "ps-prints-nothing": "4242"}


def test_live_conductor_answers_the_pid_when_its_parents_ps_command_read_fails_or_prints_nothing_2320(tmp_path, monkeypatch, fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    parent = {}

    fake_processes.answers({
        "ps -o command= -p 1004242": lambda line, **kwargs: (parent["returncode"], parent["stdout"], ""),
        "ps -o ppid= -p 4242": (0, "1004242\n", ""),
        "ps -o command= -p 4242": (0, "claude -p /tdd 5\n", ""),
    }, default=(1, "", ""), exact=True)
    run_dir = tmp_path / "run"
    (run_dir / ".tdd").mkdir(parents=True)
    (run_dir / ".tdd" / "conductor.pid").write_bytes(b"4242\n")
    answers = {}
    for name, returncode, stdout in [("ps-fails", 1, ""), ("ps-prints-nothing", 0, "\n")]:
        parent.update(returncode=returncode, stdout=stdout)
        try:
            answers[name] = pid_file.live_conductor(str(run_dir))
        except Exception as error:
            answers[name] = type(error).__name__

    assert answers == {"ps-fails": "4242", "ps-prints-nothing": "4242"}


def test_live_conductor_answers_no_pid_for_a_readable_command_line_that_does_not_match_when_every_ps_read_answers_2320(tmp_path, monkeypatch, fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    ps = {
        ("ps", "-o", "ppid=", "-p", "4242"): "1004242\n",
        ("ps", "-o", "command=", "-p", "4242"): {"stranger-parent": "claude -p /tdd 5\n", "not-claude": "sleep 600\n"},
        ("ps", "-o", "command=", "-p", "1004242"): {"stranger-parent": "/Applications/Claude.app/claude-desktop\n", "not-claude": "python3 run_conductor.py 5\n"},
    }
    case = {}

    def read(words):
        def answer(line, **kwargs):
            out = ps[words]
            return 0, out[case["name"]] if isinstance(out, dict) else out, ""
        return answer

    fake_processes.answers({" ".join(words): read(words) for words in ps}, exact=True)
    run_dir = tmp_path / "run"
    (run_dir / ".tdd").mkdir(parents=True)
    (run_dir / ".tdd" / "conductor.pid").write_bytes(b"4242\n")
    answers = {}
    for name in ["stranger-parent", "not-claude"]:
        case["name"] = name
        answers[name] = pid_file.live_conductor(str(run_dir))

    assert answers == {"stranger-parent": None, "not-claude": None}


def test_ps_answers_a_non_zero_exit_with_a_value_distinct_from_an_empty_field_2537(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    ps = {}
    fake_processes.answers({"ps": lambda line, **kwargs: (ps["answer"][0], ps["answer"][1], "")})
    answers = {}
    for name, answer in [("no-such-process", (1, "")), ("empty-field", (0, "\n"))]:
        ps["answer"] = answer
        answers[name] = pid_file.ps_field("lstart", 4242)

    assert answers["empty-field"] == ""
    assert answers["no-such-process"] != answers["empty-field"]


def test_ps_answers_a_ps_that_could_not_be_run_apart_from_no_such_process_and_an_empty_field_2537(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    ps = {}

    def answer(line, **kwargs):
        if ps["answer"] == "unrunnable":
            raise FileNotFoundError(2, "No such file or directory", "ps")
        return ps["answer"][0], ps["answer"][1], ""

    fake_processes.answers({"ps": answer})
    answers = {}
    for name, answer in [("no-such-process", (1, "")), ("empty-field", (0, "\n")), ("unrunnable", "unrunnable")]:
        ps["answer"] = answer
        try:
            answers[name] = pid_file.ps_field("lstart", 4242)
        except Exception as error:
            answers[name] = type(error).__name__

    assert answers["unrunnable"] not in (answers["no-such-process"], answers["empty-field"])
    assert answers["unrunnable"] != "FileNotFoundError"


def test_live_conductor_answers_no_pid_for_a_claude_under_run_conductor_whose_start_time_differs_from_the_recorded_one_2537(tmp_path, monkeypatch, fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    ps = {
        ("ps", "-o", "command=", "-p", "4242"): "claude -p /tdd 7\n",
        ("ps", "-o", "ppid=", "-p", "4242"): "1004242\n",
        ("ps", "-o", "command=", "-p", "1004242"): "python3 run_conductor.py 7\n",
        ("ps", "-o", "lstart=", "-p", "4242"): "Tue Oct 27 13:45:10 2026\n",
    }

    ps_answering(fake_processes, ps)
    run_dir = tmp_path / "run"
    (run_dir / ".tdd").mkdir(parents=True)
    (run_dir / ".tdd" / "conductor.pid").write_bytes(b"4242\nMon Oct 26 09:00:00 2026\n")

    assert pid_file.live_conductor(str(run_dir)) is None


def test_starting_runs_names_no_issue_whose_run_conductor_process_works_in_another_repo_3247(tmp_path, fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    root = tmp_path / "repo"
    other = tmp_path / "other"
    for issue in ("103", "104"):
        (root / ".tdd" / "wt" / issue / ".tdd").mkdir(parents=True)
    ps = "  500 /usr/bin/python3 /x/run_conductor.py 103\n  501 /usr/bin/python3 /x/run_conductor.py 104\n"
    cwds = {"500": str(other), "501": str(root)}

    fake_processes.answers({"ps": (0, ps, "")},
                           default=lambda line, **kwargs: (0, "n%s\n" % cwds[line.split()[-1]], ""))

    assert pid_file.starting_runs(str(root)) == ["104"]


def test_starting_runs_names_no_issue_for_a_process_that_only_mentions_run_conductor_in_its_command_3448(tmp_path, fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    root = tmp_path / "repo"
    (root / ".tdd" / "wt" / "103" / ".tdd").mkdir(parents=True)
    ps = "  500 claude -p review run_conductor.py 103 now\n  501 grep run_conductor.py 103\n"

    fake_processes.answers({"ps": (0, ps, "")}, default=(0, "n%s\n" % root, ""))

    assert pid_file.starting_runs(str(root)) == []


def test_starting_runs_names_the_issue_of_a_run_conductor_script_started_under_bin_sh_3448(tmp_path, fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    root = tmp_path / "repo"
    (root / ".tdd" / "wt" / "777" / ".tdd").mkdir(parents=True)
    ps = "  500 /bin/sh /x/run_conductor.py 777 /tmp/claude.pid\n"

    fake_processes.answers({"ps": (0, ps, "")}, default=(0, "n%s\n" % root, ""))

    assert pid_file.starting_runs(str(root)) == ["777"]


def test_ancestors_names_this_process_and_every_parent_up_to_pid_1(fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    me = os.getpid()
    ps_answering(fake_processes, {
        ("ps", "-o", "ppid=", "-p", str(me)): "700\n",
        ("ps", "-o", "ppid=", "-p", "700"): "300\n",
        ("ps", "-o", "ppid=", "-p", "300"): "1\n",
    })

    assert pid_file.ancestors() == {me, 700, 300}


def test_ancestors_stops_at_a_parent_ps_cannot_read_and_at_a_cycle(fake_processes):
    import os
    pid_file = importlib.import_module("veri.pid_file")
    me = os.getpid()
    answers = {}
    for name, table in [
        ("vanished-parent", {("ps", "-o", "ppid=", "-p", str(me)): "700\n"}),
        ("empty-field", {("ps", "-o", "ppid=", "-p", str(me)): "\n"}),
        ("cycle", {("ps", "-o", "ppid=", "-p", str(me)): "700\n", ("ps", "-o", "ppid=", "-p", "700"): str(me) + "\n"}),
    ]:
        ps_answering(fake_processes, table)
        answers[name] = pid_file.ancestors()

    assert answers == {"vanished-parent": {me, 700}, "empty-field": {me}, "cycle": {me, 700}}


def test_listing_answers_the_process_table_as_ps_prints_it_and_asks_once(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    fake = fake_processes.answers({"ps": (0, " 11 sh a\n 12 b c\n", "")})

    text = pid_file.listing()

    assert (text, fake.argvs) == (" 11 sh a\n 12 b c\n", [["ps", "-axo", "pid=,command="]])


def test_listing_leaves_ps_stderr_alone_unless_asked_to_be_quiet(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    fake = fake_processes.answers({"ps": (0, "", "")})

    pid_file.listing()
    pid_file.listing(quiet=True)

    assert [kwargs.get("stderr") is not None for _, kwargs in fake.seen] == [False, True]


def test_listing_answers_what_a_failing_ps_printed_and_raises_when_ps_is_missing(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    fake_processes.answers({"ps": (1, "partial\n", "")})
    assert pid_file.listing() == "partial\n"

    fake_processes.answers({"ps": FileNotFoundError(2, "No such file or directory", "ps")})
    try:
        pid_file.listing()
    except FileNotFoundError:
        raised = True
    else:
        raised = False
    assert raised


def test_argument_lines_answers_each_process_arguments_and_raises_when_ps_fails(fake_processes):
    import subprocess
    pid_file = importlib.import_module("veri.pid_file")
    fake = fake_processes.answers({"ps": [(0, "sh a b\nclaude\n", ""), (1, "", "")]})

    text = pid_file.argument_lines()
    try:
        pid_file.argument_lines()
    except subprocess.CalledProcessError:
        raised = True
    else:
        raised = False

    assert (text, raised, fake.argvs[0]) == ("sh a b\nclaude\n", True, ["ps", "-axo", "args="])


def test_started_as_answers_the_start_time_text_ps_prints_stripped_whatever_ps_exits(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    fake = fake_processes.answers({"ps": [(0, "Mon Nov  2 10:00:00 2026\n", ""), (1, "", ""), (1, "stale \n", "")]})

    answers = [pid_file.started_as(4242), pid_file.started_as("4243"), pid_file.started_as(4244)]

    assert answers == ["Mon Nov  2 10:00:00 2026", "", "stale"]
    assert fake.argvs == [["ps", "-o", "lstart=", "-p", "4242"], ["ps", "-o", "lstart=", "-p", "4243"],
                          ["ps", "-o", "lstart=", "-p", "4244"]]


def test_started_as_raises_when_ps_is_missing(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    fake_processes.answers({"ps": FileNotFoundError(2, "No such file or directory", "ps")})

    try:
        pid_file.started_as(1)
    except FileNotFoundError:
        raised = True
    else:
        raised = False

    assert raised


def test_pids_matching_answers_the_pids_pgrep_prints_in_order_and_none_when_it_prints_nothing(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    fake = fake_processes.answers({"pgrep": [(0, "31\n7\n", ""), (1, "", "")]})

    answers = [pid_file.pids_matching("report-cache.sh refresh"), pid_file.pids_matching("x")]

    assert answers == [["31", "7"], []]
    assert fake.argvs[0] == ["pgrep", "-f", "report-cache.sh refresh"]


def test_commands_of_answers_ps_pid_and_command_lines_for_the_pids_in_one_call(fake_processes):
    pid_file = importlib.import_module("veri.pid_file")
    fake = fake_processes.answers({"ps": (0, "31 /s/report-cache.sh refresh\n", "")})

    text = pid_file.commands_of(["31", "7"])

    assert (text, fake.argvs) == ("31 /s/report-cache.sh refresh\n", [["ps", "-p", "31,7", "-o", "pid=,command="]])


def test_an_atomic_record_replaces_the_pid_file_only_by_rename_so_a_failed_write_leaves_the_old_text_and_no_other_file_3993(
        tmp_path, fake_processes, monkeypatch):
    pid_file = importlib.import_module("veri.pid_file")
    ps_answering(fake_processes, {("ps", "-o", "lstart=", "-p", "77"): "Sun Nov 15 22:00:00 2026\n"})
    path = tmp_path / "holder"
    path.write_text("12\nSat Nov 14 10:00:00 2026\n")

    def refused(source, target):
        raise OSError(28, "No space left on device", target)

    monkeypatch.setattr(pid_file.os, "replace", refused)
    try:
        pid_file.record(str(path), 77, atomic=True)
        raised = False
    except OSError:
        raised = True

    assert (raised, path.read_text(), sorted(p.name for p in tmp_path.iterdir())) == (
        True, "12\nSat Nov 14 10:00:00 2026\n", ["holder"])
