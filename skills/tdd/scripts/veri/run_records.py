"""A run's local records carried on origin's `refs/veri/runs/<n>`: a commit on no branch holding the issue's lines of
`.tdd/events.jsonl` (and those naming no issue), its `.tdd/issue-<n>-skill-commit`, its `.tdd/issue-<n>-timeout` and
its `.tdd/issue-<n>-branch-base`, so another machine's metrics and resume read them; nothing else travels, since
nothing else is read back. Never committed on the run's branch: rebase-merge would carry them into main's history."""
import getpass
import json
import os
import platform
import plistlib
import re
import socket
import sys
import tempfile
import time
import unicodedata
import urllib.parse

import git
import redaction
import run_dir

IDENTITY = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@localhost",
            "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@localhost"}
EVENTS = ".tdd/events.jsonl"
# What a first launch restores: run-conductor.sh the skill and timeout pins, preflight the branch base.
PINS = ("-skill-commit", "-timeout", "-branch-base")


def ref(issue):
    return "refs/veri/runs/%s" % issue


MAC_PREFIXES = ("/System/Volumes/Data", "/private")
PREFERENCES = "/Library/Preferences/SystemConfiguration/preferences.plist"
# A path ends where a path component cannot go on: a sensitive path followed by a letter, digit, `_` or `-` is another
# path (`/Users/<name>2`), left alone.
PATH_END = r"(?![A-Za-z0-9_-])"
PATH_START = r"(?<![A-Za-z0-9_.-])"
GENERIC_TEMP = re.compile(PATH_START + r"(?:/System/Volumes/Data)?(?:/private)?"
                          r"(?:/var/folders/[^/\s\"'`]+/[^/\s\"'`]+/[A-Z]"
                          r"|/tmp)" + PATH_END)
# A whole word: no letter or digit on either side, and not the inside of a placeholder (`<user>`), so a second pass
# finds nothing new; a preceding encoded slash (`%2F`, `%2f`) also starts a word.
WORD = r"(?:(?<![A-Za-z0-9<])|(?<=%%2[Ff]))%s(?![A-Za-z0-9>])"
REDACTED = "<redacted>"


def _path_bases(path):
    """<path> as given and resolved, with and without the macOS prefixes (`/private`, `/System/Volumes/Data`)."""
    bases = set()
    for spelled in {path, os.path.realpath(path)}:
        bare = spelled
        for prefix in MAC_PREFIXES:
            bare = bare.removeprefix(prefix)
        if not bare.strip("/"):
            continue
        bases |= {bare, "/private" + bare, "/System/Volumes/Data" + bare, "/System/Volumes/Data/private" + bare}
    return bases


def _path_spellings(path):
    """The spellings the readable layer replaces: each base, with `/` written as an escaped slash, and URL-encoded
    (`safe=""` and `safe="/"`); matched ignoring case, so lower-case hex is the same spelling."""
    forms = set()
    for base in _path_bases(path):
        forms |= {base, base.replace("/", "\\/"), urllib.parse.quote(base, safe=""), urllib.parse.quote(base, safe="/")}
    return forms


def _plist_names():
    """The Bonjour LocalHostName and the ComputerName from the system preferences, read with plistlib (no process);
    none when the file or a key is absent or unreadable."""
    try:
        with open(PREFERENCES, "rb") as f:
            prefs = plistlib.load(f)
    except (OSError, ValueError, plistlib.InvalidFileException):
        return set()
    found = set()
    for keys in (("System", "Network", "HostNames", "LocalHostName"), ("System", "System", "ComputerName")):
        value = prefs
        for key in keys:
            value = value.get(key) if isinstance(value, dict) else None
        if isinstance(value, str) and value:
            found.add(value)
    return found


def _host_forms():
    """The names this machine goes by, learnt with no process: socket.gethostname(), platform.node() and the plist's
    LocalHostName and ComputerName; each with its first DNS label, each also with `.local` and with `-` and space
    written either way. An IP-looking name is kept whole, never split; a form that is all digits or under 3
    characters is left out."""
    forms = set()
    for name in ({socket.gethostname(), platform.node()} | _plist_names()) - {""}:
        if re.fullmatch(r"[0-9.]+|[0-9A-Fa-f:]*:[0-9A-Fa-f:.]*", name):
            forms.add(name)
            continue
        names = {name, name.split(".")[0]}
        for each in names:
            forms |= {each, each + ".local", each.replace("-", " "), each.replace(" ", "-"),
                      each.replace("-", " ") + ".local", each.replace(" ", "-") + ".local"}
    return {form for form in forms if len(form) >= 3 and not form.replace(".", "").isdigit()
            or re.fullmatch(r"[0-9]+(?:\.[0-9]+){3}", form)}


def _account_names():
    """The account's name: the home directory's last component, and getpass.getuser() when it differs; a name under
    3 characters is left out."""
    names = {os.path.basename(os.path.expanduser("~").rstrip("/"))}
    try:
        names.add(getpass.getuser())
    except (KeyError, OSError):
        pass
    return {name for name in names if len(name) >= 3}


def _sensitive(run):
    """(paths by placeholder, host forms, account names) for the run at <run>."""
    run = os.path.abspath(run)
    paths = (("<repo>", [p for p in (run, run_dir.main_of_worktree(run)) if p]),
             ("<tmp>", [p for p in (tempfile.gettempdir(), os.environ.get("TMPDIR", "").rstrip("/")) if p]),
             ("~", [os.path.expanduser("~")]))
    return paths, _host_forms(), _account_names()


def _redactions(run, also=()):
    """The two layers a carried string goes through.

    readable: (regex, replacement) steps, in order: the paths as plain substrings ending at a path boundary, the longest
    first within each kind (the worktree and main clone roots `<repo>`, then the temp directories `<tmp>`, then the
    home directory `~`, each in every spelling _path_spellings gives, ignoring case); then any other temp path at a path
    boundary `<tmp>`; then each host form `<host>` and the account name `<user>`, whole words ignoring case.
    fail-closed: (normalized paths, word regex) that a normalized copy of a string must not hold after the first layer;
    one that still does is replaced whole by `<redacted>`."""
    paths, hosts, accounts = _sensitive(run)
    # <also>'s roots join the `<repo>` paths, which _sensitive (one argument, the seam tests fake) gives first.
    paths = tuple((repl, kind + [os.path.abspath(p) for p in also] if repl == "<repo>" else kind)
                  for repl, kind in paths)
    steps = []
    for repl, kind in paths:
        forms = set().union(*(_path_spellings(path) for path in kind))
        steps += [(re.compile(re.escape(form) + PATH_END, re.I), repl) for form in sorted(forms, key=len, reverse=True)]
    steps.append((GENERIC_TEMP, "<tmp>"))
    for names, repl in ((hosts, "<host>"), (accounts, "<user>")):
        steps += [(re.compile(WORD % re.escape(name), re.I), repl) for name in sorted(names, key=len, reverse=True)]
    normalized_paths = {_normalized(base) for _, kind in paths for path in kind for base in _path_bases(path)} - {None}
    words = sorted({_normalized(name) for name in hosts | accounts} - {None}, key=len, reverse=True)
    pattern = "|".join([re.escape(p) + PATH_END for p in sorted(normalized_paths, key=len, reverse=True)]
                       + [r"(?<![a-z0-9<])%s(?![a-z0-9>])" % re.escape(w) for w in words])
    return steps, re.compile(pattern) if pattern else None


ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿­"))
DECODE_PASSES = 50


def _normalized(text):
    """A copy of <text> as the fail-closed layer reads it, or None when it never stops decoding: URL-decoded (`+` read
    as a space, the form encoding) until it stops changing, each pass shrinking it or leaving it, at most DECODE_PASSES
    passes; then NFKC, with the zero-width characters and the soft hyphen dropped, an escaped slash or a backslash read
    as `/`, case-folded."""
    for _ in range(DECODE_PASSES):
        decoded = urllib.parse.unquote_plus(text)
        if decoded == text:
            break
        text = decoded
    else:
        if urllib.parse.unquote_plus(text) != text:
            return None
    text = unicodedata.normalize("NFKC", text).translate(ZERO_WIDTH)
    return text.replace("\\/", "/").replace("\\", "/").casefold()


def _redact_text(text, redactions):
    steps, leak = redactions
    text = redaction.redact(text)
    for pattern, repl in steps:
        text = pattern.sub(repl, text)
    seen = _normalized(text)
    if seen is None or leak is not None and leak.search(seen):
        return REDACTED
    return text


def redact_local(text, run, also=()):
    """<text> with every local path, host name and account name of the run at <run> replaced, line by line, as a carried
    string is (the two layers _redactions describes, after the token redaction; <also> names more roots written
    `<repo>`): a line still holding one after the
    first layer is replaced whole by `<redacted>`, so one leak costs one line, never the rest."""
    redactions = _redactions(run, also)
    return "\n".join(_redact_text(line, redactions) for line in text.split("\n"))


def _redact(value, redactions):
    """<value> (decoded JSON) with every string in it, keys included, redacted; the structure is kept as it is. A key
    whose redacted name another key already holds (an original one or one redacted before it) is suffixed, `~-2`,
    `<redacted-2>`…, so no value is lost."""
    if isinstance(value, str):
        return _redact_text(value, redactions)
    if isinstance(value, list):
        return [_redact(item, redactions) for item in value]
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            name = _redact_text(key, redactions)
            if name != key:
                # A redacted key never takes the place of another: suffix it until it names no key, so no value is lost.
                base, n = name, 1
                while name in value or name in out:
                    n += 1
                    name = ("%s-%d" % (base[:-1], n) + ">" if base.startswith("<") and base.endswith(">")
                            else "%s-%d" % (base, n))
            out[name] = _redact(item, redactions)
        return out
    return value


def _issue_lines(path, issue, redactions):
    try:
        with open(path, "rb") as f:
            raw = f.read().splitlines(keepends=True)
    except OSError:
        return b""
    kept = []
    for line in raw:
        try:
            record = json.loads(line)
        except ValueError:
            continue
        # A line naming no issue was written without run context and is this run's own, as metrics counts it.
        if isinstance(record, dict) and str(record.get("issue") or issue) == str(issue):
            kept.append(json.dumps(_redact(record, redactions), ensure_ascii=False).encode() + b"\n")
    return b"".join(kept)


def _first_file(roots, issue, suffix):
    for root in roots:
        try:
            with open(run_dir.issue_file(root, issue, suffix), "rb") as f:
                return f.read()
        except OSError:
            continue
    return None


def records(run, issue):
    """{name under .tdd/: bytes} for the run at <run>: its journal lines for <issue>, and the skill pin, the timeout
    pin and the branch base, each read from the run, else from the main tree it sits under; a file the run lacks is
    left out."""
    roots = [run] + [m for m in [run_dir.main_of_worktree(os.path.abspath(run))] if m]
    found = {}
    redactions = _redactions(run)
    lines = _issue_lines(os.path.join(run, EVENTS), issue, redactions)
    if lines:
        found["events.jsonl"] = lines
    for suffix in PINS:
        pin = _first_file(roots, issue, suffix)
        if pin is not None:
            found["issue-%s%s" % (issue, suffix)] = _redact_text(os.fsdecode(pin), redactions).encode()
    return found


def _out(*args, cwd, data=None, env=None):
    done = git.git(*args, cwd=cwd, input=data, capture_output=True,
                   env=None if env is None else {**os.environ, **env})
    if done.returncode != 0:
        raise git.GitFailed(args, done.returncode, os.fsdecode(done.stderr))
    return os.fsdecode(done.stdout).strip()


def commit(run, issue):
    """The commit (no parent, on no branch) holding <run>'s records for <issue> under `.tdd/`; GitFailed on a git
    error."""
    entries = []
    for name, content in sorted(records(run, issue).items()):
        blob = _out("hash-object", "-w", "--stdin", cwd=run, data=content)
        entries.append("100644 blob %s\t%s\n" % (blob, name))
    inner = _out("mktree", cwd=run, data="".join(entries).encode())
    outer = _out("mktree", cwd=run, data=("040000 tree %s\t.tdd\n" % inner).encode())
    # The dates are UTC, so the local time zone does not travel with the records.
    stamp = "%d +0000" % int(time.time())
    return _out("commit-tree", outer, "-m", "veri: run records of #%s" % issue, cwd=run,
                env={**IDENTITY, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})


def push(run, issue):
    """Replace origin's `refs/veri/runs/<issue>` with the commit of <run>'s records; GitFailed on a git error, a push
    ended at VERI_GIT_NETWORK_TIMEOUT included."""
    args = ("push", "-q", "--force", "origin", "%s:%s" % (commit(run, issue), ref(issue)))
    done = git.network(*args, cwd=run)
    if done.returncode != 0:
        raise git.GitFailed(args, done.returncode, done.stderr or "")


def read(issue, name, cwd):
    """The text of `.tdd/<name>` in origin's `refs/veri/runs/<issue>`, fetched into the clone at <cwd> under the same
    ref; None when origin has no such ref or file, or cannot be reached. A fetch ended at VERI_GIT_NETWORK_TIMEOUT is
    no answer too, said in one stderr line."""
    if not git.ok("remote", "get-url", "origin", cwd=cwd):
        return None
    fetched = git.network("fetch", "-q", "origin", "+%s:%s" % (ref(issue), ref(issue)), cwd=cwd)
    if isinstance(fetched, git.TimedOut):
        sys.stderr.write("%s not read: %s\n" % (ref(issue), " ".join((fetched.stderr or "").split())))
    if fetched.returncode:
        return None
    shown = git.git("show", "%s:.tdd/%s" % (ref(issue), name), cwd=cwd, capture_output=True)
    return os.fsdecode(shown.stdout) if shown.returncode == 0 else None


def delete(issue, cwd):
    """Delete origin's `refs/veri/runs/<issue>` from the clone at <cwd>, ended after VERI_GIT_NETWORK_TIMEOUT seconds;
    None when deleted, absent on origin, or there is no origin; else the reason, one line. Never raises."""
    if not git.ok("remote", "get-url", "origin", cwd=cwd):
        return None
    done = git.network("push", "origin", "--delete", ref(issue), cwd=cwd)
    if done.returncode == 0 or "remote ref does not exist" in (done.stderr or ""):
        return None
    return " ".join((done.stderr or "exit %d" % done.returncode).split())


def after_push():
    """push, for the issue the current branch `tdd/<n>-<slug>` names, from the working directory; nothing on another
    branch. A git failure is one stderr line and never an exit code: the records mirror the run."""
    issue = None
    try:
        issue = run_dir.branch_issue(git.out("rev-parse", "--abbrev-ref", "HEAD"))
        if issue:
            push(".", issue)
    except git.GitFailed as failed:
        print("push-branch.sh: %s not pushed: %s"
              % (ref(issue or "<n>"), " ".join((failed.stderr or str(failed)).split())),
              file=sys.stderr)
