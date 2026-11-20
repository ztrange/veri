"""skill-edit-half.sh's computation, run in-process: a ⟦skill-edit⟧ step's clean path in one call (PRD 038.4, #4450)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = 'usage: skill-edit-half.sh <n> [--change "<change>"]'


def main(argv):
    sys.stderr.write(USAGE + "\n")
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
