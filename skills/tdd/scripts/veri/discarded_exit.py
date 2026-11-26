"""discarded-exit.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import ast
import re
import sys

import entry
import git

USAGE = "usage: discarded-exit.sh"
EXIT_CODE_CALLS = {"subprocess.run", "subprocess.call", "os.system", "fused.call"}
HUNK = re.compile(r"@@ -\S+ \+(\d+)")


def _head_diff():
    """Runs `git diff HEAD` in the current directory; returns (code, stdout)."""
    done = git.git("diff", "HEAD", capture_output=True, text=True)
    return done.returncode, done.stdout


def _added_lines(diff):
    """Maps each path a unified diff touches to the set of its added lines' numbers in the new file; a deleted
    file is touched with no added lines."""
    added, path, number, in_hunk = {}, None, 0, False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            in_hunk, path = False, None
        elif not in_hunk and line.startswith("--- a/"):
            path = line[len("--- a/"):]
            added.setdefault(path, set())
        elif not in_hunk and line.startswith("+++ b/"):
            path = line[len("+++ b/"):]
            added.setdefault(path, set())
        elif line.startswith("@@"):
            in_hunk, number = True, int(HUNK.match(line).group(1))
        elif in_hunk and line.startswith("+"):
            added[path].add(number)
            number += 1
        elif in_hunk and line.startswith(" "):
            number += 1
    return added


def _called_name(call):
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id + "." + func.attr
    return None


FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def _checks(call):
    """Whether call passes the literal keyword check=True."""
    return any(k.arg == "check" and isinstance(k.value, ast.Constant) and k.value.value is True
               for k in call.keywords)


LOOPS = (ast.For, ast.AsyncFor, ast.While)


def _unchecked_run(call):
    return isinstance(call, ast.Call) and _called_name(call) == "subprocess.run" and not _checks(call)


def _binding(node):
    """(target, call) for a statement binding an exit-code call's result, or None."""
    if isinstance(node, ast.Assign):
        target = node.targets[0]
    elif isinstance(node, ast.AnnAssign):
        target = node.target
    else:
        return None
    value = node.value
    if isinstance(value, ast.Call) and _called_name(value) in EXIT_CODE_CALLS and not (
            _called_name(value) == "subprocess.run" and _checks(value)):
        return target, value
    return None


def _drops_exit_code(node, reads_after):
    """Whether node is a statement discarding an exit-code call's code: a bare call, or one whose
    code, the whole result or its unpacked first element, goes to `_` or to a name never read after
    the binding; a subprocess.run bound whole holds its code in <name>.returncode, so that is what
    must be read. A subprocess.run passing check=True raises on a non-zero code, so it discards nothing."""
    if isinstance(node, ast.Expr):
        value = node.value
        return (isinstance(value, ast.Call) and _called_name(value) in EXIT_CODE_CALLS
                and not (_called_name(value) == "subprocess.run" and _checks(value)))
    bound = _binding(node)
    if bound is None:
        return False
    target, call = bound
    code = target.elts[0] if isinstance(target, ast.Tuple) else target
    if not isinstance(code, ast.Name):
        return False
    if code.id == "_":
        return True
    wanted = code.id + ".returncode" if _called_name(call) == "subprocess.run" and code is target else code.id
    return wanted not in reads_after(node)


def _own_nodes(scope):
    """The nodes under scope (a module or a function), not descending into a nested function."""
    pending = list(ast.iter_child_nodes(scope))
    while pending:
        node = pending.pop()
        yield node
        if not isinstance(node, FUNCTIONS):
            pending.extend(ast.iter_child_nodes(node))


def _reads(scope):
    """Each read inside scope as (what, node): a loaded name, and `<name>.returncode` for each attribute
    of that form."""
    found = []
    for node in ast.walk(scope):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            found.append((node.id, node))
        elif isinstance(node, ast.Attribute) and node.attr == "returncode" and isinstance(node.value, ast.Name):
            found.append((node.value.id + ".returncode", node))
    return found


def _within(node, outer):
    return outer.lineno <= node.lineno and node.end_lineno <= outer.end_lineno


def _after(node, statement):
    return (node.lineno, node.col_offset) >= (statement.end_lineno, statement.end_col_offset)


def _discarded(source):
    """The line numbers of the statements in source that discard an exit-code call's result. A binding
    counts as read when its scope reads it after the binding statement, a read anywhere in a loop body
    holding the binding counting as after; an attribute other than returncode taken off an unchecked
    subprocess.run, anywhere in an expression, discards its code."""
    tree = ast.parse(source)
    lines = []
    for scope in [tree, *(node for node in ast.walk(tree) if isinstance(node, FUNCTIONS))]:
        reads = _reads(scope)
        own = list(_own_nodes(scope))
        loops = [node for node in own if isinstance(node, LOOPS)]

        def reads_after(statement, reads=reads, loops=loops):
            around = [loop for loop in loops if _within(statement, loop)]
            return {what for what, node in reads
                    if _after(node, statement) or any(_within(node, loop) for loop in around)}

        lines.extend(node.lineno for node in own if _drops_exit_code(node, reads_after))
        lines.extend(node.lineno for node in own
                     if isinstance(node, ast.Attribute) and node.attr != "returncode" and _unchecked_run(node.value))
    return sorted(set(lines))


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    code, diff = _head_diff()
    if code != 0:
        return entry.refuse(usage=USAGE)
    py = {path: lines for path, lines in _added_lines(diff).items() if path.endswith(".py")}
    if not py:
        return 3
    found = False
    for path, lines in py.items():
        if not lines:
            continue
        with open(path, encoding="utf-8") as source:
            for number in _discarded(source.read()):
                if number in lines:
                    print(f"{path}:{number}")
                    found = True
    return 1 if found else 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
