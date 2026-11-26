"""Process cases for veri/tick_issue_criterion.py: the ones that start a real process; the small cases are in unit/test_tick_issue_criterion.py."""
import os
import subprocess

import pytest

AC = "## Acceptance criteria\n\n"


@pytest.mark.process("a symlink to the skill directory, and the tick-issue-criterion.sh shim run from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_directory_ticks_and_patches_the_same_body_as_in_place(tmp_path):
    scripts = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    stub = tmp_path / "stub"
    stub.mkdir()
    (stub / "gh").write_text(
        '#!/bin/sh\n'
        'if [ "$1" = "issue" ] && [ "$2" = "view" ]; then\n'
        '  printf \'%s\' "$FAKE_BODY"\n'
        'elif [ "$1" = "api" ]; then\n'
        '  for a in "$@"; do case "$a" in body=@*) cp "${a#body=@}" "$FAKE_OUT" ;; esac; done\n'
        'fi\n')
    (stub / "gh").chmod(0o755)
    (tmp_path / "linked-skill").symlink_to(os.path.dirname(scripts))
    (tmp_path / "elsewhere").mkdir()
    body = AC + "- [ ] alpha criterion\n- [ ] beta criterion"

    def run(script, cwd, out):
        env = dict(os.environ, VERI_GH_DRIVER="auto", FAKE_BODY=body, FAKE_OUT=str(out),
                   PATH=str(stub) + os.pathsep + os.environ["PATH"])
        done = subprocess.run([script, "7", "alpha"], cwd=cwd, env=env, capture_output=True, text=True)
        return done.returncode, done.stdout, done.stderr, out.read_text() if out.exists() else None

    in_place = run(os.path.join(scripts, "tick-issue-criterion.sh"), tmp_path, tmp_path / "in-place-edit")
    linked = run(str(tmp_path / "linked-skill" / "scripts" / "tick-issue-criterion.sh"),
                 tmp_path / "elsewhere", tmp_path / "linked-edit")

    assert in_place == (0, "", "", AC + "- [x] alpha criterion\n- [ ] beta criterion")
    assert linked == in_place
