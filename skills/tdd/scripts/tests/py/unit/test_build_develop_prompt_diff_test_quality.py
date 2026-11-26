"""A `⟦test-quality⟧` step's develop-diff and revise-diff prompts carry the test-quality fragment, no other step's do (#4120)."""
import importlib

import pytest

from conftest import SCRIPTS

FRAGMENT = (SCRIPTS / "prompts" / "_develop-diff-test-quality.md").read_bytes().rstrip(b"\n")
MARKED = "fix tests/test_a.py::test_b, weak-assertion ⟦test-quality⟧ ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧"
PLAIN = "drop the dead helper ⟦diff-checked⟧ ⟦criterion 2⟧"


@pytest.fixture
def bdp():
    return importlib.import_module("veri.build_develop_prompt")


def render(bdp, tmp_path, argv):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\nthe issue body\n")
    parsed = bdp.arguments([str(spec) if arg == "<spec>" else arg for arg in argv])
    step = parsed.args[1]
    return bdp.render(parsed, bdp.fragments(parsed.phase, parsed.revised_phase, step, False))


def test_the_diff_prompt_carries_the_fragment_for_a_test_quality_step_only(bdp, tmp_path, monkeypatch):
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"the flip stayed green\n")
    monkeypatch.setenv("VERI_ISSUE", "7")

    carried = [FRAGMENT in render(bdp, tmp_path, argv) for argv in (
        ["diff", "<spec>", MARKED, "make test", "make unit"],
        ["diff", "<spec>", PLAIN, "make test", "make unit"],
        ["revise", "diff", "<spec>", MARKED, "make test", str(reason), "make unit"],
        ["revise", "diff", "<spec>", PLAIN, "make test", str(reason), "make unit"],
    )]

    assert carried == [True, False, True, False]
