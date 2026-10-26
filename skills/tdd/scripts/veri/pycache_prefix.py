import os
import sys

if sys.pycache_prefix is None:
    sys.pycache_prefix = os.path.join(os.environ.get("TMPDIR") or "/tmp", "veri-pycache-%d" % os.getuid())
    import tunables
    sys.pycache_prefix = tunables.read("VERI_PYCACHE") or sys.pycache_prefix
