"""In-process cases for veri/pid_file.py, the pid-file reader lib/number-in.sh and lib/pid-file.sh define in bash."""
import importlib


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


def test_live_conductor_answers_the_digits_as_read_and_never_signals_for_no_pid_file_or_0_or_00(tmp_path, monkeypatch):
    import os

    pid_file = importlib.import_module("veri.pid_file")
    kills = []

    def fake_kill(pid, signal):
        kills.append((pid, signal))

    monkeypatch.setattr(os, "kill", fake_kill)
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


def test_supervising_runs_ps_for_the_pids_args_and_is_true_only_when_they_name_the_leafs_supervisor(monkeypatch):
    import subprocess

    pid_file = importlib.import_module("veri.pid_file")
    answered = {}
    argvs = []

    def fake_run(argv, *args, **kwargs):
        argvs.append(list(argv))
        returncode, stdout = answered["ps"]
        return subprocess.CompletedProcess(argv, returncode, stdout=stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    answers = {}
    for name, ps in [
        ("supervisor", (0, "bash /x/supervise.sh develop-red-3 claude -p\n")),
        ("ps-exits-1", (1, "bash /x/supervise.sh develop-red-3 claude -p\n")),
        ("ps-answers-empty", (0, "")),
    ]:
        answered["ps"] = ps
        answers[name] = pid_file.supervising("4242", "develop-red-3")

    assert (answers, argvs) == (
        {"supervisor": True, "ps-exits-1": False, "ps-answers-empty": False},
        [["ps", "-p", "4242", "-o", "args="]] * 3,
    )


def test_supervising_matches_the_literal_text_supervise_sh_name_with_its_trailing_space(monkeypatch):
    import subprocess

    pid_file = importlib.import_module("veri.pid_file")
    answered = {}

    def fake_run(argv, *args, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout=answered["ps"], stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    answers = {}
    for case, name, ps in [
        ("nothing-after-the-name", "develop-red-3", "supervise.sh develop-red-3\n"),
        ("name-is-a-prefix", "develop-red", "supervise.sh develop-red-3 x\n"),
        ("glob-in-the-name", "a*", "supervise.sh abc x\n"),
    ]:
        answered["ps"] = ps
        answers[case] = pid_file.supervising("4242", name)

    assert answers == {"nothing-after-the-name": False, "name-is-a-prefix": False, "glob-in-the-name": False}


def test_supervising_recognises_a_supervisor_spelled_veri_supervise_py_as_well_as_supervise_sh(monkeypatch):
    import subprocess

    pid_file = importlib.import_module("veri.pid_file")
    answered = {}

    def fake_run(argv, *args, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout=answered["ps"], stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
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
