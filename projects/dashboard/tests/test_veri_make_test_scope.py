import os
import pathlib
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]


@pytest.mark.process("make")
def test_veri_make_test_collects_nothing_under_projects_dashboard(tmp_path):
    probe = tmp_path / "scope.mk"
    probe.write_text('_scope:\n\t@printf "%s\\n" $(PY_TESTS) $(DASH_TESTS)\n')
    env = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "TESTS")}

    run = subprocess.run(
        ["make", "--no-print-directory", "-s", "-f", "Makefile", "-f", str(probe), "_scope"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    collected = run.stdout.split()

    assert collected and (run.returncode, [p for p in collected if p.startswith("projects/dashboard")]) == (0, [])
