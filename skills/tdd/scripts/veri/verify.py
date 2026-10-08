"""verify.sh's logic, run in-process."""
import glob
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

import parse_verdict

from leaf_model import resolve
from leaf_role import _write, leaf_role
from run_verdict import SCRIPTS, takes_a_value

LEAF_ARGS = ["--permission-mode", "bypassPermissions",
             "--disallowedTools", "Write", "Edit", "MultiEdit", "NotebookEdit"]
USAGE = ("usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file>"
         " <test-path> [<target-test-id>]")


def refuse(*lines):
    for line in lines + (USAGE,):
        _write(sys.stderr, line)
    return 2


def is_echo_flag(value):
    return len(value) > 1 and value[0] == "-" and all(c in "neE" for c in value[1:])


def sibling(name):
    return os.path.join(SCRIPTS, name)


def to_contract(code):
    return code if code in (0, 1, 2, 3) else 2


def start(args, **kwargs):
    try:
        return subprocess.run(args, **kwargs)
    except OSError:
        return subprocess.CompletedProcess(args, 127, b"")


def mark(role, *words):
    return start([sibling("event.sh"), *words], env=role).returncode


def preserve(issue, step, leaf, attempt, outcome):
    if start([sibling("preserve-attempt.sh"), issue, step, leaf, attempt, outcome],
             stdout=sys.stderr.fileno()).returncode:
        _write(sys.stderr, "verify: could not preserve the %s attempt (issue %s step %s %s attempt %s)"
               % (outcome, issue, step, leaf, attempt))


def git(*args, env=None):
    return start(["git", *args], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


def in_temp_index(*args):
    folder = tempfile.mkdtemp()
    env = {**os.environ, "GIT_INDEX_FILE": os.path.join(folder, "index")}
    try:
        if git("add", "-A", env=env).returncode:
            return ""
        out = git(*args, env=env)
        return out.stdout.decode().rstrip("\n") if out.returncode == 0 else ""
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def head_snapshot():
    return git("rev-parse", "--verify", "HEAD").stdout.decode().rstrip("\n")


def changed_paths(tree_before, head_before):
    if not tree_before:
        return [], head_before
    tree_after = in_temp_index("write-tree")
    head_after = head_snapshot()
    diff = git("diff-tree", "-r", "--name-only", "--no-commit-id", tree_before, tree_after)
    paths = diff.stdout.decode().splitlines() if diff.returncode == 0 else []
    if head_after != head_before:
        paths.append("HEAD")
    return paths, head_after


def gitconfig_snapshot(path):
    try:
        with open(path, "rb") as config:
            return config.read()
    except FileNotFoundError:
        return None


def unreadable_gitconfig(path, error):
    _write(sys.stderr, "verify: cannot read the global git config %s: %s" % (path, error.strerror))
    return 2


def refuse_modified(what, leaf, paths):
    _write(sys.stdout, "verifier leaf modified %s — verdict not accepted"
           " (see .tdd/%s.log); changed:" % (what, leaf))
    _write(sys.stdout, "\n".join(paths))
    return 2


def leaf_args(words):
    if not words:
        return LEAF_ARGS
    return [path for word in words.split()
            for path in (sorted(glob.glob(word)) or [word])]


def no_verdict_budget(value):
    if len(value) > 1 and value.startswith("0"):
        try:
            return int(value, 8)
        except ValueError:
            return 0
    return int(value)


def main(argv):
    args = list(argv)
    while args and takes_a_value(args[0]):
        if len(args) < 2 or not args[1]:
            return refuse("verify: %s needs a value" % args[0])
        args = args[2:]
    if len(args) < 3:
        return refuse()
    leaf = "verify-" + args[0]
    words = os.environ.get("VERIFY_LEAF_ARGS")
    flags = leaf_args(words)
    if words:
        model = resolve(leaf)
        if model and not is_echo_flag(model) and "--model" in flags:
            _write(sys.stderr, "verify: VERIFY_LEAF_ARGS carries its own --model and a role model"
                   " variable resolved '%s' — which one the leaf would run on is flag order;"
                   " unset one of them" % model)
            return 2
    built = start([sibling("build-verify-prompt.sh"), *argv], stdout=subprocess.PIPE)
    if built.returncode:
        return to_contract(built.returncode)
    prompt_path = ".tdd/%s.prompt" % leaf
    os.makedirs(".tdd", exist_ok=True)
    with open(prompt_path, "wb") as prompt:
        prompt.write(built.stdout.rstrip(b"\n"))
    tree_before = in_temp_index("write-tree")
    head_before = head_snapshot()
    gitconfig = os.environ["HOME"] + "/.gitconfig"
    try:
        gitconfig_before = gitconfig_snapshot(gitconfig)
    except OSError as error:
        return unreadable_gitconfig(gitconfig, error)
    retries = os.environ.get("VERI_NO_VERDICT_RETRIES") or "1"
    if not re.fullmatch("[0-9]+", retries):
        _write(sys.stderr, "verify: VERI_NO_VERDICT_RETRIES must be a non-negative integer,"
               " got '%s'" % retries)
        return 2
    retries = no_verdict_budget(retries)
    role = {**os.environ, **leaf_role(leaf)}
    relaunches = 0
    while True:
        launched = start(
            [sibling("supervise.sh"), leaf,
             sibling("run-leaf.sh"), prompt_path, *flags],
            stdout=subprocess.PIPE)
        if launched.returncode == 2:
            _write(sys.stdout, "verifier leaf killed-stuck — no verdict rendered (see .tdd/%s.log)" % leaf)
            return 2
        changed, head_after = changed_paths(tree_before, head_before)
        if changed:
            in_temp_index("read-tree", "-u", "--reset", tree_before)
            if head_before and head_before != head_after:
                restored = subprocess.run(["git", "update-ref", "HEAD", head_before])
                if restored.returncode != 0:
                    return 2
            return refuse_modified("the repository", leaf, changed)
        try:
            gitconfig_after = gitconfig_snapshot(gitconfig)
        except OSError as error:
            return unreadable_gitconfig(gitconfig, error)
        if gitconfig_after != gitconfig_before:
            return refuse_modified("the operator's global git config", leaf, [gitconfig])
        code, reason, err = parse(launched.stdout)
        if err:
            _write(sys.stderr, err.removesuffix("\n"))
        no_verdict = code == 2 and "no VERDICT: line found" in err
        if not no_verdict or relaunches >= retries:
            break
        relaunches += 1
        marked = mark(role, "relaunch", "cause=no-verdict")
        if marked:
            return marked
    word = {0: "PASS", 1: "REJECT"}.get(code, "malformed")
    cause = ["cause=no-verdict"] if no_verdict else []
    marked = mark(role, "verdict", "verdict=" + word, "reason=" + reason.split("\n", 1)[0], *cause)
    if marked:
        return marked
    issue, step = os.environ.get("VERI_ISSUE"), os.environ.get("VERI_STEP")
    if word != "PASS" and tree_before and issue and step:
        preserve(issue, step, leaf, role["VERI_ATTEMPT"],
                 "no-verdict" if no_verdict else word.lower())
    _write(sys.stdout, reason)
    return to_contract(code)


def parse(out):
    stdin, stdout, stderr = sys.stdin, sys.stdout, sys.stderr
    sys.stdin = io.StringIO(out.replace(b"\0", b"").decode("utf-8", "surrogateescape"))
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    try:
        code = parse_verdict.main([])
        return code, sys.stdout.getvalue().rstrip("\n"), sys.stderr.getvalue()
    finally:
        sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
