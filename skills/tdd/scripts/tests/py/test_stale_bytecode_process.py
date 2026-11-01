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


@pytest.mark.process("python3 run directly on veri/next_unchecked.py with a stale tunables .pyc planted in veri/__pycache__ and no pycache prefix in its environment")
def test_direct_module_run_with_a_stale_tunables_pyc_planted_beside_the_source_uses_the_current_source_2405(tmp_path):
    source = SCRIPTS / "veri" / "tunables.py"
    planted = source.parent / "__pycache__" / ("tunables.%s.pyc" % sys.implementation.cache_tag)
    stat = source.stat()
    code = compile("def read(name, default=None):\n    raise RuntimeError('stale tunables')\n", str(source), "exec")
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


@pytest.mark.process("python3 run directly on every runnable module of a copy of veri/ with VERI_PYCACHE under tmp_path, an empty stdin and no PYTHONPYCACHEPREFIX in its environment")
@pytest.mark.timeout(120)
@pytest.mark.tree_audit("a copy of veri/ made into tmp_path, swept for .pyc files after each module's run")
def test_every_directly_runnable_module_keeps_its_bytecode_out_of_the_tree_2405(tmp_path):
    veri = tmp_path / "veri"
    shutil.copytree(SCRIPTS / "veri", veri, ignore=shutil.ignore_patterns("__pycache__"))
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")}
    env.update(VERI_PYCACHE=str(tmp_path / "pycache"), PATH="/nonexistent", HOME=str(tmp_path))
    work = tmp_path / "work"
    work.mkdir()
    runnable = sorted(p for p in veri.glob("*.py") if "__main__" in p.read_text())
    leaked = {}
    for module in runnable:
        try:
            subprocess.run([sys.executable, str(module)], input="", env=env, cwd=work,
                           capture_output=True, text=True, timeout=3)
        except subprocess.TimeoutExpired:
            pass
        found = sorted(p.name for p in veri.rglob("*.pyc"))
        if found:
            leaked[module.name] = found
        shutil.rmtree(veri / "__pycache__", ignore_errors=True)

    assert runnable != []
    assert leaked == {}


@pytest.mark.tree_audit("copies the scripts tree to tmp_path")
@pytest.mark.process("next-unchecked.sh run from a copy of the scripts tree with a stale ledger .pyc planted under the shared pycache prefix and no PYTHONPYCACHEPREFIX in its environment")
def test_shim_run_with_a_stale_pyc_planted_under_the_shared_prefix_reads_the_current_source_2439(tmp_path):
    root = tmp_path.resolve()
    scripts = root / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    cache = root / "pycache"
    source = scripts / "veri" / "ledger.py"
    stat = source.stat()
    code = compile(STALE_LEDGER_MODULE, str(source), "exec")
    header = (importlib.util.MAGIC_NUMBER + (0).to_bytes(4, "little")
              + (int(stat.st_mtime) & 0xFFFFFFFF).to_bytes(4, "little")
              + (stat.st_size & 0xFFFFFFFF).to_bytes(4, "little"))
    planted = cache / str(source.parent).lstrip(os.sep) / ("ledger.%s.pyc" % sys.implementation.cache_tag)
    planted.parent.mkdir(parents=True)
    planted.write_bytes(header + marshal.dumps(code))
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")}
    env["VERI_PYCACHE"] = str(cache)

    ran = subprocess.run([str(scripts / "next-unchecked.sh")], input=LEDGER, env=env,
                         cwd=root, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "collapse non-alphanumerics to a single hyphen\n")


@pytest.mark.tree_audit("copies the scripts tree to tmp_path")
@pytest.mark.process("next-unchecked.sh run from a copy of the scripts tree with a stale ledger .pyc planted under a PYTHONPYCACHEPREFIX the caller exported")
def test_shim_run_with_a_stale_pyc_planted_under_a_caller_exported_prefix_reads_the_current_source_2439(tmp_path):
    root = tmp_path.resolve()
    scripts = root / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    cache = root / "callers-pycache"
    source = scripts / "veri" / "ledger.py"
    stat = source.stat()
    code = compile(STALE_LEDGER_MODULE, str(source), "exec")
    header = (importlib.util.MAGIC_NUMBER + (0).to_bytes(4, "little")
              + (int(stat.st_mtime) & 0xFFFFFFFF).to_bytes(4, "little")
              + (stat.st_size & 0xFFFFFFFF).to_bytes(4, "little"))
    planted = cache / str(source.parent).lstrip(os.sep) / ("ledger.%s.pyc" % sys.implementation.cache_tag)
    planted.parent.mkdir(parents=True)
    planted.write_bytes(header + marshal.dumps(code))
    env = {k: v for k, v in os.environ.items()
           if k not in ("VERI_PYCACHE", "PYTHONDONTWRITEBYTECODE")}
    env["PYTHONPYCACHEPREFIX"] = str(cache)

    ran = subprocess.run([str(scripts / "next-unchecked.sh")], input=LEDGER, env=env,
                         cwd=root, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "collapse non-alphanumerics to a single hyphen\n")


@pytest.mark.tree_audit("copies the scripts tree to tmp_path")
@pytest.mark.process("a shim over a probe module, run from a copy of the scripts tree, with a stale probe helper .pyc planted beside its source")
def test_shim_run_loads_the_standard_library_from_its_own_bytecode_and_veri_modules_from_source(tmp_path):
    root = tmp_path.resolve()
    scripts = root / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    helper = scripts / "veri" / "probe_helper.py"
    helper.write_text("ANSWER = 'current'\n")
    stat = helper.stat()
    header = (importlib.util.MAGIC_NUMBER + (0).to_bytes(4, "little")
              + (int(stat.st_mtime) & 0xFFFFFFFF).to_bytes(4, "little")
              + (stat.st_size & 0xFFFFFFFF).to_bytes(4, "little"))
    planted = helper.parent / "__pycache__" / ("probe_helper.%s.pyc" % sys.implementation.cache_tag)
    planted.parent.mkdir()
    planted.write_bytes(header + marshal.dumps(compile("ANSWER = 'stale'\n", str(helper), "exec")))
    (scripts / "veri" / "probe.py").write_text(
        'if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")\n'
        "import json\nimport os\nimport probe_helper\n"
        "print(probe_helper.ANSWER)\n"
        "print(os.path.dirname(json.__spec__.cached) == os.path.join(os.path.dirname(json.__file__), '__pycache__'))\n")
    shim = scripts / "probe.sh"
    shim.write_text('#!/bin/sh\n. "$(dirname "$0")/lib/shim-python.sh"\nexec "$py" "$(dirname "$0")/veri/probe.py"\n')
    shim.chmod(0o755)
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")}
    env["VERI_PYCACHE"] = str(root / "pycache")

    ran = subprocess.run([str(shim)], stdin=subprocess.DEVNULL, env=env, cwd=root, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "current\nTrue\n"), ran.stderr


RUN_PYTEST_LEG_AS_MAIN = (
    "import runpy, sys\n"
    "sys.argv = [sys.argv[1], '--help']\n"
    "sys.path.insert(0, __import__('os').path.dirname(sys.argv[0]))\n"
    "try:\n"
    "    runpy.run_path(sys.argv[0], run_name='__main__')\n"
    "except BaseException:\n"
    "    pass\n"
    "print(sys.modules['launch_floor'].__cached__)\n"
)


@pytest.mark.process("python3 -c running pytest_leg.py --help as __main__ from a copy of veri/ in a copy of veri/ with VERI_PYCACHE under tmp_path and no PYTHONPYCACHEPREFIX in its environment")
@pytest.mark.tree_audit("a copy of veri/ made into tmp_path, swept for .pyc files after the run")
def test_direct_pytest_leg_run_writes_its_bytecode_under_veri_pycache_not_the_tree_2442(tmp_path):
    veri = tmp_path / "veri"
    shutil.copytree(SCRIPTS / "veri", veri, ignore=shutil.ignore_patterns("__pycache__"))
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")}
    env.update(VERI_PYCACHE=str(tmp_path / "pycache"), PATH="/nonexistent", HOME=str(tmp_path))

    ran = subprocess.run([sys.executable, "-c", RUN_PYTEST_LEG_AS_MAIN, str(veri / "pytest_leg.py")], input="", env=env,
                         cwd=tmp_path, capture_output=True, text=True, timeout=30)

    in_tree = sorted(p.name for p in veri.rglob("*.pyc"))
    cached = ran.stdout.strip().splitlines()[-1:] if ran.stdout.strip() else []
    assert (in_tree, [c.startswith(str(tmp_path / "pycache")) for c in cached]) == ([], [True])
