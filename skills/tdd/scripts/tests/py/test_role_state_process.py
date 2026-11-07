"""Cases for veri/role_state.py that start a real process."""
import importlib
import subprocess

import pytest


@pytest.mark.process("git")
def test_coord_set_n_writes_role_coord_state_in_main_tree_and_show_prints_it(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    set_code, _, _ = run_cli(role_state, ["coord", "set", "n", "3"], cwd=repo)
    show_code, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    written = repo / ".tdd" / "role-coord.state"
    assert (set_code, show_code, written.is_file(), "3" in shown) == (0, 0, True, True)


@pytest.mark.process("git")
def test_no_arguments_and_wrong_set_argument_count_exit_2_with_usage_and_write_nothing_and_set_twice_overwrites(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    bad = [[], ["coord", "set"], ["coord", "set", "n"], ["coord", "set", "n", "3", "x"]]
    results = [run_cli(role_state, argv, cwd=repo) for argv in bad]
    codes = [code for code, _, _ in results]
    usages = ["usage: role-state.sh" in err for _, _, err in results]
    wrote = (repo / ".tdd").exists()
    run_cli(role_state, ["coord", "set", "n", "3"], cwd=repo)
    second_code, _, _ = run_cli(role_state, ["coord", "set", "n", "4"], cwd=repo)
    _, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    assert (codes, usages, wrote, second_code, "4" in shown) == ([2] * 4, [True] * 4, False, 0, True)
