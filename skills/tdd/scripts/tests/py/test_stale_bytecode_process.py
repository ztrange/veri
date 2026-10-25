"""Cases for the bytecode a veri/ module's .sh shim runs, which start the real entry point."""
import importlib.util
import marshal
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS

LEDGER = "# Plan for #42\n\n- [ ] collapse non-alphanumerics to a single hyphen\n"
STALE_LEDGER_MODULE = (
    "def read_ledger_stdin():\n    return ''\n"
    "def ledger_steps(text):\n    return []\n"
    "def handed_out(record):\n    return False\n"
)


@pytest.mark.process("next-unchecked.sh run with a stale ledger .pyc planted in veri/__pycache__ and no pycache prefix in its environment")
def test_shim_run_with_a_stale_pyc_planted_beside_the_source_uses_the_current_source_2368(tmp_path):
    source = SCRIPTS / "veri" / "ledger.py"
    planted = source.parent / "__pycache__" / ("ledger.%s.pyc" % sys.implementation.cache_tag)
    stat = source.stat()
    code = compile(STALE_LEDGER_MODULE, str(source), "exec")
    header = (importlib.util.MAGIC_NUMBER + (0).to_bytes(4, "little")
              + (int(stat.st_mtime) & 0xFFFFFFFF).to_bytes(4, "little")
              + (stat.st_size & 0xFFFFFFFF).to_bytes(4, "little"))
    original = planted.read_bytes() if planted.exists() else None
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPYCACHEPREFIX"}
    planted.parent.mkdir(exist_ok=True)
    planted.write_bytes(header + marshal.dumps(code))
    try:
        ran = subprocess.run([str(SCRIPTS / "next-unchecked.sh")], input=LEDGER, env=env,
                             cwd=tmp_path, capture_output=True, text=True)
    finally:
        if original is None:
            planted.unlink(missing_ok=True)
        else:
            planted.write_bytes(original)

    assert (ran.returncode, ran.stdout) == (0, "collapse non-alphanumerics to a single hyphen\n")


@pytest.mark.process("python3 run directly on veri/next_unchecked.py with a stale ledger .pyc planted in veri/__pycache__ and no pycache prefix in its environment")
def test_direct_module_run_with_a_stale_pyc_planted_beside_the_source_uses_the_current_source_2368(tmp_path):
    source = SCRIPTS / "veri" / "ledger.py"
    planted = source.parent / "__pycache__" / ("ledger.%s.pyc" % sys.implementation.cache_tag)
    stat = source.stat()
    code = compile(STALE_LEDGER_MODULE, str(source), "exec")
    header = (importlib.util.MAGIC_NUMBER + (0).to_bytes(4, "little")
              + (int(stat.st_mtime) & 0xFFFFFFFF).to_bytes(4, "little")
              + (stat.st_size & 0xFFFFFFFF).to_bytes(4, "little"))
    original = planted.read_bytes() if planted.exists() else None
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPYCACHEPREFIX"}
    planted.parent.mkdir(exist_ok=True)
    planted.write_bytes(header + marshal.dumps(code))
    try:
        ran = subprocess.run([sys.executable, str(SCRIPTS / "veri" / "next_unchecked.py")], input=LEDGER,
                             env=env, cwd=tmp_path, capture_output=True, text=True)
    finally:
        if original is None:
            planted.unlink(missing_ok=True)
        else:
            planted.write_bytes(original)

    assert (ran.returncode, ran.stdout) == (0, "collapse non-alphanumerics to a single hyphen\n")
