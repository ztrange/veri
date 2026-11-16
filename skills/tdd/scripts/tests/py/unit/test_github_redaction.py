"""In-process cases for github.redact, the one function every body veri hands gh passes through (#3960, #3968).

Every token here is built from a documented shape with an obviously fake body; none is read from the environment."""
import importlib

import pytest

FAKE = "FAKEfake0123"  # 12 letters and digits, mixed case: three make a 36-character classic body


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


@pytest.mark.parametrize("prefix", ["ghp_", "gho_", "ghu_", "ghs_", "ghr_"])
def test_redact_replaces_a_token_of_each_github_prefix_with_redacted_issue_3960(github, prefix):
    token = prefix + FAKE * 3

    assert github.redact("before %s after" % token) == "before [redacted] after"
