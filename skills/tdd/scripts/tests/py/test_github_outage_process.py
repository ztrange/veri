"""Entry-point contract of github-outage.sh: the shim, run from a linked worktree, acts on the main working tree."""
import os
import subprocess

import pytest

from conftest import SCRIPTS

URL = "https://github.com/o/r/pull/3"


def _run(cwd, *args):
    done = subprocess.run([str(SCRIPTS / "github-outage.sh"), *args], cwd=cwd, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    return done.returncode, done.stdout


@pytest.mark.process("github-outage.sh and git in a scratch repository with a linked worktree")
def test_github_outage_sh_from_a_linked_worktree_reads_and_writes_the_main_working_trees_outage_file(tmp_path):
    main, linked = tmp_path / "main", tmp_path / "linked"
    main.mkdir()
    for args in (["init", "-q"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "i"],
                 ["worktree", "add", "-q", str(linked)]):
        subprocess.run(["git", *args], cwd=main, check=True, stdin=subprocess.DEVNULL, capture_output=True)

    off = _run(linked, "status")
    not_held = _run(linked, "hold", URL)
    refused = _run(linked, "enter", "not-a-url")
    (main / ".tdd").mkdir(exist_ok=True)
    (main / ".tdd" / "github-outage").write_text("Incident\thttps://github.com/o/r/pull/1\n-- held after review --\n")
    held = _run(linked, "hold", URL)

    assert (off, not_held, refused[0], held) == ((3, "mode off\nwait none\n"), (3, ""), 2, (0, "held\n"))
    assert (main / ".tdd" / "github-outage").read_text().endswith(URL + "\n")
    assert not (linked / ".tdd" / "github-outage").exists()
