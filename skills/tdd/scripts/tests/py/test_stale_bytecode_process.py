"""Cases for the bytecode a veri/ module's .sh shim runs, which start the real entry point."""
import importlib.util
import marshal
import os
import shutil
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


@pytest.mark.tree_audit("copies the scripts tree to tmp_path")
@pytest.mark.process("next-unchecked.sh run twice from a copy of the scripts tree around a same-second, same-size mutation of veri/ledger.py, with the default shared pycache prefix under TMPDIR")
def test_shim_run_outside_make_after_a_same_second_mutation_reads_the_current_source_2406(tmp_path):
    scripts = tmp_path / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTHONPYCACHEPREFIX", "VERI_PYCACHE", "PYTHONDONTWRITEBYTECODE")}
    env["TMPDIR"] = str(tmpdir)

    def run():
        return subprocess.run([str(scripts / "next-unchecked.sh")], input=LEDGER, env=env,
                              cwd=tmp_path, capture_output=True, text=True)

    first = run()
    source = scripts / "veri" / "ledger.py"
    stat = source.stat()
    text = source.read_text()
    mutated = text.replace('record[1] == "open"', 'record[1] == "oper"')
    assert len(mutated) == len(text) and mutated != text
    source.write_text(mutated)
    os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    second = run()

    assert (first.returncode, first.stdout) == (0, "collapse non-alphanumerics to a single hyphen\n")
    assert (second.returncode, second.stdout) == (3, "")


@pytest.mark.process("python3 run directly on a copy of veri/next_unchecked.py with VERI_PYCACHE under tmp_path and no PYTHONPYCACHEPREFIX in its environment")
@pytest.mark.tree_audit("a copy of veri/ made into tmp_path")
def test_direct_module_run_writes_its_bytecode_under_veri_pycache_not_beside_the_source_2405(tmp_path):
    veri = tmp_path / "veri"
    shutil.copytree(SCRIPTS / "veri", veri, ignore=shutil.ignore_patterns("__pycache__"))
    cache = tmp_path / "pycache"
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPYCACHEPREFIX"}
    env["VERI_PYCACHE"] = str(cache)
    ran = subprocess.run([sys.executable, str(veri / "next_unchecked.py")], input=LEDGER,
                         env=env, cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert list(cache.rglob("ledger.*.pyc")) != []
    assert list((veri / "__pycache__").glob("ledger.*.pyc")) == []
