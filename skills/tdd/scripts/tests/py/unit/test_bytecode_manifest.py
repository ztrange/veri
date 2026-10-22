"""In-process cases for the pytest leg's bytecode-cache manifest (sources.json under the PYTHONPYCACHEPREFIX)."""
import importlib
import json
import sys

import pytest


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


@pytest.mark.parametrize("unreadable", ["", '{"/src/mod.py": "9f86d0', "[]", "not json at all"])
def test_every_cached_pyc_is_dropped_when_the_manifest_cannot_be_read_as_a_json_object(tmp_path, monkeypatch, unreadable):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    source = tmp_path / "src" / "mod.py"
    source.parent.mkdir()
    source.write_text("X = 1\n")
    pyc = prefix / str(source.parent).lstrip("/") / "mod.cpython-312.pyc"
    pyc.parent.mkdir(parents=True)
    pyc.write_bytes(b"stale bytecode")
    (prefix / "sources.json").write_text(unreadable)
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))

    pytest_leg.drop_stale_bytecode()

    assert not pyc.exists(), "a .pyc was kept under a manifest that reads %r" % unreadable


def test_a_pyc_another_run_already_removed_is_not_an_error_when_the_check_drops_it(tmp_path, monkeypatch):
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
    real_remove = pytest_leg.os.remove

    def removed_by_the_other_run(path):
        real_remove(path)
        raise FileNotFoundError(path)

    monkeypatch.setattr(pytest_leg.os, "remove", removed_by_the_other_run)

    pytest_leg.drop_stale_bytecode()

    assert not pyc.exists()
