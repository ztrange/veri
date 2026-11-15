"""queued_merge copies RELEASE_FILES beside merge_lock.py to release the lock after the worktree is gone: no module it copies may import a sibling it does not copy."""
import ast

import pytest

import queued_merge


def sibling_imports(tree, siblings):
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return found & set(siblings)


@pytest.mark.tree_audit("parses the veri/*.py modules RELEASE_FILES copies and the siblings they import")
def test_every_sibling_a_release_file_imports_is_itself_a_release_file(veri_modules_index):
    copied = {name[len("veri/"):-len(".py")] for name in queued_merge.RELEASE_FILES
              if name.startswith("veri/") and name.endswith(".py")}
    missing = sorted(f"{module} imports {sibling}, which RELEASE_FILES does not copy"
                     for module in copied
                     for sibling in sibling_imports(veri_modules_index.tree(module), veri_modules_index.names)
                     if sibling not in copied)

    assert not missing, missing
