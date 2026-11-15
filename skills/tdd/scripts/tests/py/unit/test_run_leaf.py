"""In-process cases for veri/run_leaf.py, the module run-leaf.sh is a shim over."""
import importlib


def test_leaf_argv_with_veri_leaf_tools_unset_passes_a_default_tools_list_naming_the_tools_the_leaf_prompts_use_3180(
        monkeypatch):
    run_leaf = importlib.import_module("veri.run_leaf")
    monkeypatch.delenv("VERI_LEAF_TOOLS", raising=False)

    argv = run_leaf.leaf_argv("claude", None, [])

    tools = argv[argv.index("--tools") + 1].split(",") if "--tools" in argv else []
    assert {"Bash", "Read", "Edit", "Write", "Grep", "Glob"} - set(tools) == set()


def test_leaf_argv_with_veri_leaf_tools_set_passes_exactly_that_list_and_not_the_default_3180(monkeypatch):
    run_leaf = importlib.import_module("veri.run_leaf")
    monkeypatch.setenv("VERI_LEAF_TOOLS", "Read,Grep")

    argv = run_leaf.leaf_argv("claude", None, [])

    assert (argv.count("--tools"), argv[argv.index("--tools") + 1]) == (1, "Read,Grep")


def test_leaf_argv_with_veri_leaf_tools_set_empty_passes_an_empty_tools_value_not_the_default_3180(monkeypatch):
    run_leaf = importlib.import_module("veri.run_leaf")
    monkeypatch.setenv("VERI_LEAF_TOOLS", "")

    argv = run_leaf.leaf_argv("claude", None, [])

    assert (argv.count("--tools"), argv[argv.index("--tools") + 1]) == (1, "")


def test_leaf_argv_keeps_a_tools_flag_in_the_callers_arguments_and_adds_no_second_one_3180(monkeypatch):
    run_leaf = importlib.import_module("veri.run_leaf")
    monkeypatch.setenv("VERI_LEAF_TOOLS", "Read,Grep")

    argv = run_leaf.leaf_argv("claude", None, ["--tools", "Bash"])

    assert (argv.count("--tools"), argv[-2:]) == (1, ["--tools", "Bash"])
