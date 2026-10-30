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


def expanded_develop_prompts():
    prompts = SCRIPTS / "prompts"

    def expand(text):
        return re.sub(r"\{\{INCLUDE:([^}]*)\}\}", lambda m: expand((prompts / m[1]).read_text()), text)

    return [(path, expand(path.read_text())) for path in sorted(prompts.glob("develop-*.md"))]


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1568_every_real_develop_prompt_declares_report_formats_the_parser_accepts(report_formats):
    prompts = expanded_develop_prompts()
    refused = []
    for path, text in prompts:
        try:
            report_formats.parse(text)
        except ValueError as error:
            refused.append(f"{path.name}: {error}")

    assert prompts
    assert not refused, "\n".join(refused)


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1568_every_key_a_real_develop_prompt_declares_appears_in_its_report_text(report_formats):
    prompts = expanded_develop_prompts()
    missing = []
    for path, text in prompts:
        heading = re.search(r"^#+ Report.*$", text, re.M)
        section = text[heading.start():] if heading else text
        report = "\n".join(l for l in section.splitlines() if not l.startswith("REPORT-FORMAT "))
        for declared in report_formats.parse(text):
            missing += [f"{path.name}: {key}" for key in declared["keys"] if key not in report]

    assert prompts
    assert not missing, "\n".join(missing)


def declared_formats(report_formats, suite):
    """(leaf, declared format) for each format of the given SUITE kind that a real develop prompt declares."""
    return [
        (path.stem, declared)
        for path, text in expanded_develop_prompts()
        for declared in report_formats.parse(text)
        if declared["suite"] == suite
    ]


def run_suite_reported(run_cli, work, leaf, keys):
    """(exit code, events text or None) of suite-reported.sh over a report made of `keys`."""
    (work / ".tdd").mkdir(parents=True)
    (work / ".tdd" / f"{leaf}.out").write_text("".join(f"{key} reported\n" for key in keys))
    code, _, _ = run_cli(importlib.import_module("veri.suite_reported"), [leaf], env={"VERI_ISSUE": "1"}, cwd=work)
    events = work / ".tdd" / "events.jsonl"
    return code, events.read_text() if events.exists() else None


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1568_suite_reported_passes_a_report_made_of_the_keys_of_each_exempt_format_a_real_prompt_declares(report_formats, run_cli, tmp_path):
    cases = declared_formats(report_formats, "exempt")
    refused = []
    for leaf, declared in cases:
        code, events = run_suite_reported(run_cli, tmp_path / f"{leaf}-{declared['name']}", leaf, declared["keys"])
        if code != 0 or events is not None:
            refused.append(f"{leaf} / {declared['name']}: exit {code}, report-missing recorded: {events is not None}")

    assert cases
    assert not refused, "\n".join(refused)


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1568_suite_reported_refuses_a_report_of_each_suite_required_format_a_real_prompt_declares_when_it_has_no_suite_line(report_formats, run_cli, tmp_path):
    cases = declared_formats(report_formats, "required")
    passed = []
    for leaf, declared in cases:
        keys = [key for key in declared["keys"] if key != "SUITE:"]
        code, events = run_suite_reported(run_cli, tmp_path / f"{leaf}-{declared['name']}", leaf, keys)
        recorded = events is not None and '"event": "report-missing"' in events
        if code != 2 or not recorded:
            passed.append(f"{leaf} / {declared['name']}: exit {code}, report-missing recorded: {recorded}")

    assert cases
    assert not passed, "\n".join(passed)


def test_1980_suite_reported_passes_a_retried_develop_red_2_report_made_of_the_keys_of_the_exempt_format_develop_red_declares(run_cli, tmp_path):
    keys = ["TEST_PATH:", "TARGET_TEST:", "AGAINST_UNMODIFIED:", "WHY:", "FAIL_OUTPUT:", "PREDICTED_FAILURE:",
            "PREDICTION:", "PREDICTION_NOTE:"]

    code, events = run_suite_reported(run_cli, tmp_path, "develop-red-2", keys)

    assert (code, events) == (0, None)


def test_1980_suite_reported_passes_a_retried_develop_structural_3_report_made_of_the_keys_of_the_exempt_skipped_format_develop_structural_declares(run_cli, tmp_path):
    code, events = run_suite_reported(run_cli, tmp_path, "develop-structural-3", ["SKIPPED:"])

    assert (code, events) == (0, None)


def test_1980_suite_reported_exits_2_with_one_stderr_line_naming_a_leaf_whose_prompt_file_cannot_be_found_and_records_no_report_missing(run_cli, tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-nosuchphase-2.out").write_text("SKIPPED: reported\n")

    code, _, err = run_cli(importlib.import_module("veri.suite_reported"), ["develop-nosuchphase-2"], env={"VERI_ISSUE": "1"}, cwd=tmp_path)

    assert (code, len(err.splitlines()), "develop-nosuchphase-2" in err, (tmp_path / ".tdd" / "events.jsonl").exists()) == (2, 1, True, False)
