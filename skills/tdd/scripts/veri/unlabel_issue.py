"""unlabel-issue.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import functools
import json
import os
import subprocess
import sys
import urllib.parse

import entry
import tunables

import github
import pointer_comment
import run_dir


_refuse = functools.partial(entry.refuse, prefix="unlabel-issue.sh: ")


USAGE = "usage: unlabel-issue.sh <issue-number>"


def main(argv):
    if len(argv) != 1:
        return entry.refuse(usage="usage: unlabel-issue.sh <issue-number>")
    if not argv[0].isdecimal():
        return _refuse("issue number must be numeric, got '%s'" % argv[0])
    opt_in = tunables.get("VERI_LABEL")
    label = urllib.parse.quote(opt_in, safe="")
    read = github.gh_api("repos/{owner}/{repo}/issues/%s/labels" % argv[0], stderr=subprocess.PIPE)
    if read.returncode != 0:
        return _refuse("no answer to reading the labels of issue #%s: %s" % (argv[0], read.stderr.strip()))
    names = [item["name"] for item in json.loads(read.stdout)]
    taken = tunables.taken_label(opt_in)
    held = [name for name in names if name.startswith("taken:")]
    # A re-claim: this lane's own label with no ledger means a prior launch claimed and died before planning.
    reclaim = taken in held and not os.path.exists(run_dir.ledger(os.getcwd(), argv[0]))
    if held and not (reclaim and held == [taken]):
        return _refuse("issue #%s already carries %s" % (argv[0], ", ".join(held)))
    if opt_in not in names and not reclaim:
        return _refuse("issue #%s lacks the opt-in label %s" % (argv[0], opt_in))
    if opt_in in names:
        run = github.gh_api_delete("repos/{owner}/{repo}/issues/%s/labels/%s" % (argv[0], label))
        if run.returncode != 0 and "404" not in run.stderr:
            if "HTTP" in run.stderr:
                sys.stderr.write(run.stderr)
            else:
                return _refuse("no answer to removing the label from issue #%s: %s" % (argv[0], run.stderr.strip()))
            return 2
        if run.returncode != 0 and "Label does not exist" not in run.stderr:
            return _refuse("issue #%s not found: %s" % (argv[0], run.stderr.strip()))
    run = github.gh_api("repos/{owner}/{repo}/labels/%s" % urllib.parse.quote(taken, safe=""), stderr=subprocess.PIPE)
    if run.returncode != 0 and "404" not in run.stderr:
        return _refuse("no answer to looking up %s for issue #%s: %s" % (taken, argv[0], run.stderr.strip()))
    created = True
    if run.returncode != 0:
        run = github.gh_label_create(taken)
        created = run.returncode == 0 or "already exists" in run.stderr or "already_exists" in run.stdout
    if created:
        run = github.gh_api_add_label("repos/{owner}/{repo}/issues/%s/labels" % argv[0], taken)
    if run.returncode != 0:
        return _refuse("no answer to adding %s to issue #%s: %s" % (taken, argv[0], run.stderr.strip()))
    pointer_comment.mirror(argv[0])
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
