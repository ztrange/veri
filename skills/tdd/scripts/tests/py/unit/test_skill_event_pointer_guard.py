"""Guard: every place a procedure text sends the run into an event names the file to Read for it."""
import re

EVENTS = {
    "BAIL.md": r"\bbail",
    "SKILL-EDIT.md": r"skill-edit",
    "STOPPING.md": r"\bgo(es)? to \*Stopping\*",
    "RECONCILE.md": r"reconcile leaf",
    "PIN.md": r"\bthe pin path\b|\bcontinue at the pin\b",
    "REVISE.md": r"enter the \*\*revise loop|revise under|bounded revise loop",
    "RESUME.md": r"\*\*Resume check\.\*\*",
}


def unpointed(path):
    """(file, line) of each place whose trigger words lack `<base directory>/<file>` on it or the next line."""
    lines = path.read_text().splitlines()
    found = []
    for name, trigger in EVENTS.items():
        for n, line in enumerate(lines):
            window = line + " " + "".join(lines[n + 1:n + 2])
            if re.search(trigger, line, re.I) and f"`<base directory>/{name}`" not in window:
                found.append((name, n + 1))
    return found


def test_a_bare_bail_sentence_without_the_pointer_is_named_by_file_and_line(tmp_path):
    text = tmp_path / "procedure.md"
    text.write_text("# Procedure\n\nA failed step must bail with cause `x`.\n")

    assert unpointed(text) == [("BAIL.md", 3)]
