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


def cache_with_mode(tmp_path, mode):
    cache = tmp_path / "cache"
    cache.mkdir()
    cache.chmod(mode)
    return cache


def test_3965_a_group_writable_veri_pycache_directory_is_refused_and_no_prefix_set(run_prefix, monkeypatch, tmp_path):
    monkeypatch.setenv("VERI_PYCACHE", str(cache_with_mode(tmp_path, 0o770)))

    assert run_prefix() is None


def test_3965_an_other_writable_veri_pycache_directory_is_refused_and_no_prefix_set(run_prefix, monkeypatch, tmp_path):
    monkeypatch.setenv("VERI_PYCACHE", str(cache_with_mode(tmp_path, 0o707)))

    assert run_prefix() is None


def test_3965_a_veri_pycache_path_that_is_a_symlink_even_to_a_closed_directory_of_the_users_own_is_refused(run_prefix, monkeypatch, tmp_path):
    link = tmp_path / "link"
    link.symlink_to(cache_with_mode(tmp_path, 0o700))
    monkeypatch.setenv("VERI_PYCACHE", str(link))

    assert run_prefix() is None


def test_3965_a_symlink_named_with_a_trailing_slash_is_still_refused_as_a_symlink(run_prefix, monkeypatch, tmp_path, capfd):
    link = tmp_path / "link"
    link.symlink_to(cache_with_mode(tmp_path, 0o700))
    monkeypatch.setenv("VERI_PYCACHE", str(link) + "//")

    assert (run_prefix(), capfd.readouterr().err) == (
        None, "veri: not using the bytecode cache %s: it is a symlink; compiling veri's modules from source\n" % link)


def test_3965_a_closed_veri_pycache_directory_owned_by_another_user_is_refused(run_prefix, monkeypatch, tmp_path):
    cache = cache_with_mode(tmp_path, 0o700)
    monkeypatch.setenv("VERI_PYCACHE", str(cache))
    monkeypatch.setattr(os, "getuid", lambda: os.lstat(cache).st_uid + 1)

    assert run_prefix() is None


def test_3965_a_group_writable_default_prefix_under_tmpdir_is_refused_and_no_prefix_set(run_prefix, monkeypatch, tmp_path):
    default = tmp_path / ("veri-pycache-%d" % os.getuid())
    default.mkdir()
    default.chmod(0o770)
    monkeypatch.delenv("VERI_PYCACHE", raising=False)
    monkeypatch.setenv("TMPDIR", str(tmp_path))

    assert run_prefix() is None


def test_3965_a_veri_pycache_path_that_is_a_closed_regular_file_of_the_users_own_is_refused(run_prefix, monkeypatch, tmp_path):
    cache = tmp_path / "cache"
    cache.write_text("")
    cache.chmod(0o600)
    monkeypatch.setenv("VERI_PYCACHE", str(cache))

    assert run_prefix() is None


def test_3965_a_veri_pycache_path_that_cannot_be_created_is_refused_naming_why(run_prefix, monkeypatch, tmp_path, capfd):
    (tmp_path / "file").write_text("")
    cache = tmp_path / "file" / "cache"
    monkeypatch.setenv("VERI_PYCACHE", str(cache))

    used = run_prefix()

    assert (used, capfd.readouterr().err.startswith("veri: not using the bytecode cache %s: it cannot be created or read: " % cache)) == (None, True)


def cache_under_parent_with_mode(tmp_path, mode):
    parent = tmp_path / "parent"
    parent.mkdir()
    cache = parent / "cache"
    cache.mkdir()
    cache.chmod(0o700)
    parent.chmod(mode)
    return cache


def test_3965_a_closed_prefix_whose_parent_others_can_write_without_the_sticky_bit_is_refused(run_prefix, monkeypatch, tmp_path, capfd):
    cache = cache_under_parent_with_mode(tmp_path, 0o777)
    monkeypatch.setenv("VERI_PYCACHE", str(cache))

    assert (run_prefix(), capfd.readouterr().err) == (
        None, "veri: not using the bytecode cache %s: its parent is group- or other-writable without the sticky bit; "
              "compiling veri's modules from source\n" % cache)


def test_3965_a_refused_prefix_leaves_the_run_writing_no_bytecode_anywhere(run_prefix, monkeypatch, tmp_path):
    monkeypatch.setenv("VERI_PYCACHE", str(cache_with_mode(tmp_path, 0o770)))

    assert (run_prefix(), sys.dont_write_bytecode) == (None, True)


def test_3965_a_closed_prefix_whose_parent_is_writable_by_all_with_the_sticky_bit_as_tmp_is_used(run_prefix, monkeypatch, tmp_path):
    cache = cache_under_parent_with_mode(tmp_path, 0o1777)
    monkeypatch.setenv("VERI_PYCACHE", str(cache))

    assert run_prefix() == str(cache)


def test_3965_a_group_writable_prefix_the_caller_exported_as_pythonpycacheprefix_is_refused_and_its_planted_pyc_never_runs(
        run_prefix, monkeypatch, tmp_path, capfd):
    import importlib
    import importlib.util
    import py_compile

    modules = tmp_path / "modules"
    modules.mkdir()
    victim, poison = modules / "victim_3965.py", tmp_path / "poison.py"
    victim.write_text("X = 'clean'\n")
    poison.write_text("X = 'dirty'\n")
    os.utime(poison, ns=(os.stat(victim).st_atime_ns, os.stat(victim).st_mtime_ns))
    prefix = cache_with_mode(tmp_path, 0o770)
    monkeypatch.setattr(sys, "path", [str(modules)] + sys.path[1:])
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    py_compile.compile(str(poison), cfile=importlib.util.cache_from_source(str(victim)), doraise=True)
    monkeypatch.delitem(sys.modules, "victim_3965", raising=False)

    run_prefix()
    importlib.invalidate_caches()
    loaded = importlib.import_module("victim_3965")
    monkeypatch.delitem(sys.modules, "victim_3965")

    assert (sys.pycache_prefix, loaded.X, capfd.readouterr().err) == (
        None, "clean", "veri: not using the bytecode cache %s: it is group-writable; compiling veri's modules from source\n" % prefix)


def test_3965_on_a_refusal_veri_modules_compile_from_source_and_one_stderr_line_names_the_path_and_why(run_prefix, monkeypatch, tmp_path, capfd):
    cache = cache_with_mode(tmp_path, 0o770)
    monkeypatch.setenv("VERI_PYCACHE", str(cache))

    used = run_prefix()
    loader = sys.path_hooks[0](str(VERI)).find_spec("tunables").loader

    assert (used, type(loader).__name__, capfd.readouterr().err) == (
        None, "FromSource", "veri: not using the bytecode cache %s: it is group-writable; compiling veri's modules from source\n" % cache)
