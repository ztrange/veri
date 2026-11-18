"""In-process cases for veri/merge_common.py: the merge call's driver, given or read from VERI_GH_DRIVER. The gate is
an in-process spy, so no case starts a process."""
import importlib

import pytest

GH_MERGE = ("gh", "pr", "merge", "https://github.com/owner/repo/pull/7", "--rebase", "--match-head-commit", "abc123")
REST_PUT = ("gh", "api", "-X", "PUT", "repos/owner/repo/pulls/7/merge", "-f", "merge_method=rebase", "-f", "sha=abc123")


def _merge(monkeypatch, environment_driver, **driver):
    merge_common = importlib.import_module("veri.merge_common")
    monkeypatch.setenv("VERI_GH_DRIVER", environment_driver)
    calls = []

    def gate(*argv):
        calls.append(argv)
        return 0

    code = merge_common.merge(gate, GH_MERGE[3], "owner/repo", "7", "abc123", **driver)
    return code, calls


def test_a_given_driver_is_used_instead_of_veri_gh_driver_so_graphql_makes_exactly_the_gh_pr_merge_call(monkeypatch):
    assert _merge(monkeypatch, "rest", driver="graphql") == (0, [GH_MERGE])


@pytest.mark.parametrize("environment_driver, calls", [("rest", [REST_PUT]), ("graphql", [GH_MERGE])])
def test_with_no_driver_given_veri_gh_driver_picks_the_call(monkeypatch, environment_driver, calls):
    assert _merge(monkeypatch, environment_driver) == (0, calls)
