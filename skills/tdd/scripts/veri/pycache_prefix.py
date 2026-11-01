import os
import sys

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
        sys.pycache_prefix = os.path.join(os.environ.get("TMPDIR") or "/tmp", "veri-pycache-%d" % os.getuid())
        import tunables
        sys.pycache_prefix = tunables.read("VERI_PYCACHE") or sys.pycache_prefix
