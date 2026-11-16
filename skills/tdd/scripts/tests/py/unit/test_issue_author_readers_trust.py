"""A ratchet: every module of veri/ that lists issues decides whose issue may be taken through github.trusted_author.

The rule an issue's author must meet before its body reaches a leaf lives in one function (PRD 022.4, AU1), shared with
the comment rule (github.trusted_comment calls it); a lister with its own copy, or none, lets a stranger's issue that
someone labelled be taken. "Lists issues" is read with `ast`, by what a module names: the fixture name `issues.json`, or
a string holding a REST issue listing path (`…/issues?…`). "Goes through the rule" is a call of `trusted_author`.

Blind spots, by construction: an issue listing path built from parts that never meet in one literal or f-string, and a
reader that lists issues through github.gh_issue_list (dispatch's state read, which takes no issue).
"""
import ast
import re

import pytest

# Modules of veri/ (by stem, sorted, ONE per line) that list issues and need not decide by their author, each with why. A
# listed module that no longer lists issues fails the second case below.
EXEMPT = {
    "invisible_work": "reads issue numbers and states only, to report branches; it takes no issue",
    "parked_issues": "reports the parked issues and decides their comments through trusted_comment; it takes no issue",
    "workqueue": "hands out items the operator queued by hand; it reads the listing for states and Blocked by only",
}

# The listers PRD 022.4 puts behind the rule; the detector must keep finding them.
KNOWN_READERS = ("solvable_issues",)

_LIST = re.compile(r"^issues\.json$|/issues\?")


def _literals(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.value
        elif isinstance(node, ast.JoinedStr):
            yield "".join(part.value for part in node.values if isinstance(part, ast.Constant))


def _lists_issues(tree):
    return any(_LIST.search(text) for text in _literals(tree))


def _calls_the_rule(tree):
    return any(isinstance(node, ast.Call) and (getattr(node.func, "attr", None) or getattr(node.func, "id", None))
               == "trusted_author" for node in ast.walk(tree))


def _readers(veri_modules_index):
    return sorted(name for name in veri_modules_index.names if _lists_issues(veri_modules_index.tree(name)))


@pytest.mark.tree_audit("every module of veri/")
def test_every_module_listing_issues_decides_their_author_through_github_trusted_author(veri_modules_index):
    readers = _readers(veri_modules_index)
    bypassing = [name for name in readers if name not in EXEMPT and not _calls_the_rule(veri_modules_index.tree(name))]

    assert set(KNOWN_READERS) <= set(readers), f"the detector no longer finds {sorted(set(KNOWN_READERS) - set(readers))}"
    assert not bypassing, (
        f"{bypassing} list issues without github.trusted_author: take an issue only when its author is trusted, so a "
        f"stranger's labelled issue is not taken, or list the module in EXEMPT with why it need not")


@pytest.mark.tree_audit("every module of veri/")
def test_an_exempt_module_that_no_longer_lists_issues_is_removed_from_the_list(veri_modules_index):
    gone = [name for name in EXEMPT if name not in _readers(veri_modules_index)]

    assert not gone, f"{gone} no longer list issues: remove them from EXEMPT"


@pytest.mark.parametrize("source, lists", [
    ('gh_json("issues.json", "repos/{owner}/{repo}/issues?state=all&per_page=100")', True),
    ("gh_rest_list(f'repos/{repo}/issues?state=open')", True),
    ('gh_issue_view(7, "body")', False),
])
def test_an_issue_listing_fixture_or_path_counts_as_listing_issues(source, lists):
    assert _lists_issues(ast.parse(source)) is lists


def test_the_exempt_list_is_sorted():
    assert list(EXEMPT) == sorted(EXEMPT)
