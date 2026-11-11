"""adjudicate.sh's budget and record commands, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: adjudicate.sh --check-budget | left <n> | record <n> <cause> <leaf-output>"


def main(argv):
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
