"""No file under skills/ names the retired idle reset (#3890)."""
import pytest

from conftest import ROOT


@pytest.mark.tree_audit("every file under skills/")
def test_no_file_under_skills_names_the_idle_wait_or_the_idle_reset_request():
    needles = ["reset-wait.sh" + " idle", "request-reset" + " --idle"]
    hits = []
    for path in sorted((ROOT / "skills").rglob("*")):
        if not path.is_file():
            continue
        text = path.read_bytes().decode("utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            if any(needle in line for needle in needles):
                hits.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")

    assert hits == []
