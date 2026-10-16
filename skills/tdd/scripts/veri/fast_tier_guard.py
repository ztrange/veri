"""Fast-tier admission guard: names the lines of test files that start a process."""
import ast
from pathlib import Path


def offences(root):
    found = []
    for path in sorted(Path(root).rglob("test_*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
            ):
                found.append(f"{path}:{node.lineno}: starts a process through subprocess")
    return found
