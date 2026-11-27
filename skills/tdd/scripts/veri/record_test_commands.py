"""record-test-commands.sh's logic, run in-process: commit a project's test commands to its CLAUDE.md on a branch."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import detect_test_command
import entry
import git
import github

USAGE = "usage: record-test-commands.sh [--one-file <cmd>] [--quiet <cmd>] <fast-cmd> <all-cmd> [repo-root]"
FAST, ALL, ONE_FILE = b"veri: fast tests:", b"veri: all tests:", b"veri: one test file:"
QUIET = b"veri: quiet test files:"
# The one-test-file command takes the file as "$1" anywhere in it, or as a $1 word of its own.
PLACEHOLDER = re.compile(r'"\$1"|(?:^|\s)\$1(?:\s|$)')
BRANCH = "veri-install"
MESSAGE = "Record the test commands veri runs\n\nveri reads these CLAUDE.md lines ahead of any inference."
TITLE = "Record the test commands veri runs"
BODY = ("Adds or updates the `veri: fast tests:` and `veri: all tests:` lines of `CLAUDE.md`: the commands veri runs "
        "for this repository's fast and full test tiers, read ahead of any inference. Until this pull request merges, "
        "veri's runs infer the commands. `/vinstall` opened it and never merges it.")
ONE_FILE_BODY = (" It also adds or updates the `veri: one test file:` line: the command that runs one test file, "
                 "taking it as `\"$1\"`, without which a run's preflight stops.")
QUIET_BODY = (" It also adds or updates the `veri: quiet test files:` line: the command that runs the test files named "
              "after it with little output.")


def body(wanted):
    """The pull request's body: BODY, naming the one-test-file and quiet lines too when <wanted>, the (marker,
    command) pairs recorded, holds them."""
    markers = {marker for marker, _ in wanted}
    return BODY + (ONE_FILE_BODY if ONE_FILE in markers else "") + (QUIET_BODY if QUIET in markers else "")


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
    for marker in (FAST, ALL, ONE_FILE, QUIET):
        expected = asked.get(marker, declared(old, marker))
        got = declared(new, marker)
        if got != expected:
            return "%s would read back %r, not %r: nothing written" % (
                marker.decode(), None if got is None else got.decode(errors="replace"),
                None if expected is None else expected.decode(errors="replace"))
    return None


def declarations(fast, full, one_file=None, quiet=None):
    """The (marker, command) pairs to record: both tiers, the one-test-file line when <one_file> is given and the
    quiet line when <quiet> is."""
    return ([(FAST, fast), (ALL, full)] + ([(ONE_FILE, one_file)] if one_file is not None else [])
            + ([(QUIET, quiet)] if quiet is not None else []))


def recorded(text, fast, full, one_file=None, quiet=None):
    """<text>, a CLAUDE.md's bytes, declaring <fast> and <full> as the fast and all tiers' commands, <one_file> as
    the one-test-file command and <quiet> as the quiet test files command when given: the line the detector reads each
    from rewritten from its marker on, where it stands; a declaration no line holds appended."""
    lines = text.split(b"\n")
    crlf = lines[0].endswith(b"\r") and len(lines) > 1
    end = b"\r" if crlf else b""
    missing = []
    for marker, command in declarations(fast, full, one_file, quiet):
        # The detector keeps a line's trailing \r, so a CRLF file's command is backticked to read back exactly.
        stated = marker + (b" `" + command + b"`" if crlf else b" " + command) + end
        for i, line in enumerate(lines):
            at = declaring(line, marker)
            if at is not None:
                lines[i] = line[:at] + stated
                break
        else:
            missing.append(stated + b"\n")
    text = b"\n".join(lines)
    if missing and text and not text.endswith(b"\n"):
        text += end + b"\n"
    return text + b"".join(missing)


def checked(*args, cwd, input=None):
    done = git.git(*args, cwd=cwd, input=input, capture_output=True)
    if done.returncode != 0:
        raise Refused("git %s: %s" % (" ".join(args), done.stderr.decode(errors="replace").strip()))
    return done.stdout.rstrip(b"\n")


def tip_of(root, default):
    fetched = git.network("fetch", "-q", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (default, default),
                          cwd=root)
    if fetched.returncode != 0:
        raise Refused(fetched.stderr.strip() or "git fetch origin %s failed" % default)
    return checked("rev-parse", "--verify", "refs/remotes/origin/%s^{commit}" % default, cwd=root).decode()


def claude_md_mode(root, tip):
    """The mode of <tip>'s root CLAUDE.md ("100644" when absent); Refused unless it is a regular file."""
    try:
        listed = git.out("ls-tree", tip, "--", "CLAUDE.md", cwd=root)
    except git.GitFailed as failed:
        raise Refused("git ls-tree %s -- CLAUDE.md: %s" % (tip, failed.stderr.strip())) from failed
    mode = listed.split(" ", 1)[0] if listed else "100644"
    if mode not in ("100644", "100755"):
        raise Refused("CLAUDE.md is not a regular file on the default branch (mode %s): nothing written" % mode)
    return mode


def tree_of(root, tip, text, mode="100644"):
    """The tree of <tip> with CLAUDE.md, of <mode>, holding <text>."""
    blob = checked("hash-object", "-w", "--stdin", cwd=root, input=text)
    entries = [e for e in checked("ls-tree", "-z", tip, cwd=root).split(b"\0") if e and not e.endswith(b"\tCLAUDE.md")]
    entries.append(mode.encode() + b" blob " + blob + b"\tCLAUDE.md")
    return checked("mktree", "-z", cwd=root, input=b"".join(e + b"\0" for e in entries)).decode()


def remote_branch(root):
    """The commit origin's BRANCH points at, fetched, or None when origin has no such branch."""
    listed = git.network("ls-remote", "--heads", "origin", "refs/heads/" + BRANCH, cwd=root)
    if listed.returncode != 0:
        raise Refused(listed.stderr.strip() or "git ls-remote origin failed")
    if not listed.stdout.strip():
        return None
    fetched = git.network("fetch", "-q", "origin", "refs/heads/" + BRANCH, cwd=root)
    if fetched.returncode != 0:
        raise Refused(fetched.stderr.strip() or "git fetch origin %s failed" % BRANCH)
    return listed.stdout.split()[0]


def resume(root, default, held, tip, tree, wanted):
    """For an origin BRANCH that exists: None (nothing to do) when a pull request from it in this repository is open,
    whatever it holds; else open one when the branch holds exactly the commit this run would push (<tree> on <tip>);
    else Refused, saying whether it holds these commands cut from an older tip or other commands."""
    os.chdir(root)
    try:
        # A fork's PR from a branch of the same name is not this repository's branch, so it counts for nothing.
        ours = [p for p in github.open_pulls("number,url,isCrossRepository", head=BRANCH) if not p.cross_repository]
    except (github.NoAnswer, ValueError) as unread:
        raise Refused("cannot tell whether a pull request from %s is open" % BRANCH) from unread
    if ours:
        print("a pull request from %s is already open: %s" % (BRANCH, ours[0].html_url or ours[0].url), file=sys.stderr)
        return None
    same = (checked("rev-parse", held + "^{tree}", cwd=root).decode() == tree
            and checked("rev-parse", held + "^@", cwd=root).decode() == tip)
    if not same:
        shown = git.git("show", "%s:CLAUDE.md" % held, cwd=root, capture_output=True)
        theirs = shown.stdout if shown.returncode == 0 else b""
        if all(declared(theirs, marker) == command for marker, command in wanted):
            raise Refused("origin already has a branch %s with these commands, cut from an older tip of %s: delete the "
                          "branch, or open a pull request from it, then re-run; nothing written" % (BRANCH, default))
        raise Refused("origin already has a branch %s holding other commands: open a pull request from it, or delete "
                      "the branch, then re-run; nothing written" % BRANCH)
    return open_pull(default, wanted)


def open_pull(default, wanted):
    try:
        return github.gh_pr_create(BRANCH, default, TITLE, body(wanted))
    except github.NoAnswer as refused:
        raise Refused("pushed %s, but no pull request was opened: %s; re-run with the same commands to open it"
                      % (BRANCH, refused.detail.strip())) from refused


def record(fast, full, root, one_file=None, quiet=None):
    root = os.path.abspath(root)
    checked("rev-parse", "--show-toplevel", cwd=root)
    default = git.default_branch(cwd=root)
    if not default:
        raise Refused("the default branch cannot be told")
    held = remote_branch(root)
    tip = tip_of(root, default)
    mode = claude_md_mode(root, tip)
    shown = git.git("show", "%s:CLAUDE.md" % tip, cwd=root, capture_output=True)
    text = shown.stdout if shown.returncode == 0 else b""
    wanted = declarations(fast, full, one_file, quiet)
    if all(declared(text, marker) == command for marker, command in wanted):
        return None
    new = recorded(text, fast, full, one_file, quiet)
    why = unreadable(text, new, wanted)
    if why:
        raise Refused(why)
    tree = tree_of(root, tip, new, mode)
    if held:
        return resume(root, default, held, tip, tree, wanted)
    sha = checked("commit-tree", tree, "-p", tip, "-m", MESSAGE, cwd=root).decode()
    # Create-only: the lease expects the branch absent, so one created since the check is refused, never moved.
    pushed = git.network("push", "-q", "--force-with-lease=refs/heads/%s:" % BRANCH, "origin",
                         "%s:refs/heads/%s" % (sha, BRANCH), cwd=root)
    if pushed.returncode != 0:
        raise Refused(pushed.stderr.strip() or "git push origin %s failed" % BRANCH)
    os.chdir(root)
    return open_pull(default, wanted)


def main(argv):
    args = list(argv)
    options = {"--one-file": None, "--quiet": None}
    while args[:1] and args[0] in options and options[args[0]] is None:
        options[args[0]], args = (args[1:2] or [""])[0], args[2:]
    one_file, quiet = options["--one-file"], options["--quiet"]
    fast, full = (args + ["", ""])[:2]
    if not fast or not full or one_file == "" or quiet == "":
        return entry.refuse("record-test-commands.sh: a command is missing or empty", usage=USAGE)
    if one_file is not None and not PLACEHOLDER.search(one_file):
        return entry.refuse('record-test-commands.sh: the --one-file command must take the test file as "$1" '
                            '(anywhere in it) or as a $1 word of its own: %s' % one_file, usage=USAGE)
    root = args[2] if len(args) > 2 and args[2] else "."
    try:
        url = record(os.fsencode(fast), os.fsencode(full), root, None if one_file is None else os.fsencode(one_file),
                     None if quiet is None else os.fsencode(quiet))
    except Refused as refused:
        return entry.refuse(str(refused))
    if url is None:
        return 3
    print(url)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
