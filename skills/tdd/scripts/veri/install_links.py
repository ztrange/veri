"""install-links.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

LINKED = ("vdev", "vcoord", "vplan", "vgroom", "vstatus", "vreport", "vfile", "vstop")
SKILLS = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def _veri_skills():
    done = subprocess.run(["git", "-C", SKILLS, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                          capture_output=True, text=True, check=True)
    return os.path.join(os.path.dirname(done.stdout.strip()), "skills")


def main(argv):
    root = argv[0] if argv else os.getcwd()
    done = subprocess.run(["git", "-C", root, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                          capture_output=True, text=True)
    if done.returncode != 0:
        print("install-links: not a git repository: " + root, file=sys.stderr)
        return 2
    target = os.path.join(os.path.dirname(done.stdout.strip()), ".claude", "skills")
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        os.makedirs(target, exist_ok=True)
        for name in LINKED:
            os.symlink(os.path.join(_veri_skills(), name), os.path.join(target, name))
    except OSError as err:
        print("install-links.sh: " + type(err).__name__ + ": " + str(err), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
