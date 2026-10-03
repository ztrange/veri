"""The one spelling of a path inside a run's .tdd/ directory."""
import os


def run_file(run, name):
    """The path of `name` inside `run`'s .tdd/ directory."""
    return os.path.join(run, ".tdd", name)
