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
from skill_sections import plain as _plain

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


def _conflict_text(step):
    paras, para = [], ""
    for line in step.split("\n"):
        if re.fullmatch(WS + "*", line):
            paras.append(para)
            para = ""
        else:
            para = para + " " + line
    paras.append(para)
    kept = [p for p in paras if re.search("[Cc]onflict", p)]
    return re.sub(WS + "+", " ", _plain("\n".join(kept)))


def _sentences(text):
    return text.replace(". ", ".\n").split("\n")


def test_the_ci_step_sends_a_wait_ci_exit_2_naming_a_conflict_through_the_rebase_path_once_and_bails_ci_conflict_on_a_second():
    step = _ci_step()
    assert step.strip(), NO_STEP
    text = _conflict_text(step)
    assert text.strip(), "the CI step never mentions a conflict"
    problems = []
    for want in (r"wait-ci\.sh", "exit 2", "stderr", r"rebase-onto-default\.sh|origin/<default>",
                 "verify-rebase|rebase verifier", "full (suite|test command)", "lease",
                 "once", "second conflict", "bail", "ci-conflict"):
        if not re.search(want, text):
            problems.append(f"the CI step's conflict instructions never mention /{want}/")
    if not re.search(r"event\.sh bail cause=ci-conflict", step):
        problems.append("the CI step's commands carry no event.sh bail cause=ci-conflict")
    assert not problems, "\n".join(problems)


def test_the_ci_steps_conflict_rebase_says_rebase_onto_default_exit_code_decides_the_next_action_and_nothing_starts_until_it_has_returned():
    step = _ci_step()
    assert step.strip(), NO_STEP
    gate = [s for s in _sentences(_conflict_text(step))
            if "rebase-onto-default.sh" in s and "exit code" in s
            and re.search(r"decides?[^.]*next action", s) and "full" in s
            and re.search(r"until[^.]*returned", s) and "same message" in s]
    assert gate, ("no sentence of the CI step's conflict instructions says rebase-onto-default.sh's exit code decides "
                  "the next action, so nothing after it — the rebased tip's full run in particular — is started until it "
                  "has returned, and never in the same message as the rebase; a conductor batching tool calls starts the "
                  "full run beside a rebase that exits 3")


def test_the_ci_step_gives_a_merge_conflict_ci_reports_after_the_metrics_push_the_same_one_rebase_path_not_ci_timeout():
    step = _ci_step()
    assert step.strip(), NO_STEP
    late = [s for s in _sentences(_conflict_text(step))
            if "metrics:" in s and "conflict" in s and "rebase" in s
            and re.search("same|once", s) and "ci-conflict" in s and "ci-timeout" in s]
    assert late, ("no sentence of the CI step about the metrics: push says a conflict CI reports there takes the same "
                  "one-rebase path, bails ci-conflict on a second, and is not waited into ci-timeout; read literally, "
                  "the conductor waits out a finished run and bails ci-timeout")


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
