"""The one __main__ entry point every ported module calls."""
import sys


def run(main, argv):
    sys.exit(main(argv))
