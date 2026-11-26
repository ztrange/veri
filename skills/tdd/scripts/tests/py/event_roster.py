"""Every event name emitted under skills/, found by scanning for the shell and in-process emit calls."""
import pathlib
import re
import shlex

SKILLS = pathlib.Path(__file__).resolve().parents[4]
SH_CALL = re.compile(r"event\.sh +([a-z][a-z0-9-]*)")
MARK_CALL = re.compile(r"""(?:event|verify|supervise)\.mark\((?:[^"']|""|"[^"]*:"|"[A-Za-z_]+"(?=\s*:))*?,\s*"([a-z][a-z0-9-]*)"\s*[,)]""")
BARE_MARK_CALL = re.compile(r"""mark\([^,]*,\s*[A-Za-z_]\w*\s*,\s*"([a-z][a-z0-9-]*)"\s*[,)]""")
ROLE_FIRST_MARK_CALL = re.compile(r"""mark\(\s*[A-Za-z_]\w*\s*,\s*"([a-z][a-z0-9-]*)"\s*,""")
RECORD_CALL = re.compile(r"""record\(\s*"([a-z][a-z0-9-]*)"\s*[,)]""")
CAUSE_CONST = re.compile(r"""^CAUSE\s*=\s*"([a-z][a-z0-9-]*)"\s*$""", re.M)


def emitted_events():
    names = {}
    for path in sorted(SKILLS.rglob("*")):
        if not path.is_file() or "tests" in path.parts or path.suffix not in (".sh", ".py", ".md"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in (SH_CALL, MARK_CALL, BARE_MARK_CALL, ROLE_FIRST_MARK_CALL, RECORD_CALL, CAUSE_CONST):
            for found in pattern.finditer(text):
                names.setdefault(found.group(1), path.relative_to(SKILLS))
    return names


SH_SITE = re.compile(r"event\.sh +([a-z][a-z0-9-]*)")
KEY_ARG = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=")


def _literal_keys(rest):
    """The keys of the `key=value` arguments that open `rest`, up to the end of a code span or the first other word."""
    rest = rest.split("`")[0]
    try:
        lexer = shlex.shlex(rest, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        words = list(lexer)
    except ValueError:
        words = rest.split()
    keys = []
    for word in words:
        found = KEY_ARG.match(word)
        if not found:
            break
        keys.append(found.group(1))
    return keys


def event_sh_call_sites():
    """(file:line, event, keys) for every `event.sh <name> key=…` call in a .sh or .md file under skills/, tests
    excluded, whose event name is literal; `keys` are the literal key names that follow it on its line."""
    sites = []
    for path in sorted(SKILLS.rglob("*")):
        if not path.is_file() or "tests" in path.parts or path.suffix not in (".sh", ".md"):
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            calls = list(SH_SITE.finditer(line))
            for found, after in zip(calls, calls[1:] + [None], strict=False):
                rest = line[found.end():after.start() if after else len(line)]
                sites.append((f"{path.relative_to(SKILLS)}:{n}", found.group(1), _literal_keys(rest)))
    return sites


def documented_events(text):
    return set(re.findall(r"^\|\s*`([a-z][a-z0-9-]*)`\s*\|", text, re.M))
