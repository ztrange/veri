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
  revisions(path, since=None)   the shas of the commits that touched `path`, newest first; with `since`,
                                only those in since..HEAD. [] when git cannot log.
  paths_at(rev, directory)      the repo-relative paths of the files directly in `directory` at `rev` (git
                                ls-tree, not recursive; "" is the root); [] when git cannot list.
  subject(rev)                  `rev`'s commit subject plus its newline; "" when git cannot log.
  changed_test_files()          test files that differ from HEAD (changed, then untracked), repo-relative, in
                                git's order; OSError ("git <diff|ls-files> failed: ...") when a listing fails,
                                since an empty answer would read as "no test files".
  step_commits(step, issue)     the shas of the commits that are `step`'s own, from the committed ledger of
                                `issue`: after the latest commit that ticked any line before the one that
                                ticked `step`'s (HEAD for a step committed but not ticked). LookupError when
                                no committed ledger line of the step is found (no issue included); OSError
                                when a ledger log, show or rev-list fails.
  commit_of(rev)                the sha of the commit `rev` names; OSError when it names none.
  first_revision_with(needle, path)
                                the oldest commit whose change to `path` adds or removes an occurrence of
                                `needle` (git log -S); "" when none does or git cannot log.

Error modes: toplevel, has_rev, current_branch, revisions, paths_at, subject and first_revision_with turn a git failure into None / False / "" and
raise only OSError when git cannot start. Every query runs in the current directory and
runs git through git.git, the runner veri shares, untouched: the caller owns the working directory.
"""
import os
import subprocess

import git
import ledger
import run_dir
from case_reader import cut_cases, is_js_test_file, is_test_path


def toplevel():
    done = git.git("rev-parse", "--show-toplevel", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return os.fsdecode(done.stdout).rstrip("\n") if done.returncode == 0 else None


def has_rev(rev):
    return git.git("rev-parse", "--verify", "-q", rev, stdout=subprocess.DEVNULL).returncode == 0


def default_branch():
    """origin's default branch as refs/remotes/origin/HEAD names it, asking no remote; GitFailed when it names none."""
    default = git.default_branch(remote=False)
    if default is None:
        raise git.GitFailed(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], None, "no refs/remotes/origin/HEAD")
    return default


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


def revisions(path, since=None):
    listed = git.git("log", "--format=%H", *(["%s..HEAD" % since] if since else []), "--", path,
                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return os.fsdecode(listed.stdout).split()


def paths_at(rev, directory):
    listed = git.git("ls-tree", "--name-only", rev, "--", os.path.join(directory, "") or ".", stdout=subprocess.PIPE,
                     stderr=subprocess.DEVNULL)
    return os.fsdecode(listed.stdout).splitlines() if listed.returncode == 0 else []


def subject(rev):
    shown = git.git("log", "-1", "--format=%s", rev, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return os.fsdecode(shown.stdout)


def first_revision_with(needle, path):
    listed = git.git("log", "--reverse", "--format=%H", "-S" + needle, "--", path,
                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return next(iter(listed.stdout.decode().split()), "")


def changed_test_files():
    names = []
    for command in (("diff", "--name-only", "--no-renames", "-z", "HEAD"),
                    ("ls-files", "--others", "--exclude-standard", "--full-name", "-z", ":/")):
        done = git.git(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if done.returncode != 0:
            # A failed listing is no answer: an empty one would read as "no test files".
            raise OSError("git %s failed: %s" % (command[0], " ".join(os.fsdecode(done.stderr).split())))
        for raw in done.stdout.split(b"\0"):
            name = os.fsdecode(raw)
            if raw and (is_test_path(raw) or is_js_test_file(os.path.basename(name), os.path.dirname(name))):
                names.append(name)
    return names


def _out(*argv):
    done = git.git(*argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if done.returncode != 0:
        raise OSError("git %s failed: %s" % (" ".join(argv), " ".join(os.fsdecode(done.stderr).split())))
    return done.stdout.decode("utf-8", "replace")


def commit_of(rev):
    return _out("rev-parse", "--verify", "--quiet", rev + "^{commit}").strip()


def _phases_done(text):
    return bool(ledger.listed_phases(text)) and ledger.next_phase(text) is None


def step_commits(step, issue):
    """The commits that are `step`'s own: after the latest commit that ticked any ledger line before the one
    that ticked `step`'s line, up to and including that one (HEAD for a step not ticked yet). The committed
    ledger of the step's own issue is the only record of which commit belongs to which step; a ticked line
    carries ledger.PENDING_MARK until its refactor passes, so lines are compared without it."""
    step = ledger.unphased(step)
    if issue:
        path = run_dir.ledger(".", issue)
        revs = _out("log", "--reverse", "--format=%H", "--", path).split()
        previous, last_tick, tick = set(), revs[:1], None
        for rev in revs:
            matched = ledger.items_at(rev, path)
            texts = {ledger.unphased(m.group(2)): m.group(1) != " " or _phases_done(m.group(2)) for m in matched}
            ticked = {text for text, done in texts.items() if done}
            if step in ticked:
                tick = rev
                pending = any(ledger.unphased(m.group(2)) == step and m.group(2).endswith(ledger.PENDING_MARK)
                              for m in matched)
                for later in revs[revs.index(rev) + 1:] if pending else ():
                    if any(ledger.unphased(m.group(2)) == step and not m.group(2).endswith(ledger.PENDING_MARK)
                           for m in ledger.items_at(later, path)):
                        tick = later
                        break
                break
            if step in texts:
                tick = "HEAD"
            if ticked != previous:
                last_tick = [rev]
            previous = ticked
        if tick:
            return set(_out("rev-list", "%s..%s" % (last_tick[0], tick)).split())
    raise LookupError("step %s: no committed ledger line of it was found, so which commits are its own is unknown"
                      % step)
