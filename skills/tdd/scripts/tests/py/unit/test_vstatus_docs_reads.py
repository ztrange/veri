"""README.md and CLAUDE.md name none of the reads /vstatus dropped (#2751 criterion 2)."""
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[6]

DROPPED_READS = (
    "report-cache.sh refresh",
    "status.sh --json",
    "metrics.sh",
    "git tag",
    "gh pr list",
    "solvable-issues.sh",
    "pmset",
    "status-last",
    "subagent",
)


def dropped_reads_named(text):
    """Every (line, read) where a line naming /vstatus or the status report also names a dropped read."""
    found = []
    for line in text.splitlines():
        if "vstatus" not in line.lower() and "status report" not in line.lower():
            continue
        found += [(line, read) for read in DROPPED_READS if read in line]
    return found


@pytest.mark.parametrize("name", ["README.md", "CLAUDE.md"])
def test_the_doc_names_none_of_the_reads_vstatus_dropped(name):
    assert dropped_reads_named((REPO / name).read_text()) == []
