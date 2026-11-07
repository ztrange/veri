"""Cases for what skills/tdd/REVISE.md tells the conductor about a repeated rejection reason."""
import pathlib
import re

REVISE = pathlib.Path(__file__).resolve().parents[4] / "REVISE.md"


def _same_reject_previous_file(lines):
    """The line index of REVISE.md's same-reject.sh call and the first file it names."""
    for i, line in enumerate(lines):
        match = re.search(r"same-reject\.sh\s+(\S+)", line)
        if match:
            return i, match.group(1)
    raise AssertionError("REVISE.md never calls same-reject.sh")


def test_same_reject_compares_a_file_an_earlier_line_writes():
    lines = REVISE.read_text().splitlines()
    call, previous = _same_reject_previous_file(lines)
    assert "<k-1>" in previous, (
        f"same-reject.sh's first file {previous!r} does not name the previous attempt's saved reason")
    # Attempt k-1 wrote that file under its own number, <k>, before its re-verify overwrote the reason.
    written = previous.replace("<k-1>", "<k>")
    writes = re.compile(r"(?:\bcp\s+\S+\s+|>\s*)" + re.escape(written) + r"(?:\s|$|;)")
    assert any(writes.search(line) for line in lines[:call]), (
        f"no line before the same-reject.sh call writes {written!r}, so the file it names never exists")
