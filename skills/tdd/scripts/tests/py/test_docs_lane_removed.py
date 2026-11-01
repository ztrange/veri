"""The generated docs page and its docs lane are gone from the tree."""
import subprocess

import pytest

import conftest
from conftest import ROOT


def test_no_path_under_the_removal_list_exists():
    walk = "walk" + "through"
    docs_owed = "docs" + "-owed.sh"
    merge_gates = "merge" + "-gates.sh"
    removed = [
        f"docs/{walk}.html",
        f"docs/build-{walk}.py",
        f"docs/check-{walk}.py",
        "docs/" + "wt",
        f"docs/{docs_owed}",
        f"docs/{merge_gates}",
        "docs/hooks",
        "docs/tests",
        "projects/docs",
        ".github/workflows/pages.yml",
        "skills/tdd/scripts/tests/py/test_docs_targets_refuse_process.py",
    ]

    assert [p for p in removed if (ROOT / p).exists()] == []


def test_make_has_none_of_the_docs_lane_targets():
    import re

    named = {"docs", "docs-test", "docs" + "-fresh", "docs" + "-check", "merge-gates", "install-hooks"}
    defined = set()
    for line in (ROOT / "Makefile").read_text().splitlines():
        if line.startswith("\t") or line.startswith("#"):
            continue
        m = re.match(r"([^:=]+?)\s*::?(?!=)", line)
        if m:
            defined.update(m.group(1).split())
        phony = re.match(r"\.PHONY\s*:(.*)", line)
        if phony:
            defined.update(phony.group(1).split())

    assert sorted(named & defined) == []


@pytest.mark.process("git: git grep -iE over the repository's tracked files")
@pytest.mark.tree_audit("every tracked file outside docs/adr/, .tdd/ and the test fixtures")
def test_no_tracked_file_outside_the_record_names_the_removed_page_or_its_lane(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    pattern = "|".join(["walk" + "through", "docs" + "-check", "docs" + "-fresh", "docs" + "-owed", "docs/" + "wt"])
    found = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-iE", pattern, "--", ".",
         ":!docs/adr", ":!.tdd", ":!skills/tdd/scripts/tests/fixtures"],
        capture_output=True, text=True,
    )
    assert found.returncode == 1 and found.stdout == ""


def test_docs_adr_keeps_every_record_it_had():
    at_branch_point = [
        "0001-claude-p-subprocess-substrate.md",
        "0002-programmatic-supervisor.md",
        "0003-blind-independent-verifier.md",
        "0004-bounded-revise-loop-on-reject.md",
        "0005-github-issue-as-observability-channel.md",
        "0006-plan-post-loop-to-done.md",
        "0007-local-ledger-issue-mirror.md",
        "0008-branch-per-issue-draft-pr.md",
        "0009-generality-via-triangulation.md",
        "0010-refactor-loop-with-post-loop-verdict.md",
        "0011-bail-preserves-progress-and-classifies-failure.md",
        "0012-already-satisfied-is-a-step-outcome.md",
        "0013-issue-branch-in-its-own-worktree.md",
        "0014-per-run-event-log-written-by-the-scripts.md",
        "0015-a-bug-is-an-issue-kind-not-a-phase.md",
        "0016-uncovered-lines-are-debt-the-page-reports.md",
        "0017-one-refactor-leaf-per-step.md",
        "0018-a-preamble-token-is-priced-per-night.md",
        "0019-the-contingent-half-of-skill-md-stays-resident.md",
        "0020-a-clean-exit-with-no-verdict-is-relaunched.md",
        "0021-green-is-obvious-implementation.md",
        "0022-the-ledger-grows-mid-run.md",
        "0023-a-test-framework-is-priced-per-example.md",
        "0024-the-open-pr-is-the-claim.md",
        "0025-rung-3-is-n-supervised-conductors.md",
        "0026-three-modules-under-the-entry-points.md",
        "0027-a-port-moves-coverage-and-the-old-suite-proves-it.md",
        "0028-veri-reaches-github-over-rest-through-one-port.md",
        "0029-the-scripts-are-python-behind-sh-shims.md",
        "0030-tests-change-by-parallel-change-and-mutation-parity.md",
        "0031-a-run-does-a-refactor-now-or-drops-it.md",
        "GRADED",
        "REQUIREMENTS.md",
    ]

    assert [n for n in at_branch_point if not (ROOT / "docs" / "adr" / n).exists()] == []
