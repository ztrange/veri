"""Process cases for veri/structural_predicate.py: the ones that start a real process; the small cases are in unit/test_structural_predicate.py."""
import os
import subprocess

import pytest

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "structural-predicate.sh"))


@pytest.mark.process("structural-predicate.sh started through a symlink to the skill directory, from another working directory")
def test_shim_run_through_a_symlink_and_from_another_directory_answers_relative_to_the_callers_directory(tmp_path):
    skill = os.path.dirname(os.path.dirname(SHIM))
    os.symlink(skill, str(tmp_path / "linked-skill"))
    caller = tmp_path / "caller"
    caller.mkdir()
    linked = str(tmp_path / "linked-skill" / "scripts" / "structural-predicate.sh")
    report = "Read the candidate and the files it names.\nPREDICATE: test -e marker\n"

    def run():
        return subprocess.run(
            [linked, "record"], input=report, text=True, capture_output=True, cwd=str(caller)
        )

    first = run()
    assert (first.returncode, first.stdout, first.stderr) == (0, "", "")
    assert (caller / "record").read_text() == "test -e marker\n"

    (caller / "record").unlink()
    (caller / "marker").touch()
    second = run()
    assert (second.returncode, second.stdout, second.stderr) == (1, "", "")
    assert not (caller / "record").exists()
    for directory in (skill, os.path.join(skill, "scripts")):
        assert not os.path.exists(os.path.join(directory, "record"))


@pytest.mark.process("structural-predicate.sh started for real with its stdin closed")
def test_shim_with_stdin_closed_exits_2_with_one_stderr_line_naming_the_shim_and_no_traceback(tmp_path):
    def close_stdin():
        os.close(0)

    done = subprocess.run(
        [SHIM, str(tmp_path / "predicate")],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        preexec_fn=close_stdin,
    )

    lines = done.stderr.splitlines()
    assert (done.returncode, done.stdout, len(lines)) == (2, "", 1)
    assert lines[0].startswith("structural-predicate.sh: ")
    assert "Traceback" not in done.stderr
