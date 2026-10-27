"""In-process cases for veri/leaf.py, the one place a leaf is launched through supervise.sh."""
import importlib
import os
import subprocess

from conftest import SCRIPTS


def test_launch_runs_supervise_with_the_leaf_name_run_leaf_prompt_extra_args_pipe_and_env(monkeypatch):
    leaf = importlib.import_module("veri.leaf")
    seen = []

    def fake_run(argv, **kw):
        seen.append((argv, kw))
        return subprocess.CompletedProcess(argv, 7)

    monkeypatch.setattr(subprocess, "run", fake_run)
    env = {"PATH": "/x", "VERI_MODEL": "m"}
    ran = leaf.launch("author-skill-edit-2", "/tmp/p.md",
                      "--permission-mode", "bypassPermissions", env=env)
    assert seen == [(
        [os.path.join(str(SCRIPTS), "supervise.sh"), "author-skill-edit-2",
         os.path.join(str(SCRIPTS), "run-leaf.sh"), "/tmp/p.md",
         "--permission-mode", "bypassPermissions"],
        {"stdout": subprocess.PIPE, "env": env})]
    assert ran.returncode == 7
