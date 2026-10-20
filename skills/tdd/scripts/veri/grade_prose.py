"""grade-prose.sh's entry point, run in-process."""
import os
import re
import subprocess
import sys
import tempfile

import event
import requirements
from extract_result import extract
from leaf_log import result_records
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


def no_verdict(detail):
    print("grade-prose.sh: no verdict obtained: %s" % detail, file=sys.stderr)
    return 2


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
    claims = requirements.claims(path, unit)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(prompt(unit, text, claims))
    env = dict(os.environ)
    env["PATH"] = modern_python_dir() + env.get("PATH", "")
    env["VERI_MODEL"] = model
    try:
        ran = subprocess.run([os.path.join(SCRIPTS, "supervise.sh"), "grade-prose",
                        os.path.join(SCRIPTS, "run-leaf.sh"), f.name], stdout=subprocess.PIPE, env=env)
    finally:
        os.unlink(f.name)
    if ran.returncode:
        return no_verdict("the grader leaf exited %d" % ran.returncode)
    with open(os.path.join(".tdd", "grade-prose.log"), encoding="utf-8") as log:
        raw = log.read()
    reply = extract(raw)
    cost = sum(float(r.get("total_cost_usd") or 0) for r in result_records(raw.splitlines()) if "result" in r)
    if "BEGIN GRADES" not in reply:
        return no_verdict("the reply has no BEGIN GRADES block")
    reply = reply[reply.rindex("BEGIN GRADES"):]
    block, _, after = reply.partition("END GRADES")
    trailing = "\n".join(l for l in after.splitlines() if l.strip() and not l.startswith("VERDICT:"))
    if trailing:
        return no_verdict("text after END GRADES: %s" % trailing)
    for word in re.findall(r"^\S+: (\w+)", block, re.M):
        if word not in ("PASS", "FAIL"):
            return no_verdict("grade word %s is neither PASS nor FAIL" % word)
    got = re.findall(r"^(\S+): (?:PASS|FAIL)\b", block, re.M)
    wanted = [row.split("\t", 1)[0] for row in claims.splitlines()]
    if got != wanted:
        return no_verdict("GRADES block IDs %s do not match requirement IDs %s"
                          % (", ".join(got), ", ".join(wanted)))
    failed = re.findall(r"^\S+: FAIL\b.*$", reply, re.M)
    said = re.findall(r"^VERDICT: (\S+)", after, re.M)
    if not said:
        return no_verdict("the GRADES block has no VERDICT line")
    if said[-1] != ("REJECT" if failed else "PASS"):
        return no_verdict("VERDICT %s disagrees with the GRADES lines" % said[-1])
    event.append(".", {}, "grading", ["unit=" + unit, "verdict=" + said[-1],
                                       "failing=" + ",".join(l.split(":")[0] for l in failed),
                                       "cost_usd=%s" % cost])
    print("\n".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
