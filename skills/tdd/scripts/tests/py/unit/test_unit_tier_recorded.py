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


def test_claude_md_testing_idiom_section_names_skills_tdd_scripts_tests_unit_as_the_fast_tier_and_states_its_admission_bar():
    problems = []
    records = read_section(problems, IDIOM)
    if records is not None:
        says(problems, IDIOM, records, "that skills/tdd/scripts/tests/unit/ is the fast tier",
             r"skills/tdd/scripts/tests/unit/?", r"fast")
        says(problems, IDIOM, records,
             "the admission bar — about 100 ms per case, and no git, network, servers, real waits or nested suites",
             r"100 ?ms ?(/|per|a|each) ?case", r"git", r"network", r"server", r"real waits?|sleep", r"nested")
    assert problems == []


def test_claude_md_testing_idiom_section_documents_the_unit_tier_migration_pattern_naming_lib_github_sh_as_what_still_follows_it_and_push_branch_sh_as_having_left_it_for_the_python_convention():
    problems = []
    records = read_section(problems, IDIOM)
    if records is not None:
        says(problems, IDIOM, records,
             "the migration pattern — a main guard, a unit suite that sources the script, dependencies mocked as same-named shell functions, the CLI contract unchanged",
             r"bash_source|main guard", r"sources?|sourcing", r"mock", r"shell functions?|same-named",
             r"cli contract|byte-identical", r"unchanged|unmodified|byte-identical")
        says(problems, IDIOM, records,
             "that lib/github.sh, sourced by the unit/github suite with gh mocked as a shell function, still follows that pattern",
             r"lib/github\.sh", r"tests/unit/github\.test\.sh", r"(^|[^a-z])gh([^a-z]|$)", r"mock", r"shell function")
        says(problems, IDIOM, records,
             "that push-branch.sh left that pattern for the Python convention status.sh is the worked example of",
             r"push-branch\.sh", r"left|leaves|moved|ported", r"python", r"status\.sh", r"worked example")
        if re.search(r"push-branch\.sh is (its|the) worked example", "\n".join(records)):
            problems.append(f"{CLAUDE_MD}'s '{IDIOM}' section still names push-branch.sh the worked example of the unit-tier pattern")
    assert problems == []


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
        says(problems, IDIOM, records, "that a ported script's tests live in tests/py/test_<module>.py",
             r"port", r"tests/py/test_<module>\.py")
    assert problems == []


def test_claude_md_testing_idiom_section_says_which_python3_call_the_fast_tiers_guard_lets_through_one_whose_first_argument_is_a_module_file_under_skills_tdd_scripts_veri():
    problems = []
    records = read_section(problems, IDIOM)
    if records is not None:
        says(problems, IDIOM, records,
             "in the admission-bar passage that shims git, gh, curl and python3, that the python3 call let through is one whose first argument is a module file under skills/tdd/scripts/veri/, a ported script's shim hand-off",
             r"make unit", r"shims git, gh, curl and python3", r"first argument", r"module",
             r"skills/tdd/scripts/veri/", r"shim")
    assert problems == []
