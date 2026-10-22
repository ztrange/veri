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


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1568_every_stop_skip_give_up_or_say_so_line_in_the_real_develop_prompts_names_a_declared_format_or_is_exempt(report_formats):
    prompts = expanded_develop_prompts()
    offenders = []
    for path, text in prompts:
        offenders += report_formats.stop_prose_offenders(path.name, text)

    assert prompts
    assert not offenders, "\n".join(offenders)


@pytest.mark.tree_audit("skills/tdd/scripts/prompts/develop-revise.md, includes expanded")
def test_1586_the_revise_prompts_suite_fallback_line_is_exempt_wherever_the_wrong_test_placeholders_leave_it(report_formats):
    texts = {path.name: text for path, text in expanded_develop_prompts()}

    assert report_formats.stop_prose_offenders("develop-revise.md", texts["develop-revise.md"]) == []


@pytest.mark.tree_audit("every skills/tdd/scripts/prompts/develop-*.md prompt, includes expanded")
def test_1615_every_exempt_stop_prose_entry_names_a_line_of_a_real_develop_prompt_that_still_has_a_stop_word(report_formats):
    lines = {path.name: text.splitlines() for path, text in expanded_develop_prompts()}
    stale = []
    for where in report_formats.EXEMPT:
        prompt, number = where.rsplit(":", 1)
        text = lines.get(prompt, [])
        line = text[int(number) - 1] if 0 < int(number) <= len(text) else ""
        if not report_formats._STOP_WORDS.search(line):
            stale.append(where)

    assert not stale, "\n".join(stale)


@pytest.mark.tree_audit("skills/tdd/scripts/prompts/develop-red-supersede.md, includes expanded")
def test_1862_the_red_supersede_prompts_suite_fallback_line_is_exempt_or_names_a_declared_format(report_formats):
    texts = {path.name: text for path, text in expanded_develop_prompts()}

    assert report_formats.stop_prose_offenders("develop-red-supersede.md", texts["develop-red-supersede.md"]) == []
