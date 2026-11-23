"""A ratchet: every module of veri/ that reads pull requests decides which may claim an issue, or count as a run PR,
through github.Pull.cross_repository, so a fork's PR, which anyone can open, claims nothing (PRD 022.14-022.16).

"Reads pull requests" is read with `ast`, by what a module names: github.py's PR readers `open_pulls`,
`open_pulls_text`, `pulls_in`, `joined_issues` and `stack_pulls`, or `closed_issues`, the reader of a body's `Closes #n`. "Goes
through the rule" is naming the attribute `cross_repository`. Inside github.py, every function that reads a body's
`Closes #n` names it too (joined_issues, the stack's joined claim).

Blind spots, by construction: a module that reaches GitHub's pulls without naming any of the six (a raw `gh api`
path), and one that names `cross_repository` without filtering on it.
"""
import ast

import pytest

# Modules of veri/ (by stem, sorted, ONE per line) that read pull requests and need not decide by cross_repository, each
# with why. A listed module that names cross_repository, or no longer reads pull requests, fails a case below.
EXEMPT = {
    "github": "the home of the readers and of Pull.cross_repository; its own Closes #n readers are checked below",
    "invisible_work": "reports branches no PR names, by head ref only; it claims, launches and skips nothing",
    "stack_culprit": "reads github.stack_pulls only to find the tracking pull request it comments on; it claims nothing",
    "stack_fix": "reads github.stack_pulls only to find the tracking pull request it comments on; it claims nothing",
    "stack_pr": "reads github.stack_pulls, which reads no Closes #n and already keeps only a head in this repository",
    "status": "status.sh --recover prints the open PRs for the operator to read; it claims, launches and skips nothing",
}

# The readers PRD 022.14-022.16 put behind the rule; the detector must keep finding them.
KNOWN_READERS = ("dispatch_reads", "issue_worktree", "parallel_conductors", "solvable_issues")

_READERS = {"open_pulls", "open_pulls_text", "pulls_in", "joined_issues", "stack_pulls", "closed_issues"}


def _names(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            yield node.attr
        elif isinstance(node, ast.Name):
            yield node.id
        elif isinstance(node, ast.alias):
            yield node.name


def _reads_pulls(tree):
    return bool(_READERS & set(_names(tree)))


def _decides_by_the_rule(tree):
    return "cross_repository" in set(_names(tree))


def _readers(veri_modules_index):
    return sorted(name for name in veri_modules_index.names if _reads_pulls(veri_modules_index.tree(name)))


@pytest.mark.tree_audit("every module of veri/")
def test_every_module_reading_pull_requests_decides_a_claim_through_pull_cross_repository(veri_modules_index):
    readers = _readers(veri_modules_index)
    bypassing = [name for name in readers if name not in EXEMPT and not _decides_by_the_rule(veri_modules_index.tree(name))]

    assert set(KNOWN_READERS) <= set(readers), f"the detector no longer finds {sorted(set(KNOWN_READERS) - set(readers))}"
    assert not bypassing, (
        f"{bypassing} read pull requests without github.Pull.cross_repository: count a PR's claim only when its head is "
        f"in this repository, so a fork's PR claims nothing, or list the module in EXEMPT with why it need not")


@pytest.mark.tree_audit("every module of veri/")
def test_an_exempt_module_that_no_longer_reads_pull_requests_or_now_decides_by_the_rule_is_removed_from_the_list(
        veri_modules_index):
    readers = _readers(veri_modules_index)
    stale = [name for name in EXEMPT if name != "github"
             and (name not in readers or _decides_by_the_rule(veri_modules_index.tree(name)))]

    assert not stale, f"{stale} no longer read pull requests or now decide by cross_repository: remove them from EXEMPT"


@pytest.mark.tree_audit("veri/github.py")
def test_every_function_of_github_reading_a_body_s_closes_decides_by_cross_repository(veri_modules_index):
    functions = [node for node in ast.walk(veri_modules_index.tree("github")) if isinstance(node, ast.FunctionDef)
                 and node.name != "closed_issues" and "closed_issues" in set(_names(node))]

    assert [node.name for node in functions] == ["joined_issues"], "the detector no longer finds joined_issues"
    assert all(_decides_by_the_rule(node) for node in functions), "joined_issues reads Closes #n without cross_repository"


@pytest.mark.parametrize("source, reads", [
    ("from github import pulls_in", True),
    ("github.open_pulls('body')", True),
    ("github.closed_issues(pr.body)", True),
    ("github.pull(7)", False),
])
def test_a_module_naming_a_pull_request_reader_counts_as_reading_pull_requests(source, reads):
    assert _reads_pulls(ast.parse(source)) is reads


def test_the_exempt_list_is_sorted():
    assert list(EXEMPT) == sorted(EXEMPT)
