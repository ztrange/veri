import ast
import pathlib

SERVE = pathlib.Path(__file__).resolve().parents[1] / "serve.py"

PROCESS_MODULES = {"subprocess", "multiprocessing", "pty", "asyncio"}
OS_LAUNCHERS = {"system", "popen", "fork", "forkpty", "posix_spawn", "posix_spawnp"}
OS_PREFIXES = ("exec", "spawn")


def test_serve_source_starts_no_process():
    tree = ast.parse(SERVE.read_text())
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {a.name.split(".")[0] for a in node.names} & PROCESS_MODULES
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in PROCESS_MODULES:
                found.add(node.module)
            if node.module == "os":
                found |= {a.name for a in node.names
                          if a.name in OS_LAUNCHERS or a.name.startswith(OS_PREFIXES)}
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == "os":
            if node.attr in OS_LAUNCHERS or node.attr.startswith(OS_PREFIXES):
                found.add("os." + node.attr)
    assert sorted(found) == []
