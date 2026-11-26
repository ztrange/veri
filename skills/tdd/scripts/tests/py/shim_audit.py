"""Audits of the shell shims under skills/tdd/scripts: each is the canonical `exec python3 veri/<module>.py` shim (or its
venv-first and floor-sourcing forms), no module's `__main__` block bypasses entry.run, and no shim feeds python3 a
heredoc or `-c` string or calls gh. Each returns the problems it found, as strings naming the script and line."""
import pathlib
import re

CANONICAL_SHIM = re.compile(r'exec (?:python3|"\$py") "\$\(dirname "\$0"\)/(veri/[\w-]+\.py)" "\$@"')
SHIM_EXEC = re.compile(r'^exec (?:python3|"\$py") .*/(veri/[\w-]+\.py)"', re.MULTILINE)
VENV_PREFIX = ['py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"', '[ -x "$py" ] || py=python3']
FLOOR_SOURCE = '. "$(dirname "$0")/lib/shim-python.sh"'


def shim_problems(scripts, exempt=()):
    problems = []
    seen = set()
    for script in sorted(pathlib.Path(scripts).glob("*.sh")):
        seen.add(script.name)
        lines = script.read_text().splitlines()
        code = [line for line in lines if line.strip() and not line.startswith("#")]
        exec_line = code[-1] if code else ""
        canonical = bool(lines) and lines[0] == "#!/bin/sh" and (
            (len(code) == 1 and exec_line.startswith("exec python3 "))
            or (len(code) == 3 and code[:2] == VENV_PREFIX and exec_line.startswith('exec "$py" '))
            or (len(code) == 2 and code[0] == FLOOR_SOURCE and exec_line.startswith('exec "$py" '))
        )
        match = CANONICAL_SHIM.fullmatch(exec_line) if canonical else None
        if match is not None and script.name in exempt:
            problems.append("%s: stale exemption, the script is now the canonical shim" % script.name)
        elif match is None and script.name not in exempt:
            problems.append("%s: not the canonical shim" % script.name)
        elif match is not None and not (script.parent / match.group(1)).is_file():
            problems.append("%s: %s does not exist" % (script.name, match.group(1)))
    problems += ["%s: stale exemption, the script is gone" % name for name in sorted(set(exempt) - seen)]
    return problems


def entry_bypass_problems(scripts):
    problems = []
    shims = [(script, SHIM_EXEC.search(script.read_text())) for script in sorted(pathlib.Path(scripts).glob("*.sh"))]
    shims = [(script, match) for script, match in shims if match]
    if not shims:
        problems.append("no shim found under %s" % scripts)
    for _script, match in shims:
        module = pathlib.Path(scripts) / match.group(1)
        lines = module.read_text().splitlines()
        for number, line in enumerate(lines, 1):
            if line.startswith("if __name__ == ") and "pycache_prefix.py" not in line:
                block = []
                for l in lines[number:]:
                    if l.strip() and not l[0].isspace():
                        break
                    block.append(l)
                if not any("entry.run(" in l.split("#")[0] for l in block):
                    problems.append("%s:%d __main__ block does not go through entry.run" % (module.name, number))
    return problems


def shim_source_problems(scripts):
    rules = (
        (re.compile(r"\bpython3?\b[^#]*<<"), "feeds python3 a heredoc"),
        (re.compile(r"\bpython3?\b[^#]*\s-c(?:\s|$)"), "feeds python3 a -c string"),
        (re.compile(r"\bgh\s+(issue|pr|repo|api|auth\s+status)\b"), "calls gh"),
    )
    gh_assign = re.compile(r'^(?:if\s+!?\s*|!\s*|local\s+)?(\w+)="?\$\((?:(?:gh|gh_list|gh_json|\w*_json)[\s)]|cat\s+"?\$\{?VERI_GH_JSON)')
    problems = []
    for script in sorted(pathlib.Path(scripts).glob("*.sh")) + sorted(pathlib.Path(scripts).glob("lib/*.sh")):
        library = script.parent.name == "lib"
        name = str(script.relative_to(scripts))
        gh_names = set()
        for number, line in enumerate(script.read_text().splitlines(), 1):
            code = line.lstrip()
            if code.startswith("#"):
                continue
            assigned = gh_assign.match(code)
            if assigned:
                gh_names.add(assigned.group(1))
            if re.search(r"\bpython3?\b", code) and any(re.search(r"\$\{?%s\b" % name, code) for name in gh_names):
                problems.append("%s:%d hands python3 a gh JSON document" % (name, number))
            if library:
                continue
            for pattern, what in rules:
                if pattern.search(code):
                    problems.append("%s:%d %s" % (name, number, what))
    return problems
