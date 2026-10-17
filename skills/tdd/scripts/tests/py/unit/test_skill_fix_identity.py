"""Cases for where the /tdd-fix skill ships, what it calls itself, and what it asks the user for."""
import os
import re
import stat

import pytest

from conftest import ROOT

SKILL_DIR = "skills/tdd-fix"
WANT_NAME = "tdd-fix"
SKILL_MD = f"{SKILL_DIR}/SKILL.md"
README = "README.md"


def read_bytes_as_text(path):
    return (ROOT / path).read_bytes().decode("latin-1")


def ascii_lower(text):
    return text.translate({code: code + 32 for code in range(ord("A"), ord("Z") + 1)})


def fold_prose(text):
    return ascii_lower(text.replace("*", "").replace("`", "")).replace("\n", " ")


def frontmatter_name(path):
    lines = read_bytes_as_text(path).splitlines()
    if not lines or lines[0] != "---":
        return ""
    for line in lines[1:]:
        if line == "---":
            return ""
        if line.startswith("name:"):
            return line[len("name:"):].lstrip(" \t")
    return ""


def body_text(path):
    out, inside, body = [], False, False
    for number, line in enumerate(read_bytes_as_text(path).splitlines(), 1):
        if number == 1 and line == "---":
            inside = True
        elif inside and line == "---":
            inside, body = False, True
        elif body:
            out.append(line)
    return fold_prose("".join(line + "\n" for line in out))


def issue_body_template(path):
    inside, found, buf = False, False, ""
    for line in read_bytes_as_text(path).splitlines():
        if re.match(r"^\s*```", line):
            if inside:
                if found:
                    return buf
                inside = False
                continue
            inside, buf, found = True, "", False
            continue
        if inside:
            buf += line + "\n"
            if re.match(r"^##\s+What happened\s*$", line):
                found = True
    return ""


def criteria_block(template):
    out, seen = [], False
    for line in template.splitlines():
        if re.match(r"^##\s+Acceptance criteria\s*$", line):
            seen = True
        elif seen and re.match(r"^##[^#]", line):
            break
        elif seen:
            out.append(line)
    return fold_prose("".join(line + "\n" for line in out))


def has_skill_md(problems):
    if (ROOT / SKILL_MD).is_file():
        return True
    problems.append(f"want a SKILL.md at {SKILL_MD}, found none")
    return False


def quoted_template(problems):
    template = issue_body_template(SKILL_MD)
    if not template:
        problems.append(f"{SKILL_MD} quotes no issue body: no fenced block in it holds a '## What happened' line")
    return template


def says(problems, text, pattern, message):
    if not re.search(pattern, text):
        problems.append(message)


def test_skill_md_is_the_tdd_fix_skill_and_asks_only_for_what_the_optional_description_left_out_in_one_short_round():
    problems = []
    if not (ROOT / SKILL_DIR).is_dir():
        problems.append(f"want a directory at {SKILL_DIR}, found none")
    if has_skill_md(problems):
        got = frontmatter_name(SKILL_MD)
        if got != WANT_NAME:
            problems.append(f"{SKILL_MD} frontmatter: want name '{WANT_NAME}', got {got!r}")
        text = body_text(SKILL_MD)
        if not text.replace(" ", ""):
            problems.append(f"{SKILL_MD} has no body after its frontmatter — the intake could not be read")
        else:
            says(problems, text, r"description[^.]{0,80}optional|optional[^.]{0,80}description|omit[^.]{0,80}description",
                 f"{SKILL_MD} never says the one-line description is optional")
            says(problems, text, r"(only|just)[^.]{0,100}(left out|did not answer|didn.t answer|missing|unanswered)|(left out|did not answer|didn.t answer|unanswered)[^.]{0,100}(only|just)",
                 f"{SKILL_MD} never says it asks only for what the description left out")
            says(problems, text, r"one[^.]{0,40}round|single[^.]{0,40}round|one[^.]{0,40}question|no essay",
                 f"{SKILL_MD} never says the asking is one short round")
    assert not problems, "\n".join(problems)


def test_skill_md_quotes_an_issue_body_carrying_exactly_the_six_headings_the_conductor_reads_with_blocked_by_holding_none():
    problems = []
    want_headings = ["## What happened", "## Expected", "## Steps to reproduce", "## Environment",
                     "## Acceptance criteria", "## Blocked by"]
    if has_skill_md(problems):
        template = quoted_template(problems)
        if template:
            got = [line for line in template.splitlines() if re.match(r"^##[^#]", line)]
            if got != want_headings:
                problems.append(f"{SKILL_MD}'s issue body has the wrong headings: want {want_headings}, got {got}")
            blocked, seen = "", False
            for line in template.splitlines():
                if re.match(r"^##\s+Blocked by\s*$", line):
                    seen = True
                elif seen and line.strip():
                    blocked = line
                    break
            if blocked != "None.":
                problems.append(f"{SKILL_MD}'s issue body: want 'None.' under '## Blocked by', got {blocked!r}")
    assert not problems, "\n".join(problems)


def test_skill_md_issue_body_writes_one_acceptance_criterion_per_manifestation_each_failing_now_and_passing_after_the_fix():
    problems = []
    if has_skill_md(problems):
        template = quoted_template(problems)
        if template:
            text = criteria_block(template)
            if not text.replace(" ", ""):
                problems.append(f"{SKILL_MD}'s issue body has nothing under '## Acceptance criteria'")
            else:
                says(problems, text, r"- \[ \]",
                     f"{SKILL_MD}'s issue body writes no '- [ ]' checkbox under '## Acceptance criteria'")
                says(problems, text, r"one[^.]{0,40}per manifestation|per manifestation",
                     f"{SKILL_MD}'s issue body never says one criterion per manifestation")
                says(problems, text, r"(reproduction|repro)[^.]{0,80}fails[^.]{0,80}(current|today|now|unfixed)",
                     f"{SKILL_MD}'s issue body never says the reproduction fails on the current code")
                says(problems, text, r"passes[^.]{0,60}(after the fix|once fixed|when fixed)",
                     f"{SKILL_MD}'s issue body never says the reproduction passes after the fix")
    assert not problems, "\n".join(problems)


def test_skill_md_labels_the_issue_bug_and_the_scopes_opt_in_label_creating_bug_where_the_repo_lacks_it():
    problems = []
    if has_skill_md(problems):
        text = body_text(SKILL_MD)
        if not text.replace(" ", ""):
            problems.append(f"{SKILL_MD} has no body after its frontmatter — the labelling could not be read")
        else:
            says(problems, text, r"labels?[^.]{0,120}bug",
                 f"{SKILL_MD} never says the issue is labelled bug")
            says(problems, text, r"ready-for-agent[^.:]{0,80}default|default[^.]{0,80}ready-for-agent",
                 f"{SKILL_MD} never says ready-for-agent is the opt-in label by default")
            says(problems, text, r"ready-for-agent:[^ ]*[^.]{0,100}scope|scope[^.]{0,100}ready-for-agent:",
                 f"{SKILL_MD} never says a named scope makes the opt-in label ready-for-agent:<scope>")
            says(problems, text, r"creates?[^.]{0,120}bug label|bug label[^.]{0,120}(if|when)[^.]{0,80}(lacks|missing|absent|removed|no )|gh label create",
                 f"{SKILL_MD} never says it creates the bug label where the repo lacks it")
    assert not problems, "\n".join(problems)


def test_skill_md_asks_before_starting_the_fix_run_and_invokes_tdd_only_on_yes():
    problems = []
    if has_skill_md(problems):
        text = body_text(SKILL_MD)
        if not text.replace(" ", ""):
            problems.append(f"{SKILL_MD} has no body after its frontmatter — the fix-run offer could not be read")
        else:
            says(problems, text, r"ask[^.]{0,120}(before|first)[^.]{0,120}(/tdd|fix run)|(before|first)[^.]{0,120}ask[^.]{0,120}(/tdd|fix run)",
                 f"{SKILL_MD} never says it asks before starting the fix run")
            says(problems, text, r"only[^.]{0,80}yes|yes[^.]{0,80}only|if[^.]{0,40}yes|on a yes",
                 f"{SKILL_MD} never says it invokes /tdd only on yes")
    assert not problems, "\n".join(problems)


def shipped_scripts(skill_dir):
    shipped = []
    for top, dirs, files in os.walk(ROOT / skill_dir):
        for name in dirs + files:
            path = os.path.join(top, name)
            mode = os.lstat(path).st_mode
            if (name.endswith(".sh") or (stat.S_ISDIR(mode) and name == "scripts")
                    or (stat.S_ISREG(mode) and mode & stat.S_IXUSR)):
                shipped.append(os.path.relpath(path, ROOT))
    return shipped


@pytest.mark.tree_audit("skills/tdd-fix for scripts")
def test_readme_documents_tdd_fix_beside_tdd_and_the_skill_dir_ships_no_scripts():
    problems = []
    if (ROOT / README).is_file():
        section, found = [], False
        for line in read_bytes_as_text(README).splitlines():
            if re.match(r"^##[^#]", line):
                if found:
                    break
                section = []
            section.append(line)
            if f"/{WANT_NAME}" in line:
                found = True
        if not found:
            problems.append(f"{README} never mentions /{WANT_NAME}")
        else:
            text = fold_prose("".join(line + "\n" for line in section))
            says(problems, text, r"/tdd[^-a-z]",
                 f"{README} documents /{WANT_NAME} in a section that never names /tdd")
            says(problems, text, r"bug", f"{README} never says /{WANT_NAME} files a bug")
    else:
        problems.append(f"want a {README} at the repo root, found none")
    if (ROOT / SKILL_DIR).is_dir():
        shipped = shipped_scripts(SKILL_DIR)
        if shipped:
            problems.append(f"{SKILL_DIR} ships scripts and is meant to ship none: {' '.join(shipped)}")
    assert not problems, "\n".join(problems)
