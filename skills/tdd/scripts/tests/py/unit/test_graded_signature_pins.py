"""The signatures that stamp graded prose, pinned as exact values, and the prose-owed listing built on them.

A signature that drifts re-opens every graded unit (prose-owed lists it as owed), so the digests below are literal:
changing the formula, a unit's text cut or the grader.conf parse must change them on purpose, never by a refactor."""
import hashlib
import importlib
import shutil
from pathlib import Path

import pytest

MODEL = "grader-model-1"

UNITS = {
    "plain.md": "The widget is blue.\n",
    "no-newline.md": "The widget is blue.",
    "empty.md": "",
    "sections.md": "# Top\nintro\n## Part one\nfirst\n```\n## Part two\ndecoy\n```\n## Part two\nsecond\nline\n## Part three\nthird\n",
    "unicode.md": "Der Käfer ist blau — 青い.\n",
}
UNIT_NAMES = ["plain.md", "no-newline.md", "empty.md", "sections.md#Part two", "sections.md#Part one",
              "unicode.md"]
ROW = "| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n| A2 | It is round \\| flat. | because |\n"

PINS = {
    "plain.md": "3a0cd88c3f8b7b366e8dd51e6228a17c7f12d5aa52d7f0a1c4818e64260b79d2",
    "no-newline.md": "34c9a41856a9f1f37b97ff4a0073979b80c3d4e59ab7ee587d51d64f4c0d8821",
    "empty.md": "0dfad5ea9d8e0285c5d1e4b6c224bb16f562599b3e6860ac75a6b9bd6dcc7a93",
    "sections.md#Part two": "57265dd0e3b29a981fdeb5eb18d691d784ec2053f668b6c8fb2fe61377ecd5fe",
    "sections.md#Part one": "539b30f097346c6be960d3a7191c6e63c04a0d1568ec23efbe7ad1309753cbc9",
    "unicode.md": "03367441b15ed2d415bb2d8747b74b7c707763923136148fd07b90940e3e91b3",
}


@pytest.fixture
def grade_prose(monkeypatch):
    module = importlib.import_module("veri.grade_prose")
    monkeypatch.setattr(module, "grader_model", lambda: MODEL)
    return module


def _tree(root):
    for name, text in UNITS.items():
        (root / name).write_text(text)
    (root / "REQUIREMENTS.md").write_text("".join(f"## {unit}\n\n{ROW}\n" for unit in UNIT_NAMES))


@pytest.mark.parametrize("unit", UNIT_NAMES)
def test_the_signature_of_a_fixed_unit_is_the_pinned_digest(tmp_path, monkeypatch, grade_prose, unit):
    _tree(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert grade_prose.signature("REQUIREMENTS.md", unit) == PINS[unit]


def test_the_signature_is_the_sha256_of_the_unit_text_the_claims_and_the_model_joined_by_nul(tmp_path, monkeypatch, grade_prose):
    _tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    claims = "A1\tThe widget is blue.\nA2\tIt is round | flat.\n"

    expected = hashlib.sha256(("\0".join(["The widget is blue.\n", claims, MODEL])).encode("utf-8")).hexdigest()

    assert grade_prose.signature("REQUIREMENTS.md", "plain.md") == expected


def test_the_grader_model_is_the_first_value_line_of_grader_conf(tmp_path, monkeypatch):
    module = importlib.import_module("veri.grade_prose")
    scripts = tmp_path / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("# comment\n\nmodel = 'claude-x-4'\nother=ignored\n")
    monkeypatch.setattr(module, "SCRIPTS", str(scripts))

    assert module.grader_model() == "claude-x-4"


def test_the_graded_path_is_the_skills_graded_file_or_the_one_beside_the_unit(grade_prose):
    assert grade_prose.graded_path("skills/tdd/SKILL.md#x") == str(Path("skills/tdd/GRADED"))
    assert grade_prose.graded_path("docs/adr/0001-demo.md") == str(Path("docs/adr/GRADED"))
    assert grade_prose.graded_path("README.md") == "GRADED"


def test_signer_runs_the_trees_own_copy_of_grade_prose_when_the_tree_has_one(tmp_path, monkeypatch, grade_prose):
    _tree(tmp_path)
    own = Path(grade_prose.__file__)
    tree_file = tmp_path / "skills" / "tdd" / "scripts" / "veri" / "grade_prose.py"
    tree_file.parent.mkdir(parents=True)
    shutil.copy(own, tree_file)
    tree_file.write_text(tree_file.read_text() + "\nTREE_COPY = True\n")
    monkeypatch.chdir(tmp_path)

    tree = grade_prose.signer()

    tree.grader_model = lambda: MODEL
    assert tree is not grade_prose and tree.TREE_COPY is True
    assert tree.signature("REQUIREMENTS.md", "plain.md") == grade_prose.signature("REQUIREMENTS.md", "plain.md")


def test_signer_is_the_running_module_when_the_tree_has_no_copy(tmp_path, monkeypatch, grade_prose):
    monkeypatch.chdir(tmp_path)

    assert grade_prose.signer() is grade_prose


def _graded(root, lines):
    (root / "GRADED").write_text("".join(line + "\n" for line in lines))


def test_prose_owed_lists_the_stale_and_the_unsigned_units_and_the_orphan_and_not_the_current_one(
        tmp_path, monkeypatch, run_cli, grade_prose):
    owed = importlib.import_module("veri.prose_owed")
    _tree(tmp_path)
    (tmp_path / "REQUIREMENTS.md").write_text("".join(f"## {unit}\n\n{ROW}\n" for unit in ["plain.md", "empty.md", "unicode.md"]))
    _graded(tmp_path, [f"plain.md {PINS['plain.md']} 2026-01-01 g1 t1", "empty.md deadbeef 2026-01-01 g2 t1",
                       "gone.md cafe 2026-01-01 g3 t1"])

    code, out, err = run_cli(owed, [str(tmp_path)])

    assert (code, out.split("\n")[:-1]) == (1, ["empty.md", "unicode.md", "gone.md (orphan)"]), (code, out, err)
