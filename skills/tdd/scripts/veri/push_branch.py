"""push-branch.sh's logic, run in-process."""
import errno
import os
import re
import shutil
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE = "usage: push-branch.sh [--force-with-lease=<branch>:<sha>]"
LEASE = re.compile(r"--force-with-lease=[^:]+:[0-9a-f]{7,40}")
REJECTIONS = ("non-fast-forward", "fetch first", "stale info")


def run(args, **kwargs):
    path = shutil.which(args[0]) or args[0]
    try:
        return subprocess.run([path, *args[1:]], **kwargs)
    except OSError as error:
        # hazard: a shell runs an executable with no #! line as a script; exec refuses it with ENOEXEC.
        if error.errno != errno.ENOEXEC:
            raise
        return subprocess.run(["sh", path, *args[1:]], **kwargs)


def record(*fields):
    if run([os.path.join(SCRIPTS, "event.sh"), *fields]).returncode != 0:
        return 2
    return 0


def output(args):
    return run(args, stdout=subprocess.PIPE, text=True).stdout.rstrip("\n")


def failed(attempts):
    print(f"push-branch.sh: push failed after {attempts} attempts; the branch is not on the remote",
          file=sys.stderr)


def tunable(name, default):
    value = os.environ.get(name) or default
    if not re.fullmatch(r"[0-9]+", value):
        print(f"push-branch.sh: {name} must be a non-negative integer, got '{value}'",
              file=sys.stderr)
        return None
    return value


def main(argv):
    if argv and (len(argv) != 1 or not LEASE.fullmatch(argv[0])):
        print("push-branch.sh: the only argument is --force-with-lease=<branch>:<sha>, "
              f"got '{' '.join(argv)}'", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    retries = tunable("VERI_PUSH_RETRIES", "3")
    if retries is None:
        return 2
    backoff = tunable("VERI_PUSH_BACKOFF", "2")
    if backoff is None:
        return 2
    attempt = 0
    retries = int(retries)
    while attempt <= retries:
        attempt += 1
        pushed = run(["git", "push", *argv, "--set-upstream", "origin", "HEAD"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if pushed.returncode == 0:
            return 0
        out = pushed.stdout.rstrip("\n")
        if "[rejected]" in out and any(reason in out for reason in REJECTIONS):
            branch = output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            listed = output(["git", "ls-remote", "origin", f"refs/heads/{branch}"])
            remote_sha = "\n".join(line.split("\t")[0] for line in listed.split("\n")) if listed else ""
            print(f"push rejected (non-fast-forward): origin/{branch} is at {remote_sha}",
                  file=sys.stderr)
            return record("push-rejected", f"remote_sha={remote_sha}", f"error={out}") or 1
        if attempt <= retries:
            run(["sleep", backoff])
            backoff = str(int(backoff) * 2)
    failed(attempt)
    return record("push-failed", f"error={out}", f"attempts={attempt}")


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
