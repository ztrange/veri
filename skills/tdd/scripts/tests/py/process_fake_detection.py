"""Which test source installs its own fake on `subprocess`: the detection behind unit/test_local_process_fakes.py.

A pure function over source text, kept out of the audit file so the audit itself only queries the shared tests_py_index."""
import ast

PROCESS_STARTERS = ("run", "Popen", "check_output", "check_call", "call", "getoutput", "getstatusoutput")


def _is_subprocess_module(node):
    return (isinstance(node, ast.Name) and node.id == "subprocess") or (
        isinstance(node, ast.Attribute) and node.attr == "subprocess")


def _names_a_starter_path(text):
    parts = text.split(".")
    return len(parts) >= 2 and parts[-2] == "subprocess" and parts[-1] in PROCESS_STARTERS


def _string_target_installs(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return _names_a_starter_path(node.value)
    if isinstance(node, ast.JoinedStr):
        head = node.values[0] if node.values else None
        return (isinstance(head, ast.Constant) and isinstance(head.value, str) and head.value.endswith(".")
                and head.value[:-1].split(".")[-1] == "subprocess")
    return False


def _installs_on_subprocess(call):
    args = call.args
    method = call.func.attr
    if method == "setattr" and len(args) >= 2 and _is_subprocess_module(args[0]):
        name = args[1]
        return not (isinstance(name, ast.Constant) and isinstance(name.value, str)) or name.value in PROCESS_STARTERS
    if method in ("setattr", "patch") and args and _string_target_installs(args[0]):
        return True
    if method == "object" and len(args) >= 2 and _is_subprocess_module(args[0]):
        return isinstance(args[1], ast.Constant) and args[1].value in PROCESS_STARTERS
    return False


def installs_a_subprocess_fake(source):
    """True when <source> replaces how subprocess starts a process (see the module docstring for what counts)."""
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and _installs_on_subprocess(node):
            return True
        if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Attribute) and target.attr in PROCESS_STARTERS
                and _is_subprocess_module(target.value) for target in node.targets):
            return True
    return False
