"""Process cases for veri/build_develop_prompt.py, the module build-develop-prompt.sh is a shim over."""
import pytest

from conftest import SCRIPTS


def _spec(tmp_path, extra=""):
    spec = tmp_path / "spec.md"
    spec.write_text('zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" — see {ref}\\n done.\n' + extra)
    return str(spec)


@pytest.mark.process("build-develop-prompt.sh run through a symlink to the scripts directory from another working directory")
def test_cli_run_through_a_symlink_to_the_scripts_directory_answers_red_green_and_diff_as_in_place_but_names_the_symlink_in_the_timed_test_run_path(
        tmp_path):
    import subprocess

    spec = _spec(tmp_path)
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    diff_step = "the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧"
    test_cmd = 'make test ZORBLAT=1 -- --only "frob & nitz/quux"'
    linked = tmp_path / "linked"
    linked.mkdir()
    (linked / "veri-scripts").symlink_to(SCRIPTS)
    calls = {
        "red": ["red", spec, step, test_cmd],
        "green": ["green", spec, step, test_cmd, "tests/zorblat/test_frob & nitz.sh",
                  "qwixtle seeds a newline-terminated block", "make unit"],
        "diff": ["diff", spec, diff_step, test_cmd, 'make unit ZORBLAT=fast -- --only "frob & nitz/quux"'],
    }
    problems = []
    for label, argv in calls.items():
        want = subprocess.run([str(SCRIPTS / "build-develop-prompt.sh"), *argv], capture_output=True, text=True,
                              cwd=str(tmp_path))
        got = subprocess.run(["./veri-scripts/build-develop-prompt.sh", *argv], capture_output=True, text=True,
                             cwd=str(linked))
        in_place = f"{SCRIPTS}/timed-test-run.sh"
        if in_place not in want.stdout:
            problems.append(f"{label} in place names no {in_place}")
        expected = want.stdout.replace(in_place, f"{linked}/veri-scripts/timed-test-run.sh")
        expected = expected.replace(f"{tmp_path}/.tdd/", f"{linked}/.tdd/")
        if label == "red":
            if f"`{tmp_path}/.tdd/red-prediction.md`" not in want.stdout:
                problems.append(f"red in place names no {tmp_path}/.tdd/red-prediction.md")
            if f"`{linked}/.tdd/red-prediction.md`" not in got.stdout:
                problems.append(f"red through the link names no {linked}/.tdd/red-prediction.md")
        if (got.returncode, got.stdout, got.stderr) != (want.returncode, expected, want.stderr):
            problems.append(f"{label} differs through the link")

    assert problems == []
