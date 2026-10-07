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
