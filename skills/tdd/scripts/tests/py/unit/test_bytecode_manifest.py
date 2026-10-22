"""In-process cases for the pytest leg's bytecode-cache manifest (sources.json under the PYTHONPYCACHEPREFIX)."""
import hashlib
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


def test_the_manifest_records_only_plain_pycs_and_the_check_drops_pytest_rewritten_and_optimised_ones(tmp_path, monkeypatch):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    src = tmp_path / "src"
    src.mkdir()
    plain_source = src / "mod.py"
    plain_source.write_text("X = 1\n")
    test_source = src / "test_mod.py"
    test_source.write_text("def test_x(): pass\n")
    cache = prefix / str(src).lstrip("/")
    cache.mkdir(parents=True)
    plain = cache / "mod.cpython-312.pyc"
    rewritten = cache / "mod.cpython-312-pytest-8.3.4.pyc"
    optimised = cache / "mod.cpython-312.opt-1.pyc"
    only_rewritten = cache / "test_mod.cpython-312-pytest-8.3.4.pyc"
    for pyc in (plain, rewritten, optimised, only_rewritten):
        pyc.write_bytes(b"bytecode")
    digest = hashlib.sha256(plain_source.read_bytes()).hexdigest()
    manifest = prefix / "sources.json"
    manifest.write_text(json.dumps({str(plain_source): digest}))
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))

    pytest_leg.drop_stale_bytecode()

    assert plain.exists(), "a plain .pyc of an unchanged listed source was dropped"
    assert not rewritten.exists(), "a pytest-rewritten .pyc was kept"
    assert not optimised.exists(), "an optimised .opt-N.pyc was kept"
    assert json.loads(manifest.read_text()) == {str(plain_source): digest}
    only_rewritten.write_bytes(b"bytecode")

    pytest_leg.drop_stale_bytecode(after_run=True)

    assert json.loads(manifest.read_text()) == {str(plain_source): digest}, "the record lists a source for a pytest-rewritten .pyc"
