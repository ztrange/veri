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


def _process_start(module, attr):
    if module == "pty" and attr:
        return f"{module}.{attr}"
    if module == "os" and attr and attr.startswith(("system", "popen", "exec", "spawn", "posix_spawn")):
        return f"{module}.{attr}"
    return None


def _require_reasons(exemptions):
    for entry, reason in exemptions.items():
        if not str(reason).strip():
            raise ValueError(f"exemption {entry} has no reason")


def offences(root, exemptions=None):
    exemptions = exemptions or {}
    _require_reasons(exemptions)
    root = Path(root)
    if not root.is_dir():
        raise NotADirectoryError(f"{root}: no such directory")
    files = sorted(root.rglob("test_*.py"))
    present = {str(path) for path in files} | {str(path.relative_to(root)) for path in files}
    for entry in exemptions:
        if entry.rpartition(":")[0] not in present:
            raise ValueError(f"exemption {entry} matches no file under {root}")
    found = []
    for path in files:
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
            started = _process_start(module, attr) or (_process_start(*imported) if imported else None)
            if (module, attr) == ("time", "sleep") or imported == ("time", "sleep"):
                message = "sleeps through time.sleep"
            elif module == "socket" or imported == ("socket", "socket"):
                message = "opens a socket through socket"
            elif (
                receiver in modules
                or (isinstance(func, ast.Name) and func.id in functions)
            ):
                message = "starts a process through subprocess"
            elif started:
                message = f"starts a process through {started}"
            elif (module, attr) == ("pytest", "main") or any(
                isinstance(arg, ast.Constant) and isinstance(arg.value, str) and _SUITE_PATH.search(arg.value)
                for arg in node.args
            ):
                message = "runs a nested suite"
            else:
                continue
            found.append(f"{path}:{node.lineno}: {message}")

    def exempt(line):
        key = line.split(": ")[0]
        file, _, number = key.rpartition(":")
        return key in exemptions or f"{Path(file).relative_to(root)}:{number}" in exemptions

    return [line for line in found if not exempt(line)]


def main(argv):
    found = offences(argv[0])
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
