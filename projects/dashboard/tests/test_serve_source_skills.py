import ast
import pathlib

SERVE = pathlib.Path(__file__).resolve().parents[1] / "serve.py"


def mentions_skills(node):
    return any(isinstance(n, ast.Constant) and isinstance(n.value, str) and "skills" in n.value
               for n in ast.walk(node))


def touches_sys_path(node):
    return any(isinstance(n, ast.Attribute) and n.attr == "path"
               and isinstance(n.value, ast.Name) and n.value.id == "sys"
               for n in ast.walk(node))


def test_serve_source_imports_nothing_under_skills_and_adds_no_skills_path():
    tree = ast.parse(SERVE.read_text())
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [a.name for a in node.names if a.name.split(".")[0] == "skills"]
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] == "skills":
                found.append(node.module)
        elif isinstance(node, ast.stmt) and touches_sys_path(node) and mentions_skills(node):
            found.append("sys.path line %d" % node.lineno)
    assert found == []
