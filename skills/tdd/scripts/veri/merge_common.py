"""The merge call, the settle-window read and the CI wait a landing makes, shared so each merge path makes them alike.

Each function takes the call it makes as an argument (the gate a merge command runs under, the read of the pull
request, the wait-ci.sh call), so a caller keeps its own process seam and this module starts no process itself.
"""
import time

import entry
import tunables


def settle_window():
    """(reads, sleep) for the settle window from VERI_MERGE_SETTLE_READS (a whole number >= 1) and
    VERI_MERGE_SETTLE_SLEEP (a non-negative number of seconds); a refusal message instead when either is unusable."""
    reads = tunables.get("VERI_MERGE_SETTLE_READS", unless_empty=True)
    sleep = tunables.get("VERI_MERGE_SETTLE_SLEEP", unless_empty=True)
    if entry.whole_number(reads) is None:
        return None, "VERI_MERGE_SETTLE_READS is '%s': expected a whole number of at least 1" % reads
    try:
        seconds = float(sleep)
    except ValueError:
        seconds = -1.0
    if not seconds >= 0 or seconds == float("inf"):
        return None, "VERI_MERGE_SETTLE_SLEEP is '%s': expected a non-negative number of seconds" % sleep
    return (entry.whole_number(reads), seconds), None


def merge(gate, pr, repo, number, head, driver=None):
    """The exit code of merging <pr> (pull request <number> of <repo>) at <head> by rebase, each command run as
    gate(*argv): `gh pr merge` under the graphql driver, it then one REST PUT when it fails under auto, else the REST
    PUT alone. The driver is <driver> when given, else VERI_GH_DRIVER."""
    gh_merge = ("gh", "pr", "merge", pr, "--rebase", "--match-head-commit", head)
    rest_merge = ("gh", "api", "-X", "PUT", "repos/%s/pulls/%s/merge" % (repo, number),
                  "-f", "merge_method=rebase", "-f", "sha=%s" % head)
    driver = tunables.get("VERI_GH_DRIVER") if driver is None else driver
    if driver == "graphql":
        return gate(*gh_merge)
    if driver == "auto":
        code = gate(*gh_merge)
        return gate(*rest_merge) if code else code
    return gate(*rest_merge)


def merged(pull):
    """Whether a read of a pull request answered merged: true."""
    return bool(pull) and pull.get("merged") is True


def settle(read, window, wait_first=False):
    """The answers of read() over the settle <window> (reads, sleep), in order, ending at the first that reads merged:
    a sleep between two reads, and before the first when <wait_first>."""
    reads, sleep = window
    answers = []
    for attempt in range(reads):
        if wait_first or attempt:
            time.sleep(sleep)
        answers.append(read())
        if merged(answers[-1]):
            break
    return answers


def ci_wait(wait):
    """wait()'s exit code once it answers other than 3, wait-ci.sh's "not settled yet": it is called again on a 3."""
    code = 3
    while code == 3:
        code = wait()
    return code
