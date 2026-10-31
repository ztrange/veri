"""In-process cases for veri/classify_bail.py, the module classify-bail.sh is a shim over."""
import importlib
import io
import os
import sys

import pytest

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


def test_main_classifies_step_add_refused_as_system_with_0_1379(capsys, classify_bail):
    code = classify_bail.main(["step-add-refused"])

    assert (code, *capsys.readouterr()) == (0, "system\n", "")


def test_main_classifies_needs_user_as_process_with_0_1866(capsys, classify_bail):
    code = classify_bail.main(["needs-user"])

    assert (code, *capsys.readouterr()) == (0, "process\n", "")


def test_main_refuses_stop_and_budget_words_with_2(capsys, classify_bail):
    results = {}
    for cause in ("stopped", "stop", "at-ledger", "at-leaf", "now", "step-over-budget", "over-budget", "wat"):
        code = classify_bail.main([cause])
        results[cause] = (code, capsys.readouterr().out)

    assert results == {cause: (2, "") for cause in results}


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


def test_main_echoes_an_unknown_cause_back_byte_for_byte_on_stderr_newline_and_non_utf8_byte_kept(monkeypatch, capsys, classify_bail):
    results = {}
    for name, cause in {"newline": b"line one\nline two", "0xff": b"bad\xffbyte"}.items():
        stderr = io.BytesIO()
        monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(stderr, encoding="utf-8", errors="backslashreplace",
                                                            write_through=True))
        code = classify_bail.main([os.fsdecode(cause)])
        sys.stderr.flush()
        results[name] = (code, capsys.readouterr().out, stderr.getvalue())

    assert results == {
        "newline": (2, "", b"classify-bail: unknown cause: line one\nline two\n" + USAGE.encode()),
        "0xff": (2, "", b"classify-bail: unknown cause: bad\xffbyte\n" + USAGE.encode()),
    }


def test_main_raises_rather_than_returning_0_when_stdout_is_closed(monkeypatch, classify_bail):
    monkeypatch.setattr(sys, "stdout", None)

    with pytest.raises(Exception):
        classify_bail.main(["killed-stuck"])


def test_main_classifies_rebased_tip_red_as_a_process_failure_with_0(capsys, classify_bail):
    code = classify_bail.main(["rebased-tip-red"])

    assert (code, *capsys.readouterr()) == (0, "process\n", "")


def test_main_classifies_unreplaced_cases_as_a_process_failure_with_0_1521(capsys, classify_bail):
    code = classify_bail.main(["unreplaced-cases"])

    assert (code, *capsys.readouterr()) == (0, "process\n", "")


def test_main_classifies_report_missing_as_a_system_failure_with_0_1300(capsys, classify_bail):
    code = classify_bail.main(["report-missing"])

    assert (code, *capsys.readouterr()) == (0, "system\n", "")


def test_main_classifies_replaces_report_failed_as_a_system_failure_with_0_1625(capsys, classify_bail):
    code = classify_bail.main(["replaces-report-failed"])

    assert (code, *capsys.readouterr()) == (0, "system\n", "")


def test_main_classifies_step_added_off_route_as_a_process_failure_with_0_2130(capsys, classify_bail):
    code = classify_bail.main(["step-added-off-route"])

    assert (code, *capsys.readouterr()) == (0, "process\n", "")


def test_main_classifies_fixture_owed_as_a_process_failure_with_0_2172(capsys, classify_bail):
    code = classify_bail.main(["fixture-owed"])

    assert (code, *capsys.readouterr()) == (0, "process\n", "")


def test_main_classifies_criterion_unreadable_as_system_with_0_2222(capsys, classify_bail):
    code = classify_bail.main(["criterion-unreadable"])

    assert (code, *capsys.readouterr()) == (0, "system\n", "")


def test_main_refuses_red_baseline_with_2_and_prints_nothing_to_stdout_2205(capsys, classify_bail):
    code = classify_bail.main(["red-baseline"])

    assert (code, capsys.readouterr().out) == (2, "")


def test_main_classifies_setup_failed_as_a_system_failure_with_0_2231(capsys, classify_bail):
    code = classify_bail.main(["setup-failed"])

    assert (code, *capsys.readouterr()) == (0, "system\n", "")


def test_main_classifies_killed_external_as_a_system_failure_on_its_own_line_with_0_2427(capsys, classify_bail):
    code = classify_bail.main(["killed-external"])

    assert (code, *capsys.readouterr()) == (0, "system\n", "")


def test_main_classifies_preflight_refused_as_system_with_0_2481(capsys, classify_bail):
    code = classify_bail.main(["preflight-refused"])

    assert (code, *capsys.readouterr()) == (0, "system\n", "")


def test_main_classifies_missing_reroutes_exhausted_as_a_process_failure_with_0_2573(capsys, classify_bail):
    code = classify_bail.main(["missing-reroutes-exhausted"])

    assert (code, *capsys.readouterr()) == (0, "process\n", "")


def test_main_classifies_pr_ready_failed_as_a_system_failure_with_0_2581(capsys, classify_bail):
    code = classify_bail.main(["pr-ready-failed"])

    assert (code, *capsys.readouterr()) == (0, "system\n", "")


def test_main_classifies_revise_impossible_as_a_process_failure_with_0_2617(capsys, classify_bail):
    code = classify_bail.main(["revise-impossible"])

    assert (code, *capsys.readouterr()) == (0, "process\n", "")
