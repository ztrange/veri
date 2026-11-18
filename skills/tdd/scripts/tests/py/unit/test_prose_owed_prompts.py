"""prose-owed.sh lists a prompt file no REQUIREMENTS.md lists as a unit (#4384)."""
import importlib
import os

PROMPTS = "skills/tdd/scripts/prompts"
ROWS = "## %s\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"


def graded_repo(root, *rowed):
    """A repository whose prompts directory holds `rowed`, each listed and graded, so prose-owed.sh owes nothing."""
    grade_prose = importlib.import_module("veri.grade_prose")
    (root / PROMPTS).mkdir(parents=True)
    for name in rowed:
        (root / PROMPTS / name).write_text("The widget is blue.\n")
    (root / "REQUIREMENTS.md").write_text("".join(ROWS % (PROMPTS + "/" + n) + "\n" for n in rowed))
    cwd = os.getcwd()
    os.chdir(root)
    try:
        lines = ["%s/%s %s g1\n" % (PROMPTS, n, grade_prose.signature("REQUIREMENTS.md", PROMPTS + "/" + n)) for n in rowed]
    finally:
        os.chdir(cwd)
    (root / "skills" / "tdd" / "GRADED").write_text("".join(lines))


def test_prose_owed_sh_prints_a_prompt_file_no_requirements_list_names_with_no_rows_and_exits_1_4384(tmp_path, run_cli):
    prose_owed = importlib.import_module("veri.prose_owed")
    graded_repo(tmp_path, "develop-x.md")
    (tmp_path / PROMPTS / "_fragment.md").write_text("Say nothing.\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.splitlines()) == (1, [PROMPTS + "/_fragment.md (no rows)"]), (code, out, err)
