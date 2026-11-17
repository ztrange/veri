"""graded-changed.sh's entry point, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
import tempfile

import git
import grade_prose
import requirements

USAGE = "usage: graded-changed.sh <base-sha>"


def text_at(rev, file):
    """`file`'s text at `rev`, None when git cannot show it there."""
    shown = git.git("show", "%s:%s" % (rev, file), capture_output=True, text=True)
    return None if shown.returncode else shown.stdout


def units_at(rev):
    """The units every REQUIREMENTS.md at `rev` lists, read from that commit; a list absent there lists nothing."""
    tree = git.git("ls-tree", "-r", "-z", "--name-only", rev, capture_output=True, text=True)
    if tree.returncode:
        return []
    units = []
    for path in tree.stdout.split("\0"):
        if os.path.basename(path) != "REQUIREMENTS.md":
            continue
        text = text_at(rev, path)
        if text is None:
            continue
        with tempfile.TemporaryDirectory() as scratch:
            copy = os.path.join(scratch, "REQUIREMENTS.md")
            with open(copy, "w", encoding="utf-8") as f:
                f.write(text)
            units += requirements.listed_units(copy)
    return units


def signed_at(rev, unit, units):
    """What `unit` signs at `rev`, cut by `units`, the units listed at `rev`: a heading unit's own text, a split
    whole-file unit's view, an unsplit one's file; None when git cannot show the file there or the heading matches no
    line, or several."""
    text = text_at(rev, unit.partition("#")[0])
    if text is None:
        return None
    try:
        return grade_prose.signed_text(unit, grade_prose.unit_text(unit, lambda path: text), units)
    except ValueError:
        return None


def changed_unit(unit, changed, base, listed):
    """Whether what `unit` signs changed between `base` and HEAD, each revision's view cut by the heading units that
    revision lists (`listed`, {rev: units}): so a range that claims or drops a section and edits it reports the
    whole-file unit. An unsplit whole-file unit at both revisions changed when its file did."""
    file, _, heading = unit.partition("#")
    if file not in changed:
        return False
    if not heading and not any(grade_prose.claimed_headings(file, units) for units in listed.values()):
        return True
    return signed_at(base, unit, listed[base]) != signed_at("HEAD", unit, listed["HEAD"])


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    diff = git.git("diff", "--name-only", argv[0], "HEAD", capture_output=True, text=True)
    if diff.returncode:
        return 2
    changed = diff.stdout.split()
    listed = {argv[0]: units_at(argv[0]), "HEAD": units_at("HEAD")}
    hits = [fields[0] for g in requirements.tracked("GRADED") for fields in grade_prose.graded_lines(g)
            if changed_unit(fields[0], changed, argv[0], listed)]
    for path in hits:
        print(path)
    return 1 if hits else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
