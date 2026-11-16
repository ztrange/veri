"""Sets where this run reads and writes bytecode; a veri module's first line runs it before any veri import."""
import os
import stat
import sys


def refusal(prefix):
    """Why <prefix> may not be this user's bytecode cache, or None when it may; an absent one is created with mode 0700."""
    try:
        os.makedirs(prefix, 0o700)
    except FileExistsError:
        pass
    mode = os.lstat(prefix).st_mode
    if stat.S_ISLNK(mode):
        return "it is a symlink"
    if mode & stat.S_IWGRP:
        return "it is group-writable"
    if mode & stat.S_IWOTH:
        return "it is other-writable"
    return None


if sys.pycache_prefix is None:
    if sys.dont_write_bytecode:
        # A shim run: no manifest vouches for veri's bytecode (#2368, #2439), so its modules always
        # compile from source, while the standard library keeps its own .pyc files. A prefix would
        # hide those too, and recompile every import on every start.
        from importlib.machinery import SOURCE_SUFFIXES, FileFinder, SourceFileLoader

        class FromSource(SourceFileLoader):
            def path_stats(self, path):
                raise OSError("a shim run never reads veri's bytecode")

        def veri_finder(path, modules=sys.path[0], finder=FileFinder.path_hook((FromSource, SOURCE_SUFFIXES))):
            if path != modules:
                raise ImportError("not veri's directory")
            return finder(path)

        sys.path_hooks.insert(0, veri_finder)
        sys.path_importer_cache.pop(sys.path[0], None)
    else:
        prefix = os.path.join(os.environ.get("TMPDIR") or "/tmp", "veri-pycache-%d" % os.getuid())
        sys.dont_write_bytecode = True  # tunables' own bytecode waits until the prefix is proved this user's
        import tunables
        sys.dont_write_bytecode = False
        prefix = tunables.get("VERI_PYCACHE") or prefix
        if refusal(prefix) is None:
            sys.pycache_prefix = prefix
