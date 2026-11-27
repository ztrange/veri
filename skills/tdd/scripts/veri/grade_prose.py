"""grade-prose.sh's entry point, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import typing
import uuid

import event
import leaf
import leaf_log
import markdown_sections
import requirements
import tunables
from extract_result import extract
from paths import SCRIPTS

USAGE = "usage: grade-prose.sh <requirements-file> <unit> | --signed <base>"
GRADE_KEY = r"^(?!VERDICT|REASON:)\S+: "
EFFORTS = ("low", "medium", "high", "xhigh", "max")
BAD_GRADE = re.compile(GRADE_KEY + r"(?!PASS\b|FAIL\b)\S", re.M)


GRADER_INSTRUCTIONS = """You grade a piece of prose against a list of requirements. You judge only what the prose \
states or instructs, read as its reader (an AI agent following it) would read it. You do not judge whether the \
instructions are wise, and you do not judge behaviour.

Rules:
- `{{NAME}}` and `{{INCLUDE:...}}` are template slots filled in later. Never fail a requirement because of a slot; \
judge the literal text around it.
- A requirement PASSES when the prose clearly states or instructs it, in any wording. It FAILS when the prose omits \
it, contradicts it, or states something that would lead the reader to act against it.
- A requirement row that names a concrete artefact (a file, a section heading or an identifier) FAILS when the prose \
does not name that artefact too; substance alone does not discharge a named reference. A row that names no artefact \
passes on meaning alone, in any wording, so a unit wording such a row differently keeps PASS; the artefact rule is \
not substring matching.
- Judge each requirement independently.
- Answer from the text given here. Do not call any tool.
- An empty unit is graded FAIL on every requirement row without using any reading tool.

First, analyse each requirement against the prose in free text — quote the prose you rely on. Change your mind here \
if you need to.

Then end your reply with this block and nothing after it. Inside the block, one line per requirement, in the order \
given, starting with the requirement's ID exactly as written in the list (e.g. `DR4`), and no corrections:
BEGIN GRADES
<ID>: PASS — <reason, at most 20 words>
<ID>: FAIL — <reason, at most 20 words, quoting the failing prose when it exists>
VERDICT: PASS or VERDICT: REJECT
END GRADES
VERDICT is PASS only if every line inside the block is PASS."""


def prompt(unit, text, claims):
    rows = "".join("%s: %s\n" % tuple(row.split("\t", 1)) for row in claims.splitlines())
    return "%s\n\nUnit: %s\n\n%s\n\nRequirements:\n%s" % (GRADER_INSTRUCTIONS, unit, text, rows)


class HeadingCount(ValueError):
    """A heading unit's heading matches `count` unfenced heading lines of its file, not exactly one."""

    def __init__(self, count):
        super().__init__(count)
        self.count = count


def section(text, heading):
    """`heading`'s own text in `text`: its unfenced heading line up to the next unfenced heading line of any level.
    HeadingCount when the heading matches no unfenced heading line, or more than one."""
    found = [own for line, own in own_texts(text)[1:] if heading_text(line) == heading]
    if len(found) != 1:
        raise HeadingCount(len(found))
    return found[0]


def own_texts(text):
    """`text` cut at its unfenced heading lines, in file order: `(None, the text above the first heading)`, then
    `(heading line as written, its own text)` per heading line; the texts joined are `text`."""
    lines = re.findall(r"[^\n]*\n|[^\n]+\Z", text)
    flat = [" ".join(line.removesuffix("\n").splitlines()) for line in lines]
    fenced = markdown_sections.fenced_lines("\n".join(flat))
    fenced += [False] * (len(lines) - len(fenced))
    cuts = [[None, ""]]
    for line, plain, inside in zip(lines, flat, fenced, strict=True):
        if not inside and heading_text(plain) is not None:
            cuts.append([line.removesuffix("\n"), ""])
        cuts[-1][1] += line
    return [tuple(cut) for cut in cuts]


def claimed_headings(file, units=None):
    """The headings of every `<file>#<heading>` unit a tracked REQUIREMENTS.md lists; `units` are the listed units
    when the caller has read them already (None: read every list)."""
    if units is None:
        units = [unit for listed in requirements.lists() for unit in requirements.listed_units(listed)]
    return {unit.partition("#")[2] for unit in units if unit.partition("#")[0] == file and "#" in unit}


def signed_text(unit, text, units=None):
    """What `unit` signs and the grader is shown, from `text`, its unit text. A whole-file unit whose file has a listed
    heading unit is split: its view is the file's heading lines, a blank line, then the text above the first heading
    and the own text of every section no listed heading unit claims, in file order. Any other unit signs `text`."""
    file, _, heading = unit.partition("#")
    claimed = set() if heading else claimed_headings(file, units)
    if not claimed:
        return text
    cuts = own_texts(text)
    return ("".join(line + "\n" for line, _ in cuts if line is not None) + "\n"
            + "".join(own for line, own in cuts if line is None or heading_text(line) not in claimed))


def heading_text(line):
    """The heading a line of hashes names, None when the line is no heading line."""
    line = " ".join(line.splitlines())
    hashes = len(line) - len(line.lstrip("#"))
    return line[hashes:].strip() if hashes else None


def modern_python_dir():
    check = "import sys; sys.exit(sys.version_info < (3, 12))"
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        binary = os.path.join(folder, "python3")
        if os.access(binary, os.X_OK) and subprocess.run([binary, "-c", check]).returncode == 0:
            return folder + os.pathsep
    return ""


def grader_conf():
    """grader.conf's `key=value` lines as {key: value}, comments skipped, a line with no `=` read as the model (as
    grader.conf files older than the `key=` form name it); ValueError on a repeated key, since which
    of two values the grader ran at would otherwise be a silent choice."""
    settings = {}
    with open(os.path.join(SCRIPTS, "..", "grader.conf"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, equals, value = line.partition("=")
                key = key.strip() if equals else "model"
                value = value if equals else line
                if key in settings:
                    raise ValueError("grader.conf repeats the key %s" % key)
                settings[key] = value.strip().strip("'\"")
    return settings


def grader_model():
    return grader_conf().get("model", "")


def read(file):
    with open(file, encoding="utf-8") as f:
        return f.read()


def unit_text(unit, reader=None):
    """`unit`'s text: a whole-file unit's file, a `file#heading` unit's own text (ValueError naming the unit and the
    count when its heading matches no unfenced heading line of its file, or more than one)."""
    file, _, heading = unit.partition("#")
    text = (reader or read)(file)
    if not heading:
        return text
    try:
        return section(text, heading)
    except HeadingCount as e:
        raise ValueError("%s: its heading matches %d unfenced heading lines of %s, not one"
                         % (unit, e.count, file)) from e


def signature(path, unit, text=None, units=None):
    """The stamp of `unit` under the list `path` names; `text` is the unit's text (None: the working tree's); `units`
    the listed units, when the caller has read them (None: claimed_headings reads every list)."""
    parts = [unit_text(unit) if text is None else text, requirements.claims(path, unit), grader_model()]
    parts[0] = signed_text(unit, parts[0], units)
    return stamp(with_effort(parts, grader_conf().get("effort")))


def with_effort(parts, effort):
    """What a signature stamps: the unit text, its rows and the grader model, and the effort level only when
    grader.conf sets one, so a grader.conf without an effort= line stamps the three parts it always did."""
    return parts + ([] if effort is None else [effort])


def stamp(parts):
    return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()


class Grading(typing.NamedTuple):
    """One grading's answer. `code` is grade-prose.sh's exit (0 PASS, 1 REJECT, 2 no answer); `verdict` the grader's
    last word; `failing` the ids of the rows it failed; `lines` what grade-prose.sh prints, the failing rows' grade
    lines or the same-text refusal; `cost` the grader leaves' dollars; `grading_id` the `grading` event's id."""
    code: int
    verdict: str = None
    failing: tuple = ()
    lines: tuple = ()
    cost: float = None
    grading_id: str = None

    @property
    def out(self):
        """The bytes grade-prose.sh writes to stdout for this grading: nothing when no answer was obtained."""
        return "" if self.code == 2 else "\n".join(self.lines) + "\n"


def signer():
    own = os.path.join("skills", "tdd", "scripts", "veri", "grade_prose.py")
    if not os.path.isfile(own):
        return sys.modules[__name__]
    with open(own, "rb") as tree, open(__file__, "rb") as running:
        if tree.read() == running.read():
            return sys.modules[__name__]
    import importlib.util
    spec = importlib.util.spec_from_file_location("tree_grade_prose", own)
    tree = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tree)
    return tree


def graded_path(unit):
    parts = unit.partition("#")[0].split("/")
    if len(parts) > 2 and parts[0] == "skills":
        return os.path.join(parts[0], parts[1], "GRADED")
    return os.path.join(os.path.dirname(unit.partition("#")[0]), "GRADED")


def graded_fields(line):
    """A GRADED line's fields, split on each single space: unit, signature, date, grading id, grader-template prefix.
    The unit field is decoded as graded_line encodes it: `%20` back to a space, `%25` back to `%`."""
    fields = line.split(" ")
    fields[0] = re.sub(r"%(20|25)", lambda m: " " if m.group(1) == "20" else "%", fields[0])
    return fields


def graded_line(fields):
    """The GRADED line holding `fields`, without its newline: the inverse of graded_fields. The unit field is written
    with each `%` as `%25` and each space as `%20`, so a `file#heading` unit whose heading holds spaces stays one field;
    a unit holding neither is written as it is."""
    return " ".join([fields[0].replace("%", "%25").replace(" ", "%20"), *fields[1:]])


def requirements_beside(unit):
    """The REQUIREMENTS.md beside the file `unit` names before its `#`, so a `/` in a heading never moves it."""
    return os.path.join(os.path.dirname(unit.partition("#")[0]), "REQUIREMENTS.md")


def signed_units(base, head):
    """The units a branch signed, as `(requirements file, unit)` pairs, from two `{GRADED path: text}` maps (the merge
    base's and HEAD's): each unit, decoded by graded_fields and listed once, whose line at head its file at base lacks,
    so a line a conflict resolution duplicated from the default branch is not the branch's,
    and a blank line is no unit."""
    listed = []
    for path in sorted(head):
        held = set(base.get(path, "").splitlines())
        for line in head[path].splitlines():
            unit = graded_fields(line)[0]
            if line and line not in held and (requirements_beside(unit), unit) not in listed:
                listed.append((requirements_beside(unit), unit))
    return listed


def graded_at(rev):
    """{GRADED path: text} for every GRADED file of the tree at `rev`, read with git (GitFailed when it cannot)."""
    import git
    paths = [p for p in git.out("ls-tree", "-r", "-z", "--name-only", rev).split("\0")
             if os.path.basename(p) == "GRADED"]
    return {p: git.out("show", "%s:%s" % (rev, p)) for p in paths}


def signed(base):
    """`grade-prose.sh --signed <base>`: one `<requirements file>\t<unit>` line per unit signed_units lists between
    `<base>` and HEAD; exit 0, an empty list included, or 2 when git cannot read either tree."""
    import git
    try:
        pairs = signed_units(graded_at(base), graded_at("HEAD"))
    except git.GitFailed as e:
        print("grade-prose.sh: --signed %s: %s" % (base, e), file=sys.stderr)
        return 2
    sys.stdout.write("".join("%s\t%s\n" % pair for pair in pairs))
    return 0


def graded_lines(graded):
    if not os.path.exists(graded):
        return
    with open(graded, encoding="utf-8") as f:
        for line in f.read().splitlines():
            yield graded_fields(line)


def graded_signature(unit):
    graded = graded_path(unit)
    for fields in graded_lines(graded):
        if fields[0] == unit and len(fields) > 1:
            return fields[1]
    return None


def orphans(units):
    for graded in requirements.tracked("GRADED"):
        for fields in graded_lines(graded):
            if fields[0] not in units:
                yield fields[0]


def listed_pairs(path):
    """Every (list, unit) pair the tracked lists name, `path` first, and the units alone."""
    listed = [(p, u) for p in requirements.lists(path) for u in requirements.listed_units(p)]
    return listed, [u for _, u in listed]


def owed_listed(path="REQUIREMENTS.md"):
    listed, units = listed_pairs(path)
    owed = [(p, u) for p, u in listed if graded_signature(u) != signature(p, u, units=units)]
    return owed, list(orphans(units))


def read_graded(graded):
    with open(graded, encoding="utf-8") as f:
        return f.read().splitlines()


def record_graded(unit, sig, grading_id):
    graded = graded_path(unit)
    kept = []
    if os.path.exists(graded):
        kept = [line for line in read_graded(graded) if graded_fields(line)[0] != unit]
    with open(graded, "w", encoding="utf-8") as f:
        f.write("".join(line + "\n" for line in kept))
        template = hashlib.sha256(GRADER_INSTRUCTIONS.encode("utf-8")).hexdigest()[:12]
        f.write(graded_line([unit, sig, time.strftime("%Y-%m-%d"), grading_id, template]) + "\n")


def graded_ids(text):
    return re.findall(r"^(?!VERDICT)(\S+): (?:PASS|FAIL)\b", text, re.M)


def drop_off_list(lines, allowed):
    kept, dropped = [], []
    for line in lines:
        m = re.match(r"(?!VERDICT)(\S+): (?:PASS|FAIL)\b", line)
        if m and m.group(1) not in allowed:
            dropped.append(m.group(1))
        else:
            kept.append(line)
    if dropped:
        print("grade-prose.sh: ignoring graded IDs outside the prompt's list: %s"
              % ", ".join(sorted(set(dropped))), file=sys.stderr)
    return kept


def no_verdict(detail):
    print("grade-prose.sh: no verdict obtained: %s" % detail, file=sys.stderr)
    return Grading(2)


def keeps_protocol(reply, wanted):
    block = reply[reply.rindex("BEGIN GRADES"):]
    ids = graded_ids(block)
    return (len(set(ids)) == len(ids)
            and not BAD_GRADE.search(block) and not reply.partition("END GRADES")[2].strip())


def resign(unit, own, tree):
    graded = graded_path(unit)
    lines = read_graded(graded)
    for i, line in enumerate(lines):
        fields = graded_fields(line)
        if fields[:2] == [unit, own]:
            fields[1] = tree
            lines[i] = graded_line(fields)
    with open(graded, "w", encoding="utf-8") as f:
        f.write("".join(line + "\n" for line in lines))


def convert(path):
    with requirements.parsed_once():
        listed, units = listed_pairs(path)
        formula = signer()
        for p, unit in listed:
            try:
                tree = formula.signature(p, unit, units=units)
            except Exception as e:
                print("grade-prose.sh: signature-formula-disagreement: %s: the tree's formula gave none (%s)"
                      % (unit, e),
                      file=sys.stderr)
                return 2
            own = tree if formula is sys.modules[__name__] else signature(p, unit, units=units)
            if own != tree:
                resign(unit, own, tree)


def main(argv):
    if argv == ["--owed"]:
        path = "REQUIREMENTS.md"
        return max([printed(grade_unit(p, unit)) for p, unit in owed_listed(path)[0]], default=0)
    if argv == ["--convert"]:
        return convert("REQUIREMENTS.md")
    if argv[:1] == ["--signed"] and len(argv) == 2:
        return signed(argv[1])
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path, unit = argv
    return printed(grade_unit(path, unit))


def printed(grading):
    sys.stdout.write(grading.out)
    return grading.code


def grade_unit(path, unit, read=None):
    """Grade `unit` against the requirements list `path` names: what `grade-prose.sh <path> <unit>` does.

    `read(file)` answers the text of the unit's file (None: `read`, the working tree). Launches the grader leaf
    (retrying a reply without a verdict, and re-grading failed rows), signs the unit into its GRADED file on PASS,
    appends a `grading` event, and returns a `Grading`: code 0 PASS; 1 REJECT; 2 no answer (a grader model naming
    no version, a grader.conf key repeated or effort level unknown, no requirements list, a reply that breaks the
    protocol, a signature disagreement), whose reason is
    on stderr."""
    try:
        model = grader_model()
        effort = grader_conf().get("effort")
    except ValueError as e:
        print("grade-prose.sh: %s" % e, file=sys.stderr)
        return Grading(2)
    effort_args = () if effort is None else ("--effort", effort)
    if not re.search(r"(^|-)\d+(-|$)", model):
        print("grade-prose.sh: grader.conf model %r names no version" % model, file=sys.stderr)
        return Grading(2)
    if effort is not None and effort not in EFFORTS:
        print("grade-prose.sh: grader.conf effort %r is not one of %s" % (effort, ", ".join(EFFORTS)), file=sys.stderr)
        return Grading(2)
    try:
        text = unit_text(unit, read)
    except ValueError as e:
        print("grade-prose.sh: %s" % e, file=sys.stderr)
        return Grading(2)
    shown = signed_text(unit, text)
    claims = requirements.claims(path, unit)
    if not claims.strip():
        return no_verdict("%s has no requirements list for %s" % (path, unit))
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(prompt(unit, shown, claims))
    env = dict(os.environ)
    env["PATH"] = modern_python_dir() + env.get("PATH", "")
    env.pop("VERI_MODEL_GRADER", None)
    env["VERI_MODEL"] = model
    env["VERI_LEAF_TOOLS"] = ""
    env["VERI_LEAF_SKIP_PROJECT_CLAUDE_MD"] = "1"
    raw_retries = tunables.get("VERI_NO_VERDICT_RETRIES", unless_empty=True)
    try:
        retries = tunables.tokens(raw_retries)
    except ValueError:
        print("grade-prose.sh: VERI_NO_VERDICT_RETRIES must be a non-negative integer, got '%s'"
              % raw_retries, file=sys.stderr)
        return Grading(2)
    launches = {}

    def launch(path, retry=""):
        launches[retry] = launches.get(retry, 0) + 1
        retry += "" if launches[retry] == 1 else ".%d" % launches[retry]
        ran = leaf.launch("grade-prose", path, *effort_args, env=env)
        if ran.returncode:
            return None
        live = os.path.join(".tdd", "grade-prose.log")
        with open(live, encoding="utf-8") as log:
            text = log.read()
        shutil.copyfile(live, os.path.join(
            ".tdd", "grade-prose-" + re.sub(r"[^A-Za-z0-9._-]", "_", unit) + retry + ".log"))
        return text

    def launch_rows(ids):
        rows = "".join(r + "\n" for r in claims.splitlines() if r.split("\t", 1)[0] in ids)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as g:
            g.write(prompt(unit, shown, rows))
        try:
            return launch(g.name, ".rows")
        finally:
            os.unlink(g.name)

    wanted = [row.split("\t", 1)[0] for row in claims.splitlines()]
    try:
        for _ in range(retries + 1):
            raw = launch(f.name)
            if raw is None:
                return no_verdict("the grader leaf exited non-zero")
            reply = extract(raw)
            if "BEGIN GRADES" in reply and keeps_protocol(reply, wanted):
                break
    finally:
        os.unlink(f.name)
    cost = leaf_log.cost(raw.splitlines())
    if "BEGIN GRADES" not in reply:
        return no_verdict("the reply has no BEGIN GRADES block")
    reply = "\n".join(drop_off_list(reply[reply.rindex("BEGIN GRADES"):].split("\n"), wanted))
    seen = graded_ids(reply)
    missing = [i for i in wanted if i not in seen]
    if missing and "END GRADES" in reply and keeps_protocol(reply, wanted):
        more = launch_rows(set(missing))
        if more is None:
            return no_verdict("the grader leaf exited non-zero")
        follow = extract(more)
        if "BEGIN GRADES" in follow:
            follow = follow[follow.rindex("BEGIN GRADES"):].partition("END GRADES")[0]
            added = drop_off_list([line for line in follow.splitlines()[1:] if not line.startswith("VERDICT")], missing)
            kept = [line for line in reply.partition("END GRADES")[0].splitlines() if not line.startswith("VERDICT")]
            lines = kept + added
            verdict = "REJECT" if any(": FAIL" in line for line in lines) else "PASS"
            reply = "\n".join(lines + ["VERDICT: " + verdict, "END GRADES"])
        still = [i for i in missing if i not in graded_ids(reply)]
        if still:
            return no_verdict("GRADES block is missing requirement IDs %s; the follow-up for them was tried"
                              % ", ".join(still))
    block, _, after = reply.partition("END GRADES")
    trailing = "\n".join(line for line in after.splitlines() if line.strip())
    if trailing:
        return no_verdict("text after END GRADES: %s" % trailing)
    for word in re.findall(GRADE_KEY + r"(\S+)", block, re.M):
        if word not in ("PASS", "FAIL"):
            return no_verdict("grade word %s is neither PASS nor FAIL" % word)
    got = graded_ids(block)
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
    if failed:
        asked = {line.split(":")[0] for line in failed}
        counted = set(asked)
        for _ in range(2):
            for _try in range(retries + 1):
                more = launch_rows(asked)
                if more is None:
                    return no_verdict("the grader leaf exited non-zero")
                again = extract(more)
                if "BEGIN GRADES" in again and keeps_protocol(again, asked):
                    break
            if not asked <= set(graded_ids(again)):
                return no_verdict("the re-grade has no GRADES block for the rows it was asked about")
            counted &= set(re.findall(r"^(?!VERDICT)(\S+): FAIL\b", again, re.M))
        failed = [line for line in failed if line.split(":")[0] in counted]
        if not failed:
            said = ["PASS"]
    grading_id = uuid.uuid4().hex
    event.append(".", {}, "grading", ["unit=" + unit, "verdict=" + said[-1],
                                       "failing=" + ",".join(line.split(":")[0] for line in failed),
                                       "cost_usd=%s" % leaf_log.plain(cost), "id=" + grading_id,
                                       "effort=" + (effort or "default")])
    ours = stamp(with_effort([shown, claims, model], effort))
    try:
        own = signer()
        if own is sys.modules[__name__]:
            sig = ours
        else:
            sig = own.signature(path, unit) if read is None else own.signature(path, unit, text)
    except Exception as e:
        print("grade-prose.sh: signature-formula-disagreement: %s: the running grader signs %s, the tree's formula "
              "gave none (%s)"
              % (unit, ours, e), file=sys.stderr)
        return Grading(2)
    answered = dict(verdict=said[-1], failing=tuple(line.split(":")[0] for line in failed), cost=cost,
                    grading_id=grading_id)
    rejected = os.path.join(".tdd", "grade-prose-rejected")
    if not failed:
        if os.path.exists(rejected):
            with open(rejected, encoding="utf-8") as f:
                earlier = [line for line in f.read().splitlines()
                           if line.split(" ")[:2] == [unit, sig]]
            if earlier:
                return Grading(1, lines=("grade-prose.sh: %s was REJECTed on this same text (%s); change the text "
                                         "before it can be signed" % (unit, earlier[-1]),), **answered)
        own.record_graded(unit, sig, grading_id)
    else:
        os.makedirs(".tdd", exist_ok=True)
        with open(rejected, "a", encoding="utf-8") as f:
            f.write("%s %s %s %s\n" % (unit, sig, time.strftime("%Y-%m-%d"), grading_id))
    return Grading(1 if failed else 0, lines=tuple(failed), **answered)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
