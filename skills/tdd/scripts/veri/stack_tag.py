"""stack-tag.sh's logic, run in-process: cuts the tags of a landed slice, one per issue that changed behaviour (PRD
034.4c)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import re
import subprocess
import sys

import entry
import git
import github
import stack_fix
import stack_green

USAGE = "usage: stack-tag.sh <slice-pr-url> [--message <n>=<text>]..."
TAGGED = ("feat", "fix")  # a commit type that changes behaviour: its issue owes a tag
UNTAGGED = ("docs", "test", "refactor", "chore", "plan")  # a commit type that changes no behaviour
VERSION = re.compile(r"v([0-9]+)\.([0-9]+)")
_TYPE = re.compile(r"(\w+)(?:\([^()]*\))?!?:")


def arguments(argv):
    """(<slice-pr-url>, {issue number: message}) from <argv>; None when it is not one url followed by `--message
    <n>=<text>` pairs."""
    if not argv or argv[0].startswith("-") or len(argv) % 2 != 1:
        return None
    messages = {}
    for flag, value in zip(argv[1::2], argv[2::2], strict=True):
        pair = re.fullmatch(r"(\d+)=(.+)", value, re.S)
        if flag != "--message" or not pair:
            return None
        messages[pair[1]] = pair[2]
    return argv[0], messages


class _Unanswered(Exception):
    """A read got no answer; the message names the read."""


def _json(path, what):
    """GitHub's JSON answer on <path>; _Unanswered naming <what> when gh fails or the answer is not JSON."""
    run = github.gh_api(path, stderr=subprocess.PIPE)
    try:
        if run.returncode:
            raise ValueError(" ".join((run.stderr or "").split()))
        return json.loads(run.stdout)
    except ValueError as error:
        raise _Unanswered("%s got no answer: %s" % (what, error)) from None


class UnknownType(Exception):
    """A commit of an issue whose type is neither TAGGED nor UNTAGGED; the message is its subject."""


def owing(subjects):
    """The issues <subjects> name (stack_green.named's rule), in the order of their last commit, that owe a tag: any of
    their commits has a type in TAGGED. UnknownType naming the first commit of an issue whose type is in neither
    TAGGED nor UNTAGGED, or that has none."""
    last, owes = {}, set()
    for at, subject in enumerate(subjects):
        kind = _TYPE.match(subject)
        if stack_green.named(subject) and not (kind and kind[1] in TAGGED + UNTAGGED):
            raise UnknownType(subject)
        for issue in stack_green.named(subject):
            last[issue] = at
            if kind and kind[1] in TAGGED:
                owes.add(issue)
    return [issue for issue in sorted(last, key=last.get) if issue in owes]


def _subjects(repo, number):
    """The subjects of pull request <number>'s commits, oldest first, every page read."""
    subjects, page = [], 1
    while True:
        listed = _json("repos/%s/pulls/%s/commits?per_page=100&page=%d" % (repo, number, page),
                       "reading the commits of pull request %s" % number)
        if not listed:
            return subjects
        subjects += [commit["commit"]["message"].split("\n", 1)[0] for commit in listed]
        page += 1


def main(argv):
    parsed = arguments(argv)
    if parsed is None:
        return entry.refuse(usage=USAGE)
    pr, messages = parsed
    repo, number = pr.removeprefix("https://github.com/").rsplit("/pull/", 1)
    default = git.default_branch(cwd=".")
    try:
        pull = _json("repos/%s/pulls/%s" % (repo, number), "reading pull request " + pr)
        base = (pull.get("base") or {}).get("ref")
        if pull.get("merged") is not True or base != default:
            return entry.refuse("%s is %s; nothing tagged" % (
                pr, "not merged" if pull.get("merged") is not True else "merged into %s, not %s" % (base, default)),
                prefix="stack-tag: ")
        subjects = _subjects(repo, number)
    except _Unanswered as unanswered:
        return entry.refuse("%s; nothing tagged" % unanswered, prefix="stack-tag: ")
    try:
        owed = owing(subjects)
    except UnknownType as unknown:
        return entry.refuse("the commit '%s' of %s has a type that is neither %s nor %s; nothing tagged"
                            % (unknown, pr, ", ".join(TAGGED), ", ".join(UNTAGGED)), prefix="stack-tag: ")
    if not owed:
        print("stack-tag: no issue of %s owes a tag: none has a commit of type %s" % (pr, " or ".join(TAGGED)),
              file=sys.stderr)
        return 3
    try:
        titles = {issue: messages.get(issue) or _json("repos/%s/issues/%s" % (repo, issue), "reading issue #%s" % issue)
                  ["title"] for issue in owed}
    except _Unanswered as unanswered:
        return entry.refuse("%s; nothing tagged" % unanswered, prefix="stack-tag: ")
    code, _ = stack_fix.script("merge-lock.sh", "take", "--pid", str(os.getpid()))
    if code:
        return entry.refuse("merge-lock.sh take exits %d: nothing fetched or tagged" % code, prefix="stack-tag: ")
    try:
        return _tag(pull["merge_commit_sha"], subjects, owed, titles)
    finally:
        stack_fix.script("merge-lock.sh", "release", "--pid", str(os.getpid()))


def _next(tags):
    """The vN.M after the first of <tags> (`git tag --sort=-v:refname`'s lines) that is one; None when none is."""
    for tag in tags:
        version = VERSION.fullmatch(tag)
        if version:
            return "v%s.%d" % (version[1], int(version[2]) + 1)
    return None


def _tag(merge, subjects, owed, titles):
    """Under the merge lock: fetch tags, then cut and push one tag per issue in <owed>, in order, on its last commit
    of the landed range ending at <merge>."""
    fetched = git.network("fetch", "--tags", "origin", cwd=".")
    if fetched.returncode:
        return entry.refuse("git fetch --tags origin failed (exit %d): %s; nothing tagged"
                            % (fetched.returncode, " ".join(fetched.stderr.split())), prefix="stack-tag: ")
    landed = git.out("log", "--format=%H %s", "-n", str(len(subjects)), merge, cwd=".").splitlines()[::-1]
    if [line.split(" ", 1)[-1] for line in landed] != subjects:
        return entry.refuse("the %d commits ending at the merge commit %s are not the pull request's %d subjects in order;"
                            " nothing tagged" % (len(landed), merge, len(subjects)), prefix="stack-tag: ")
    commit = {}
    for line in landed:
        sha, subject = line.split(" ", 1)
        for issue in stack_green.named(subject):
            commit[issue] = sha
    untagged = [issue for issue in owed if not git.out("tag", "--points-at", commit[issue], cwd=".")]
    for issue in [issue for issue in owed if issue not in untagged]:
        print("stack-tag: #%s skipped: its commit %s already carries a tag" % (issue, commit[issue]), file=sys.stderr)
    if not untagged:
        print("stack-tag: every owed tag is already there; nothing tagged", file=sys.stderr)
        return 3
    for issue in untagged:
        name = _next(git.out("tag", "--sort=-v:refname", cwd=".").split())
        if name is None:
            return entry.refuse("the repository has no vN.M tag to bump from; #%s and after not tagged" % issue,
                                prefix="stack-tag: ")
        git.out("tag", "-a", name, "-m", titles[issue], commit[issue], cwd=".")
        pushed = git.network("push", "origin", "refs/tags/" + name, cwd=".")
        if pushed.returncode:
            git.out("tag", "-d", name, cwd=".")
            return entry.refuse("the push of tag %s for #%s failed (exit %d): %s; that local tag deleted, the tags pushed"
                                " before it kept" % (name, issue, pushed.returncode, " ".join(pushed.stderr.split())),
                                prefix="stack-tag: ")
        print("%s #%s %s" % (name, issue, commit[issue]))
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
