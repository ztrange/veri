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


def _gh_api(path):
    return _gh("api", path)


_ISSUES = "repos/{owner}/{repo}/issues"


def _issue(number):
    return "%s/%s" % (_ISSUES, number)


class GraphQLAdapter:
    def _run(self, *args):
        run = _gh(*args, stderr=subprocess.DEVNULL)
        if run.returncode != 0:
            raise NoAnswer("")
        return run.stdout

    def list(self, *args):
        return self._run(*args)

    def issue_view(self, number, field):
        query = ".body" if field == "body" else ".labels[].name"
        return self._run("issue", "view", number, "--json", field, "-q", query)


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

    def issue_edit(self, number, body_file):
        run = _gh("api", "-X", "PATCH", _issue(number), "-F", "body=@%s" % body_file)
        if run.returncode != 0:
            raise NoAnswer("")

    def issue_create(self, title, body):
        run = _gh("api", _ISSUES, "-f", "title=%s" % title,
                  "-f", "body=%s" % body, "-q", ".html_url")
        if run.returncode != 0:
            raise NoAnswer("")
        return run.stdout


class FallbackAdapter:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def list(self, path, *args):
        try:
            return self.first.list(*args)
        except NoAnswer:
            return self.second.list(path)

    def rest_list(self, path, empty=r"^\[\]$"):
        return self.second.list(path, empty)

    def issue_view(self, number, field):
        try:
            return self.first.issue_view(number, field)
        except NoAnswer:
            return self.second.issue_view(number, field)

    def issue_edit(self, number, body_file):
        self.second.issue_edit(number, body_file)

    def issue_create(self, title, body):
        return self.second.issue_create(title, body)

    def json(self, fixture, path, *args):
        if args:
            return self.list(path, *args)
        return self.rest_list(path)


class NoRouteAdapter:
    def list(self, *args):
        raise NoAnswer("")

    def issue_view(self, number, field):
        raise NoAnswer("")


class FixtureAdapter:
    def __init__(self, directory):
        self.directory = directory

    def json(self, fixture, path, *args):
        with open(os.path.join(self.directory, fixture)) as f:
            return f.read()


def _select(operation):
    fixtures = os.environ.get("VERI_GH_JSON")
    if operation == "json" and fixtures:
        return FixtureAdapter(fixtures)
    first = GraphQLAdapter() if os.environ.get("VERI_GH_DRIVER") == "auto" else NoRouteAdapter()
    return FallbackAdapter(first, RestAdapter())


def gh_rest_list(path, empty=r"^\[\]$"):
    return _select("rest_list").rest_list(path, empty)


def gh_list(path, *args):
    return _select("list").list(path, *args)


def gh_json(fixture, path, *args):
    return _select("json").json(fixture, path, *args)


def gh_issue_view(number, field):
    return _select("issue_view").issue_view(number, field)


def gh_issue_edit(number, body_file):
    _select("issue_edit").issue_edit(number, body_file)


def gh_issue_create(title, body):
    return _select("issue_create").issue_create(title, body)
