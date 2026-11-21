"""PRD 041.2: the dev session's reset scripts, their modules and their tests are gone (R12, #4465)."""
from conftest import ROOT

SCRIPTS = "skills/tdd/scripts/"
DELETED = [SCRIPTS + p for p in (
    "role-growth.sh", "reset-wait.sh", "veri/role_growth.py", "veri/reset_wait.py",
    "tests/py/test_reset_wait_process.py", "tests/py/unit/test_role_growth.py",
    "tests/py/unit/test_reset_wait.py", "tests/py/unit/test_no_idle_reset_sweep.py")]


def test_issue_4465_no_dev_reset_script_module_or_test_exists():
    assert [p for p in DELETED if (ROOT / p).exists()] == []


def test_issue_4465_veri_readme_names_no_deleted_script_or_module():
    readme = (ROOT / SCRIPTS / "veri" / "README.md").read_text()

    assert [n for n in ("role-growth.sh", "reset-wait.sh", "role_growth", "reset_wait") if n in readme] == []
