"""Guard: preflight.py's ordered list of steps names exactly PREFLIGHT.md's numbered steps."""
import importlib
import re
from pathlib import Path

PREFLIGHT_MD = Path(__file__).resolve().parents[4] / "PREFLIGHT.md"


def test_3771_steps_list_names_exactly_the_numbered_steps_of_preflight_md():
    preflight = importlib.import_module("veri.preflight")
    doc_steps = [int(m.group(1)) for m in re.finditer(r"^(\d+)\. \*\*", PREFLIGHT_MD.read_text(), re.M)]
    listed = [k for k, _ in preflight.STEPS]

    assert [k for k in doc_steps if k not in listed] == []
    assert [k for k in listed if k not in doc_steps] == []
