"""The git history queries tests_frozen's record policy asks; it decides, this module only looks.

Interface:
  toplevel()                    the working tree's root, or None outside a repository.
  has_rev(rev)                  True when git can verify `rev`.
  current_branch()              the abbreviated HEAD ("HEAD" when detached, "" when git cannot say).

Error modes: toplevel, has_rev and current_branch turn a git failure into None / False / "" and
raise only OSError when git cannot start. Every query runs in the current directory and
runs git through git.git, the runner veri shares, untouched: the caller owns the working directory.
"""
import os
import subprocess

import git


def toplevel():
    done = git.git("rev-parse", "--show-toplevel", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return os.fsdecode(done.stdout).rstrip("\n") if done.returncode == 0 else None


def has_rev(rev):
    return git.git("rev-parse", "--verify", "-q", rev, stdout=subprocess.DEVNULL).returncode == 0


def current_branch():
    done = git.git("rev-parse", "--abbrev-ref", "HEAD", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                   stdin=subprocess.DEVNULL)
    return done.stdout.decode().strip()
