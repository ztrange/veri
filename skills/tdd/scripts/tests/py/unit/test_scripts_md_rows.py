"""Every `$S/<script>.sh` bullet in skills/tdd/SCRIPTS.md is graded by an SC row."""
import re

import pytest

from conftest import SCRIPTS

TDD_DIR = SCRIPTS.parent


def test_every_scripts_md_bullet_has_an_sc_row_2486():
    catalogue = (TDD_DIR / "SCRIPTS.md").read_text()
    requirements = (TDD_DIR / "REQUIREMENTS.md").read_text()
    section = requirements.split("\n## skills/tdd/SCRIPTS.md\n", 1)[1]
    section = re.split(r"^## ", section, maxsplit=1, flags=re.M)[0]
    rows = [line for line in section.splitlines() if re.match(r"\| SC\d+ \|", line)]
    bullets = re.findall(r"^- `\$S/([\w.-]+\.sh)", catalogue, flags=re.M)
    missing = [b for b in bullets if not any(b in row for row in rows)]
    assert bullets and rows
    assert not missing, f"{len(bullets)} bullets, {len(rows)} SC rows; no SC row for: {missing}"


UNCATALOGUED = frozenset(
    {
    "affected-suites.sh",
    "comment-class.sh",
    "cover-outcome.sh",
    "coverage-blocker.sh",
    "criterion-finished.sh",
    "exhausted-outcome.sh",
    "grade-prose.sh",
    "graded-changed.sh",
    "harvest-usage.sh",
    "install-links.sh",
    "invisible-work.sh",
    "leaf-launchable.sh",
    "leaf-model.sh",
    "leaf-role.sh",
    "leaf-timeout.sh",
    "ledger-steps.sh",
    "no-product-caller.sh",
    "orchestrate.sh",
    "parallel-conductors.sh",
    "preserve-attempt.sh",
    "production-frozen.sh",
    "profile.sh",
    "rebase-onto-default.sh",
    "red-divergence.sh",
    "refactor-touched.sh",
    "refactor-triage.sh",
    "replaces-case-survivors.sh",
    "requirements.sh",
    "run-affordable.sh",
    "run-conductor.sh",
    "run-finished.sh",
    "skill-drift.sh",
    "stale-rows.sh",
    "step-budget.sh",
    "step-cost.sh",
    "structural-predicate.sh",
    "suite-reported.sh",
    "tier-usual.sh",
    "time-budget.sh",
    "timed-test-run.sh",
    "unlabel-issue.sh",
    "unreachable.sh",
    "unreplaced-cases.sh",
    "workqueue.sh",
    "wrong-test-route.sh",
    }
)


def _scripts_without_bullet(scripts_dir, catalogue, excluded):
    bullets = set(re.findall(r"^- `\$S/([\w.-]+\.sh)", catalogue, flags=re.M))
    listed = {p.name for p in scripts_dir.glob("*.sh")}
    return sorted(listed - bullets - excluded)


@pytest.mark.tree_audit("lists skills/tdd/scripts/*.sh and a scratch scripts dir")
def test_every_script_has_a_scripts_md_bullet_3549(tmp_path):
    catalogue = (TDD_DIR / "SCRIPTS.md").read_text()
    unbulleted = _scripts_without_bullet(SCRIPTS, catalogue, UNCATALOGUED)
    assert not unbulleted, f"scripts with no `- $S/<name>.sh` bullet in SCRIPTS.md: {unbulleted}"

    scratch = tmp_path / "scripts"
    scratch.mkdir()
    for name in ("known-gap.sh", "new-entry.sh"):
        (scratch / name).write_text("#!/bin/sh\nexit 0\n")
    assert _scripts_without_bullet(scratch, "", frozenset({"known-gap.sh"})) == ["new-entry.sh"]


def test_scripts_md_bullet_guard_is_not_read_as_a_red_subsection_reader_3549():
    import importlib.util
    from pathlib import Path

    from conftest import TestFile

    here = Path(__file__).resolve()
    spec = importlib.util.spec_from_file_location("red_readers_3549", here.parent / "test_skill_red_readers.py")
    readers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(readers)
    subsection, rest = readers._subsection_and_rest()
    flagged = readers._readers(TestFile(here), subsection, rest)
    assert not [n for n in flagged if n.endswith("_3549")], f"read as a Red-subsection reader: {flagged}"
