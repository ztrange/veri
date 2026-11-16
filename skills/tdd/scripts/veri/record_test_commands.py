"""record-test-commands.sh's logic, run in-process: commit a project's test commands to its CLAUDE.md on a branch."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import detect_test_command
import entry
import git

USAGE = "usage: record-test-commands.sh <fast-cmd> <all-cmd> [repo-root]"
BRANCH = "veri-install"
MESSAGE = "Record the test commands veri runs\n\nveri reads these CLAUDE.md lines ahead of any inference."


class Refused(Exception):
    """No answer could be obtained (exit 2); str() is the stderr line."""


def declaring(line, marker):
    """Where in <line> the <marker> detect-test-command.sh reads a command after starts, or None: the first one outside
    a backtick span that a non-empty command follows."""
    at = 0
    while True:
        at = line.find(marker, at)
        if at < 0:
            return None
        if line[:at].count(b"`") % 2 == 0 and detect_test_command.unwrapped(
                line[at + len(marker):].lstrip(detect_test_command.SPACE)):
            return at
        at += len(marker)


def recorded(text, fast, full):
    """<text>, a CLAUDE.md's bytes, declaring <fast> and <full> as the fast and all tiers' commands: the line the
    detector reads each from rewritten from its marker on, where it stands; a tier no line declares appended."""
    lines = text.split(b"\n")
    missing = []
    for marker, command in ((b"veri: fast tests:", fast), (b"veri: all tests:", full)):
        for i, line in enumerate(lines):
            at = declaring(line, marker)
            if at is not None:
                lines[i] = line[:at] + marker + b" " + command
                break
        else:
            missing.append(marker + b" " + command + b"\n")
    text = b"\n".join(lines)
    if missing and text and not text.endswith(b"\n"):
        text += b"\n"
    return text + b"".join(missing)


def checked(*args, cwd, input=None):
    done = git.git(*args, cwd=cwd, input=input, capture_output=True)
    if done.returncode != 0:
        raise Refused("git %s: %s" % (" ".join(args), done.stderr.decode(errors="replace").strip()))
    return done.stdout.rstrip(b"\n")


def tip_of(root, default):
    fetched = git.network("fetch", "-q", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (default, default), cwd=root)
    if fetched.returncode != 0:
        raise Refused(fetched.stderr.strip() or "git fetch origin %s failed" % default)
    return checked("rev-parse", "--verify", "refs/remotes/origin/%s^{commit}" % default, cwd=root).decode()


def commit(root, tip, text):
    """A commit on <tip> whose tree is <tip>'s with CLAUDE.md holding <text>."""
    blob = checked("hash-object", "-w", "--stdin", cwd=root, input=text)
    entries = [e for e in checked("ls-tree", "-z", tip, cwd=root).split(b"\0") if e and not e.endswith(b"\tCLAUDE.md")]
    entries.append(b"100644 blob " + blob + b"\tCLAUDE.md")
    tree = checked("mktree", "-z", cwd=root, input=b"".join(e + b"\0" for e in entries))
    return checked("commit-tree", tree.decode(), "-p", tip, "-m", MESSAGE, cwd=root).decode()


def record(fast, full, root):
    default = git.default_branch(cwd=root)
    if not default:
        raise Refused("the default branch cannot be told")
    tip = tip_of(root, default)
    shown = git.git("show", "%s:CLAUDE.md" % tip, cwd=root, capture_output=True)
    text = shown.stdout if shown.returncode == 0 else b""
    sha = commit(root, tip, recorded(text, fast, full))
    pushed = git.network("push", "-q", "origin", "%s:refs/heads/%s" % (sha, BRANCH), cwd=root)
    if pushed.returncode != 0:
        raise Refused(pushed.stderr.strip() or "git push origin %s failed" % BRANCH)


def main(argv):
    args = list(argv)
    fast, full = (args + ["", ""])[:2]
    root = args[2] if len(args) > 2 and args[2] else "."
    try:
        record(os.fsencode(fast), os.fsencode(full), root)
    except Refused as refused:
        return entry.refuse(str(refused))
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
