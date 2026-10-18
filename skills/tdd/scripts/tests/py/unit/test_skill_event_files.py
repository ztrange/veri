"""SKILL.md hands Stopping and the reconcile leaf to STOPPING.md and RECONCILE.md, read as text (#1716)."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def _lines():
    return SKILL.read_text().splitlines()


def test_every_line_sending_the_run_to_stopping_points_at_stopping_md_1716():
    """Subject is source text: each line of SKILL.md that sends the run to *Stopping* names the file to read."""
    sends = [line for line in _lines() if re.search(r"\bgo(es)? to \*Stopping\*", line)]

    assert len(sends) >= 5
    assert [line for line in sends if "`<base directory>/STOPPING.md`" not in line] == []


def test_every_line_launching_the_reconcile_leaf_points_at_reconcile_md_1716():
    """Subject is source text: each line of SKILL.md naming the reconcile leaf names the file to read."""
    launches = [line for line in _lines() if "reconcile leaf" in line]

    assert len(launches) >= 2
    assert [line for line in launches if "`<base directory>/RECONCILE.md`" not in line] == []


def test_skill_md_no_longer_carries_the_stopping_or_reconciling_sections_1716():
    """Subject is source text: the moved sections and their distinctive lines are gone from SKILL.md."""
    text = SKILL.read_text()

    assert [line for line in _lines() if line in ("## Stopping", "## Reconciling a rejected push")] == []
    assert [marker for marker in ("event.sh stop mode=", "reconcile-ledger.before") if marker in text] == []
