"""wait-ci.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import base64
import json
import re
import subprocess
import sys
import time
import traceback
from dataclasses import replace
from datetime import datetime

import github
from github import NoAnswer, run_gh, gh_api, gh_rest_list
from json_documents import documents
import tunables
import ci_marks
from ci_decision import Crash, Loop, Need, Observation, Options, Record, Sleep, UNREAD_LIMIT, decide, decimal, retry_sleep
from ci_on_pr import declared, trigger_lines

USAGE = "usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha] | --fresh-window <head-sha>"
PASSING = ("success", "neutral", "skipped")
SLICE_CAP = 540
CEILING = 600
RUN = ""


def warn(message):
    print("wait-ci.sh: %s" % message, file=sys.stderr)


class ArithError(ValueError):
    pass


def arith(text, scope):
    word = str(text).strip()
    if not word:
        return 0
    sign = -1 if word[0] == "-" else 1
    body = word[1:] if word[0] == "-" else word
    if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", body):
        if body not in scope:
            raise NameError("%s: unbound variable" % body)
        value = arith(scope[body], scope)
    elif re.fullmatch(r"0[xX][0-9a-fA-F]+", body):
        value = int(body, 16)
    elif re.fullmatch(r"0[0-7]*", body):
        value = int(body, 8)
    elif re.fullmatch(r"0[0-9]+", body):
        raise ArithError('%s: value too great for base (error token is "%s")' % (word, body))
    elif re.fullmatch(r"[1-9][0-9]*", body):
        value = int(body)
    else:
        raise ArithError('%s: syntax error: invalid arithmetic operator (error token is "%s")' % (word, body))
    return sign * value


def capped(value, cap, scope):
    return cap if arith(value, scope) > cap else value


def fall_back(why):
    warn("%s; bounding the wait at %s s" % (why, SLICE_CAP))
    return str(SLICE_CAP)


def ci_bound(repo, n=5):
    pages = ""
    for c in ("success", "failure"):
        run = run_gh("run", "list", "--repo", repo, "--workflow", "CI", "--status", c,
                  "--limit", str(n), "--json", "databaseId,conclusion,startedAt,updatedAt")
        if run.returncode != 0:
            return fall_back("gh run list could not answer")
        pages += run.stdout.rstrip("\n")
    at = lambda s: datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").timestamp()
    runs = sorted((r for page in documents(pages) for r in page),
                  key=lambda r: r["databaseId"], reverse=True)[:n]
    if len(runs) < n:
        return fall_back("fewer than %d success or failure CI runs found" % n)
    return str(min(CEILING, round(2 * sum(at(r["updatedAt"]) - at(r["startedAt"]) for r in runs) / len(runs))))


def pr_head(repo, pr, on_limit=None):
    run = gh_api("repos/%s/pulls/%s" % (repo, pr.rsplit("/pull/", 1)[-1]), stderr=subprocess.PIPE)
    if run.returncode != 0:
        sys.stderr.write(run.stderr or "")
        if on_limit:
            on_limit(run.stderr or "", False)
        return None, "", False
    pull = json.loads(run.stdout)
    return pull.get("mergeable"), pull["head"]["sha"] or "", bool(pull.get("draft"))


def sha_state(repo, sha, on_limit=None, draft=False):
    try:
        runs = gh_rest_list("repos/%s/commits/%s/check-runs" % (repo, sha), r'"check_runs": *\[ *\]')
    except NoAnswer as error:
        if on_limit:
            on_limit(error.detail or "", draft)
        raise
    status = gh_api("repos/%s/commits/%s/status" % (repo, sha), stderr=subprocess.PIPE)
    if status.returncode != 0:
        sys.stderr.write(status.stderr or "")
        refused = re.search(r"HTTP (4\d\d)", status.stderr or "")
        if on_limit:
            on_limit(status.stderr or "", draft)
        raise NoAnswer("permanent" if refused and refused.group(1) not in ("403", "429") else "")
    statuses = status.stdout
    docs = documents(runs + statuses)
    states = [s["state"] for s in docs[-1].get("statuses") or []]
    check_runs = [r for p in docs[:-1] for r in p.get("check_runs") or []]
    outcomes = [r.get("conclusion") if r.get("status") == "completed" else None for r in check_runs]
    failed = [r.get("name", "") for r in check_runs
              if r.get("conclusion") and r["conclusion"].lower() not in PASSING]
    if any(o is not None and o not in PASSING for o in outcomes) \
            or any(s in ("failure", "error") for s in states):
        return "red", ",".join(failed), False
    if not check_runs and not states:
        return "none", "", False
    only_skipped = all(o == "skipped" for o in outcomes)
    if only_skipped and not states:
        return "skipped", "", False
    if None in outcomes or only_skipped or "pending" in states:
        statuses_of = [r.get("status") for r in check_runs]
        return "pending", "", "queued" in statuses_of and "in_progress" not in statuses_of
    return "green", "", False


def wait_for_reset(stderr, key, draft, total, bound, slice_end=None):
    """On a rate-limit refusal in <stderr>, sleeps until GitHub's reset when it falls before the CI deadline
    (the key's mark, else the one made now and recorded unless a draft); raises NoAnswer("permanent") when it
    falls at or past it. An unknown reset, or any other refusal, returns for the caller's backoff retry."""
    if "rate limit" not in stderr:
        return
    reset = github.rate_limit_reset(subprocess.run)
    if reset is None:
        return
    limit = ci_marks.seconds(RUN, "deadline", key) if key else None
    if limit is None:
        if "limit" not in bound:
            bound["limit"] = epoch() + int(total)
        limit = bound["limit"]
        if key and not draft and not ci_marks.exists(RUN, "deadline", key):
            ci_marks.record(RUN, "deadline", key, limit)
    if reset >= limit:
        warn("GitHub rate limit resets at %s, past the CI deadline %s" % (reset, limit))
        raise NoAnswer("permanent")
    if slice_end is not None and reset > slice_end:
        time.sleep(max(0, slice_end - epoch()))
        raise NoAnswer("slice")
    time.sleep(max(0, reset - epoch()))


def no_pull_request_workflow(repo, head):
    root = "repos/%s/contents/.github/workflows" % repo
    listing = gh_api("%s?ref=%s" % (root, head), stderr=subprocess.PIPE)
    if "HTTP 404" in (listing.stderr or ""):
        return True
    try:
        entries = json.loads(listing.stdout)
    except ValueError:
        return False
    for entry in entries:
        run = gh_api("%s/%s?ref=%s" % (root, entry["name"], head), stderr=subprocess.PIPE)
        if run.returncode != 0:
            return False
        text = base64.b64decode(json.loads(run.stdout)["content"]).decode()
        if any("pull_request" in line for line in trigger_lines(text)):
            return False
    return True


def unreadable(what):
    warn("could not read the checks of %s" % what)
    return 2


def epoch():
    return int(subprocess.run(["date", "+%s"], stdout=subprocess.PIPE, text=True).stdout)


def before_deadline(key):
    limit = ci_marks.seconds(RUN, "deadline", key)
    return limit is not None and epoch() < limit


def main(argv):
    if len(argv) == 2 and argv[0] == "--fresh-window":
        ci_marks.fresh_window(RUN, argv[1])
        return 0
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        stated = declared()
    except ValueError as refusal:
        warn(str(refusal))
        return 2
    explicit = bool(stated)
    on_pr = stated or "1"
    backoff = tunables.read("VERI_CI_RETRY_BACKOFF", unless_empty="1")
    if backoff not in ("0", "1"):
        warn("VERI_CI_RETRY_BACKOFF '%s' is not 0 or 1" % backoff)
        return 2
    no_run_wait = tunables.read("VERI_CI_NO_RUN_WAIT", unless_empty="600")
    if not re.fullmatch(r"[0-9]+", no_run_wait):
        warn("VERI_CI_NO_RUN_WAIT '%s' is not a non-negative whole number" % no_run_wait)
        return 2
    pr = argv[0]
    repo = pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]
    want = argv[3] if len(argv) > 3 else ""
    if want and not re.fullmatch(r"[0-9a-f]{40}", want):
        warn("head-sha '%s' is not a full 40-hex sha; a full 40-hex sha is required" % want)
        return 2
    scope = {}
    numbers = []
    for which, given in zip(("slice-seconds", "total-seconds"), (argv[1:3] + ["", ""])[:2]):
        value = decimal(given) if given else ""
        if value is None:
            warn("%s '%s' is not a non-negative whole number" % (which, given))
            return 2
        numbers.append(value)
    slice_arg, total = numbers
    span = capped(slice_arg or str(SLICE_CAP), SLICE_CAP, scope)
    if total:
        total = capped(total, CEILING, scope)
    else:
        try:
            total = ci_bound(repo)
        except Exception:
            traceback.print_exc()
            total = span
    poll = tunables.read("VERI_POLL", unless_empty="10")
    options = Options(pr=pr, want=want, explicit=explicit, on_pr=on_pr, no_run_wait=int(no_run_wait),
                      queue_wait=tunables.read("VERI_CI_QUEUE_WAIT", unless_empty="3600"), poll=poll,
                      span=arith(span, scope), total=arith(total, scope))
    bound = {}
    call_end = epoch() + options.span
    loop = Loop()
    unread = 0
    while True:
        draft = False
        try:
            mergeable, head, draft = pr_head(
                repo, pr, lambda err, is_draft: wait_for_reset(err, want, is_draft, total, bound, call_end))
        except NoAnswer as error:
            if str(error) == "permanent":
                return unreadable(want or pr)
            if str(error) == "slice":
                return 3
            head = ""
        except Exception:
            traceback.print_exc()
            head = ""
        state = None
        failed = ""
        queued = False
        if head:
            try:
                state, failed, queued = sha_state(
                    repo, head, lambda err, is_draft: wait_for_reset(err, want or head, is_draft, total, bound, call_end), draft)
            except NoAnswer as error:
                if str(error) == "permanent":
                    return unreadable(head)
                if str(error) == "slice":
                    return 3
            except Exception:
                traceback.print_exc()
        if state is None:
            unread += 1
            key = want or head
            if key and not draft and not ci_marks.exists(RUN, "deadline", key):
                ci_marks.record(RUN, "deadline", key, epoch() + options.total)
            if unread >= UNREAD_LIMIT and not before_deadline(want or head):
                return unreadable(head or pr)
            subprocess.run(["sleep", retry_sleep(poll, unread, backoff)])
            continue
        unread = 0
        observation = Observation(state, head, failed, queued, mergeable, draft)
        marks = ci_marks.load(RUN, want or head, head)
        now = None
        while True:
            decision = decide(observation, marks, now, loop, options)
            if not isinstance(decision.outcome, Need):
                break
            if decision.outcome.what == "workflow":
                observation = replace(observation, no_workflow=no_pull_request_workflow(repo, head))
            else:
                now = epoch()
        loop = decision.loop
        for effect in decision.effects:
            if isinstance(effect, Record):
                ci_marks.record(RUN, effect.kind, effect.key, effect.value)
            else:
                ci_marks.remove(RUN, effect.kind, effect.key)
        outcome = decision.outcome
        if isinstance(outcome, Crash):
            raise outcome.error
        if isinstance(outcome, Sleep):
            subprocess.run(["sleep", outcome.seconds])
            continue
        sys.stdout.write(outcome.out)
        sys.stderr.write(outcome.err)
        return outcome.code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
