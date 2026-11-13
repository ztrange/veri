"""install-links.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

LINKED = ("vcoord", "vdev", "vfile", "vgroom", "vhandoff", "vplan")
RETIRED = ("vready", "vreport", "vstatus", "vstop")
SKILLS = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", ".."))


def _common_dir(path):
    return subprocess.run(["git", "-C", path, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                          capture_output=True, text=True)


def _veri_skills():
    done = _common_dir(SKILLS)
    done.check_returncode()
    return os.path.join(os.path.dirname(done.stdout.strip()), "skills")


def _is_veri_link(link, veri_skills):
    return os.path.islink(link) and os.readlink(link).startswith(veri_skills + os.sep)


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
        if os.path.lexists(link) and not _is_veri_link(link, veri_skills):
            print("install-links.sh: not a veri link, left untouched: " + link, file=sys.stderr)
            return 2
    removed = []
    for name in RETIRED:
        link = os.path.join(target, name)
        if _is_veri_link(link, veri_skills):
            os.unlink(link)
            removed.append("/.claude/skills/" + name)
            print("removed " + name)
    for name in LINKED:
        link = os.path.join(target, name)
        if os.path.islink(link) and not os.path.exists(link):
            os.unlink(link)
        if not os.path.islink(link):
            os.symlink(os.path.join(veri_skills, name), link)
            print(name)
    exclude = os.path.join(common, "info", "exclude")
    os.makedirs(os.path.dirname(exclude), exist_ok=True)
    with open(exclude, "a+") as out:
        out.seek(0)
        listed = out.read().splitlines()
        if any(line in removed for line in listed):
            listed = [line for line in listed if line not in removed]
            out.seek(0)
            out.truncate()
            out.write("".join(line + "\n" for line in listed))
        for name in LINKED:
            entry_line = "/.claude/skills/" + name
            if entry_line not in listed:
                out.write(entry_line + "\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
