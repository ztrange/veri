"""In-process cases for veri/pid_file.py, the pid-file reader lib/number-in.sh and lib/pid-file.sh define in bash."""
import importlib
import pathlib
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


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
