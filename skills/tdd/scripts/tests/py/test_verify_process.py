"""Cases for veri/verify.py that start a real process: the verify.sh entry point."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import INTERPRETER_VENV
from test_supervise import checked_step, committed_head

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("verify.sh run as a real shim over veri/verify.py, a real supervise.sh and run-leaf.sh"
                     " around a stub claude that answers VERDICT: PASS")
def test_verify_sh_green_rejects_a_pass_on_a_replaces_case_step_naming_each_case_its_suite_still_holds_1507(
        tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / "tests" / "x.test.sh").write_text("test\n")
    (tmp_path / "tests" / "demo.test.sh").write_text('verdict "kept case" 0\nverdict "stale second" 0\n')
    claude = tmp_path / "claude-pass"
    claude.write_text("#!/bin/sh\nprintf 'VERDICT: PASS\\nREASON: the named cases are gone.'\n")
    claude.chmod(0o755)
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_step(tmp_path, committed_head(tmp_path))}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), "--step", "the replacement takes over: replaces 'stale first', 'stale second'"
         " in tests/demo.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧", "--fast-cmd", "make unit", "green", "spec.md",
         "tests/x.test.sh"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True)

    assert (done.returncode, b"stale second" in done.stdout, b"stale first" in done.stdout) == (1, True, False)


@pytest.mark.process("verify.sh run as a real shim over veri/verify.py and a real supervise.sh around a stub claude,"
                     " from a subdirectory of a throwaway git repo")
def test_verify_sh_run_from_a_subdirectory_writes_its_prompt_and_run_state_under_the_repo_root_1895(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
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
        [str(SCRIPTS / "verify.sh"), "--fast-cmd", "make unit", "green", "../spec.md", "../x_test.py", "x_test.py::test_x"],
        cwd=sub, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert ((tmp_path / ".tdd" / "verify-green.prompt").exists(), (sub / ".tdd").exists()) == (True, False), done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a real lint gate and a real test runner, around a stub claude")
def test_verify_sh_red_whose_lint_gate_fails_on_its_tree_but_passes_without_it_exits_1_with_a_gate_reason_and_launches_no_verifier(
        tmp_path):
    committed_head(tmp_path)
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
        [str(SCRIPTS / "verify.sh"), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    first = done.stdout.splitlines()[0] if done.stdout else ""
    assert (done.returncode, first.startswith("GATE:"), "sh lint.sh" in first, "F841" in first,
            launched.exists()) == (1, True, True, True, False), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a passing lint gate and a real test runner, around a stub claude")
def test_verify_sh_red_whose_lint_gate_passes_and_whose_only_failure_is_the_target_test_launches_the_verifier_and_its_pass_stands(
        tmp_path):
    head = committed_head(tmp_path)
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
        [str(SCRIPTS / "verify.sh"), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, launched.exists()) == (0, False, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a passing lint gate, an empty segment and a real test runner, around a stub claude")
def test_verify_sh_red_whose_test_command_has_an_empty_gate_segment_runs_and_reports_no_empty_gate_and_launches_the_verifier(
        tmp_path):
    head = committed_head(tmp_path)
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
        [str(SCRIPTS / "verify.sh"), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, launched.exists()) == (0, False, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a real lint gate and a real test runner, around a stub claude")
def test_verify_sh_red_whose_lint_gate_written_with_surrounding_whitespace_fails_exits_1_with_a_gate_reason_naming_the_trimmed_command(
        tmp_path):
    committed_head(tmp_path)
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
        [str(SCRIPTS / "verify.sh"), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    first = done.stdout.splitlines()[0] if done.stdout else ""
    assert (done.returncode, first.startswith("GATE: sh lint.sh fails on the Red's tree")) == (1, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a failing lint gate printing a padded line and a real test runner, around a stub claude")
def test_verify_sh_red_whose_failing_lint_gate_prints_its_offending_line_padded_with_whitespace_exits_1_with_that_line_trimmed(
        tmp_path):
    head = committed_head(tmp_path)
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
        [str(SCRIPTS / "verify.sh"), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    first = done.stdout.splitlines()[0] if done.stdout else ""
    assert (done.returncode, first) == (
        1, "GATE: sh lint.sh fails on the Red's tree: tests/test_slugify.py:3: F841 local variable 'unused' is never used"
    ), done.stdout + done.stderr


@pytest.mark.process("verify.sh green run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a failing lint gate and a real test runner, around a stub claude")
def test_verify_sh_green_with_the_same_test_command_whose_lint_gate_fails_is_not_refused_with_a_gate_reason_and_launches_the_verifier(
        tmp_path):
    head = committed_head(tmp_path)
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
        [str(SCRIPTS / "verify.sh"), "--fast-cmd", "make unit", "green", "spec.md", "tests/test_slugify.py"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, launched.exists()) == (0, False, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD chains a lint gate red on both trees and a real test runner, around a stub claude")
def test_verify_sh_red_whose_lint_gate_fails_on_the_tree_without_the_red_too_exits_2_naming_the_gate_as_red_before_the_red_and_launches_no_verifier(
        tmp_path):
    committed_head(tmp_path)
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
        [str(SCRIPTS / "verify.sh"), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, "sh lint.sh" in done.stderr,
            "red before the Red" in done.stderr, "pre-existing" in done.stderr,
            launched.exists()) == (2, False, True, True, True, False), done.stdout + done.stderr


@pytest.mark.process("verify.sh red run as a real shim over veri/verify.py in a throwaway git repo whose"
                     " VERI_TEST_CMD is a single test runner whose only failure names the target test, around a stub claude")
def test_verify_sh_red_whose_test_command_is_a_single_runner_with_no_lint_gate_launches_the_verifier_and_is_not_rejected_with_a_gate_reason(
        tmp_path):
    head = committed_head(tmp_path)
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
        [str(SCRIPTS / "verify.sh"), "red", "spec.md", "tests/test_slugify.py", "test_lowercases"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (done.returncode, "GATE:" in done.stdout, launched.exists()) == (0, False, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that records the VERI_MUTATION_RECORD it was launched with")
def test_verify_sh_pin_launches_its_verifier_with_the_mutation_record_set_to_the_absolute_path_of_the_issue_file_2506(
        tmp_path):
    head = committed_head(tmp_path)
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    seen = tmp_path / ".tdd" / "seen-record"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\nprintf '%s' \"$VERI_MUTATION_RECORD\" > {seen}\n"
                      "printf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           **checked_step(tmp_path, head, issue="2506")}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), "--fast-cmd", "make unit", "pin", "spec.md", "tests/test_x.py"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    got = seen.read_text() if seen.exists() else None
    assert (done.returncode, got) == (0, str(tmp_path / ".tdd" / "issue-2506-mutations.md")), done.stdout + done.stderr


@pytest.mark.process("verify.sh green run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that records whether VERI_MUTATION_RECORD is set in the environment it was launched with")
def test_verify_sh_green_with_an_issue_launches_its_verifier_without_the_mutation_record_set_2506(tmp_path):
    head = committed_head(tmp_path)
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    seen = tmp_path / ".tdd" / "seen-record"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\nprintf '%s' \"${{VERI_MUTATION_RECORD+set}}\" > {seen}\n"
                     "printf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           **checked_step(tmp_path, head, issue="2506")}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), "--fast-cmd", "make unit", "green", "spec.md", "tests/test_x.py"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    got = seen.read_text() if seen.exists() else None
    assert (done.returncode, got) == (0, ""), done.stdout + done.stderr


@pytest.mark.process("verify.sh green run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that records whether VERI_MUTATION_RECORD is set in the environment it was launched with")
def test_verify_sh_green_launches_its_verifier_without_an_ambient_mutation_record_2506(tmp_path):
    head = committed_head(tmp_path)
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    seen = tmp_path / ".tdd" / "seen-record"
    claude = tmp_path / "claude-pass"
    claude.write_text(f"#!/bin/sh\nprintf '%s' \"${{VERI_MUTATION_RECORD+set}}\" > {seen}\n"
                     "printf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01",
           "VERI_MUTATION_RECORD": str(tmp_path / ".tdd" / "issue-2506-mutations.md"),
           **checked_step(tmp_path, head, issue="2506")}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), "--fast-cmd", "make unit", "green", "spec.md", "tests/test_x.py"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    got = seen.read_text() if seen.exists() else None
    assert (done.returncode, got) == (0, ""), done.stdout + done.stderr


def run_verify_writing(tmp_path, phase, writes, then="", cwd=None, recorded=None):
    head = committed_head(tmp_path)
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
        [str(SCRIPTS / "verify.sh"), "--fast-cmd", "make unit", phase, up + "spec.md", up + "tests/test_x.py"],
        cwd=tmp_path / (cwd or ""), env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return done, record


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that appends to the tracked mutation record before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_writes_only_its_mutation_record_takes_the_pass_and_keeps_the_record_2741(tmp_path):
    done, record = run_verify_writing(tmp_path, "pin", [".tdd/issue-2741-mutations.md"])

    assert (done.returncode, "modified the repository" in done.stdout, record.exists()) == (0, False, True), \
        done.stdout + done.stderr


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


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py from a subdirectory of a throwaway git repo,"
                     " around a stub claude that appends to the mutation record before answering VERDICT: PASS")
def test_verify_sh_pin_run_from_a_subdirectory_whose_verifier_writes_only_its_mutation_record_takes_the_pass_2741(tmp_path):
    done, record = run_verify_writing(tmp_path, "pin", [".tdd/issue-2741-mutations.md"], cwd="skills")

    assert (done.returncode, "modified the repository" in done.stdout, record.exists()) == (0, False, True), \
        done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo, around a stub"
                     " claude that appends to the mutation record and commits before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_writes_its_mutation_record_and_moves_head_is_refused_2741(tmp_path):
    done, _ = run_verify_writing(tmp_path, "pin", [".tdd/issue-2741-mutations.md"],
                                 then="git commit -q --allow-empty -m moved\n")

    assert (done.returncode, "modified the repository" in done.stdout) == (2, True), done.stdout + done.stderr


@pytest.mark.process("verify.sh pin run as a real shim over veri/verify.py in a throwaway git repo holding a mutation"
                     " record, around a stub claude that appends to it before answering VERDICT: PASS")
def test_verify_sh_pin_whose_verifier_appends_to_an_existing_mutation_record_takes_the_pass_2741(tmp_path):
    done, record = run_verify_writing(tmp_path, "pin", [".tdd/issue-2741-mutations.md"], recorded="earlier pin\n")

    assert (done.returncode, record.read_text()) == (0, "earlier pin\nwritten\n"), done.stdout + done.stderr


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
