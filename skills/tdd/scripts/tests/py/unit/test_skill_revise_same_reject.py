"""Cases for what skills/tdd/REVISE.md tells the conductor about a repeated rejection reason."""
import pathlib

REVISE = pathlib.Path(__file__).resolve().parents[4] / "REVISE.md"


def test_revise_md_names_same_reject_and_both_branches():
    text = REVISE.read_text()
    assert "same-reject.sh" in text, "REVISE.md never names same-reject.sh"
    start = text.index("same-reject.sh")
    window = text[start:start + 1500]
    assert "exit 0" in window.lower(), window
    assert "develop-exhausted" in window, window
    assert "exit 1" in window.lower(), window
    assert "exit 2" in window.lower(), window
