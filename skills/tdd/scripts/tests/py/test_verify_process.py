"""Cases for veri/verify.py that start a real process: the verify.sh entry point."""
import importlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import INTERPRETER_VENV
from repo_builder import new_repo, origin_head_at
from test_supervise_process import checked_head, checked_step, committed_head


def with_origin_head(work):
    head = committed_head(work)
    origin_head_at(work)
    return head

SCRIPTS = Path(__file__).resolve().parents[2]


def based(repo):
    """`--branch-base` and <repo>'s HEAD, the recorded base every phase takes (#4375, #4376); a hex sha naming no
    commit outside a git repository, where the verifier reads nothing at it."""
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return ["--branch-base", head or "0000000"]


@pytest.mark.process("verify.sh run as a real shim over veri/verify.py, a real supervise.sh and run-leaf.sh"
                     " around a stub claude that answers VERDICT: PASS")
def test_verify_sh_green_rejects_a_pass_on_a_replaces_case_step_naming_each_case_its_suite_still_holds_1507(
        tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / "tests" / "x.test.sh").write_text("test\n")
    (tmp_path / "tests" / "demo.py").write_text('verdict "kept case" 0\nverdict "stale second" 0\n')
    claude = tmp_path / "claude-pass"
    claude.write_text("#!/bin/sh\nprintf 'VERDICT: PASS\\nREASON: the named cases are gone.'\n")
    claude.chmod(0o755)
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_step(tmp_path, with_origin_head(tmp_path))}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "--step", "the replacement takes over: replaces 'stale first', 'stale second'"
         " in tests/demo.py ⟦replaces-case⟧ ⟦criterion 1⟧", "--fast-cmd", "make unit", "green", "spec.md",
         "tests/x.test.sh"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True)

    assert (done.returncode, b"stale second" in done.stdout, b"stale first" in done.stdout) == (1, True, False)


@pytest.mark.process("verify.sh run as a real shim over veri/verify.py and a real supervise.sh around a stub claude,"
                     " from a subdirectory of a throwaway git repo")
def test_verify_sh_run_from_a_subdirectory_writes_its_prompt_and_run_state_under_the_repo_root_1895(tmp_path):
    with_origin_head(tmp_path)
    sub = tmp_path / "skills"
    sub.mkdir()
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / "x_test.py").write_text("def test_x():\n    pass\n")
    claude = tmp_path / "claude-pass"
    claude.write_text("#!/bin/sh\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", "PYTHONDONTWRITEBYTECODE": "1"}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(sub), "--fast-cmd", "make unit", "green", "../spec.md", "../x_test.py", "x_test.py::test_x"],
        cwd=sub, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert ((tmp_path / ".tdd" / "verify-green.prompt").exists(), (sub / ".tdd").exists()) == (True, False), done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a real lint gate and a real test runner, around a stub claude")
def test_verify_sh_red_whose_lint_gate_fails_on_its_tree_but_passes_without_it_exits_1_with_a_gate_reason_and_launches_no_verifier(
        tmp_path):
    with_origin_head(tmp_path)
    identity = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@example.test",
                "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@example.test",
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

    def commit(message):
        for argv in (["add", "-A"], ["commit", "-q", "-m", message]):
            subprocess.run(["git", "-C", str(tmp_path), *argv], check=True, env={**os.environ, **identity})

    (tmp_path / "tests").mkdir()
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    (tmp_path / "lint.sh").write_text(
        "if grep -n '^ *unused = ' tests/test_slugify.py; then\n"
        "  echo \"tests/test_slugify.py:3: F841 local variable 'unused' is assigned to but never used\"; exit 1\n"
        "fi\n")
    (tmp_path / "run-tests.sh").write_text("echo 'FAILED tests/test_slugify.py::test_lowercases - assert 1 == 2'\nexit 1\n")
    (tmp_path / "tests" / "test_slugify.py").write_text("def test_other():\n    assert True\n")
    commit("base")
    (tmp_path / "tests" / "test_slugify.py").write_text(
        "def test_other():\n    assert True\n\n\ndef test_lowercases():\n    unused = 1\n    assert 1 == 2\n")
    commit("red")
    head = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()
    launched = tmp_path / ".tdd" / "leaf-launched"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\ntouch {launched}\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           "VERI_TEST_CMD": "sh lint.sh && sh run-tests.sh",
           **checked_step(tmp_path, head)}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    first = done.stdout.splitlines()[0] if done.stdout else ""
    assert (done.returncode, first.startswith("GATE:"), "sh lint.sh" in first, "F841" in first,
            launched.exists()) == (1, True, True, True, False), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a passing lint gate and a real test runner, around a stub claude")
def test_verify_sh_red_whose_lint_gate_passes_and_whose_only_failure_is_the_target_test_launches_the_verifier_and_its_pass_stands(
        tmp_path):
    head = with_origin_head(tmp_path)
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    (tmp_path / "lint.sh").write_text("echo 'lint: all clean'\n")
    (tmp_path / "run-tests.sh").write_text("echo 'FAILED tests/test_slugify.py::test_lowercases - assert 1 == 2'\nexit 1\n")
    launched = tmp_path / ".tdd" / "leaf-launched"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\ntouch {launched}\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           "VERI_TEST_CMD": "sh lint.sh && sh run-tests.sh",
           **checked_step(tmp_path, head)}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, launched.exists()) == (0, False, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a passing lint gate, an empty segment and a real test runner, around a stub claude")
def test_verify_sh_red_whose_test_command_has_an_empty_gate_segment_runs_and_reports_no_empty_gate_and_launches_the_verifier(
        tmp_path):
    head = with_origin_head(tmp_path)
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    (tmp_path / "lint.sh").write_text("echo 'lint: all clean'\n")
    (tmp_path / "run-tests.sh").write_text("echo 'FAILED tests/test_slugify.py::test_lowercases - assert 1 == 2'\nexit 1\n")
    launched = tmp_path / ".tdd" / "leaf-launched"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\ntouch {launched}\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           "VERI_TEST_CMD": "sh lint.sh && && sh run-tests.sh",
           **checked_step(tmp_path, head)}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, launched.exists()) == (0, False, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a real lint gate and a real test runner, around a stub claude")
def test_verify_sh_red_whose_lint_gate_written_with_surrounding_whitespace_fails_exits_1_with_a_gate_reason_naming_the_trimmed_command(
        tmp_path):
    with_origin_head(tmp_path)
    identity = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@example.test",
                "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@example.test",
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

    def commit(message):
        for argv in (["add", "-A"], ["commit", "-q", "-m", message]):
            subprocess.run(["git", "-C", str(tmp_path), *argv], check=True, env={**os.environ, **identity})

    (tmp_path / "tests").mkdir()
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    (tmp_path / "lint.sh").write_text(
        "if grep -n '^ *unused = ' tests/test_slugify.py; then\n"
        "  echo \"tests/test_slugify.py:3: F841 local variable 'unused' is assigned to but never used\"; exit 1\n"
        "fi\n")
    (tmp_path / "run-tests.sh").write_text("echo 'FAILED tests/test_slugify.py::test_lowercases - assert 1 == 2'\nexit 1\n")
    (tmp_path / "tests" / "test_slugify.py").write_text("def test_other():\n    assert True\n")
    commit("base")
    (tmp_path / "tests" / "test_slugify.py").write_text(
        "def test_other():\n    assert True\n\n\ndef test_lowercases():\n    unused = 1\n    assert 1 == 2\n")
    commit("red")
    head = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()
    launched = tmp_path / ".tdd" / "leaf-launched"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\ntouch {launched}\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           "VERI_TEST_CMD": "   sh lint.sh   && sh run-tests.sh",
           **checked_step(tmp_path, head)}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    first = done.stdout.splitlines()[0] if done.stdout else ""
    assert (done.returncode, first.startswith("GATE: sh lint.sh fails on the Red's tree")) == (1, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a failing lint gate printing a padded line and a real test runner, around a stub claude")
def test_verify_sh_red_whose_failing_lint_gate_prints_its_offending_line_padded_with_whitespace_exits_1_with_that_line_trimmed(
        tmp_path):
    head = with_origin_head(tmp_path)
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    (tmp_path / "lint.sh").write_text(
        "echo \"   tests/test_slugify.py:3: F841 local variable 'unused' is never used   \"\nexit 1\n")
    (tmp_path / "run-tests.sh").write_text("echo 'FAILED tests/test_slugify.py::test_lowercases - assert 1 == 2'\nexit 1\n")
    claude = tmp_path / "claude-pass"
    claude.write_text("#!/bin/sh\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           "VERI_TEST_CMD": "sh lint.sh && sh run-tests.sh",
           **checked_step(tmp_path, head)}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    first = done.stdout.splitlines()[0] if done.stdout else ""
    assert (done.returncode, first) == (
        1, "GATE: sh lint.sh fails on the Red's tree: tests/test_slugify.py:3: F841 local variable 'unused' is never used"
    ), done.stdout + done.stderr


@pytest.mark.process("verify.sh green run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a failing lint gate and a real test runner, around a stub claude")
def test_verify_sh_green_with_the_same_test_command_whose_lint_gate_fails_is_not_refused_with_a_gate_reason_and_launches_the_verifier(
        tmp_path):
    head = with_origin_head(tmp_path)
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    (tmp_path / "lint.sh").write_text("echo \"tests/test_slugify.py:3: F841 local variable 'unused' is never used\"; exit 1\n")
    (tmp_path / "run-tests.sh").write_text("echo 'all passed'\n")
    launched = tmp_path / ".tdd" / "leaf-launched"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\ntouch {launched}\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           "VERI_TEST_CMD": "sh lint.sh && sh run-tests.sh",
           **checked_step(tmp_path, head)}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "--fast-cmd", "make unit", "green", "spec.md", "tests/test_slugify.py"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, launched.exists()) == (0, False, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a lint gate red on both trees and a real test runner, around a stub claude")
def test_verify_sh_red_whose_lint_gate_fails_on_the_tree_without_the_red_too_exits_2_naming_the_gate_as_red_before_the_red_and_launches_no_verifier(
        tmp_path):
    with_origin_head(tmp_path)
    identity = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@example.test",
                "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@example.test",
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

    def commit(message):
        for argv in (["add", "-A"], ["commit", "-q", "-m", message]):
            subprocess.run(["git", "-C", str(tmp_path), *argv], check=True, env={**os.environ, **identity})

    (tmp_path / "tests").mkdir()
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    (tmp_path / "lint.sh").write_text("echo 'src/legacy.py:9: E999 syntax error'\nexit 1\n")
    (tmp_path / "run-tests.sh").write_text("echo 'FAILED tests/test_slugify.py::test_lowercases - assert 1 == 2'\nexit 1\n")
    (tmp_path / "tests" / "test_slugify.py").write_text("def test_other():\n    assert True\n")
    commit("base")
    (tmp_path / "tests" / "test_slugify.py").write_text(
        "def test_other():\n    assert True\n\n\ndef test_lowercases():\n    assert 1 == 2\n")
    commit("red")
    head = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()
    launched = tmp_path / ".tdd" / "leaf-launched"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\ntouch {launched}\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           "VERI_TEST_CMD": "sh lint.sh && sh run-tests.sh",
           **checked_step(tmp_path, head)}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, "sh lint.sh" in done.stderr,
            "red before the Red" in done.stderr, "pre-existing" in done.stderr,
            launched.exists()) == (2, False, True, True, True, False), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD is a single test runner whose only failure names the target test, around a stub claude")
def test_verify_sh_red_whose_test_command_is_a_single_runner_with_no_lint_gate_launches_the_verifier_and_is_not_rejected_with_a_gate_reason(
        tmp_path):
    head = with_origin_head(tmp_path)
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_slugify.py").write_text(
        "def test_lowercases():\n    stored, id = 1, 2\n    assert stored == 2\n")
    (tmp_path / "run-tests.sh").write_text(
        "echo 'FAILED tests/test_slugify.py::test_lowercases - assert 1 == 2'\nexit 1\n")
    launched = tmp_path / ".tdd" / "leaf-launched"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\ntouch {launched}\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           "VERI_TEST_CMD": "sh run-tests.sh",
           **checked_step(tmp_path, head)}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, launched.exists()) == (0, False, True), done.stdout + done.stderr


def run_verify_writing(tmp_path, phase, writes, then="", cwd=None, recorded=None):
    head = with_origin_head(tmp_path)
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/*\n!.tdd/issue-*.md\n")
    record = tmp_path / ".tdd" / "issue-2741-mutations.md"
    if recorded is not None:
        record.parent.mkdir(exist_ok=True)
        record.write_text(recorded)
    claude = tmp_path / "claude-pass"
    claude.write_text("#!/bin/sh\n" + "".join("echo written >> %s\n" % (tmp_path / path) for path in writes)
                      + then + "printf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", "VERI_NO_VERDICT_RETRIES": "0",
           **checked_step(tmp_path, head, issue="2741")}
    if cwd:
        (tmp_path / cwd).mkdir()
    up = "../" if cwd else ""
    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), *based(tmp_path), "--fast-cmd", "make unit", phase, up + "spec.md", up + "tests/test_x.py"],
        cwd=tmp_path / (cwd or ""), env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return done, record


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that writes the path a mutation record once had before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_writes_only_the_old_mutation_record_path_is_refused_4741(tmp_path):
    done, _ = run_verify_writing(tmp_path, "pin", [".tdd/issue-2741-mutations.md"])

    assert (done.returncode, "modified the repository" in done.stdout) == (2, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that appends to the mutation record and to another file before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_writes_its_mutation_record_and_another_file_is_refused_2741(tmp_path):
    done, _ = run_verify_writing(tmp_path, "pin", [".tdd/issue-2741-mutations.md", "other.txt"])

    assert (done.returncode, "modified the repository" in done.stdout) == (2, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh green run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that appends to the mutation record's path before answering VERDICT: PASS")
def test_verify_sh_green_whose_verifier_writes_the_mutation_record_path_is_refused_2741(tmp_path):
    done, _ = run_verify_writing(tmp_path, "green", [".tdd/issue-2741-mutations.md"])

    assert (done.returncode, "modified the repository" in done.stdout) == (2, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that appends to the mutation record and commits before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_writes_its_mutation_record_and_moves_head_is_refused_2741(tmp_path):
    done, _ = run_verify_writing(tmp_path, "pin", [".tdd/issue-2741-mutations.md"],
                                 then="git -c user.name=v -c user.email=v@v.invalid commit -q --allow-empty -m moved\n")

    assert (done.returncode, "modified the repository" in done.stdout) == (2, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo holding a mutation"
                     " record, around a stub claude that deletes it before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_deletes_its_mutation_record_is_refused_and_the_record_restored_2741(tmp_path):
    done, record = run_verify_writing(tmp_path, "pin", [], recorded="earlier pin\n",
                                      then="rm %s\n" % (tmp_path / ".tdd" / "issue-2741-mutations.md"))

    got = record.read_text() if record.exists() else None
    assert (done.returncode, "modified the repository" in done.stdout, got) == (2, True, "earlier pin\n"), \
        done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo holding a mutation"
                     " record, around a stub claude that rewrites it before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_rewrites_its_mutation_record_is_refused_and_the_record_restored_2741(tmp_path):
    done, record = run_verify_writing(tmp_path, "pin", [], recorded="earlier pin\n",
                                      then="echo rewritten > %s\n" % (tmp_path / ".tdd" / "issue-2741-mutations.md"))

    assert (done.returncode, "modified the repository" in done.stdout, record.read_text()) == (2, True, "earlier pin\n"), \
        done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that writes another issue's mutation record before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_writes_another_issues_mutation_record_is_refused_2741(tmp_path):
    done, _ = run_verify_writing(tmp_path, "pin", [".tdd/issue-9-mutations.md"])

    assert (done.returncode, "modified the repository" in done.stdout) == (2, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that makes the mutation record a symlink to an ignored file before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_makes_its_mutation_record_a_symlink_is_refused_2741(tmp_path):
    record = tmp_path / ".tdd" / "issue-2741-mutations.md"
    done, _ = run_verify_writing(tmp_path, "pin", [".tdd/elsewhere"], then="ln -s elsewhere %s\n" % record)

    assert (done.returncode, "modified the repository" in done.stdout, record.is_symlink()) == (2, True, False), \
        done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo holding a mutation"
                     " record, around a stub claude that replaces it with an empty directory before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_replaces_its_mutation_record_with_a_directory_is_refused_and_the_record_restored_2741(
        tmp_path):
    record = tmp_path / ".tdd" / "issue-2741-mutations.md"
    done, _ = run_verify_writing(tmp_path, "pin", [], recorded="earlier pin\n", then="rm %s; mkdir %s\n" % (record, record))

    got = record.read_text() if record.is_file() else None
    assert (done.returncode, "modified the repository" in done.stdout, got) == (2, True, "earlier pin\n"), \
        done.stdout + done.stderr


@pytest.fixture(autouse=True)
def no_ambient_leaf_args(monkeypatch):
    monkeypatch.delenv("VERIFY_LEAF_ARGS", raising=False)


def write_inputs(directory):
    directory = pathlib.Path(directory)
    (directory / "tests").mkdir(exist_ok=True)
    (directory / "spec.md").write_text("the behavior spec\n")
    (directory / "tests" / "x.test.sh").write_text("test\n")


def record(event, *pairs, issue="", step="", phase="green"):
    return {"issue": issue, "actor": "verifier", "phase": phase, "step": step, "event": event, "attempt": "1",
            "skill_commit": "", **dict(pair.split("=", 1) for pair in pairs)}


def through_fixture(fake_processes, fake):
    """Hand the local <fake>(args, *rest, **kwargs), which answers with a CompletedProcess, to fake_processes as one callable answer."""
    holder = []

    def answer(line, **kwargs):
        done = holder[0].argvs[-1]
        done = fake(done, **kwargs)
        if not isinstance(done, subprocess.CompletedProcess):
            return 0, done, b""
        return done.returncode, done.stdout, done.stderr

    holder.append(fake_processes.answers({"": answer}))
    return holder[0]


NO_LINE = b"parse-verdict: no VERDICT: line found\n"


HUNG_LEAF = "#!/bin/sh\necho thinking...\nexec sleep 60\n"


FAKE_BASE = "3f9a1c0d5e7b4a2896fd01c3b5e7a9d2c4f60812"


SPEC = "slugify must lowercase the title and join words with hyphens."


def answering_leaf(monkeypatch, fake_processes, *leaf_outs, supervised=None):
    launches = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        name = os.path.basename(words[0])
        if name == "supervise.sh":
            launches.append((words[1], pathlib.Path(words[3]).read_text()))
            if supervised is not None:
                supervised.append(words)
            out = leaf_outs[min(len(launches), len(leaf_outs)) - 1]
            return subprocess.CompletedProcess(args, 0, out if isinstance(out, bytes) else (out + "\n").encode(), None)
        if name == "git" and "merge-base" in words:
            return subprocess.CompletedProcess(args, 0, (FAKE_BASE + "\n").encode(), None)
        return subprocess.CompletedProcess(args, 128 if name == "git" else 0, b"", None)

    through_fixture(fake_processes, fake)
    return launches


def test_verify_sh_red_with_a_suite_command_failing_only_on_the_target_test_still_launches_the_verifier_and_its_pass_stands(
        run_cli, tmp_path, monkeypatch, fake_processes):
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")
    launches = answering_leaf(monkeypatch, fake_processes, "VERDICT: PASS\nREASON: ok")
    env = {"HOME": str(tmp_path),
           "VERI_TEST_CMD": "echo 'FAILED tests/test_slugify.py::test_lowercases - assert 1 == 2'; exit 1"}

    code, out, _ = run_cli(verify, [*based(tmp_path), "red", str(tmp_path / "spec.md"), "tests/test_slugify.py", "test_lowercases"],
                           env=env, cwd=tmp_path)

    assert (code, [phase for phase, _ in launches], out.startswith("ok")) == (0, ["verify-red"], True)


HUNG = pytest.mark.process("a hung verifier leaf killed by the real supervise.sh")


@pytest.mark.parametrize("leaf, ambient", [
    ("answers", None),
    pytest.param("hangs", None, marks=HUNG),
    pytest.param("hangs", "3", marks=HUNG),
])
def test_verify_sh_passes_the_blind_prompt_carrying_the_spec_to_the_leaf_and_a_hung_leaf_runs_once_killed_stuck_with_exit_2(
        leaf, ambient, run_cli, tmp_path, monkeypatch, fake_processes):
    if ambient is not None:
        monkeypatch.setenv("VERI_STUCK_RETRIES", ambient)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")
    argv = ["red", str(tmp_path / "spec.md"), "tests/test_slugify.py", "test_lowercases"]
    env = {"HOME": str(tmp_path)}
    if leaf == "answers":
        launches = answering_leaf(monkeypatch, fake_processes, "VERDICT: PASS\nREASON: ok")
    else:
        claude = tmp_path / "claude-hang"
        claude.write_text(HUNG_LEAF)
        claude.chmod(0o755)
        env.update(CLAUDE_BIN=str(claude), VERI_STUCK_RETRIES="0", VERI_TIMEOUT="0",
                   VERI_POLL="0.02", VERI_KILL_POLL="0.01")
        (tmp_path / ".gitignore").write_text(".tdd/\n")
        env.update(checked_step(tmp_path, with_origin_head(tmp_path)))

    code, out, err = run_cli(verify, [*based(tmp_path), *argv], env=env, cwd=tmp_path)

    if leaf == "answers":
        assert (code, len(launches), SPEC in launches[0][1]) == (0, 1, True)
    else:
        assert (code, "killed-stuck" in out,
                err.count("supervise[verify-red]: killed-stuck"), "retry " in err) == (2, True, 1, False)


def stream(*results):
    records = ['{"type":"system","subtype":"init","session_id":"s"}']
    records += ['{"type":"result","subtype":"success","is_error":false,"result":%s}' % json.dumps(r)
                for r in results]
    return "\n".join(records)


FAST = ["--fast-cmd", "make unit"]


WAITING = "Waiting for the background `make test` run to complete before rendering a verdict."


GREEN_REASON = "Target test and full suite are green."


GREEN = "VERDICT: PASS\nREASON: " + GREEN_REASON


DELIVERED = "No action needed — verdict already delivered for this verification."


NO_LINE_TEXT = NO_LINE.decode()


RELAUNCH = ["relaunch", "cause=no-verdict"]


NO_VERDICT_MARK = ["verdict", "verdict=malformed", "reason=", "cause=no-verdict", "name=verify-green"]


GREEN_MARK = ["verdict", "verdict=PASS", "reason=" + GREEN_REASON, "name=verify-green"]


KILLED_OUT = "verifier leaf killed-stuck — no verdict rendered (see .tdd/verify-green.log)\n"


EXHAUSTED = (2, "\n", NO_LINE_TEXT * 2, 2, [RELAUNCH, NO_VERDICT_MARK])


KILLED = (2, KILLED_OUT, "", 1, [])


@pytest.mark.parametrize("env, leaf_outs, supervise_code, expected", [
    pytest.param({}, [stream(WAITING, GREEN, DELIVERED)], 0,
                 (0, GREEN_REASON + "\n", "", 1, [GREEN_MARK]), id="earlier-record"),
    pytest.param({}, [stream(WAITING, DELIVERED)], 0,
                 EXHAUSTED, id="no-record-verdict"),
    pytest.param({}, [stream("VERDICT: REJECT\nREASON: Missing edge case.",
                             "VERDICT: PASS\nREASON: Revised: target and full suite green.", DELIVERED)], 0,
                 (0, "Revised: target and full suite green.\n", "", 1,
                  [["verdict", "verdict=PASS", "reason=Revised: target and full suite green.", "name=verify-green"]]), id="newest-wins"),
    pytest.param({}, [WAITING, GREEN], 0,
                 (0, GREEN_REASON + "\n", NO_LINE_TEXT, 2, [RELAUNCH, GREEN_MARK]),
                 id="relaunched-second-verdict"),
    pytest.param({}, [WAITING], 0,
                 EXHAUSTED, id="budget-default"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "0"}, [WAITING], 0,
                 (2, "\n", NO_LINE_TEXT, 1, [NO_VERDICT_MARK]), id="budget-0"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "2"}, [WAITING], 0,
                 (2, "\n", NO_LINE_TEXT * 3, 3, [RELAUNCH, RELAUNCH, NO_VERDICT_MARK]), id="budget-2"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "many"}, [WAITING], 0,
                 (2, "", "verify: VERI_NO_VERDICT_RETRIES must be a non-negative integer, got 'many'\n", 0, []),
                 id="budget-not-an-integer"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "3", "VERI_STUCK_RETRIES": "1"}, [GREEN], 2,
                 KILLED, id="killed-not-relaunched"),
    pytest.param({"VERI_STUCK_RETRIES": "3"}, [WAITING], 0,
                 EXHAUSTED, id="stuck-retries-leave-no-verdict-count"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "3", "VERI_STUCK_RETRIES": "0"}, [GREEN], 2,
                 KILLED, id="no-verdict-retries-leave-stuck-count"),
])
def test_verify_sh_reads_the_newest_verdict_across_result_records_and_relaunches_only_a_clean_no_verdict_exit_within_its_own_budget_marking_it_no_verdict(
        env, leaf_outs, supervise_code, expected, run_cli, tmp_path, monkeypatch, events, fake_processes):
    write_inputs(tmp_path)
    extract = importlib.import_module("veri.extract_result").extract
    stuck_seen = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        name = os.path.basename(words[0])
        if name == "supervise.sh":
            stuck_seen.append(os.environ.get("VERI_STUCK_RETRIES"))
            leaf = leaf_outs[min(len(stuck_seen), len(leaf_outs)) - 1]
            return subprocess.CompletedProcess(args, supervise_code, (leaf + "\n" + extract(leaf)).encode(), None)
        return subprocess.CompletedProcess(args, 128 if name == "git" else 0, b"", None)

    through_fixture(fake_processes, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code, out, err = run_cli(verify, [*based(tmp_path), *FAST, "green", "spec.md", "tests/test_slugify.py", "test_lowercases"],
                             env={"HOME": str(tmp_path), **env}, cwd=tmp_path)

    assert (code, out, err, len(stuck_seen), events.records(tmp_path)) == (
        *expected[:4], [record(*mark) for mark in expected[4]])
    assert stuck_seen == [env.get("VERI_STUCK_RETRIES")] * len(stuck_seen)


def git_state(repo):
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout.decode()

    files = sorted(git("ls-files", "-co", "--exclude-standard").splitlines())
    return ["HEAD " + git("rev-parse", "HEAD").strip()] + [
        "%s %s" % (f, git("hash-object", "--", f).strip()) for f in files]


def tamper_scratch(tmp_path, monkeypatch, gitignore, tracked, origin=True):
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    (repo / "src.txt").write_text("the developer committed this\n")
    (repo / ".gitignore").write_bytes(gitignore)
    for path, text in tracked.items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text(text)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "initial"], check=True)
    if origin:
        subprocess.run(["git", "-C", str(repo), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
        subprocess.run(["git", "-C", str(repo), "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main"],
                       check=True)
    (tmp_path / "spec.md").write_text(SPEC)
    claude = tmp_path / "claude-mutate"
    claude.write_text('#!/bin/sh\neval "${VERI_TEST_FAKE_MUTATE:-}" >/dev/null 2>&1\nprintf \'%s\' "${VERI_TEST_FAKE_OUT_TEXT:-}"\nexit 0\n')
    claude.chmod(0o755)
    return repo, claude


@pytest.mark.process("a real git scratch repository whose state the verifier leaf changes")
@pytest.mark.parametrize("mutation, leaf_args, expected_code, named", [
    ('printf "the verifier rewrote this\\n" > src.txt', None, 2, "src.txt"),
    ('printf "the verifier left this behind\\n" > leftover.txt', None, 2, "leftover.txt"),
    ('git commit -q -a -m "the verifier committed the developer\'s work"', None, 2, "HEAD"),
    ('b="$(mktemp)"; cp src.txt "$b"; printf "the verifier broke this\\n" > src.txt; cp "$b" src.txt; rm -f "$b"',
     None, 0, "full suite are green"),
    ('printf "%s\\n" "$@" > "$VERI_TEST_LEAFARGS_OUT"; printf "the verifier rewrote this\\n" > src.txt',
     "--permission-mode bypassPermissions --disallowedTools Write", 2, "src.txt"),
])
def test_verify_sh_refuses_a_verifier_leaf_that_changed_the_tree_or_head_with_exit_2_naming_it_and_restores_what_it_was_handed(
        mutation, leaf_args, expected_code, named, run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    (repo / "src.txt").write_text("the developer is still editing this\n")
    (repo / "new.txt").write_text("the developer has not committed this yet\n")
    leafargs_out = tmp_path / "leafargs"
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_TEST_LEAFARGS_OUT": str(leafargs_out), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}
    if leaf_args is not None:
        env["VERIFY_LEAF_ARGS"] = leaf_args
    env.update(checked_head(repo))
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, named in out, git_state(repo)) == (expected_code, True, before)
    if leaf_args is not None:
        reached = leafargs_out.read_text().splitlines()
        assert ("--disallowedTools" in reached, "MultiEdit" in reached) == (True, False)


@pytest.mark.process("a real git scratch repository whose verifier leaf chmods a tracked executable")
def test_verify_sh_accepts_a_pass_from_a_verifier_leaf_that_changed_only_a_tracked_files_mode_and_restores_the_mode_with_no_relaunch_3087(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {"tool.sh": "#!/bin/sh\n"})
    (repo / "tool.sh").chmod(0o755)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "make tool executable"], check=True)
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": "chmod 644 tool.sh",
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}
    env.update(checked_head(repo))
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, (repo / "tool.sh").stat().st_mode & 0o777) == (0, 0o755)


@pytest.mark.process("a real git scratch repository whose verifier leaf makes a committed non-executable file executable")
def test_verify_sh_accepts_a_pass_from_a_verifier_leaf_that_made_a_committed_100644_file_executable_and_restores_100644_3087(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {"tool.sh": "#!/bin/sh\n"})
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": "chmod 755 tool.sh",
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}
    env.update(checked_head(repo))
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True).stdout
    assert (code, (repo / "tool.sh").stat().st_mode & 0o777, status) == (0, 0o644, "")


@pytest.mark.process("a real git scratch repository whose verifier leaf chmods a tracked executable with a non-ASCII name")
def test_verify_sh_restores_the_mode_of_a_tracked_file_with_a_non_ascii_name_and_ends_with_a_clean_tree_3087(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {"\u00e9.sh": "#!/bin/sh\n"})
    (repo / "\u00e9.sh").chmod(0o755)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "make it executable"], check=True)
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": "chmod 644 \u00e9.sh",
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}
    env.update(checked_head(repo))
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True).stdout
    assert (code, (repo / "\u00e9.sh").stat().st_mode & 0o777, status) == (0, 0o755, "")


@pytest.mark.process("a real git scratch repository whose verifier leaf turns a tracked executable into a symlink")
def test_verify_sh_still_refuses_a_verifier_leaf_that_turned_a_tracked_file_into_a_symlink_with_exit_2_3087(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {"tool.sh": "#!/bin/sh\n"})
    (repo / "tool.sh").chmod(0o755)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "make tool executable"], check=True)
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": "rm tool.sh; ln -s src.txt tool.sh",
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}
    env.update(checked_head(repo))
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "tool.sh" in out, "full suite are green" in out) == (2, True, False)


@pytest.mark.process("a real git scratch repository whose verifier leaf chmods a tracked executable")
def test_verify_sh_exits_2_naming_the_cause_when_restoring_a_mode_raises_3087(run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {"tool.sh": "#!/bin/sh\n"})
    (repo / "tool.sh").chmod(0o755)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "make tool executable"], check=True)
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": "chmod 644 tool.sh",
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}
    env.update(checked_head(repo))
    verify = importlib.import_module("veri.verify")

    def broken_chmod(path, mode):
        raise PermissionError("chmod refused for the test")

    monkeypatch.setattr(verify.os, "chmod", broken_chmod)

    code, out, err = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                      "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "chmod refused for the test" in err, "full suite are green" in out) == (2, True, False)


@pytest.mark.process("a real git scratch repository whose verifier leaf chmods and rewrites a tracked executable")
def test_verify_sh_still_refuses_a_verifier_leaf_that_changed_both_the_mode_and_the_content_of_a_tracked_file_with_exit_2_3087(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {"tool.sh": "#!/bin/sh\n"})
    (repo / "tool.sh").chmod(0o755)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "make tool executable"], check=True)
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "VERI_TEST_FAKE_MUTATE": 'chmod 644 tool.sh; printf "the verifier rewrote this\\n" > tool.sh',
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}
    env.update(checked_head(repo))
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "tool.sh" in out, "full suite are green" in out) == (2, True, False)


@pytest.mark.process("a real git scratch repository whose verifier leaf edits a tracked file and makes an untracked one unreadable")
def test_verify_sh_does_not_accept_a_pass_from_a_verifier_leaf_that_left_an_unreadable_file_in_the_tree_2764(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'printf "the verifier rewrote this\\n" > src.txt; printf "secret\\n" > hidden.txt; chmod 000 hidden.txt'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository whose verifier leaf edits a tracked file and makes an untracked one unreadable")
def test_verify_sh_restores_a_tracked_file_the_leaf_edited_when_it_refuses_for_an_unreadable_file_2773(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'printf "the verifier rewrote this\\n" > src.txt; printf "secret\\n" > hidden.txt; chmod 000 hidden.txt'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, (repo / "src.txt").read_text()) == (2, "the developer committed this\n")


@pytest.mark.process("a real git scratch repository whose verifier leaf edits a tracked file and makes an untracked one unreadable")
def test_verify_sh_names_the_unreadable_file_on_stderr_when_it_refuses_for_one_the_leaf_left_2773(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'printf "the verifier rewrote this\\n" > src.txt; printf "secret\\n" > hidden.txt; chmod 000 hidden.txt'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, _, err = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "hidden.txt" in err) == (2, True)


@pytest.mark.process("a real git scratch repository whose verifier leaf adds a file and makes an untracked one unreadable")
def test_verify_sh_removes_a_file_the_leaf_added_when_it_refuses_for_an_unreadable_file_2784(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'printf "added\\n" > added.txt; printf "secret\\n" > hidden.txt; chmod 000 hidden.txt'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, (repo / "added.txt").exists()) == (2, False)


@pytest.mark.process("a real git scratch repository with an untracked file, whose verifier leaf makes another untracked file unreadable")
def test_verify_sh_keeps_an_untracked_file_that_predates_the_leaf_when_it_refuses_for_an_unreadable_file_2784(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    (repo / "notes.txt").write_text("the developer has not committed this yet\n")
    mutation = 'printf "secret\\n" > hidden.txt; chmod 000 hidden.txt'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, (repo / "notes.txt").read_text()) == (2, "the developer has not committed this yet\n")


@pytest.mark.process("a real git scratch repository whose pin verifier leaf rewrites its mutation record and makes it unreadable")
def test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_rewrote_its_mutation_record_and_made_it_unreadable_2764(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2764")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2764-mutations.md\n",
                                  {".tdd/issue-2764-mutations.md": "mutation one\n"})
    mutation = 'printf "rewritten\\n" > .tdd/issue-2764-mutations.md; chmod 000 .tdd/issue-2764-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository whose pin verifier leaf replaces a mutation record that was unreadable before it ran")
def test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_left_a_regular_file_where_the_mutation_record_was_unreadable_2764(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2764")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2764-mutations.md\n",
                                  {".tdd/issue-2764-mutations.md": "mutation one\n"})
    subprocess.run(["chmod", "000", str(repo / ".tdd" / "issue-2764-mutations.md")], check=True)
    mutation = 'rm -f .tdd/issue-2764-mutations.md; printf "mutation one\\n" > .tdd/issue-2764-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository whose pin verifier leaf replaces a mutation record that was a symlink before it ran")
def test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_replaced_a_symlinked_mutation_record_with_a_regular_file_2772(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2772")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2772-mutations.md\n", {})
    (tmp_path / "elsewhere.md").write_text("mutation one\n")
    (repo / ".tdd").mkdir(exist_ok=True)
    (repo / ".tdd" / "issue-2772-mutations.md").symlink_to(tmp_path / "elsewhere.md")
    mutation = 'rm -f .tdd/issue-2772-mutations.md; printf "mutation one\\n" > .tdd/issue-2772-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo, issue="2772")}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository holding an unreadable file, and a git wrapper translating Permission denied")
def test_verify_sh_does_not_accept_a_pass_from_a_verifier_leaf_that_left_an_unreadable_file_when_git_translates_its_messages_2772(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    wrapper = tmp_path / "translating-bin"
    wrapper.mkdir()
    (wrapper / "git").write_text(
        '#!/bin/sh\nerr="$(mktemp)"\n%s "$@" 2>"$err"\nrc=$?\n'
        'case "$LC_ALL" in de_*) sed "s/Permission denied/Zugriff verweigert/" "$err" >&2 ;; *) cat "$err" >&2 ;; esac\n'
        'rm -f "$err"\nexit $rc\n' % shutil.which("git"))
    (wrapper / "git").chmod(0o755)
    (repo / "hidden.txt").write_text("secret\n")
    subprocess.run(["chmod", "000", str(repo / "hidden.txt")], check=True)
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", "LC_ALL": "de_DE.UTF-8",
           "PATH": "%s:%s" % (wrapper, os.environ["PATH"]), **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository whose global config sets an external diff driver, color.ui=always and a textconv filter")
def test_verify_sh_saves_the_same_refusal_diff_whatever_the_global_git_config_says_1846(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {".gitattributes": "*.txt diff=shout\n"})
    driver = tmp_path / "external-driver"
    driver.write_text("#!/bin/sh\necho EXTERNAL-DRIVER-OUTPUT\n")
    driver.chmod(0o755)
    (tmp_path / ".gitconfig").write_text(
        "[diff]\n\texternal = %s\n[color]\n\tui = always\n[diff \"shout\"]\n\ttextconv = tr a-z A-Z <\n" % driver)
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "VERI_TEST_FAKE_MUTATE": 'printf "the verifier rewrote this\\n" > src.txt',
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    saved = list((repo / ".tdd").glob("*.diff"))
    text = saved[0].read_text() if saved else ""
    assert (code, [line for line in text.splitlines() if not line.startswith("index ")]) == (2, [
        "diff --git a/src.txt b/src.txt", "--- a/src.txt", "+++ b/src.txt", "@@ -1 +1 @@",
        "-the developer committed this", "+the verifier rewrote this"])


@pytest.mark.process("a real git scratch repository under the repo's own .gitignore that the verifier leaf writes into")
@pytest.mark.parametrize("tracked, mutation, verdict, expected_code, named", [
    ({}, 'mkdir -p projects/docs/.tdd && printf "{}\\n" > projects/docs/.tdd/events.jsonl',
     "VERDICT: PASS\nREASON: Target test and full suite are green.", 0, ["full suite are green"]),
    ({}, 'mkdir -p a/b/.tdd && printf "log\\n" > a/b/.tdd/run.log',
     "VERDICT: REJECT\nREASON: The target test still fails.", 1, ["target test still fails"]),
    ({".tdd/issue-569.md": "- [ ] a step\n"},
     'printf -- "- [x] a step\\n" > .tdd/issue-569.md && mkdir -p projects/docs/.tdd'
     ' && printf "{}\\n" > projects/docs/.tdd/events.jsonl',
     "VERDICT: PASS\nREASON: Target test and full suite are green.", 2,
     ["modified the repository", ".tdd/issue-569.md"]),
    ({"projects/docs/doomed.txt": "the developer committed this too\n"},
     'printf "the verifier rewrote this\\n" > src.txt && rm projects/docs/doomed.txt'
     ' && printf "new\\n" > projects/docs/added.txt && mkdir -p projects/docs/.tdd'
     ' && printf "{}\\n" > projects/docs/.tdd/events.jsonl',
     "VERDICT: PASS\nREASON: Target test and full suite are green.", 2,
     ["modified the repository", "src.txt", "projects/docs/doomed.txt", "projects/docs/added.txt"]),
])
def test_verify_sh_under_the_repos_own_gitignore_accepts_nested_run_state_and_refuses_an_edited_root_ledger_or_tracked_path_naming_each_569(
        tracked, mutation, verdict, expected_code, named, run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, (SCRIPTS.parents[2] / ".gitignore").read_bytes(), tracked)
    ignored = [subprocess.run(["git", "-C", str(repo), "check-ignore", "--no-index", "-q", path]).returncode == 0
               for path in (".tdd/issue-569.md", ".tdd/issue-569-spec.md")]
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation, "VERI_TEST_FAKE_OUT_TEXT": verdict,
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (ignored, code, [n for n in named if n not in out], "modified the repository" in out) == (
        [False, True], expected_code, [], expected_code == 2)


@pytest.mark.process("a real git scratch repository whose first verifier launch leaves an untracked file and whose second does not")
def test_verify_sh_relaunches_a_verifier_that_left_an_untracked_file_and_returns_the_relaunched_verdict_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "1")
    mutation = '[ -e .tdd/second-launch ] || { : > .tdd/second-launch; printf "stray\\n" > riting.ts; }'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    saved = list((repo / ".tdd").glob("*.diff"))
    diff = saved[0].read_text() if saved else ""
    log_events = repo / ".tdd" / "events.jsonl"
    relaunches = [json.loads(line) for line in log_events.read_text().splitlines()
                  if '"relaunch"' in line] if log_events.is_file() else []
    assert (code, git_state(repo), "riting.ts" in diff,
            [(r["event"], r.get("cause") != "no-verdict") for r in relaunches]) == (
        0, before, True, [("relaunch", True)])


@pytest.mark.process("a real git scratch repository whose first verifier launch edits a tracked file and whose second does not")
def test_verify_sh_relaunches_a_verifier_that_edited_a_tracked_file_and_returns_the_relaunched_verdict_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "1")
    mutation = '[ -e .tdd/second-launch ] || { : > .tdd/second-launch; printf "the verifier rewrote this\\n" > src.txt; }'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    log_events = repo / ".tdd" / "events.jsonl"
    relaunches = [json.loads(line) for line in log_events.read_text().splitlines()
                  if '"relaunch"' in line] if log_events.is_file() else []
    assert (code, git_state(repo), (repo / "src.txt").read_text(), [r.get("cause") for r in relaunches]) == (
        0, before, "the developer committed this\n", ["tree-change"])


@pytest.mark.process("a real git scratch repository whose first verifier launch commits and whose second does not")
def test_verify_sh_relaunches_a_verifier_that_moved_head_and_restores_head_and_the_tree_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "1")
    mutation = ('[ -e .tdd/second-launch ] || { : > .tdd/second-launch; printf "the verifier committed this\\n" > src.txt;'
                ' git commit -q -a -m "the verifier committed"; }')
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, _, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    log_events = repo / ".tdd" / "events.jsonl"
    relaunches = [json.loads(line) for line in log_events.read_text().splitlines()
                  if '"relaunch"' in line] if log_events.is_file() else []
    assert (code, git_state(repo), [r.get("cause") for r in relaunches]) == (0, before, ["tree-change"])


@pytest.mark.process("a real git scratch repository whose only verifier launch leaves an untracked file")
def test_verify_sh_refuses_a_verifier_that_left_an_untracked_file_without_a_relaunch_when_the_no_verdict_budget_is_0_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'echo launch >> .tdd/launches; printf "stray\\n" > riting.ts'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    launches = (repo / ".tdd" / "launches").read_text().splitlines()
    assert (code, "verifier leaf modified the repository — verdict not accepted" in out, launches,
            git_state(repo)) == (2, True, ["launch"], before)


@pytest.mark.process("a real git scratch repository whose every verifier launch leaves a new untracked file")
def test_verify_sh_writes_one_tree_change_relaunch_then_refuses_when_every_launch_leaves_an_untracked_file_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "1")
    mutation = 'echo launch >> .tdd/launches; printf "stray\\n" > "riting-$(wc -l < .tdd/launches).ts"'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    log_events = repo / ".tdd" / "events.jsonl"
    relaunches = [json.loads(line) for line in log_events.read_text().splitlines()
                  if '"relaunch"' in line] if log_events.is_file() else []
    assert (code, "verifier leaf modified the repository — verdict not accepted" in out,
            [r.get("cause") for r in relaunches], git_state(repo)) == (2, True, ["tree-change"], before)


def attempts_trace(repo, phase):
    refs = subprocess.run(["git", "-C", str(repo), "for-each-ref", "--format=%(refname)", "refs/veri/attempts/"],
                          capture_output=True, check=True).stdout.decode().splitlines()
    shown = [subprocess.run(["git", "-C", str(repo), "show", ref + ":src.txt"],
                            capture_output=True).stdout.decode() for ref in refs]
    attempts = repo / ".tdd" / "attempts"
    copies = sorted(attempts.iterdir()) if attempts.is_dir() else []
    log = (repo / ".tdd" / ("verify-%s.log" % phase)).read_bytes()
    log_events = repo / ".tdd" / "events.jsonl"
    events = [json.loads(line) for line in log_events.read_text().splitlines()] if log_events.is_file() else []
    return refs, shown, [c.name for c in copies], [c.read_bytes() == log for c in copies], events


PRIVATE = "The test asserts on a private helper, not observable behavior."


REJECT_PRIVATE = "VERDICT: REJECT\nREASON: " + PRIVATE


RAMBLE = "the leaf rambled and never rendered a verdict"


JUDGED = "the work the verifier judged\n"


BLOCKER = "refs/veri/attempts/625/6"


@pytest.mark.process("a real git scratch repository whose rejected attempts land under refs/veri/attempts/,"
                     " behind the real supervise.sh, every event appended in-process")
@pytest.mark.parametrize("phase, leaf, text, env, expected", [
    pytest.param("green", "answers", "VERDICT: REJECT\nREASON: the helper it asserts on is still private.",
                 {"VERI_ISSUE": "409", "VERI_STEP": "4"},
                 (1, "the helper it asserts on is still private.\n", [("REJECT", "409", "4", None)],
                  ["refs/veri/attempts/409/4/verify-green-{attempt}"], ["4-verify-green-{attempt}-reject.log"], False),
                 id="reject-preserved"),
    pytest.param("green", "answers", RAMBLE, {"VERI_ISSUE": "409", "VERI_STEP": "5", "VERI_NO_VERDICT_RETRIES": "0"},
                 (2, "\n", [("malformed", "409", "5", "no-verdict")],
                  ["refs/veri/attempts/409/5/verify-green-{attempt}"], ["5-verify-green-{attempt}-no-verdict.log"],
                  False), id="no-verdict-preserved"),
    pytest.param("green", "answers", GREEN, {"VERI_ISSUE": "409", "VERI_STEP": "7"},
                 (0, GREEN_REASON + "\n", [("PASS", "409", "7", None)], [], [], False), id="pass-nothing"),
    pytest.param("green", "fails", GREEN, {"VERI_ISSUE": "409", "VERI_STEP": "7"},
                 (0, GREEN_REASON + "\n", [("PASS", "409", "7", None)], [], [], False), id="clean-failure-nothing"),
    pytest.param("red", "answers", REJECT_PRIVATE, {"VERI_ISSUE": "625", "VERI_STEP": "6"},
                 (1, PRIVATE + "\n", [("REJECT", "625", "6", None)], [BLOCKER], [], True),
                 id="unpreservable-reason-alone"),
    pytest.param("red", "hangs", REJECT_PRIVATE, {"VERI_ISSUE": "409", "VERI_STEP": "8"},
                 (2, "verifier leaf killed-stuck — no verdict rendered (see .tdd/verify-red.log)\n", [],
                  ["refs/veri/attempts/409/8/verify-red-1"], ["8-verify-red-1-stuck.log"], False),
                 id="killed-leaves-no-verdict"),
])
def test_verify_sh_preserves_a_rejected_or_no_verdict_attempt_under_its_ref_and_a_copy_its_verdict_event_names_and_answers_the_verdicts_reason_and_code_alone(
        phase, leaf, text, env, expected, run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    (repo / "src.txt").write_text(JUDGED)
    if BLOCKER in expected[3]:
        subprocess.run(["git", "-C", str(repo), "update-ref", BLOCKER, "HEAD"], check=True)
    if leaf != "answers":
        claude = tmp_path / ("claude-" + leaf)
        claude.write_text({"fails": "#!/bin/sh\nprintf '%s' \"$VERI_TEST_FAKE_OUT_TEXT\"\nexit 1\n",
                           "hangs": HUNG_LEAF}[leaf])
        claude.chmod(0o755)
    step = checked_head(repo, issue=env["VERI_ISSUE"], step=int(env["VERI_STEP"])) if "VERI_STEP" in env else {}
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_OUT_TEXT": text,
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **step, **env}
    if leaf == "hangs":
        env.update(VERI_STUCK_RETRIES="0", VERI_TIMEOUT="0")
    verify = importlib.import_module("veri.verify")

    code, out, err = run_cli(verify, [*based(repo), *(FAST if phase == "green" else []), phase, str(tmp_path / "spec.md"),
                                      "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    refs, shown, copies, paired, events = attempts_trace(repo, phase)
    verdicts = [e for e in events if e.get("event") == "verdict"]
    attempt = verdicts[0].get("attempt") if verdicts else None
    want_code, want_out, want_verdicts, want_refs, want_copies, unpreserved = expected
    assert (code, out, [(e.get("verdict"), e.get("issue"), e.get("step"), e.get("cause")) for e in verdicts],
            refs, copies, "verify: could not preserve the reject attempt" in err) == (
        want_code, want_out, want_verdicts, [r.format(attempt=attempt) for r in want_refs],
        [c.format(attempt=attempt) for c in want_copies], unpreserved)
    assert (shown, paired) == ([JUDGED if r != BLOCKER else "the developer committed this\n" for r in refs],
                               [True] * len(copies))
    assert [e.get("event") for e in events if e.get("event") == "exit"] != []
    if leaf == "fails":
        assert (repo / ".tdd" / "verify-green.rc").read_text().strip() == "1"


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_verify_sh_diff_exits_1_without_launching_the_leaf_naming_the_pytest_case_a_step_deleted_that_an_earlier_step_added_1486(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_refuses_start():\n    pass\n")
    step_base = commit("an earlier step adds test_refuses_start")
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    commit("this step deletes test_refuses_start")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "no test fakes X any longer ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "tests/test_start.py::test_refuses_start" in out, started.exists()) == (1, True, False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, with origin/main rewritten"
                     " past the branch base, and a stub claude that records any start")
@pytest.mark.parametrize("deletes", [True, False], ids=["gate-reads-cases-at-branch-base", "prompt-diffs-from-branch-base"])
def test_4376_verify_sh_diff_takes_its_branch_base_from_the_branch_base_flag_not_origin_main_for_both_its_gate_and_its_prompt(
        deletes, run_cli, tmp_path):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_refuses_start():\n    pass\n")
    step_base = commit("an earlier step adds test_refuses_start")
    for ref in ("refs/remotes/origin/main", "refs/remotes/origin/HEAD"):
        subprocess.run(["git", "-C", str(repo), "update-ref", ref, step_base], check=True)
    if deletes:
        (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    else:
        (repo / "tests" / "test_other.py").write_text("def test_other():\n    pass\n")
    commit("this step")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, err = run_cli(
        verify, ["--step", "no test fakes X any longer ⟦diff-checked⟧", "--fast-cmd", "make unit",
                 "--branch-base", branch_base, "diff", str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    if deletes:
        assert (code, out.strip(), started.exists()) == (
            1, "step deleted test cases an earlier step added: tests/test_start.py::test_refuses_start", False), err
    else:
        prompt = " ".join((repo / ".tdd" / "verify-diff.prompt").read_text().split())
        assert (code, started.exists(), f"git diff {branch_base}..HEAD" in prompt,
                f"git diff {step_base}..HEAD" in prompt, f"branched at `{branch_base}`" in prompt) == (
            0, True, True, True, True), err


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_verify_sh_diff_still_launches_the_leaf_for_a_pytest_case_an_earlier_step_added_and_this_step_moved_to_another_file_under_the_same_name_1486(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    (repo / "tests" / "test_moved.py").write_text("def test_other():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_refuses_start():\n    pass\n")
    step_base = commit("an earlier step adds test_refuses_start")
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    (repo / "tests" / "test_moved.py").write_text(
        "def test_other():\n    pass\n\n\ndef test_refuses_start():\n    pass\n")
    commit("this step moves test_refuses_start to test_moved.py")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "no test fakes X any longer ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "test_refuses_start" in out, started.exists()) == (0, False, True)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2329_verify_sh_diff_launches_the_leaf_for_a_pytest_case_an_earlier_step_added_and_this_step_renamed_with_its_text_otherwise_unchanged(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_exits_with_the_command_code():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds test_exits_with_the_command_code")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_exits_1():\n    assert 1 == 1\n")
    commit("this step renames the case, its body unchanged")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "test_exits_with_the_command_code" in out, started.exists()) == (0, False, True)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2329_verify_sh_diff_exits_1_naming_a_renamed_case_whose_body_or_def_line_also_changed_and_a_removed_case_without_launching_the_leaf(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_body_alpha():\n    assert 1 == 1\n"
        "\n\ndef test_head_beta():\n    assert 2 == 2\n"
        "\n\ndef test_gone_gamma():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds three cases")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_body_renamed():\n    assert 1 == 2\n"
        "\n\ndef test_head_renamed(tmp_path):\n    assert 2 == 2\n")
    commit("this step renames two cases and changes a line of each, and removes the third")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, started.exists()) == (1, False)
    for vanished in ("test_body_alpha", "test_gone_gamma", "test_head_beta"):
        assert "tests/test_start.py::" + vanished in out


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2329_verify_sh_diff_exits_1_naming_a_renamed_case_whose_decorator_line_also_changed_without_launching_the_leaf(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\n@pytest.mark.timeout(5)\ndef test_decorated_old():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds test_decorated_old")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\n@pytest.mark.timeout(60)\ndef test_decorated_new():\n    assert 1 == 1\n")
    commit("this step renames the case and changes its decorator")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, started.exists()) == (1, False)
    assert "tests/test_start.py::test_decorated_old" in out


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2594_verify_sh_diff_exits_1_with_a_line_naming_a_case_renamed_and_changed_to_be_split_without_launching_the_leaf(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_defaults_to_3_2594():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds test_defaults_to_3_2594")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_defaults_to_5_2594():\n    assert 5 == 5\n")
    commit("this step renames the case and changes its body")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    named = [line for line in out.splitlines()
             if "tests/test_start.py::test_defaults_to_3_2594 -> " in line and "test_defaults_to_5_2594" in line]
    assert (code, started.exists(), len(named)) == (1, False, 1)
    assert "renamed" in named[0] and "split" in named[0]


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2594_verify_sh_diff_launches_the_leaf_and_exits_0_on_its_pass_printing_no_renamed_and_changed_line_for_a_case_renamed_with_its_body_and_def_line_unchanged(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_defaults_to_3_2594():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds test_defaults_to_3_2594")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_defaults_to_5_2594():\n    assert 3 == 3\n")
    commit("this step renames the case, its body unchanged")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, started.exists(), "renamed" in out or "split" in out) == (0, True, False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2594_verify_sh_diff_exits_1_with_the_deleted_cases_line_and_no_traceback_for_an_async_case_removed_with_no_counterpart(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\nasync def test_async_2594():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds test_async_2594")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_unrelated_2594():\n    assert 1 == 1\n")
    commit("this step removes the async case and adds an unrelated one")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, err = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists(), "Traceback" in err) == (
        1, "step deleted test cases an earlier step added: tests/test_start.py::test_async_2594", False, False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2594_verify_sh_diff_exits_1_with_the_deleted_cases_line_alone_for_a_removed_case_whose_def_line_no_added_case_shares_but_for_the_name(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_dropped_2594():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds test_dropped_2594")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_other_2594(tmp_path):\n    assert 5 == 5\n")
    commit("this step drops the case and adds one with another def line")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted test cases an earlier step added: tests/test_start.py::test_dropped_2594", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2419_verify_sh_diff_exits_1_naming_exactly_one_of_two_identical_removed_cases_when_one_added_case_carries_their_text(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_alpha():\n    assert 1 == 1\n"
        "\n\ndef test_beta():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds two identical cases")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_gamma():\n    assert 1 == 1\n")
    commit("this step removes both and adds one case with their text")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted test cases an earlier step added: tests/test_start.py::test_beta", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2419_verify_sh_diff_exits_1_naming_exactly_the_third_of_three_identical_removed_cases_when_two_added_cases_carry_their_text(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_alpha():\n    assert 1 == 1\n"
        "\n\ndef test_beta():\n    assert 1 == 1\n"
        "\n\ndef test_delta():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds three identical cases")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_gamma():\n    assert 1 == 1\n"
        "\n\ndef test_epsilon():\n    assert 1 == 1\n")
    commit("this step removes all three and adds two cases with their text")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted test cases an earlier step added: tests/test_start.py::test_delta", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2419_verify_sh_diff_launches_the_leaf_for_a_single_removed_case_renamed_to_one_added_case_while_an_identical_twin_stays(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_alpha():\n    assert 1 == 1\n"
        "\n\ndef test_twin():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds two identical cases")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_gamma():\n    assert 1 == 1\n"
        "\n\ndef test_twin():\n    assert 1 == 1\n")
    commit("this step renames one case; its identical twin stays")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "test_alpha" in out, started.exists()) == (0, False, True)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2329_verify_sh_diff_exits_1_naming_a_removed_case_whose_text_reappears_under_another_name_in_another_file(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    (repo / "tests" / "test_other.py").write_text("def test_other_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_moved_old():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds test_moved_old")
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    (repo / "tests" / "test_other.py").write_text(
        "def test_other_keeps():\n    pass\n\n\ndef test_moved_new():\n    assert 1 == 1\n")
    commit("this step removes the case and adds an identical one under another name in another file")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted test cases an earlier step added: tests/test_start.py::test_moved_old", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_verify_sh_diff_exits_2_without_launching_the_leaf_when_the_step_base_sha_does_not_resolve_1486(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "test_start.py").write_text("def test_keeps():\n    pass\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "branch base"], check=True)
    branch_base = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                                 capture_output=True).stdout.decode().strip()
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "no test fakes X any longer ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), "0123456789abcdef0123456789abcdef01234567"],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "VERDICT" in out, started.exists()) == (2, False, False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_verify_sh_diff_still_launches_the_leaf_and_returns_its_verdict_when_the_step_deletes_only_a_pytest_case_that_existed_at_the_branch_base_1486(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_fakes_x():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_other.py").write_text("def test_added_earlier():\n    pass\n")
    step_base = commit("an earlier step adds an unrelated case")
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    commit("this step deletes test_fakes_x, which predates the branch")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "no test fakes X any longer ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "test_fakes_x" in out, started.exists(), out == "fine.\n") == (0, False, True, True)


def test_verify_sh_green_exits_2_when_the_named_cases_check_cannot_read_the_suite_after_a_pass_1507(
        run_cli, tmp_path, monkeypatch, fake_processes):
    write_inputs(tmp_path)
    answering_leaf(monkeypatch, fake_processes, "VERDICT: PASS\nREASON: the named cases are gone.")
    verify = importlib.import_module("veri.verify")
    monkeypatch.setattr(verify.replaces_case_survivors, "survivors", lambda step: (2, "", ""))

    code, out, _ = run_cli(
        verify, [*based(tmp_path), "--step", "the replacement takes over: replaces 'stale first' in tests/demo.py"
                 " ⟦replaces-case⟧ ⟦criterion 1⟧", "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert code == 2


def test_verify_sh_green_returns_the_leafs_pass_unchanged_on_a_step_without_replaces_case_even_when_its_text_names_a_surviving_case_1507(
        run_cli, tmp_path, monkeypatch, fake_processes):
    write_inputs(tmp_path)
    (tmp_path / "tests" / "demo.py").write_text('verdict "stale first" 0\n')
    answering_leaf(monkeypatch, fake_processes, "VERDICT: PASS\nREASON: fine.")
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, [*based(tmp_path), "--step", "the replacement takes over: replaces 'stale first' in tests/demo.py"
                 " ⟦criterion 2⟧", "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (0, "fine.\n")


def test_verify_sh_green_returns_the_leafs_pass_with_exit_0_on_a_replaces_case_step_whose_every_named_case_is_gone_1507(
        run_cli, tmp_path, monkeypatch, fake_processes):
    write_inputs(tmp_path)
    (tmp_path / "tests" / "demo.py").write_text('verdict "kept case" 0\n')
    answering_leaf(monkeypatch, fake_processes, "VERDICT: PASS\nREASON: the named cases are gone.")
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, [*based(tmp_path), "--step", "the replacement takes over: replaces 'stale first', 'stale second' in tests/demo.py"
                 " ⟦replaces-case⟧ ⟦criterion 2⟧", "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (0, "the named cases are gone.\n")


def test_verify_sh_green_returns_the_leafs_pass_with_exit_0_on_a_step_naming_the_replaces_case_mark_without_a_replaces_clause_1603(
        run_cli, tmp_path, monkeypatch, fake_processes):
    write_inputs(tmp_path)
    answering_leaf(monkeypatch, fake_processes, "VERDICT: PASS\nREASON: fine.")
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, [*based(tmp_path), "--step", "the Red prompt describes the \u27e6replaces-case\u27e7 mark \u27e6criterion 1\u27e7",
                 "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (0, "fine.\n")


def test_verify_sh_green_returns_the_leafs_pass_with_exit_0_on_a_replaces_case_step_with_a_quoted_case_but_no_suite_path_1603(
        run_cli, tmp_path, monkeypatch, fake_processes):
    write_inputs(tmp_path)
    answering_leaf(monkeypatch, fake_processes, "VERDICT: PASS\nREASON: fine.")
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, [*based(tmp_path), "--step", "the Red prompt says replaces 'stale first' \u27e6replaces-case\u27e7 \u27e6criterion 4\u27e7",
                 "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (0, "fine.\n")


@pytest.mark.parametrize("suite, check", [
    ('verdict "kept case" 0\n', None),
    ('verdict "stale first" 0\n', None),
    ('verdict "kept case" 0\n', 2),
], ids=["every-named-case-gone", "a-named-case-survives", "the-check-cannot-answer"])
def test_verify_sh_green_returns_the_leafs_reject_with_exit_1_and_its_own_reason_on_a_replaces_case_step_whatever_the_named_cases_check_would_say_1507(
        suite, check, run_cli, tmp_path, monkeypatch, fake_processes):
    write_inputs(tmp_path)
    (tmp_path / "tests" / "demo.py").write_text(suite)
    answering_leaf(monkeypatch, fake_processes, "VERDICT: REJECT\nREASON: the replacement asserts nothing.")
    verify = importlib.import_module("veri.verify")
    if check is not None:
        monkeypatch.setattr(verify.replaces_case_survivors, "survivors", lambda step: (check, "", ""))

    code, out, _ = run_cli(
        verify, [*based(tmp_path), "--step", "the replacement takes over: replaces 'stale first' in tests/demo.py"
                 " ⟦replaces-case⟧ ⟦criterion 1⟧", "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (1, "the replacement asserts nothing.\n")


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that rewrites a tracked file")
def test_main_saves_the_content_diff_of_a_verifier_that_modified_a_tracked_file_under_dot_tdd_named_after_the_leaf_and_names_it_in_the_refusal_1846(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    new_repo(repo)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    origin_head_at(repo)
    expected = []
    verify = importlib.import_module("veri.verify")
    real_start = verify.leaf_tree_guard.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\nTWO\nthree\n")
        expected.append(git("diff", "HEAD", "--", "tracked.txt"))
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify.leaf_tree_guard, "start", stub_start)

    code = verify.main([*based("."), "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    out = capfd.readouterr().out
    named = [m for m in re.findall(r"\.tdd/verify-green[\w.-]*", out)
             if not m.endswith((".log", ".prompt"))]
    saved = [(repo / m).read_bytes() for m in named if (repo / m).is_file()]
    assert (code, len(named), saved, (repo / "tracked.txt").read_text()) == (
        2, 1, expected, "one\ntwo\nthree\n")


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that changes only a tracked file's mode")
def test_main_saves_a_mode_only_change_of_a_verifier_in_the_diff_byte_exactly_1846(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.sh").write_text("echo hi\n")
    (repo / "tracked.sh").chmod(0o755)
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    new_repo(repo)
    git("config", "core.fileMode", "true")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    origin_head_at(repo)
    launches = []
    verify = importlib.import_module("veri.verify")
    real_start = verify.leaf_tree_guard.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        launches.append(args)
        os.chmod(repo / "tracked.sh", 0o644)
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify.leaf_tree_guard, "start", stub_start)

    code = verify.main([*based("."), "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    capfd.readouterr()
    assert (code, len(launches), (repo / "tracked.sh").stat().st_mode & 0o777) == (0, 1, 0o755)


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that changes a tracked binary file")
def test_main_saves_a_binary_change_of_a_verifier_in_a_diff_that_applies_with_binary_1846(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    before = bytes([0, 1, 2, 255, 254, 0, 7]) * 40
    after = bytes([0, 9, 8, 255, 0, 0, 3, 128]) * 40
    (repo / "blob.bin").write_bytes(before)
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    new_repo(repo)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    origin_head_at(repo)
    verify = importlib.import_module("veri.verify")
    real_start = verify.leaf_tree_guard.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "blob.bin").write_bytes(after)
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify.leaf_tree_guard, "start", stub_start)

    code = verify.main([*based("."), "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    out = capfd.readouterr().out
    named = [m for m in re.findall(r"\.tdd/verify-green[\w.-]*", out)
             if not m.endswith((".log", ".prompt"))]
    applied = None
    if len(named) == 1 and (repo / named[0]).is_file():
        patch = (repo / named[0]).resolve()
        subprocess.run(["git", "apply", "--binary", str(patch)], cwd=repo,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        applied = (repo / "blob.bin").read_bytes()
    assert (code, len(named), applied) == (2, 1, after)


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that rewrites a tracked file and leaves a directory at the diff path")
def test_main_still_refuses_with_2_and_resets_the_tree_saying_the_diff_could_not_be_saved_when_its_path_is_a_directory_1846(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    new_repo(repo)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    origin_head_at(repo)
    verify = importlib.import_module("veri.verify")
    real_start = verify.leaf_tree_guard.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\nTWO\nthree\n")
        (repo / ".tdd" / "verify-green.diff").mkdir()
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify.leaf_tree_guard, "start", stub_start)

    try:
        code = verify.main([*based("."), "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    except OSError as error:
        code = repr(error)

    out = capfd.readouterr().out
    assert (code, "verifier leaf modified the repository" in out,
            bool(re.search(r"diff could not be saved", out)),
            (repo / "tracked.txt").read_text()) == (2, True, True, "one\ntwo\nthree\n")


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that rewrites a tracked file while git diff is made to fail")
def test_main_still_refuses_with_2_saying_the_diff_could_not_be_saved_and_writes_no_diff_when_git_diff_fails_1878(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    new_repo(repo)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    origin_head_at(repo)
    verify = importlib.import_module("veri.verify")
    real_start = verify.leaf_tree_guard.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\nTWO\nthree\n")
        git("config", "diff.orderFile", str(tmp_path / "no-such-order-file"))
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify.leaf_tree_guard, "start", stub_start)

    code = verify.main([*based("."), "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    out = capfd.readouterr().out
    assert (code, "verifier leaf modified the repository" in out,
            bool(re.search(r"diff could not be saved to \.tdd/verify-green\.diff", out)),
            sorted(p.name for p in (repo / ".tdd").glob("*.diff"))) == (2, True, True, [])


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that rewrites a tracked file while git diff is made to fail over an earlier refusal's diff")
def test_main_removes_an_earlier_refusals_diff_when_this_refusals_diff_could_not_be_saved_1878(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    new_repo(repo)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    origin_head_at(repo)
    (repo / ".tdd").mkdir(exist_ok=True)
    (repo / ".tdd" / "verify-green.diff").write_text("an earlier refusal's diff\n")
    verify = importlib.import_module("veri.verify")
    real_start = verify.leaf_tree_guard.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\nTWO\nthree\n")
        git("config", "diff.orderFile", str(tmp_path / "no-such-order-file"))
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify.leaf_tree_guard, "start", stub_start)

    code = verify.main([*based("."), "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    out = capfd.readouterr().out
    assert (code, bool(re.search(r"diff could not be saved to \.tdd/verify-green\.diff", out)),
            sorted(p.name for p in (repo / ".tdd").glob("*.diff"))) == (2, True, [])


@pytest.mark.process("a real git scratch repository, a stub verifier leaf that rewrites a tracked file, and a real git apply --check")
def test_main_saves_a_diff_that_passes_git_apply_check_whatever_the_users_prefix_context_and_abbreviation_config_says_1878(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\nfour\nfive\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    new_repo(repo)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    origin_head_at(repo)
    verify = importlib.import_module("veri.verify")
    real_start = verify.leaf_tree_guard.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\ntwo\nTHREE\nfour\nfive\n")
        git("config", "diff.noprefix", "true")
        git("config", "diff.context", "0")
        git("config", "core.abbrev", "4")
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify.leaf_tree_guard, "start", stub_start)

    code = verify.main([*based("."), "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    capfd.readouterr()
    saved = list((repo / ".tdd").glob("*.diff"))
    checked = None
    if len(saved) == 1:
        checked = subprocess.run(["git", "apply", "--check", str(saved[0])], cwd=repo,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode
    assert (code, len(saved), checked) == (2, 1, 0)


@pytest.mark.process("a real git scratch repository whose rebased range the marker check reads, and a stub claude that records any start")
def test_verify_sh_rebase_exits_1_without_launching_the_leaf_naming_the_commit_and_file_that_added_a_conflict_marker_a_later_commit_removed_2516(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 2 |\n")
    onto = commit("onto")
    origin_head_at(repo)
    (repo / "docs" / "backend.md").write_text(
        "| a | b |\n|---|---|\n<<<<<<< HEAD\n| 1 | 2 |\n=======\n| 1 | 3 |\n>>>>>>> topic\n")
    marked = commit("rebase resolution keeping the markers")
    (repo / "notes.txt").write_text("unrelated\n")
    commit("an unrelated commit")
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 3 |\n")
    commit("a later commit removes the markers")
    pre_rebase = onto
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, [*based(repo), "rebase", str(tmp_path / "spec.md"), onto, pre_rebase],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, marked in out, "docs/backend.md" in out, started.exists()) == (1, True, True, False)


@pytest.mark.process("a real git scratch repository whose rebased range the marker check reads, and a stub claude that records any start")
def test_verify_sh_rebase_exits_1_without_launching_the_leaf_when_a_commit_added_only_a_closing_conflict_marker_2516(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 2 |\n")
    onto = commit("onto")
    origin_head_at(repo)
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 2 |\n>>>>>>> topic\n")
    marked = commit("rebase resolution keeping a closing marker")
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 3 |\n")
    commit("a later commit removes the marker")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, [*based(repo), "rebase", str(tmp_path / "spec.md"), onto, onto],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, marked in out, "docs/backend.md" in out, started.exists()) == (1, True, True, False)


@pytest.mark.process("a real git scratch repository whose rebased range the marker check reads, and a stub claude that records any start")
def test_verify_sh_rebase_launches_the_leaf_and_returns_its_verdict_when_no_commit_of_the_range_adds_a_conflict_marker_2516(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 2 |\n")
    onto = commit("onto")
    origin_head_at(repo)
    (repo / "docs" / "backend.md").write_text("Title\n=======\n| a | b |\n|---|---|\n| 1 | 3 |\n")
    commit("a clean resolution with a setext heading")
    (repo / "notes.txt").write_text("unrelated\n")
    commit("an unrelated commit")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, [*based(repo), "rebase", str(tmp_path / "spec.md"), onto, onto],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "docs/backend.md" in out, started.exists()) == (0, False, True)


def rebased_repo_and_recorder(tmp_path):
    """A scratch repo with one clean commit past <onto>, and a stub claude that records any start."""
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 2 |\n")
    onto = commit("onto")
    origin_head_at(repo)
    (repo / "notes.txt").write_text("unrelated\n")
    commit("a clean rebased commit")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    return repo, onto, claude, started


def run_rebase_verify(run_cli, tmp_path, repo, onto, claude):
    return run_cli(
        importlib.import_module("veri.verify"), [*based(repo), "rebase", str(tmp_path / "spec.md"), onto, onto],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)


@pytest.mark.process("a real git scratch repository whose working tree holds an uncommitted change to a tracked file, and a stub claude that records any start")
def test_verify_sh_rebase_exits_2_without_launching_the_leaf_naming_a_tracked_file_left_modified_and_uncommitted_4552(
        run_cli, tmp_path):
    repo, onto, claude, started = rebased_repo_and_recorder(tmp_path)
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 3 |\n")

    code, _, err = run_rebase_verify(run_cli, tmp_path, repo, onto, claude)

    assert (code, err.rstrip().endswith(": docs/backend.md"), started.exists()) == (2, True, False)


@pytest.mark.process("a real git scratch repository whose index file is corrupt, so git status fails, and a stub claude that records any start")
def test_verify_sh_rebase_exits_2_without_launching_the_leaf_when_git_status_fails_4552(run_cli, tmp_path):
    repo, onto, claude, started = rebased_repo_and_recorder(tmp_path)
    (repo / ".git" / "index").write_bytes(b"not an index")

    code, _, err = run_rebase_verify(run_cli, tmp_path, repo, onto, claude)

    assert (code, "git status failed" in err, started.exists()) == (2, True, False)


@pytest.mark.process("a real git scratch repository whose tracked files are committed but which holds an untracked file, and a stub claude that records any start")
def test_verify_sh_rebase_launches_the_leaf_when_only_an_untracked_file_is_present_4552(run_cli, tmp_path):
    repo, onto, claude, started = rebased_repo_and_recorder(tmp_path)
    (repo / "scratch.txt").write_text("untracked\n")

    code, _, _ = run_rebase_verify(run_cli, tmp_path, repo, onto, claude)

    assert (code, started.exists()) == (0, True)


@pytest.mark.process("a real git scratch repository whose pin verifier leaf replaces a mutation record that was a directory before it ran")
def test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_replaced_a_directory_mutation_record_with_a_regular_file_2772(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2772")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2772-mutations.md\n", {})
    (repo / ".tdd" / "issue-2772-mutations.md").mkdir(parents=True)
    mutation = 'rmdir .tdd/issue-2772-mutations.md; printf "mutation one\\n" > .tdd/issue-2772-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_TEST_FAKE_MUTATE": mutation,
           "VERI_TEST_FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo, issue="2772")}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, [*based(repo), "--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


def test_4375_verify_sh_pin_renders_the_prompt_with_branch_base_filled_by_its_branch_base_flag_never_a_merge_base(
        run_cli, tmp_path, monkeypatch, fake_processes):
    base = "3f9a1c0d5e7b"
    (tmp_path / "spec.md").write_text(SPEC)
    launched = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine")
    fallback = subprocess.run

    def fake(args, *rest, **kwargs):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "git" and "merge-base" in words and "HEAD" in words:
            return subprocess.CompletedProcess(args, 0, b"0123abcdef01\n", b"")
        return fallback(args, *rest, **kwargs)

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, ["--branch-base", base, "--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"],
                         env={"HOME": str(tmp_path)}, cwd=tmp_path)

    prompt = launched[0][1] if launched else ""
    assert (code, f"--before {base} --keep" in prompt, "{{BRANCH_BASE}}" in prompt) == (0, True, False)


def test_2916_verify_green_with_veri_issue_hands_the_runs_ledger_to_the_builder_so_the_prompt_lists_its_later_unchecked_steps(
        run_cli, tmp_path, monkeypatch, fake_processes):
    (tmp_path / "spec.md").write_text(SPEC)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-2916.md").write_text(
        "- [ ] first criterion\n- [ ] second criterion\n- [ ] third criterion\n")
    launched = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine")
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, [*based(tmp_path), "--step", "first criterion", "--fast-cmd", "make unit", "green", "spec.md",
                                  "tests/test_slugify.py"],
                         env={"HOME": str(tmp_path), "VERI_ISSUE": "2916"}, cwd=tmp_path)

    prompt = launched[0][1] if launched else ""
    assert (code, "- second criterion" in prompt, "- third criterion" in prompt,
            "- first criterion" in prompt) == (0, True, True, False), prompt


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2897_verify_sh_diff_exits_1_with_the_deleted_cases_line_for_a_go_test_func_removed_from_a_test_go_file(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "pkg").mkdir()
    (repo / "pkg" / "start_test.go").write_text("package pkg\n\nfunc TestKeeps(t *testing.T) {\n}\n")
    branch_base = commit("branch base")
    (repo / "pkg" / "start_test.go").write_text(
        "package pkg\n\nfunc TestKeeps(t *testing.T) {\n}\n\nfunc TestDropped2897(t *testing.T) {\n\tif 3 != 3 {\n\t\tt.Fatal()\n\t}\n}\n")
    step_base = commit("an earlier step adds TestDropped2897")
    (repo / "pkg" / "start_test.go").write_text("package pkg\n\nfunc TestKeeps(t *testing.T) {\n}\n")
    commit("this step removes TestDropped2897")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted test cases an earlier step added: pkg/start_test.go::TestDropped2897", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2897_verify_sh_diff_exits_1_with_the_deleted_cases_line_for_an_it_case_removed_from_a_test_js_file(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "web").mkdir()
    (repo / "web" / "start.test.js").write_text('it("keeps", () => {\n});\n')
    branch_base = commit("branch base")
    (repo / "web" / "start.test.js").write_text(
        'it("keeps", () => {\n});\n\nit("dropped2897", () => {\n  expect(3).toBe(3);\n});\n')
    step_base = commit("an earlier step adds dropped2897")
    (repo / "web" / "start.test.js").write_text('it("keeps", () => {\n});\n')
    commit("this step removes dropped2897")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip().startswith("step deleted test cases an earlier step added: web/start.test.js::"),
            started.exists()) == (1, True, False), out


def run_2897_diff(run_cli, tmp_path, path, base_text, added_text, final_text):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message, text):
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text(text)
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    branch_base = commit("branch base", base_text)
    step_base = commit("an earlier step adds cases", added_text)
    commit("this step edits them", final_text)
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")
    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff",
                 str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)
    return code, out.strip(), started.exists()


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2897_verify_sh_diff_does_not_refuse_a_non_test_go_func_removed_from_a_test_go_file(run_cli, tmp_path):
    keep = "package pkg\n\nfunc TestKeeps(t *testing.T) {\n}\n"
    code, out, started = run_2897_diff(run_cli, tmp_path, "pkg/start_test.go", keep,
                                       keep + "\nfunc helper2897() {\n}\n", keep)

    assert (code, "deleted test cases" in out, started) == (0, False, True), out


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2897_verify_sh_diff_refuses_an_indented_it_case_removed_by_deleting_its_describe_in_a_test_js_file(
        run_cli, tmp_path):
    keep = 'it("keeps", () => {\n});\n'
    block = 'describe("group2897", () => {\n  it("nested2897", () => {\n    expect(3).toBe(3);\n  });\n});\n'
    code, out, started = run_2897_diff(run_cli, tmp_path, "web/start.test.js", keep, keep + "\n" + block, keep)

    assert (code, out, started) == (
        1, "step deleted test cases an earlier step added: web/start.test.js::nested2897", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2897_verify_sh_diff_does_not_refuse_an_it_case_removed_from_a_plain_js_file(run_cli, tmp_path):
    keep = 'it("keeps", () => {\n});\n'
    code, out, started = run_2897_diff(run_cli, tmp_path, "web/helpers.js", keep,
                                       keep + '\nit("dropped2897", () => {\n  run();\n});\n', keep)

    assert (code, "deleted test cases" in out, started) == (0, False, True), out


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_3110_verify_sh_diff_refuses_a_single_quoted_it_case_removed_from_a_test_js_file(run_cli, tmp_path):
    keep = "it('keeps', () => {\n});\n"
    code, out, started = run_2897_diff(run_cli, tmp_path, "web/start.test.js", keep,
                                       keep + "\nit('dropped3110', () => {\n  expect(3).toBe(3);\n});\n", keep)

    assert (code, out, started) == (
        1, "step deleted test cases an earlier step added: web/start.test.js::dropped3110", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_3110_verify_sh_diff_refuses_a_backtick_it_case_removed_from_a_test_js_file(run_cli, tmp_path):
    keep = "it(`keeps`, () => {\n});\n"
    code, out, started = run_2897_diff(run_cli, tmp_path, "web/start.test.js", keep,
                                       keep + "\nit(`dropped3110`, () => {\n  expect(3).toBe(3);\n});\n", keep)

    assert (code, out, started) == (
        1, "step deleted test cases an earlier step added: web/start.test.js::dropped3110", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_3110_verify_sh_diff_refuses_a_double_quoted_test_case_removed_from_a_test_js_file(run_cli, tmp_path):
    keep = 'test("keeps", () => {\n});\n'
    code, out, started = run_2897_diff(run_cli, tmp_path, "web/start.test.js", keep,
                                       keep + '\ntest("dropped3110", () => {\n  expect(3).toBe(3);\n});\n', keep)

    assert (code, out, started) == (
        1, "step deleted test cases an earlier step added: web/start.test.js::dropped3110", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_3110_verify_sh_diff_refuses_a_single_quoted_test_case_removed_from_a_test_js_file(run_cli, tmp_path):
    keep = "test('keeps', () => {\n});\n"
    code, out, started = run_2897_diff(run_cli, tmp_path, "web/start.test.js", keep,
                                       keep + "\ntest('dropped3110', () => {\n  expect(3).toBe(3);\n});\n", keep)

    assert (code, out, started) == (
        1, "step deleted test cases an earlier step added: web/start.test.js::dropped3110", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_3110_verify_sh_diff_refuses_a_double_quoted_it_case_removed_from_a_spec_js_file(run_cli, tmp_path):
    keep = 'it("keeps", () => {\n});\n'
    code, out, started = run_2897_diff(run_cli, tmp_path, "web/start.spec.js", keep,
                                       keep + '\nit("dropped3110", () => {\n  expect(3).toBe(3);\n});\n', keep)

    assert (code, out, started) == (
        1, "step deleted test cases an earlier step added: web/start.spec.js::dropped3110", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_3110_verify_sh_diff_does_not_refuse_a_single_quoted_test_case_kept_in_a_spec_js_file_that_is_otherwise_edited(
        run_cli, tmp_path):
    keep = 'it("keeps", () => {\n});\n'
    case = "\ntest('kept3110', () => {\n  expect(3).toBe(3);\n});\n"
    code, out, started = run_2897_diff(run_cli, tmp_path, "web/start.spec.js", keep, keep + case,
                                       keep.replace("keeps", "keeps edited") + case)

    assert (code, "deleted test cases" in out, started) == (0, False, True), out


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_3110_verify_sh_diff_does_not_refuse_a_single_quoted_test_case_renamed_in_a_spec_js_file(run_cli, tmp_path):
    keep = 'it("keeps", () => {\n});\n'
    body = "', () => {\n  expect(3).toBe(3);\n});\n"
    code, out, started = run_2897_diff(run_cli, tmp_path, "web/start.spec.js", keep,
                                       keep + "\ntest('old3110" + body, keep + "\ntest('new3110" + body)

    assert (code, "deleted test cases" in out, started) == (0, False, True), out


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2897_verify_sh_diff_does_not_refuse_a_go_test_renamed_in_a_test_go_file_with_its_body_unchanged(
        run_cli, tmp_path):
    keep = "package pkg\n\nfunc TestKeeps(t *testing.T) {\n}\n"
    body = "{\n\tif 3 != 3 {\n\t\tt.Fatal()\n\t}\n}\n"
    code, out, started = run_2897_diff(run_cli, tmp_path, "pkg/start_test.go", keep,
                                       keep + "\nfunc TestOld2897(t *testing.T) " + body,
                                       keep + "\nfunc TestNew2897(t *testing.T) " + body)

    assert (code, "deleted test cases" in out, started) == (0, False, True), out


@pytest.mark.process("a real git scratch repository whose working tree and git stash create snapshot the diff check reads, and a stub claude that records any start")
def test_3120_verify_sh_diff_with_supersede_base_exits_1_naming_a_case_the_uncommitted_edits_delete_though_head_still_holds_it(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    test_file = repo / "tests" / "test_start.py"
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    test_file.write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    keeps_and_old = "def test_keeps():\n    pass\n\n\ndef test_old_3120():\n    assert 3 == 3\n"
    test_file.write_text(keeps_and_old)
    step_base = commit("an earlier step adds test_old_3120")
    test_file.write_text(keeps_and_old.replace("pass", "assert True", 1))
    snapshot = subprocess.run(["git", "-C", str(repo), "stash", "create"], check=True,
                              capture_output=True).stdout.decode().strip()
    assert snapshot
    test_file.write_text("def test_keeps():\n    assert True\n")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit",
                 "--supersede-base", snapshot, "--branch-base", branch_base, "diff", str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted test cases an earlier step added: tests/test_start.py::test_old_3120", False)


@pytest.mark.process("a real git scratch repository whose working tree and git stash create snapshot the diff check reads, and a stub claude that records any start")
def test_3120_verify_sh_diff_without_supersede_base_still_compares_against_head_so_an_uncommitted_deletion_is_not_reported(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    test_file = repo / "tests" / "test_start.py"
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    test_file.write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    keeps_and_old = "def test_keeps():\n    pass\n\n\ndef test_old_3120():\n    assert 3 == 3\n"
    test_file.write_text(keeps_and_old)
    step_base = commit("an earlier step adds test_old_3120")
    test_file.write_text(keeps_and_old.replace("pass", "assert True", 1))
    snapshot = subprocess.run(["git", "-C", str(repo), "stash", "create"], check=True,
                              capture_output=True).stdout.decode().strip()
    assert snapshot
    test_file.write_text("def test_keeps():\n    assert True\n")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit", "--branch-base", branch_base, "diff", str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "deleted test cases" in out, started.exists()) == (0, False, True), out


@pytest.mark.process("a real git scratch repository whose working tree and git stash create snapshot the diff check reads, and a stub claude that records any start")
def test_3120_verify_sh_diff_with_supersede_base_does_not_report_a_case_the_uncommitted_edits_only_rename(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    test_file = repo / "tests" / "test_start.py"
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    test_file.write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    keeps_and_old = "def test_keeps():\n    pass\n\n\ndef test_old_3120():\n    assert 3 == 3\n"
    test_file.write_text(keeps_and_old)
    step_base = commit("an earlier step adds test_old_3120")
    test_file.write_text(keeps_and_old.replace("pass", "assert True", 1))
    snapshot = subprocess.run(["git", "-C", str(repo), "stash", "create"], check=True,
                              capture_output=True).stdout.decode().strip()
    assert snapshot
    test_file.write_text("def test_keeps():\n    assert True\n\n\ndef test_renamed_3120():\n    assert 3 == 3\n")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit",
                 "--supersede-base", snapshot, "--branch-base", branch_base, "diff", str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "deleted test cases" in out, started.exists()) == (0, False, True), out


@pytest.mark.process("a real git scratch repository whose working tree and git stash create snapshot the diff check reads, and a stub claude that records any start")
def test_3120_verify_sh_diff_with_supersede_base_tells_the_step_to_split_when_the_uncommitted_edits_rename_and_change_a_case(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    test_file = repo / "tests" / "test_start.py"
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    test_file.write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    keeps_and_old = "def test_keeps():\n    pass\n\n\ndef test_old_3120():\n    assert 3 == 3\n"
    test_file.write_text(keeps_and_old)
    step_base = commit("an earlier step adds test_old_3120")
    test_file.write_text(keeps_and_old.replace("pass", "assert True", 1))
    snapshot = subprocess.run(["git", "-C", str(repo), "stash", "create"], check=True,
                              capture_output=True).stdout.decode().strip()
    assert snapshot
    test_file.write_text("def test_keeps():\n    assert True\n\n\ndef test_renamed_3120():\n    assert 4 == 4\n")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit",
                 "--supersede-base", snapshot, "--branch-base", branch_base, "diff", str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step renamed and changed test cases, so the step must be split: tests/test_start.py::test_old_3120 -> test_renamed_3120", False)


@pytest.mark.process("a real git scratch repository whose frozen-edit snapshot commit the diff check reads instead of HEAD, and a stub claude that records any start")
def test_4730_verify_sh_diff_with_frozen_edit_judges_the_snapshot_tip_so_a_case_it_deletes_is_named_though_head_still_holds_it(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    new_repo(repo)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    test_file = repo / "tests" / "test_start.py"
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    test_file.write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    keeps_and_old = "def test_keeps():\n    pass\n\n\ndef test_old_4730():\n    assert 3 == 3\n"
    test_file.write_text(keeps_and_old)
    step_base = commit("an earlier step adds test_old_4730")
    test_file.write_text("def test_keeps():\n    assert True\n")
    snapshot = commit("the frozen edit's snapshot drops test_old_4730")
    subprocess.run(["git", "-C", str(repo), "reset", "-q", "--hard", step_base], check=True)
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit",
                 "--frozen-edit", snapshot, "--branch-base", branch_base, "diff", str(tmp_path / "spec.md"), step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted test cases an earlier step added: tests/test_start.py::test_old_4730", False)
