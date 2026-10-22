import os


def scripts_of(file):
    return os.path.dirname(os.path.dirname(os.path.abspath(file)))
