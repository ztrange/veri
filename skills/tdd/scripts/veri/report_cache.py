"""report-cache.sh's computations, run in-process."""
import sys

USAGE = "usage: report-cache.sh refresh\n"


def main(argv):
    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
