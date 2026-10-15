"""In-process cases for veri/report_formats.py, the parser of a develop prompt's declared report formats."""
import importlib
import re

import pytest

from conftest import SCRIPTS


@pytest.fixture
def report_formats():
    return importlib.import_module("veri.report_formats")


def test_parse_reads_each_declared_format_refuses_none_and_a_required_format_without_suite_and_never_reads_an_outcome_line(report_formats):
    declared = (
        "Report.\n"
        "REPORT-FORMAT green | keys IMPL_PATH: SUITE: | suite required\n"
        "REPORT-FORMAT split | keys SPLIT: | suite exempt: a split runs no tests\n"
    )
    revise = "OUTCOME: revised\nREPORT-FORMAT revise | keys OUTCOME: SUITE: | suite required\n"

    assert report_formats.parse(declared) == [
        {"name": "green", "keys": ["IMPL_PATH:", "SUITE:"], "suite": "required", "reason": ""},
        {"name": "split", "keys": ["SPLIT:"], "suite": "exempt", "reason": "a split runs no tests"},
    ]
    assert [f["name"] for f in report_formats.parse(revise)] == ["revise"]
    for text in ("OUTCOME: revised\nSUITE: ran\n",
                 "REPORT-FORMAT green | keys IMPL_PATH: | suite required\n"):
        with pytest.raises(ValueError):
            report_formats.parse(text)


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1568_every_real_develop_prompt_declares_report_formats_the_parser_accepts(report_formats):
    prompts = SCRIPTS / "prompts"

    def expand(text):
        return re.sub(r"\{\{INCLUDE:([^}]*)\}\}", lambda m: expand((prompts / m[1]).read_text()), text)

    paths = sorted(prompts.glob("develop-*.md"))
    refused = []
    for path in paths:
        try:
            report_formats.parse(expand(path.read_text()))
        except ValueError as error:
            refused.append(f"{path.name}: {error}")

    assert paths
    assert not refused, "\n".join(refused)


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1568_every_key_a_real_develop_prompt_declares_appears_in_its_report_text(report_formats):
    prompts = SCRIPTS / "prompts"

    def expand(text):
        return re.sub(r"\{\{INCLUDE:([^}]*)\}\}", lambda m: expand((prompts / m[1]).read_text()), text)

    paths = sorted(prompts.glob("develop-*.md"))
    missing = []
    for path in paths:
        text = expand(path.read_text())
        heading = re.search(r"^#+ Report.*$", text, re.M)
        section = text[heading.start():] if heading else text
        report = "\n".join(l for l in section.splitlines() if not l.startswith("REPORT-FORMAT "))
        for declared in report_formats.parse(text):
            missing += [f"{path.name}: {key}" for key in declared["keys"] if key not in report]

    assert paths
    assert not missing, "\n".join(missing)
