"""In-process cases for the `pin` phase's test ids: verify.py's `pin` phase, through build_verify_prompt.py, takes 1 to
5 test ids after the spec file (PRD 044.2, D8, SC650)."""
import importlib

from test_verify import BRANCH, answering_leaf, write_inputs

STEP = "the zorblat is frobbed ⟦criterion 7⟧"


def test_pin_phase_builds_the_pin_prompt_for_5_tracked_ids_carrying_every_id_space_separated(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    ids = []
    for k in range(1, 6):
        (tmp_path / "tests" / f"test_{k}.py").write_text("def test_case(): pass\n")
        ids.append(f"tests/test_{k}.py::test_case")
    launches = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\ncovered")
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--step", STEP, "pin", "spec.md", *ids])

    prompts = [prompt for leaf, prompt in launches if leaf == "verify-pin"]
    assert (code, len(prompts)) == (0, 1), capfdbinary.readouterr().err
    assert " ".join(ids) in prompts[0]
