"""entry.py is imported by most scripts at start, so its module level imports only what every start needs."""
import ast
import inspect

from veri import entry


def test_entry_does_not_import_traceback_at_module_level_since_only_an_escaped_exception_needs_it():
    module_level = {
        alias.name
        for node in ast.parse(inspect.getsource(entry)).body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(node.module)])
    }

    assert "traceback" not in module_level, (
        "traceback loads _colorize, dataclasses and inspect (about 20 ms): import it inside refusal()")
