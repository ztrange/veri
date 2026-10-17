"""Cases that run the launch lines skills/tdd/SKILL.md prescribes against a stub `claude`, asking the leaf at the far end what it saw."""
import json
import os
import pathlib
import re
import subprocess
import time

import pytest

from conftest import ROOT, SCRIPTS

SKILL = ROOT / "skills" / "tdd" / "SKILL.md"
SKILL_MD = "skills/tdd/SKILL.md"

SENTINEL = "make sentinel-test-cmd"
SENTINEL_ISSUE = "143"
LITERAL_STEP = "A title naming `kill " + chr(37) + "1`, the \"blind\" verifier, $HOME and the shell s own job spec"
SENTINEL_STEP = LITERAL_STEP.replace("shell s own", "shell's own")

STUB = """#!/bin/sh
printf '%s\\n' "${VERI_TEST_CMD-<unset>}" > "$SEEN"
printf '%s\\n' "${VERI_STEP-<unset>}" > "$SEEN.step"
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
"""

DEVELOPER_LAUNCHES = r"\$S/supervise\.sh .*run-leaf\.sh"
VERIFIER_LAUNCHES = r"\$S/detach-leaf\.sh .*\$S/run-verdict\.sh .*\.tdd/issue-<n>-spec\.md"

PLACEHOLDERS = (
    ("<test-cmd>", SENTINEL), ("<phase>", "red"), ("<k>", "1"), ("<n>", SENTINEL_ISSUE),
    ("<test-path>", "probe.test.sh"), ("<target-test-id>", "probe-target"), ("<green-sha>", "0123abc"),
    ("<fast-cmd>", "make probe-fast"), ("<onto-sha>", "0123abc"), ("<pre-rebase-sha>", "4567def"),
    ("<base-sha>", "89abcde"), ("<conflicting-files>", "probe.txt"), ("[target]", "probe-target"),
)


class Probe:
    def __init__(self, root):
        self.root = root
        self.stub = root / "stub"
        self.run = root / "run"
        self.stub.mkdir()
        self.run.mkdir()
        (self.stub / "claude").write_text(STUB)
        (self.stub / "claude").chmod(0o755)
        self.problems = []

    def problem(self, lineno, line, text):
        self.problems.append(f"{SKILL_MD}:{lineno} {text}:{line}")


def runnable(launch, step=LITERAL_STEP):
    for placeholder, value in PLACEHOLDERS[:4]:
        launch = launch.replace(placeholder, value)
    launch = launch.replace("<STEP>", step)
    for placeholder, value in PLACEHOLDERS[4:]:
        launch = launch.replace(placeholder, value)
    opened = launch.find("<")
    if opened != -1 and ">" in launch[opened:]:
        return None
    return launch


def launch_over(directory):
    found = False
    for pidfile in sorted((directory / ".tdd").glob("*.pid")):
        found = True
        try:
            pid = int(pidfile.read_text().strip())
            os.kill(pid, 0)
        except (OSError, ValueError):
            continue
        return False
    return found


def completion_landed(directory):
    return any((directory / ".tdd").glob("*.exit"))


def launched_test_cmd(probe, lineno, line, leaf, launch, *files):
    directory = probe.run / f"{lineno}-{leaf}"
    (directory / ".tdd").mkdir(parents=True, exist_ok=True)
    (directory / "origin").write_text(f"{lineno}\t{line}\n")
    ledger = directory / ".tdd" / f"issue-{SENTINEL_ISSUE}.md"
    if leaf == "develop-refactor":
        ledger.write_text(f"# Plan for #{SENTINEL_ISSUE}\n\n- [x] {SENTINEL_STEP} ⟂ refactor pending\n- [ ] a later step the run has not reached\n")
    else:
        ledger.write_text(f"# Plan for #{SENTINEL_ISSUE}\n\n- [ ] {SENTINEL_STEP}\n")
    for name in files:
        if name:
            (directory / name).write_text(f"the {name} this launch names, which the stub never reads\n")
    env = {name: value for name, value in os.environ.items() if name not in ("VERI_TEST_CMD", "VERI_ISSUE", "VERI_STEP")}
    env.update(S=str(SCRIPTS), CLAUDE_BIN=str(probe.stub / "claude"), SEEN=str(directory / "seen"),
               VERI_STUCK_RETRIES="0", VERI_NO_VERDICT_RETRIES="0", VERI_HEARTBEAT="30", VERI_TIMEOUT="60", VERI_POLL="0.2")
    subprocess.run(["bash", "-c", launch], cwd=directory, env=env, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    exitfile = directory / ".tdd" / f"{leaf}.exit"
    deadline = time.monotonic() + 60
    while not exitfile.exists():
        if launch_over(directory) and completion_landed(directory):
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(0.2)
    try:
        answer = (directory / "seen").read_text()
    except OSError:
        return "<no leaf ran>"
    if not exitfile.exists():
        return f"<no completion file under leaf {leaf}>"
    return answer.rstrip("\n")


def scan_launches(probe, pattern, shape, check):
    numbered = [(n, line) for n, line in enumerate(SKILL.read_text().splitlines(), 1) if re.search(pattern, line)]
    if not numbered:
        probe.problems.append(f"{SKILL_MD} has no line launching {shape} — the launch this case is about could not be found")
        return
    for lineno, line in numbered:
        launch = runnable(line)
        if launch is None:
            probe.problem(lineno, line, "names a placeholder this probe cannot supply, so its launch could not be run")
            continue
        check(probe, lineno, line, launch)


def expect_sentinel(probe, lineno, line, leaf, launch, *files):
    got = launched_test_cmd(probe, lineno, line, leaf, launch, *files).rstrip("\n")
    if got != SENTINEL:
        probe.problem(lineno, line, f"launches {leaf}, whose leaf saw VERI_TEST_CMD={got}, want {SENTINEL}")


def check_developer_launch(probe, lineno, line, launch):
    leaf = re.sub(r".*supervise\.sh +([^ ]+).*", r"\1", launch)
    prompt = re.search(r"\.tdd/[A-Za-z0-9_.-]+\.prompt", launch)
    if prompt is None:
        probe.problem(lineno, line, f"launches {leaf} with no .tdd/<name>.prompt file to run, so its leaf could not be started")
        return
    expect_sentinel(probe, lineno, line, leaf, launch, prompt.group(0))


def check_verifier_launch(probe, lineno, line, launch):
    clean = re.sub(r" --(step|fast-cmd) ('[^']*'|\"[^\"]*\")", "", launch)
    words = clean.split("run-verdict.sh ", 1)[1].split()
    words += [""] * (3 - len(words))
    phase, spec, subject = words[:3]
    expect_sentinel(probe, lineno, line, f"verify-{phase}", launch, spec, subject)


def run_developer_launches(probe):
    scan_launches(probe, DEVELOPER_LAUNCHES, "a leaf through supervise.sh into run-leaf.sh", check_developer_launch)


def run_verifier_launches(probe):
    scan_launches(probe, VERIFIER_LAUNCHES, "a verifier through run-verdict.sh against a spec file", check_verifier_launch)


def bad_context(log, step):
    try:
        lines = [l for l in pathlib.Path(log).read_text().splitlines() if l.strip()]
    except OSError:
        return "<<no event log>>"
    bad = []
    for line in lines:
        try:
            obj = json.loads(line)
        except ValueError:
            bad.append("unparseable event line")
            continue
        if obj.get("issue") != SENTINEL_ISSUE or obj.get("step") != step:
            bad.append("%s issue=%r step=%r" % (obj.get("event"), obj.get("issue"), obj.get("step")))
    if not lines:
        return "<<no event line written>>"
    return "; ".join(bad)


def launched_trees(probe):
    return sorted(probe.run.iterdir())


def want_step_for(line):
    want = ""
    if "VERI_STEP" in line:
        want = SENTINEL_STEP
    if "VERI_STEP='<STEP>'" in line:
        want = LITERAL_STEP
    return want


@pytest.fixture
def probe(tmp_path):
    return Probe(tmp_path)


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(300)
def test_every_leaf_skill_md_launches_through_supervise_sh_sees_the_runs_test_command_as_veri_test_cmd(probe):
    run_developer_launches(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through verify.sh")
@pytest.mark.timeout(300)
def test_every_verifier_skill_md_launches_through_verify_sh_sees_the_runs_test_command_as_veri_test_cmd(probe):
    run_verifier_launches(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(600)
def test_every_leaf_skill_md_launches_leaves_events_carrying_the_runs_issue_and_step(probe):
    run_developer_launches(probe)
    run_verifier_launches(probe)
    probe.problems.clear()

    trees = launched_trees(probe)
    if not trees:
        probe.problems.append("no launch line was run, so no leaf's events could be read")
    for tree in trees:
        if not (tree / "origin").is_file():
            probe.problems.append(f"{tree.name} was launched with no record of which line of {SKILL_MD} ran it")
            continue
        lineno, line = (tree / "origin").read_text().rstrip("\n").split("\t", 1)
        want = want_step_for(line)
        complaint = bad_context(tree / ".tdd" / "events.jsonl", want)
        if complaint:
            probe.problem(lineno, line, f"leaves events that do not carry issue={SENTINEL_ISSUE} step='{want}' ({complaint})")

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(600)
def test_every_leaf_skill_md_launches_with_veri_step_set_sees_the_runs_step_as_veri_step(probe):
    run_developer_launches(probe)
    run_verifier_launches(probe)
    probe.problems.clear()

    trees = launched_trees(probe)
    if not trees:
        probe.problems.append("no launch line was run, so no leaf's VERI_STEP could be read")
    for tree in trees:
        if not (tree / "origin").is_file():
            continue
        lineno, line = (tree / "origin").read_text().rstrip("\n").split("\t", 1)
        if " verdict-plan " in line:
            continue
        want = LITERAL_STEP if "VERI_STEP='<STEP>'" in line else SENTINEL_STEP
        try:
            got = (tree / "seen.step").read_text().rstrip("\n")
        except OSError:
            got = "<no leaf ran>"
        if got != want:
            probe.problem(lineno, line, f"launches {tree.name}, whose leaf saw VERI_STEP=<{got}>, want <{want}>")

    assert probe.problems == []
