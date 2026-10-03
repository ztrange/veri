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


def test_main_classes_a_heredoc_line_by_its_target_never_as_class_1_and_never_carries_a_heredoc_into_the_next_file(tmp_path, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    fixtures = {
        "mixed": ("# a comment in code", "cat << EOF", "# a line in a heredoc", "EOF", "# a comment after the heredoc"),
        "open": ("cat <<EOF", "# a line in a heredoc"),
        "after": ("# a comment in code",),
        "delims": (
            "cat <<'EOF'", "# in a single-quoted heredoc", "EOF", 'cat <<"EOF"', "# in a double-quoted heredoc", "EOF",
            "cat <<-EOF", "# in a dash heredoc", "\tEOF", "cat <<< word", "# a comment after a here-string",
        ),
        "targets": (
            'cat > "$dir/fixture.txt" <<EOF', "# written to a file", "EOF", "claude -p <<EOF", "# sent to a model", "EOF",
            'prompt="$(cat <<EOF', "# held in a variable", "EOF", ')"', "cat <<EOF", "# printed to stdout", "EOF",
            "cat >&2 <<EOF", "# printed to stderr", "EOF",
        ),
        "fd-redirect": ("claude -p 2>/dev/null <<EOF", "# sent to a model with stderr discarded", "EOF"),
        "piped-tee": ('cat <<EOF | tee "$dir/fixture.txt"', "# written to a file through tee", "EOF"),
    }
    paths = {}
    for name, lines in fixtures.items():
        paths[name] = tmp_path / f"{name}.sh"
        paths[name].write_text("\n".join(lines) + "\n")

    def classify(*names):
        code = comment_class.main([str(paths[name]) for name in names])
        return code, capsys.readouterr().out

    p = {name: str(path) for name, path in paths.items()}
    assert {
        "mixed": classify("mixed"),
        "open-then-after": classify("open", "after"),
        "delims": classify("delims"),
        "targets": classify("targets"),
        "fd-redirect": classify("fd-redirect"),
        "piped-tee": classify("piped-tee"),
    } == {
        "mixed": (0, f"{p['mixed']}:1:1\n{p['mixed']}:3:3\n{p['mixed']}:5:1\n"),
        "open-then-after": (0, f"{p['open']}:2:3\n{p['after']}:1:1\n"),
        "delims": (0, f"{p['delims']}:2:3\n{p['delims']}:5:3\n{p['delims']}:8:3\n{p['delims']}:11:1\n"),
        "targets": (
            0,
            f"{p['targets']}:2:2\n{p['targets']}:5:3\n{p['targets']}:8:3\n{p['targets']}:12:3\n{p['targets']}:15:3\n",
        ),
        "fd-redirect": (0, f"{p['fd-redirect']}:2:3\n"),
        "piped-tee": (0, f"{p['piped-tee']}:2:2\n"),
    }
