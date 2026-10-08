"""veri's git runner, shared by the modules that shell out to git."""
import re
import subprocess


def git(*args, **kwargs):
    return subprocess.run(["git", *args], **kwargs)


def symref_default(answer):
    for line in answer.splitlines():
        m = re.match(r"ref: refs/heads/(\S+)\s+HEAD$", line)
        if m:
            return m.group(1)
    return None
