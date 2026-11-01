"""install-links.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

LINKED = ("vdev", "vcoord", "vplan", "vgroom", "vstatus", "vreport", "vfile", "vstop")
SKILLS = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def _common_dir(path):
    return subprocess.run(["git", "-C", path, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                          capture_output=True, text=True)


def _veri_skills():
    done = _common_dir(SKILLS)
    done.check_returncode()
    return os.path.join(os.path.dirname(done.stdout.strip()), "skills")


def main(argv):
    root = argv[0] if argv else os.getcwd()
    done = _common_dir(root)
    if done.returncode != 0:
        print("install-links: not a git repository: " + root, file=sys.stderr)
        return 2
    common = done.stdout.strip()
    target = os.path.join(os.path.dirname(common), ".claude", "skills")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    os.makedirs(target, exist_ok=True)
    veri_skills = _veri_skills()
    for name in LINKED:
        link = os.path.join(target, name)
        held = os.path.islink(link) and os.readlink(link).startswith(veri_skills + os.sep)
        if os.path.lexists(link) and not held:
            print("install-links.sh: not a veri link, left untouched: " + link, file=sys.stderr)
            return 2
    for name in LINKED:
        link = os.path.join(target, name)
        if os.path.islink(link) and not os.path.exists(link):
            os.unlink(link)
        if not os.path.islink(link):
            os.symlink(os.path.join(veri_skills, name), link)
    exclude = os.path.join(common, "info", "exclude")
    os.makedirs(os.path.dirname(exclude), exist_ok=True)
    with open(exclude, "a+") as out:
        out.seek(0)
        listed = out.read().splitlines()
        for name in LINKED:
            entry_line = "/.claude/skills/" + name
            if entry_line not in listed:
                out.write(entry_line + "\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
