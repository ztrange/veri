"""build-adjudicate-prompt.sh's prompt builder, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: build-adjudicate-prompt.sh <n> <cause> <exit-code> <stderr-file> <command…>"


def main(argv):
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
