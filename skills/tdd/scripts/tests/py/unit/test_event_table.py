"""veri/event_table.py is the one table of every event veri emits and its keys (PRD 030.1)."""
import ast

from conftest import SCRIPTS

TABLE = SCRIPTS / "veri" / "event_table.py"


def test_the_table_module_imports_no_other_veri_module():
    tree = ast.parse(TABLE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    siblings = sorted(name for name in imported if name == "veri" or (SCRIPTS / "veri" / f"{name}.py").exists())

    assert not siblings, f"veri/event_table.py imports veri modules {siblings}; it must be readable alone"
