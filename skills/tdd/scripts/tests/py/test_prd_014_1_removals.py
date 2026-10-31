"""PRD 014.1: the old dashboard, render-leaf-log and session-cost are gone."""
from conftest import SCRIPTS

DASHBOARD = "dash" + "board"
RENDER = "render" + "-leaf-" + "log"
RENDER_PY = "render" + "_leaf_" + "log"
COST = "session" + "-cost"
COST_PY = "session" + "_cost"


def test_no_path_under_the_prd_014_1_remove_list_exists():
    removed = [
        f"{DASHBOARD}.sh",
        f"{DASHBOARD}.html",
        f"veri/{DASHBOARD}.py",
        f"{RENDER}.sh",
        f"veri/{RENDER_PY}.py",
        f"tests/fixtures/{RENDER}",
        f"{COST}.sh",
        f"veri/{COST_PY}.py",
        f"tests/py/test_{DASHBOARD}.py",
        f"tests/py/test_{RENDER_PY}.py",
        f"tests/py/test_{COST_PY}.py",
    ]
    assert [p for p in removed if (SCRIPTS / p).exists()] == []
