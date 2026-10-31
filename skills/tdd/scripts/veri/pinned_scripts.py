"""pinned-scripts.sh: the directory holding a run's pinned scripts."""
import os
import sys


def main(argv):
    if not argv:
        print("usage: pinned-scripts.sh <n>", file=sys.stderr)
        return 2
    tdd = os.path.join(os.getcwd(), ".tdd")
    here = os.path.join(tdd, "pinned-scripts")
    if not os.path.isdir(here):
        here = os.path.join(tdd, "wt", argv[0], ".tdd", "pinned-scripts")
    pin_name = "issue-%s-skill-commit" % argv[0]
    pin_file = os.path.join(os.path.dirname(here), pin_name)
    if not os.path.isfile(pin_file):
        pin_file = os.path.join(tdd, pin_name)
    if not os.path.isdir(here) and os.path.isfile(pin_file):
        with open(pin_file) as f:
            pin = f.read().strip()
        print("pinned scripts for run %s are gone; pinned commit %s; recover with: git archive %s skills/tdd/scripts"
              % (argv[0], pin, pin), file=sys.stderr)
        return 2
    if not os.path.isdir(here):
        print("pinned scripts for run %s are gone and no pin is recorded" % argv[0], file=sys.stderr)
        return 2
    print(here)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
