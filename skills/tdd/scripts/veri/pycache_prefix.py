"""Sets where this run reads and writes bytecode; a veri module's first line runs it before any veri import."""
import os
import stat
import sys


def refusal(prefix):
    """Why <prefix> may not be this user's bytecode cache, or None when it may; an absent one is created with mode 0700.

    It may only when `lstat` shows a directory, not a symlink, owned by this user and writable by neither group nor
    others, in a parent that group and others cannot write unless it has the sticky bit, as /tmp does (#3965): on a
    shared /tmp another user can create the path first, and in an open parent swap it after the check."""
    try:
        try:
            os.makedirs(prefix, 0o700)
        except FileExistsError:
            pass
        info = os.lstat(prefix)
        parent = os.stat(os.path.dirname(os.path.abspath(prefix))).st_mode
    except OSError as error:
        return "it cannot be created or read: %s" % error.strerror
    mode = info.st_mode
    if stat.S_ISLNK(mode):
        return "it is a symlink"
    if not stat.S_ISDIR(mode):
        return "it is not a directory"
    if info.st_uid != os.getuid():
        return "it is owned by uid %d, not this user's %d" % (info.st_uid, os.getuid())
    if mode & stat.S_IWGRP:
        return "it is group-writable"
    if mode & stat.S_IWOTH:
        return "it is other-writable"
    if parent & (stat.S_IWGRP | stat.S_IWOTH) and not parent & stat.S_ISVTX:
        return "its parent is group- or other-writable without the sticky bit"
    return None


def from_source():
    """Makes veri's modules (those in sys.path[0]) compile from source, never reading or writing their bytecode, while
    the standard library keeps its own .pyc files."""
    from importlib.machinery import SOURCE_SUFFIXES, FileFinder, SourceFileLoader

    class FromSource(SourceFileLoader):
        def path_stats(self, path):
            raise OSError("this run never reads veri's bytecode")

    def veri_finder(path, modules=sys.path[0], finder=FileFinder.path_hook((FromSource, SOURCE_SUFFIXES))):  # noqa: B008 -- built once, not on every path asked about
        if path != modules:
            raise ImportError("not veri's directory")
        return finder(path)

    sys.path_hooks.insert(0, veri_finder)
    sys.path_importer_cache.pop(sys.path[0], None)


if sys.pycache_prefix is None and sys.dont_write_bytecode:
    # A shim run: no manifest vouches for veri's bytecode (#2368, #2439), so its modules always
    # compile from source. A prefix would hide the standard library's .pyc files too, and
    # recompile every import on every start.
    from_source()
else:
    # The prefix is checked whatever set it: VERI_PYCACHE, the default, or a PYTHONPYCACHEPREFIX the caller exported.
    prefix = sys.pycache_prefix
    if prefix is None:
        # Until the prefix is proved this user's, tunables compiles from source: under /dev/null no .pyc can exist or be
        # written, and none beside the source is read (#2405).
        sys.pycache_prefix = os.devnull
        import tunables
        sys.pycache_prefix = None
        default = os.path.join(os.environ.get("TMPDIR") or "/tmp", "veri-pycache-%d" % os.getuid())
        prefix = tunables.get("VERI_PYCACHE") or default
    prefix = prefix.rstrip("/") or "/"  # with a trailing slash lstat would follow a symlink
    reason = refusal(prefix)
    if reason is None:
        sys.pycache_prefix = prefix
    else:
        sys.pycache_prefix = None
        sys.dont_write_bytecode = True  # with no prefix, a write would land beside the source, in the repository
        sys.stderr.write("veri: not using the bytecode cache %s: %s; compiling veri's modules from source\n" % (prefix, reason))
        from_source()
