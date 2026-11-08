import ast
import pathlib

SERVE = pathlib.Path(__file__).resolve().parents[1] / "serve.py"

WRITERS = {"write_text", "write_bytes", "mkdir", "touch", "unlink", "rename", "replace",
           "system", "popen", "Popen", "run", "call", "check_output", "execv", "execvp", "fork"}


def test_serve_source_opens_only_runs_and_report_cache_and_runs_nothing():
    tree = ast.parse(SERVE.read_text())
    imported = set()
    calls = set()
    literals = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
        elif isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            calls.add(name)
            if name == "open":
                args = node.args[1:2] + [k.value for k in node.keywords if k.arg == "mode"]
                if any(isinstance(a, ast.Constant) and set(a.value) & set("wax+") for a in args):
                    calls.add("open-for-write")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)

    bad_imports = sorted(m for m in imported if m.split(".")[0] in {"subprocess", "skills"})
    bad_calls = sorted(calls & (WRITERS | {"open-for-write"}))
    stray = sorted(s for s in literals
                   if ("skills" in s or s.endswith((".json", ".jsonl", ".log", ".md")))
                   and s not in {"*.jsonl", "report-cache.json", "report-owed.json"}
                   and not s.startswith(("/", "<", "%", "Usage")) and "\n" not in s)
    assert (bad_imports, bad_calls, stray) == ([], [], [])
