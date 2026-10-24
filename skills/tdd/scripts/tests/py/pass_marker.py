import importlib


def write_pass_marker(root, step, head, tree="tree"):
    """Write root's check-earlier pass marker for step, naming head and tree."""
    path = root / importlib.import_module("veri.tests_frozen")._pass_marker_path(step)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"step: {step}\nhead: {head}\ntree: {tree}\n")
    return path
