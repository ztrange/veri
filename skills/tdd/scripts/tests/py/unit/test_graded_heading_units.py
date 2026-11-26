"""`file#heading` units in GRADED files (PRD 024.7): a heading holding spaces is one unit field."""
import hashlib
import importlib

import pytest

MODEL = "grader-model-1"
HEADING_UNIT = "unit.md#Two words, 100% sure"
ENCODED = "unit.md#Two%20words,%20100%25%20sure"


@pytest.fixture
def grade_prose(monkeypatch):
    module = importlib.import_module("veri.grade_prose")
    monkeypatch.setattr(module, "grader_model", lambda: MODEL)
    monkeypatch.setattr(module, "grader_conf", lambda: {"model": MODEL})
    return module


def test_4016_signing_a_heading_unit_writes_each_space_as_percent_20_and_each_percent_as_percent_25(
        tmp_path, monkeypatch, grade_prose):
    monkeypatch.chdir(tmp_path)

    grade_prose.record_graded(HEADING_UNIT, "sig", "gid")

    fields = (tmp_path / "GRADED").read_text().split("\n")[0].split(" ")
    assert (len(fields), fields[:2], fields[3]) == (5, [ENCODED, "sig"], "gid")


ROWS = "| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"


def heading_tree(root):
    (root / "unit.md").write_text("# Unit\nintro\n## Two words, 100% sure\nThe widget is blue.\n## Other\nelse\n")
    (root / "REQUIREMENTS.md").write_text("## %s\n\n%s\n## unit.md\n\n%s" % (HEADING_UNIT, ROWS, ROWS))


def test_4016_prose_owed_reads_a_signed_heading_unit_back_as_owing_nothing_and_an_orphan_one_by_its_heading(
        tmp_path, monkeypatch, run_cli, grade_prose):
    owed = importlib.import_module("veri.prose_owed")
    heading_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    signed = [grade_prose.signature("REQUIREMENTS.md", unit) for unit in (HEADING_UNIT, "unit.md")]
    (tmp_path / "GRADED").write_text("%s %s 2026-01-01 g1 t1\nunit.md %s 2026-01-01 g2 t1\n"
                                     "unit.md#Gone%%20heading cafe 2026-01-01 g3 t1\n" % (ENCODED, signed[0], signed[1]))

    code, out, err = run_cli(owed, [str(tmp_path)])

    assert (code, out) == (1, "unit.md#Gone heading (orphan)\n"), err


def test_4016_a_whole_file_units_graded_line_stays_byte_for_byte_and_owes_nothing_when_a_heading_unit_is_signed_beside_it(
        tmp_path, monkeypatch, grade_prose):
    heading_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    whole = "unit.md %s 2026-01-01 g2 t1\n" % grade_prose.signature("REQUIREMENTS.md", "unit.md")
    (tmp_path / "GRADED").write_text(whole)

    grade_prose.record_graded(HEADING_UNIT, grade_prose.signature("REQUIREMENTS.md", HEADING_UNIT), "g1")

    lines = (tmp_path / "GRADED").read_text().splitlines(keepends=True)
    assert (lines[0], grade_prose.owed_listed()) == (whole, ([], []))


BEFORE = "# Unit\nintro\n## Two words, 100% sure\nThe widget is blue.\n## Other\nelse\n"


@pytest.mark.parametrize("head_text, printed", [
    (BEFORE.replace("The widget is blue.", "The widget is green."), [HEADING_UNIT, "unit.md"]),
    (BEFORE.replace("else", "something else"), ["unit.md"]),
    (BEFORE, []),
])
def test_4016_graded_changed_prints_a_heading_unit_only_when_its_section_text_changed_and_a_whole_file_unit_when_its_file_did(
        head_text, printed, tmp_path, monkeypatch, run_cli, fake_processes):
    changed = importlib.import_module("veri.graded_changed")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "GRADED").write_text("%s sig 2026-01-01 g1 t1\nunit.md sig 2026-01-01 g2 t1\n" % ENCODED)
    answer_revisions(fake_processes, {"base": {"unit.md": BEFORE}, "HEAD": {"unit.md": head_text}})

    code, out, err = run_cli(changed, ["base"], cwd=tmp_path)

    assert (code, out.splitlines()) == (1 if printed else 0, printed), err


def test_4016_the_requirements_list_of_a_heading_unit_whose_heading_holds_a_slash_sits_beside_its_file():
    requirements = importlib.import_module("veri.requirements")

    assert requirements.list_path("skills/tdd/SKILL.md#The scripts (this skill's `scripts/` directory)") == \
        "skills/tdd/REQUIREMENTS.md"


def test_4016_a_heading_units_text_is_its_own_text_up_to_the_next_unfenced_heading_of_any_level(tmp_path, grade_prose):
    (tmp_path / "unit.md").write_text("# Unit\nintro\n## Two words, 100% sure\nown\n```\n# fenced\n```\nstill own\n"
                                      "### Deeper\nsubsection\n## Other\nelse\n")

    text = grade_prose.unit_text(str(tmp_path / "unit.md") + "#Two words, 100% sure")

    assert text == "## Two words, 100% sure\nown\n```\n# fenced\n```\nstill own\n"


@pytest.mark.parametrize("prose, count", [
    ("# Unit\nintro\n## Other\nelse\n", 0),
    ("# Unit\n```\n## Two words, 100% sure\n```\n## Other\nelse\n", 0),
    ("# Unit\n## Two words, 100% sure\none\n### Two words, 100% sure\ntwo\n", 2),
])
@pytest.mark.parametrize("script", ["grade_prose", "prose_owed"])
def test_4016_grade_prose_and_prose_owed_exit_2_naming_the_unit_and_the_count_when_a_heading_units_heading_matches_no_heading_or_several(
        prose, count, script, tmp_path, monkeypatch, run_cli, grade_prose):
    heading_tree(tmp_path)
    (tmp_path / "unit.md").write_text(prose)
    monkeypatch.chdir(tmp_path)
    module = importlib.import_module("veri." + script)
    argv = ["REQUIREMENTS.md", HEADING_UNIT] if script == "grade_prose" else [str(tmp_path)]

    code, out, err = run_cli(module, argv, cwd=tmp_path)

    assert (code, HEADING_UNIT in err, "matches %d unfenced heading" % count in err) == (2, True, True), (code, out, err)


SPLIT = ("---\nname: f\n---\n# Title\ntitle text\n## Claimed one\nclaimed text\n```\n## fenced\n```\n### Sub of claimed\n"
         "sub text\n## Path/with a slash\nslash text\n## Free\nfree text\n")
SPLIT_VIEW = ("# Title\n## Claimed one\n### Sub of claimed\n## Path/with a slash\n## Free\n\n"
              "---\nname: f\n---\n# Title\ntitle text\n### Sub of claimed\nsub text\n## Free\nfree text\n")


def split_tree(root, claimed=("Claimed one", "Path/with a slash")):
    (root / "f.md").write_text(SPLIT)
    (root / "REQUIREMENTS.md").write_text("".join("## %s\n\n%s\n" % (unit, ROWS)
                                                  for unit in ["f.md"] + ["f.md#" + h for h in claimed]))


def test_4016_a_whole_file_unit_with_a_listed_heading_unit_is_split_and_signs_the_heading_lines_then_every_unclaimed_own_text(
        tmp_path, monkeypatch, grade_prose):
    split_tree(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert grade_prose.signed_text("f.md", SPLIT) == SPLIT_VIEW


def test_4016_a_whole_file_unit_with_no_listed_heading_unit_is_unsplit_and_signs_its_file(tmp_path, monkeypatch, grade_prose):
    split_tree(tmp_path, claimed=())
    monkeypatch.chdir(tmp_path)

    assert grade_prose.signed_text("f.md", SPLIT) == SPLIT


@pytest.mark.parametrize("text", [SPLIT, SPLIT.replace("\n", "\r\n"), SPLIT.rstrip("\n"), SPLIT + "\n\n"])
def test_4016_the_views_cuts_join_back_to_the_file_and_each_heading_cut_is_that_heading_units_own_text(text, grade_prose):
    cuts = grade_prose.own_texts(text)

    assert "".join(own for _, own in cuts) == text
    assert [own for line, own in cuts[1:]] == [grade_prose.section(text, grade_prose.heading_text(line)) for line, _ in cuts[1:]]


def signed_split_tree(root, grade_prose):
    split_tree(root)
    units = ["f.md", "f.md#Claimed one", "f.md#Path/with a slash"]
    (root / "GRADED").write_text("".join(
        grade_prose.graded_line([u, grade_prose.signature("REQUIREMENTS.md", u), "2026-01-01", "g", "t"]) + "\n"
        for u in units))


@pytest.mark.parametrize("old, new, owed", [
    ("claimed text", "claimed words", ["f.md#Claimed one"]),
    ("slash text", "slash words", ["f.md#Path/with a slash"]),
    # A subsection of a claimed section is not in the claimed unit's own text; unclaimed, it is in f.md's view.
    ("sub text", "sub words", ["f.md"]),
    ("free text", "free words", ["f.md"]),
    ("## Free\n", "## Freed\n", ["f.md"]),
    ("name: f\n", "name: g\n", ["f.md"]),
    ("title text", "title words", ["f.md"]),
])
def test_4016_an_edit_owes_the_unit_that_signs_the_edited_text_and_no_other(
        old, new, owed, tmp_path, monkeypatch, run_cli, grade_prose):
    monkeypatch.chdir(tmp_path)
    signed_split_tree(tmp_path, grade_prose)
    (tmp_path / "f.md").write_text(SPLIT.replace(old, new))

    code, out, err = run_cli(importlib.import_module("veri.prose_owed"), [str(tmp_path)])

    assert (code, out.splitlines()) == (1, owed), err


def test_4016_a_split_whole_file_units_signature_stamps_its_view_its_rows_and_the_model(tmp_path, monkeypatch, grade_prose):
    split_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    claims = "A1\tThe widget is blue.\n"

    expected = hashlib.sha256("\0".join([SPLIT_VIEW, claims, MODEL]).encode("utf-8")).hexdigest()

    assert grade_prose.signature("REQUIREMENTS.md", "f.md") == expected


def test_4016_removing_the_last_listed_heading_unit_unsplits_the_whole_file_unit_which_owes_against_its_whole_file(
        tmp_path, monkeypatch, run_cli, grade_prose):
    monkeypatch.chdir(tmp_path)
    signed_split_tree(tmp_path, grade_prose)
    (tmp_path / "REQUIREMENTS.md").write_text("## f.md\n\n%s" % ROWS)
    whole = hashlib.sha256("\0".join([SPLIT, "A1\tThe widget is blue.\n", MODEL]).encode("utf-8")).hexdigest()

    code, out, err = run_cli(importlib.import_module("veri.prose_owed"), [str(tmp_path)])

    assert (code, out.splitlines(), grade_prose.signature("REQUIREMENTS.md", "f.md")) == (
        1, ["f.md", "f.md#Claimed one (orphan)", "f.md#Path/with a slash (orphan)"], whole), err


def test_4016_grade_prose_shows_the_grader_a_split_whole_file_units_view_and_signs_it_while_unit_text_is_the_whole_file(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    import json
    split_tree(tmp_path)
    (tmp_path / ".tdd").mkdir()
    prompts = []

    def launch(line, **kwargs):
        with open(line.split()[3], encoding="utf-8") as f:
            prompts.append(f.read())
        reply = "BEGIN GRADES\nA1: PASS - blue\nVERDICT: PASS\nEND GRADES\n"
        (tmp_path / ".tdd" / "grade-prose.log").write_text(json.dumps({"type": "result", "result": reply}) + "\n")
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    fake_processes.answers({"supervise.sh": launch})
    monkeypatch.chdir(tmp_path)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "f.md"], cwd=tmp_path)

    graded = tmp_path / "GRADED"
    signed = [line.split(" ")[1] for line in graded.read_text().splitlines() if line.startswith("f.md ")] if graded.exists() else []
    assert (code, prompts, signed, grade_prose.unit_text("f.md")) == (
        0, [grade_prose.prompt("f.md", SPLIT_VIEW, "A1\tThe widget is blue.\n")],
        [grade_prose.signature("REQUIREMENTS.md", "f.md")], SPLIT), err


@pytest.mark.parametrize("head_text, printed", [
    (BEFORE.replace("The widget is blue.", "The widget is green."), [HEADING_UNIT]),
    (BEFORE.replace("else", "something else"), ["unit.md"]),
    (BEFORE.replace("## Other", "## Another"), ["unit.md"]),
    (BEFORE.replace("intro", "preface"), ["unit.md"]),
])
def test_4016_graded_changed_prints_a_split_whole_file_unit_only_when_its_view_changed(
        head_text, printed, tmp_path, monkeypatch, run_cli, fake_processes):
    changed = importlib.import_module("veri.graded_changed")
    heading_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "GRADED").write_text("%s sig 2026-01-01 g1 t1\nunit.md sig 2026-01-01 g2 t1\n" % ENCODED)
    listed = (tmp_path / "REQUIREMENTS.md").read_text()
    answer_revisions(fake_processes, {"base": {"unit.md": BEFORE, "REQUIREMENTS.md": listed},
                                      "HEAD": {"unit.md": head_text, "REQUIREMENTS.md": listed}})

    code, out, err = run_cli(changed, ["base"], cwd=tmp_path)

    assert (code, out.splitlines()) == (1, printed), err


def answer_revisions(fake_processes, revisions):
    """Answers graded-changed.sh's git calls from `revisions`, {rev: {path: text}}: the diff between `base` and `HEAD`,
    each revision's file list and each file's text there (a path absent at a revision is a failed show)."""
    def show(line, **kwargs):
        rev, _, path = line.split(" ", 2)[2].partition(":")
        text = revisions[rev].get(path)
        return (0, text, "") if text is not None else (128, "", "fatal: path not in revision")

    changed = sorted(p for p in set(revisions["base"]) | set(revisions["HEAD"])
                     if revisions["base"].get(p) != revisions["HEAD"].get(p))
    table = {"git diff --name-only base HEAD": (0, "".join(p + "\n" for p in changed), ""), "git show": show}
    for rev, files in revisions.items():
        table["git ls-tree -r -z --name-only " + rev] = (0, "".join(p + "\0" for p in sorted(files)), "")
    fake_processes.answers(table)


WHOLE_LISTED = "## unit.md\n\n%s" % ROWS
BOTH_LISTED = "## %s\n\n%s\n## unit.md\n\n%s" % (HEADING_UNIT, ROWS, ROWS)
CLAIMED_EDIT = BEFORE.replace("The widget is blue.", "The widget is green.")


@pytest.mark.parametrize("base_list, head_list, graded, printed", [
    # The range claims A and edits inside it: the base view keeps A, the HEAD view does not, so unit.md is reported
    # although f.md#A has no GRADED line yet.
    (WHOLE_LISTED, BOTH_LISTED, "unit.md sig 2026-01-01 g2 t1\n", ["unit.md"]),
    # The reverse: the range drops the claim on A and edits inside it.
    (BOTH_LISTED, WHOLE_LISTED, "%s sig 2026-01-01 g1 t1\nunit.md sig 2026-01-01 g2 t1\n" % ENCODED,
     [HEADING_UNIT, "unit.md"]),
])
def test_4016_graded_changed_cuts_each_revisions_view_by_the_heading_units_that_revision_lists(
        base_list, head_list, graded, printed, tmp_path, monkeypatch, run_cli, fake_processes):
    changed = importlib.import_module("veri.graded_changed")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "REQUIREMENTS.md").write_text(head_list)
    (tmp_path / "GRADED").write_text(graded)
    answer_revisions(fake_processes, {
        "base": {"unit.md": BEFORE, "REQUIREMENTS.md": base_list, "GRADED": graded},
        "HEAD": {"unit.md": CLAIMED_EDIT, "REQUIREMENTS.md": head_list, "GRADED": graded},
    })

    code, out, err = run_cli(changed, ["base"], cwd=tmp_path)

    assert (code, out.splitlines()) == (1, printed), err
