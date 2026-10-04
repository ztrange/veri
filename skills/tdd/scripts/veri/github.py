"""veri's GitHub access: lib/github.sh's GraphQL→REST fallback, run through gh."""
import json
import os
import re
import subprocess


class NoAnswer(Exception):
    def __init__(self, answer):
        self.answer = answer


def _gh_api(path):
    return subprocess.run(["gh", "api", path], stdout=subprocess.PIPE, text=True)


def _issue(number):
    return "repos/{owner}/{repo}/issues/%s" % number


def gh_rest_list(path, empty=r"^\[\]$"):
    answer = ""
    sep = "&" if "?" in path else "?"
    page = 1
    while True:
        run = _gh_api("%s%spage=%d" % (path, sep, page))
        if run.returncode != 0:
            raise NoAnswer(answer)
        body = run.stdout.rstrip("\n")
        if re.search(empty, body):
            return answer
        answer += body
        page += 1


def gh_list(path, *args):
    run = subprocess.run(["gh", *args], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True)
    if run.returncode != 0:
        return gh_rest_list(path)
    return run.stdout


def gh_json(fixture, path, *args):
    fixtures = os.environ.get("VERI_GH_JSON")
    if not fixtures:
        if args:
            return gh_list(path, *args)
        return gh_rest_list(path)
    with open(os.path.join(fixtures, fixture)) as f:
        return f.read()


def gh_issue_view(number, field):
    query = ".body" if field == "body" else ".labels[].name"
    run = subprocess.run(["gh", "issue", "view", number, "--json", field, "-q", query],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if run.returncode != 0:
        rest = _gh_api(_issue(number))
        if rest.returncode != 0:
            raise NoAnswer("")
        try:
            issue = json.loads(rest.stdout)
        except ValueError:
            raise NoAnswer("")
        if field == "labels":
            return "".join(label["name"] + "\n" for label in issue["labels"])
        return (issue["body"] or "") + "\n"
    return run.stdout


def gh_issue_edit(number, body_file):
    run = subprocess.run(["gh", "api", "-X", "PATCH", _issue(number),
                          "-F", "body=@%s" % body_file], stdout=subprocess.DEVNULL)
    if run.returncode != 0:
        raise NoAnswer("")
