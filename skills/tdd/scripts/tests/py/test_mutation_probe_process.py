"""Medium cases for mutation-probe.sh: the shim and the command it runs, started for real."""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

PROBE = Path(__file__).resolve().parents[2] / "mutation-probe.sh"


@pytest.mark.process("mutation-probe.sh and the sh command it runs against the edited fixture")
def test_command_sees_the_edited_content_and_a_failing_command_exits_0(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("keep alpha keep\n")
    witness = tmp_path / "witness.txt"
    result = subprocess.run(
        [str(PROBE), str(target), "alpha", "beta", "--", "sh", "-c", 'cp "$1" "$2"; ! grep -q beta "$1"', "sh", str(target), str(witness)],
        capture_output=True, text=True, timeout=20)
    assert (result.returncode, witness.read_text() if witness.exists() else None) == (0, "keep beta keep\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh and the sh command it runs, sent SIGTERM midway")
def test_probe_sent_sigterm_while_the_command_runs_restores_the_file_and_leaves_git_status_empty(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    target = tmp_path / "target.txt"
    target.write_text("keep alpha keep\n")
    git("add", "target.txt")
    git("commit", "-q", "-m", "fixture")
    started = tmp_path.parent / (tmp_path.name + "-started")
    probe = subprocess.Popen([str(PROBE), str(target), "alpha", "beta", "--", "sh", "-c", 'echo $$ > "$1"; exec sleep 20', "sh", str(started)],
                             cwd=tmp_path, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not (started.exists() and started.read_text().endswith("\n")):
            time.sleep(0.02)
        assert started.exists(), "the command never started"
        probe.send_signal(signal.SIGTERM)
        probe.wait(timeout=10)
    finally:
        if started.exists() and started.read_text().strip().isdigit():
            try:
                os.kill(int(started.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass
        if probe.poll() is None:
            probe.kill()
            probe.wait()
    assert (target.read_text(), git("status", "--porcelain")) == ("keep alpha keep\n", "")


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_exits_1_when_the_test_stays_green_on_the_branch_point_and_leaves_the_tree_unchanged(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "view.txt").write_text("view\n")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("grep -q view view.txt\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    scratch = tmp_path / "scratch.txt"
    scratch.write_text("untracked\n")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    tree = {name: (tmp_path / name).read_text() for name in ("view.txt", "quote.txt", "test.sh", "scratch.txt")}
    assert (result.returncode, tree, git("status", "--porcelain")) == (
        1, {"view.txt": "view\n", "quote.txt": "10\n", "test.sh": "grep -q view view.txt\n", "scratch.txt": "untracked\n"},
        "?? scratch.txt\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_runs_the_kept_file_as_it_is_and_exits_0_when_that_command_fails(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("exit 1\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "test.sh").read_text()) == (0, "exit 1\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_leaves_a_kept_file_that_differs_from_the_sha_as_it_is_in_the_working_tree(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    (tmp_path / "test.sh").write_text("exit 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("exit 1\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "test.sh").read_text()) == (0, "exit 1\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_leaves_every_file_under_tdd_as_it_is_in_the_working_tree_while_the_command_runs(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "ledger.md").write_text("old\n")
    (tmp_path / "quote.txt").write_text("0\n")
    (tmp_path / "test.sh").write_text("grep -q new .tdd/ledger.md\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / ".tdd" / "ledger.md").write_text("new\n")
    (tmp_path / "quote.txt").write_text("10\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / ".tdd" / "ledger.md").read_text()) == (1, "new\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_removes_a_file_added_since_the_sha_tracked_or_untracked_while_the_command_runs(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "added.txt").write_text("tracked\n")
    (tmp_path / "test.sh").write_text("test ! -e added.txt && test ! -e fresh.txt\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    (tmp_path / "fresh.txt").write_text("untracked\n")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert result.returncode == 1, result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_keeps_a_test_path_that_is_new_since_the_sha_with_its_working_tree_bytes_while_the_command_runs(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("# kept-marker\nexit 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "grep", "-q", "kept-marker", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "test.sh").read_text()) == (1, "# kept-marker\nexit 0\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_brings_back_a_file_deleted_since_the_sha_with_its_sha_content_while_the_command_runs(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    (tmp_path / "gone.txt").write_text("sha-content\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    git("rm", "-q", "gone.txt")
    (tmp_path / "test.sh").write_text("exit 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "grep", "-q", "sha-content", "gone.txt"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "gone.txt").exists()) == (1, False), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_restores_the_working_tree_when_the_command_deletes_a_file_it_brought_back(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "a_gone.txt").write_text("sha-content\n")
    (tmp_path / "b_changed.txt").write_text("sha-content\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    git("rm", "-q", "a_gone.txt")
    (tmp_path / "b_changed.txt").write_text("branch-content\n")
    (tmp_path / "test.sh").write_text("exit 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "rm", "a_gone.txt"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "a_gone.txt").exists(), (tmp_path / "b_changed.txt").read_text(),
            "Traceback" in result.stderr) == (1, False, "branch-content\n", False), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_restores_a_renamed_file_as_the_new_name_removed_and_the_old_name_back_while_the_command_runs(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "old_name.txt").write_text("sha-content line one\nsha-content line two\nsha-content line three\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    git("mv", "old_name.txt", "new_name.txt")
    (tmp_path / "test.sh").write_text("exit 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "-c",
                             "test ! -e new_name.txt && grep -q 'line two' old_name.txt"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "new_name.txt").exists(), (tmp_path / "old_name.txt").exists()) == (1, True, False), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_puts_a_restored_tracked_file_back_to_its_uncommitted_working_tree_bytes(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "prod.bin").write_bytes(b"sha-content\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "prod.bin").write_bytes(b"branch-content\n")
    (tmp_path / "test.sh").write_text("exit 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    dirty = b"\x00\xffuncommitted edit\r\n"
    (tmp_path / "prod.bin").write_bytes(dirty)
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "grep", "-q", "sha-content", "prod.bin"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "prod.bin").read_bytes()) == (1, dirty), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_removes_again_a_file_it_brought_back_when_the_deletion_is_uncommitted(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "gone.txt").write_text("sha-content\n")
    (tmp_path / "test.sh").write_text("exit 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "gone.txt").unlink()
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "grep", "-q", "sha-content", "gone.txt"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "gone.txt").exists(), git("status", "--porcelain")) == (1, False, " D gone.txt\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_puts_back_an_untracked_file_it_removed_byte_for_byte(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "prod.txt").write_text("sha-content\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "prod.txt").write_text("branch-content\n")
    (tmp_path / "test.sh").write_text("exit 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    (tmp_path / "sub").mkdir()
    untracked = b"\x00\xff untracked\r\n\x80"
    (tmp_path / "sub" / "scratch.bin").write_bytes(untracked)
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "test", "-e", "sub/scratch.bin"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "sub" / "scratch.bin").read_bytes()) == (0, untracked), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it would run against a scratch repo")
def test_issue_2900_before_state_probe_exits_2_without_running_the_command_when_the_sha_does_not_resolve_to_a_commit(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    (tmp_path / "quote.txt").write_text("10\n")
    result = subprocess.run([str(PROBE), "--before", "abcdef1234567", "--keep", "test.sh", "--", "touch", "ran.marker"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "ran.marker").exists()) == (2, False), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it would run against a scratch repo")
def test_issue_2900_before_state_probe_exits_2_without_running_the_command_when_the_sha_is_not_hex_though_it_resolves(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    (tmp_path / "quote.txt").write_text("10\n")
    result = subprocess.run([str(PROBE), "--before", "HEAD", "--keep", "test.sh", "--", "touch", "ran.marker"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "ran.marker").exists()) == (2, False), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it would run against a scratch repo")
def test_issue_2900_before_state_probe_exits_2_without_running_the_command_when_only_the_test_path_and_tdd_differ_from_the_sha(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    (tmp_path / "test.sh").write_text("old\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "test.sh").write_text("new\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "ledger.md").write_text("step\n")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "touch", "ran.marker"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "ran.marker").exists()) == (2, False), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_exiting_0_appends_before_keep_and_command_to_the_record(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("exit 1\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    green = git("rev-parse", "HEAD").strip()
    record = tmp_path.parent / (tmp_path.name + "-mutations.md")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20,
                            env={**os.environ, "VERI_MUTATION_RECORD": str(record)})
    expected = f"before {len(base)}\n{base}\nkeep 7\ntest.sh\ncommand 10\nsh test.sh\ngreen {len(green)}\n{green}\n\n"
    assert (result.returncode, record.read_text() if record.exists() else None) == (0, expected), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2974_before_state_probe_exiting_0_records_the_green_commit_head_names_beside_before_keep_and_command(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("exit 1\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    green = git("rev-parse", "HEAD").strip()
    record = tmp_path.parent / (tmp_path.name + "-mutations.md")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20,
                            env={**os.environ, "VERI_MUTATION_RECORD": str(record)})
    text = record.read_text() if record.exists() else ""
    assert (result.returncode, f"green {len(green)}\n{green}\n" in text, f"before {len(base)}\n{base}\n" in text) == (0, True, True), (
        result.stderr, text)


@pytest.mark.process("git, mutation-probe.sh --before, timed-test-run.sh and the sh command it runs against a scratch repo")
def test_issue_3357_before_state_probe_records_the_command_without_the_timed_test_run_wrapper_and_its_path(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("exit 1\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    record = tmp_path.parent / (tmp_path.name + "-mutations.md")
    wrapper = PROBE.parent / "timed-test-run.sh"
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", str(wrapper), "target", "test.sh", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20,
                            env={**os.environ, "VERI_MUTATION_RECORD": str(record)})
    text = record.read_text() if record.exists() else ""
    assert (result.returncode, "command 10\nsh test.sh\n" in text) == (0, True), (result.stderr, text)


@pytest.mark.process("git, mutation-probe.sh --before and python running a test that stubs the quote, against a scratch repo")
def test_issue_2900_before_state_probe_exits_1_for_a_test_stubbing_the_quote_and_leaves_the_working_tree_unchanged(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "view.py").write_text('def render(q): return str(q["deps"])\n')
    (tmp_path / "quote.py").write_text('def fetch(deps=()): return {"deps": 0}\n')
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.py").write_text('def fetch(deps=()): return {"deps": 10 * len(deps)}\n')
    (tmp_path / "check_view.py").write_text(
        'import sys\nfrom view import render\nsys.exit(0 if render({"deps": 10}) == "10" else 1)\n')
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "check_view.py", "--", sys.executable, "-B", "check_view.py"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    tree = {name: (tmp_path / name).read_text() for name in ("view.py", "quote.py", "check_view.py")}
    assert (result.returncode, tree, git("status", "--porcelain")) == (
        1, {"view.py": 'def render(q): return str(q["deps"])\n',
            "quote.py": 'def fetch(deps=()): return {"deps": 10 * len(deps)}\n',
            "check_view.py": 'import sys\nfrom view import render\nsys.exit(0 if render({"deps": 10}) == "10" else 1)\n'},
        ""), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_3016_before_state_probe_at_a_plan_only_head_does_not_stamp_head_as_green(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("exit 1\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-3016.md").write_text("- [ ] 1. the step\n")
    git("add", ".")
    git("commit", "-q", "-m", "plan")
    head = git("rev-parse", "HEAD").strip()
    record = tmp_path / ".tdd" / "issue-3016-mutations.md"
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20,
                            env={**os.environ, "VERI_MUTATION_RECORD": str(record)})
    text = record.read_text() if record.exists() else ""
    assert (result.returncode, f"green {len(head)}\n{head}\n" in text) == (0, False), (result.stderr, text)


@pytest.mark.process("git, mutation-probe.sh applying an event.py mutant and a copied timed-test-run.sh in a scratch repo")
@pytest.mark.tree_audit("copies the veri scripts and lib trees into a temporary repo")
def test_issue_3383_probe_dropping_o_append_from_event_py_leaves_the_live_journal_append_only(tmp_path):
    import json
    import shutil

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    scripts = tmp_path / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(PROBE.parent / "timed-test-run.sh", scripts)
    shutil.copytree(PROBE.parent / "lib", scripts / "lib")
    shutil.copytree(PROBE.parent / "veri", scripts / "veri", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    git("init", "-q")
    (tmp_path / ".gitignore").write_text(".tdd/events.jsonl\n")
    (tmp_path / ".tdd").mkdir()
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    journal = tmp_path / ".tdd" / "events.jsonl"
    before = "".join(json.dumps({"ts": 1794156370 + n, "event": "step", "note": "x" * 200}) + "\n" for n in range(3))
    journal.write_text(before)

    subprocess.run([str(PROBE), str(scripts / "veri" / "event.py"), "os.O_WRONLY | os.O_APPEND | os.O_CREAT", "os.O_WRONLY | os.O_CREAT",
                    "--", str(scripts / "timed-test-run.sh"), "affected", "suite", "true"],
                   cwd=tmp_path, capture_output=True, text=True, timeout=60,
                   env={**os.environ, "VERI_MUTATION_RECORD": str(tmp_path.parent / (tmp_path.name + "-mutations.md"))})

    after = journal.read_text()
    assert (after.startswith(before), after[len(before):] == "" or after.endswith("\n")) == (True, True), after
