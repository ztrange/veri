"""In-process cases for veri/classify_bail.py, the module classify-bail.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

USAGE = "usage: classify-bail.sh <cause>\n"


@pytest.fixture
def classify_bail():
    return importlib.import_module("veri.classify_bail")


def test_main_prints_the_category_of_a_known_cause_and_refuses_an_unknown_or_missing_one_with_2(capsys, classify_bail):
    results = {}
    for name, argv in {"ci-timeout": ["ci-timeout"], "ci-red": ["ci-red"], "bogus": ["bogus"], "none": []}.items():
        code = classify_bail.main(argv)
        results[name] = (code, *capsys.readouterr())

    assert results == {
        "ci-timeout": (0, "system\n", ""),
        "ci-red": (0, "process\n", ""),
        "bogus": (2, "", "classify-bail: unknown cause: bogus\n" + USAGE),
        "none": (2, "", "classify-bail: unknown cause: \n" + USAGE),
    }


SYSTEM_CAUSES = ("killed-stuck", "no-verdict", "reconcile-failed", "ci-timeout", "ci-conflict")
PROCESS_CAUSES = ("revise-exhausted", "untestable-criterion", "step-too-big", "rebase-unresolved",
                  "uncovered", "ci-red", "suite-red")


def test_main_classifies_every_known_cause_as_system_or_process_with_0(capsys, classify_bail):
    results = {}
    for cause in SYSTEM_CAUSES + PROCESS_CAUSES:
        code = classify_bail.main([cause])
        results[cause] = (code, capsys.readouterr().out.split("\n")[0])

    assert results == {
        **{cause: (0, "system") for cause in SYSTEM_CAUSES},
        **{cause: (0, "process") for cause in PROCESS_CAUSES},
    }


def test_main_refuses_stop_and_budget_words_with_2_and_skill_md_calls_ci_conflict_a_system_failure(capsys, classify_bail):
    results = {}
    for cause in ("stopped", "stop", "at-ledger", "at-leaf", "now", "step-over-budget", "over-budget", "wat"):
        code = classify_bail.main([cause])
        results[cause] = (code, capsys.readouterr().out)

    bailing = (SCRIPTS.parent / "SKILL.md").read_text().split("\n## Bailing", 1)[1].split("\n## ", 1)[0]
    entry = bailing.split("\n- `ci-conflict` —", 1)[1].split("\n- ", 1)[0].split("\n\n", 1)[0]

    assert results == {cause: (2, "") for cause in results}
    assert "**system**" in entry


def test_main_keeps_the_bash_quirks_exact_case_first_argument_only_no_option_marker_and_empty_is_missing(capsys, classify_bail):
    results = {}
    for name, argv in {"upper": ["KILLED-STUCK"], "leading space": [" killed-stuck"],
                       "extra args": ["killed-stuck", "extra", "args"], "dashdash": ["--", "killed-stuck"],
                       "empty": [""], "none": []}.items():
        code = classify_bail.main(argv)
        results[name] = (code, *capsys.readouterr())

    assert results == {
        "upper": (2, "", "classify-bail: unknown cause: KILLED-STUCK\n" + USAGE),
        "leading space": (2, "", "classify-bail: unknown cause:  killed-stuck\n" + USAGE),
        "extra args": (0, "system\n", ""),
        "dashdash": (2, "", "classify-bail: unknown cause: --\n" + USAGE),
        "empty": results["none"],
        "none": (2, "", "classify-bail: unknown cause: \n" + USAGE),
    }
