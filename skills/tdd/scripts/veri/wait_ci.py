"""wait-ci.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
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
    status = gh_api("repos/%s/commits/%s/status" % (repo, sha))
    if status.returncode != 0:
        raise NoAnswer("")
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


OPENING_TYPES = {"opened", "synchronize", "reopened", "ready_for_review"}


def on_region(text):
    lines = [re.sub(r"(^|\s)#.*", "", line) for line in text.splitlines()]
    for i, line in enumerate(lines):
        head = re.match(r"['\"]?on['\"]?\s*:", line)
        if head:
            region = [line[head.end():]]
            for more in lines[i + 1:]:
                if re.match(r"\w", more):
                    break
                region.append(more)
            return region
    return None


def trigger_block(region, row, col):
    rest = region[row][col:]
    if rest.lstrip().startswith("{"):
        flat = "\n".join([rest] + region[row + 1:])
        start, depth = flat.index("{"), 0
        for pos in range(start, len(flat)):
            depth += {"{": 1, "}": -1}.get(flat[pos], 0)
            if depth == 0:
                break
        return flat[start:pos + 1]
    indent = len(region[row]) - len(region[row].lstrip())
    block = [rest]
    for more in region[row + 1:]:
        if more.strip() and len(more) - len(more.lstrip()) <= indent:
            break
        block.append(more)
    return "\n".join(block)


def opens_checks(text):
    region = on_region(text)
    if re.search(r"[\x00-\x08\x0e-\x1f]", text):
        return True
    if region is None:
        return False
    if region[0].lstrip().startswith("!"):
        return True
    for row, line in enumerate(region):
        for key in re.finditer(r"pull_request(?:_target)?", line):
            colon = re.match(r"\s*:", line[key.end():])
            if not colon:
                return True
            block = trigger_block(region, row, key.end() + colon.end())
            named = re.search(r"\btypes:(.*(?:\n\s*-.*)*)", block)
            if not named or OPENING_TYPES.intersection(re.findall(r"[\w-]+", named.group(1))):
                return True
    return False


def runs_on_pull_requests(repo, sha):
    listing = gh_api("repos/%s/contents/.github/workflows?ref=%s" % (repo, sha),
                      stderr=subprocess.DEVNULL)
    if listing.returncode != 0:
        try:
            return json.loads(listing.stdout).get("message") != "Not Found"
        except (ValueError, AttributeError):
            return True
    try:
        entries = json.loads(listing.stdout)
    except ValueError:
        return True
    for entry in entries:
        body = _gh("api", "-H", "Accept: application/vnd.github.raw",
                   "repos/%s/contents/%s?ref=%s" % (repo, entry["path"], sha),
                   stderr=subprocess.DEVNULL)
        if body.returncode != 0 or opens_checks(body.stdout):
            return True
    return False


def unreadable(what):
    warn("could not read the checks of %s" % what)
    return 2


def record(mark, deadline):
    try:
        with open(mark, "w") as out:
            out.write("%s\n" % deadline)
    except OSError as error:
        warn(error)


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    pr = argv[0]
    repo = pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]
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
    want = argv[3] if len(argv) > 3 else ""
    poll = tunables.read("VERI_POLL", unless_empty="10")
    deadline = ""
    slice_end = None
    unread = 0
    while True:
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
            except NoAnswer:
                pass
            except Exception:
                traceback.print_exc()
        if state is None:
            unread += 1
            if unread >= UNREAD_LIMIT:
                return unreadable(head or pr)
            subprocess.run(["sleep", poll])
            continue
        unread = 0
        if state in ("none", "skipped") and mergeable is False:
            warn("%s conflicts with its base branch; no workflow will start until it is rebased" % pr)
            return 2
        if state == "skipped":
            state = "pending"
        mismatched = bool(want and head != want)
        if mismatched:
            state = "pending"
        if state == "green":
            return 0
        if state == "red":
            if failed:
                print(failed)
            return 1
        now = int(subprocess.run(["date", "+%s"], stdout=subprocess.PIPE, text=True).stdout)
        scope["now"] = now
        if slice_end is None:
            try:
                slice_end = now + arith(span, scope)
                if mismatched and os.path.dirname(".tdd/ci-deadline-" + want) != ".tdd":
                    warn("head-sha %s cannot name a deadline file" % want)
            except ArithError as error:
                warn(error)
                break
        if queued and not mismatched:
            seen = ".tdd/ci-queued-" + (want or head)
            try:
                with open(seen) as found:
                    first = int(found.read())
            except (OSError, ValueError):
                first = now
                record(seen, now)
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
                mark = ".tdd/ci-deadline-" + key
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
                elif state == "none" and not runs_on_pull_requests(repo, head):
                    warn("%s reports no checks and no workflow runs on pull requests" % pr)
                    return 4
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
