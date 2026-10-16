"""Fast-tier admission guard: names the lines of test files that start a process."""
import ast
import re
import sys
from pathlib import Path

_SUITE_PATH = re.compile(r"(^|/)test_[^/]*\.py$|\.test\.sh$")

EXEMPTIONS = {}


def _aliases(tree):
    modules, names = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                names[alias.asname or alias.name] = (node.module, alias.name)
    return modules, names


def _receiver_and_attr(func):
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id, func.attr
    return None, None


def _starts_process(func):
    receiver, attr = _receiver_and_attr(func)
    if receiver == "pty":
        return True
    return receiver == "os" and attr.startswith(("system", "exec", "spawn"))


def _require_reasons(exemptions):
    for entry, reason in exemptions.items():
        if not reason:
            raise ValueError(f"exemption {entry} has no reason")


def offences(root, exemptions=None):
    exemptions = exemptions or {}
    _require_reasons(exemptions)
    if not Path(root).is_dir():
        raise NotADirectoryError(f"{root}: no such directory")
    found = []
    for path in sorted(Path(root).rglob("test_*.py")):
        tree = ast.parse(path.read_text())
        module_aliases, name_imports = _aliases(tree)
        modules = {alias for alias, name in module_aliases.items() if name == "subprocess"}
        modules.add("subprocess")
        functions = {alias for alias, (module, _) in name_imports.items() if module == "subprocess"}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            receiver, attr = _receiver_and_attr(func)
            imported = name_imports.get(func.id) if isinstance(func, ast.Name) else None
            module = module_aliases.get(receiver, receiver)
            if (module, attr) == ("time", "sleep") or imported == ("time", "sleep"):
                message = "sleeps through time.sleep"
            elif module == "socket" or imported == ("socket", "socket"):
                message = "opens a socket through socket"
            elif (
                receiver in modules
                or (isinstance(func, ast.Name) and func.id in functions)
                or _starts_process(func)
            ):
                message = "starts a process through subprocess"
            elif (module, attr) == ("pytest", "main") or any(
                isinstance(arg, ast.Constant) and isinstance(arg.value, str) and _SUITE_PATH.search(arg.value)
                for arg in node.args
            ):
                message = "runs a nested suite"
            else:
                continue
            found.append(f"{path}:{node.lineno}: {message}")
    return [line for line in found if line.split(": ")[0] not in exemptions]


def main(argv):
    offences(argv[0])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
