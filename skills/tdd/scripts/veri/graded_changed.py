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


def signed_at(rev, unit, units):
    """What `unit` signs at `rev`: a heading unit's own text, a split whole-file unit's view (cut by the heading units
    listed in the working tree), None when git cannot show the file there or the heading matches no line, or several."""
    text = text_at(rev, unit.partition("#")[0])
    if text is None:
        return None
    try:
        return grade_prose.signed_text(unit, grade_prose.unit_text(unit, lambda path: text), units)
    except ValueError:
        return None


def changed_unit(unit, changed, base, units):
    """Whether what `unit` signs changed: a heading unit's own text, a split whole-file unit's view, an unsplit
    whole-file unit's file."""
    file, _, heading = unit.partition("#")
    if file not in changed:
        return False
    if not heading and not grade_prose.claimed_headings(file, units):
        return True
    return signed_at(base, unit, units) != signed_at("HEAD", unit, units)


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    diff = git.git("diff", "--name-only", argv[0], "HEAD", capture_output=True, text=True)
    if diff.returncode:
        return 2
    changed = diff.stdout.split()
    units = [u for p in requirements.lists() for u in requirements.listed_units(p)]
    hits = [fields[0] for g in requirements.tracked("GRADED") for fields in grade_prose.graded_lines(g)
            if changed_unit(fields[0], changed, argv[0], units)]
    for path in hits:
        print(path)
    return 1 if hits else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
