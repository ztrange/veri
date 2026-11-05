"""SKILL.md's supersede-diff route: the diff verifier against the pre-reroute commit, no verify-pin."""
import re

from conftest import SCRIPTS

SKILL = SCRIPTS.parent / "SKILL.md"


def _route_paragraph():
    lines = SKILL.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if "print `supersede-diff" in line)
    return lines[start]


def test_issue_2868_supersede_diff_route_launches_the_diff_verifier_on_the_pre_reroute_commit_and_no_verify_pin():
    route = _route_paragraph()
    launches = re.findall(r"run-verdict\.sh [^`]*?\b(diff|pin|red|green|refactor)\b[^`]*`", route)
    command = re.search(r"run-verdict\.sh[^`]*`", route).group(0)
    assert re.search(r"--supersede-base\s+<pre-reroute-sha>\s+diff\s+\.tdd/issue-<n>-spec\.md\s+<branch-base-sha>\s+<step-base-sha>", command)
    assert "git stash create" in route
    assert launches == ["diff"]
    assert re.search(r"never verify-red and never verify-pin", route)
    assert not re.search(r"run-verdict\.sh[^`]*\bpin\b", route)
