"""In-process cases for CLAUDE.md's record of the fast test tier."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
CLAUDE_MD = "CLAUDE.md"
LOWER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def plain(text):
    return text.replace("*", "").replace("`", "").translate(LOWER)


def section_records(section_name):
    inside, out, rec = False, [], ""
    for line in (ROOT / CLAUDE_MD).read_text().split("\n"):
        if not inside:
            inside = line == f"## {section_name}"
            continue
        if line.startswith("## "):
            break
        if re.match(r"[-*] ", line):
            if rec != "":
                out.append(rec)
            rec = line
        elif re.match(r"\s*$", line):
            if rec != "":
                out.append(rec)
            rec = ""
        elif rec == "":
            rec = line
        else:
            rec = rec + " " + line
    if rec != "":
        out.append(rec)
    return [plain(r) for r in out]


def read_section(problems, section_name):
    records = section_records(section_name)
    if "".join(records).replace(" ", "") != "":
        return records
    problems.append(f"{CLAUDE_MD} has no '## {section_name}' section to read")
    return None


def says(problems, section_name, records, fact, *regexes):
    for line in records:
        if all(re.search(r, line) for r in regexes):
            return
    problems.append(f"{CLAUDE_MD}'s '{section_name}' section does not say {fact}")


IDIOM = "Testing idiom"


def test_claude_md_commands_table_and_testing_idiom_section_describe_the_pytest_leg_its_admission_rule_make_install_dev_venv_and_the_two_refusals():
    problems = []
    records = read_section(problems, IDIOM)
    if records is not None:
        says(problems, IDIOM, records, "that make unit and make test run a pytest leg over skills/tdd/scripts/tests/py/",
             r"pytest", r"skills/tdd/scripts/tests/py/?", r"make unit", r"make test")
        says(problems, IDIOM, records, "the pytest suites' admission rule — no process but the interpreter",
             r"pytest", r"no (other )?process (but|other than|except|besides) the interpreter")
        says(problems, IDIOM, records,
             "that make install-dev installs pytest into the one environment at VERI_VENV, default ~/.veri-tools/venv",
             r"make install-dev", r"veri_venv", r"\.veri-tools/venv")
        says(problems, IDIOM, records, "the refusal when pytest cannot be imported — exit 2, naming make install-dev",
             r"pytest", r"exit 2|refuse", r"make install-dev")
        says(problems, IDIOM, records, "the refusal below the interpreter floor — exit 2, naming Python 3.12",
             r"3\.12", r"floor|older", r"exit 2|refuse")
    records = read_section(problems, "Commands")
    if records is not None:
        says(problems, "Commands", records, "a row for make install-dev naming requirements-dev.txt and VERI_VENV",
             r"make install-dev", r"requirements-dev\.txt", r"veri_venv")
    assert problems == []


def test_claude_md_testing_idiom_section_records_the_shim_convention_for_a_ported_script_and_that_its_tests_live_in_tests_py_test_module_py():
    problems = []
    records = read_section(problems, IDIOM)
    if records is not None:
        says(problems, IDIOM, records,
             "the shim convention — a ported script's .sh entry point is a /bin/sh shim over its veri/ module, its Bash holding no Python source",
             r"port", r"\.sh", r"/bin/sh", r"shim", r"veri/", r"module",
             r"no python source|never (contains|holds) python source|holds no python")
        says(problems, IDIOM, records, "that a ported script's tests live in tests/py/test_<module>.py, one file per module",
             r"port", r"tests/py/test_<module>\.py\b")
    assert problems == []
