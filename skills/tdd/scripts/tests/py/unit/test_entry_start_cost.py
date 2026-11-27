"""A script starts once per leaf, so a module's level imports only what every start needs.

The table names, per module, the costly stdlib imports a rare path alone needs; each is imported inside the
function that uses it. An AST check, never a timing: the cost shows in `python3 -B -X importtime -c "import <module>"`.
"""
import ast
import importlib
import inspect

import pytest

RARE_PATH_IMPORTS = {
    "entry": {"traceback": "loads _colorize, dataclasses and inspect (about 20 ms): only refusal() needs it"},
    "harvest_usage": {"traceback": "only the crash path prints one, and supervise imports this module at every leaf start"},
    "wait_ci": {"traceback": "only the unexpected-error paths of the poll loop print one; ready_check imports this module"},
    "status": {"statistics": "only eta_range() needs it, and only once three runs have finished"},
    "pytest_leg": {"concurrent.futures": "only the cache sweep's thread pool needs it"},
    "event": {"github": "pulls run_records (about 20 ms): only state_labels() needs it, with VERI_STATE_LABEL_ISSUE set"},
}


def module_level_imports(module):
    return {
        alias.name
        for node in ast.parse(inspect.getsource(module)).body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(node.module)])
    }


@pytest.mark.parametrize(
    "module_name, name", [(m, n) for m, names in RARE_PATH_IMPORTS.items() for n in names]
)
def test_module_does_not_import_a_rare_path_module_at_module_level(module_name, name):
    module = importlib.import_module(module_name)  # flat: pytest_leg lives in tests/leg/, not veri/ (#4051)

    assert name not in module_level_imports(module), (
        "%s: %s (import it inside the function that needs it)" % (name, RARE_PATH_IMPORTS[module_name][name])
    )
