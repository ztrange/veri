"""In-process cases for veri/build_develop_prompt.py, the module build-develop-prompt.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

PHASES = b"red|green|refactor|cover|transform|diff|structural|predicate|revise|reconcile|exhausted|over-budget|rebase"
USAGE = b"build-develop-prompt.sh: usage: " + PHASES + b" <issue-spec-file> <step-text> <test-cmd> ...\n"


@pytest.fixture
def build_develop_prompt():
    return importlib.import_module("veri.build_develop_prompt")


def test_main_refuses_no_argument_an_unknown_phase_a_short_count_an_unknown_revise_phase_and_a_missing_fast_cmd_with_exit_2_and_its_message_then_the_usage_line(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    s, r = str(spec), str(reason)
    results = {}
    for argv in ([], ["bogus", s, "s", "c"], ["green", s, "s", "c"],
                 ["revise", "bogus", s, "s", "c", r], ["diff", s, "s", "c"],
                 ["revise", "diff", s, "s", "c", r]):
        code = build_develop_prompt.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("bogus", s, "s", "c"): (
            2, b"", b"build-develop-prompt.sh: unknown phase 'bogus' (want " + PHASES + b")\n" + USAGE),
        ("green", s, "s", "c"): (2, b"", b"build-develop-prompt: green needs 7 arguments, got 4\n" + USAGE),
        ("revise", "bogus", s, "s", "c", r): (
            2, b"", b"build-develop-prompt.sh: unknown phase to revise 'bogus' (want red|green|refactor|diff)\n"
            + USAGE),
        ("diff", s, "s", "c"): (2, b"", b"build-develop-prompt: diff needs 5 arguments, got 4\n" + USAGE),
        ("revise", "diff", s, "s", "c", r): (2, b"", b"build-develop-prompt: missing <fast-cmd>\n" + USAGE),
    }
