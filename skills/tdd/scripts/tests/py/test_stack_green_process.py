"""Process cases for stack-green.sh, the shim over veri/stack_green.py: a real git clone of a local bare origin whose
default branch is `trunk`, with a stack of commits whose subjects name issues, and a stub gh answering each sha's
check-run pages from files the case writes."""
import json
import os
import subprocess

import pytest

from repo_builder import git
from stub_script import write_stub

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "stack-green.sh"))
GH = """here="$(dirname "$0")"
case "$*" in
  *check-runs*)
    key="$(printf '%s' "$*" | sed -n 's#.*commits/\\([0-9a-f]*\\)/check-runs.*page=\\([0-9]*\\).*#\\1-\\2#p')"
    if [ -f "$here/runs-$key" ]; then cat "$here/runs-$key"; exit "$(cat "$here/rc-$key" 2>/dev/null || echo 0)"; fi
    echo '{"total_count": 0, "check_runs": []}'; exit 0 ;;
esac
exit 1
"""
SUBJECTS = ("feat: a (#11)", "fix: b (#12)", "docs: b's README entry (#12)", "feat: a again (#11)", "test: c (#13)")


def stack_clone(tmp_path):
    """A clone of a bare origin whose default branch is trunk, its CLAUDE.md naming the stack branch `stack`, which
    holds SUBJECTS' commits on top of trunk; their shas, oldest first. The issue ends are the last two."""
    origin, seed, work = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "trunk", str(origin)], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "init", "-q", "-b", "trunk", str(seed)], cwd=str(tmp_path), check=True)
    (seed / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    git(seed, "add", "CLAUDE.md")
    git(seed, "commit", "-q", "-m", "docs: name the stack (#10)")
    git(seed, "remote", "add", "origin", str(origin))
    git(seed, "push", "-q", "origin", "trunk")
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], cwd=str(tmp_path), check=True)
    git(work, "checkout", "-q", "-b", "stack")
    shas = []
    for n, subject in enumerate(SUBJECTS):
        (work / ("f%d" % n)).write_text(subject)
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", subject)
        shas.append(git(work, "rev-parse", "HEAD"))
    git(work, "push", "-q", "origin", "stack")
    return work, shas


def runs(*pairs, total=None):
    found = [{"name": "job %d" % n, "status": status, "conclusion": conclusion} for n, (status, conclusion) in enumerate(pairs)]
    return json.dumps({"total_count": len(found) if total is None else total, "check_runs": found})


OK, FAILED, RUNNING = ("completed", "success"), ("completed", "failure"), ("in_progress", None)


@pytest.mark.process("stack-green.sh run as its /bin/sh shim in a clone of a local bare origin (default branch trunk) holding a stack, with a stub gh on PATH")
@pytest.mark.parametrize("pages, expected", [
    ({(4, 1): runs(OK, ("completed", "skipped"))}, (0, 4)),
    ({(4, 1): runs(OK, RUNNING), (3, 1): runs(OK)}, (0, 3)),
    ({(4, 1): runs(*[OK] * 100, total=101), (4, 2): runs(FAILED, total=101), (3, 1): runs(OK)}, (0, 3)),
    ({(4, 1): runs(FAILED)}, (3, None)),
    ({(4, 1): "<html>502</html>"}, (2, None)),
    ({(4, 1): ("", 1)}, (2, None)),
])
def test_stack_green_prints_the_newest_tested_issue_end_3_when_none_is_and_2_without_an_answer(tmp_path, pages, expected):
    work, shas = stack_clone(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(str(bin_dir / "gh"), GH)
    for (index, page), answer in pages.items():
        text, rc = answer if isinstance(answer, tuple) else (answer, 0)
        (bin_dir / ("runs-%s-%d" % (shas[index], page))).write_text(text)
        (bin_dir / ("rc-%s-%d" % (shas[index], page))).write_text(str(rc))
    env = {**os.environ, "PATH": "%s:%s" % (bin_dir, os.environ["PATH"])}

    done = subprocess.run([SHIM], cwd=str(work), env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          timeout=60)

    code, index = expected
    assert (done.returncode, done.stdout) == (code, shas[index] + "\n" if index is not None else ""), done.stderr
    assert done.stderr.count("\n") == (0 if code == 0 else 1), done.stderr
