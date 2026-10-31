"""verify.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import glob
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

import build_verify_prompt
import event
import parse_verdict
import preserve_attempt
import renamed_case
import replaces_case_survivors
import tunables

from leaf_model import _env, resolve
from entry import write
from leaf_role import leaf_role
from run_verdict import SCRIPTS, takes_a_value

LEAF_ARGS = ["--permission-mode", "bypassPermissions",
             "--disallowedTools", "Write", "Edit", "MultiEdit", "NotebookEdit"]
USAGE = ("usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file>"
         " <test-path> [<target-test-id>]")


def refuse(*lines):
    for line in lines + (USAGE,):
        write(sys.stderr, line)
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
    return event.mark("", event.context(role), words[0], words[1:])


def preserve(issue, step, leaf, attempt, outcome):
    if preserve_attempt.preserve(".", issue, step, leaf, attempt, outcome):
        write(sys.stderr, "verify: could not preserve the %s attempt (issue %s step %s %s attempt %s)"
               % (outcome, issue, step, leaf, attempt))


def git(*args, env=None):
    return start(["git", *args], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


@contextlib.contextmanager
def temp_index_env():
    folder = tempfile.mkdtemp()
    try:
        yield {**os.environ, "GIT_INDEX_FILE": os.path.join(folder, "index")}
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def in_temp_index(*args):
    with temp_index_env() as env:
        if git("add", "-A", env=env).returncode:
            return ""
        out = git(*args, env=env)
        return out.stdout.decode().rstrip("\n") if out.returncode == 0 else ""


def unreadable_file_in_tree():
    with temp_index_env() as env:
        added = start(["git", "add", "-A"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return added.returncode != 0 and b"Permission denied" in (added.stderr or b"")


def head_snapshot():
    return git("rev-parse", "--verify", "HEAD").stdout.decode().rstrip("\n")


def changed_paths(tree_before, head_before):
    if not tree_before:
        return [], head_before, ""
    tree_after = in_temp_index("write-tree")
    head_after = head_snapshot()
    diff = git("diff-tree", "-r", "--name-only", "--no-commit-id", tree_before, tree_after)
    paths = diff.stdout.decode().splitlines() if diff.returncode == 0 else []
    if head_after != head_before:
        paths.append("HEAD")
    return paths, head_after, tree_after


def file_bytes(path):
    """A regular file's bytes; None for anything else — absent, a symlink, a directory, unreadable."""
    if os.path.islink(path) or not os.path.isfile(path):
        return None
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None


def appended(before, after):
    return after is not None and after.startswith(before or b"")


def gitconfig_snapshot(path):
    try:
        with open(path, "rb") as config:
            return config.read()
    except FileNotFoundError:
        return None


def unreadable_gitconfig(path, error):
    write(sys.stderr, "verify: cannot read the global git config %s: %s" % (path, error.strerror))
    return 2


def save_diff(leaf, tree_before, tree_after):
    diff = git("diff", "--binary", "--no-ext-diff", "--no-textconv", "--no-color",
               "--src-prefix=a/", "--dst-prefix=b/", "-U3", tree_before, tree_after)
    path = ".tdd/%s.diff" % leaf
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


def no_verdict_budget(value):
    if len(value) > 1 and value.startswith("0"):
        try:
            return int(value, 8)
        except ValueError:
            return 0
    return int(value)


def pytest_cases(sha):
    listed = git("ls-tree", "-r", "--name-only", sha)
    if listed.returncode != 0:
        return None
    cases = set()
    for path in listed.stdout.decode().splitlines():
        name = path.rsplit("/", 1)[-1]
        if not (name.startswith("test_") and name.endswith(".py")):
            continue
        shown = git("show", "%s:%s" % (sha, path))
        if shown.returncode != 0:
            return None
        for case in re.findall(r"^[ \t]*(?:async[ \t]+)?def[ \t]+(test_\w+)", shown.stdout.decode(), re.M):
            cases.add((path, case))
    return cases


def deleted_cases(branch_base, step_base):
    before, middle, after = (pytest_cases(sha) for sha in (branch_base, step_base, "HEAD"))
    if None in (before, middle, after):
        return None
    kept = {case for _, case in after}
    taken = {other for _, other in middle}
    return sorted(case for case in sorted(middle - before)
                  if case[1] not in kept and not was_renamed(case, step_base, taken))


def rename_of(find, case, step_base, taken):
    path, name = case
    old = git("show", "%s:%s" % (step_base, path))
    new = git("show", "HEAD:" + path)
    return find(name, old.stdout.decode(), new.stdout.decode(), taken)


def was_renamed(case, step_base, taken):
    return rename_of(renamed_case.renamed_to, case, step_base, taken) is not None


def changed_rename(case, step_base, taken):
    return rename_of(renamed_case.renamed_and_changed_to, case, step_base, taken)


def added_markers(onto):
    log = git("log", "-p", "-U0", "--no-color", "--no-ext-diff", "--format=commit %H", onto + "..HEAD")
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
    done = start(["sh", "-c", gate], cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                 stderr=subprocess.STDOUT)
    return done.returncode == 0, done.stdout.decode("utf-8", "replace")


def fails_at_head(gate, output):
    scratch = tempfile.mkdtemp(prefix="veri-head-")
    try:
        git("worktree", "add", "--detach", scratch + "/tree", "HEAD~1")
        try:
            passed, before_output = passes_in(gate, scratch + "/tree")
            return not passed and before_output == output
        finally:
            git("worktree", "remove", "--force", scratch + "/tree")
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
        if (model and not is_echo_flag(model) and "--model" in flags
                and (_env("VERI_MODEL_VERIFIER") or _env("VERI_MODEL"))):
            write(sys.stderr, "verify: VERIFY_LEAF_ARGS carries its own --model and a role model"
                   " variable resolved '%s' — which one the leaf would run on is flag order;"
                   " unset one of them" % model)
            return 2
    options = {"--step": "", "--fast-cmd": ""}
    words = list(argv)
    while words[:1] and words[0] in options:
        options[words[0]] = words[1]
        words = words[2:]
    if not all(words[:3]):
        return to_contract(build_verify_prompt._refuse())
    if len(words) > 4:
        return to_contract(build_verify_prompt._refuse("build-verify-prompt: too many arguments"))
    code, built = build_verify_prompt.build(options["--step"], options["--fast-cmd"], *words)
    if code:
        return to_contract(code)
    if words[0] == "diff" and git("rev-parse", "--git-dir").returncode == 0:
        deleted = deleted_cases(words[2], words[3])
        if deleted is None:
            return refuse("verify: cannot read the test files at %s, %s or HEAD" % (words[2], words[3]))
        if deleted:
            taken = {other for _, other in pytest_cases(words[3])}
            changed = [(case, changed_rename(case, words[3], taken)) for case in deleted]
            pairs = [(case, other) for case, other in changed if other]
            if pairs:
                write(sys.stdout, "step renamed and changed pytest cases, so the step must be split: "
                       + ", ".join("%s::%s -> %s" % (case + (other,)) for case, other in pairs))
                return 1
            write(sys.stdout, "step deleted pytest cases an earlier step added: "
                   + ", ".join("%s::%s" % case for case in deleted))
            return 1
    if words[0] == "rebase" and git("rev-parse", "--git-dir").returncode == 0:
        marked = added_markers(words[2])
        if marked:
            write(sys.stdout, "rebase committed conflict markers: "
                   + ", ".join("%s %s" % pair for pair in marked))
            return 1
    if words[0] == "red":
        failure = red_gate_failure()
        if failure and failure.startswith("verify: "):
            write(sys.stderr, failure)
            return 2
        if failure:
            write(sys.stdout, failure)
            return 1
    top = event.toplevel()
    run_state = os.path.join(top, ".tdd") if top and top != os.getcwd() else ".tdd"
    prompt_path = "%s/%s.prompt" % (run_state, leaf)
    os.makedirs(run_state, exist_ok=True)
    with open(prompt_path, "wb") as prompt:
        prompt.write(built.rstrip(b"\n"))
    tree_before = in_temp_index("write-tree")
    if not tree_before and unreadable_file_in_tree():
        write(sys.stderr, "verify: could not read the tree before the %s leaf; its verdict is not accepted" % leaf)
        return 2
    head_before = head_snapshot()
    gitconfig = os.environ["HOME"] + "/.gitconfig"
    try:
        gitconfig_before = gitconfig_snapshot(gitconfig)
    except OSError as error:
        return unreadable_gitconfig(gitconfig, error)
    retries = tunables.read("VERI_NO_VERDICT_RETRIES", unless_empty="1")
    try:
        tunables.tokens(retries)
    except ValueError:
        write(sys.stderr, "verify: VERI_NO_VERDICT_RETRIES must be a non-negative integer,"
               " got '%s'" % retries)
        return 2
    retries = no_verdict_budget(retries)
    role = {**os.environ, **leaf_role(leaf)}
    relaunches = 0
    own_record = None
    if words[0] == "pin":
        record = os.path.abspath("%s/issue-%s-mutations.md" % (run_state, tunables.read("VERI_ISSUE")))
        launch_env = tunables.with_values(VERI_MUTATION_RECORD=record)
        own_record = os.path.relpath(record, top or os.getcwd())
        record_before = file_bytes(record)
        record_irregular = record_before is None and os.path.lexists(record)
    else:
        launch_env = tunables.without("VERI_MUTATION_RECORD")
    while True:
        launched = start(
            [sibling("supervise.sh"), leaf,
             sibling("run-leaf.sh"), prompt_path, *flags],
            env=launch_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        changed, head_after, tree_after = changed_paths(tree_before, head_before)
        if tree_before and not tree_after:
            write(sys.stderr, "verify: could not read the tree after the %s leaf; its verdict is not accepted" % leaf)
            return 2
        # A pin's verifier records the mutations it watched fail; appending to that record alone is not a
        # tree change (#2741). Deleting or rewriting it would disarm earlier pins, so that still refuses.
        if changed and not (changed == [own_record] and not record_irregular
                                                   and appended(record_before, file_bytes(record))):
            diff = save_diff(leaf, tree_before, tree_after)
            in_temp_index("read-tree", "-u", "--reset", tree_before)
            if head_before and head_before != head_after:
                restored = start(["git", "update-ref", "HEAD", head_before])
                if restored.returncode != 0:
                    return 2
            if relaunches >= retries:
                return refuse_modified("the repository", leaf, changed, diff)
            relaunches += 1
            mark(role, "relaunch", "cause=tree-change")
            continue
        try:
            gitconfig_after = gitconfig_snapshot(gitconfig)
        except OSError as error:
            return unreadable_gitconfig(gitconfig, error)
        if gitconfig_after != gitconfig_before:
            return refuse_modified("the operator's global git config", leaf, [gitconfig])
        code, reason, err = parse(launched.stdout)
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
    marked = mark(role, "verdict", "verdict=" + word, "reason=" + reason.split("\n", 1)[0], *cause)
    if marked:
        return marked
    issue, step = tunables.read("VERI_ISSUE") or None, tunables.read("VERI_STEP") or None
    if word != "PASS" and tree_before and issue and step:
        preserve(issue, step, leaf, role["VERI_ATTEMPT"],
                 "no-verdict" if no_verdict else word.lower())
    write(sys.stdout, reason)
    return to_contract(code)


def survivors(step):
    stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        code = replaces_case_survivors.main([step])
        printed = sys.stdout.getvalue().rstrip("\n")
    finally:
        sys.stdout = stdout
    return (code, printed) if code in (1, 2) else (0, "")


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
    import entry
    entry.run(main, sys.argv[1:])
