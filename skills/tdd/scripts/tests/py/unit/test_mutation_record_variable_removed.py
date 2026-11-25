"""No file under veri/ names the retired mutation-record variable (#4741)."""
from pathlib import Path

import pytest

VERI = Path(__file__).resolve().parents[3] / "veri"


@pytest.mark.tree_audit("every file under veri/")
def test_4741_no_file_under_veri_names_the_mutation_record_variable():
    naming = sorted(str(path.relative_to(VERI)) for path in VERI.rglob("*")
                    if path.is_file() and "__pycache__" not in path.parts
                    and b"VERI_MUTATION_RECORD" in path.read_bytes())

    assert naming == []
