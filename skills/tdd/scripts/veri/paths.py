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
    return os.path.dirname(os.path.dirname(_abspath_dotdot_after_symlink(file)))


def resolved_scripts_of(file):
    return os.path.dirname(os.path.dirname(os.path.realpath(file)))
