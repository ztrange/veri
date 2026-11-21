"""The smell catalogue, skills/tdd/SMELLS.md, that the refactor and structural prompts include (#4115)."""
import importlib.util
import shutil

import pytest

from conftest import SCRIPTS

SMELLS = SCRIPTS.parent / "SMELLS.md"


def test_the_smell_catalogue_is_at_most_60_lines():
    assert len(SMELLS.read_bytes().splitlines()) <= 60


def scratch_builder(skill, module):
    """<module> (build_develop_prompt or build_verify_prompt) loaded from a copy of the skill at <skill>, whose
    prompts are the tree's and whose SMELLS.md is whatever the case wrote there."""
    scripts = skill / "scripts"
    (scripts / "veri").mkdir(parents=True, exist_ok=True)
    (scripts / "veri" / f"{module}.py").write_bytes((SCRIPTS / "veri" / f"{module}.py").read_bytes())
    if not (scripts / "prompts").exists():
        shutil.copytree(SCRIPTS / "prompts", scripts / "prompts")
    loader = importlib.util.spec_from_file_location(f"smells_{module}", scripts / "veri" / f"{module}.py")
    loaded = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(loaded)
    return loaded


@pytest.mark.tree_audit("the templates under prompts/, copied to render with a catalogue of the case's own")
def test_the_refactor_structural_and_verify_refactor_renders_each_carry_the_catalogue_text_whatever_it_says(
        tmp_path, capsysbinary, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "4115")
    skill = tmp_path / "skill"
    skill.mkdir()
    catalogue = b"| Sentinel Smell 7f3c | met when 9 lines | Sentinel Refactoring 7f3c |\n"
    (skill / "SMELLS.md").write_bytes(catalogue)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n\ntidy it\n")
    develop = scratch_builder(skill, "build_develop_prompt")
    verify = scratch_builder(skill, "build_verify_prompt")
    calls = {
        "develop refactor": (develop, ["refactor", str(spec), "the step", "make test", "a.py"]),
        "develop structural": (develop, ["structural", str(spec), "the candidate", "make test", "a.py"]),
        "verify refactor": (verify, ["--fast-cmd", "make unit", "--step-green", "0123abc", "refactor", str(spec), "tests/t.py", "0123abc"]),
    }
    results = {}
    for name, (module, argv) in calls.items():
        code = module.main(argv)
        out, err = capsysbinary.readouterr()
        results[name] = (code, catalogue.rstrip(b"\n") in out, err)

    assert results == {name: (0, True, b"") for name in calls}
