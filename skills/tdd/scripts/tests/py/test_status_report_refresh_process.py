"""Process case for veri.status --report: a stale snapshot's refresh never holds a captured report."""
import contextlib
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
WAIT = 5
EOF_WAIT = 10
STUB_WAIT = 20


def release(fifo):
    """Unblock the stub: write one line into the fifo, giving up quietly when no reader is left."""
    try:
        fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
    except OSError:
        return
    with os.fdopen(fd, "w") as f:
        f.write("go\n")


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def end_stub(fifo, started):
    """End the stub report-cache.sh refresh the case started, also when it has not opened the fifo yet: release it,
    then kill it by the pid it recorded, waiting a bounded time for it to record one, and for that pid to be gone."""
    release(fifo)
    deadline = time.monotonic() + STUB_WAIT
    while not (started.is_file() and started.read_text().strip()) and time.monotonic() < deadline:
        time.sleep(0.05)
    recorded = started.read_text().strip() if started.is_file() else ""
    if not recorded:
        return
    pid = int(recorded)
    try:
        os.kill(pid, 9)
    except ProcessLookupError:
        return
    while alive(pid) and time.monotonic() < deadline:
        time.sleep(0.05)


def report_beside_a_blocked_refresh(tmp_path, hold=None):
    """status.py --report run for real beside a stub report-cache.sh refresh that blocks on a fifo; with <hold>,
    the stub opens the fifo only once <hold> exists. Returns the report's exit code, stdout and stderr."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copytree(SCRIPTS / "veri", scripts / "veri", ignore=shutil.ignore_patterns("__pycache__"))
    fifo, started = tmp_path / "gate", tmp_path / "started"
    os.mkfifo(fifo)
    stub = scripts / "report-cache.sh"
    held = 'while [ ! -e "%s" ]; do sleep 0.05; done\n' % hold if hold else ""
    stub.write_text('#!/bin/sh\necho $$ > "%s"\n%sread line < "%s"\n' % (started, held, fifo))
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
        eof = not reader.is_alive()
        deadline = time.monotonic() + WAIT
        while not (started.exists() and started.read_text().strip()) and time.monotonic() < deadline:
            time.sleep(0.05)
        blocked = started.exists()
        assert eof, "the captured report did not reach EOF while the refresh was blocked"
        assert blocked, "the stub report-cache.sh refresh was never started"
        out = chunks[0]
        err = proc.stderr.read()
        return proc.wait(timeout=WAIT), out, err
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.communicate(timeout=WAIT)
        end_stub(fifo, started)
        if hold:
            hold.touch()


@pytest.mark.process("status.py started for real beside a stub report-cache.sh that blocks on a fifo the case controls")
@pytest.mark.tree_audit("copies the veri modules into a scratch scripts directory")
def test_2750_report_with_a_stale_snapshot_ends_its_captured_stdout_while_the_refresh_is_still_running(tmp_path):
    code, out, err = report_beside_a_blocked_refresh(tmp_path)

    assert code == 0, err
    assert "Queue" in out


@pytest.mark.process("status.py started for real beside a stub report-cache.sh held back from opening its fifo until after the release")
@pytest.mark.tree_audit("copies the veri modules into a scratch scripts directory")
def test_4131_the_stub_refresh_has_ended_when_the_case_ends_also_when_it_opens_its_fifo_only_after_the_release(tmp_path):
    with contextlib.suppress(AssertionError):
        report_beside_a_blocked_refresh(tmp_path, hold=tmp_path / "open-now")
    recorded = (tmp_path / "started").read_text().strip() if (tmp_path / "started").is_file() else ""
    pid = int(recorded) if recorded else None
    try:
        assert pid is None or not alive(pid), "the stub report-cache.sh refresh %d outlived the case" % pid
    finally:
        if pid is not None:
            try:
                os.kill(pid, 9)
            except OSError:
                pass
