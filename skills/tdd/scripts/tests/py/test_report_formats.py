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


@pytest.mark.tree_audit("develop-green.md and develop-structural.md, includes expanded")
def test_1568_green_wrong_test_and_structural_skip_and_green_split_each_report_through_a_declared_exempt_key(report_formats):
    outcomes = [
        ("develop-green.md", "looks wrong"),
        ("develop-green.md", "A step that needs more than one new behaviour"),
        ("develop-structural.md", "as you found it and say so"),
    ]
    prompts = {path.name: text for path, text in expanded_develop_prompts()}
    free_text = []
    for name, phrase in outcomes:
        text = prompts[name]
        exempt_keys = {k for f in report_formats.parse(text) if f["suite"] == "exempt" for k in f["keys"]}
        paragraphs = [" ".join(p.split()) for p in text.split("\n\n")]
        owning = [p for p in paragraphs if phrase in p]
        assert owning, f"{name}: no paragraph says {phrase!r}"
        if not any(key in p for p in owning for key in exempt_keys):
            free_text.append(f"{name}: {phrase!r} names no declared SUITE-exempt key")

    assert not free_text, "\n".join(free_text)


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1568_suite_reported_passes_a_report_made_of_the_keys_of_each_exempt_format_a_real_prompt_declares(report_formats, run_cli, tmp_path):
    suite_reported = importlib.import_module("veri.suite_reported")
    prompts = expanded_develop_prompts()
    refused = []
    for path, text in prompts:
        leaf = path.stem
        for declared in report_formats.parse(text):
            if declared["suite"] != "exempt":
                continue
            work = tmp_path / f"{leaf}-{declared['name']}"
            (work / ".tdd").mkdir(parents=True)
            (work / ".tdd" / f"{leaf}.out").write_text("".join(f"{key} reported\n" for key in declared["keys"]))
            code, _, _ = run_cli(suite_reported, [leaf], env={"VERI_ISSUE": "1"}, cwd=work)
            events = work / ".tdd" / "events.jsonl"
            if code != 0 or events.exists():
                refused.append(f"{leaf} / {declared['name']}: exit {code}, report-missing recorded: {events.exists()}")

    assert prompts
    assert not refused, "\n".join(refused)


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1568_suite_reported_refuses_a_report_of_each_suite_required_format_a_real_prompt_declares_when_it_has_no_suite_line(report_formats, run_cli, tmp_path):
    suite_reported = importlib.import_module("veri.suite_reported")
    prompts = expanded_develop_prompts()
    passed = []
    cases = 0
    for path, text in prompts:
        leaf = path.stem
        for declared in report_formats.parse(text):
            if declared["suite"] != "required":
                continue
            cases += 1
            work = tmp_path / f"{leaf}-{declared['name']}"
            (work / ".tdd").mkdir(parents=True)
            (work / ".tdd" / f"{leaf}.out").write_text(
                "".join(f"{key} reported\n" for key in declared["keys"] if key != "SUITE:"))
            code, _, _ = run_cli(suite_reported, [leaf], env={"VERI_ISSUE": "1"}, cwd=work)
            events = work / ".tdd" / "events.jsonl"
            recorded = events.exists() and '"event": "report-missing"' in events.read_text()
            if code != 2 or not recorded:
                passed.append(f"{leaf} / {declared['name']}: exit {code}, report-missing recorded: {recorded}")

    assert cases
    assert not passed, "\n".join(passed)


def test_1568_stop_prose_guard_names_prompt_and_line_of_a_planted_stop_that_names_no_declared_format_and_passes_one_that_does_or_is_exempt(report_formats):
    planted = (
        "Do the step.\n"
        "If the fixture is missing, give up and say so in your report.\n"
        "If the test looks wrong, stop and report one `WRONG_TEST: <why>` line.\n"
        "Skip the candidate when it is out of bounds.\n"
        "REPORT-FORMAT green-wrong-test | keys WRONG_TEST: | suite exempt: nothing ran\n"
    )

    assert report_formats.stop_prose_offenders("develop-planted.md", planted) == [
        "develop-planted.md:2",
        "develop-planted.md:4",
    ]
    assert report_formats.stop_prose_offenders(
        "develop-planted.md", planted, exempt={"develop-planted.md:4": "a skip with nothing to report"}
    ) == ["develop-planted.md:2"]
