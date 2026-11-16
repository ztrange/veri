"""The `uses:` lines of each workflow under .github/workflows/, read as text the way GitHub Actions reads them."""
import re

import pytest

from conftest import ROOT

WORKFLOWS = ROOT / ".github/workflows"

def read_lines(path):
    return path.read_bytes().decode("utf-8", "surrogateescape").split("\n")


def pin_problems(path):
    """One refusal per `uses:` line of <path> whose ref is not a 40-hex commit sha followed by a `# v<tag>`
    comment, naming file and line."""
    problems = []
    for number, line in enumerate(read_lines(path), 1):
        found = re.match(r"\s*(?:- )?uses:\s*([^\s#]+)\s*(#.*)?$", line)
        if not found:
            continue
        if not re.search(r"@[0-9a-f]{40}$", found.group(1)):
            problems.append("%s:%d: uses: does not name a 40-hex commit sha (%s)" % (path.name, number, found.group(1)))
        elif not re.match(r"#\s*v[0-9][0-9A-Za-z.+-]*\s*$", found.group(2) or ""):
            problems.append("%s:%d: uses: has no trailing comment naming its tag (%s)" % (path.name, number, found.group(1)))
    return problems


def test_a_uses_line_not_naming_a_40_hex_commit_sha_is_refused_naming_the_file_and_line(tmp_path):
    fixture = tmp_path / "ci.yml"
    fixture.write_text(
        "jobs:\n  gates:\n    steps:\n      - uses: actions/checkout@v4\n"
        "      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5\n"
        "      - name: restore\n        uses: actions/cache/restore@0057852bfaa8 # v4\n"
    )

    assert pin_problems(fixture) == [
        "ci.yml:4: uses: does not name a 40-hex commit sha (actions/checkout@v4)",
        "ci.yml:7: uses: does not name a 40-hex commit sha (actions/cache/restore@0057852bfaa8)",
    ]


def test_a_sha_pinned_uses_line_without_a_trailing_comment_naming_its_tag_is_refused_naming_the_file_and_line(tmp_path):
    fixture = tmp_path / "ci.yml"
    fixture.write_text(
        "      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262\n"
        "      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # pinned\n"
        "      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5\n"
        "        uses: actions/cache/save@0057852bfaa89a56745cba8c7296529d2fc39830  # v4.2.3\n"
    )

    assert pin_problems(fixture) == [
        "ci.yml:1: uses: has no trailing comment naming its tag (actions/checkout@11d5960a326750d5838078e36cf38b85af677262)",
        "ci.yml:2: uses: has no trailing comment naming its tag (actions/checkout@11d5960a326750d5838078e36cf38b85af677262)",
    ]


@pytest.mark.tree_audit("the workflow files under .github/workflows")
def test_every_uses_line_under_github_workflows_names_a_40_hex_commit_sha_followed_by_its_tag():
    files = sorted(p for pattern in ("*.yml", "*.yaml") for p in WORKFLOWS.glob(pattern) if p.is_file())
    problems = [problem for wf in files for problem in pin_problems(wf)]
    if not any(re.search(r"^\s*(- )?uses:", line, re.M) for line in (wf.read_text() for wf in files)):
        problems.append("no uses: line found under .github/workflows/ — the sweep read nothing")

    assert problems == []
