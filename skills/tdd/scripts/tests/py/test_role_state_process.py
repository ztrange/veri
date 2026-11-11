"""Cases for veri/role_state.py that start a real process."""
import importlib
import os
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
    texts = {name: "text-of-" + name for name in lists}
    texts["timed-n"] = "4 until 2026-11-10T20:00:00"
    added = [run_cli(role_state, ["coord", "add", name, texts[name]], cwd=repo) for name in lists]
    _, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    codes = [code for code, _, _ in added]
    printed_ids = [out.strip() != "" for _, out, _ in added]
    listed = [texts[name] in shown for name in lists]
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


@pytest.mark.process("git")
def test_coord_drop_of_an_item_added_after_an_earlier_drop_removes_only_it_and_keeps_the_other(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    _, first_id, _ = run_cli(role_state, ["coord", "add", "decision", "gone-alpha"], cwd=repo)
    run_cli(role_state, ["coord", "add", "decision", "stays-beta"], cwd=repo)
    run_cli(role_state, ["coord", "drop", "decision", first_id.strip()], cwd=repo)
    _, third_id, _ = run_cli(role_state, ["coord", "add", "decision", "fresh-gamma"], cwd=repo)
    run_cli(role_state, ["coord", "drop", "decision", third_id.strip()], cwd=repo)
    _, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    assert ("stays-beta" in shown, "fresh-gamma" in shown) == (True, False)


@pytest.mark.process("git")
def test_coord_add_after_a_set_prints_the_next_id_and_show_lists_the_item(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    run_cli(role_state, ["coord", "set", "n", "3"], cwd=repo)
    code, printed, _ = run_cli(role_state, ["coord", "add", "decision", "after-set-alpha"], cwd=repo)
    _, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    assert (code, printed.strip(), "after-set-alpha" in shown) == (0, "1", True)


@pytest.mark.process("git")
def test_coord_recovered_records_recovered_at_and_the_session_id_and_show_prints_them(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    code, _, _ = run_cli(role_state, ["coord", "recovered"], cwd=repo, env={"CLAUDE_CODE_SESSION_ID": "sess-4242"})
    _, shown, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    assert (code, "recovered-at" in shown, "sess-4242" in shown) == (0, True, True)


@pytest.mark.process("git")
def test_coord_recovered_without_a_session_id_exits_2_and_leaves_the_state_file_unchanged(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    state = repo / ".tdd" / "role-coord.state"
    empty_code, _, _ = run_cli(role_state, ["coord", "recovered"], cwd=repo, env={"CLAUDE_CODE_SESSION_ID": ""})
    absent_after = state.exists()
    run_cli(role_state, ["coord", "set", "n", "3"], cwd=repo)
    before = state.read_bytes()
    empty_present_code, _, _ = run_cli(role_state, ["coord", "recovered"], cwd=repo, env={"CLAUDE_CODE_SESSION_ID": ""})
    assert (empty_code, absent_after, empty_present_code, state.read_bytes() == before) == (2, False, 2, True)


@pytest.mark.process("git")
def test_coord_set_whose_rename_over_the_state_file_fails_leaves_the_previous_file_byte_for_byte_unchanged(tmp_path, run_cli, monkeypatch):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    run_cli(role_state, ["coord", "set", "n", "3"], cwd=repo)
    state = repo / ".tdd" / "role-coord.state"
    before = state.read_bytes()

    def failing_replace(src, dst, *args, **kwargs):
        raise OSError("rename refused")

    monkeypatch.setattr(os, "replace", failing_replace)
    monkeypatch.setattr(os, "rename", failing_replace)
    try:
        code, _, _ = run_cli(role_state, ["coord", "set", "n", "4"], cwd=repo)
    except OSError:
        code = "raised"
    assert (code != 0, state.read_bytes() == before) == (True, True)


@pytest.mark.process("git")
def test_coord_drop_whose_rename_over_the_state_file_fails_leaves_the_previous_file_byte_for_byte_unchanged(tmp_path, run_cli, monkeypatch):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    run_cli(role_state, ["coord", "add", "decision", "keep-alpha"], cwd=repo)
    _, second_id, _ = run_cli(role_state, ["coord", "add", "decision", "drop-beta"], cwd=repo)
    state = repo / ".tdd" / "role-coord.state"
    before = state.read_bytes()

    def failing_replace(src, dst, *args, **kwargs):
        raise OSError("rename refused")

    monkeypatch.setattr(os, "replace", failing_replace)
    monkeypatch.setattr(os, "rename", failing_replace)
    try:
        code, _, _ = run_cli(role_state, ["coord", "drop", "decision", second_id.strip()], cwd=repo)
    except OSError:
        code = "raised"
    assert (code != 0, state.read_bytes() == before) == (True, True)


@pytest.mark.process("git")
def test_coord_show_with_no_state_file_exits_3_and_prints_nothing(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    code, out, _ = run_cli(role_state, ["coord", "show"], cwd=repo)
    assert (code, out) == (3, "")


@pytest.mark.process("git")
def test_a_role_other_than_coord_or_dev_exits_2_with_usage_and_writes_no_state_file(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    code, _, err = run_cli(role_state, ["admin", "set", "n", "3"], cwd=repo)
    assert (code, "usage: role-state.sh" in err, (repo / ".tdd").exists()) == (2, True, False)


@pytest.mark.process("git")
def test_an_unknown_verb_exits_2_with_usage_and_writes_no_state_file(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    code, out, err = run_cli(role_state, ["coord", "frobnicate", "n", "3"], cwd=repo)
    assert (code, out, "usage: role-state.sh" in err, (repo / ".tdd").exists()) == (2, "", True, False)


@pytest.mark.process("git")
def test_set_with_a_field_other_than_n_or_lane_exits_2_with_usage_and_writes_no_state_file(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    code, out, err = run_cli(role_state, ["coord", "set", "color", "red"], cwd=repo)
    assert (code, out, "usage: role-state.sh" in err, (repo / ".tdd").exists()) == (2, "", True, False)


@pytest.mark.process("git")
def test_add_with_a_list_other_than_the_four_exits_2_with_usage_and_writes_no_state_file(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    code, out, err = run_cli(role_state, ["coord", "add", "gossip", "hello"], cwd=repo)
    assert (code, out, "usage: role-state.sh" in err, (repo / ".tdd").exists()) == (2, "", True, False)


@pytest.mark.process("git")
def test_drop_with_a_list_other_than_the_four_exits_2_with_usage_and_leaves_the_state_file_unchanged(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    _, item, _ = run_cli(role_state, ["coord", "add", "decision", "keep-alpha"], cwd=repo)
    state = repo / ".tdd" / "role-coord.state"
    before = state.read_bytes()
    code, out, err = run_cli(role_state, ["coord", "drop", "gossip", item.strip()], cwd=repo)
    assert (code, out, "usage: role-state.sh" in err, state.read_bytes()) == (2, "", True, before)


@pytest.mark.process("git")
def test_set_n_with_a_value_that_is_not_a_whole_number_exits_2_with_usage_and_leaves_the_state_file_unchanged(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    run_cli(role_state, ["coord", "set", "n", "3"], cwd=repo)
    state = repo / ".tdd" / "role-coord.state"
    before = state.read_bytes()
    results = [run_cli(role_state, ["coord", "set", "n", v], cwd=repo) for v in ["-1", "2.5", "abc", ""]]
    codes = [code for code, _, _ in results]
    usages = ["usage: role-state.sh" in err for _, _, err in results]
    assert (codes, usages, state.read_bytes()) == ([2] * 4, [True] * 4, before)


@pytest.mark.process("git")
def test_drop_of_an_id_the_list_does_not_hold_exits_3_and_leaves_the_state_file_unchanged(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    run_cli(role_state, ["coord", "add", "decision", "keep-alpha"], cwd=repo)
    state = repo / ".tdd" / "role-coord.state"
    before = state.read_bytes()
    code, _, _ = run_cli(role_state, ["coord", "drop", "decision", "99"], cwd=repo)
    assert (code, state.read_bytes()) == (3, before)


@pytest.mark.process("git")
def test_add_timed_n_with_unparseable_text_exits_2_naming_the_form_and_writes_nothing_3583(tmp_path, run_cli):
    role_state = importlib.import_module("veri.role_state")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    text = "4 until weekly usage reset ~2026-11-10 evening (Mario 11-09)"
    code, out, err = run_cli(role_state, ["dev", "add", "timed-n", text], cwd=repo)
    wrote = (repo / ".tdd" / "role-dev.state").exists()
    assert (code, "<n> until <ISO-8601 datetime>" in err, wrote) == (2, True, False)
