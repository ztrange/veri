"""skill-drift.sh's block, driven through the CLI of veri/skill_drift.py."""
import importlib

import pytest

REF = "refs/remotes/origin/main"
ABSENT = "0123456789abcdef0123456789abcdef01234567"


@pytest.fixture
def skill_drift():
    return importlib.import_module("veri.skill_drift")


def test_an_unpinned_run_or_an_unset_or_empty_skill_commit_answers_not_pinned(tmp_path, run_cli, skill_drift):
    want = "Skill drift: unavailable — run was not pinned to a skill commit\n"
    base = {"VERI_SKILL_CLONE": str(tmp_path), "VERI_SKILL_REF": REF}
    variants = {
        "unpinned": {**base, "VERI_SKILL_UNPINNED": "1", "VERI_SKILL_COMMIT": ABSENT},
        "unset": base,
        "empty": {**base, "VERI_SKILL_COMMIT": ""},
    }
    got = {name: run_cli(skill_drift, [], env=env) for name, env in variants.items()}

    assert got == {name: (0, want, "") for name in variants}
