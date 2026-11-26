"""In-process cases for veri/run_verdict.py, the module run-verdict.sh is a shim over."""
import importlib.util
import os
import shutil
import subprocess

import pytest

from conftest import SCRIPTS


def staged_module(scripts):
    """veri/run_verdict.py copied under <scripts>/veri/ and loaded from there, so the scripts
    directory it computes from its own path is <scripts>."""
    (scripts / "veri").mkdir(parents=True)
    copy = scripts / "veri" / "run_verdict.py"
    shutil.copy(SCRIPTS / "veri" / "run_verdict.py", copy)
    spec = importlib.util.spec_from_file_location("staged_run_verdict", copy)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NOISE = "the verifier wrote this to stderr\n"
VERDICT_LINE = "the test pins the criterion and fails for the reason it names\n"
APOSTROPHE = "A background process is killed by the pid recorded when it started, never by that shell's own job spec"


def staged_tree(scripts):
    run_verdict = staged_module(scripts)
    (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    (scripts / "verify.sh").chmod(0o755)
    return run_verdict


def launch(run_verdict, argv, run, monkeypatch, run_cli, fake_processes, answer):
    """run_cli over main, with the exec handed to the faked subprocess boundary and fd 2 put back afterwards."""
    import signal
    calls = fake_processes(answer)
    handed = []

    def exec_over_the_fake(path, args):
        handed.append((path, list(args)))
        raise SystemExit(subprocess.run(args).returncode)

    monkeypatch.setattr(os, "execv", exec_over_the_fake)
    monkeypatch.setattr(signal, "signal", lambda signum, handler: None)
    saved = os.dup(2)
    try:
        result = run_cli(run_verdict, list(argv), cwd=run)
    finally:
        os.dup2(saved, 2)
        os.close(saved)
    return result, handed, calls


def test_cli_exits_2_and_never_1_when_verify_sh_refuses_an_empty_step_title_handed_to_it_unchanged(
        tmp_path, monkeypatch, run_cli, fake_processes):
    scripts = tmp_path / "scripts"
    run_verdict = staged_tree(scripts)
    run = tmp_path / "run"
    run.mkdir()
    verifier = f"{scripts}/verify.sh"
    argv = ["--step", "", "red", "spec.md", "suite.test.sh", "a-target-test-id"]

    result, handed, calls = launch(run_verdict, argv, run, monkeypatch, run_cli, fake_processes,
                                   lambda line, **_: (2, "", ""))

    assert (result, handed, len(calls)) == ((2, "", ""), [(verifier, [verifier, *argv])], 1)


@pytest.mark.process("a real supervise.sh running the real run-verdict.sh, whose real verify.sh refuses --step \"\"")
def test_a_verdict_red_supervision_whose_verify_sh_refused_an_empty_step_records_2_and_exits_2_never_1(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    (run / "spec.md").write_text("# spec\n")
    (run / "suite.test.sh").write_text("# test\n")
    env = {k: v for k, v in os.environ.items() if k == "VERI_VENV" or not k.startswith(("VERI_", "CLAUDE_"))}
    env.update(VERI_STUCK_RETRIES="0", VERI_POLL="0.02")

    done = subprocess.run(
        [str(SCRIPTS / "supervise.sh"), "verdict-red", str(SCRIPTS / "run-verdict.sh"),
         "--step", "", "red", "spec.md", "suite.test.sh", "a-target-test-id"],
        cwd=run, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    exit_file = run / ".tdd" / "verdict-red.exit"
    assert (exit_file.read_text().strip() if exit_file.is_file() else None, done.returncode) == ("2", 2), done.stderr


@pytest.mark.process("run_verdict.py loaded through a real symlink to the skill directory, run from another directory")
def test_cli_run_through_a_symlinked_skill_from_another_directory_acts_on_the_callers_tdd(
        tmp_path, monkeypatch, run_cli, fake_processes):
    skill = tmp_path / "linked-skill"
    staged_tree(skill / "scripts")
    link = tmp_path / "skill-link"
    link.symlink_to(skill)
    spec = importlib.util.spec_from_file_location("linked_run_verdict", link / "scripts" / "veri" / "run_verdict.py")
    run_verdict = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_verdict)
    elsewhere = tmp_path / "elsewhere"
    (elsewhere / ".tdd").mkdir(parents=True)
    (elsewhere / ".tdd" / "verify-red.reason").write_text("REJECT: the previous step's reason\n")
    (elsewhere / ".tdd" / "verify-red.stderr").write_text("an earlier verifier wrote this to stderr\n")
    verifier = f"{link}/scripts/verify.sh"
    argv = ["--step", APOSTROPHE, "red", "spec.md", "suite.test.sh", "a-target-test-id"]

    def verify(line, **_):
        os.write(2, NOISE.encode())
        os.write(1, VERDICT_LINE.encode())
        return 0, "", ""

    result, handed, _ = launch(run_verdict, argv, elsewhere, monkeypatch, run_cli, fake_processes, verify)

    assert (result, handed, (elsewhere / ".tdd" / "verify-red.reason").read_text(),
            (elsewhere / ".tdd" / "verify-red.stderr").read_text()) == (
        (0, VERDICT_LINE, ""), [(verifier, [verifier, *argv])], "",
        "an earlier verifier wrote this to stderr\n" + NOISE)
