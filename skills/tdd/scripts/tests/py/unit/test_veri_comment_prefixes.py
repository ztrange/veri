"""A ratchet: every emoji heading a module of veri/ writes (`### <emoji> …`, how each comment veri posts begins) is one
github.VERI_COMMENT_PREFIXES lists, so a reader of human answers (park_decision) never takes veri's own comment for one.

Read with `ast`: each string literal, and each f-string's leading literal part, that starts with `### ` and a non-ASCII
character. Blind spot, by construction: a heading assembled from parts that never meet in one literal.
"""
import ast
import importlib

import pytest


def _headings(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
        elif isinstance(node, ast.JoinedStr) and node.values and isinstance(node.values[0], ast.Constant):
            text = node.values[0].value
        else:
            continue
        if text.startswith("### ") and len(text) > 4 and not text[4].isascii():
            yield text.split("\n", 1)[0]


def _unlisted(trees, prefixes):
    return sorted({h for tree in trees for h in _headings(tree) if not h.startswith(prefixes)})


@pytest.mark.tree_audit("every module of veri/")
def test_every_emoji_heading_a_veri_module_writes_starts_with_a_listed_veri_comment_prefix(veri_modules_index):
    prefixes = importlib.import_module("veri.github").VERI_COMMENT_PREFIXES

    unlisted = _unlisted([veri_modules_index.tree(name) for name in veri_modules_index.names], prefixes)

    assert not unlisted, f"{unlisted}: add each to github.VERI_COMMENT_PREFIXES, or a human answer may be read as veri's"


def test_a_new_emoji_heading_in_a_literal_or_an_f_string_is_named_and_an_ascii_heading_is_not():
    source = 'post(f"### 🧪 Probe — {x}")\nprint("### ✅ Done")\nprint("### The step")\n'

    assert _unlisted([ast.parse(source)], ("### ✅ Done",)) == ["### 🧪 Probe — "]
