"""Fast-tier admission guard: names the lines of test files that start a process."""
import ast
from pathlib import Path


def _subprocess_names(tree):
    modules, functions = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    modules.add(alias.asname or "subprocess")
        elif isinstance(node, ast.ImportFrom) and node.module == "subprocess":
            for alias in node.names:
                functions.add(alias.asname or alias.name)
    return modules, functions


def _starts_process(func):
    if not (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)):
        return False
    if func.value.id == "pty":
        return True
    return func.value.id == "os" and func.attr.startswith(("system", "exec", "spawn"))


def offences(root):
    found = []
    for path in sorted(Path(root).rglob("test_*.py")):
        tree = ast.parse(path.read_text())
        modules, functions = _subprocess_names(tree)
        modules.add("subprocess")
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id in modules
            ) or (isinstance(func, ast.Name) and func.id in functions) or _starts_process(func):
                found.append(f"{path}:{node.lineno}: starts a process through subprocess")
    return found
