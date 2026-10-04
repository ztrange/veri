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
