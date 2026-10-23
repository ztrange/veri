"""grade-prose.sh's entry point, run in-process."""
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid

import event
import requirements
import tunables
import markdown_sections
from extract_result import extract
from leaf_log import result_records
from run_verdict import SCRIPTS

USAGE = "usage: grade-prose.sh <requirements-file> <unit>"


GRADER_INSTRUCTIONS = """You grade a piece of prose against a list of requirements. You judge only what the prose states or instructs, read as its reader (an AI agent following it) would read it. You do not judge whether the instructions are wise, and you do not judge behaviour.

Rules:
- `{{NAME}}` and `{{INCLUDE:...}}` are template slots filled in later. Never fail a requirement because of a slot; judge the literal text around it.
- A requirement PASSES when the prose clearly states or instructs it, in any wording. It FAILS when the prose omits it, contradicts it, or states something that would lead the reader to act against it.
- Judge each requirement independently.
- An empty unit is graded FAIL on every requirement row without using any reading tool.

First, analyse each requirement against the prose in free text — quote the prose you rely on. Change your mind here if you need to.

Then end your reply with this block and nothing after it. Inside the block, one line per requirement, in the order given, starting with the requirement's ID exactly as written in the list (e.g. `DR4`), and no corrections:
BEGIN GRADES
<ID>: PASS — <reason, at most 20 words>
<ID>: FAIL — <reason, at most 20 words, quoting the failing prose when it exists>
VERDICT: PASS or VERDICT: REJECT
END GRADES
VERDICT is PASS only if every line inside the block is PASS."""


def prompt(unit, text, claims):
    rows = "".join("%s: %s\n" % tuple(row.split("\t", 1)) for row in claims.splitlines())
    return "%s\n\nUnit: %s\n\n%s\n\nRequirements:\n%s" % (GRADER_INSTRUCTIONS, unit, text, rows)


def section(text, heading):
    lines = text.splitlines()
    for index, (line, fenced) in enumerate(zip(lines, markdown_sections.fenced_lines(text))):
        hashes = len(line) - len(line.lstrip("#"))
        if not fenced and hashes and line[hashes:].strip() == heading:
            body = markdown_sections.section(text, line, bare=True)
            joined = "".join(l + "\n" for l in body)
            if not text.endswith("\n") and index + len(body) == len(lines):
                return joined.removesuffix("\n")
            return joined
    return ""


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


def unit_text(unit):
    file, _, heading = unit.partition("#")
    with open(file, encoding="utf-8") as f:
        text = f.read()
    return section(text, heading) if heading else text


def signature(path, unit):
    parts = [unit_text(unit), requirements.claims(path, unit), GRADER_INSTRUCTIONS, grader_model()]
    return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()


def graded_path(unit):
    parts = unit.partition("#")[0].split("/")
    if len(parts) > 2 and parts[0] == "skills":
        return os.path.join(parts[0], parts[1], "GRADED")
    return os.path.join(os.path.dirname(unit.partition("#")[0]), "GRADED")


def record_graded(unit, sig, grading_id):
    graded = graded_path(unit)
    kept = []
    if os.path.exists(graded):
        with open(graded, encoding="utf-8") as f:
            kept = [l for l in f.read().splitlines() if l.partition(" ")[0] != unit]
    with open(graded, "w", encoding="utf-8") as f:
        f.write("".join(l + "\n" for l in kept))
        f.write("%s %s %s %s\n" % (unit, sig, time.strftime("%Y-%m-%d"), grading_id))


def no_verdict(detail):
    print("grade-prose.sh: no verdict obtained: %s" % detail, file=sys.stderr)
    return 2


def main(argv):
    if argv == ["--owed"]:
        import prose_owed
        path = "REQUIREMENTS.md"
        return max([main([p, unit]) for p, unit in prose_owed.owed_listed(path)[0]], default=0)
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path, unit = argv
    model = grader_model()
    if not re.search(r"(^|-)\d+(-|$)", model):
        print("grade-prose.sh: grader.conf model %r names no version" % model, file=sys.stderr)
        return 2
    text = unit_text(unit)
    claims = requirements.claims(path, unit)
    if not claims.strip():
        return no_verdict("%s has no requirements list for %s" % (path, unit))
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(prompt(unit, text, claims))
    env = dict(os.environ)
    env["PATH"] = modern_python_dir() + env.get("PATH", "")
    env.pop("VERI_MODEL_GRADER", None)
    env["VERI_MODEL"] = model
    env["VERI_LEAF_TOOLS"] = ""
    retries = int(tunables.read("VERI_NO_VERDICT_RETRIES") or "1")
    try:
        for _ in range(retries + 1):
            ran = subprocess.run([os.path.join(SCRIPTS, "supervise.sh"), "grade-prose",
                            os.path.join(SCRIPTS, "run-leaf.sh"), f.name], stdout=subprocess.PIPE, env=env)
            if ran.returncode:
                return no_verdict("the grader leaf exited %d" % ran.returncode)
            with open(os.path.join(".tdd", "grade-prose.log"), encoding="utf-8") as log:
                raw = log.read()
            reply = extract(raw)
            if "BEGIN GRADES" in reply:
                break
    finally:
        os.unlink(f.name)
    cost = sum(float(r.get("total_cost_usd") or 0) for r in result_records(raw.splitlines()) if "result" in r)
    if "BEGIN GRADES" not in reply:
        return no_verdict("the reply has no BEGIN GRADES block")
    reply = reply[reply.rindex("BEGIN GRADES"):]
    block, _, after = reply.partition("END GRADES")
    trailing = "\n".join(l for l in after.splitlines() if l.strip())
    if trailing:
        return no_verdict("text after END GRADES: %s" % trailing)
    for word in re.findall(r"^(?!VERDICT)\S+: (\S+)", block, re.M):
        if word not in ("PASS", "FAIL"):
            return no_verdict("grade word %s is neither PASS nor FAIL" % word)
    got = [i for i in re.findall(r"^(\S+): (?:PASS|FAIL)\b", block, re.M) if i != "VERDICT"]
    wanted = [row.split("\t", 1)[0] for row in claims.splitlines()]
    if sorted(got) != sorted(wanted):
        missing = [i for i in wanted if i not in got]
        if missing:
            return no_verdict("GRADES block is missing requirement IDs %s" % ", ".join(missing))
        repeated = sorted({i for i in got if got.count(i) > 1})
        if repeated:
            return no_verdict("GRADES block names requirement IDs repeated: %s" % ", ".join(repeated))
        return no_verdict("GRADES block IDs %s do not match requirement IDs %s"
                          % (", ".join(got), ", ".join(wanted)))
    failed = re.findall(r"^(?!VERDICT)\S+: FAIL\b.*$", reply, re.M)
    said = re.findall(r"^VERDICT: (\S+)", reply, re.M)
    if not said:
        return no_verdict("the GRADES block has no VERDICT line")
    if said[-1] != ("REJECT" if failed else "PASS"):
        return no_verdict("VERDICT %s disagrees with the GRADES lines" % said[-1])
    grading_id = uuid.uuid4().hex
    event.append(".", {}, "grading", ["unit=" + unit, "verdict=" + said[-1],
                                       "failing=" + ",".join(l.split(":")[0] for l in failed),
                                       "cost_usd=%s" % cost, "id=" + grading_id])
    if not failed:
        record_graded(unit, signature(path, unit), grading_id)
    print("\n".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
