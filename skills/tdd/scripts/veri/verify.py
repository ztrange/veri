"""verify.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

import build_verify_prompt
import entry
import event
import leaf_tree_guard
import parse_verdict
import preserve_attempt
import renamed_case
import replaces_case_survivors
import run_dir
import tunables
from case_reader import is_js_test_file
from entry import write
from js_tests import CALL
from leaf_model import env_value, resolve
from leaf_role import leaf_role
from paths import SCRIPTS
from run_verdict import takes_a_value


def write_ban_command(python, module):
    """The write-ban hook's shell command: `python module`, any non-zero status of it turned into 2, the only status
    with which the CLI blocks a call, so a missing interpreter (127) or a crash at import (1) blocks too."""
    return shlex.join([python, module]) + " || exit 2"


WRITE_BAN = {"PreToolUse": [{"matcher": "Write|Edit|MultiEdit|NotebookEdit", "hooks": [
    {"type": "command",
     "command": write_ban_command(sys.executable, os.path.join(SCRIPTS, "veri", "verifier_write_ban.py"))}]}]}
LEAF_ARGS = ["--permission-mode", "bypassPermissions", "--settings", json.dumps({"hooks": WRITE_BAN})]
USAGE = ("usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>']"
         " [--supersede-base <sha>|--frozen-edit <sha>] [--step-green <sha>] --branch-base <sha> <phase> <issue-spec-file>"
         " <test-path> [<target-test-id>]"
         "\n       verify.sh --fast-cmd '<CMD>' --branch-base <sha> branch <issue-spec-file>")


def is_echo_flag(value):
    return len(value) > 1 and value[0] == "-" and all(c in "neE" for c in value[1:])


def sibling(name):
    return os.path.join(SCRIPTS, name)


def mark(role, *words):
    return event.mark("", event.context(role), words[0], words[1:])


def preserve(issue, step, leaf, attempt, outcome):
    if preserve_attempt.preserve(".", issue, step, leaf, attempt, outcome):
        write(sys.stderr, "verify: could not preserve the %s attempt (issue %s step %s %s attempt %s)"
               % (outcome, issue, step, leaf, attempt))


def unreadable_gitconfig(unreadable):
    write(sys.stderr, "verify: cannot read the global git config %s: %s" % (unreadable.path, unreadable.strerror))
    return 2


def save_diff(leaf, tree_before, tree_after):
    diff = leaf_tree_guard.git("diff", "--binary", "--no-ext-diff", "--no-textconv", "--no-color",
               "--src-prefix=a/", "--dst-prefix=b/", "-U3", tree_before, tree_after)
    path = run_dir.run_file("", "%s.diff" % leaf)
    if diff.returncode == 0 and not diff.stdout:
        return None
    try:
        if diff.returncode != 0:
            raise OSError
        with open(path, "wb") as saved:
            saved.write(diff.stdout)
    except OSError:
        try:
            os.remove(path)
        except OSError:
            pass
        write(sys.stdout, "diff could not be saved to %s" % path)
        return None
    return path


def refuse_modified(what, leaf, paths, diff=None):
    write(sys.stdout, "verifier leaf modified %s — verdict not accepted"
           " (see .tdd/%s.log); changed:" % (what, leaf))
    if diff:
        write(sys.stdout, "diff saved to %s" % diff)
    write(sys.stdout, "\n".join(paths))
    return 2


def leaf_args(words):
    if not words:
        return LEAF_ARGS
    return [path for word in words.split()
            for path in (sorted(glob.glob(word)) or [word])]


CASE_PATTERNS = (
    ("_test.go", r"^func[ \t]+(Test\w+)"),
)
JS_CASE_PATTERN = r"^[ \t]*" + CALL + r"([\"'`])(.+?)\1"
PY_CASE_PATTERN = r"^[ \t]*(?:async[ \t]+)?def[ \t]+(test_\w+)"


def case_pattern(name):
    for suffix, pattern in CASE_PATTERNS:
        if name.endswith(suffix):
            return pattern
    if is_js_test_file(name):
        return JS_CASE_PATTERN
    if name.startswith("test_") and name.endswith(".py"):
        return PY_CASE_PATTERN
    return None


def pytest_cases(sha):
    listed = leaf_tree_guard.git("ls-tree", "-r", "--name-only", sha)
    if listed.returncode != 0:
        return None
    cases = set()
    for path in listed.stdout.decode().splitlines():
        pattern = case_pattern(path.rsplit("/", 1)[-1])
        if pattern is None:
            continue
        shown = leaf_tree_guard.git("show", "%s:%s" % (sha, path))
        if shown.returncode != 0:
            return None
        for found in re.finditer(pattern, shown.stdout.decode(), re.M):
            cases.add((path, found.group(found.lastindex)))
    return cases


def deleted_cases(branch_base, step_base, tip="HEAD"):
    before, middle, after = (pytest_cases(sha) for sha in (branch_base, step_base, tip))
    if None in (before, middle, after):
        return None
    kept = {case for _, case in after}
    taken = {other for _, other in middle}
    return sorted(case for case in sorted(middle - before)
                  if case[1] not in kept and not was_renamed(case, step_base, taken, tip))


def rename_of(find, case, step_base, taken, tip="HEAD"):
    path, name = case
    old = leaf_tree_guard.git("show", "%s:%s" % (step_base, path))
    new = leaf_tree_guard.git("show", "%s:%s" % (tip, path))
    return find(name, old.stdout.decode(), new.stdout.decode(), taken)


def was_renamed(case, step_base, taken, tip="HEAD"):
    return rename_of(renamed_case.renamed_to, case, step_base, taken, tip) is not None


def changed_rename(case, step_base, taken, tip="HEAD"):
    return rename_of(renamed_case.renamed_and_changed_to, case, step_base, taken, tip)


def added_markers(onto):
    log = leaf_tree_guard.git("log", "-p", "-U0", "--no-color", "--no-ext-diff", "--format=commit %H", onto + "..HEAD")
    found, sha, path = [], None, None
    for line in log.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith("commit "):
            sha = line[7:]
        elif line.startswith("+++ "):
            path = line[4:].removeprefix("b/")
        elif line.startswith(("+<<<<<<< ", "+>>>>>>> ")):
            found.append((sha, path))
    return found


def passes_in(gate, cwd):
    done = leaf_tree_guard.start(["sh", "-c", gate], cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
    return done.returncode == 0, done.stdout.decode("utf-8", "replace")


def fails_at_head(gate, output):
    scratch = tempfile.mkdtemp(prefix="veri-head-")
    try:
        leaf_tree_guard.git("worktree", "add", "--detach", scratch + "/tree", "HEAD~1")
        try:
            passed, before_output = passes_in(gate, scratch + "/tree")
            return not passed and before_output == output
        finally:
            leaf_tree_guard.git("worktree", "remove", "--force", scratch + "/tree")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def red_gate_failure():
    for gate in (g.strip() for g in tunables.read("VERI_TEST_CMD").split("&&")[:-1]):
        passed, output = passes_in(gate, ".")
        if not passed:
            if fails_at_head(gate, output):
                return "verify: %s is red before the Red (a pre-existing red suite, not the Red's fault)" % gate
            return "GATE: %s fails on the Red's tree: %s" % (gate, output.rstrip().rsplit("\n", 1)[-1].strip())
    return None


def diff_gate(words, options):
    """The exit code when the diff step deleted or renamed-and-changed an earlier test case, else None."""
    if leaf_tree_guard.git("rev-parse", "--git-dir").returncode:
        return None
    tip = "HEAD"
    if options["--supersede-base"]:
        tip = leaf_tree_guard.in_temp_index("write-tree")
    if options["--frozen-edit"]:
        tip = options["--frozen-edit"]
    branch, step_base = options["--branch-base"], words[2]
    deleted = deleted_cases(branch, step_base, tip)
    if deleted is None:
        return entry.refuse("verify: cannot read the test files at %s, %s or HEAD" % (branch, step_base), usage=USAGE)
    if deleted:
        taken = {other for _, other in pytest_cases(step_base)}
        changed = [(case, changed_rename(case, step_base, taken, tip)) for case in deleted]
        pairs = [(case, other) for case, other in changed if other]
        if pairs:
            write(sys.stdout, "step renamed and changed test cases, so the step must be split: "
                   + ", ".join("%s::%s -> %s" % (case + (other,)) for case, other in pairs))
            return 1
        write(sys.stdout, "step deleted test cases an earlier step added: "
               + ", ".join("%s::%s" % case for case in deleted))
        return 1
    return None


def rebase_gate(words, options):
    """2 when tracked files hold uncommitted changes or git status fails, 1 when the rebase committed conflict markers, else None."""
    if leaf_tree_guard.git("rev-parse", "--git-dir").returncode:
        return None
    status = leaf_tree_guard.git("status", "--porcelain", "--untracked-files=no")
    if status.returncode:
        write(sys.stderr, "verify: git status failed (exit %d), so whether the tree holds uncommitted changes "
              "to tracked files is unknown" % status.returncode)
        return 2
    dirty = [line[3:] for line in os.fsdecode(status.stdout).splitlines() if line.strip()]
    if dirty:
        write(sys.stderr, "verify: the tree has uncommitted changes to tracked files, "
              "so HEAD is not what the verifier would judge: " + ", ".join(dirty))
        return 2
    marked = added_markers(words[2])
    if marked:
        write(sys.stdout, "rebase committed conflict markers: "
               + ", ".join("%s %s" % pair for pair in marked))
        return 1
    return None


def red_gate(words, options):
    """2 for a refusal of verify's own, 1 for a gate that fails on the Red's tree, else None."""
    failure = red_gate_failure()
    if failure and failure.startswith("verify: "):
        write(sys.stderr, failure)
        return 2
    if failure:
        write(sys.stdout, failure)
        return 1
    return None


# A phase's gate runs before its prompt is written; adding one is one entry.
PHASE_GATES = {"diff": diff_gate, "rebase": rebase_gate, "red": red_gate}


def main(argv):
    options = {"--step": "", "--fast-cmd": "", "--supersede-base": "", "--branch-base": "", "--step-green": "",
               "--frozen-edit": ""}
    words = list(argv)
    while words and takes_a_value(words[0]):
        if len(words) < 2 or not words[1]:
            return entry.refuse("verify: %s needs a value" % words[0], usage=USAGE)
        options[words[0]] = words[1]
        words = words[2:]
    if words[:1] == ["branch"] and len(words) == 2:
        # The branch phase judges the whole branch, so it names no test (build-verify-prompt.sh's own branch form);
        # verify-branch.sh launches it as `branch <issue-spec-file>`, and an empty <test-path> is what the builder takes.
        words = [*words, ""]
    elif len(words) < 3:
        return entry.refuse(usage=USAGE)
    if not build_verify_prompt.HEX_SHA.fullmatch(options["--branch-base"]):
        return entry.refuse("verify: %s needs --branch-base <sha> as 7-40 lowercase hex characters, got '%s'"
                            % (words[0], options["--branch-base"]), usage=USAGE)
    leaf = "verify-" + words[0]
    leaf_words = os.environ.get("VERIFY_LEAF_ARGS")
    effort = tunables.get("VERI_EFFORT_VERIFIER")
    flags = leaf_args(leaf_words)
    if effort and not tunables.parses("VERI_EFFORT_VERIFIER", effort):
        write(sys.stderr, "verify: VERI_EFFORT_VERIFIER is %r, not one of low, medium, high, xhigh or max"
               " — the CLI would ignore it and run at its default effort" % effort)
        return 2
    if effort and any(flag == "--effort" or flag.startswith("--effort=") for flag in flags):
        write(sys.stderr, "verify: VERIFY_LEAF_ARGS carries its own --effort and VERI_EFFORT_VERIFIER is '%s'"
               " — which one the leaf would run at is flag order; unset one of them" % effort)
        return 2
    flags = flags + (["--effort", effort] if effort else [])
    if leaf_words:
        model = resolve(leaf)
        if (model and not is_echo_flag(model) and "--model" in flags
                and (env_value("VERI_MODEL_VERIFIER") or env_value("VERI_MODEL"))):
            write(sys.stderr, "verify: VERIFY_LEAF_ARGS carries its own --model and a role model"
                   " variable resolved '%s' — which one the leaf would run on is flag order;"
                   " unset one of them" % model)
            return 2
    if not all(words[:2 if words[0] == "branch" else 3]):
        return entry.to_contract(build_verify_prompt.refuse())
    if len(words) > 4:
        return entry.to_contract(build_verify_prompt.refuse("build-verify-prompt: too many arguments"))
    # The commit a verifier reads its run lines, and whether it is veri's own tree, at (#4263): the `--branch-base` the
    # conductor recorded (#4375, #4376), never a merge base with a remote-tracking ref a leaf could rewrite.
    base = options["--branch-base"]
    issue = tunables.read("VERI_ISSUE")
    ledger = run_dir.ledger(".", issue) if issue else ""
    code, built = build_verify_prompt.build(options["--step"], options["--fast-cmd"], *words, branch_base=base,
                                            root=event.toplevel() or ".",
                                            ledger=ledger, supersede_base=options["--supersede-base"],
                                            step_green=options["--step-green"],
                                            frozen_edit=options["--frozen-edit"])
    if code:
        return entry.to_contract(code)
    gate = PHASE_GATES.get(words[0])
    refused = gate(words, options) if gate else None
    if refused is not None:
        return refused
    top = event.toplevel()
    run = top if top and top != os.getcwd() else ""
    run_state = os.path.join(run, ".tdd")
    prompt_path = run_dir.run_file(run, "%s.prompt" % leaf)
    os.makedirs(run_state, exist_ok=True)
    with open(prompt_path, "wb") as prompt:
        prompt.write(built.rstrip(b"\n"))
    guard = leaf_tree_guard.snapshot()
    if isinstance(guard, leaf_tree_guard.Unreadable):
        write(sys.stderr, "verify: could not read the tree before the %s leaf; its verdict is not accepted" % leaf)
        return 2
    if isinstance(guard, leaf_tree_guard.ConfigUnreadable):
        return unreadable_gitconfig(guard)
    raw_retries = tunables.get("VERI_NO_VERDICT_RETRIES", unless_empty=True)
    try:
        retries = tunables.tokens(raw_retries)
    except ValueError:
        write(sys.stderr, "verify: VERI_NO_VERDICT_RETRIES must be a non-negative integer,"
               " got '%s'" % raw_retries)
        return 2
    role = {**os.environ, **leaf_role(leaf)}
    relaunches = 0
    while True:
        launched = leaf_tree_guard.start(
            [sibling("supervise.sh"), leaf,
             sibling("run-leaf.sh"), prompt_path, *flags],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        said = (launched.stderr or b"").decode("utf-8", "replace")
        if said:
            write(sys.stderr, said.removesuffix("\n"))
        if launched.returncode == 2:
            refused = [line for line in said.splitlines() if line.startswith("supervise: refusing to launch")]
            if refused:
                write(sys.stdout, "verifier leaf not launched — %s" % refused[0])
                return 2
            write(sys.stdout, "verifier leaf killed-stuck — no verdict rendered (see .tdd/%s.log)" % leaf)
            return 2
        found = guard.changes()
        if isinstance(found, leaf_tree_guard.Unreadable):
            write(sys.stderr, "verify: could not read the tree after the %s leaf; its verdict is not accepted\n%s"
                  % (leaf, guard.restore_unreadable()))
            return 2
        if isinstance(found, leaf_tree_guard.Changed):
            diff = save_diff(leaf, found.before, found.after)
            if not guard.restore(found):
                return 2
            if relaunches >= retries:
                return refuse_modified("the repository", leaf, found.paths, diff)
            relaunches += 1
            mark(role, "relaunch", "cause=tree-change")
            continue
        if isinstance(found, leaf_tree_guard.ConfigUnreadable):
            return unreadable_gitconfig(found)
        if isinstance(found, leaf_tree_guard.ConfigChanged):
            return refuse_modified("the operator's global git config", leaf, [found.path])
        code, reason, err = parse(without_checks(launched.stdout) if words[0] == "green" else launched.stdout)
        if err:
            write(sys.stderr, err.removesuffix("\n"))
        no_verdict = code == 2 and "no VERDICT: line found" in err
        if not no_verdict or relaunches >= retries:
            break
        relaunches += 1
        marked = mark(role, "relaunch", "cause=no-verdict")
        if marked:
            return marked
    if code == 0 and words[0] == "green" and options["--step"]:
        surviving = survivors(options["--step"])
        if surviving[0]:
            code, reason = surviving
    word = {0: "PASS", 1: "REJECT"}.get(code, "malformed")
    cause = ["cause=no-verdict"] if no_verdict else []
    check = named_check(launched.stdout) if words[0] == "green" else []
    judged = ["tree=" + guard.tree] if guard.tree else []
    marked = mark(role, "verdict", "verdict=" + word, "reason=" + reason.split("\n", 1)[0], *cause, *check, *judged,
                  "name=" + leaf)
    if marked:
        return marked
    issue, step = tunables.read("VERI_ISSUE") or None, tunables.read("VERI_STEP") or None
    if word != "PASS" and guard.tree and issue and step:
        preserve(issue, step, leaf, role["VERI_ATTEMPT"],
                 "no-verdict" if no_verdict else word.lower())
    write(sys.stdout, reason)
    return entry.to_contract(code)


def survivors(step):
    code, printed, err = replaces_case_survivors.survivors(step)
    sys.stderr.write(err)
    return (code, printed.rstrip("\n")) if code in (1, 2) else (0, "")


CHECK_RE = re.compile(rb"^[ \t]*CHECK:[ \t]*(.*?)[ \t\r]*$", re.MULTILINE)


def named_check(out):
    """The `check=<n>` word for the reply's last `CHECK:` line when its value is one digit 1 to 5, else none."""
    said = CHECK_RE.findall(out.replace(b"\0", b""))
    return ["check=" + said[-1].decode()] if said and said[-1] in (b"1", b"2", b"3", b"4", b"5") else []


def without_checks(out):
    """The reply with every `CHECK:` line dropped, so the verdict and the reason read as if the verifier wrote none."""
    return b"\n".join(line for line in out.split(b"\n") if not CHECK_RE.match(line.replace(b"\0", b"")))


def parse(out):
    return parse_verdict.verdict(out.replace(b"\0", b"").decode("utf-8", "surrogateescape"))


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
