"""The bytecode cache functions of veri/pytest_leg.py, called in-process over a cache prefix and sources inside tmp_path."""
import importlib
import importlib.util
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
