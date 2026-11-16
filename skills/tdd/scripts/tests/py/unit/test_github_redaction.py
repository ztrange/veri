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


def test_redact_replaces_a_fine_grained_github_pat_token_with_redacted_issue_3960(github):
    token = "github_pat_" + FAKE * 2 + "_" + FAKE * 5

    assert github.redact("pat=%s;" % token) == "pat=[redacted];"


def test_redact_replaces_an_sk_ant_key_with_redacted_issue_3960(github):
    key = "sk-ant-api03-" + FAKE + "_" + FAKE

    assert github.redact("key %s\n" % key) == "key [redacted]\n"


def test_redact_replaces_an_akia_access_key_id_with_redacted_issue_3960(github):
    assert github.redact("id=AKIAFAKE0123FAKE0123 ok") == "id=[redacted] ok"


def test_redact_replaces_every_occurrence_of_a_listed_variables_value_issue_3960(github, monkeypatch):
    monkeypatch.setenv("VERI_REDACT_VARS", "FAKE_SECRET")
    monkeypatch.setenv("FAKE_SECRET", "not-a-real-secret")

    assert github.redact("a not-a-real-secret b not-a-real-secret") == "a [redacted] b [redacted]"


def test_redact_leaves_alone_a_listed_variables_value_shorter_than_8_characters_issue_3960(github, monkeypatch):
    monkeypatch.setenv("VERI_REDACT_VARS", "FAKE_SHORT")
    monkeypatch.setenv("FAKE_SHORT", "a1b2c3d")

    assert github.redact("a1b2c3d stays") == "a1b2c3d stays"


def test_veri_redact_vars_defaults_to_gh_token_and_names_another_variable_when_set_issue_3960(github, monkeypatch):
    monkeypatch.delenv("VERI_REDACT_VARS", raising=False)
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")
    monkeypatch.setenv("FAKE_DEPLOY_KEY", "fake-deploy-key-value")
    unset = github.redact("fake-gh-token-value fake-deploy-key-value")
    monkeypatch.setenv("VERI_REDACT_VARS", "FAKE_DEPLOY_KEY")

    assert (unset, github.redact("fake-gh-token-value fake-deploy-key-value")) == (
        "[redacted] fake-deploy-key-value", "fake-gh-token-value [redacted]")


def posted(fake_processes, answer=(0, "https://github.com/o/r/issues/7#issuecomment-1\n", "")):
    """fake_processes answering every gh call with <answer>; the returned fake's argvs are what gh was handed."""
    return fake_processes.answers({"gh": answer})


def test_gh_issue_comment_hands_gh_the_body_redacted_issue_3960(github, fake_processes):
    token = "ghp_" + FAKE * 3
    fake = posted(fake_processes)

    github.gh_issue_comment("7", "leaf said %s\n" % token)

    assert "body=leaf said [redacted]\n" in fake.argvs[-1] and token not in " ".join(fake.argvs[-1])
