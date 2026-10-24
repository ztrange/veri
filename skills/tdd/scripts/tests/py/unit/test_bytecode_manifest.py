"""The bytecode cache functions of veri/pytest_leg.py, called in-process over a cache prefix and sources inside tmp_path."""
import importlib
import importlib.util
import json
import os
import py_compile
import sys
import time


def test_the_check_before_a_run_drops_pytest_rewritten_and_optimised_pycs_and_leaves_a_recorded_plain_module_pyc_2054(tmp_path, monkeypatch):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    sources = tmp_path / "src"
    sources.mkdir()
    helper = sources / "helper.py"
    helper.write_text("VALUE = 1\n")
    test_helper = sources / "test_helper.py"
    test_helper.write_text("def test_value():\n    pass\n")
    an_hour_ago = time.time() - 3600
    for source in (helper, test_helper):
        os.utime(source, (an_hour_ago, an_hour_ago))
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    plain = importlib.util.cache_from_source(str(helper))
    optimised = importlib.util.cache_from_source(str(helper), optimization=1)
    rewritten = importlib.util.cache_from_source(str(test_helper))[:-len(".pyc")] + "-pytest-8.3.4.pyc"

    run = pytest_leg.check_bytecode_cache(str(prefix))
    a_minute_on = time.time() + 60
    for cfile in (plain, optimised, rewritten):
        py_compile.compile(str(helper if cfile != rewritten else test_helper), cfile=cfile, doraise=True)
        os.utime(cfile, (a_minute_on, a_minute_on))
    pytest_leg.record_bytecode_cache(str(prefix), run)
    pytest_leg.check_bytecode_cache(str(prefix))

    assert sorted(os.listdir(os.path.dirname(plain))) == [os.path.basename(plain)]


def test_the_check_treats_a_pyc_another_run_already_removed_as_dropped_and_carries_on_2054(tmp_path, monkeypatch):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    source = tmp_path / "test_gone.py"
    source.write_text("def test_value():\n    pass\n")
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    rewritten = importlib.util.cache_from_source(str(source))[:-len(".pyc")] + "-pytest-8.3.4.pyc"
    os.makedirs(os.path.dirname(rewritten))
    py_compile.compile(str(source), cfile=rewritten, doraise=True)
    removed = []
    real_remove = os.remove

    def remove_then_lose_the_race(path):
        real_remove(path)
        removed.append(path)
        raise FileNotFoundError(path)

    monkeypatch.setattr(os, "remove", remove_then_lose_the_race)

    run = pytest_leg.check_bytecode_cache(str(prefix))

    assert (removed, os.path.exists(rewritten), sorted(run)) == ([rewritten], False, ["snapshot", "start"])


def test_the_check_drops_a_cached_plain_pyc_whose_source_the_manifest_does_not_list_2054(tmp_path, monkeypatch):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    source = tmp_path / "unlisted.py"
    source.write_text("VALUE = 1\n")
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    plain = importlib.util.cache_from_source(str(source))
    os.makedirs(os.path.dirname(plain))
    py_compile.compile(str(source), cfile=plain, doraise=True)

    pytest_leg.check_bytecode_cache(str(prefix))

    assert os.path.exists(plain) is False


def test_the_check_drops_every_cached_pyc_when_the_manifest_is_empty_truncated_or_not_a_json_object_2054(tmp_path, monkeypatch):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    source = tmp_path / "recorded.py"
    source.write_text("VALUE = 1\n")
    an_hour_ago = time.time() - 3600
    os.utime(source, (an_hour_ago, an_hour_ago))
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    plain = importlib.util.cache_from_source(str(source))
    os.makedirs(os.path.dirname(plain))
    manifest = prefix / "veri-manifest.json"
    survivors = {}
    for broken in ("", '{"' + plain + '": "ab', "[]", "not json at all"):
        run = pytest_leg.check_bytecode_cache(str(prefix))
        py_compile.compile(str(source), cfile=plain, doraise=True)
        a_minute_on = time.time() + 60
        os.utime(plain, (a_minute_on, a_minute_on))
        pytest_leg.record_bytecode_cache(str(prefix), run)
        assert plain in manifest.read_text()
        manifest.write_text(broken)

        pytest_leg.check_bytecode_cache(str(prefix))

        survivors[broken] = os.path.exists(plain)

    assert survivors == {"": False, '{"' + plain + '": "ab': False, "[]": False, "not json at all": False}


def test_the_record_after_a_run_lists_a_plain_module_pyc_this_run_compiled_and_never_a_pytest_rewritten_or_optimised_one_2054(tmp_path, monkeypatch):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    helper = tmp_path / "helper.py"
    helper.write_text("VALUE = 1\n")
    an_hour_ago = time.time() - 3600
    os.utime(helper, (an_hour_ago, an_hour_ago))
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    plain = importlib.util.cache_from_source(str(helper))
    optimised = importlib.util.cache_from_source(str(helper), optimization=2)
    rewritten = plain[:-len(".pyc")] + "-pytest-8.3.4.pyc"

    run = pytest_leg.check_bytecode_cache(str(prefix))
    a_minute_on = time.time() + 60
    for cfile in (plain, optimised, rewritten):
        py_compile.compile(str(helper), cfile=cfile, doraise=True)
        os.utime(cfile, (a_minute_on, a_minute_on))
    pytest_leg.record_bytecode_cache(str(prefix), run)

    assert sorted(pytest_leg.read_manifest(str(prefix))) == [plain]


def test_the_record_after_a_run_does_not_newly_record_a_pyc_present_in_the_snapshot_and_unchanged_since_2054(tmp_path, monkeypatch):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    helper = tmp_path / "helper.py"
    helper.write_text("VALUE = 1\n")
    an_hour_ago = time.time() - 3600
    os.utime(helper, (an_hour_ago, an_hour_ago))
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    plain = importlib.util.cache_from_source(str(helper))
    py_compile.compile(str(helper), cfile=plain, doraise=True)
    first_digest = pytest_leg.source_digest(plain)
    (prefix / pytest_leg.MANIFEST).write_text(json.dumps({plain: first_digest}))
    a_minute_on = time.time() + 60
    os.utime(plain, (a_minute_on, a_minute_on))

    run = pytest_leg.check_bytecode_cache(str(prefix))
    helper.write_text("VALUE = 2\n")
    os.utime(helper, (an_hour_ago, an_hour_ago))
    pytest_leg.record_bytecode_cache(str(prefix), run)

    assert pytest_leg.read_manifest(str(prefix)) == {plain: first_digest}


def test_the_record_after_a_run_does_not_list_a_pyc_planted_after_the_check_with_its_sources_mtime_and_size_2054(tmp_path, monkeypatch):
    pytest_leg = importlib.import_module("veri.pytest_leg")
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    helper = tmp_path / "helper.py"
    helper.write_text("VALUE = 1\n")
    an_hour_ago = time.time() - 3600
    os.utime(helper, (an_hour_ago, an_hour_ago))
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    plain = importlib.util.cache_from_source(str(helper))

    run = pytest_leg.check_bytecode_cache(str(prefix))
    py_compile.compile(str(helper), cfile=plain, doraise=True)
    os.utime(plain, (an_hour_ago, an_hour_ago))
    pytest_leg.record_bytecode_cache(str(prefix), run)

    assert pytest_leg.read_manifest(str(prefix)) == {}
