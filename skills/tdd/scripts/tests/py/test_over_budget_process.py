"""Process-starting cases split from unit/test_over_budget.py, which holds the small cases of the same module."""
import importlib

import pytest


@pytest.fixture
def over_budget():
    return importlib.import_module("veri.over_budget")


def _unset_tunables(monkeypatch):
    for name in ("VERI_UNIT_BUDGET", "VERI_TIME_WARN_RATIO"):
        monkeypatch.delenv(name, raising=False)


def test_cli_ends_an_over_budget_run_on_its_leafs_own_verdict_with_no_retry_and_no_bail(
        monkeypatch, tmp_path, run_cli, over_budget, fake_processes, events):
    import json

    verify = importlib.import_module("veri.verify")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(
        json.dumps({"ts": 1, "issue": "342", "actor": "", "phase": "", "step": "", "event": "test-run",
                    "attempt": "1", "skill_commit": "", "tier": "unit", "suites": "make unit",
                    "seconds": seconds}) + "\n" for seconds in ["1"] * 10 + ["40"]))
    (tmp_path / "spec.md").write_text("slugify must lowercase the title and join words with hyphens.\n")
    for name in ("VERI_MODEL", "VERI_MODEL_VERIFIER", "VERI_MODEL_DEVELOPER", "VERIFY_LEAF_ARGS"):
        monkeypatch.delenv(name, raising=False)
    _unset_tunables(monkeypatch)

    def answer(line, **_):
        if line.startswith("supervise.sh "):
            return 0, b"VERDICT: PASS\nREASON: the new case fails for the reason the step names.\n", b""
        return 0, b"", b""

    calls = fake_processes(answer)
    usual = "1.0"
    assert run_cli(over_budget, ["unit", "40", usual], cwd=tmp_path)[0] == 0
    before = len(events.records(tmp_path))

    env = {"HOME": str(tmp_path), "VERI_NO_VERDICT_RETRIES": "0"}
    code, out, _ = run_cli(verify, ["--branch-base", "0000000", "red", str(tmp_path / "spec.md"), "tests/test_slugify.py", "test_lowercases"],
                           env=env, cwd=tmp_path)
    after = events.records(tmp_path)[before:]

    assert (code, "the reason the step names" in out) == (0, True)
    assert [(e["event"], e.get("verdict")) for e in after if e["event"] in ("verdict", "relaunch", "bail")] == [
        ("verdict", "PASS")]
    assert len([line for line in calls if line.startswith("supervise.sh ")]) == 1


@pytest.mark.process("over-budget.sh's shim run through a symlink to the skill directory from another working directory")
def test_shim_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_in_place(tmp_path):
    import os
    import pathlib
    import subprocess

    skill = pathlib.Path(__file__).resolve().parents[3]
    (tmp_path / "link").mkdir()
    (tmp_path / "link" / "skill").symlink_to(skill, target_is_directory=True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    env = {k: v for k, v in os.environ.items() if k not in ("VERI_UNIT_BUDGET", "VERI_TIME_WARN_RATIO")}

    def answer(script, cwd, argv):
        ran = subprocess.run([str(script), *argv], cwd=cwd, env=env, capture_output=True, text=True)
        return ran.returncode, ran.stdout

    for argv, want in ((["unit", "12", "100"], 0), (["unit", "4", "100"], 1)):
        in_place = answer(skill / "scripts" / "over-budget.sh", None, argv)
        via_link = answer(tmp_path / "link" / "skill" / "scripts" / "over-budget.sh", elsewhere, argv)
        assert (argv, via_link) == (argv, in_place)
        assert (argv, via_link[0], ("⏱" in via_link[1]) if want == 0 else via_link[1]) == (
            argv, want, True if want == 0 else "")
