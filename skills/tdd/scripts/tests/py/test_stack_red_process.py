"""Process cases for stack-red.sh, the shim over veri/stack_red.py: a real git clone of a local bare origin whose default
branch is `trunk` and whose CLAUDE.md names the stack branch `stack`, and a stub gh answering the stack's workflow runs
from a file the case writes."""
import json
import os
import subprocess

import pytest

from stub_script import write_stub
from test_stack_green_process import stack_clone

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "stack-red.sh"))
GH = """here="$(dirname "$0")"
case "$*" in
  *actions/runs?branch=stack*) cat "$here/runs"; exit "$(cat "$here/rc")" ;;
esac
exit 1
"""


def runs(*found):
    return json.dumps({"total_count": len(found), "workflow_runs": [
        {"head_sha": sha, "html_url": "https://github.com/o/r/actions/runs/%d" % n, "status": status,
         "conclusion": conclusion, "created_at": "2026-11-16T10:00:%02dZ" % n, "repository": {"full_name": "o/r"},
         "head_repository": {"full_name": "o/r"}} for n, (sha, status, conclusion) in enumerate(found)]})


@pytest.mark.process("stack-red.sh run as its /bin/sh shim in a clone of a local bare origin (default branch trunk) holding a stack, with a stub gh on PATH")
@pytest.mark.parametrize("answer, rc, expected", [
    (lambda s: runs((s[3], "completed", "failure"), (s[4], "in_progress", None)), 0, (0, 3)),
    (lambda s: runs((s[3], "completed", "failure"), (s[4], "completed", "success")), 0, (3, None)),
    (lambda s: "<html>502</html>", 0, (2, None)),
    (lambda s: "", 1, (2, None)),
])
def test_stack_red_prints_a_red_latest_answer_3_when_it_is_not_and_2_without_an_answer(tmp_path, answer, rc, expected):
    work, shas = stack_clone(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(str(bin_dir / "gh"), GH)
    (bin_dir / "runs").write_text(answer(shas))
    (bin_dir / "rc").write_text(str(rc))
    env = {**os.environ, "PATH": "%s:%s" % (bin_dir, os.environ["PATH"])}

    done = subprocess.run([SHIM], cwd=str(work), env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          timeout=60)

    code, index = expected
    printed = "%s https://github.com/o/r/actions/runs/0 failure\n" % shas[index] if index is not None else ""
    assert (done.returncode, done.stdout) == (code, printed), done.stderr
    assert done.stderr.count("\n") == (0 if code == 0 else 1), done.stderr
