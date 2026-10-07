"""In-process cases for veri/build_verify_prompt.py, the module build-verify-prompt.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = b"usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]\n"


@pytest.fixture
def build_verify_prompt():
    return importlib.import_module("veri.build_verify_prompt")


def test_main_refuses_a_missing_argument_an_option_with_no_value_an_unknown_phase_and_a_green_or_diff_call_without_fast_cmd_with_exit_2_and_its_message_then_the_usage_line(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    results = {}
    for argv in ([], ["red", "", "t"], ["--fast-cmd"], ["bogus", str(spec), "t"],
                 ["green", str(spec), "t", "x"],
                 ["--step", "s", "diff", str(spec), "0123abc", "0123abc"]):
        code = build_verify_prompt.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("red", "", "t"): (2, b"", USAGE),
        ("--fast-cmd",): (2, b"", b"build-verify-prompt: --fast-cmd needs a value\n" + USAGE),
        ("bogus", str(spec), "t"): (2, b"", b"build-verify-prompt: unknown phase 'bogus' "
                                    b"(want red|green|refactor|pin|plan|rebase|transform|diff)\n" + USAGE),
        ("green", str(spec), "t", "x"): (
            2, b"", b"build-verify-prompt: green needs --fast-cmd '<fast-tier test command>'\n" + USAGE),
        ("--step", "s", "diff", str(spec), "0123abc", "0123abc"): (
            2, b"", b"build-verify-prompt: diff needs --fast-cmd '<fast-tier test command>'\n" + USAGE),
    }


def test_main_parses_only_leading_options_in_either_order_the_last_winning_and_refuses_an_empty_option_too_many_arguments_and_refactor_without_fast_cmd_in_the_check_order(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    s = str(spec)

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    def refusal(message):
        return (2, b"", message + b"\n" + USAGE)

    refused = {tuple(argv): run(argv) for argv in (
        ["--step"],
        ["--step", "", "red", s, "t"],
        ["--fast-cmd", "", "green", s, "t"],
        ["--fast-cmd", "m", "--step", "", "green", s, "t"],
        ["--step", "", "bogus", "a", "b", "c", "d"],
        ["bogus", "a", "b", "c", "d"],
        ["refactor", s, "t", "0123abc", "x"],
        ["red", s, "t", "--step", "s"],
        ["refactor", s, "t", "0123abc"],
    )}
    assert refused == {
        ("--step",): refusal(b"build-verify-prompt: --step needs a value"),
        ("--step", "", "red", s, "t"): refusal(b"build-verify-prompt: --step needs a value"),
        ("--fast-cmd", "", "green", s, "t"): refusal(b"build-verify-prompt: --fast-cmd needs a value"),
        ("--fast-cmd", "m", "--step", "", "green", s, "t"): refusal(b"build-verify-prompt: --step needs a value"),
        ("--step", "", "bogus", "a", "b", "c", "d"): refusal(b"build-verify-prompt: --step needs a value"),
        ("bogus", "a", "b", "c", "d"): refusal(b"build-verify-prompt: too many arguments"),
        ("refactor", s, "t", "0123abc", "x"): refusal(b"build-verify-prompt: too many arguments"),
        ("red", s, "t", "--step", "s"): refusal(b"build-verify-prompt: too many arguments"),
        ("refactor", s, "t", "0123abc"): refusal(
            b"build-verify-prompt: refactor needs --fast-cmd '<fast-tier test command>'"),
    }

    step_first = run(["--step", "s", "--fast-cmd", "m", "green", s, "t"])
    fast_first = run(["--fast-cmd", "m", "--step", "s", "green", s, "t"])
    repeated = run(["--fast-cmd", "a", "--step", "r", "--fast-cmd", "m", "--step", "s", "green", s, "t"])
    assert (step_first[0], step_first[2]) == (0, b"")
    assert fast_first == step_first
    assert repeated == step_first
    assert build_verify_prompt.PHASES == (
        "red", "green", "refactor", "pin", "plan", "rebase", "transform", "diff")
