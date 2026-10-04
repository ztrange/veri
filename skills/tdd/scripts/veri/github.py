"""veri's GitHub access: lib/github.sh's GraphQL→REST fallback, run through gh."""
import json
import os
import re
import subprocess
import sys


class NoAnswer(Exception):
    def __init__(self, answer):
        self.answer = answer


def _gh(*args, stderr=None):
    return subprocess.run(["gh", *args], stdout=subprocess.PIPE, stderr=stderr, text=True)


def _gh_graphql(*args):
    return _gh(*args, stderr=subprocess.DEVNULL)


def _gh_api(path):
    return _gh("api", path)


_ISSUES = "repos/{owner}/{repo}/issues"


def _issue(number):
    return "%s/%s" % (_ISSUES, number)


class RestAdapter:
    def list(self, path, empty=r"^\[\]$"):
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

    def issue_view(self, number, field):
        rest = _gh_api(_issue(number))
        try:
            issue = json.loads(rest.stdout)
        except json.JSONDecodeError as error:
            print("json.decoder.JSONDecodeError: %s" % error, file=sys.stderr)
            raise NoAnswer("")
        if rest.returncode != 0:
            raise NoAnswer("")
        if field == "labels":
            return "".join(label["name"] + "\n" for label in issue["labels"])
        return (issue["body"] or "") + "\n"


def gh_rest_list(path, empty=r"^\[\]$"):
    return RestAdapter().list(path, empty)


def gh_list(path, *args):
    run = _gh_graphql(*args)
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
    run = _gh_graphql("issue", "view", number, "--json", field, "-q", query)
    if run.returncode != 0:
        return RestAdapter().issue_view(number, field)
    return run.stdout


def gh_issue_edit(number, body_file):
    run = _gh("api", "-X", "PATCH", _issue(number), "-F", "body=@%s" % body_file)
    if run.returncode != 0:
        raise NoAnswer("")


def gh_issue_create(title, body):
    run = _gh("api", _ISSUES, "-f", "title=%s" % title,
              "-f", "body=%s" % body, "-q", ".html_url")
    if run.returncode != 0:
        raise NoAnswer("")
    return run.stdout
