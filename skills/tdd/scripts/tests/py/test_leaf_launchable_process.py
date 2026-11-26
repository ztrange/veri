"""Process-starting cases split from unit/test_leaf_launchable.py, which holds the small cases of the same module."""
import os
import subprocess

import pytest


@pytest.mark.process("leaf-launchable.sh run as a real process through a symlink to the skill directory")
def test_run_through_a_symlink_to_the_skill_directory_from_another_working_directory_answers_as_run_in_place_for_a_launching_and_a_failing_binary(
        tmp_path):
    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    skill = os.path.dirname(scripts)
    os.symlink(skill, str(tmp_path / "skill"))
    (tmp_path / "elsewhere").mkdir()
    stubs = {
        "launching": "#!/bin/sh\nprintf '%s\\n' '1.2.3 (Claude Code)'\nprintf '%s\\n' 'chatter' >&2\nexit 0\n",
        "failing": "#!/bin/sh\nprintf '%s\\n' 'Error: cannot be launched here.' >&2\nexit 1\n",
    }
    answers = {}
    for name, body in stubs.items():
        stub = tmp_path / name
        stub.write_text(body)
        stub.chmod(0o755)
        env = {key: value for key, value in os.environ.items() if key != "CLAUDECODE"}
        env["CLAUDE_BIN"] = str(stub)

        def run(command, cwd, env=env):
            done = subprocess.run([command], cwd=cwd, env=env, capture_output=True)
            return done.returncode, done.stdout, done.stderr

        in_place = run(os.path.join(scripts, "leaf-launchable.sh"), scripts)
        linked = run(str(tmp_path / "skill" / "scripts" / "leaf-launchable.sh"), str(tmp_path / "elsewhere"))
        answers[name] = (in_place[0], linked == in_place)
    assert answers == {"launching": (0, True), "failing": (2, True)}
