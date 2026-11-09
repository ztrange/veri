"""Cases for the emitted-text cksum pins that run a real shell."""
import importlib.util
import os
import shutil
import subprocess

import pytest

from conftest import SCRIPTS

UNIT = SCRIPTS / "tests" / "py" / "unit" / "test_emitted_text.py"


@pytest.mark.process("bash running the reproducing command a mismatched emitted-text pin prints")
def test_3368_reproducing_command_of_a_mismatched_pin_prints_the_cksum_the_test_computes(monkeypatch, run_cli):
    spec = importlib.util.spec_from_file_location("emitted_text_pins_under_test", UNIT)
    pins = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pins)
    monkeypatch.setattr(pins, "USAGE", [("1 1", "tick-ledger.sh", [])])

    with pytest.raises(AssertionError) as failure:
        pins.test_usage_output_on_a_missing_argument_is_unchanged(run_cli)

    message = "\n".join(failure.traceback[-1].frame.f_locals["problems"])
    command = [l.split("reproduce:", 1)[1].strip() for l in message.splitlines() if "reproduce:" in l][0]
    computed = pins.cksum(pins.emitted(run_cli, "tick-ledger.sh", []).encode("utf-8", "surrogateescape"))
    ran = subprocess.run(["bash", "-c", command], cwd=SCRIPTS.parents[2], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    assert ran.stdout.strip() == computed


def _interleaving_pin_reproduce_command(monkeypatch, run_cli, tmp_path):
    stub = tmp_path / "interleave.sh"
    stub.write_text("#!/bin/sh\necho out1\necho err1 >&2\necho out2\nexit 2\n")
    stub.chmod(0o755)
    name = os.path.relpath(stub, SCRIPTS)
    spec = importlib.util.spec_from_file_location("emitted_text_pins_under_test", UNIT)
    pins = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pins)
    monkeypatch.setattr(pins, "USAGE", [("1 1", name, [])])
    monkeypatch.setattr(pins, "emitted", lambda run_cli, script, argv: "exit 2\nout1\nout2\nerr1\n")

    with pytest.raises(AssertionError) as failure:
        pins.test_usage_output_on_a_missing_argument_is_unchanged(run_cli)

    message = "\n".join(failure.traceback[-1].frame.f_locals["problems"])
    command = [l.split("reproduce:", 1)[1].strip() for l in message.splitlines() if "reproduce:" in l][0]
    return pins, command


@pytest.mark.process("bash running the reproducing command a mismatched pin prints, for a script interleaving both streams")
def test_3408_reproducing_command_for_a_script_interleaving_stdout_and_stderr_prints_the_pin_cksum(monkeypatch, run_cli, tmp_path):
    pins, command = _interleaving_pin_reproduce_command(monkeypatch, run_cli, tmp_path)
    computed = pins.cksum(b"exit 2\nout1\nout2\nerr1\n")
    ran = subprocess.run(["bash", "-c", command], cwd=SCRIPTS.parents[2], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    assert ran.stdout.strip() == computed


@pytest.mark.process("bash running the reproducing command a mismatched pin prints, with a scratch TMPDIR")
def test_3408_reproducing_command_prints_the_pin_cksum_and_leaves_no_temp_files_behind(monkeypatch, run_cli, tmp_path):
    pins, command = _interleaving_pin_reproduce_command(monkeypatch, run_cli, tmp_path)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    shims = tmp_path / "shims"
    shims.mkdir()
    shim = shims / "mktemp"
    shim.write_text('#!/bin/sh\nexec %s "%s/f.XXXXXX"\n' % (shutil.which("mktemp"), scratch))
    shim.chmod(0o755)
    ran = subprocess.run(["bash", "-c", command], cwd=SCRIPTS.parents[2], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, env={**os.environ, "PATH": "%s:%s" % (shims, os.environ["PATH"])})
    assert (ran.stdout.strip(), sorted(p.name for p in scratch.iterdir())) == (pins.cksum(b"exit 2\nout1\nout2\nerr1\n"), [])


@pytest.mark.process("bash running the reproducing command a mismatched pin prints, for a script that records its argv")
def test_3408_reproducing_command_passes_every_argument_to_the_script_verbatim(monkeypatch, run_cli, tmp_path):
    argv = ["a b", "it's", 'say "hi"', "$HOME", "`id`", "x;y", "*", ""]
    record = tmp_path / "argv.bin"
    stub = tmp_path / "echo-argv.sh"
    stub.write_text('#!/bin/sh\nprintf \'%%s\\0\' "$@" > "%s"\nexit 2\n' % record)
    stub.chmod(0o755)
    name = os.path.relpath(stub, SCRIPTS)
    spec = importlib.util.spec_from_file_location("emitted_text_pins_under_test", UNIT)
    pins = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pins)
    monkeypatch.setattr(pins, "USAGE", [("1 1", name, argv)])
    monkeypatch.setattr(pins, "emitted", lambda run_cli, script, argv: "exit 2\n")

    with pytest.raises(AssertionError) as failure:
        pins.test_usage_output_on_a_missing_argument_is_unchanged(run_cli)

    message = "\n".join(failure.traceback[-1].frame.f_locals["problems"])
    command = [l.split("reproduce:", 1)[1].strip() for l in message.splitlines() if "reproduce:" in l][0]
    subprocess.run(["bash", "-c", command], cwd=SCRIPTS.parents[2], stdin=subprocess.DEVNULL,
                   capture_output=True, text=True)
    assert record.read_bytes().split(b"\0")[:-1] == [a.encode() for a in argv]
