import os


def scripts_dir(file):
    return os.path.dirname(os.path.dirname(os.path.abspath(file)))
