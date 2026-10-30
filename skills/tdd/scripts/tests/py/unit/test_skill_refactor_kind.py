"""Cases for what skills/tdd/SKILL.md tells a refactor-kind run, read as text."""
import importlib
import pathlib

import pytest
from skill_sections import has, plain_folded as plain, window

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


@pytest.fixture
def build_develop_prompt():
    return importlib.import_module("veri.build_develop_prompt")


def skill_text():
    return plain(SKILL.with_name("REFACTOR-KIND.md").read_bytes())


def test_the_develop_cover_prompt_ends_in_covered_and_caught_by_lines(
    tmp_path, run_cli, build_develop_prompt
):
    spec = tmp_path / "spec"
    spec.write_text("QWIXTLE spec\n")
    code, out, _ = run_cli(build_develop_prompt, ["cover", str(spec), "Extract Function QWIXTLE", "make test"])
    raw = out.encode()
    assert raw.strip(), "build-develop-prompt.sh cover printed no prompt to read"
    tail = b"\n".join([line for line in raw.split(b"\n") if line.strip()][-3:])
    assert has(tail, r"^COVERED:"), "closing lines carry no COVERED: line"
    assert has(tail, r"^CAUGHT_BY:"), "closing lines carry no CAUGHT_BY: line"



def test_skill_md_says_a_diff_checked_step_in_a_refactor_kind_run_runs_develop_diff_then_verify_diff_and_never_cover_or_transform_1915():
    near = window(b" ".join(skill_text().split()), r"unless it is ⟦diff-checked⟧", 400)
    assert near, "never says what a diff-checked step runs in a refactor-kind run"
    assert has(near, r"develop-diff then verify-diff"), "does not say it runs develop-diff then verify-diff"
    assert has(near, r"never cover or transform"), "does not say it never runs Cover or Transform"
