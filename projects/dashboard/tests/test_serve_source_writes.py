import ast
import pathlib

SERVE = pathlib.Path(__file__).resolve().parents[1] / "serve.py"

MUTATORS = {"write_text", "write_bytes", "mkdir", "makedirs", "touch", "unlink", "remove",
            "rmdir", "removedirs", "rename", "renames", "replace", "symlink", "symlink_to",
            "link", "hardlink_to", "truncate", "ftruncate", "copy", "copy2", "copyfile",
            "copytree", "move", "rmtree", "mkfifo", "mknod", "mkstemp", "mkdtemp",
            "NamedTemporaryFile", "TemporaryFile", "TemporaryDirectory"}


def test_serve_source_opens_nothing_for_writing_and_creates_moves_or_removes_nothing():
    tree = ast.parse(SERVE.read_text())
    imported = set()
    mutating = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if name in MUTATORS:
                mutating.add(name)
            if name in {"open", "fdopen"}:
                mode_at = 1 if isinstance(f, ast.Name) else 0
                modes = node.args[mode_at:mode_at + 1] + [
                    k.value for k in node.keywords if k.arg in {"mode", "flags"}]
                if any(not isinstance(m, ast.Constant) or set(str(m.value)) & set("wax+")
                       for m in modes):
                    mutating.add("open-for-write")
    bad_imports = sorted(imported & {"shutil", "tempfile", "fileinput", "tarfile", "zipfile"})
    assert (bad_imports, sorted(mutating)) == ([], [])
