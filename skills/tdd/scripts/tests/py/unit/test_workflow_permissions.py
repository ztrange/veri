"""The token permissions each workflow under .github/workflows/ grants, read as text the way GitHub Actions reads them."""
import re

import pytest

from conftest import ROOT

CI_YML = ROOT / ".github/workflows/ci.yml"
WORKFLOWS = ROOT / ".github/workflows"


def read_lines(path):
    return path.read_bytes().decode("utf-8", "surrogateescape").split("\n")


def top_level_permissions(path):
    """The entries of <path>'s top-level `permissions:` block, comments dropped; None when it has none."""
    entries = None
    for line in read_lines(path):
        if entries is None:
            found = re.match(r"permissions:\s*(.*?)\s*(#.*)?$", line)
            if found:
                entries = [found.group(1)] if found.group(1) else []
        elif re.match(r"[^\s#]", line):
            break
        else:
            text = line.split("#", 1)[0].strip()
            if text:
                entries.append(text)
    return entries


def write_grants(path):
    """(line number, text) of each `write` or `write-all` a `permissions:` block at any level grants."""
    grants, block_indent = [], None
    for number, line in enumerate(read_lines(path), 1):
        text = line.split("#", 1)[0].rstrip()
        if not text.strip():
            continue
        indent = len(text) - len(text.lstrip())
        if block_indent is not None and indent <= block_indent:
            block_indent = None
        found = re.match(r"(\s*)permissions:\s*(.*)$", text)
        if found:
            if re.match(r"write", found.group(2)):
                grants.append((number, text.strip()))
            elif not found.group(2):
                block_indent = len(found.group(1))
        elif block_indent is not None and re.match(r"\s*[A-Za-z-]+:\s*write\s*$", text):
            grants.append((number, text.strip()))
    return grants


def permission_problems(path):
    problems = []
    if top_level_permissions(path) is None:
        problems.append("%s: no top-level permissions: block" % path.name)
    for number, text in write_grants(path):
        problems.append("%s:%d: grants write (%s)" % (path.name, number, text))
    return problems


def test_ci_yml_declares_a_top_level_permissions_block_whose_only_entry_is_contents_read():
    assert top_level_permissions(CI_YML) == ["contents: read"]


def test_a_workflow_without_a_top_level_permissions_block_is_refused_naming_the_file(tmp_path):
    fixture = tmp_path / "unscoped.yml"
    fixture.write_text(
        "on: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n    permissions:\n      contents: read\n"
    )

    assert permission_problems(fixture) == ["unscoped.yml: no top-level permissions: block"]


def test_a_workflow_granting_any_write_at_the_top_or_in_a_job_is_refused_naming_the_file_and_line(tmp_path):
    job_grant = tmp_path / "job-grant.yml"
    job_grant.write_text(
        "permissions:\n  contents: read\njobs:\n  label:\n    runs-on: ubuntu-latest\n"
        "    permissions:\n      contents: read\n      issues: write  # labels the issue\n"
    )
    all_grant = tmp_path / "all-grant.yaml"
    all_grant.write_text("permissions: write-all\njobs:\n  build:\n    runs-on: ubuntu-latest\n")

    assert permission_problems(job_grant) == ["job-grant.yml:8: grants write (issues: write)"]
    assert permission_problems(all_grant) == ["all-grant.yaml:1: grants write (permissions: write-all)"]


@pytest.mark.tree_audit("the workflow files under .github/workflows")
def test_every_workflow_file_declares_a_top_level_permissions_block_and_grants_no_write():
    files = sorted(p for pattern in ("*.yml", "*.yaml") for p in WORKFLOWS.glob(pattern) if p.is_file())
    problems = [problem for wf in files for problem in permission_problems(wf)]
    if not files:
        problems.append("no workflow files found under .github/workflows/")

    assert problems == []
