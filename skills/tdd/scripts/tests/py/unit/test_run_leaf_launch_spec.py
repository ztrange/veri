"""In-process cases for run_leaf.launch_spec: what a leaf is launched with, decided without a pipe or a process."""
import importlib
import json
import os
import shlex
import sys

import pytest


@pytest.fixture
def run_leaf(monkeypatch):
    monkeypatch.delenv("VERI_LEAF_TOOLS", raising=False)
    return importlib.import_module("veri.run_leaf")


def spec(run_leaf, environ=None, *, git_path="/tmp/gitcfg", shell="/opt/bash", seconds="900",
         binary="claude", model="", extra=(), coerce_marker=""):
    return run_leaf.launch_spec(environ if environ is not None else {"PATH": "/usr/bin"},
                                git_path, shell, seconds, binary, model, list(extra), coerce_marker)


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


def test_4013_veri_effort_verifier_adds_no_effort_to_a_leaf_the_caller_launched_without_one(run_leaf, monkeypatch):
    """A develop-*, revise-* or adjudicate-* leaf is launched as supervise.sh <name> run-leaf.sh <prompt> <flags>,
    with no --effort among the flags; run-leaf.sh must not add one from the verifier's knob."""
    monkeypatch.setenv("VERI_EFFORT_VERIFIER", "low")
    argv, _ = spec(run_leaf, {"PATH": "/usr/bin", "VERI_EFFORT_VERIFIER": "low"}, model="opus",
                   extra=["--permission-mode", "bypassPermissions"])
    assert "--effort" not in argv


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
    _, env = spec(run_leaf, {"VERI_SHIM_SET_COERCE": "1", "PYTHONCOERCECLOCALE": "0"}, coerce_marker="1")
    assert "VERI_SHIM_SET_COERCE" not in env and "PYTHONCOERCECLOCALE" not in env
    for marker in ("0", ""):
        _, env = spec(run_leaf, {"VERI_SHIM_SET_COERCE": marker, "PYTHONCOERCECLOCALE": "0"},
                      coerce_marker=marker)
        assert (env["VERI_SHIM_SET_COERCE"], env["PYTHONCOERCECLOCALE"]) == (marker, "0")
    _, env = spec(run_leaf, {"PYTHONCOERCECLOCALE": "0"})
    assert env["PYTHONCOERCECLOCALE"] == "0"


def test_launch_spec_removes_the_conductors_session_variables_and_values_carrying_its_session_id(run_leaf):
    _, env = spec(run_leaf, {"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "abc123", "CLAUDE_PID": "9",
                             "CLAUDE_AUTO_BACKGROUND_TASKS": "1", "CARRIER": "x-abc123-y",
                             "VERI_KEEP": "abc123", "CLAUDE_BIN": "abc123", "HOME": "ok", "PATH": "/p"})
    assert sorted(env) == ["BASH_DEFAULT_TIMEOUT_MS", "BASH_MAX_TIMEOUT_MS",
                           "CLAUDE_BIN", "CLAUDE_CODE_DISABLE_BACKGROUND_TASKS", "CLAUDE_CODE_SHELL",
                           "FORCE_PROMPT_CACHING_5M", "GIT_CONFIG_GLOBAL", "HOME", "PATH",
                           "PYTHONDONTWRITEBYTECODE", "SHELL", "VERI_KEEP"]


def test_launch_spec_passes_an_allow_listed_variable_through_and_leaves_the_incoming_environment_untouched(run_leaf):
    held = {"VERI_TEST_CMD": "make", "CLAUDE_CODE_SESSION_ID": "s", "VERI_SHIM_SET_COERCE": "1", "PATH": "/p"}
    before = dict(held)
    _, env = spec(run_leaf, held, coerce_marker="1")
    assert env["VERI_TEST_CMD"] == "make" and held == before


ALLOWED = {"PATH": "/usr/bin", "HOME": "/h", "TMPDIR": "/t", "PWD": "/w", "USER": "u", "LOGNAME": "u",
           "LANG": "C", "LC_ALL": "C", "LC_CTYPE": "C", "VERI_TEST_CMD": "make", "CLAUDE_BIN": "/c",
           "REVISE_BUDGET": "3", "VERIFY_LEAF_ARGS": "--x", "PYTHONCOERCECLOCALE": "0",
           "ANTHROPIC_API_KEY": "k", "CLAUDE_CODE_OAUTH_TOKEN": "o", "ANTHROPIC_BASE_URL": "b",
           "CLAUDE_CONFIG_DIR": "d", "HTTPS_PROXY": "p", "HTTP_PROXY": "p", "NO_PROXY": "n",
           "NODE_EXTRA_CA_CERTS": "c"}


def test_3976_launch_spec_passes_only_allow_listed_names_and_drops_every_credential_no_list_names(run_leaf):
    _, env = spec(run_leaf, {**ALLOWED, "GH_TOKEN": "g", "GITHUB_TOKEN": "g", "AWS_SECRET_ACCESS_KEY": "a",
                             "SOME_UNLISTED": "s"})
    assert not {"GH_TOKEN", "GITHUB_TOKEN", "AWS_SECRET_ACCESS_KEY", "SOME_UNLISTED"} & set(env)
    assert {name: env[name] for name in ALLOWED if name != "PATH"} == {
        name: value for name, value in ALLOWED.items() if name != "PATH"}


def test_3976_veri_leaf_env_adds_its_names_to_the_allow_list_and_no_other(run_leaf):
    _, env = spec(run_leaf, {"VERI_LEAF_ENV": "JAVA_HOME", "JAVA_HOME": "/jdk", "GH_TOKEN": "g"})
    assert (env.get("JAVA_HOME"), "GH_TOKEN" in env) == ("/jdk", False)


def test_3976_ssh_auth_sock_reaches_a_develop_and_a_verify_leaf_and_gh_token_reaches_neither(run_leaf):
    verify = importlib.import_module("veri.verify")
    held = {"SSH_AUTH_SOCK": "/agent.sock", "GH_TOKEN": "g"}
    for extra in (["--permission-mode", "bypassPermissions"], verify.leaf_args(None)):
        _, env = spec(run_leaf, held, extra=extra)
        assert (env.get("SSH_AUTH_SOCK"), "GH_TOKEN" in env) == ("/agent.sock", False)


def leaf_settings(argv):
    """Every --settings value of a leaf's argv, parsed."""
    return [json.loads(argv[at + 1]) for at, word in enumerate(argv) if word == "--settings"]


def test_a_verify_leaf_has_one_settings_carrying_the_write_ban_pre_tool_use_hook_and_a_develop_or_revise_leaf_has_none(run_leaf):
    verify = importlib.import_module("veri.verify")
    ban = os.path.join(os.path.dirname(os.path.abspath(verify.__file__)), "verifier_write_ban.py")
    develop, _ = spec(run_leaf, model="sonnet", extra=["--permission-mode", "bypassPermissions"])
    verifier, _ = spec(run_leaf, model="sonnet", extra=verify.leaf_args(None))

    [settings] = leaf_settings(verifier)
    [developer] = leaf_settings(develop)
    assert settings.pop("hooks", None) == {"PreToolUse": [{"matcher": "Write|Edit|MultiEdit|NotebookEdit", "hooks": [
        {"type": "command", "command": shlex.join([sys.executable, ban]) + " || exit 2"}]}]}
    assert (settings, "hooks" in developer) == (developer, False)


@pytest.mark.parametrize("tools", [None, "Bash,Read"])
def test_a_verify_leaf_gets_the_tools_value_a_develop_leaf_gets_and_no_disallowed_tools(run_leaf, monkeypatch, tools):
    if tools is not None:
        monkeypatch.setenv("VERI_LEAF_TOOLS", tools)
    verify = importlib.import_module("veri.verify")
    develop, _ = spec(run_leaf, extra=["--permission-mode", "bypassPermissions"])
    verifier, _ = spec(run_leaf, extra=verify.leaf_args(None))

    def given(argv):
        return [argv[at + 1] for at, word in enumerate(argv) if word == "--tools"]
    assert (given(verifier), "--disallowedTools" in verifier) == ([tools or run_leaf.DEFAULT_TOOLS], False)
    assert given(develop) == given(verifier)


def test_every_json_object_a_caller_passes_as_settings_is_merged_into_the_one_settings_flag(run_leaf):
    argv, _ = spec(run_leaf, extra=["--settings", '{"hooks": {"PreToolUse": []}}', "--x",
                                    "--settings", '{"env": {"A": "1"}}'])
    [settings] = leaf_settings(argv)
    assert (settings["hooks"], settings["env"], settings["autoMemoryEnabled"], argv[-1]) == (
        {"PreToolUse": []}, {"A": "1"}, False, "--x")


@pytest.mark.parametrize("value", ["/etc/leaf-settings.json", "[1]", "{not json"])
def test_main_refuses_a_callers_settings_that_is_not_a_json_object_with_exit_2_naming_it_and_launches_nothing(
        run_leaf, value, tmp_path, monkeypatch, run_cli, fake_processes):
    prompt = tmp_path / "leaf.prompt"
    prompt.write_text("hello")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    calls = fake_processes()

    code, out, err = run_cli(run_leaf, [str(prompt), "--settings", value])

    assert (code, out, err, calls) == (
        2, "", "run-leaf.sh: --settings %r is not a JSON object, so it cannot be merged into the leaf's"
               " one --settings\n" % value, [])


def test_3976_a_veri_leaf_env_name_veri_redact_vars_also_names_passes_with_one_stderr_line_naming_it_never_its_value(
        run_leaf, tmp_path, monkeypatch, run_cli, fake_processes):
    prompt = tmp_path / "leaf.prompt"
    prompt.write_text("hello")
    for name, value in (("HOME", str(tmp_path)), ("TMPDIR", str(tmp_path)), ("CLAUDE_BIN", "/stub/claude"),
                        ("VERI_LEAF_ENV", "GH_TOKEN JAVA_HOME"), ("GH_TOKEN", "ghvalue-not-printed"),
                        ("JAVA_HOME", "/jdk")):
        monkeypatch.setenv(name, value)
    launched = fake_processes.answers({"claude": FileNotFoundError(2, "No such file or directory")})

    _, _, err = run_cli(run_leaf, [str(prompt)])

    [(_, kwargs)] = launched.seen
    named = [line for line in err.splitlines() if "GH_TOKEN" in line]
    assert (len(named), "ghvalue-not-printed" in err, "JAVA_HOME" in err) == (1, False, False)
    assert kwargs["env"]["GH_TOKEN"] == "ghvalue-not-printed"


def test_3976_one_stderr_line_names_each_veri_leaf_env_item_that_is_not_a_variable_name_and_the_leaf_still_launches(
        run_leaf, tmp_path, monkeypatch, run_cli, fake_processes):
    prompt = tmp_path / "leaf.prompt"
    prompt.write_text("hello")
    for name, value in (("HOME", str(tmp_path)), ("TMPDIR", str(tmp_path)), ("CLAUDE_BIN", "/stub/claude"),
                        ("VERI_LEAF_ENV", "A=B JAVA_* 9LIVES UNSET_BUT_VALID")):
        monkeypatch.setenv(name, value)
    launched = fake_processes.answers({"claude": FileNotFoundError(2, "No such file or directory")})

    _, _, err = run_cli(run_leaf, [str(prompt)])

    named = [line for line in err.splitlines() if "VERI_LEAF_ENV" in line]
    assert (len(named), [item in named[0] for item in ("A=B", "JAVA_*", "9LIVES")] if named else None,
            "UNSET_BUT_VALID" in err, len(launched.seen)) == (1, [True, True, True], False, 1)
