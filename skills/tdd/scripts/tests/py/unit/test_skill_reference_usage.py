import pathlib
import re

SCRIPTS = pathlib.Path(__file__).resolve().parents[3]
SKILL = SCRIPTS.parent / "SCRIPTS.md"
SKILL_MD = SCRIPTS.parent / "SKILL.md"
# The catalogue held 29 entries when it moved out of SKILL.md (#1715); fewer means one was lost.
ENTRIES_AT_MOVE = 29


def synopses(skill):
    return [m.group(1) for m in re.finditer(r"^ *- `\$S/([^`]*)", skill.read_text(), re.M)]


def usage_block(script):
    block, found = [], False
    for line in script.read_text().splitlines():
        if found and (re.fullmatch(r"#\s*", line) or not line.startswith("#")):
            break
        found = found or bool(re.match(r"# *usage:", line, re.I))
        if found:
            block.append(line)
    return block


def flags_of(text):
    return set(re.findall(r"--[a-z][a-z0-9-]*", text))


def verbs_of(line):
    rest = line.split(" ", 1)[1] if " " in line else ""
    for pattern in (r"<[^>]*>", r"'[^']*'", r'"[^"]*"', r" #.*", r"\([^)]*\)", r"\[[^\]|\-][^\]|]*\]"):
        rest = re.sub(pattern, "", rest)
    words = re.sub(r"[\[\]]", " ", rest).split()
    return {v for w in words if not w.startswith("-") for v in w.split("|")
            if re.fullmatch(r"[a-z][a-z0-9-]*", v)}


def invocations(name, block):
    lines = (re.sub(r"^([A-Z_]+=\S* +)*", "", re.sub(r"^# *([Uu]sage:)? *", "", line)) for line in block)
    return [line for line in lines if line == name or line.startswith(name + " ")]


def problems(scripts, skill):
    found = []
    for synopsis in synopses(skill):
        name = synopsis.split(" ")[0]
        script = scripts / name
        if not script.is_file():
            continue
        block = usage_block(script)
        for flag in sorted(flags_of("\n".join(block)) - flags_of(synopsis)):
            found.append("%s: %s is in its usage line, not in SKILL.md's entry" % (name, flag))
        words = set(re.findall(r"[a-z][a-z0-9-]*", synopsis))
        verbs = set().union(*(verbs_of(line) for line in invocations(name, block)), set())
        for verb in sorted(verbs - words):
            found.append("%s: %s is a verb in its usage line, not in SKILL.md's entry" % (name, verb))
    return found


def test_a_flag_or_verb_of_a_usage_block_missing_from_its_skill_md_entry_is_named_with_its_script_and_the_real_tree_has_none(tmp_path):
    """Subject is source text: SKILL.md's script reference read against each script's `# usage:` block."""
    assert list(synopses(SKILL)) != []
    assert problems(SCRIPTS, SKILL) == []

    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "exp-two-line.sh").write_text(
        "#!/bin/sh\n# usage: exp-two-line.sh <n>\n#        exp-two-line.sh --drop <n>\n")
    skill = tmp_path / "SKILL.md"
    skill.write_text("- `$S/exp-two-line.sh <n>` — a fixture entry.\n")
    assert problems(scripts, skill) == [
        "exp-two-line.sh: --drop is in its usage line, not in SKILL.md's entry"]


def test_a_first_line_flag_and_a_missing_literal_or_alternative_verb_are_each_named_with_their_script(tmp_path):
    """Subject is source text: planted drift in a scratch SKILL.md and script, never the real ones."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "exp-verb.sh").write_text(
        "#!/bin/sh\n# usage: exp-verb.sh --quick <n>\n#        exp-verb.sh start|stop <n>\n"
        "#        exp-verb.sh reset\n")
    skill = tmp_path / "SKILL.md"
    skill.write_text("- `$S/exp-verb.sh <n> start` — a fixture entry.\n")
    assert problems(scripts, skill) == [
        "exp-verb.sh: --quick is in its usage line, not in SKILL.md's entry",
        "exp-verb.sh: reset is a verb in its usage line, not in SKILL.md's entry",
        "exp-verb.sh: stop is a verb in its usage line, not in SKILL.md's entry"]


def test_skill_md_points_at_scripts_md_and_carries_no_catalogue_entry_and_scripts_md_keeps_every_moved_entry_1715():
    """Subject is source text: SKILL.md's pointer to the catalogue and the catalogue's entry count (#1715)."""
    text = SKILL_MD.read_text()

    assert "The catalogue of every script (arguments, output, exit codes) is `<base directory>/SCRIPTS.md`." in text
    assert synopses(SKILL_MD) == []
    assert len(synopses(SKILL)) >= ENTRIES_AT_MOVE
