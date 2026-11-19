"""`make ceiling` is test-ceiling.sh's one entry point (#4418, HW15): one ramp is hours of full suites, the human's call
on an idle machine, so no other make target, CI job, procedure file, prompt or script runs it."""
import os
import re

import pytest

import unreachable
from conftest import ROOT

SHIM = "test-ceiling.sh"
# The files that may name the shim: itself, the module behind it, its catalogue entries and its tests.
DESCRIBES = {"skills/tdd/scripts/test-ceiling.sh", "skills/tdd/scripts/veri/ceiling.py", "skills/tdd/SCRIPTS.md",
             "skills/tdd/scripts/veri/README.md"}


def recipes(makefile):
    """Each Makefile target mapped to its recipe's text."""
    targets, current = {}, None
    for line in makefile.splitlines():
        rule = re.match(r"^([\w-]+(?: [\w-]+)*):(?!=)", line)
        if rule:
            current = rule.group(1)
            for name in current.split():
                targets.setdefault(name, "")
        elif line.startswith("\t") and current:
            for name in current.split():
                targets[name] += line + "\n"
        elif not line.startswith("\t"):
            current = None
    return targets


def namers(top, skip):
    for parent, dirs, files in os.walk(top):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".tdd", "tests")]
        for name in files:
            path = os.path.join(parent, name)
            rel = os.path.relpath(path, ROOT)
            if rel in skip or not name.endswith((".md", ".sh", ".py", ".yml", ".yaml")):
                continue
            with open(path, errors="replace") as f:
                if SHIM in f.read():
                    yield rel


@pytest.mark.tree_audit("the Makefile, .github/ and skills/ for test-ceiling.sh")
def test_make_ceiling_is_the_one_entry_point_of_test_ceiling_sh():
    makefile = (ROOT / "Makefile").read_text()
    targets = recipes(makefile)

    assert any("ceiling" in line.split() for line in re.findall(r"^\.PHONY:(.*)$", makefile, flags=re.M))
    assert "skills/tdd/scripts/test-ceiling.sh" in targets["ceiling"]
    assert [name for name, recipe in targets.items() if SHIM in recipe] == ["ceiling"]
    assert list(namers(str(ROOT / ".github"), set())) == []
    assert sorted(namers(str(ROOT / "skills"), DESCRIBES)) == []


@pytest.mark.tree_audit("skills/tdd/scripts and the entry points unreachable.sh walks")
def test_unreachable_does_not_list_test_ceiling_sh():
    listed = [line.decode() for line in unreachable.listing(os.fsencode(str(ROOT)))]

    assert not [line for line in listed if SHIM in line]
