"""grade-prose.sh's entry point, run in-process."""
import os
import subprocess
import sys
import tempfile

import requirements
from run_verdict import SCRIPTS

USAGE = "usage: grade-prose.sh <requirements-file> <unit>"


def prompt(unit, text, claims):
    rows = "".join("%s: %s\n" % tuple(row.split("\t", 1)) for row in claims.splitlines())
    return "Unit: %s\n\n%s\n\nRequirements:\n%s" % (unit, text, rows)


def section(text, heading):
    out, level = [], None
    for line in text.splitlines(keepends=True):
        hashes = len(line) - len(line.lstrip("#"))
        if level is None:
            if hashes and line[hashes:].strip() == heading:
                level = hashes
                out.append(line)
        elif 0 < hashes <= level:
            break
        else:
            out.append(line)
    return "".join(out)


def modern_python_dir():
    check = "import sys; sys.exit(sys.version_info < (3, 12))"
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        binary = os.path.join(folder, "python3")
        if os.access(binary, os.X_OK) and subprocess.run([binary, "-c", check]).returncode == 0:
            return folder + os.pathsep
    return ""


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path, unit = argv
    file, _, heading = unit.partition("#")
    with open(file, encoding="utf-8") as f:
        text = f.read()
    if heading:
        text = section(text, heading)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(prompt(unit, text, requirements.claims(path, unit)))
    env = {**os.environ, "PATH": modern_python_dir() + os.environ.get("PATH", "")}
    try:
        subprocess.run([os.path.join(SCRIPTS, "supervise.sh"), "verify-grade",
                        os.path.join(SCRIPTS, "run-leaf.sh"), f.name], stdout=subprocess.PIPE, env=env)
    finally:
        os.unlink(f.name)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
