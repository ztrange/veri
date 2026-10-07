"""In-process cases for veri/red_divergence.py, the module red-divergence.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def red_divergence():
    return importlib.import_module("veri.red_divergence")


def run(monkeypatch, capsys, red_divergence, report, argv):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(report.encode()), newline="\n"))
    code = red_divergence.main(argv)
    return (code, *capsys.readouterr())


def test_main_reads_its_report_through_report_read_and_returns_each_exit_code_inside_0_to_3_with_its_stdout_and_stderr_ignoring_arguments(monkeypatch, capsys, red_divergence):
    diverged = (
        "PREDICTED_FAILURE: slugify: command not found\n"
        "FAIL_OUTPUT: FAIL - slugify lowercases the title (want exit 0, got 127)\n"
        "PREDICTION: DIVERGED\n"
        "PREDICTION_NOTE: the suite died on a missing helper before it reached the assertion"
    )
    matched = "FAIL_OUTPUT: FAIL - slugify lowercases the title\nPREDICTION: MATCHED"
    results = {
        "diverged": run(monkeypatch, capsys, red_divergence, diverged, []),
        "matched": run(monkeypatch, capsys, red_divergence, matched, []),
        "matched --bogus": run(monkeypatch, capsys, red_divergence, matched, ["--bogus"]),
        "no PREDICTION": run(monkeypatch, capsys, red_divergence, "FAIL_OUTPUT: FAIL - slugify lowercases the title\n", []),
    }

    assert results == {
        "diverged": (
            0,
            "The red leaf's prediction diverged from the failure it saw, so the test is the suspect.\n"
            "\n"
            "PREDICTED_FAILURE: slugify: command not found\n"
            "FAIL_OUTPUT: FAIL - slugify lowercases the title (want exit 0, got 127)\n"
            "PREDICTION_NOTE: the suite died on a missing helper before it reached the assertion\n",
            "",
        ),
        "matched": (3, "", ""),
        "matched --bogus": (3, "", ""),
        "no PREDICTION": (2, "", ""),
    }
    assert all(code in range(4) for code, _, _ in results.values())


def test_main_prints_an_absent_key_as_its_label_and_a_space_prints_dollar_backtick_and_backslash_verbatim_and_lets_the_last_occurrence_of_a_key_win(monkeypatch, capsys, red_divergence):
    report = (
        "PREDICTION: MATCHED\n"
        "FAIL_OUTPUT: an earlier value\n"
        "FAIL_OUTPUT: $x `id` C:\\path\\n\n"
        "PREDICTION_NOTE: $HOME and \\$x\n"
        "PREDICTION: DIVERGED"
    )

    assert run(monkeypatch, capsys, red_divergence, report, []) == (
        0,
        "The red leaf's prediction diverged from the failure it saw, so the test is the suspect.\n"
        "\n"
        "PREDICTED_FAILURE: \n"
        "FAIL_OUTPUT: $x `id` C:\\path\\n\n"
        "PREDICTION_NOTE: $HOME and \\$x\n",
        "",
    )


def test_main_strips_exactly_one_trailing_comma_semicolon_colon_or_period_from_the_verdict_word_and_no_em_dash_answering_2_silently_otherwise(monkeypatch, capsys, red_divergence):
    values = "PREDICTED_FAILURE: p\nFAIL_OUTPUT: f\nPREDICTION_NOTE: n\n"
    reason = (
        "The red leaf's prediction diverged from the failure it saw, so the test is the suspect.\n"
        "\n"
        "PREDICTED_FAILURE: p\n"
        "FAIL_OUTPUT: f\n"
        "PREDICTION_NOTE: n\n"
    )
    words = ["DIVERGED,", "DIVERGED;", "DIVERGED:", "DIVERGED.", "MATCHED.", "DIVERGED..", "MATCHED,;", "DIVERGED—"]
    results = {word: run(monkeypatch, capsys, red_divergence, values + "PREDICTION: " + word, []) for word in words}

    assert results == {
        "DIVERGED,": (0, reason, ""),
        "DIVERGED;": (0, reason, ""),
        "DIVERGED:": (0, reason, ""),
        "DIVERGED.": (0, reason, ""),
        "MATCHED.": (3, "", ""),
        "DIVERGED..": (2, "", ""),
        "MATCHED,;": (2, "", ""),
        "DIVERGED—": (2, "", ""),
    }


def test_main_cuts_the_verdict_word_at_the_first_space_only_matches_it_case_sensitively_keeps_a_carriage_return_and_answers_2_silently_otherwise(monkeypatch, capsys, red_divergence):
    reports = {
        "trailing clause": "FAIL_OUTPUT: f\nPREDICTION: MATCHED because the helper is missing",
        "tab": "FAIL_OUTPUT: f\nPREDICTION: MATCHED\tyes",
        "two spaces": "FAIL_OUTPUT: f\nPREDICTION:  MATCHED",
        "lowercase": "FAIL_OUTPUT: f\nPREDICTION: diverged",
        "capitalised": "FAIL_OUTPUT: f\nPREDICTION: Matched",
        "carriage return": "FAIL_OUTPUT: f\nPREDICTION: MATCHED\r\n",
    }
    results = {name: run(monkeypatch, capsys, red_divergence, report, []) for name, report in reports.items()}

    assert results == {
        "trailing clause": (3, "", ""),
        "tab": (2, "", ""),
        "two spaces": (2, "", ""),
        "lowercase": (2, "", ""),
        "capitalised": (2, "", ""),
        "carriage return": (2, "", ""),
    }


def test_main_reads_stdin_and_writes_stdout_as_bytes_passing_a_non_utf8_byte_in_fail_output_through_unchanged(monkeypatch, capsysbinary, red_divergence):
    report = b"PREDICTED_FAILURE: p\nFAIL_OUTPUT: f\xff\nPREDICTION_NOTE: n\nPREDICTION: DIVERGED"
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(report), newline="\n"))
    code = red_divergence.main([])

    assert (code, *capsysbinary.readouterr()) == (
        0,
        b"The red leaf's prediction diverged from the failure it saw, so the test is the suspect.\n"
        b"\n"
        b"PREDICTED_FAILURE: p\n"
        b"FAIL_OUTPUT: f\xff\n"
        b"PREDICTION_NOTE: n\n",
        b"",
    )
