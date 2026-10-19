"""grade-prose.sh's entry point, run in-process."""
import os
import re
import subprocess
import sys
import tempfile

import requirements
from extract_result import extract
from run_verdict import SCRIPTS

USAGE = "usage: grade-prose.sh <requirements-file> <unit>"


def prompt(unit, text, claims):
    rows = "".join("%s: %s\n" % tuple(row.split("\t", 1)) for row in claims.splitlines())
    return "Unit: %s\n\n%s\n\nRequirements:\n%s" % (unit, text, rows)


def section(text, heading):
    out, level, fenced = [], None, False
    for line in text.splitlines(keepends=True):
        if line.startswith("```"):
            fenced = not fenced
        hashes = 0 if fenced else len(line) - len(line.lstrip("#"))
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


def grader_model():
    with open(os.path.join(SCRIPTS, "..", "grader.conf"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                return line.split("=", 1)[-1].strip().strip("'\"")
    return ""


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path, unit = argv
    model = grader_model()
    if not re.search(r"(^|-)\d+(-|$)", model):
        print("grade-prose.sh: grader.conf model %r names no version" % model, file=sys.stderr)
        return 2
    file, _, heading = unit.partition("#")
    with open(file, encoding="utf-8") as f:
        text = f.read()
    if heading:
        text = section(text, heading)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(prompt(unit, text, requirements.claims(path, unit)))
    env = {**os.environ, "PATH": modern_python_dir() + os.environ.get("PATH", ""), "VERI_MODEL": model}
    try:
        subprocess.run([os.path.join(SCRIPTS, "supervise.sh"), "grade-prose",
                        os.path.join(SCRIPTS, "run-leaf.sh"), f.name], stdout=subprocess.PIPE, env=env)
    finally:
        os.unlink(f.name)
    with open(os.path.join(".tdd", "grade-prose.log"), encoding="utf-8") as log:
        reply = extract(log.read())
    if "BEGIN GRADES" not in reply:
        print("grade-prose.sh: no verdict obtained: the reply has no BEGIN GRADES block", file=sys.stderr)
        return 2
    failed = re.findall(r"^\S+: FAIL\b.*$", reply, re.M)
    print("\n".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
