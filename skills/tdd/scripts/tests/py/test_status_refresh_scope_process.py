"""Process case for veri.status --report: only a refresh of its own sibling report-cache.sh counts as already running."""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
WAIT = 8


@pytest.mark.process("status.py started for real, with the system pgrep first on its PATH, beside a stub report-cache.sh, while an unrelated report-cache.sh refresh process the case starts is alive")
@pytest.mark.tree_audit("copies the veri modules into a scratch scripts directory")
def test_3521_report_with_a_stale_snapshot_launches_its_own_refresh_while_an_unrelated_refresh_is_alive(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copytree(SCRIPTS / "veri", scripts / "veri", ignore=shutil.ignore_patterns("__pycache__"))
    started = tmp_path / "started"
    stub = scripts / "report-cache.sh"
    stub.write_text('#!/bin/sh\necho started > "%s"\n' % started)
    stub.chmod(0o755)
    other = tmp_path / "elsewhere"
    other.mkdir()
    unrelated = other / "report-cache.sh"
    unrelated.write_text("#!/bin/sh\nread line\n")
    unrelated.chmod(0o755)
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / ".tdd" / "report-cache.json").write_text('{"cache_format": 2, "fetched_at": "2000-01-01T00:00:00Z", "issues": []}')
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "pgrep").symlink_to(shutil.which("pgrep", path="/usr/bin:/bin"))
    env = dict(os.environ, PATH="%s:%s" % (tools, os.environ["PATH"]))
    holder = subprocess.Popen([str(unrelated), "refresh"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        subprocess.run([sys.executable, str(scripts / "veri" / "status.py"), "--report"], cwd=repo,
                       stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=WAIT, env=env)
        deadline = time.monotonic() + WAIT
        while not started.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert started.exists(), "the stale report did not launch its own refresh while an unrelated refresh was alive"
    finally:
        holder.kill()
        holder.wait()


@pytest.mark.process("status.py started for real, with the system pgrep first on its PATH, beside a stub report-cache.sh, while an unrelated <tmp>/other/scripts/report-cache.sh refresh process the case starts is alive")
@pytest.mark.tree_audit("copies the veri modules into a scratch scripts directory")
def test_3521_report_launches_its_own_refresh_while_an_unrelated_refresh_in_another_scripts_directory_is_alive(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copytree(SCRIPTS / "veri", scripts / "veri", ignore=shutil.ignore_patterns("__pycache__"))
    started = tmp_path / "started"
    stub = scripts / "report-cache.sh"
    stub.write_text('#!/bin/sh\necho started > "%s"\n' % started)
    stub.chmod(0o755)
    other = tmp_path / "other" / "scripts"
    other.mkdir(parents=True)
    unrelated = other / "report-cache.sh"
    unrelated.write_text("#!/bin/sh\nread line\n")
    unrelated.chmod(0o755)
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / ".tdd" / "report-cache.json").write_text('{"cache_format": 2, "fetched_at": "2000-01-01T00:00:00Z", "issues": []}')
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "pgrep").symlink_to(shutil.which("pgrep", path="/usr/bin:/bin"))
    env = dict(os.environ, PATH="%s:%s" % (tools, os.environ["PATH"]))
    holder = subprocess.Popen([str(unrelated), "refresh"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        subprocess.run([sys.executable, str(scripts / "veri" / "status.py"), "--report"], cwd=repo,
                       stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=WAIT, env=env)
        deadline = time.monotonic() + WAIT
        while not started.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert started.exists(), "the stale report did not launch its own refresh while an unrelated refresh in another scripts directory was alive"
    finally:
        holder.kill()
        holder.wait()
