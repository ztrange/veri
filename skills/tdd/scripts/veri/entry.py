"""The one __main__ entry point every ported module calls."""
import os
import sys


def _shim_name(main):
    module = os.path.splitext(os.path.basename(main.__code__.co_filename))[0]
    return module.replace("_", "-") + ".sh"


def run(main, argv):
    try:
        code = main(argv)
    except Exception as exc:
        reason = " ".join(str(exc).split())
        sys.stderr.write(f"{_shim_name(main)}: {type(exc).__name__}: {reason}\n")
        sys.exit(2)
    sys.exit(code)
