"""Every verify phase renders whole: exit 0, its issue spec text, no unfilled slot."""
import importlib

import pytest

SPEC_TEXT = 'slugify("Hello & World/Foo") must return "hello-world-foo".\n'


@pytest.fixture
def build_verify_prompt():
    return importlib.import_module("veri.build_verify_prompt")


def test_each_verify_phase_renders_with_exit_0_its_issue_spec_text_and_no_unfilled_slot(
        tmp_path, run_cli, build_verify_prompt, fake_processes):
    fake_processes.answers({"git ls-files": (0, "", "")})
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_TEXT)
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [ ] a step ⟦criterion 1⟧\n")
    step = ["--step", "pin the slug", "--fast-cmd", "make unit"]
    argvs = {
        "red": [*step, "red", str(spec), "tests/test_x.py", "test_x"],
        "green": [*step, "green", str(spec), "tests/test_x.py", "test_x"],
        "refactor": [*step, "--step-green", "0123abc", "refactor", str(spec), "tests/test_x.py", "0123abc"],
        "pin": [*step, "--branch-base", "0123abc", "pin", str(spec), "tests/test_x.py", "test_x"],
        "plan": ["plan", str(spec), str(ledger)],
        "rebase": ["rebase", str(spec), "0123abc", "0123abd"],
        "transform": [*step, "transform", str(spec), "rec", "0123abc"],
        "diff": [*step, "--branch-base", "0123abc", "diff", str(spec), "0123abd"],
    }

    results = {}
    for phase, argv in argvs.items():
        code, out, _ = run_cli(build_verify_prompt, argv)
        results[phase] = (code, 'slugify("Hello & World/Foo")' in out, "{{" in out)

    assert results == dict.fromkeys(argvs, (0, True, False))


def test_a_green_step_marked_with_a_repair_or_replaces_mark_carries_its_own_fragment_and_none_of_the_other_three(
        tmp_path, run_cli, build_verify_prompt):
    from pathlib import Path
    prompts = Path(build_verify_prompt.__file__).resolve().parents[1] / "prompts"
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_TEXT)
    marks = ["replaces-case", "suite-repair", "ci-repair", "fixture-repair"]
    lines = {m: [line for line in (prompts / f"_verify-green-{m}.md").read_text().splitlines()
                 if line.strip() and "{{" not in line] for m in marks}

    results = {}
    for mark in marks:
        code, out, _ = run_cli(build_verify_prompt, [
            "--step", f"pin the slug ⟦{mark}⟧", "--fast-cmd", "make unit",
            "green", str(spec), "tests/x_suite.py", "test_x"])
        rendered = out.splitlines()
        others = [line for m in marks if m != mark for line in lines[m]]
        results[mark] = (code, bool(lines[mark]) and any(line in rendered for line in lines[mark]),
                         [line for line in others if line in rendered], "{{" in out)

    assert results == dict.fromkeys(marks, (0, True, [], False))
