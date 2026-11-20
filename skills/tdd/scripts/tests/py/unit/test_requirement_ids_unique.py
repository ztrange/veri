"""A requirement row ID names one row in its REQUIREMENTS.md, not just within one unit's table.

`requirements.claims` refuses a duplicate only inside one `## <unit>` table, so the same ID under two units of
one list never collided and six such pairs landed in skills/tdd/REQUIREMENTS.md. Each REQUIREMENTS.md is its own
namespace: the same ID in two lists (README.md's RD rows and develop-red.md's, say) is not a collision.
"""
import glob
import importlib
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[6]


@pytest.mark.tree_audit("every REQUIREMENTS.md in the repository, outside dot directories")
def test_no_requirement_row_id_appears_twice_in_one_requirements_list_across_its_units(monkeypatch):
    requirements = importlib.import_module("veri.requirements")
    monkeypatch.chdir(ROOT)
    # Found without git, as requirements.tracked would find them: a unit case may not start git (#4016).
    duplicates = {}
    for path in sorted(glob.glob("**/REQUIREMENTS.md", recursive=True)):
        where = defaultdict(list)
        for unit in requirements.listed_units(path):
            for row in requirements.claims(path, unit).splitlines():
                where[row.split("\t", 1)[0]].append(unit)
        duplicates.update({"%s %s" % (path, rid): units for rid, units in sorted(where.items()) if len(units) > 1})

    assert duplicates == {}, duplicates
