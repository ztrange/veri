"""In-process cases for run_leaf.launch_spec: what a leaf is launched with, decided without a pipe or a process."""
import importlib
import os

import pytest


@pytest.fixture
def run_leaf(monkeypatch):
    monkeypatch.delenv("VERI_LEAF_TOOLS", raising=False)
    return importlib.import_module("veri.run_leaf")


def spec(run_leaf, environ=None, *, git_path="/tmp/gitcfg", shell="/opt/bash", seconds="900",
         binary="claude", model="", extra=()):
    return run_leaf.launch_spec(environ if environ is not None else {"PATH": "/usr/bin"},
                                git_path, shell, seconds, binary, model, list(extra))


def test_launch_spec_argv_is_the_binary_the_stream_options_the_model_only_when_non_empty_and_the_callers_arguments_in_order(
        run_leaf):
    head = ["-p", "--output-format", "stream-json", "--verbose"]
    limits = run_leaf.context_limits()
    tools = ["--tools", run_leaf.DEFAULT_TOOLS]
    for binary, model, extra, tail in (
            ("claude", "", [], []),
            ("/stub/claude", "", ["--x"], ["--x"]),
            ("/stub/claude", "a model", ["--a", "", "b"], ["--model", "a model", "--a", "", "b"])):
        argv, _ = spec(run_leaf, binary=binary, model=model, extra=extra)
        assert argv == [binary, *head, *limits, *tools, *tail]


def test_launch_spec_leaves_a_model_flag_in_the_callers_arguments_alone(run_leaf):
    argv, _ = spec(run_leaf, model="sonnet", extra=["--model", "haiku"])
    assert argv.count("--model") == 1 and argv[-2:] == ["--model", "haiku"]


def test_launch_spec_sets_the_private_git_config_whatever_the_caller_held(run_leaf):
    _, env = spec(run_leaf, {"GIT_CONFIG_GLOBAL": "/operator/gitconfig"}, git_path="/tmp/private")
    assert env["GIT_CONFIG_GLOBAL"] == "/tmp/private"


@pytest.mark.parametrize("name,held", [
    ("PYTHONDONTWRITEBYTECODE", "0"),
    ("FORCE_PROMPT_CACHING_5M", ""),
    ("CLAUDE_CODE_DISABLE_BACKGROUND_TASKS", "0"),
])
def test_launch_spec_forces_the_flag_to_1_whatever_the_caller_held_or_left_unset(run_leaf, name, held):
    assert spec(run_leaf, {name: held})[1][name] == "1"
    assert spec(run_leaf, {})[1][name] == "1"


def test_launch_spec_names_the_given_bash_as_shell_and_claude_code_shell_whatever_the_caller_held(run_leaf):
    _, env = spec(run_leaf, {"SHELL": "/bin/zsh", "CLAUDE_CODE_SHELL": "/bin/zsh"}, shell="/opt/bash")
    assert (env["SHELL"], env["CLAUDE_CODE_SHELL"]) == ("/opt/bash", "/opt/bash")


def test_launch_spec_sets_both_bash_tool_timeouts_to_the_cap_in_milliseconds(run_leaf):
    _, env = spec(run_leaf, seconds="120")
    assert (env["BASH_DEFAULT_TIMEOUT_MS"], env["BASH_MAX_TIMEOUT_MS"]) == ("120000", "120000")


def test_launch_spec_keeps_each_bash_tool_timeout_the_caller_set_and_fills_only_the_other(run_leaf):
    _, env = spec(run_leaf, {"BASH_DEFAULT_TIMEOUT_MS": "5"}, seconds="120")
    assert (env["BASH_DEFAULT_TIMEOUT_MS"], env["BASH_MAX_TIMEOUT_MS"]) == ("5", "120000")
    _, env = spec(run_leaf, {"BASH_MAX_TIMEOUT_MS": "7"}, seconds="120")
    assert (env["BASH_DEFAULT_TIMEOUT_MS"], env["BASH_MAX_TIMEOUT_MS"]) == ("120000", "7")


@pytest.mark.parametrize("seconds", ["abc", "", "1.5"])
def test_launch_spec_raises_value_error_for_a_cap_that_is_not_a_whole_number(run_leaf, seconds):
    with pytest.raises(ValueError):
        spec(run_leaf, seconds=seconds)


def test_launch_spec_puts_the_guard_first_on_path_whether_the_caller_held_one_or_not(run_leaf):
    assert spec(run_leaf, {"PATH": "/usr/bin"})[1]["PATH"] == run_leaf.GUARD + os.pathsep + "/usr/bin"
    assert spec(run_leaf, {})[1]["PATH"] == run_leaf.GUARD + os.pathsep


def test_launch_spec_drops_the_shims_locale_marker_and_pythoncoerceclocale_only_when_the_marker_is_1(run_leaf):
    _, env = spec(run_leaf, {"VERI_SHIM_SET_COERCE": "1", "PYTHONCOERCECLOCALE": "0"})
    assert "VERI_SHIM_SET_COERCE" not in env and "PYTHONCOERCECLOCALE" not in env
    for marker in ("0", ""):
        _, env = spec(run_leaf, {"VERI_SHIM_SET_COERCE": marker, "PYTHONCOERCECLOCALE": "0"})
        assert (env["VERI_SHIM_SET_COERCE"], env["PYTHONCOERCECLOCALE"]) == (marker, "0")
    _, env = spec(run_leaf, {"PYTHONCOERCECLOCALE": "0"})
    assert env["PYTHONCOERCECLOCALE"] == "0"


def test_launch_spec_removes_the_conductors_session_variables_and_values_carrying_its_session_id(run_leaf):
    _, env = spec(run_leaf, {"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "abc123", "CLAUDE_PID": "9",
                             "CLAUDE_AUTO_BACKGROUND_TASKS": "1", "CARRIER": "x-abc123-y",
                             "VERI_KEEP": "abc123", "CLAUDE_BIN": "abc123", "KEEP": "ok", "PATH": "/p"})
    assert sorted(env) == ["BASH_DEFAULT_TIMEOUT_MS", "BASH_MAX_TIMEOUT_MS",
                           "CLAUDE_BIN", "CLAUDE_CODE_DISABLE_BACKGROUND_TASKS", "CLAUDE_CODE_SHELL",
                           "FORCE_PROMPT_CACHING_5M", "GIT_CONFIG_GLOBAL", "KEEP", "PATH",
                           "PYTHONDONTWRITEBYTECODE", "SHELL", "VERI_KEEP"]


def test_launch_spec_passes_every_other_variable_through_and_leaves_the_incoming_environment_untouched(run_leaf):
    held = {"VERI_TEST_CMD": "make", "CLAUDE_CODE_SESSION_ID": "s", "VERI_SHIM_SET_COERCE": "1", "PATH": "/p"}
    before = dict(held)
    _, env = spec(run_leaf, held)
    assert env["VERI_TEST_CMD"] == "make" and held == before
