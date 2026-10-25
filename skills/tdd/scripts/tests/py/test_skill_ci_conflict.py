"""Cases for how skills/tdd/SKILL.md's CI step answers a conflicting PR, read as text.

Contract under test:
  1. In the step that readies the PR and reads its CI, a wait-ci.sh exit 2 whose stderr names a
     conflict rebases onto origin/<default> through the existing rebase path -- the rebase verifier,
     the full suite, the push under a pinned lease -- and waits for CI again, once; a second
     conflict bails with cause ci-conflict.
  2. That conflict rebase says rebase-onto-default.sh's exit code decides the next action, so
     nothing after it -- the rebased tip's full run in particular -- starts until it has returned,
     and never in the same message as the rebase.
"""
import os
import pathlib
import re
import subprocess

import pytest

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"

CI_START = re.compile(r"^2\. \*\*Mark the PR ready")
CI_END = re.compile(r"^([0-9]+\. |#)")
WS = r"[ \t\n\r\f\v]"
NO_STEP = "SKILL.md has no CI step (2. **Mark the PR ready …) to read — nothing could be checked"


def _ci_step():
    out, inside = [], False
    for line in SKILL.read_bytes().decode("latin-1").split("\n"):
        if CI_START.match(line):
            inside = True
        if inside and CI_END.match(line) and not CI_START.match(line):
            break
        if inside:
            out.append(line)
    return "\n".join(out)


def _block(step):
    out, after, on = [], False, False
    for line in step.split("\n"):
        if re.fullmatch(WS + r"*\$S/push-branch\.sh" + WS + "*", line):
            after = True
            continue
        if after and re.search(r"\$S/refactor-owed\.sh render", line):
            break
        if after and re.search(r"\$S/wait-ci\.sh", line):
            on = True
        if on:
            out.append(line)
    return "\n".join(out).rstrip("\n").replace("<n>", "1458").replace("<pr-url>", "https://example.test/pull/1")


@pytest.mark.process("the block SKILL.md prescribes after the metrics: push runs under bash -c in a git repo, against stub scripts")
def test_the_block_run_after_the_metrics_push_bails_nothing_on_a_conflict_the_first_time_and_ci_conflict_once_the_marker_exists(tmp_path):
    step = _ci_step()
    assert step.strip(), NO_STEP
    block = _block(step)
    assert block.strip(), "no wait-ci.sh line between $S/push-branch.sh and $S/refactor-owed.sh render in the CI step — nothing could be run"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {"wait-ci.sh": '#!/bin/sh\necho "PR conflicts with its base branch" >&2\nexit 2\n',
             "event.sh": '#!/bin/sh\necho "$*" >> events.log\n',
             "classify-bail.sh": '#!/bin/sh\necho "$1"\n',
             "ledger-steps.sh": "#!/bin/sh\nexit 0\n",
             "gh": "#!/bin/sh\nexit 0\n"}
    for name, body in stubs.items():
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    problems = []
    for marked in ("no", "yes"):
        work = tmp_path / f"work-{marked}"
        work.mkdir()
        subprocess.run(["git", "-C", str(work), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(work), "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-q", "--allow-empty", "-m", "init"], check=True)
        (work / ".tdd").mkdir()
        if marked == "yes":
            (work / ".tdd" / "ci-conflict-rebased").write_text("")
        env = dict(os.environ, S=str(bin_dir), PATH=f"{bin_dir}:{os.environ['PATH']}")
        subprocess.run(["bash", "-c", block.encode("latin-1").decode("utf-8", "surrogateescape")], cwd=work, env=env,
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log = work / "events.log"
        got = log.read_text().rstrip("\n") if log.exists() else ""
        if marked == "no":
            if "bail" in got:
                problems.append(f"first conflict exit 2 after the metrics: push recorded a bail: {got}")
        elif got != "bail cause=ci-conflict classification=ci-conflict":
            problems.append(f"second conflict exit 2 after the metrics: push recorded [{got}], not bail cause=ci-conflict")
    assert not problems, "\n".join(problems)


def _first_block(step):
    out, on = [], False
    for line in step.split("\n"):
        if not on and re.search(r"\$S/wait-ci\.sh", line):
            on = True
        if on and line.strip() == "```":
            break
        if on:
            out.append(line)
    return "\n".join(out).rstrip("\n").replace("<n>", "1458").replace("<pr-url>", "https://example.test/pull/1").replace("<run-id>", "1").replace("<pr-number>", "1")


@pytest.mark.process("the two CI blocks SKILL.md prescribes run under bash -c in a git repo, against stub scripts")
def test_a_green_ci_wait_in_either_ci_block_bails_no_ci_red_and_appends_no_ci_repair_step_with_or_without_one_in_the_ledger(tmp_path):
    step = _ci_step()
    assert step.strip(), NO_STEP
    blocks = {"first CI wait": _first_block(step), "post-metrics CI wait": _block(step)}
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {"pr-ready.sh": "#!/bin/sh\nexit 0\n",
             "wait-ci.sh": "#!/bin/sh\nexit 0\n",
             "event.sh": '#!/bin/sh\necho "$*" >> events.log\n',
             "classify-bail.sh": '#!/bin/sh\necho "$1"\n',
             "add-ledger-step.sh": '#!/bin/sh\necho "$*" >> added.log\n',
             "ledger-steps.sh": '#!/bin/sh\n[ "$1" != has-mark ] || [ -e has-repair ] || exit 1\n[ "$1" != last-done ] || echo "step 1"\nexit 0\n',
             "gh": "#!/bin/sh\nexit 0\n"}
    for name, body in stubs.items():
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    problems = []
    for label, block in blocks.items():
        assert block.strip(), f"no {label} block found in the CI step — nothing could be run"
        for held in ("with-repair", "no-repair"):
            work = tmp_path / f"work-{label.split()[0]}-{held}"
            work.mkdir()
            subprocess.run(["git", "-C", str(work), "init", "-q"], check=True)
            (work / ".tdd").mkdir()
            (work / ".tdd" / "issue-1458.md").write_text("")
            if held == "with-repair":
                (work / "has-repair").write_text("")
            env = dict(os.environ, S=str(bin_dir), PATH=f"{bin_dir}:{os.environ['PATH']}")
            subprocess.run(["bash", "-c", block.encode("latin-1").decode("utf-8", "surrogateescape")], cwd=work, env=env,
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            events = (work / "events.log").read_text() if (work / "events.log").exists() else ""
            added = (work / "added.log").read_text() if (work / "added.log").exists() else ""
            if "bail" in events or "step-added" in events or added:
                problems.append(f"{label}, green CI, ledger {held}: events [{events.strip()}] added [{added.strip()}]")
    assert not problems, "\n".join(problems)


@pytest.mark.process("the Draft PR step's ready line runs under bash -c in a git repo, against stub scripts")
def test_issue_2147_a_failing_pr_ready_script_leaves_wait_ci_unrun_and_writes_no_ci_deadline(tmp_path):
    step = _ci_step()
    assert step.strip(), NO_STEP
    all_lines = step.split("\n")
    start = next((i for i, l in enumerate(all_lines) if re.search(r"\$S/pr-ready\.sh", l)), None)
    assert start is not None, "no line running $S/pr-ready.sh in the CI step — nothing could be run"
    end = next((i for i in range(start, len(all_lines)) if re.search(r"\$S/wait-ci\.sh", all_lines[i])), None)
    assert end is not None, "no line running $S/wait-ci.sh at or after the $S/pr-ready.sh line in the CI step"
    lines = all_lines[start:end + 1]
    block = "\n".join(lines).replace("<n>", "2147").replace("<pr-number>", "7").replace("<pr-url>", "https://example.test/pull/7")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {"pr-ready.sh": "#!/bin/sh\nexit 1\n",
             "wait-ci.sh": '#!/bin/sh\necho called >> wait-ci.log\nmkdir -p .tdd\n: > ".tdd/ci-deadline-$4"\nexit 0\n',
             "event.sh": "#!/bin/sh\nexit 0\n",
             "classify-bail.sh": '#!/bin/sh\necho "$1"\n'}
    for name, body in stubs.items():
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "-C", str(work), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(work), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "init"], check=True)
    (work / ".tdd").mkdir()
    env = dict(os.environ, S=str(bin_dir), PATH=f"{bin_dir}:{os.environ['PATH']}")
    script = block.encode("latin-1").decode("utf-8", "surrogateescape")
    parsed = subprocess.run(["bash", "-n", "-c", script], cwd=work, env=env,
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    assert parsed.returncode == 0, f"the pr-ready..wait-ci lines are not valid bash as written:\n{parsed.stderr}"
    subprocess.run(["bash", "-c", script], cwd=work, env=env,
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    problems = []
    if (work / "wait-ci.log").exists():
        problems.append("wait-ci.sh ran although pr-ready.sh exited non-zero")
    deadlines = sorted(p.name for p in (work / ".tdd").glob("ci-deadline-*"))
    if deadlines:
        problems.append(f"a CI deadline was written after a failed ready: {deadlines}")
    assert not problems, "\n".join(problems)


def _preflight_block():
    lines = SKILL.read_bytes().decode("latin-1").split("\n")
    at = next((i for i, l in enumerate(lines) if l.strip() == "rm -f .tdd/ci-conflict-rebased"), None)
    if at is None:
        return ""
    top = max(i for i in range(at) if lines[i].strip() == "```")
    bottom = next(i for i in range(at, len(lines)) if lines[i].strip() == "```")
    return "\n".join(lines[top + 1:bottom]).replace("<n>", "2375").replace("<slug>", "a-slug")


@pytest.mark.process("SKILL.md's preflight lines, then its first CI-wait block, run under bash -c in a git repo, against stub scripts")
def test_issue_2375_a_resumed_run_with_a_marker_an_earlier_run_left_records_no_ci_conflict_bail_on_its_first_conflict(tmp_path):
    preflight = _preflight_block()
    assert preflight.strip(), "no `rm -f .tdd/ci-conflict-rebased` line in a SKILL.md code block — no preflight to run"
    first = _first_block(_ci_step())
    assert first.strip(), "no first CI-wait block in the CI step — nothing could be run"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {"issue-worktree.sh": '#!/bin/sh\necho "$PWD"\n',
             "stop-requested.sh": "#!/bin/sh\nexit 0\n",
             "pr-ready.sh": "#!/bin/sh\nexit 0\n",
             "wait-ci.sh": '#!/bin/sh\necho called >> wait-ci.log\necho "PR conflicts with its base branch" >&2\nexit 2\n',
             "event.sh": '#!/bin/sh\necho "$*" >> events.log\n',
             "classify-bail.sh": '#!/bin/sh\necho "$1"\n',
             "ledger-steps.sh": "#!/bin/sh\nexit 0\n",
             "gh": "#!/bin/sh\nexit 0\n"}
    for name, body in stubs.items():
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "-C", str(work), "init", "-q"], check=True)
    (work / ".tdd").mkdir()
    (work / ".tdd" / "ci-conflict-rebased").write_text("")
    env = dict(os.environ, S=str(bin_dir), PATH=f"{bin_dir}:{os.environ['PATH']}")
    script = (preflight + "\n" + first).encode("latin-1").decode("utf-8", "surrogateescape")
    subprocess.run(["bash", "-c", script], cwd=work, env=env,
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = work / "events.log"
    got = log.read_text().rstrip("\n") if log.exists() else ""
    assert "bail" not in got, f"a resumed run with a leftover marker met its first conflict and recorded [{got}] instead of rebasing"
    waits = (work / "wait-ci.log").read_text().split() if (work / "wait-ci.log").exists() else []
    assert waits == ["called"], f"the first CI-wait block ran wait-ci.sh {len(waits)} times, not once, so the conflict it rebases on was never met"
    assert got == "", f"the first conflict of a resumed run recorded [{got}]; it must record nothing and leave the one rebase to the run"
    assert not (work / ".tdd" / "ci-conflict-rebased").exists(), "the leftover marker survived preflight, so the run's one rebase was already spent"


@pytest.mark.process("SKILL.md's preflight, its CI-conflict rebase marker, then its first CI-wait block, run under bash -c in a git repo, against stub scripts")
def test_issue_2375_a_second_conflict_after_the_runs_own_rebase_records_a_ci_conflict_bail(tmp_path):
    preflight = _preflight_block()
    assert preflight.strip(), "no `rm -f .tdd/ci-conflict-rebased` line in a SKILL.md code block — no preflight to run"
    first = _first_block(_ci_step())
    assert first.strip(), "no first CI-wait block in the CI step — nothing could be run"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {"issue-worktree.sh": '#!/bin/sh\necho "$PWD"\n',
             "stop-requested.sh": "#!/bin/sh\nexit 0\n",
             "pr-ready.sh": "#!/bin/sh\nexit 0\n",
             "wait-ci.sh": '#!/bin/sh\necho "PR conflicts with its base branch" >&2\nexit 2\n',
             "event.sh": '#!/bin/sh\necho "$*" >> events.log\n',
             "classify-bail.sh": '#!/bin/sh\necho "$1"\n',
             "ledger-steps.sh": "#!/bin/sh\nexit 0\n",
             "gh": "#!/bin/sh\nexit 0\n"}
    for name, body in stubs.items():
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "-C", str(work), "init", "-q"], check=True)
    (work / ".tdd").mkdir()
    env = dict(os.environ, S=str(bin_dir), PATH=f"{bin_dir}:{os.environ['PATH']}")
    script = (preflight + "\ntouch .tdd/ci-conflict-rebased\n" + first).encode("latin-1").decode("utf-8", "surrogateescape")
    subprocess.run(["bash", "-c", script], cwd=work, env=env,
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = work / "events.log"
    got = log.read_text().rstrip("\n") if log.exists() else ""
    assert got == "bail cause=ci-conflict classification=ci-conflict", f"a second conflict after the run's own rebase recorded [{got}], not bail cause=ci-conflict"
