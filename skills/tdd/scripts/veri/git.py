"""veri's git runner, shared by the modules that shell out to git."""
import subprocess


def git(*args, **kwargs):
    return subprocess.run(["git", *args], **kwargs)
