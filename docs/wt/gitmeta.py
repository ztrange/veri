"""gitmeta.py — what the walkthrough knows about veri's version history.

Everything here is read from git at build time, so the capability index cannot drift
from what actually shipped: a version is an annotated tag, its name is the tag's
message, and which sections it touched is computed from the commits in its range.

Two rules keep the generated page DETERMINISTIC, which `make docs-check` requires —
it regenerates and demands a byte-identical result:

  * no commit shas, and no count of commits as such, ever reaches the page. Both
    change on every commit, which would turn docs-check red after each one until
    someone re-ran `make docs` — a treadmill, not a guard. solved_by_itself() counts
    a specific commit — one issue veri scoped for itself — so it moves once per
    issue, on the same rhythm as a tag, not once per commit.
  * dates are absolute (the tag's own date, retro-dated at creation). A relative
    date baked into HTML would make docs-check fail by the calendar with no code
    change at all.

Everything degrades to None when git is unavailable or the repo carries no tags:
docs/tests/build-guards.test.sh builds from a copied tree with no .git in it, and
that build must still succeed — just without the version layer.
"""
import re
import subprocess

# A version is a capability. Documentation, tests, refactors and chores do not get
# one, so only these two types count a commit as having changed what veri can do.
BEHAVIOUR = re.compile(r"^(feat|fix)(\(.*\))?:")
ISSUE = re.compile(r"\(#(\d+)\)")

# One issue veri solved by being run on its own repository. The conductor's first act on
# an issue is to commit the plan ledger under exactly this subject (SKILL.md step 2.2),
# and it does it once per issue — so counting these commits counts the issues, without
# needing the run's own bookkeeping to have survived anywhere.
SELF_SCOPE = re.compile(r"^plan: scope #\d+")


def _git(root, *args):
    """stdout of a git command, or None if git or the repo is not there."""
    try:
        p = subprocess.run(("git", "-C", str(root)) + args,
                           capture_output=True, text=True)
    except (OSError, ValueError):
        return None
    return p.stdout.strip() if p.returncode == 0 else None


def _first_tag_containing(root, sha, order):
    """The earliest version that contains this commit — i.e. the one it shipped in.

    `git tag --contains` answers in whatever order it likes, so rank against the
    caller's ordered tag list rather than trusting the output. Returns None for a
    commit no tag contains, which is the honest answer: it has not shipped yet.
    """
    out = _git(root, "tag", "--contains", sha)
    if not out:
        return None
    have = {t for t in out.splitlines() if t}
    for t in order:                      # order is oldest-first
        if t in have:
            return t
    return None


def _subject_prose(subject):
    """A commit subject as prose: no `feat:`/`fix(scope):` prefix, no `(#N)` reference."""
    return ISSUE.sub("", BEHAVIOUR.sub("", subject)).strip()


def _blame_lines(out):
    """(sha, subject) for each line of `git blame --line-porcelain` output, in file order.

    Every record is a header line — `<sha> <orig> <final> [<n>]` — then key/value
    fields, then the source line itself prefixed with a tab. --line-porcelain (rather
    than --porcelain) repeats the fields for every line, so each record is complete on
    its own and no state has to be carried between commits.
    """
    sha = subject = None
    for line in out.splitlines():
        if line.startswith("\t"):            # the source line closes the record
            yield sha, subject or ""
            sha = subject = None
        elif sha is None:
            sha = line.split(" ", 1)[0]
        elif line.startswith("summary "):
            subject = line[len("summary "):]
    if sha is not None:                      # a final line whose tab _git() stripped
        yield sha, subject or ""


def _blame(root, rel):
    """(sha, subject) per line of `rel` as HEAD has it — or None if git cannot answer.

    The one place the blame command is spelled, for the two questions asked of it: which
    versions touched a script (hunks) and which touched the prose about one (prose_marks).
    Both need the same list of lines, and a difference between them here — a different
    revision, a missing `--line-porcelain` — would be a difference nothing names.
    """
    out = _git(root, "blame", "--line-porcelain", "HEAD", "--", rel)
    return None if out is None else list(_blame_lines(out))


def _runs(blame):
    """(first line, last line, sha, subject) for each run of lines one commit last touched.

    The grouping half of hunks() below, kept apart from the tagging half because the two
    read differently: this one knows nothing about versions, only that consecutive lines
    blaming the same commit are one run.

    A run's end is only known once a different sha has answered for the line below it, so
    a run is yielded as the next one opens — and the last one when the lines run out.
    """
    first = last = sha = subject = None
    for lineno, (line_sha, line_subject) in enumerate(blame, start=1):
        if line_sha != sha:
            if sha is not None:
                yield first, last, sha, subject
            first, sha, subject = lineno, line_sha, line_subject
        last = lineno
    if sha is not None:
        yield first, last, sha, subject


def _newest_tag(root, lines, tags):
    """The latest version any of these blamed lines shipped in — None if none did.

    The ranking half of prose_marks() below, kept apart from the span half for the reason
    _runs() is kept apart from hunks(): this one knows nothing about where the lines came
    from, only that a set of them answers with one version, the newest.

    Two kinds of line answer nothing and are skipped rather than counted: one whose last
    commit changed no capability — a `docs:` or `refactor:` hides what it sat on, and
    reaching past it would be guessing at which of the two wrote the words — and one whose
    commit no tag contains yet, which has not shipped in any version to report.

    A commit is asked about once however many of the span's lines it wrote. That is a
    saving and not a nicety: _first_tag_containing() forks a `git tag --contains`, a span
    is normally one commit repeated down every line of it, and the whole of a prose file
    gets covered by spans — so the naive form spends one process per line of it and turns
    a one-second build into a minute-long one.
    """
    newest = None
    asked = set()
    for sha, subject in lines:
        if sha in asked or not BEHAVIOUR.match(subject):
            continue
        asked.add(sha)
        tag = _first_tag_containing(root, sha, tags)
        if tag is None:
            continue
        if newest is None or tags.index(tag) > tags.index(newest):
            newest = tag
    return newest


def hunks(root, rel, tags, since):
    """{first line: (tag, description, last line)} for each tagged hunk.

    A hunk is a run of consecutive lines whose last-touching commit is the same one, so
    it has two ends: the key is the line it starts on, and the last element of the value
    is the line it ends on. A reader ruling a margin down its side, or linking to it as
    `classify-bail.sh L3–4`, needs both.

    It earns a tag only when that commit changed a capability and shipped in a version
    later than the file's own `since` — a hunk from the version the file arrived in says
    nothing the header badge has not already said, once.

    A non-behaviour commit hides what it sat on rather than inheriting its tag: blame
    answers who touched the line LAST, so reaching back past a `refactor:` for the
    `feat:` underneath it would be guessing.

    `since` is None for a file no tag contains yet, and there is no floor to rank hunks
    against without it — so that answers {} here rather than at every call site.
    """
    if since not in tags:
        return {}
    blame = _blame(root, rel)
    if blame is None:
        return {}
    floor = tags.index(since)
    marks = {}
    for first, last, sha, subject in _runs(blame):
        if not BEHAVIOUR.match(subject):
            continue
        tag = _first_tag_containing(root, sha, tags)
        if tag is None or tags.index(tag) <= floor:
            continue
        marks[first] = (tag, _subject_prose(subject), last)
    return marks


def prose_marks(root, rel, tags, spans):
    """{(first line, last line): tag} for each span of prose that a version explains.

    The same blame as hunks(), pointed at the file the PROSE is committed in — the spans
    are line ranges of `rel` itself, not of the script a chunk describes, because only
    the former has a history that can say when the explanation changed.

    A span is answered by the NEWEST version any of its lines shipped in: a chunk a reader
    comes back to is as new as the newest thing said in it, and one line rewritten by a
    later version makes the whole paragraph a different explanation.

    A non-behaviour commit hides what it sat on, exactly as it does for the scripts — a
    prose tidy is not a new explanation. A span with nothing left visible for _newest_tag()
    to answer with is absent from the map rather than keyed to None.
    """
    blame = _blame(root, rel)
    if blame is None:
        return {}
    marks = {}
    for first, last in spans:
        newest = _newest_tag(root, blame[first - 1:last], tags)
        if newest is not None:
            marks[(first, last)] = newest
    return marks


def origin_url(root):
    """The repo's https URL, for linking issue numbers — or None if it cannot be read.

    Both remote forms reduce to the same page; anything else returns None and the
    issue numbers render as plain text rather than as links that go nowhere.
    """
    url = _git(root, "remote", "get-url", "origin")
    if not url:
        return None
    m = re.match(r"(?:git@github\.com:|https://github\.com/)(.+?)(?:\.git)?$", url)
    return "https://github.com/" + m.group(1) if m else None


def solved_by_itself(root):
    """How many issues veri has solved by being run on its own repository — or None.

    One `plan: scope #<n>` commit reachable from HEAD is one issue veri scoped, tested
    and landed for itself, so the page can state the figure instead of carrying a number
    somebody typed and nobody re-counts.

    None — not 0 — is the answer for a tree that cannot say: no git, no commits, or a
    history with none of those commits in it, which is what a fork, a tarball or a
    shallow checkout looks like. The claim is prose and stays on the page either way;
    only the figure goes, because "0 issues" would be a worse answer than none.
    """
    out = _git(root, "log", "--format=%s", "HEAD")
    if out is None:
        return None
    return sum(1 for s in out.splitlines() if SELF_SCOPE.match(s)) or None


def read(root, script_rel_paths):
    """The version history, or None when this tree cannot answer.

    script_rel_paths maps a script's filename to its path relative to the repo root.
    """
    if _git(root, "rev-parse", "--git-dir") is None:
        return None
    # -v:refname is git's version sort. Plain sort makes v0.9 outrank v0.10, which
    # would put the newest release in the middle of the index.
    out = _git(root, "tag", "--sort=v:refname")
    tags = [t for t in (out or "").splitlines() if re.fullmatch(r"v\d+\.\d+", t)]
    if not tags:
        return None                      # a repo that does not version this way

    versions = []
    for i, tag in enumerate(tags):
        rng = tag if i == 0 else "%s..%s" % (tags[i - 1], tag)
        log = (_git(root, "log", "--format=%H\t%s", rng) or "").splitlines()
        issues, touched = [], set()
        for line in log:
            sha, subject = line.split("\t", 1)
            m = ISSUE.search(subject)
            if m and m.group(1) not in issues:
                issues.append(m.group(1))
            if not BEHAVIOUR.match(subject):
                continue
            for path in (_git(root, "show", "--name-only", "--format=", sha) or "").splitlines():
                name = path.rsplit("/", 1)[-1]
                if name in script_rel_paths:
                    touched.add(name)
        versions.append({
            "tag": tag,
            "date": _git(root, "for-each-ref", "--format=%(creatordate:short)",
                         "refs/tags/" + tag) or "",
            "title": _git(root, "for-each-ref", "--format=%(contents:subject)",
                          "refs/tags/" + tag) or "",
            "issues": sorted(issues, key=int),
            "scripts": sorted(touched),
        })

    marks = {}
    for name, rel in script_rel_paths.items():
        # --follow, or the move out of .claude/skills truncates every history to it.
        # One path at a time: --follow refuses more.
        added = (_git(root, "log", "--diff-filter=A", "--follow", "--format=%H",
                      "--", rel) or "").splitlines()
        hist = (_git(root, "log", "--follow", "--format=%H\t%s", "--", rel) or "").splitlines()
        changed = [l.split("\t", 1)[0] for l in hist if BEHAVIOUR.match(l.split("\t", 1)[1])]
        since = _first_tag_containing(root, added[-1], tags) if added else None
        marks[name] = {
            "since": since,
            "changed": _first_tag_containing(root, changed[0], tags) if changed else None,
            "hunks": hunks(root, rel, tags, since),
        }

    # "is there work past the last tag" — a boolean, deliberately not a count, so the
    # page changes state once at a tag boundary instead of on every commit.
    head = _git(root, "rev-list", "-1", "HEAD")
    tip = _git(root, "rev-list", "-1", tags[-1] + "^{commit}")
    return {"versions": versions, "marks": marks, "latest": tags[-1],
            "unreleased": bool(head and tip and head != tip)}
