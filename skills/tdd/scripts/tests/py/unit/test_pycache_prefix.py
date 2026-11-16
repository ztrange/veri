"""In-process cases for veri/pycache_prefix.py, the file a veri module's first line runs to set where its bytecode goes.

Each case runs the file with runpy, as a module's first line does, under a sys state of its own: no prefix yet, bytecode
writing on, and `sys.path`, `sys.path_hooks` and `sys.path_importer_cache` copies the case may change."""
import os
import pathlib
import runpy
import stat
import sys

import pytest

VERI = pathlib.Path(__file__).resolve().parents[3] / "veri"


@pytest.fixture
def run_prefix(monkeypatch):
    """Runs pycache_prefix.py as a fresh veri module start would; returns the prefix it set (None when it set none)."""
    monkeypatch.setattr(sys, "pycache_prefix", None)
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    monkeypatch.setattr(sys, "path", [str(VERI)] + sys.path[1:])
    monkeypatch.setattr(sys, "path_hooks", list(sys.path_hooks))
    monkeypatch.setattr(sys, "path_importer_cache", dict(sys.path_importer_cache))

    def run():
        runpy.run_path(str(VERI / "pycache_prefix.py"))
        return sys.pycache_prefix

    return run


def test_3965_an_absent_prefix_is_created_with_mode_0700_and_used(run_prefix, monkeypatch, tmp_path):
    cache = tmp_path / "cache"
    monkeypatch.setenv("VERI_PYCACHE", str(cache))

    used = run_prefix()

    assert (used, cache.is_dir() and stat.S_IMODE(os.lstat(cache).st_mode)) == (str(cache), 0o700)
