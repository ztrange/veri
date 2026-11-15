"""The git history queries tests_frozen's record policy asks; it decides, this module only looks.

Interface:
  toplevel()                    the working tree's root, or None outside a repository.
  has_rev(rev)                  True when git can verify `rev`.
  current_branch()              the abbreviated HEAD ("HEAD" when detached, "" when git cannot say).
  text_at(rev, path, quiet=False)
                                the file's text at `rev`, "" when git cannot show it. quiet=True
                                swallows git's stderr; otherwise it reaches the caller's.
  cases_at(rev, path)           {case name: body} of the file at `rev`; {} when the file is absent from a
                                readable `rev`; OSError ("git show <rev>:<path> failed: ...") when git
                                cannot read `rev` at all. Twin names keep the last body.

Error modes: toplevel, has_rev and current_branch turn a git failure into None / False / "" and
raise only OSError when git cannot start. Every query runs in the current directory and
runs git through git.git, the runner veri shares, untouched: the caller owns the working directory.
"""
import os
import subprocess

import git
from case_reader import cut_cases


def toplevel():
    done = git.git("rev-parse", "--show-toplevel", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return os.fsdecode(done.stdout).rstrip("\n") if done.returncode == 0 else None


def has_rev(rev):
    return git.git("rev-parse", "--verify", "-q", rev, stdout=subprocess.DEVNULL).returncode == 0


def current_branch():
    done = git.git("rev-parse", "--abbrev-ref", "HEAD", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                   stdin=subprocess.DEVNULL)
    return done.stdout.decode().strip()


def text_at(rev, path, quiet=False):
    shown = git.git("show", "%s:%s" % (rev, path), stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL if quiet else None)
    return shown.stdout.decode("utf-8", "replace")


def cases_at(rev, path):
    shown = git.git("show", "%s:%s" % (rev, path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if shown.returncode != 0:
        # A file absent from a readable revision has no cases there; any other failure is no answer.
        listed = git.git("ls-tree", "--name-only", rev, "--", path, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
        if listed.returncode == 0 and not listed.stdout.strip():
            return {}
        raise OSError("git show %s:%s failed: %s" % (rev, path, " ".join(os.fsdecode(shown.stderr).split())))
    return dict(cut_cases(shown.stdout.decode("utf-8", "replace")))
