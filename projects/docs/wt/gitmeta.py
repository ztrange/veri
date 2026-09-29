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

And one rule keeps a build CHEAP, which docs/tests/build-guards.test.sh pins as a
budget: git is asked once per script, once per tag, and a fixed handful of times
besides. Every question is a process, and a process costs ~30 ms to start whatever
it answers — so a build's time is its question count, and a question asked per
commit or per blamed line is the one shape this module never takes. Twenty sandboxed
builds are most of what `make docs-test` costs, and a leaf on a docs issue runs that
suite after every edit.

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


# Which version each commit shipped in, answered once per (repo, tag list) and kept for
# the rest of the process. A build is one process, so this caches one build's answer;
# it is not state that outlives the tree it was read from.
_SHIPPED = {}


def _shipped(root, order):
    """{sha: the earliest tag containing it}, for every commit any tag contains.

    One `git rev-list <tag>` per tag, oldest first, and a sha keeps the first tag that
    claims it — which is what "the version it shipped in" means. Per tag rather than per
    commit because containment is the one question git only answers from a walk: `tag
    --contains` walks the whole history for ONE sha, and asking it once per blamed run
    and twice per script cost a real build 235 of its 476 processes.
    """
    key = (str(root), tuple(order))
    if key not in _SHIPPED:
        table = {}
        for tag in order:                    # oldest first, so the first claim wins
            for sha in (_git(root, "rev-list", tag) or "").splitlines():
                table.setdefault(sha, tag)
        _SHIPPED[key] = table
    return _SHIPPED[key]


def _first_tag_containing(root, sha, order):
    """The earliest version that contains this commit — i.e. the one it shipped in.

    Returns None for a commit no tag contains, which is the honest answer: it has not
    shipped yet. `order` is oldest-first; the ranking happened once, in _shipped().
    """
    return _shipped(root, order).get(sha)


def _history(root, starts):
    """[(sha, subject, [(status, old path, new path), ...])] newest first, for every
    commit reachable from any of `starts` — or None if git cannot answer.

    One `git log --name-status` over everything, in place of `show --name-only` once per
    commit and `log --follow` twice per script: the paths a commit touched are the same
    fact whichever question is later asked of them. A rename record carries both names
    — `R100<tab>old<tab>new` — and -M asks for rename detection outright rather than
    trusting diff.renames, because _added_and_changed() follows a script back through
    its renames by those records, which is what `--follow` did. A plain record has one
    path, reported as both.

    Each record is a NUL, the sha, a tab, the subject, then the status lines. NUL rather
    than a line-start sentinel because a subject can begin with anything.
    """
    out = _git(root, "log", "-M", "--name-status", "--format=%x00%H%x09%s", *starts)
    if out is None:
        return None
    history = []
    for record in out.split("\x00"):
        if not record.strip():
            continue
        head, _, body = record.partition("\n")
        sha, _, subject = head.partition("\t")
        files = []
        for line in body.splitlines():
            if line.strip():
                parts = line.split("\t")
                files.append((parts[0], parts[1], parts[-1]))
        history.append((sha, subject, files))
    return history


def _added_and_changed(history, rel):
    """(the commit that added `rel`, the newest behaviour commit that touched it).

    Either is None when the history does not say. Walks newest-first under the name the
    file had at each point: a rename record met on the way switches the name being looked
    for to the old one, which is `--follow` by hand — once over one history for every
    script, rather than twice per script. The rename commit itself counts as touching the
    file, as it does under --follow: a feat: that moves the skill is the version every
    script arrived at its path in. The add is the OLDEST add, as `--diff-filter=A` read
    from the bottom was: the walk is newest-first, so the last one seen wins.
    """
    path, added, changed = rel, None, None
    for sha, subject, files in history:
        for status, old, new in files:
            if new != path:
                continue
            if changed is None and BEHAVIOUR.match(subject):
                changed = sha
            if status == "A":
                added = sha
            elif status.startswith("R"):
                path = old
    return added, changed


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
    out = _git(root, "blame", "--line-porcelain", "HEAD", "--", rel)
    if out is None:
        return {}
    floor = tags.index(since)
    marks = {}
    for first, last, sha, subject in _runs(_blame_lines(out)):
        if not BEHAVIOUR.match(subject):
            continue
        tag = _first_tag_containing(root, sha, tags)
        if tag is None or tags.index(tag) <= floor:
            continue
        marks[first] = (tag, _subject_prose(subject), last)
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

    # A version's range is the commits that shipped in it — the ones it is the earliest
    # tag to contain, which is the rule the hunks rank by too, so the index and the
    # margins cannot disagree about which version a commit belongs to. HEAD is read
    # alongside the tags so a script's own history is on hand for the marks below.
    history = _history(root, ["HEAD"] + tags) or []
    shipped = _shipped(root, tags)
    in_version = {tag: [] for tag in tags}
    for sha, subject, files in history:
        tag = shipped.get(sha)
        if tag is not None:
            in_version[tag].append((subject, files))

    # Every tag's date and title in one question rather than two per tag.
    dated = {}
    for line in (_git(root, "for-each-ref",
                      "--format=%(refname:short)%09%(creatordate:short)%09%(contents:subject)",
                      "refs/tags") or "").splitlines():
        tag, _, rest = line.partition("\t")
        date, _, title = rest.partition("\t")
        dated[tag] = (date.strip(), title.strip())

    versions = []
    for tag in tags:
        issues, touched = [], set()
        for subject, files in in_version[tag]:
            m = ISSUE.search(subject)
            if m and m.group(1) not in issues:
                issues.append(m.group(1))
            if not BEHAVIOUR.match(subject):
                continue
            for _, _, path in files:
                name = path.rsplit("/", 1)[-1]
                if name in script_rel_paths:
                    touched.add(name)
        date, title = dated.get(tag, ("", ""))
        versions.append({
            "tag": tag,
            "date": date,
            "title": title,
            "issues": sorted(issues, key=int),
            "scripts": sorted(touched),
        })

    marks = {}
    for name, rel in script_rel_paths.items():
        added, changed = _added_and_changed(history, rel)
        since = _first_tag_containing(root, added, tags) if added else None
        marks[name] = {
            "since": since,
            "changed": _first_tag_containing(root, changed, tags) if changed else None,
            "hunks": hunks(root, rel, tags, since),
        }

    # "is there work past the last tag" — a boolean, deliberately not a count, so the
    # page changes state once at a tag boundary instead of on every commit.
    head = _git(root, "rev-list", "-1", "HEAD")
    tip = _git(root, "rev-list", "-1", tags[-1] + "^{commit}")
    return {"versions": versions, "marks": marks, "latest": tags[-1],
            "unreleased": bool(head and tip and head != tip)}
