"""PRD 013.9 (#4075): the absolute plan-growth knob is retired, so no tracked file names it outside the ones that say so."""
import subprocess

import pytest

import conftest
from conftest import ROOT

RETIRED = "VERI_STEP_GROWTH"

# The files that name the knob as retired: the code that refuses it, the prose that says so, the rows and the ADR.
NAMING_IT_AS_RETIRED = {
    "skills/tdd/scripts/veri/tunables.py",
    "skills/tdd/scripts/veri/add_ledger_step.py",
    "skills/tdd/scripts/veri/ledger_growth.py",
    "skills/tdd/scripts/veri/preflight.py",
    "skills/tdd/PREFLIGHT.md",
    "skills/tdd/PREFLIGHT-FAILURES.md",
    "skills/tdd/SCRIPTS.md",
    "skills/tdd/BAIL.md",
    "skills/tdd/REQUIREMENTS.md",
    "docs/adr/0022-the-ledger-grows-mid-run.md",
}


def naming_the_retired_knob(listed):
    """The paths of `git grep -lw` output that name the retired knob without being allowed to."""
    return sorted(path for path in listed.split("\n") if path and path not in NAMING_IT_AS_RETIRED)


def test_4075_a_listed_path_outside_the_allowed_files_is_named_and_an_allowed_one_is_not():
    listed = "skills/tdd/BAIL.md\nCLAUDE.md\ndocs/adr/0022-the-ledger-grows-mid-run.md\nREADME.md\n"

    assert naming_the_retired_knob(listed) == ["CLAUDE.md", "README.md"]


@pytest.mark.process("git: git grep -lw over the repository's tracked files")
@pytest.mark.tree_audit("every tracked file outside .tdd/, specs/ and skills/tdd/scripts/tests/")
def test_4075_no_tracked_file_names_the_retired_step_growth_knob_save_those_naming_it_as_retired(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    found = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-lw", RETIRED, "--", ".", ":!.tdd", ":!specs", ":!skills/tdd/scripts/tests"],
        capture_output=True, text=True,
    )

    assert (found.returncode in (0, 1), naming_the_retired_knob(found.stdout)) == (True, []), found.stderr
