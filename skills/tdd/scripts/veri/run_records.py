"""A run's local records carried on origin's `refs/veri/runs/<n>`: a commit on no branch holding the issue's lines of
`.tdd/events.jsonl` (and those naming no issue) and its `.tdd/issue-<n>-skill-commit`, so another machine's
metrics and resume read them; nothing else travels, since nothing else is read back. Never committed on the run's branch: rebase-merge would carry them into main's history."""
import getpass
import json
import os
import platform
import re
import socket
import sys
import tempfile
import time
import urllib.parse

import git
import run_dir

IDENTITY = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@localhost",
            "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@localhost"}
EVENTS = ".tdd/events.jsonl"


def ref(issue):
    return "refs/veri/runs/%s" % issue


MAC_PREFIXES = ("/System/Volumes/Data", "/private")
GENERIC_TEMP = re.compile(r"(?:/System/Volumes/Data)?(?:/private)?/var/folders/[^/\s\"'`]+/[^/\s\"'`]+/[A-Z]"
                          r"|(?:/System/Volumes/Data)?(?:/private)?/tmp")
WORD = r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])"


def _path_spellings(path):
    """Every spelling of <path> a line may hold: as given and resolved, with or without the macOS prefixes
    (`/private`, `/System/Volumes/Data`), each as is, with `/` written as an escaped slash, and URL-encoded (`safe=""` and `safe="/"`)."""
    bases = set()
    for spelled in {path, os.path.realpath(path)}:
        bare = spelled
        for prefix in MAC_PREFIXES:
            bare = bare.removeprefix(prefix)
        if not bare.strip("/"):
            continue
        bases |= {bare, "/private" + bare, "/System/Volumes/Data" + bare, "/System/Volumes/Data/private" + bare}
    forms = set()
    for base in bases:
        forms |= {base, base.replace("/", "\\/"), urllib.parse.quote(base, safe=""), urllib.parse.quote(base, safe="/")}
    return forms


def _host_forms():
    """The names this machine goes by, as Python sees them (no process started): socket.gethostname() and
    platform.node(), their first DNS label when it is not numeric and at least 3 characters, each also with `.local`
    and with `-` written as a space. An IP-looking name is kept whole, never split into labels."""
    forms = set()
    for name in {socket.gethostname(), platform.node()} - {""}:
        if re.fullmatch(r"[0-9.]+|[0-9A-Fa-f:]*:[0-9A-Fa-f:.]*", name):
            forms.add(name)
            continue
        names = {name}
        label = name.split(".")[0]
        if not label.isdigit() and len(label) >= 3:
            names.add(label)
        for each in names:
            forms |= {each, each + ".local", each.replace("-", " "), each.replace("-", " ") + ".local"}
    return forms


def _account_names():
    """The account's name: the home directory's last component, and getpass.getuser() when it differs; a name under
    3 characters is left out."""
    names = {os.path.basename(os.path.expanduser("~").rstrip("/"))}
    try:
        names.add(getpass.getuser())
    except (KeyError, OSError):
        pass
    return {name for name in names if len(name) >= 3}


def _redactions(run):
    """The steps a carried string goes through, in order: plain substrings, the longest first within each kind (the
    worktree and main clone roots read `<repo>`, then the temp directories `<tmp>`, then the home directory `~`, each in
    every spelling _path_spellings gives); then any other temp path; then each host form, whole word and ignoring case,
    `<host>`; then the account name, whole word and ignoring case, `<user>`."""
    run = os.path.abspath(run)
    steps = []
    kinds = (("<repo>", [run, run_dir.main_of_worktree(run)]),
             ("<tmp>", [tempfile.gettempdir(), os.environ.get("TMPDIR", "").rstrip("/")]),
             ("~", [os.path.expanduser("~")]))
    for repl, paths in kinds:
        forms = set().union(*(_path_spellings(path) for path in paths if path))
        steps += [(form, repl) for form in sorted(forms, key=len, reverse=True)]
    steps.append((GENERIC_TEMP, "<tmp>"))
    for names, repl in ((_host_forms(), "<host>"), (_account_names(), "<user>")):
        steps += [(re.compile(WORD % re.escape(name), re.I), repl) for name in sorted(names, key=len, reverse=True)]
    return steps


def _redact_text(text, redactions):
    for pattern, repl in redactions:
        text = text.replace(pattern, repl) if isinstance(pattern, str) else pattern.sub(repl, text)
    return text


def _redact(value, redactions):
    """<value> (decoded JSON) with every string in it, keys included, redacted; the structure is kept as it is."""
    if isinstance(value, str):
        return _redact_text(value, redactions)
    if isinstance(value, list):
        return [_redact(item, redactions) for item in value]
    if isinstance(value, dict):
        return {_redact(key, redactions): _redact(item, redactions) for key, item in value.items()}
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
    """{name under .tdd/: bytes} for the run at <run>: its journal lines for <issue>, and the skill pin, read from the
    run, else from the main tree it sits under; a file the run lacks is left out."""
    roots = [run] + [m for m in [run_dir.main_of_worktree(os.path.abspath(run))] if m]
    found = {}
    redactions = _redactions(run)
    lines = _issue_lines(os.path.join(run, EVENTS), issue, redactions)
    if lines:
        found["events.jsonl"] = lines
    pin = _first_file(roots, issue, "-skill-commit")
    if pin is not None:
        found["issue-%s-skill-commit" % issue] = _redact_text(os.fsdecode(pin), redactions).encode()
    return found


def _out(*args, cwd, data=None, env=None):
    done = git.git(*args, cwd=cwd, input=data, capture_output=True,
                   env=None if env is None else {**os.environ, **env})
    if done.returncode != 0:
        raise git.GitFailed(args, done.returncode, os.fsdecode(done.stderr))
    return os.fsdecode(done.stdout).strip()


def commit(run, issue):
    """The commit (no parent, on no branch) holding <run>'s records for <issue> under `.tdd/`; GitFailed on a git error."""
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
        print("push-branch.sh: %s not pushed: %s" % (ref(issue or "<n>"), " ".join((failed.stderr or str(failed)).split())),
              file=sys.stderr)
