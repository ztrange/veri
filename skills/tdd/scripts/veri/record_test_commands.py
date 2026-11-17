"""record-test-commands.sh's logic, run in-process: commit a project's test commands to its CLAUDE.md on a branch."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import detect_test_command
import entry
import git
import github

USAGE = "usage: record-test-commands.sh [--one-file <cmd>] <fast-cmd> <all-cmd> [repo-root]"
FAST, ALL, ONE_FILE = b"veri: fast tests:", b"veri: all tests:", b"veri: one test file:"
BRANCH = "veri-install"
MESSAGE = "Record the test commands veri runs\n\nveri reads these CLAUDE.md lines ahead of any inference."
TITLE = "Record the test commands veri runs"
BODY = ("Adds or updates the `veri: fast tests:` and `veri: all tests:` lines of `CLAUDE.md`: the commands veri runs for "
        "this repository's fast and full test tiers, read ahead of any inference. Until this pull request merges, veri's "
        "runs infer the commands. `/vinstall` opened it and never merges it.")


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


def declared(text, marker):
    """The command detect-test-command.sh reads after <marker> in <text>, a CLAUDE.md's bytes, or None: its own
    reader, line by line, first match."""
    try:
        for line in text.split(b"\n"):
            detect_test_command.answer_from(line, marker)
    except detect_test_command.Answer as found:
        return found.command
    return None


def unreadable(old, new, wanted):
    """Why <new>, the CLAUDE.md written over <old>, would not read back as asked, or None: every marker in <wanted>
    must read back exactly its command, and every other marker as it read in <old>."""
    asked = dict(wanted)
    for marker in (FAST, ALL, ONE_FILE):
        expected = asked.get(marker, declared(old, marker))
        got = declared(new, marker)
        if got != expected:
            return "%s would read back %r, not %r: nothing written" % (
                marker.decode(), None if got is None else got.decode(errors="replace"),
                None if expected is None else expected.decode(errors="replace"))
    return None


def declarations(fast, full, one_file=None):
    """The (marker, command) pairs to record: both tiers, and the one-test-file line when <one_file> is given."""
    return [(FAST, fast), (ALL, full)] + ([(ONE_FILE, one_file)] if one_file is not None else [])


def recorded(text, fast, full, one_file=None):
    """<text>, a CLAUDE.md's bytes, declaring <fast> and <full> as the fast and all tiers' commands, and <one_file> as
    the one-test-file command when given: the line the detector reads each from rewritten from its marker on, where it
    stands; a declaration no line holds appended."""
    lines = text.split(b"\n")
    missing = []
    for marker, command in declarations(fast, full, one_file):
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


def record(fast, full, root, one_file=None):
    checked("rev-parse", "--show-toplevel", cwd=root)
    default = git.default_branch(cwd=root)
    if not default:
        raise Refused("the default branch cannot be told")
    listed = git.network("ls-remote", "--heads", "origin", "refs/heads/" + BRANCH, cwd=root)
    if listed.returncode != 0:
        raise Refused(listed.stderr.strip() or "git ls-remote origin failed")
    if listed.stdout.strip():
        raise Refused("origin already has a branch %s: an earlier pull request may await review; nothing written" % BRANCH)
    tip = tip_of(root, default)
    shown = git.git("show", "%s:CLAUDE.md" % tip, cwd=root, capture_output=True)
    text = shown.stdout if shown.returncode == 0 else b""
    wanted = declarations(fast, full, one_file)
    if all(declared(text, marker) == command for marker, command in wanted):
        return None
    new = recorded(text, fast, full, one_file)
    why = unreadable(text, new, wanted)
    if why:
        raise Refused(why)
    sha = commit(root, tip, new)
    pushed = git.network("push", "-q", "origin", "%s:refs/heads/%s" % (sha, BRANCH), cwd=root)
    if pushed.returncode != 0:
        raise Refused(pushed.stderr.strip() or "git push origin %s failed" % BRANCH)
    os.chdir(root)
    try:
        return github.gh_pr_create(BRANCH, default, TITLE, BODY)
    except github.NoAnswer as refused:
        raise Refused("pushed %s, but no pull request was opened: %s" % (BRANCH, refused.detail.strip())) from refused


def main(argv):
    args = list(argv)
    one_file = None
    if args[:1] == ["--one-file"]:
        one_file, args = (args[1:2] or [""])[0], args[2:]
    fast, full = (args + ["", ""])[:2]
    if not fast or not full or one_file == "":
        return entry.refuse("record-test-commands.sh: a command is missing or empty", usage=USAGE)
    root = args[2] if len(args) > 2 and args[2] else "."
    try:
        url = record(os.fsencode(fast), os.fsencode(full), root, None if one_file is None else os.fsencode(one_file))
    except Refused as refused:
        return entry.refuse(str(refused))
    if url is None:
        return 3
    print(url)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
