"""Every event name emitted under skills/, found by scanning for the shell and in-process emit calls."""
import pathlib
import re

SKILLS = pathlib.Path(__file__).resolve().parents[3]
SH_CALL = re.compile(r"event\.sh +([a-z][a-z0-9-]*)")
MARK_CALL = re.compile(r"""(?:event|verify|supervise)\.mark\((?:[^"']|""|"[^"]*:"|"[A-Za-z_]+"(?=\s*:))*?,\s*"([a-z][a-z0-9-]*)"\s*[,)]""")
RECORD_CALL = re.compile(r"""push_branch\.record\(\s*"([a-z][a-z0-9-]*)"\s*[,)]""")


def emitted_events():
    names = {}
    for path in sorted(SKILLS.rglob("*")):
        if not path.is_file() or "tests" in path.parts or path.suffix not in (".sh", ".py", ".md"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in (SH_CALL, MARK_CALL, RECORD_CALL):
            for found in pattern.finditer(text):
                names.setdefault(found.group(1), path.relative_to(SKILLS))
    return names
