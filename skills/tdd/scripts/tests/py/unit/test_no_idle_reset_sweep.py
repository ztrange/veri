"""No file under skills/ names the retired idle reset (#3890)."""
import pytest

from conftest import ROOT


def _hits(root):
    """`<path>:<line>: <text>` for every line of every file under `root/skills` naming a retired invocation."""
    needles = ["reset-wait.sh" + " idle", "request-reset" + " --idle"]
    hits = []
    for path in sorted((root / "skills").rglob("*")):
        if not path.is_file():
            continue
        text = path.read_bytes().decode("utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            if any(needle in line for needle in needles):
                hits.append(f"{path.relative_to(root)}:{number}: {line.strip()}")
    return hits


@pytest.mark.tree_audit("every file under skills/")
def test_no_file_under_skills_names_the_idle_wait_or_the_idle_reset_request():
    assert _hits(ROOT) == []


def test_the_sweep_finds_a_retired_invocation_in_a_file_that_is_not_markdown(tmp_path):
    script = tmp_path / "skills" / "vdev" / "scripts" / "wait.sh"
    script.parent.mkdir(parents=True)
    script.write_text("#!/bin/sh\n$S/role-state.sh dev request-reset" + " --idle\n")

    assert _hits(tmp_path) == ["skills/vdev/scripts/wait.sh:2: $S/role-state.sh dev request-reset" + " --idle"]
