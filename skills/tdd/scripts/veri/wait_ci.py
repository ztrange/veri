"""wait-ci.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import base64
import json
import os
import re
import subprocess
import sys
import traceback
from datetime import datetime

try:
    from github import NoAnswer, _gh, gh_api, gh_rest_list
    from json_documents import documents
    import tunables
except ImportError:
    from .github import NoAnswer, _gh, gh_api, gh_rest_list
    from .json_documents import documents
    from . import tunables

USAGE = "usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]"
PASSING = ("success", "neutral", "skipped")
SLICE_CAP = 540
CEILING = 600
UNREAD_LIMIT = 3
RETRY_CAP = 60


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


def decimal(text):
    return str(int(text)) if re.fullmatch(r"[0-9]+", text) else None


def capped(value, cap, scope):
    return cap if arith(value, scope) > cap else value


def fall_back(why):
    warn("%s; bounding the wait at %s s" % (why, SLICE_CAP))
    return str(SLICE_CAP)


def ci_bound(repo, n=5):
    pages = ""
    for c in ("success", "failure"):
        run = _gh("run", "list", "--repo", repo, "--workflow", "CI", "--status", c,
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


def pr_head(repo, pr):
    run = gh_api("repos/%s/pulls/%s" % (repo, pr.rsplit("/pull/", 1)[-1]))
    if run.returncode != 0:
        return None, "", False
    pull = json.loads(run.stdout)
    return pull.get("mergeable"), pull["head"]["sha"] or "", bool(pull.get("draft"))


def sha_state(repo, sha):
    runs = gh_rest_list("repos/%s/commits/%s/check-runs" % (repo, sha), r'"check_runs": *\[ *\]')
    status = gh_api("repos/%s/commits/%s/status" % (repo, sha), stderr=subprocess.PIPE)
    if status.returncode != 0:
        sys.stderr.write(status.stderr or "")
        refused = re.search(r"HTTP (4\d\d)", status.stderr or "")
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


def trigger_lines(text):
    indent = None
    for line in text.splitlines():
        if not line.strip():
            continue
        depth = len(line) - len(line.lstrip(" "))
        if indent is not None and depth > indent:
            yield line
            continue
        indent = depth if line.lstrip(" ").startswith("on:") else None
        if indent is not None:
            yield line


def unreadable(what):
    warn("could not read the checks of %s" % what)
    return 2


def epoch():
    return int(subprocess.run(["date", "+%s"], stdout=subprocess.PIPE, text=True).stdout)


def deadline_mark(key):
    return ".tdd/ci-deadline-" + key


def before_deadline(mark):
    try:
        with open(mark) as found:
            limit = int(found.read())
    except (OSError, ValueError):
        return False
    return epoch() < limit


def retry_sleep(poll, unread):
    try:
        return "%g" % min(RETRY_CAP, float(poll) * 2 ** (unread - 1))
    except ValueError:
        return poll


def record(mark, deadline):
    try:
        with open(mark, "w") as out:
            out.write("%s\n" % deadline)
    except OSError as error:
        warn(error)


def first_sighting(mark, now):
    try:
        with open(mark) as found:
            return int(found.read())
    except (OSError, ValueError):
        record(mark, now)
        return now


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    explicit = bool(tunables.read("VERI_CI_ON_PR"))
    on_pr = tunables.read("VERI_CI_ON_PR", unless_empty="1")
    if on_pr not in ("0", "1"):
        warn("VERI_CI_ON_PR '%s' is not 0 or 1" % on_pr)
        return 2
    backoff = tunables.read("VERI_CI_RETRY_BACKOFF", unless_empty="1")
    if backoff not in ("0", "1"):
        warn("VERI_CI_RETRY_BACKOFF '%s' is not 0 or 1" % backoff)
        return 2
    no_run_wait = tunables.read("VERI_CI_NO_RUN_WAIT", unless_empty="120")
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
    deadline = ""
    slice_end = None
    unread = 0
    first_none = None
    none_head = None
    while True:
        draft = False
        try:
            mergeable, head, draft = pr_head(repo, pr)
        except Exception:
            traceback.print_exc()
            head = ""
        state = None
        failed = ""
        queued = False
        if head:
            try:
                state, failed, queued = sha_state(repo, head)
            except NoAnswer as error:
                if str(error) == "permanent":
                    return unreadable(head)
            except Exception:
                traceback.print_exc()
        if state is None:
            unread += 1
            key = want or head
            if key and not draft and not os.path.exists(deadline_mark(key)):
                record(deadline_mark(key), str(epoch() + arith(total, scope)))
            if unread >= UNREAD_LIMIT and not before_deadline(deadline_mark(want or head)):
                return unreadable(head or pr)
            subprocess.run(["sleep", retry_sleep(poll, unread) if backoff == "1" else poll])
            continue
        unread = 0
        if state in ("none", "skipped") and mergeable is False:
            warn("%s conflicts with its base branch; no workflow will start until it is rebased" % pr)
            return 2
        mismatched = bool(want and head != want)
        if state == "none" and on_pr == "0" and not mismatched:
            warn("%s has no checks and VERI_CI_ON_PR=0 says none will come" % pr)
            return 0
        if state == "none" and not explicit and no_pull_request_workflow(repo, head):
            warn("%s has no checks and no workflow triggers on pull_request; no check will come" % pr)
            return 0
        none = state == "none"
        if state == "skipped":
            state = "pending"
        if mismatched:
            state = "pending"
        if state == "green":
            return 0
        if state == "red":
            if failed:
                print(failed)
            return 1
        now = epoch()
        scope["now"] = now
        if none and mergeable:
            if none_head != head:
                none_head = head
                first_none = first_sighting(".tdd/ci-none-" + head, now)
            if now - first_none >= int(no_run_wait):
                warn("no CI run for %s" % head)
                return 2
        if slice_end is None:
            try:
                slice_end = now + arith(span, scope)
                if mismatched and os.path.dirname(deadline_mark(want)) != ".tdd":
                    warn("head-sha %s cannot name a deadline file" % want)
            except ArithError as error:
                warn(error)
                break
        if queued and not mismatched:
            first = first_sighting(".tdd/ci-queued-" + (want or head), now)
            if now - first > int(tunables.read("VERI_CI_QUEUE_WAIT", unless_empty="3600")):
                warn("checks of %s never started: queued since %s" % (pr, first))
                return 2
        if mismatched or queued:
            if now >= slice_end:
                break
            subprocess.run(["sleep", poll])
            continue
        if not deadline:
            try:
                key = want or head
                mark = deadline_mark(key)
                inherited = os.path.exists(mark)
                if inherited:
                    try:
                        with open(mark) as found:
                            deadline = found.read().rstrip("\n")
                    except OSError:
                        deadline = ""
                    deadline = decimal(deadline)
                    if deadline is None:
                        warn("deadline file %s is unreadable or not a non-negative whole number" % mark)
                        return 2
                elif draft:
                    warn("%s is a draft; mark it ready before waiting on its checks" % pr)
                    return 2
                else:
                    deadline = str(now + arith(total, scope))
                    record(mark, deadline)
            except ArithError as error:
                warn(error)
                break
        if now >= arith(deadline, scope):
            if inherited:
                warn("checks of %s still pending past the deadline recorded for %s" % (pr, key))
                return 2
            break
        if now >= slice_end:
            break
        subprocess.run(["sleep", poll])
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
