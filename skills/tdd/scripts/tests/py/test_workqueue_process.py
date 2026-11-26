"""Process cases for veri/workqueue.py: the ones that start a real process; the small cases are in unit/test_workqueue.py."""
import importlib
import os
import re
import subprocess

import pytest


@pytest.fixture(autouse=True)
def no_ambient_tunables(monkeypatch):
    for name in ("VERI_GH_JSON", "VERI_WORKQUEUE_LOCK_WAIT"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def workqueue():
    return importlib.import_module("veri.workqueue")


@pytest.mark.process("parallel workqueue.sh processes writing one queue under a real git repository")
def test_assign_and_start_run_as_parallel_processes_leave_a_well_formed_queue_holding_every_write(tmp_path):
    script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "workqueue.sh")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    queue.write_text("".join("alpha\t%d\tqueued\t\n" % (100 + i) for i in range(1, 21)))
    writers = []
    for i in range(1, 21):
        for argv in (["assign", "w%d" % i, str(i)], ["start", "alpha", str(100 + i)]):
            writers.append(subprocess.Popen([script] + argv, cwd=tmp_path, stdin=subprocess.DEVNULL,
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    for writer in writers:
        writer.wait(timeout=25)
    lines = queue.read_text().split("\n")
    assert lines.pop() == ""
    torn = [line for line in lines if not re.fullmatch(r"[^\t]+\t[0-9]+\t(queued|running|merged|parked|skipped)\t[^\t]*", line)]
    assert torn == []
    want = {"w%d\t%d\tqueued\t" % (i, i) for i in range(1, 21)} | {"alpha\t%d\trunning\t" % (100 + i) for i in range(1, 21)}
    assert want - set(lines) == set()


def git_repo_with_queue(path):
    git = ["git", "-c", "user.name=veri", "-c", "user.email=veri@example.test"]
    subprocess.run(git + ["init", "-q", "-b", "main", str(path)], check=True)
    subprocess.run(git + ["-C", str(path), "commit", "-q", "--allow-empty", "-m", "initial"], check=True)
    (path / ".tdd").mkdir()
    (path / ".tdd" / "workqueue").write_bytes(b"beta\t4\tqueued\t\n")
    return path


@pytest.mark.process("a real linked git worktree whose `git worktree list` names the main working tree")
def test_called_from_a_linked_worktree_through_the_cli_assign_and_show_act_on_the_main_working_tree_queue(tmp_path, run_cli, workqueue):
    main = git_repo_with_queue(tmp_path / "main")
    linked = tmp_path / "linked"
    subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", "-b", "side", str(linked)], check=True)

    assert run_cli(workqueue, ["assign", "alpha", "7"], cwd=str(linked)) == (0, "", "")
    assert run_cli(workqueue, ["show"], cwd=str(linked)) == (0, "beta\n\t4\tqueued\nalpha\n\t7\tqueued\n", "")
    assert (main / ".tdd" / "workqueue").read_bytes() == b"beta\t4\tqueued\t\nalpha\t7\tqueued\t\n"
    assert not (linked / ".tdd" / "workqueue").exists()


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.mark.process("workqueue.sh run through a symlink to the skill directory from a subdirectory of a real linked git worktree")
def test_run_through_a_symlinked_skill_from_a_linked_worktree_subdirectory_assign_start_and_show_act_as_in_place_on_the_main_working_tree_queue(tmp_path):
    in_place, main, linked = git_repo_with_queue(tmp_path / "in-place"), git_repo_with_queue(tmp_path / "main"), tmp_path / "linked"
    subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", "-b", "side", str(linked)], check=True)
    (linked / "sub" / "dir").mkdir(parents=True)
    (tmp_path / "skill-link").symlink_to(SKILL_DIR, target_is_directory=True)

    def sequence(script, cwd):
        out = []
        for argv in (["assign", "alpha", "7", "8"], ["start", "alpha", "7"], ["show"]):
            done = subprocess.run([script] + argv, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
            out.append((done.returncode, done.stdout, done.stderr))
        return out

    want = [(0, "", ""), (0, "", ""), (0, "beta\n\t4\tqueued\nalpha\n\t7\trunning\n\t8\tqueued\n", "")]
    assert sequence(os.path.join(SKILL_DIR, "scripts", "workqueue.sh"), in_place) == want
    assert sequence(str(tmp_path / "skill-link" / "scripts" / "workqueue.sh"), linked / "sub" / "dir") == want
    queue = b"beta\t4\tqueued\t\nalpha\t7\trunning\t\nalpha\t8\tqueued\t\n"
    assert (in_place / ".tdd" / "workqueue").read_bytes() == queue
    assert (main / ".tdd" / "workqueue").read_bytes() == queue
    assert not (linked / ".tdd" / "workqueue").exists()
    assert not (linked / "sub" / "dir" / ".tdd" / "workqueue").exists()
