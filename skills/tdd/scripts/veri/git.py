"""veri's one place for running git and naming the default branch.

Interface:
  git(*args, **kwargs)          subprocess.run(["git", *args], **kwargs), untouched: the
                                caller owns capture, check and the missing-binary case.
  out(*args, cwd=None)          stdout as str, trailing newlines stripped, nothing else.
                                Raises GitFailed on a non-zero exit or a missing git binary.
  ok(*args, cwd=None)           True on exit 0; False on any failure, a missing binary
                                included. Never raises.
  default_branch(cwd=None, remote=True)
                                the repository's default branch name, or None when it
                                cannot be told. Never raises.
  symref_default(answer)        the branch a `git ls-remote --symref` answer names, or None.

Error modes: out raises GitFailed (args_, returncode, stderr; returncode is None when git
could not start); ok and default_branch turn every failure into False / None. None, not an
exception, because "cannot tell" is an ordinary answer and each caller's fallback differs:
`git.default_branch() or "main"` or a refusal reads visibly at its own call site.

default_branch order: (1) the local refs/remotes/origin/HEAD, no network; (2) with
remote=True, what `git ls-remote --symref origin HEAD` reports; else None. remote=False
stops after (1), for callers that must not touch the network. A fallback to a local
main/master is the caller's to write.
"""
import re
import subprocess


class GitFailed(Exception):
    def __init__(self, args_, returncode, stderr):
        self.args_ = tuple(args_)
        self.returncode = returncode
        self.stderr = stderr
        how = "exit %s" % returncode if returncode is not None else "could not start"
        super().__init__("git %s failed (%s)" % (" ".join(self.args_), how))


def git(*args, **kwargs):
    return subprocess.run(["git", *args], **kwargs)


def out(*args, cwd=None):
    try:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    except OSError as error:
        raise GitFailed(args, None, str(error)) from error
    if done.returncode != 0:
        raise GitFailed(args, done.returncode, done.stderr)
    return done.stdout.rstrip("\n")


def ok(*args, cwd=None):
    try:
        out(*args, cwd=cwd)
    except GitFailed:
        return False
    return True


def default_branch(cwd=None, remote=True):
    try:
        local = out("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD", cwd=cwd)
        if local:
            return local.removeprefix("origin/")
    except GitFailed:
        pass
    if not remote:
        return None
    try:
        return symref_default(out("ls-remote", "--symref", "origin", "HEAD", cwd=cwd))
    except GitFailed:
        return None


def symref_default(answer):
    for line in answer.splitlines():
        m = re.match(r"ref: refs/heads/(\S+)\s+HEAD$", line)
        if m:
            return m.group(1)
    return None
