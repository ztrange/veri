"""A ratchet: every module of veri/ that reads issue or PR comments decides who may speak through github.trusted_comment.

The rule a comment must meet to change what a run, the dispatcher or the operator's release does lives in one function
(PRD 022.3, "Where the comment-trust rule lives"); a reader with its own copy, or none, lets a stranger's comment steer a
run. "Reads comments" is read with `ast`, by what a module names: a string holding a REST comments path
(`…/comments?…`, or one ending in `/comments`), the JSON field `comments` (`"comments"`, `"number,comments"`), or
`issue_comments` / `_comments`, github.py's readers of comments. "Goes through the rule" is a call of `trusted_comment`.

Blind spots, by construction: a comments path built from parts that never meet in one literal or f-string, and a reader
that reaches GitHub without naming any of the three.
"""
import ast
import re

import pytest

# Modules of veri/ (by stem, sorted, ONE per line) that read comments and need not go through trusted_comment, each with
# why. A listed module that no longer reads comments fails the second case below.
EXEMPT = {
    "github": "the home of the readers and of trusted_comment itself",
    "plan_publish": "posts step 2b's start comment through the comments path; reads no comment",
    "pointer_comment": "matches only its own pointer comment, by the gh login alone (stricter than trust): it edits it",
    "report_cache": "reports links and metrics fields only; nothing it reads changes a run (PRD 022, not in the set)",
}

# The readers PRD 022.3 and 022.11-022.13 put behind the rule; the detector must keep finding them.
KNOWN_READERS = ("dispatch_reads", "issue_decisions", "park_decision", "parked_issues", "release_issue", "run_conductor")

_READ = re.compile(r"/comments(\?|$)|^comments$|^comments,|,comments(,|$)")


def _literals(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.value
        elif isinstance(node, ast.JoinedStr):
            yield "".join(part.value for part in node.values if isinstance(part, ast.Constant))


def _names(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            yield node.attr
        elif isinstance(node, ast.Name):
            yield node.id


def _reads_comments(tree):
    return any(_READ.search(text) for text in _literals(tree)) or bool({"issue_comments", "_comments"} & set(_names(tree)))


def _calls_the_rule(tree):
    return any(isinstance(node, ast.Call) and (getattr(node.func, "attr", None) or getattr(node.func, "id", None))
               == "trusted_comment" for node in ast.walk(tree))


def _readers(veri_modules_index):
    return sorted(name for name in veri_modules_index.names if _reads_comments(veri_modules_index.tree(name)))


@pytest.mark.tree_audit("every module of veri/")
def test_every_module_reading_comments_decides_trust_through_github_trusted_comment(veri_modules_index):
    readers = _readers(veri_modules_index)
    bypassing = [name for name in readers if name not in EXEMPT and not _calls_the_rule(veri_modules_index.tree(name))]

    assert set(KNOWN_READERS) <= set(readers), f"the detector no longer finds {sorted(set(KNOWN_READERS) - set(readers))}"
    assert not bypassing, (
        f"{bypassing} read issue or PR comments without github.trusted_comment: filter the comments through it, so a "
        f"stranger's comment cannot speak for a run, or list the module in EXEMPT with why it need not")


@pytest.mark.tree_audit("every module of veri/")
def test_an_exempt_module_that_no_longer_reads_comments_is_removed_from_the_list(veri_modules_index):
    gone = [name for name in EXEMPT if name not in _readers(veri_modules_index)]

    assert not gone, f"{gone} no longer read comments: remove them from EXEMPT"


@pytest.mark.parametrize("source", [
    'github.rest_items("repos/{owner}/{repo}/issues/%s/comments" % n)',
    "github.rest_items(f'repos/o/r/issues/{n}/comments')",
    "github._comments(n)",
])
def test_a_comments_path_with_no_query_or_github_comments_counts_as_a_read(source):
    assert _reads_comments(ast.parse(source))


def test_the_exempt_list_is_sorted():
    assert list(EXEMPT) == sorted(EXEMPT)
