"""SKILL.md and SCRIPTS.md describe a leaf's Bash timeouts, read as text."""
import pathlib

TDD = pathlib.Path(__file__).resolve().parents[4]


def test_1939_leaf_launch_prose_and_run_leaf_entry_say_bash_timeouts_follow_the_effective_timeout():
    problems = []
    for name in ("SKILL.md", "SCRIPTS.md"):
        text = " ".join((TDD / name).read_text().split())
        at = text.find("BASH_DEFAULT_TIMEOUT_MS")
        window = text[at:at + 300] if at >= 0 else ""
        if "effective timeout" not in window:
            problems.append(f"{name}: Bash timeouts not tied to the effective timeout")
        if "VERI_TIMEOUT seconds, default 900" in text:
            problems.append(f"{name}: still says 'VERI_TIMEOUT seconds, default 900'")

    assert problems == [], problems
