import os


def scripts_of(file):
    return os.path.dirname(os.path.dirname(os.path.abspath(file)))


def resolved_scripts_of(file):
    return os.path.dirname(os.path.dirname(os.path.realpath(file)))
