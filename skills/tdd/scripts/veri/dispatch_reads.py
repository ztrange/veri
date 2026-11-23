"""dispatch.sh's reads, run in-process: GitHub's comments, PRs and issue lists, the queued merges this clone runs, and
the overlap between an issue and the open run draft PRs. It never imports dispatch: dispatch.py hands over its namespace
(bind), and each name a test patches on dispatch (`last_comment`, `target_repo`, `clock`, `_reads`, ...) is looked up
there when called (via), so the patch still takes effect."""
import json
import os
import re
import subprocess
import sys
import time

import github
import json_documents
import paths
import pid_file
import role_state
import tunables
import watch_runs
import workqueue

_home = {}


def bind(namespace):
    """Hands this module the namespace its lookups read: dispatch.py's globals(). The first binder wins, so a copy of
    dispatch.py a test loads from its file (spec_from_file_location) never takes the lookups from the module it copies;
    dispatch.sh runs dispatch.py as its main module, the one binder."""
    _home.setdefault("namespace", namespace)


def via(name):
    """<name> as the bound namespace holds it now, a patch included."""
    return _home["namespace"][name]


class RateLimitPersists(watch_runs.QueueUnreadable):
    pass


def _read_after_rate_limit(read, path):
    """read(path); a rate limit waits for the reset (none already past) and reads again, at most
    VERI_GH_REFUSAL_RETRIES waits, then RateLimitPersists; a reset gh cannot report is the read's own NoAnswer."""
    waits = 0
    while True:
        try:
            return read(path)
        except github.NoAnswer as failure:
            detail = failure.detail or str(failure.answer)
            if failure.kind != "rate-limit":
                raise
            if waits >= github.refusal_retries():
                raise RateLimitPersists(f"dispatch.sh: reading {path} failed: {' '.join(detail.split())}\n")
            reset = github.rate_limit_reset(subprocess.run)
            if reset is None:
                raise
            waits += 1
            time.sleep(max(0, reset - time.time()))


def comment_bodies(issue):
    """The bodies of issue <issue>'s trusted comments (github.trusted_comment), oldest first: an untrusted one is
    skipped as if absent, so it never decides the exit line."""
    path = f"repos/{{owner}}/{{repo}}/issues/{issue}/comments?per_page=100"
    listed = _read_after_rate_limit(github.gh_rest_list, path)
    comments = json_documents.items(listed)
    return [comment["body"] for comment in comments if github.trusted_comment(comment)]


def last_comment(issue):
    bodies = via("comment_bodies")(issue)
    return bodies[-1] if bodies else ""


def target_repo():
    """The owner/repo this dispatch serves: the main working tree's origin."""
    return workqueue.origin_slug()


def owner_repo(pr_url):
    """The <owner>/<repo> of a https://github.com/<owner>/<repo>/pull/<n> url."""
    return "/".join(pr_url.split("/")[-4:-2])


PR_URL = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/pull/\d+")


def queued_merges():
    """The PR urls of this clone's queued merges for the target repo; one clone serves several repos (#3877); with no readable origin it counts them all, a merge never goes unseen."""
    urls = []
    repo = via("target_repo")()
    mine = os.path.realpath(os.path.join(paths.scripts_of(__file__), "queued-merge.sh"))
    py_mine = os.path.realpath(os.path.join(paths.scripts_of(__file__), "veri", "queued_merge.py"))
    for line in pid_file.argument_lines().splitlines():
        words = line.split()
        if len(words) < 3:
            continue
        script = os.path.realpath(words[1])
        if script == mine or (script == py_mine and os.path.basename(words[0]).startswith("python")):
            # The first PR url among the arguments: --skip-suite puts two words before it, --local-green has none.
            url = next((word for word in words[2:] if PR_URL.fullmatch(word)), None)
            if url and (not repo or owner_repo(url).casefold() == repo.casefold()):
                urls.append(url)
    return urls


def pr_state(pr_url):
    path = f"repos/{owner_repo(pr_url)}/pulls/{pr_url.split('/')[-1]}"
    read = _read_after_rate_limit(github.gh_api, path)
    pull = json.loads(read.stdout)
    if "merged" not in pull:
        return "UNRESOLVED"
    return "MERGED" if pull["merged"] else pull["state"].upper()


def issue_states(issues):
    listed = json.loads(github.gh_issue_list("--state", "all", "--limit", "1000", "--json", "number,state"))
    states = {str(item["number"]): item["state"] for item in listed}
    return {issue: states[issue] for issue in issues if issue in states}


TRANSIENT_RETRY_BOUND = 12


def transient(detail):
    return github.refusal_kind(detail) == "transient"


def answered(what, read, *args, **kwargs):
    """<read>(*args), a gh read; no answer is an unreadable queue naming <what>. A rate limit waits for the reset
    (the caller's), but a read still rate-limited after VERI_GH_REFUSAL_RETRIES waits in a row is a RateLimitPersists."""
    retries = 0
    limited = via("_reads").setdefault("limited", {})
    while True:
        try:
            answer = read(*args, **kwargs)
            limited.pop(what, None)
            return answer
        except github.NoAnswer as failure:
            detail = " ".join((failure.detail or str(failure.answer)).split()) or "no answer"
            if transient(detail) and retries < TRANSIENT_RETRY_BOUND:
                retries += 1
                time.sleep(int(tunables.get("VERI_DISPATCH_RETRY_SLEEP")))
                continue
            unreadable = f"dispatch.sh: reading {what} failed: {detail}\n"
            if github.refusal_kind(detail) == "rate-limit":
                limited[what] = limited.get(what, 0) + 1
                if limited[what] > github.refusal_retries():
                    raise RateLimitPersists(unreadable)
            raise watch_runs.QueueUnreadable(unreadable)


def overlap_poll():
    return tunables.get("VERI_DISPATCH_OVERLAP_POLL", unless_empty=True)


def issue_paths(issue):
    """The backticked words of <issue>'s body: the repo paths it names. Read once per dispatch process."""
    bodies = via("_reads").setdefault("bodies", {})
    if issue not in bodies:
        bodies[issue] = answered(f"issue {issue}'s body", github.gh_issue_view, issue, "body")
    return re.findall(r"`([^`\s]+)`", bodies[issue])


def parked_issues():
    """The numbers of the open issues labelled parked, as strings."""
    listed = answered("the parked issue list", github.gh_issue_list,
                      "--state", "open", "--label", "parked", "--limit", "1000", "--json", "number")
    return {str(item["number"]) for item in json.loads(listed)}


def head_issue(head_ref):
    """The <p> of a run branch tdd/<p>-…, else None."""
    run = re.match(r"tdd/(\d+)-", head_ref or "")
    return run and run.group(1)


def run_prs():
    """(url, number, head sha) of every open run draft PR (head tdd/… in this repository, not a fork's), on any
    machine, listed at most once per VERI_DISPATCH_OVERLAP_POLL seconds. A PR labelled parked, or whose issue
    (the <p> of its tdd/<p>-… head) is, blocks nothing and is left out."""
    reads, clock = via("_reads"), via("clock")
    listed = reads.get("listed")
    if listed is None or clock() - listed[0] >= int(overlap_poll()):
        prs = []
        parked = via("parked_issues")()
        for pr in answered("the open PR list", github.open_pulls,
                           "number,url,isDraft,headRefName,headRefOid,labels,isCrossRepository", limit=None):
            if "parked" in pr.labels or head_issue(pr.head_ref) in parked:
                continue
            if pr.draft is True and pr.head_ref.startswith("tdd/") and not pr.cross_repository:
                url = pr.url or pr.html_url
                reads.setdefault("heads", {})[url] = pr.head_ref
                prs.append((url, pr.number, pr.head_sha))
        listed = reads["listed"] = (clock(), prs)
    return listed[1]


def run_pr_paths():
    """{url: changed paths} of every open run draft PR, each diff read once per head sha."""
    diffs = via("_reads").setdefault("diffs", {})
    changed = {}
    for url, number, sha in run_prs():
        if (url, sha) not in diffs:
            diffs[(url, sha)] = answered(f"{url}'s diff", github.gh_pr_diff_names, number)
        changed[url] = diffs[(url, sha)]
    return changed


def overlap(issue, changed):
    """(path, PR url) of the first path <issue> names that an open run draft PR in <changed> changes, else None."""
    return next(((path, url) for path in via("issue_paths")(issue) for url, files in changed.items()
                 if path in files and not (via("_reads").get("heads", {}).get(url) or "").startswith(f"tdd/{issue}-")),
                None)


def launchable(issue, changed, reported, world=None):
    """Whether <issue> overlaps no open run draft PR; a skip prints one line naming the issue, the path and the PR,
    once per (issue, path, PR) in <reported>, the skips this dispatch process already printed."""
    world = via("World")() if world is None else world
    found = world.overlap(issue, changed)
    if found and (issue, *found) not in reported:
        reported.add((issue, *found))
        world.say(f"skip {issue} {found[0]} {found[1]}\n")
    return not found


def exit_line(issue):
    body = via("last_comment")(issue)
    if not body.startswith(("### ⛔ Bailed", "### ✅ Done")):
        bodies = via("comment_bodies")(issue)
        if len(bodies) > 1:
            body = bodies[-2]
    heading = next(iter(body.splitlines()), "")
    if heading.startswith("### ⛔ Bailed"):
        return f"bail {issue}"
    if not heading.startswith("### ✅ Done"):
        return f"silent-exit {issue}"
    return f"done {issue} {heading.split()[-1]}"


def say(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def parse_args(argv):
    if (
        not argv
        or not via("stall_window")().isdigit()
        or not via("overlap_poll")().isdigit()
        or len(argv) != 2
        or argv[0] != "--target"
        or not argv[1].isdigit()
    ):
        return None
    return int(argv[1])


def prioritize(free, lines):
    named_before = set()
    for named in role_state.State(lines).override_numbers():
        if named in free and named not in named_before:
            named_before.add(named)
            free.remove(named)
            free.insert(0, named)
    return free
