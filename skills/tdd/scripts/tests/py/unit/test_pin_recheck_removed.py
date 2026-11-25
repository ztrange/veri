"""pin-recheck.sh, its module and the mutation record's module are gone, and no script names them (#4741)."""
import re
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[3]
NAMES = re.compile(r"pin[-_]recheck|mutation_record\b|REPIN_STEP")


@pytest.mark.tree_audit("every shim and every module under veri/")
def test_4741_no_pin_recheck_or_mutation_record_module_or_shim_exists_and_no_script_names_them(veri_modules_index):
    present = [name for name in ("pin-recheck.sh", "veri/pin_recheck.py", "veri/mutation_record.py")
               if (SCRIPTS / name).exists()]
    shims = sorted(path.name for path in SCRIPTS.glob("*.sh")
                   if NAMES.search(path.read_text(encoding="utf-8", errors="replace")))
    modules = sorted(name for name in veri_modules_index.names if NAMES.search(veri_modules_index.text(name)))

    assert (present, shims, modules) == ([], [], [])
