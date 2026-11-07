"""Cases for veri/role_state.py that start a real process."""
import importlib
import subprocess
import time

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


@pytest.mark.process("git")
def test_coord_set_lane_writes_the_lane_and_show_prints_it_beside_an_earlier_n(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    n_code, _, _ = run_cli(role_state, ["coord", "set", "n", "7"], cwd=repo)
    lane_code, _, _ = run_cli(role_state, ["coord", "set", "lane", "mu"], cwd=repo)
    show_code, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    assert (n_code, lane_code, show_code, "7" in shown, "mu" in shown) == (0, 0, 0, True, True)


@pytest.mark.process("git")
def test_coord_set_n_from_a_linked_worktree_writes_into_the_main_working_tree(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    linked = tmp_path / "linked"
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "init"], cwd=repo, check=True)
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(linked)], cwd=repo, check=True)
    code, _, _ = run_cli(role_state, ["coord", "set", "n", "2"], cwd=linked)
    in_main = repo / ".tdd" / "role-coord.state"
    in_linked = linked / ".tdd" / "role-coord.state"
    assert (code, in_main.is_file(), in_linked.exists()) == (0, True, False)


@pytest.mark.process("git")
def test_coord_lane_mu_set_n_writes_the_lane_file_and_leaves_the_default_lane_file_unchanged(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    run_cli(role_state, ["coord", "set", "n", "5"], cwd=repo)
    default = repo / ".tdd" / "role-coord.state"
    before = default.read_bytes()
    code, _, _ = run_cli(role_state, ["coord", "--lane", "mu", "set", "n", "1"], cwd=repo)
    lane = repo / ".tdd" / "role-coord-mu.state"
    assert (code, lane.is_file(), default.read_bytes() == before) == (0, True, True)


@pytest.mark.process("git")
def test_coord_add_to_each_list_prints_an_id_and_show_lists_the_text(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    lists = ["decision", "message", "override", "timed-n"]
    added = [run_cli(role_state, ["coord", "add", name, "text-of-" + name], cwd=repo) for name in lists]
    _, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    codes = [code for code, _, _ in added]
    printed_ids = [out.strip() != "" for _, out, _ in added]
    listed = ["text-of-" + name in shown for name in lists]
    assert (codes, printed_ids, listed) == ([0] * 4, [True] * 4, [True] * 4)


@pytest.mark.process("git")
def test_coord_add_records_the_local_add_time_and_show_lists_it_on_the_items_line(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    before = time.strftime("%Y-%m-%d")
    run_cli(role_state, ["coord", "add", "decision", "pick-the-lane"], cwd=repo)
    after = time.strftime("%Y-%m-%d")
    _, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    line = next(l for l in shown.splitlines() if "pick-the-lane" in l)
    assert any(day in line for day in {before, after}), line


@pytest.mark.process("git")
def test_coord_drop_removes_the_item_with_that_id_from_show_and_keeps_the_other_items(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    _, first_id, _ = run_cli(role_state, ["coord", "add", "decision", "keep-alpha"], cwd=repo)
    _, second_id, _ = run_cli(role_state, ["coord", "add", "decision", "drop-beta"], cwd=repo)
    code, _, _ = run_cli(role_state, ["coord", "drop", "decision", second_id.strip()], cwd=repo)
    _, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    assert (code, "drop-beta" in shown, "keep-alpha" in shown) == (0, False, True)
