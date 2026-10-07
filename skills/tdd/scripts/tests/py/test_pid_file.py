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
