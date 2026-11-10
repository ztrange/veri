"""Process case for veri.status --report: a stale snapshot's refresh never holds a captured report."""
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
WAIT = 10
EOF_WAIT = 20


def release(fifo):
    """Unblock the stub: write one line into the fifo, giving up quietly when no reader is left."""
    try:
        fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
    except OSError:
        return
    with os.fdopen(fd, "w") as f:
        f.write("go\n")


@pytest.mark.process("status.py started for real beside a stub report-cache.sh that blocks on a fifo the case controls")
@pytest.mark.tree_audit("copies the veri modules into a scratch scripts directory")
def test_2750_report_with_a_stale_snapshot_ends_its_captured_stdout_while_the_refresh_is_still_running(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copytree(SCRIPTS / "veri", scripts / "veri", ignore=shutil.ignore_patterns("__pycache__"))
    fifo, started = tmp_path / "gate", tmp_path / "started"
    os.mkfifo(fifo)
    stub = scripts / "report-cache.sh"
    stub.write_text('#!/bin/sh\necho started > "%s"\nread line < "%s"\n' % (started, fifo))
    stub.chmod(0o755)
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / ".tdd" / "report-cache.json").write_text('{"cache_format": 2, "fetched_at": "2000-01-01T00:00:00Z", "issues": []}')
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    proc = subprocess.Popen([sys.executable, str(scripts / "veri" / "status.py"), "--report"], cwd=repo,
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        chunks = []
        reader = threading.Thread(target=lambda: chunks.append(proc.stdout.read()), daemon=True)
        reader.start()
        reader.join(EOF_WAIT)
        ended = not reader.is_alive()
        deadline = time.monotonic() + WAIT
        while not started.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        blocked = started.exists()
        assert ended, "the captured report did not reach EOF while the refresh was blocked"
        assert blocked, "the stub report-cache.sh refresh was never started"
        out = chunks[0]
        err = proc.stderr.read()
        assert proc.wait(timeout=WAIT) == 0, err
        assert "Queue" in out
    finally:
        release(fifo)
        if proc.poll() is None:
            proc.communicate(timeout=WAIT)
