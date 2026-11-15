"""Where a veri module's own scripts directory is, and whether a directory lies inside it.

Interface:

SCRIPTS                    the scripts directory of the veri modules themselves (scripts_of this file).

scripts_of(file)           the scripts directory two levels above file, with `..` resolved after any
                           symlink before it (the lexical path, not the real one); returns a str.
resolved_scripts_of(file)  the same directory from realpath(file), every symlink resolved; returns a str.
inside_scripts(file, where=None)
                           True when the real path of where (default: the current directory) equals
                           resolved_scripts_of(file) or lies under it; returns a bool.
"""
import os


def _abspath_dotdot_after_symlink(file):
    path = os.sep
    for part in os.path.join(os.getcwd(), file).split(os.sep):
        if not part:
            continue
        if part == "..":
            path = os.path.dirname(os.path.realpath(path))
        else:
            path = os.path.join(path, part)
    return path


def scripts_of(file):
    """The scripts directory above file's module directory, `..` resolved after any symlink."""
    return os.path.dirname(os.path.dirname(_abspath_dotdot_after_symlink(file)))


SCRIPTS = scripts_of(__file__)


def resolved_scripts_of(file):
    """The scripts directory above file's module directory, from the real path of file."""
    return os.path.dirname(os.path.dirname(os.path.realpath(file)))


def inside_scripts(file, where=None):
    """True when where (default: the current directory) is file's scripts directory or inside it."""
    scripts = resolved_scripts_of(file)
    here = os.path.realpath(os.getcwd() if where is None else where)
    return here == scripts or here.startswith(scripts + os.sep)
