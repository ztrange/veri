"""In-process cases for veri/stack_tag.py, the module stack-tag.sh is a shim over (PRD 034.4c): git (git.out,
git.network), GitHub (github.gh_api) and the merge lock (stack_fix.script) are injected in-process, so no case starts a
process."""
import importlib
import json
import re
import subprocess

import pytest

PR = "https://github.com/owner/repo/pull/90"
USAGE = "usage: stack-tag.sh <slice-pr-url> [--message <n>=<text>]...\n"


@pytest.fixture
def stack_tag():
    return importlib.import_module("veri.stack_tag")


@pytest.mark.parametrize("argv", [
    [],
    [PR, PR],
    [PR, "--message"],
    [PR, "--message", "seven=text"],
    [PR, "--message", "7"],
    ["--message", "7=text"],
])
def test_any_argument_list_but_one_url_and_message_pairs_exits_2_with_the_usage_line(run_cli, stack_tag, argv):
    code, out, err = run_cli(stack_tag, argv)

    assert (code, out, err) == (2, "", USAGE)
