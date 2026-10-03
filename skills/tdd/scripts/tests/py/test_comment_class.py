"""In-process cases for veri/comment_class.py, the module comment-class.sh is a shim over."""
import importlib
import pathlib
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_main_with_no_argument_returns_2_naming_its_usage(capsys):
    comment_class = importlib.import_module("veri.comment_class")

    refused = comment_class.main([])
    refusal = capsys.readouterr()

    assert (refused, refusal.out, refusal.err) == (2, "", "usage: comment-class.sh [--sweepable] <file>…\n")


def test_main_prints_each_hash_line_with_its_class_and_sweepable_keeps_classes_1_and_2_less_the_header(tmp_path, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    script = tmp_path / "s.sh"
    script.write_text(
        "#!/bin/sh\n"
        "# a contract header\n"
        "echo one\n"
        "# a comment in code\n"
        "cat > out.txt <<EOF\n"
        "# written to a file\n"
        "EOF\n"
        "cat <<EOF\n"
        "# in any other heredoc\n"
        "EOF\n"
    )

    every = comment_class.main([str(script)])
    every_out = capsys.readouterr().out
    sweepable = comment_class.main(["--sweepable", str(script)])
    sweepable_out = capsys.readouterr().out

    assert (every, every_out, sweepable, sweepable_out) == (
        0,
        f"{script}:1:1\n{script}:2:1\n{script}:4:1\n{script}:6:2\n{script}:9:3\n",
        0,
        f"{script}:4:1\n{script}:6:2\n",
    )
