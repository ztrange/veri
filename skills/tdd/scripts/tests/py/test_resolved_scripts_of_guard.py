from pathlib import Path

import pytest

VERI = Path(__file__).resolve().parents[2] / "veri"
INLINE = "os.path.dirname(os.path.dirname(os.path.realpath(__file__)))"
MODULES = ["queued_merge.py", "ready_check.py", "restart_conductor.py", "status.py",
           "tick_ledger.py", "comment.py", "update_veri.py"]


@pytest.mark.tree_audit("veri modules' source")
def test_no_listed_veri_module_computes_its_scripts_directory_inline():
    offenders = [name for name in MODULES if INLINE in (VERI / name).read_text()]
    assert offenders == [], f"{offenders} compute the scripts directory inline; use paths.resolved_scripts_of(__file__)"
