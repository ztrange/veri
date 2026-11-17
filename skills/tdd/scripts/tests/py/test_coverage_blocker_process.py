"""Process-starting cases split from unit/test_coverage_blocker.py, which holds the small cases of the same module."""
import json
import os
import pathlib
import subprocess

import pytest


@pytest.fixture(autouse=True)
def default_driver(monkeypatch):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)


@pytest.mark.process("coverage-blocker.sh run through a symlink to the skill directory from another working directory, with a stub gh on PATH")
def test_the_shim_run_through_a_symlink_to_the_skill_directory_from_another_cwd_prints_the_same_url_patches_the_same_body_and_exits_as_when_run_in_place(tmp_path):
    scripts = pathlib.Path(__file__).resolve().parents[2]
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(
        '#!/bin/sh\n'
        'case "$*" in\n'
        '  *PATCH*)\n'
        '    for a in "$@"; do case "$a" in *=@*) cp "${a#*=@}" "$FAKE_OUT" ;; esac; done\n'
        "    echo '{}' ;;\n"
        '  "api "*"repos/"*"/issues/60"*) cat "$FAKE_VIEW" ;;\n'
        "  \"api \"*\"repos/\"*\"/issues?\"*) echo '[]' ;;\n"
        '  "api "*"repos/"*"/issues"*) echo "https://github.com/owner/name/issues/77" ;;\n'
        'esac\n')
    gh.chmod(0o755)
    view = tmp_path / "view.json"
    view.write_text(json.dumps({"body": "## What to build\n\nExtract the parser.\n\n## Blocked by\n\nNone (can start immediately).\n"}))
    (tmp_path / "linked-skill").symlink_to(scripts.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    for cwd in (tmp_path, tmp_path / "elsewhere"):
        (cwd / ".tdd").mkdir()
        (cwd / ".tdd" / "develop-cover.out").write_text("COVERED: no\n")
        (cwd / ".tdd" / "issue-60.md").write_text("- [ ] Extract Method `parse` out of `veri/a.py:run`\n")
    env = {k: v for k, v in os.environ.items() if k != "VERI_GH_DRIVER"}
    env.update(PATH="%s:%s" % (bin_dir, os.environ["PATH"]), FAKE_VIEW=str(view))

    def run(script, cwd, edited):
        ran = subprocess.run([str(script), "60"], cwd=cwd, env=dict(env, FAKE_OUT=str(edited)),
                             stdin=subprocess.DEVNULL, capture_output=True, text=True)
        return ran.returncode, ran.stdout, edited.read_text() if edited.exists() else None

    in_place = run(scripts / "coverage-blocker.sh", tmp_path, tmp_path / "inplace-edit")
    linked = run(tmp_path / "linked-skill" / "scripts" / "coverage-blocker.sh", tmp_path / "elsewhere", tmp_path / "linked-edit")

    assert in_place[:2] == (0, "https://github.com/owner/name/issues/77\n")
    assert in_place[2] is not None and "#77" in in_place[2]
    assert linked == in_place
