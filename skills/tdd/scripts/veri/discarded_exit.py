"""discarded-exit.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import ast
import re
import subprocess
import sys

import entry


USAGE = "usage: discarded-exit.sh"
EXIT_CODE_CALLS = {"subprocess.run", "subprocess.call", "os.system", "fused.call"}
HUNK = re.compile(r"@@ -\S+ \+(\d+)")


def _git(*args):
    """Runs git with args in the current directory; returns (code, stdout)."""
    done = subprocess.run(["git", *args], capture_output=True, text=True)
    return done.returncode, done.stdout


def _added_lines(diff):
    """Maps each new-side path of a unified diff to the set of its added lines' numbers in the new file."""
    added, path, number, in_hunk = {}, None, 0, False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            in_hunk = False
        elif not in_hunk and line.startswith("+++ b/"):
            path = line[len("+++ b/"):]
            added[path] = set()
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


def _drops_exit_code(node):
    """Whether node is a statement discarding an exit-code call's code: a bare call, or one whose
    code, the whole result or its unpacked first element, goes to `_`."""
    if not (isinstance(node, (ast.Expr, ast.Assign)) and isinstance(node.value, ast.Call)
            and _called_name(node.value) in EXIT_CODE_CALLS):
        return False
    if isinstance(node, ast.Expr):
        return True
    target = node.targets[0]
    code = target.elts[0] if isinstance(target, ast.Tuple) else target
    return isinstance(code, ast.Name) and code.id == "_"


def _discarded(source):
    """The line numbers of the statements in source that discard an exit-code call's result."""
    return sorted(node.lineno for node in ast.walk(ast.parse(source)) if _drops_exit_code(node))


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    code, diff = _git("diff", "HEAD")
    if code != 0:
        return entry.refuse(usage=USAGE)
    py = {path: lines for path, lines in _added_lines(diff).items() if path.endswith(".py")}
    if not py:
        return 3
    found = False
    for path, lines in py.items():
        with open(path, encoding="utf-8") as source:
            for number in _discarded(source.read()):
                if number in lines:
                    print(f"{path}:{number}")
                    found = True
    return 1 if found else 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
