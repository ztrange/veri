"""In-process cases for veri/run_verdict.py, the module run-verdict.sh is a shim over."""
import importlib.util
import os
import pathlib
import shutil
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


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


@pytest.mark.parametrize("verifier", ["absent", "not executable"])
def test_main_without_an_executable_verify_sh_returns_2_names_it_and_never_execs(
        verifier, tmp_path, monkeypatch, capfd):
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    if verifier == "not executable":
        (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "verify-red.reason").write_text("an earlier step's reason\n")
    monkeypatch.chdir(run)
    calls = []
    monkeypatch.setattr(os, "execv", lambda path, args: calls.append((path, list(args))))

    code = run_verdict.main(["--step", "t", "red", "spec.md", "tests/x.test.sh", "case"])

    captured = capfd.readouterr()
    assert (code, calls, captured.err) == (
        2, [],
        f"run-verdict.sh: cannot start the verifier: {scripts}/verify.sh is missing or not executable\n")
    assert (run / ".tdd" / "verify-red.reason").read_text() == "an earlier step's reason\n"
