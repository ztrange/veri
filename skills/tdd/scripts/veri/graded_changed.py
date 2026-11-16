"""graded-changed.sh's entry point, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import git
import grade_prose
import requirements

USAGE = "usage: graded-changed.sh <base-sha>"


def text_at(rev, file):
    """`file`'s text at `rev`, None when git cannot show it there."""
    shown = git.git("show", "%s:%s" % (rev, file), capture_output=True, text=True)
    return None if shown.returncode else shown.stdout


def section_at(rev, unit):
    file = unit.partition("#")[0]
    if text_at(rev, file) is None:
        return None
    return grade_prose.unit_text(unit, lambda path: text_at(rev, path))


def changed_unit(unit, changed, base):
    """Whether `unit` changed: a whole-file unit when its file did, a `file#heading` unit when its section's text did."""
    file, _, heading = unit.partition("#")
    if file not in changed:
        return False
    return not heading or section_at(base, unit) != section_at("HEAD", unit)


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    diff = git.git("diff", "--name-only", argv[0], "HEAD", capture_output=True, text=True)
    if diff.returncode:
        return 2
    changed = diff.stdout.split()
    hits = [fields[0] for g in requirements.tracked("GRADED") for fields in grade_prose.graded_lines(g)
            if changed_unit(fields[0], changed, argv[0])]
    for path in hits:
        print(path)
    return 1 if hits else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
