"""veri's GitHub access through gh, the Python twin of lib/github.sh.

VERI_GH_DRIVER picks the route an operation with a GraphQL route takes (gh_issue_view,
gh_list, gh_json with gh args): rest, the default when unset, runs only `gh api`; graphql
runs only the gh porcelain command, with no fallback; auto tries GraphQL, then REST. Set
but empty, or any other value, raises NoAnswer at call time with a stderr line naming the
variable and the value. Operations with no GraphQL route (issue edit and create,
gh_rest_list, gh_json with no gh args) use REST under every value, and VERI_GH_JSON takes
precedence over it. A Claude Code cloud session, where GraphQL is refused, needs nothing set.
"""
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
_EMPTY_PAGE = r"^\[\]$"


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
    def list(self, path, empty=_EMPTY_PAGE):
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


class RestOnlyAdapter:
    def __init__(self):
        self.rest = RestAdapter()

    def list(self, path, *args):
        return self.rest.list(path)

    def rest_list(self, path, empty=_EMPTY_PAGE):
        return self.rest.list(path, empty)

    def issue_view(self, number, field):
        return self.rest.issue_view(number, field)

    def issue_edit(self, number, body_file):
        self.rest.issue_edit(number, body_file)

    def issue_create(self, title, body):
        return self.rest.issue_create(title, body)

    def json(self, fixture, path, *args):
        if args:
            return self.list(path, *args)
        return self.rest_list(path)

    def page(self, fixture, path, *args):
        run = _gh_api(path)
        if run.returncode != 0:
            raise NoAnswer("")
        return run.stdout


class GraphQLOnlyAdapter(RestOnlyAdapter):
    def __init__(self):
        super().__init__()
        self.graphql = GraphQLAdapter()

    def list(self, path, *args):
        return self.graphql.list(*args)

    def page(self, fixture, path, *args):
        return self.graphql.list(*args)

    def issue_view(self, number, field):
        return self.graphql.issue_view(number, field)


class FallbackAdapter(GraphQLOnlyAdapter):
    def list(self, path, *args):
        try:
            return super().list(path, *args)
        except NoAnswer:
            return RestOnlyAdapter.list(self, path)

    def page(self, fixture, path, *args):
        try:
            return super().page(fixture, path, *args)
        except NoAnswer:
            return RestOnlyAdapter.page(self, fixture, path, *args)

    def issue_view(self, number, field):
        try:
            return super().issue_view(number, field)
        except NoAnswer:
            return RestOnlyAdapter.issue_view(self, number, field)


class FixtureAdapter:
    def __init__(self, directory):
        self.directory = directory

    def json(self, fixture, path, *args):
        with open(os.path.join(self.directory, fixture)) as f:
            return f.read()

    def page(self, fixture, path, *args):
        return self.json(fixture, path, *args)


def _select(operation):
    fixtures = os.environ.get("VERI_GH_JSON")
    if operation == "json" and fixtures:
        return FixtureAdapter(fixtures)
    driver = os.environ.get("VERI_GH_DRIVER", "rest")
    if driver not in ("auto", "rest", "graphql"):
        print("VERI_GH_DRIVER is '%s': expected auto, rest or graphql" % driver, file=sys.stderr)
        raise NoAnswer("")
    if driver == "graphql":
        return GraphQLOnlyAdapter()
    if driver == "auto":
        return FallbackAdapter()
    return RestOnlyAdapter()


def gh_rest_list(path, empty=_EMPTY_PAGE):
    return _select("rest_list").rest_list(path, empty)


def gh_list(path, *args):
    return _select("list").list(path, *args)


def gh_json(fixture, path, *args):
    return _select("json").json(fixture, path, *args)


def gh_json_page(fixture, path, *args):
    return _select("json").page(fixture, path, *args)


def gh_issue_view(number, field):
    return _select("issue_view").issue_view(number, field)


def gh_issue_edit(number, body_file):
    _select("issue_edit").issue_edit(number, body_file)


def gh_issue_create(title, body):
    return _select("issue_create").issue_create(title, body)
