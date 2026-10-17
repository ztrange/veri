"""Cases for the refactor leaf's report footer skills/tdd/SKILL.md describes, held against the report lines the built refactor prompt asks for."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"

REFACTOR = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"


def refactor_lines():
    sections = importlib.import_module("skill_sections")
    body = sections.section(SKILL, REFACTOR).split("\n")[1:]
    lines = []
    for line in body:
        if line.startswith("#"):
            break
        lines.append(line)
    return lines


def footer_labels():
    fenced, found, kept = False, False, []
    for line in refactor_lines():
        if re.match(r"\s*```", line):
            fenced = not fenced
            continue
        if not fenced and not found and "develop-refactor.out" in line:
            found = True
        if found and re.match(r"[0-9]+\. ", line):
            break
        if found:
            kept.append(line)
    footer = " ".join(kept).translate(str.maketrans("", "", "*`"))
    footer = footer.split("develop-refactor.out", 1)[1]
    return {label.rstrip(":") for label in re.findall(r"[A-Z][A-Z_]+:", footer)}


def emitted_labels(run_cli, tmp_path):
    spec = tmp_path / "spec"
    spec.write_text("spec\n")
    module = importlib.import_module("veri.build_develop_prompt")
    code, out, err = run_cli(module, ["refactor", str(spec), "step", "make test", "a.sh"])
    assert code == 0, err
    return {m.group(1) for line in out.splitlines() if (m := re.match(r"([A-Z][A-Z_]+):", line))}


def test_skill_md_refactor_section_names_exactly_the_report_lines_the_built_refactor_prompt_asks_the_leaf_for(run_cli, tmp_path):
    emitted = emitted_labels(run_cli, tmp_path)
    named = footer_labels()
    assert emitted, "build-develop-prompt.sh refactor printed no report line"
    assert named, "no account of the leaf's report after .tdd/develop-refactor.out could be found"
    assert named - emitted == set(), f"SKILL.md names report lines the prompt never asks for: {sorted(named - emitted)}"
    assert emitted - named == set(), f"SKILL.md never names report lines the prompt asks for: {sorted(emitted - named)}"
