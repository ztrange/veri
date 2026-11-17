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


# The calls PREFLIGHT.md step 3 names for a worktree issue-worktree.sh handed back (RP15).
HANDED_BACK_IN_STEP_3 = ("resume-clean.sh", "rebase-onto-default.sh", "event.sh resume-rebase",
                         "tests-frozen.sh rerecord-rebased", "push-branch.sh --force-with-lease")


def test_4023_every_call_preflight_md_step_3_names_for_a_handed_back_worktree_is_in_the_scripts_ordered_list():
    preflight = importlib.import_module("veri.preflight")
    text = PREFLIGHT_MD.read_text()
    step_3 = text[text.index("\n3. **"):text.index("\n4. **")]

    assert [call for call in HANDED_BACK_IN_STEP_3 if "$S/" + call not in step_3] == []
    assert [call for call in HANDED_BACK_IN_STEP_3 if call not in preflight.HANDED_BACK] == []
