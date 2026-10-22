"""In-process cases for the pytest leg's bytecode-cache manifest (sources.json under the PYTHONPYCACHEPREFIX)."""
import importlib
import json
import sys


def test_a_cached_pyc_whose_source_the_manifest_does_not_list_is_dropped_before_the_run(tmp_path, monkeypatch):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    source = tmp_path / "src" / "mod.py"
    source.parent.mkdir()
    source.write_text("X = 1\n")
    pyc = prefix / str(source.parent).lstrip("/") / "mod.cpython-312.pyc"
    pyc.parent.mkdir(parents=True)
    pyc.write_bytes(b"stale bytecode")
    (prefix / "sources.json").write_text(json.dumps({}))
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))

    pytest_leg.drop_stale_bytecode()

    assert not pyc.exists(), "a .pyc whose source the manifest does not list was kept"
