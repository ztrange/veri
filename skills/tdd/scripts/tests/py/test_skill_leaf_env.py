"""Cases that run the launch lines skills/tdd/SKILL.md prescribes against a stub `claude`, asking the leaf at the far end what it saw."""
import collections
import hashlib
import importlib
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
REVISE_MD = SKILL.with_name("REVISE.md")
STOPPING = ROOT / "skills" / "tdd" / "STOPPING.md"
BAIL = ROOT / "skills" / "tdd" / "BAIL.md"
RECONCILE = ROOT / "skills" / "tdd" / "RECONCILE.md"

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


class Shared:
    def __init__(self, root):
        self.root = root
        self.stages = {}


class Probe:
    def __init__(self, root, shared=None):
        self.root = root
        self.shared = shared or Shared(root / "shared")
        self.stub = root / "stub"
        self.run = root / "run"
        self.stub.mkdir()
        self.run.mkdir()
        (self.stub / "claude").write_text(STUB)
        (self.stub / "claude").chmod(0o755)
        self.problems = []
        self.launches = []

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


def note_launch(probe, lineno, line, tree):
    if "detach-leaf.sh" not in line:
        return
    try:
        ledger = (tree / ".tdd" / f"issue-{SENTINEL_ISSUE}.md").read_text()
    except OSError:
        ledger = ""
    shape = "ticked" if "refactor pending" in ledger else "done" if "[x]" in ledger else "plain"
    probe.launches.append((lineno, shape, line))


def launched_beside(probe, lineno, planter, line):
    shape = "ticked" if planter is plant_ticked_ledger else "plain"
    return (lineno, shape, line) in probe.launches


def write_check_earlier_pass(directory, step):
    identity = ["-c", "user.name=probe", "-c", "user.email=probe@example.com"]
    subprocess.run(["git", "init", "-q"], cwd=directory, check=True)
    (directory / ".git" / "info" / "exclude").write_text("*\n")
    subprocess.run(["git", *identity, "commit", "-q", "--allow-empty", "-m", "probe"], cwd=directory, check=True)
    here = os.getcwd()
    os.chdir(directory)
    try:
        importlib.import_module("veri.tests_frozen")._write_pass_marker(step)
    finally:
        os.chdir(here)


def launched_test_cmd(probe, lineno, line, leaf, launch, *files, scripts=SCRIPTS, clock=time.monotonic, sleep=time.sleep):
    directory = probe.run / f"{lineno}-{leaf}"
    (directory / ".tdd").mkdir(parents=True, exist_ok=True)
    (directory / "origin").write_text(f"{lineno}\t{line}\n")
    ledger = directory / ".tdd" / f"issue-{SENTINEL_ISSUE}.md"
    if leaf == "develop-refactor":
        ledger.write_text(f"# Plan for #{SENTINEL_ISSUE}\n\n- [x] {SENTINEL_STEP} ⟂ refactor pending\n- [ ] a later step the run has not reached\n")
    else:
        ledger.write_text(f"# Plan for #{SENTINEL_ISSUE}\n\n- [ ] {SENTINEL_STEP}\n")
    note_launch(probe, lineno, line, directory)
    for name in files:
        if name:
            (directory / name).write_text(f"the {name} this launch names, which the stub never reads\n")
    if leaf in ("verify-red", "verify-green"):
        write_check_earlier_pass(directory, SENTINEL_STEP)
    env = {name: value for name, value in os.environ.items() if name not in ("VERI_TEST_CMD", "VERI_ISSUE", "VERI_STEP")}
    env.update(S=str(scripts), CLAUDE_BIN=str(probe.stub / "claude"), SEEN=str(directory / "seen"),
               VERI_STUCK_RETRIES="0", VERI_NO_VERDICT_RETRIES="0", VERI_HEARTBEAT="30", VERI_TIMEOUT="60", VERI_POLL="0.2")
    subprocess.run(["bash", "-c", launch], cwd=directory, env=env, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    exitfile = directory / ".tdd" / f"{leaf}.exit"
    deadline = clock() + 60
    while not exitfile.exists():
        if launch_over(directory) and completion_landed(directory):
            break
        if clock() >= deadline:
            break
        sleep(0.2)
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


def expect_sentinel(probe, lineno, line, leaf, launch, *files, **kwargs):
    got = launched_test_cmd(probe, lineno, line, leaf, launch, *files, **kwargs).rstrip("\n")
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


class Scans:
    def __init__(self, probe, developer, verifier):
        self.probe = probe
        self.developer = developer
        self.verifier = verifier


def launch_scans_once(root, shared):
    probe = Probe(root, shared)
    run_developer_launches(probe)
    developer, probe.problems = probe.problems, []
    run_verifier_launches(probe)
    verifier, probe.problems = probe.problems, []
    return Scans(probe, developer, verifier)


def launched_trees(scans):
    return sorted(scans.probe.run.iterdir())


def want_step_for(line):
    want = ""
    if "VERI_STEP" in line:
        want = SENTINEL_STEP
    if "VERI_STEP='<STEP>'" in line:
        want = LITERAL_STEP
    return want


APOSTROPHE_STEP = "A background process is killed by the pid recorded when it started, never by that shell's own job spec"
EXPANDING_STEP = 'A title naming `kill ' + chr(37) + '1`, the "blind" verifier and $HOME reaches the leaf as written'
DECOY_STEP = "a decoy step the ledger holds, which ledger-steps.sh current never names"
CRITERION_TEXT = "The issue's own words: `echo $SHELL` in \"quotes\" and $HOME, as the issue wrote them"

DETACH_RECORDER = """#!/bin/sh
printf '%s\\n' "${VERI_STEP-<unset>}" > "$SEEN"
step='<no --step argument>'
while [ "$#" -gt 0 ]; do
  if [ "$1" = --step ]; then step="${2-<--step with no value>}"; break; fi
  shift
done
printf '%s\\n' "$step" > "$SEEN.argv"
"""

TITLE_RECORDER = """#!/bin/sh
out="$SEEN.$(basename "$0" .sh)"
printf '%s\\n' "${VERI_STEP-<unset>}" > "$out"
for a in "$@"; do printf '%s\\n' "$a" >> "$out"; done
"""

LEDGER_STEPS_RECORDER = """#!/bin/sh
case "$1" in current|current-or-last-done) ;; *) exit 2 ;; esac
cat "$SEEN.current"
"""

CONDUCTOR_CALLEES = ("event", "preserve-attempt", "tick-ledger", "clear-refactor-pending", "tick-issue-criterion")
CONDUCTOR_CALLEE = re.compile(r"\$S/(" + "|".join(CONDUCTOR_CALLEES) + r")\.sh")
PROMPT_CALLEE = re.compile(r"\$S/(build-develop-prompt|add-ledger-step)\.sh")

GH_STUB = """#!/bin/sh
cat <<'BODY'
## Problem

- [ ] a checkbox in the prose, not a criterion

## Acceptance criteria

- [ ] the first criterion
- [ ] %s
      wrapped onto a second line

Test command: `make test`
BODY
"""


def write_executable(path, text):
    path.write_text(text)
    path.chmod(0o755)


def recorder(probe, name, text):
    directory = probe.shared.root / "recorders"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    if not path.exists():
        write_executable(path, text)
    return path


def write_ledger(tree, steps):
    (tree / ".tdd" / f"issue-{SENTINEL_ISSUE}.md").write_text(f"# Plan for #{SENTINEL_ISSUE}\n\n{steps}")


def plant_ledger(tree, title):
    write_ledger(tree, f"- [ ] {title}\n")


def plant_ticked_ledger(tree, title):
    write_ledger(tree, f"- [x] {title} ⟂ refactor pending\n- [ ] a later step the run has not reached\n")


def plant_done_ledger(tree, title):
    write_ledger(tree, f"- [x] {title}\n- [ ] a later step the run has not reached\n")


def shared_stage(probe, titled):
    shared = probe.shared
    if titled not in shared.stages:
        stage = shared.root / f"stage-{len(shared.stages)}-scripts"
        stage.mkdir(parents=True)
        for script in sorted(SCRIPTS.glob("*.sh")) + [SCRIPTS / "lib", SCRIPTS / "prompts", SCRIPTS / "veri"]:
            if script.name != "detach-leaf.sh" and script.stem not in titled:
                (stage / script.name).symlink_to(script)
        (stage / "detach-leaf.sh").symlink_to(recorder(probe, "detach-leaf.sh", DETACH_RECORDER))
        for script in titled:
            if script == "ledger-steps":
                (stage / "ledger-steps.sh").symlink_to(recorder(probe, "ledger-steps.sh", LEDGER_STEPS_RECORDER))
            else:
                (stage / f"{script}.sh").symlink_to(recorder(probe, "title.sh", TITLE_RECORDER))
        shared.stages[titled] = stage
    return shared.stages[titled]


def stage_recorder(probe, tag, *titled):
    seen = probe.root / f"{tag}-seen"
    tree = probe.root / f"{tag}-tree"
    (tree / ".tdd").mkdir(parents=True)
    return shared_stage(probe, tuple(sorted(titled))), seen, tree


def read_answer(path, default):
    try:
        return path.read_text().rstrip("\n")
    except OSError:
        return default


def run_staged(stage, seen, tree, launch, default, path=None):
    env = {name: value for name, value in os.environ.items() if name not in ("VERI_TEST_CMD", "VERI_ISSUE", "VERI_STEP")}
    env.update(S=str(stage), SEEN=str(seen))
    if path is not None:
        env["PATH"] = path
    done = subprocess.run(["bash", "-c", launch], cwd=tree, env=env, stdin=subprocess.DEVNULL,
                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    err = done.stderr.decode(errors="replace")
    got = read_answer(pathlib.Path(f"{seen}"), default)
    argv = read_answer(pathlib.Path(f"{seen}.argv"), "<no verifier was launched>")
    return err, got, argv


def flat(err):
    return err.replace("\n", "")


def numbered_lines(pattern, text=None):
    text = SKILL.read_text() if text is None else text
    return [(n, line) for n, line in enumerate(text.split("\n"), 1) if re.search(pattern, line)]


def supervise_arg(text):
    return re.sub(r".*supervise\.sh +([^ ]+).*", r"\1", text)


def scan_step_title(probe, title=APOSTROPHE_STEP, tag="step-title", leaf="develop-red", planter=plant_ledger, text=None):
    pattern = r"\$S/detach-leaf\.sh .*\$S/supervise\.sh " + leaf + r" \$S/run-leaf\.sh"
    hits = numbered_lines(pattern, text)[:1]
    if not hits:
        probe.problems.append(f"{SKILL_MD} has no line launching {leaf} through supervise.sh into run-leaf.sh — the launch this case is about could not be found")
        return
    lineno, line = hits[0]
    launch = runnable(line, title)
    if launch is None:
        probe.problem(lineno, line, "names a placeholder this probe cannot supply, so its launch could not be run")
        return
    if launched_beside(probe, lineno, planter, line):
        return
    stage, seen, tree = stage_recorder(probe, tag)
    (tree / ".tdd" / f"{leaf}.prompt").write_text("the prompt this launch names, which the recorder never reads\n")
    planter(tree, title)
    note_launch(probe, lineno, line, tree)
    err, got, _ = run_staged(stage, seen, tree, launch, "<no leaf was launched>")
    if got != title:
        probe.problem(lineno, line, f"launched with the step title <{title}>, whose leaf saw VERI_STEP=<{got}> (the launching shell said: {flat(err)})")


def scan_verdict_step_title(probe):
    title = EXPANDING_STEP
    hits = numbered_lines(r"\$S/detach-leaf\.sh .*\$S/supervise\.sh verdict-red \$S/run-verdict\.sh")[:1]
    if not hits:
        probe.problems.append(f"{SKILL_MD} has no line launching verdict-red through supervise.sh into run-verdict.sh — the launch this case is about could not be found")
        return
    lineno, line = hits[0]
    launch = runnable(line, title)
    if launch is None:
        probe.problem(lineno, line, "names a placeholder this probe cannot supply, so its launch could not be run")
        return
    if launched_beside(probe, lineno, plant_ledger, line):
        return
    stage, seen, tree = stage_recorder(probe, "expanding-step-title-verdict")
    plant_ledger(tree, title)
    note_launch(probe, lineno, line, tree)
    err, got, argv = run_staged(stage, seen, tree, launch, "<no verifier was launched>")
    if got != title:
        probe.problem(lineno, line, f"launched with the step title <{title}>, whose verifier saw VERI_STEP=<{got}> (the launching shell said: {flat(err)})")
    if argv != title:
        probe.problem(lineno, line, f"launched with the step title <{title}>, whose verifier was handed --step <{argv}> (the launching shell said: {flat(err)})")


def fill_supplied_leaf(numbered_line):
    return numbered_line.replace("<name>", "probe-leaf").replace("<cmd> [args...]", "$S/run-leaf.sh .tdd/probe-leaf.prompt")


def ledgers_for(leaf):
    if re.search(r"<.*>", leaf) or leaf in ("develop-exhausted", "develop-reconcile"):
        return [plant_ledger, plant_ticked_ledger]
    if leaf.endswith("-refactor"):
        return [plant_ticked_ledger]
    return [plant_ledger]


def scan_every_step_title(probe):
    title = EXPANDING_STEP
    hits = [(n, line) for n, line in numbered_lines(r"\$S/detach-leaf\.sh .*\$S/supervise\.sh ") if "VERI_STEP=" in line]
    if not hits:
        probe.problems.append(f"{SKILL_MD} has no line launching a leaf with VERI_STEP set through detach-leaf.sh and supervise.sh — the launch this case is about could not be found")
        return
    for lineno, original in hits:
        launch = runnable(fill_supplied_leaf(original), title)
        if launch is None:
            probe.problem(lineno, fill_supplied_leaf(original), "names a placeholder this probe cannot supply, so its launch could not be run")
            continue
        leaf = supervise_arg(launch)
        for planter in ledgers_for(supervise_arg(original)):
            if launched_beside(probe, lineno, planter, original):
                continue
            stage, seen, tree = stage_recorder(probe, f"every-step-title-{lineno}-{planter.__name__}")
            planter(tree, title)
            note_launch(probe, lineno, original, tree)
            err, got, argv = run_staged(stage, seen, tree, launch, "<no leaf was launched>")
            if got != title:
                probe.problem(lineno, original, f"launched {leaf} beside a ledger from {planter.__name__} with the step title <{title}>, whose leaf saw VERI_STEP=<{got}> (the launching shell said: {flat(err)})")
            if "--step" not in original:
                continue
            if argv != title:
                probe.problem(lineno, original, f"launched {leaf} beside a ledger from {planter.__name__} with the step title <{title}>, whose verifier was handed --step <{argv}> (the launching shell said: {flat(err)})")


NEXT_STEP_READS = ('VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)"',
                   'VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh)"')


def scan_current_step_title(probe):
    title = EXPANDING_STEP
    hits = [(n, line) for n, line in numbered_lines(r"\$S/detach-leaf\.sh .*\$S/supervise\.sh ")
            if "VERI_STEP=" in line and not any(read in line for read in NEXT_STEP_READS)]
    if not hits:
        probe.problems.append(f"{SKILL_MD} has no line launching a leaf whose VERI_STEP reads the current step — the launch this case is about could not be found")
        return
    for lineno, original in hits:
        launch = runnable(fill_supplied_leaf(original), title)
        if launch is None:
            probe.problem(lineno, fill_supplied_leaf(original), "names a placeholder this probe cannot supply, so its launch could not be run")
            continue
        leaf = supervise_arg(launch)
        stage, seen, tree = stage_recorder(probe, f"current-step-title-{lineno}", "ledger-steps")
        plant_ledger(tree, DECOY_STEP)
        pathlib.Path(f"{seen}.current").write_text(title + "\n")
        err, got, argv = run_staged(stage, seen, tree, launch, "<no leaf was launched>")
        if got != title:
            probe.problem(lineno, original, f"launched {leaf} with ledger-steps.sh current answering <{title}>, whose leaf saw VERI_STEP=<{got}> (the launching shell said: {flat(err)})")
        if "--step" not in original:
            continue
        if argv != title:
            probe.problem(lineno, original, f"launched {leaf} with ledger-steps.sh current answering <{title}>, whose verifier was handed --step <{argv}> (the launching shell said: {flat(err)})")


def conductor_command(md_lines, n, script):
    text = md_lines[n - 1]
    if "`" not in text:
        return text.lstrip(" \t\n\v\f\r").split("  # ")[0]
    before = text[:text.index(f"$S/{script}.sh")]
    after = text[len(before):]
    while "`" not in after and n < len(md_lines):
        after += " " + md_lines[n].lstrip(" \t\n\v\f\r")
        n += 1
    return before.rsplit("`", 1)[-1] + after.split("`", 1)[0]


def fill_title(cmd, title):
    launch = cmd.replace("<n>", SENTINEL_ISSUE)
    for placeholder in ("<STEP>", "<distinctive substring of STEP>", "<substring>", "<anchor>"):
        launch = launch.replace(placeholder, title)
    launch = launch.replace("<phase>", "red").replace("<k>", "2")
    return re.sub(r"<[^<>]*>", "probe", launch)


def recorded_arguments(seen, script):
    try:
        text = pathlib.Path(f"{seen}.{script}").read_text()
    except OSError:
        return None
    return text.removesuffix("\n").split("\n") if text else []


def beside_every_ledger(probe, counter, tag, stage, script, title, launch, check, path=None, origin=None):
    first = ""
    failed = ""
    for planter in (plant_ledger, plant_ticked_ledger, plant_done_ledger):
        counter[0] += 1
        tree = probe.root / f"{tag}-{counter[0]}-tree"
        seen = probe.root / f"{tag}-{counter[0]}-seen"
        (tree / ".tdd").mkdir(parents=True)
        planter(tree, title)
        if origin is not None:
            note_launch(probe, *origin, tree)
        err, _, _ = run_staged(stage, seen, tree, launch, "<not run>", path)
        rec = recorded_arguments(seen, script)
        failed = f"{script}.sh was never run " if rec is None else check(rec)
        if not failed:
            break
        if not first:
            first = f"{failed}(the typing shell said: {flat(err)})"
    return failed, first


def scan_conductor_titles(probe):
    title = EXPANDING_STEP
    md_lines = SKILL.read_text().split("\n")
    hits = [(n, line) for n, line in numbered_lines(CONDUCTOR_CALLEE.pattern) if not line.startswith("- `")]
    if not hits:
        probe.problems.append(f"{SKILL_MD} has no line launching the conductor's own marks, preserve-attempt.sh or tick calls — the launch this case is about could not be found")
        return
    stage, _, _ = stage_recorder(probe, "conductor-title", *CONDUCTOR_CALLEES)
    bin_dir = probe.root / "conductor-title-bin"
    bin_dir.mkdir()
    write_executable(bin_dir / "gh", GH_STUB % CRITERION_TEXT)
    counter = [0]
    for lineno, text in hits:
        script = CONDUCTOR_CALLEE.search(text).group(1)
        cmd = conductor_command(md_lines, lineno, script)
        if script == "event" and "VERI_STEP" not in cmd and "anchor=" not in cmd:
            continue
        launch = fill_title(cmd, title)
        expected = CRITERION_TEXT if script == "tick-issue-criterion" else title

        def check(rec, cmd=cmd, script=script, expected=expected):
            failed = ""
            if "VERI_STEP" in cmd and rec[0] != title:
                failed += f"VERI_STEP=<{rec[0]}> "
            if "anchor=" in cmd and f"anchor={title}" not in rec[1:]:
                failed += f"no argument anchor=<{title}> "
            if script in ("preserve-attempt", "tick-issue-criterion"):
                want = rec[2] if len(rec) > 2 else "<none>"
            elif script in ("tick-ledger", "clear-refactor-pending"):
                want = rec[-1] if rec else ""
            else:
                want = title
            if want != expected:
                failed += f"title argument <{want}> "
            return failed

        failed, first = beside_every_ledger(probe, counter, "conductor-title", stage, script, title, launch, check,
                                            path=f"{bin_dir}:{os.environ['PATH']}", origin=(lineno, cmd))
        if failed:
            probe.problem(lineno, cmd, f"passes {script}.sh <{expected}>, which arrived as {first} beside every ledger state")


def scan_prompt_titles(probe):
    title = EXPANDING_STEP
    md_lines = SKILL.read_text().split("\n")
    hits = [(n, line) for n, line in numbered_lines(PROMPT_CALLEE.pattern) if not line.startswith("- `")]
    if not hits:
        probe.problems.append(f"{SKILL_MD} has no line launching build-develop-prompt.sh or add-ledger-step.sh — the launch this case is about could not be found")
        return
    stage, _, _ = stage_recorder(probe, "prompt-title", "build-develop-prompt", "add-ledger-step")
    counter = [0]
    for lineno, text in hits:
        script = PROMPT_CALLEE.search(text).group(1)
        cmd = conductor_command(md_lines, lineno, script)
        if f"{script}.sh " not in cmd:
            continue
        launch = fill_title(cmd, title)

        def check(rec, script=script):
            want = "<none>"
            for k in range(1, len(rec) - 1):
                if (script == "build-develop-prompt" and rec[k].endswith("-spec.md")) or \
                        (script == "add-ledger-step" and rec[k] in ("after", "before", "instead-of")):
                    want = rec[k + 1]
                    break
            return "" if want == title else f"title argument <{want}> "

        failed, first = beside_every_ledger(probe, counter, "prompt-title", stage, script, title, launch, check, origin=(lineno, cmd))
        if failed:
            probe.problem(lineno, cmd, f"passes {script}.sh <{title}>, which arrived as {first} beside every ledger state")


def plant_every_step_ticked_ledger(tree, title):
    write_ledger(tree, f"- [x] an earlier step the run finished\n- [x] {title}\n")


def first_line(pattern, source=None):
    hits = numbered_lines(pattern, None if source is None else source.read_text())[:1]
    return hits[0] if hits else (None, None)


def no_launch(probe, shape):
    probe.problems.append(f"{SKILL_MD} has no line launching {shape} — the launch this case is about could not be found")


def take_line(probe, lineno, line, title):
    launch = runnable(line, title)
    if launch is None:
        probe.problem(lineno, line, "names a placeholder this probe cannot supply, so its launch could not be run")
    return launch


def clear_seen(seen):
    seen.unlink(missing_ok=True)
    for path in seen.parent.glob(seen.name + ".*"):
        path.unlink()


def prompt_step_arg(seen):
    rec = recorded_arguments(seen, "build-develop-prompt") or []
    for k in range(1, len(rec) - 1):
        if rec[k].endswith("-spec.md"):
            return rec[k + 1]
    return "<no step argument>"


def mark_step(seen):
    try:
        return pathlib.Path(f"{seen}.event").read_text().split("\n")[0]
    except OSError:
        return "<no mark was made>"


def check_mark_step(probe, lineno, line, seen, title, err, what, shell="launching"):
    got = mark_step(seen)
    if got != title:
        probe.problem(lineno, line, f"marked {what} beside a ledger with every step ticked with VERI_STEP=<{got}>, want the last done step <{title}> (the {shell} shell said: {flat(err)})")


def check_prompt_step(probe, lineno, line, seen, title, err, what):
    want = prompt_step_arg(seen)
    if want != title:
        probe.problem(lineno, line, f"built the {what} prompt beside a ledger with every step ticked, passing build-develop-prompt.sh the step <{want}>, want the last done step <{title}> (the launching shell said: {flat(err)})")


def scan_rebase_verifier_last_done(probe, tag, by_env):
    title = EXPANDING_STEP
    lineno, line = first_line(r"\$S/detach-leaf\.sh .*\$S/supervise\.sh verdict-rebase \$S/run-verdict\.sh")
    if lineno is None:
        no_launch(probe, "verdict-rebase through supervise.sh into run-verdict.sh")
        return
    launch = take_line(probe, lineno, line, title)
    if launch is None:
        return
    stage, seen, tree = stage_recorder(probe, tag)
    plant_every_step_ticked_ledger(tree, title)
    err, got, argv = run_staged(stage, seen, tree, launch, "<no verifier was launched>")
    if by_env and got != title:
        probe.problem(lineno, line, f"launched verdict-rebase beside a ledger with every step ticked, whose verifier saw VERI_STEP=<{got}>, want the last done step <{title}> (the launching shell said: {flat(err)})")
    if not by_env and argv != title:
        probe.problem(lineno, line, f"launched verdict-rebase beside a ledger with every step ticked, whose verifier was handed --step <{argv}>, want the last done step <{title}> (the launching shell said: {flat(err)})")


def scan_develop_last_done(probe, phase, source=None):
    title = EXPANDING_STEP
    stage, seen, tree = stage_recorder(probe, f"develop-{phase}-last-done", "build-develop-prompt")
    plant_every_step_ticked_ledger(tree, title)
    lineno, line = first_line(rf"\$S/build-develop-prompt\.sh {phase} .*> \.tdd/develop-{phase}\.prompt", source)
    if lineno is None:
        no_launch(probe, f"build-develop-prompt.sh {phase} into .tdd/develop-{phase}.prompt")
    else:
        line = line.replace("<branch>", "tdd/probe-branch").replace("<remote-sha>", "0123abc")
        launch = take_line(probe, lineno, line, title)
        if launch is not None:
            err, _, _ = run_staged(stage, seen, tree, launch, "<no prompt was built>")
            check_prompt_step(probe, lineno, line, seen, title, err, f"develop-{phase}")
    lineno, line = first_line(rf"\$S/detach-leaf\.sh .*\$S/supervise\.sh develop-{phase} \$S/run-leaf\.sh", source)
    if lineno is None:
        no_launch(probe, f"develop-{phase} through supervise.sh into run-leaf.sh")
        return
    launch = take_line(probe, lineno, line, title)
    if launch is None:
        return
    err, got, _ = run_staged(stage, seen, tree, launch, "<no leaf was launched>")
    if got != title:
        probe.problem(lineno, line, f"launched develop-{phase} beside a ledger with every step ticked, whose leaf saw VERI_STEP=<{got}>, want the last done step <{title}> (the launching shell said: {flat(err)})")


def scan_revise_last_done(probe):
    title = EXPANDING_STEP
    stage, seen, tree = stage_recorder(probe, "revise-last-done", "build-develop-prompt", "event")
    plant_every_step_ticked_ledger(tree, title)
    patterns = {
        "mark": r"\$S/event\.sh revise budget=",
        "prompt": r"\$S/build-develop-prompt\.sh revise <phase> .*> \.tdd/revise-<phase>-<k>\.prompt",
        "leaf": r"\$S/detach-leaf\.sh .*\$S/supervise\.sh revise-<phase>-<k> \$S/run-leaf\.sh",
        "re-verify": r"\$S/detach-leaf\.sh .*\$S/supervise\.sh verdict-<phase> \$S/run-verdict\.sh --step .* --fast-cmd ",
    }
    for which, pattern in patterns.items():
        lineno, line = first_line(pattern, REVISE_MD)
        if lineno is None:
            no_launch(probe, f"the revise loop's {which} line")
            continue
        line = line.replace("<REVISE_BUDGET>", "3")
        launch = take_line(probe, lineno, line, title)
        if launch is None:
            continue
        clear_seen(seen)
        err, got, _ = run_staged(stage, seen, tree, launch, "<no leaf was launched>")
        if which == "mark":
            check_mark_step(probe, lineno, line, seen, title, err, "the revise event")
        elif which == "prompt":
            check_prompt_step(probe, lineno, line, seen, title, err, "revise")
        elif got != title:
            probe.problem(lineno, line, f"launched the revise loop's {which} line beside a ledger with every step ticked, whose leaf saw VERI_STEP=<{got}>, want the last done step <{title}> (the launching shell said: {flat(err)})")


def scan_revise_diff_last_done(probe):
    title = EXPANDING_STEP
    lineno, line = first_line(r"\$S/build-develop-prompt\.sh revise diff .*> \.tdd/revise-diff-<k>\.prompt", REVISE_MD)
    if lineno is None:
        no_launch(probe, "build-develop-prompt.sh revise diff into .tdd/revise-diff-<k>.prompt")
        return
    launch = take_line(probe, lineno, line, title)
    if launch is None:
        return
    stage, seen, tree = stage_recorder(probe, "revise-diff-last-done", "build-develop-prompt")
    plant_every_step_ticked_ledger(tree, title)
    err, _, _ = run_staged(stage, seen, tree, launch, "<no prompt was built>")
    check_prompt_step(probe, lineno, line, seen, title, err, "revise diff")


def scan_exhausted_last_done(probe):
    title = EXPANDING_STEP
    stage, seen, tree = stage_recorder(probe, "exhausted-last-done", "build-develop-prompt", "event")
    plant_every_step_ticked_ledger(tree, title)
    patterns = {
        "prompt": r"\$S/build-develop-prompt\.sh exhausted .*> \.tdd/develop-exhausted\.prompt",
        "leaf": r"\$S/detach-leaf\.sh .*\$S/supervise\.sh develop-exhausted \$S/run-leaf\.sh",
        "mark": r"\$S/event\.sh step-escalated anchor=",
    }
    for which, pattern in patterns.items():
        lineno, line = first_line(pattern, REVISE_MD)
        if lineno is None:
            no_launch(probe, f"the revise-exhausted path's {which} line")
            continue
        launch = take_line(probe, lineno, line, title)
        if launch is None:
            continue
        clear_seen(seen)
        err, got, _ = run_staged(stage, seen, tree, launch, "<no leaf was launched>")
        if which == "prompt":
            check_prompt_step(probe, lineno, line, seen, title, err, "exhausted")
        elif which == "leaf":
            if got != title:
                probe.problem(lineno, line, f"launched develop-exhausted beside a ledger with every step ticked, whose leaf saw VERI_STEP=<{got}>, want the last done step <{title}> (the launching shell said: {flat(err)})")
        else:
            check_mark_step(probe, lineno, line, seen, title, err, "step-escalated")


def scan_bail_last_done(probe):
    title = EXPANDING_STEP
    stage, seen, tree = stage_recorder(probe, "bail-last-done", "preserve-attempt", "event")
    plant_every_step_ticked_ledger(tree, title)
    patterns = {
        "preserve": r"\$S/preserve-attempt\.sh <n> .* <phase> <attempt> bail$",
        "mark": r"\$S/event\.sh bail cause=<cause>",
    }
    for which, pattern in patterns.items():
        lineno, line = first_line(pattern, BAIL)
        if lineno is None:
            no_launch(probe, f"Bailing's {which} line")
            continue
        line = line.replace("<attempt>", "1").replace("<cause>", "suite-red")
        launch = take_line(probe, lineno, line, title)
        if launch is None:
            continue
        clear_seen(seen)
        err, _, _ = run_staged(stage, seen, tree, launch, "<not run>")
        if which == "preserve":
            rec = recorded_arguments(seen, "preserve-attempt") or []
            got = rec[2] if len(rec) > 2 else "<no step argument>"
            if got != title:
                probe.problem(lineno, line, f"preserved a bailed attempt beside a ledger with every step ticked, passing preserve-attempt.sh the step <{got}>, want the last done step <{title}> (the typing shell said: {flat(err)})")
        else:
            check_mark_step(probe, lineno, line, seen, title, err, "bail", "typing")


def scan_event_mark_last_done(probe, tag, pattern, shape, mark, fills=(), source=None):
    title = EXPANDING_STEP
    stage, seen, tree = stage_recorder(probe, tag, "event")
    plant_every_step_ticked_ledger(tree, title)
    hits = numbered_lines(pattern, None if source is None else source.read_text())[:1]
    lineno, line = hits[0] if hits else (None, None)
    if lineno is None:
        no_launch(probe, shape)
        return
    for placeholder, value in fills:
        line = line.replace(placeholder, value)
    launch = take_line(probe, lineno, line, title)
    if launch is None:
        return
    clear_seen(seen)
    err, _, _ = run_staged(stage, seen, tree, launch, "<not run>")
    check_mark_step(probe, lineno, line, seen, title, err, mark, "typing")


def scan_resume_last_done(probe):
    title = EXPANDING_STEP
    stage, seen, tree = stage_recorder(probe, "resume-last-done", "event")
    plant_every_step_ticked_ledger(tree, title)
    lineno = line = None
    for n, text in enumerate(SKILL.with_name("RESUME.md").read_text().split("\n"), 1):
        found = re.search(r"`VERI_ISSUE=[^`]*\$S/event\.sh resume`", text)
        if found:
            lineno, line = n, found.group(0).replace("`", "")
            break
    if lineno is None:
        no_launch(probe, "Resume's resume mark")
        return
    launch = take_line(probe, lineno, line, title)
    if launch is None:
        return
    clear_seen(seen)
    err, _, _ = run_staged(stage, seen, tree, launch, "<not run>")
    check_mark_step(probe, lineno, line, seen, title, err, "resume", "typing")


def scan_transform_verifier_last_done(probe):
    title = EXPANDING_STEP
    lineno = line = None
    inside = False
    for n, text in enumerate(SKILL.read_text().split("\n"), 1):
        if "one structural pass" in text:
            inside = True
        if re.search(r"^2\. \*\*Mark the PR ready", text):
            inside = False
        if inside and re.search(r"\$S/detach-leaf\.sh .*\$S/supervise\.sh verdict-transform \$S/run-verdict\.sh", text):
            lineno, line = n, text
            break
    if lineno is None:
        no_launch(probe, "verdict-transform through supervise.sh into run-verdict.sh in the structural pass")
        return
    line = line.replace("<base-sha>", "89abcde")
    launch = take_line(probe, lineno, line, title)
    if launch is None:
        return
    stage, seen, tree = stage_recorder(probe, "transform-verifier-last-done")
    plant_every_step_ticked_ledger(tree, title)
    err, _, argv = run_staged(stage, seen, tree, launch, "<no verifier was launched>")
    if argv != title:
        probe.problem(lineno, line, f"launched verdict-transform beside a ledger with every step ticked, whose verifier was handed --step <{argv}>, want the last done step <{title}> (the launching shell said: {flat(err)})")


def scan_phase_verifiers_last_done(probe):
    title = EXPANDING_STEP
    patterns = {
        "general": r"\$S/supervise\.sh verdict-<phase> \$S/run-verdict\.sh --step .* <phase> … >",
        "revise": r"\$S/supervise\.sh verdict-<phase> \$S/run-verdict\.sh --step .* --fast-cmd .<fast-cmd>. <phase> ",
    }
    for which, pattern in patterns.items():
        lineno, line = first_line(r"\$S/detach-leaf\.sh .*" + pattern, REVISE_MD if which == "revise" else None)
        if lineno is None:
            no_launch(probe, f"the {which} verdict-<phase> shape through supervise.sh into run-verdict.sh")
            continue
        launch = take_line(probe, lineno, line, title)
        if launch is None:
            continue
        stage, seen, tree = stage_recorder(probe, f"phase-verifier-last-done-{which}")
        plant_every_step_ticked_ledger(tree, title)
        err, _, argv = run_staged(stage, seen, tree, launch, "<no verifier was launched>")
        if argv != title:
            probe.problem(lineno, line, f"launched the {which} verdict-<phase> line beside a ledger with every step ticked, whose verifier was handed --step <{argv}>, want the last done step <{title}> (the launching shell said: {flat(err)})")


@pytest.fixture(scope="module")
def scripts_before():
    return scripts_fingerprint()


@pytest.fixture(scope="module")
def shared_stages(tmp_path_factory):
    return Shared(tmp_path_factory.mktemp("stages"))


@pytest.fixture(scope="module")
def scans(tmp_path_factory, shared_stages):
    return launch_scans_once(tmp_path_factory.mktemp("launch-scans"), shared_stages)


@pytest.fixture
def probe(tmp_path, scripts_before, shared_stages):
    return Probe(tmp_path, shared_stages)


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(900)
def test_every_leaf_skill_md_launches_through_supervise_sh_sees_the_runs_test_command_as_veri_test_cmd(scans):
    assert scans.developer == []


@pytest.mark.process("SKILL.md launch line through verify.sh")
@pytest.mark.timeout(900)
def test_every_verifier_skill_md_launches_through_verify_sh_sees_the_runs_test_command_as_veri_test_cmd(scans):
    assert scans.verifier == []


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(900)
def test_every_leaf_skill_md_launches_leaves_events_carrying_the_runs_issue_and_step(probe, scans):
    trees = launched_trees(scans)
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
@pytest.mark.timeout(900)
def test_every_leaf_skill_md_launches_with_veri_step_set_sees_the_runs_step_as_veri_step(probe, scans):
    trees = launched_trees(scans)
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


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(120)
def test_a_step_title_carrying_an_apostrophe_reaches_the_leaf_skill_md_launches_with_it_intact(probe):
    scan_step_title(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(120)
def test_a_step_title_carrying_a_dollar_sign_a_backtick_and_a_double_quote_reaches_the_leaf_skill_md_launches_with_it_byte_identical_437(probe):
    scan_step_title(probe, EXPANDING_STEP, "expanding-step-title")

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(120)
def test_a_step_title_carrying_a_dollar_sign_a_backtick_and_a_double_quote_reaches_the_develop_refactor_leaf_skill_md_launches_after_the_step_is_ticked_byte_identical_437(probe):
    scan_step_title(probe, EXPANDING_STEP, "expanding-step-title-refactor", "develop-refactor", plant_ticked_ledger)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(120)
def test_a_step_title_carrying_a_dollar_sign_a_backtick_and_a_double_quote_reaches_the_verifier_skill_md_launches_byte_identical_in_veri_step_and_in_step_437(probe):
    scan_verdict_step_title(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_a_step_title_carrying_a_dollar_sign_a_backtick_and_a_double_quote_reaches_every_other_developer_and_verifier_leaf_skill_md_launches_with_it_byte_identical_437(probe):
    scan_every_step_title(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_every_leaf_and_verifier_launch_line_in_skill_md_reads_the_step_through_ledger_steps_sh_current_and_a_title_carrying_a_dollar_sign_a_backtick_and_a_double_quote_reaches_veri_step_and_step_byte_identical_682(probe):
    scan_current_step_title(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md conductor line through event.sh, preserve-attempt.sh and the tick scripts")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_a_step_title_carrying_a_dollar_sign_a_backtick_and_a_double_quote_reaches_every_event_sh_mark_preserve_attempt_sh_call_and_tick_fragment_the_conductor_types_from_skill_md_byte_identical_437(probe):
    scan_conductor_titles(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md conductor line through build-develop-prompt.sh and add-ledger-step.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_a_step_title_carrying_a_dollar_sign_a_backtick_and_a_double_quote_reaches_every_build_develop_prompt_sh_prompt_and_add_ledger_step_sh_anchor_the_conductor_types_from_skill_md_byte_identical_437(probe):
    scan_prompt_titles(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_753_the_verify_rebase_launch_line_in_skill_md_run_with_every_ledger_step_ticked_hands_its_verifier_the_last_done_steps_text_as_step_byte_identical(probe):
    scan_rebase_verifier_last_done(probe, "rebase-verifier-last-done", False)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_907_the_draft_pr_steps_verdict_rebase_launch_line_in_skill_md_run_with_every_ledger_step_ticked_gives_its_verifier_the_last_done_steps_text_as_veri_step_byte_identical(probe):
    scan_rebase_verifier_last_done(probe, "rebase-verifier-env-last-done", True)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through build-develop-prompt.sh and detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_892_the_draft_pr_steps_develop_rebase_block_in_skill_md_run_with_every_ledger_step_ticked_passes_build_develop_prompt_sh_rebase_and_the_leafs_veri_step_the_last_done_steps_text_byte_identical(probe):
    scan_develop_last_done(probe, "rebase")

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through build-develop-prompt.sh and detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_892_the_develop_reconcile_block_of_reconciling_a_rejected_push_in_skill_md_run_with_every_ledger_step_ticked_passes_build_develop_prompt_sh_reconcile_and_the_leafs_veri_step_the_last_done_steps_text_byte_identical(probe):
    scan_develop_last_done(probe, "reconcile", source=RECONCILE)

    assert probe.problems == []


@pytest.mark.process("SKILL.md revise loop through event.sh, build-develop-prompt.sh and detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_892_the_revise_loop_of_revising_on_a_reject_in_skill_md_run_with_every_ledger_step_ticked_passes_the_revise_marks_veri_step_the_revise_prompt_the_revise_leafs_veri_step_and_the_re_verify_launchs_veri_step_the_last_done_steps_text_byte_identical(probe):
    scan_revise_last_done(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md conductor line through build-develop-prompt.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_907_the_revise_diff_prompt_line_of_revising_on_a_reject_in_skill_md_run_with_every_ledger_step_ticked_passes_build_develop_prompt_sh_revise_diff_the_last_done_steps_text_byte_identical(probe):
    scan_revise_diff_last_done(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md revise-exhausted path through event.sh, build-develop-prompt.sh and detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_907_the_revise_exhausted_path_of_revising_on_a_reject_in_skill_md_run_with_every_ledger_step_ticked_passes_build_develop_prompt_sh_exhausted_the_develop_exhausted_leafs_veri_step_and_the_step_escalated_marks_veri_step_the_last_done_steps_text_byte_identical(probe):
    scan_exhausted_last_done(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md conductor line through event.sh and preserve-attempt.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_907_bailing_in_skill_md_run_with_every_ledger_step_ticked_passes_preserve_attempt_sh_and_the_bail_marks_veri_step_the_last_done_steps_text_byte_identical(probe):
    scan_bail_last_done(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md conductor line through event.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_907_stopping_in_skill_md_run_with_every_ledger_step_ticked_gives_the_stop_marks_veri_step_the_last_done_steps_text_byte_identical(probe):
    scan_event_mark_last_done(probe, "stop-last-done", r"\$S/event\.sh stop mode=<mode> at=<at>",
                              "Stopping's stop mark", "stop", (("<mode>", "at-ledger"), ("<at>", "step-done")), source=STOPPING)

    assert probe.problems == []


@pytest.mark.process("SKILL.md conductor line through event.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_907_resume_in_skill_md_run_with_every_ledger_step_ticked_gives_the_resume_marks_veri_step_the_last_done_steps_text_byte_identical(probe):
    scan_resume_last_done(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_753_the_structural_pass_in_skill_md_spells_the_transform_verifiers_launch_line_and_run_with_every_ledger_step_ticked_it_hands_its_verifier_the_last_done_steps_text_as_step_byte_identical(probe):
    scan_transform_verifier_last_done(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(300)
def test_753_the_general_verifier_launch_shape_and_the_revise_loops_re_verify_line_in_skill_md_run_with_every_ledger_step_ticked_hand_their_verifier_the_last_done_steps_text_as_step_byte_identical(probe):
    scan_phase_verifiers_last_done(probe)

    assert probe.problems == []


ANSWER_CEILING = 15

LATE_COMPLETION_DETACH = """#!/bin/sh
printf '%s\\n' "${VERI_TEST_CMD-<unset>}" > "$SEEN"
printf '%s\\n' "$$" > ".tdd/$2.pid"
( sleep 1; printf '0\\n' > ".tdd/$2.exit" ) </dev/null >/dev/null 2>&1 &
"""

NAMING_FIXTURE = (
    "VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh fixture-good-1 $S/run-leaf.sh .tdd/fixture-good-1.prompt",
    "VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh fixture-bad $S/run-leaf.sh .tdd/fixture-bad.prompt",
    "VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh fixture-good-2 $S/run-leaf.sh .tdd/fixture-good-2.prompt",
)


def only_complaint_about(probe, needle, asked):
    got = list(probe.problems)
    probe.problems.clear()
    if len(got) != 1 or needle not in got[0]:
        probe.problems.append(f"{asked} reported: {' '.join(got) or '<nothing>'}")


def developer_launch_fixture(probe, tag):
    lineno = f"{tag}-1"
    leaf = f"fixture-{tag}"
    prompt = f".tdd/{leaf}.prompt"
    line = f"VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh {leaf} $S/run-leaf.sh {prompt}"
    launch = runnable(line)
    assert launch is not None, f"the {tag} fixture names a placeholder this probe cannot supply"
    return lineno, line, launch, leaf, prompt


def late_stage(probe, tag, script):
    stage = probe.root / f"{tag}-scripts"
    stage.mkdir()
    write_executable(stage / "detach-leaf.sh", script)
    return stage


def scripts_fingerprint():
    found = {}
    paths = list(SCRIPTS.glob("*.sh")) + [p for sub in ("lib", "prompts") for p in (SCRIPTS / sub).rglob("*")]
    for path in sorted(paths):
        if path.is_file() and not path.is_symlink():
            found[str(path.relative_to(SCRIPTS))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


def scan_reverted_step_title(probe):
    scan_step_title(probe, EXPANDING_STEP, "reverted-431-as-is")
    if probe.problems:
        probe.problems[:] = ["the document's own develop-red line already fails the probe, so its #431 revert shows nothing: " + " ".join(probe.problems)]
        return
    lines = SKILL.read_text().split("\n")
    n = numbered_lines(r"\$S/supervise\.sh develop-red \$S/run-leaf\.sh")[0][0]
    lines[n - 1] = re.sub(r"VERI_STEP=.* \$S/detach-leaf\.sh", lambda _: 'VERI_STEP="<STEP>" $S/detach-leaf.sh', lines[n - 1], count=1)
    scan_step_title(probe, EXPANDING_STEP, "reverted-431", text="\n".join(lines))
    only_complaint_about(probe, "whose leaf saw VERI_STEP=", "the develop-red line put back to #431's hand-typed VERI_STEP=\"<STEP>\"")


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(120)
def test_a_single_broken_launch_line_is_reported_by_name_alone_while_unrelated_lines_report_nothing(probe):
    for i, line in enumerate(NAMING_FIXTURE, 1):
        launch = runnable(line)
        assert launch is not None
        check_developer_launch(probe, f"fixture-naming-{i}", line, launch)
    only_complaint_about(probe, "fixture-bad", "the fixture's three launches (only the middle one broken)")

    assert probe.problems == []


def test_report_s_fail_line_its_indented_problem_line_and_the_count_line_keep_their_shape(tmp_path):
    probe = Probe(tmp_path)
    probe.problem("999", "sample line text", "sample problem")

    assert probe.problems == ["skills/tdd/SKILL.md:999 sample problem:sample line text"]


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(120)
def test_a_launch_writing_no_completion_file_under_the_derived_leaf_name_is_reported_naming_that_line(probe):
    lineno, line, launch, leaf, prompt = developer_launch_fixture(probe, "wrong-leaf-name")
    expect_sentinel(probe, lineno, line, f"{leaf}-no-such-leaf", launch, prompt)
    only_complaint_about(probe, line, "a launch whose leaf name no completion file is written under")

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(120)
def test_a_derived_leaf_name_no_launch_writes_is_answered_once_its_supervisor_is_gone_not_at_the_end_of_the_wait_budget(probe):
    lineno, line, launch, leaf, prompt = developer_launch_fixture(probe, "answer-latency")
    started = time.monotonic()
    launched_test_cmd(probe, lineno, line, f"{leaf}-no-such-leaf", launch, prompt)
    elapsed = time.monotonic() - started
    if elapsed >= ANSWER_CEILING:
        probe.problems.append(f"a launch whose derived leaf name no completion file is written under was answered after {int(elapsed)}s, want under {ANSWER_CEILING}s: the wait ran on past the supervisor that had already exited")

    assert probe.problems == []


@pytest.mark.process("the stage of linked scripts SKILL.md launch lines run against")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
def test_a_stage_reaches_every_script_it_does_not_replace_by_a_link_to_the_script_under_test_never_a_copy(probe):
    stage, _, _ = stage_recorder(probe, "stage-links")
    for script in sorted(SCRIPTS.glob("*.sh")) + sorted((SCRIPTS / "lib").glob("*")):
        name = str(script.relative_to(SCRIPTS))
        if name == "detach-leaf.sh":
            continue
        if not ((stage / name).exists() and os.path.samefile(stage / name, script)):
            probe.problems.append(f"the stage reaches {name} by a copy, want a link to {script}")

    assert probe.problems == []


@pytest.mark.process("the stage of linked scripts SKILL.md launch lines run against")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
def test_each_distinct_recorder_is_written_once_per_suite_run_and_every_stage_reaches_it_by_a_link_its_per_stage_difference_only_seen(probe):
    titled = ("event", "build-develop-prompt")
    first = None
    for tag in ("a", "b"):
        stage, _, tree = stage_recorder(probe, f"shared-recorders-{tag}", *titled)
        first = first or stage
    for name in ("detach-leaf", *titled):
        if not ((first / f"{name}.sh").is_symlink() and (stage / f"{name}.sh").is_symlink()):
            probe.problems.append(f"{name}.sh: a stage holds its own recorder, want a link to the one written once per suite run")
        if not os.path.samefile(first / f"{name}.sh", stage / f"{name}.sh"):
            probe.problems.append(f"{name}.sh: two stages reach different recorders, want both linked to one")
        if os.path.samefile(stage / f"{name}.sh", SCRIPTS / f"{name}.sh"):
            probe.problems.append(f"{name}.sh: the stage reaches the script under test, want the recorder")
        text = (stage / f"{name}.sh").read_text()
        if "$SEEN" not in text or str(first) in text or str(stage) in text:
            probe.problems.append(f"{name}.sh: the recorder differs per stage by more than $SEEN")

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(120)
def test_the_step_title_probe_with_one_title_carrying_a_dollar_sign_a_backtick_and_a_double_quote_goes_red_on_a_launch_line_put_back_to_431_s_hand_typed_double_quotes_437(probe):
    scan_reverted_step_title(probe)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(120)
def test_a_launch_whose_completion_file_lands_after_its_last_recorded_pid_has_exited_is_reported_by_what_its_leaf_saw_457(probe):
    lineno, line, launch, leaf, prompt = developer_launch_fixture(probe, "late-completion")
    stage = late_stage(probe, "late-completion", LATE_COMPLETION_DETACH)
    expect_sentinel(probe, lineno, line, leaf, launch, prompt, scripts=stage)

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through supervise.sh")
@pytest.mark.timeout(120)
def test_a_launch_whose_leaf_name_no_completion_file_is_written_under_is_still_reported_as_a_naming_fault_well_inside_the_wait_budget_when_its_own_file_lands_late_457(probe):
    lineno, line, launch, leaf, prompt = developer_launch_fixture(probe, "late-wrong-leaf-name")
    stage = late_stage(probe, "late-wrong-leaf-name", LATE_COMPLETION_DETACH)
    want = f"<no completion file under leaf {leaf}-no-such-leaf>"
    started = time.monotonic()
    got = launched_test_cmd(probe, lineno, line, f"{leaf}-no-such-leaf", launch, prompt, scripts=stage)
    elapsed = time.monotonic() - started
    if got != want or elapsed >= ANSWER_CEILING:
        probe.problem(lineno, line, f"launches under a leaf name no completion file is written under, reported as <{got}> after {int(elapsed)}s, want <{want}> under {ANSWER_CEILING}s")

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through a detach-leaf.sh that reaches no supervisor")
@pytest.mark.timeout(120)
def test_a_launch_line_that_reaches_no_supervisor_at_all_is_reported_as_no_leaf_ran_457(probe):
    lineno, line, launch, leaf, prompt = developer_launch_fixture(probe, "no-leaf-ran")
    stage = late_stage(probe, "no-leaf-ran", "#!/bin/sh\nexit 0\n")
    now = [0.0]

    def jump(_seconds):
        now[0] += 3600

    got = launched_test_cmd(probe, lineno, line, leaf, launch, prompt, scripts=stage, clock=lambda: now[0], sleep=jump)
    if got != "<no leaf ran>":
        probe.problem(lineno, line, f"launches nothing, reported as <{got}>, want <no leaf ran>")

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch lines through supervise.sh and detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(600)
def test_no_launch_line_in_skill_md_is_launched_more_than_once_per_ledger_shape_the_suite_plants(probe, scans):
    probe.launches.extend(scans.probe.launches)
    scan_step_title(probe)
    scan_step_title(probe, EXPANDING_STEP, "record-develop-red")
    scan_step_title(probe, EXPANDING_STEP, "record-develop-refactor", leaf="develop-refactor", planter=plant_ticked_ledger)
    scan_verdict_step_title(probe)
    scan_every_step_title(probe)
    scan_conductor_titles(probe)
    scan_prompt_titles(probe)
    probe.problems.clear()
    if not probe.launches:
        probe.problems.append("no launch was recorded")
    for (lineno, shape, line), count in collections.Counter(probe.launches).items():
        if count > 1:
            probe.problem(lineno, line, f"launched {count} times beside a ledger of shape {shape}, want at most once")

    assert probe.problems == []


@pytest.mark.process("SKILL.md launch line through detach-leaf.sh")
@pytest.mark.tree_audit("the scripts directory the stage links every script of")
@pytest.mark.timeout(120)
def test_a_recorder_replaces_a_stage_s_link_rather_than_writing_through_it_so_the_suite_leaves_every_script_under_skills_tdd_scripts_byte_identical(probe, scripts_before):
    before = scripts_before
    stage, _, _ = stage_recorder(probe, "untouched", "event", "build-develop-prompt")
    scan_step_title(probe, EXPANDING_STEP, "untouched-run")
    after = scripts_fingerprint()
    for name in sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name)):
        probe.problems.append(f"{name} changed while the suite ran, want every script under test byte-identical")

    assert before and probe.problems == []
