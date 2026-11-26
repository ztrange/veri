"""Process-starting cases split from unit/test_capture_spec.py, which holds the small cases of the same module."""
import os
import pathlib
import subprocess

import pytest

BUG_BODY = """## What happened
tick-ledger.sh ticked the same step twice.

## Expected
tick-ledger.sh ticks a step once.

## Steps to reproduce
Run tick-ledger.sh twice against the same step text.

## Environment
bash 5.2 on macOS 15.6.

## Acceptance criteria

- [ ] a step is ticked once
"""


@pytest.mark.process("capture-spec.sh run through a symlink to the skill directory from another working directory, with a stub gh on PATH")
def test_the_shim_run_through_a_symlink_to_the_skill_directory_from_another_cwd_prints_the_same_spec_and_exit_code_as_when_run_in_place(tmp_path):
    scripts = pathlib.Path(__file__).resolve().parents[2]
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (tmp_path / "body.md").write_text(BUG_BODY)
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/sh\ncase "$*" in\n  *labels*) echo bug; echo refactor ;;\n  *body*) cat "$FIXTURE" ;;\n  *) exit 1 ;;\nesac\n')
    gh.chmod(0o755)
    (tmp_path / "linked-skill").symlink_to(scripts.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    env = dict(os.environ, VERI_GH_DRIVER="auto", PATH="%s:%s" % (bin_dir, os.environ["PATH"]), FIXTURE=str(tmp_path / "body.md"))

    def run(script, cwd):
        ran = subprocess.run([str(script), "112"], cwd=cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
        return ran.returncode, ran.stdout, ran.stderr

    in_place = run(scripts / "capture-spec.sh", scripts)
    linked = run(tmp_path / "linked-skill" / "scripts" / "capture-spec.sh", tmp_path / "elsewhere")

    assert in_place[0] == 0 and "\n## Bug\n" in in_place[1]
    assert linked == in_place
