"""Fast-tier admission guard: names the lines of test files that start a process."""
import ast
import re
import sys
from pathlib import Path

_SUITE_PATH = re.compile(r"(^|/)test_[^/]*\.py$|\.test\.sh$")

_PATH_WITH_SPACES = re.compile(r"[^\s\\]*/[^\\]*$|[^\s\\]+$")

_COMMAND = re.compile(r"(python3 -m pytest|bash) ")

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
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"exemption {entry} has no reason")


def _names(path, root):
    relative = str(path.relative_to(root))
    names = (str(path), relative)
    return names + (f"unit/{relative}",) if Path(root).name == "unit" else names


def _require_matches(exemptions, files, root):
    present = {name for path in files for name in _names(path, root)}
    for entry in exemptions:
        if entry.rpartition(":")[0] not in present:
            raise ValueError(f"exemption {entry} matches no file under {root}")


def _discover(root, exemptions):
    _require_reasons(exemptions)
    root = Path(root)
    if not root.is_dir():
        raise NotADirectoryError(f"{root}: no such directory")
    files = sorted(root.rglob("test_*.py"))
    _require_matches(exemptions, files, root)
    return root, files


def _names_a_suite(arg):
    return (
        isinstance(arg, ast.Constant)
        and isinstance(arg.value, str)
        and _SUITE_PATH.search(arg.value)
        and (_COMMAND.match(arg.value) or _PATH_WITH_SPACES.match(arg.value))
    )


def _classify(node, module_aliases, name_imports, modules, functions, defined=frozenset()):
    func = node.func
    receiver, attr = _receiver_and_attr(func)
    name = func.id if isinstance(func, ast.Name) else None
    imported = name_imports.get(name)
    module = module_aliases.get(receiver, receiver)
    started = _process_start(module, attr) or (_process_start(*imported) if imported else None)
    if (module, attr) == ("time", "sleep") or imported == ("time", "sleep"):
        return "sleeps through time.sleep"
    if module == "socket" or imported == ("socket", "socket"):
        return "opens a socket through socket"
    if attr == "CompletedProcess" or (attr in ("setitem", "delitem") and receiver == "monkeypatch"):
        return None
    if receiver in modules or name in functions:
        return "starts a process through subprocess"
    if started:
        return f"starts a process through {started}"
    args = [*node.args, *(kw.value for kw in node.keywords)]
    if name == "run_cli":
        listed = [item for arg in args if isinstance(arg, (ast.List, ast.Tuple)) for item in arg.elts]
        args += [item for item in listed if isinstance(item, ast.Constant) and "/" in str(item.value)]
    if name in defined or (name and name.startswith("assert")) or "Path" in (name, attr):
        return None
    if (module, attr) == ("pytest", "main") or any(_names_a_suite(arg) for arg in args):
        return "runs a nested suite"
    return None


def _file_offences(path):
    tree = ast.parse(path.read_text())
    module_aliases, name_imports = _aliases(tree)
    modules = {alias for alias, name in module_aliases.items() if name == "subprocess"}
    modules.add("subprocess")
    functions = {alias for alias, (module, _) in name_imports.items() if module == "subprocess"}
    defined = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        message = _classify(node, module_aliases, name_imports, modules, functions, defined)
        if message:
            found.append(f"{path}:{node.lineno}: {message}")
    return found


def _exempt(line, root, exemptions):
    key = line.split(": ")[0]
    file, _, number = key.rpartition(":")
    return any(f"{name}:{number}" in exemptions for name in _names(Path(file), root))


def offences(root, exemptions=None):
    exemptions = exemptions or {}
    root, files = _discover(root, exemptions)
    found = [line for path in files for line in _file_offences(path)]
    return [line for line in found if not _exempt(line, root, exemptions)]


def main(argv):
    found = offences(argv[0])
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
