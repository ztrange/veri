"""veri's GitHub access through gh: the one home of gh_pr_ready and every other GitHub call.

VERI_GH_DRIVER picks the route an operation with a GraphQL route takes (gh_pr_ready,
gh_issue_view, gh_list, gh_json with gh args): rest, the default when unset, runs only `gh api`; graphql
runs only the gh porcelain command, with no fallback; auto tries GraphQL, then REST. Set
but empty, or any other value, raises NoAnswer at call time with a stderr line naming the
variable and the value. Operations with no GraphQL route (issue edit and create,
gh_rest_list, gh_json and gh_json_page with no gh args) use REST under every value, and VERI_GH_JSON takes
precedence over it. A Claude Code cloud session, where GraphQL is refused, needs nothing set: the
tree-audit case in skills/tdd/scripts/tests/py/test_gh_porcelain_guard.py holds that claim, refusing gh
issue, gh pr, gh label and gh auth porcelain off the graphql branch.
"""
import contextlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.parse
from typing import NamedTuple, Optional

import entry
import json_documents
import run_records
import tunables
from redaction import redact

PARKED_HEADING = "### ⏸ Parked"
# How every comment veri posts on an issue begins, whichever module posts it (comment.py's kinds, park_issue,
# pointer_comment, preflight_refused, run_conductor's needs-user note): a reader that wants a human's words, not veri's
# own, skips a body starting with one. tests/py/unit/test_veri_comment_prefixes.py fails on a posted heading not here.
VERI_COMMENT_PREFIXES = (
    PARKED_HEADING, "### ▶️ Resuming", "### ⛔ Bailed", "### ✅ Done", "### ✅ Step done", "### 📍 Run state",
    "### ⏹️ Stopped", "### ⛔ Preflight refused", "### 🔴 Red", "### 🟢 Green", "### 🛠️ Refactor", "### 🔎 ",
    "### 🗺️ ", "### 📊 Metrics", "### ♻️ Revise ", "### 📌 Already satisfied", "### 🪦 Retired", "needs-user: the conductor stopped without a verdict.",
)

# An absolute local path redact_local leaves (another account's home, any temp or /private path): to `<path>`, whole,
# from its prefix at a path boundary (`/homepage` is not one) to its last character that is not `,` `.` `;` or `:`.
_LOCAL_PATH = re.compile(run_records.PATH_START + r"(?:/System/Volumes/Data)?(?:/private)?"
                        r"/(?:Users|home|tmp|var/folders|private)" + run_records.PATH_END
                        + r"(?:/[^\s\"'`<>()\[\]]*(?<![,.;:]))?")


_TEMP_SCRIPT = re.compile(r"<tmp>(?:/[^\s/\"'`<>()\[\]]+)+/([\w.-]+\.sh)(?![\w./-])")


def published(text):
    """<text> as a comment veri posts publishes it: this machine's paths, host and account names redacted as a PR body's
    are (`~` for the home directory), then any other absolute local path replaced by `<path>`, save that one ending in a
    `.sh` file keeps that last component (`<path>/run-conductor.sh`); a path redact_local left under `<tmp>` is
    rewritten only when it so ends, else kept as it was."""
    redacted = _TEMP_SCRIPT.sub(r"<path>/\1", run_records.redact_local(text, os.getcwd()))
    return _LOCAL_PATH.sub(_redacted_path, redacted)


def _redacted_path(match):
    script = re.search(r"/([\w.-]+\.sh)$", match.group(0))
    return "<path>/" + script.group(1) if script else "<path>"


class NoAnswer(Exception):
    """<answer>: what was read before the failure; <detail>: gh's stderr for it, when captured."""
    def __init__(self, answer, detail=""):
        self.answer = answer
        self.detail = detail

    @property
    def kind(self):
        """refusal_kind of the detail, else of the answer when that is what carries gh's words."""
        return refusal_kind(self.detail or str(self.answer))


_RATE_LIMIT_MARKERS = ("rate limit",)
_RATE_LIMIT_HEADERS = ("retry-after", "x-ratelimit-remaining: 0")
_TRANSIENT_MARKERS = ("HTTP 5", "error connecting to api.github.com")


def refusal_kind(text):
    """What kind of refusal gh's stderr <text> describes: "rate-limit" (the words `rate limit`, or a
    Retry-After or exhausted X-RateLimit-Remaining header), "transient" (an HTTP 5xx, or no connection
    to api.github.com), else "refused". A rate limit outranks a transient marker in the same text."""
    lowered = text.lower()
    if any(m in text for m in _RATE_LIMIT_MARKERS) or any(m in lowered for m in _RATE_LIMIT_HEADERS):
        return "rate-limit"
    if any(m in text for m in _TRANSIENT_MARKERS):
        return "transient"
    return "refused"


def _gh_api_said(path):
    """gh api <path> with its stderr captured and still written to ours, so a caller can read why it failed."""
    run = gh_api(path, stderr=subprocess.PIPE)
    sys.stderr.write(run.stderr or "")
    return run


def wait_seconds(name, least):
    raw = tunables.get(name)
    value = entry.whole_number(raw, least)
    if value is None:
        print("%s: invalid value %r" % (name, raw), file=sys.stderr)
        raise NoAnswer("")
    return value


def refusal_retries():
    """How many rate-limit refusals a read waits out (VERI_GH_REFUSAL_RETRIES)."""
    return wait_seconds("VERI_GH_REFUSAL_RETRIES", 0)


def bounded(argv, run=None, **kwargs):
    """(run or subprocess.run)(argv, **kwargs), killed after VERI_GH_TIMEOUT seconds and then answered as a failed
    call: exit 124, with a line naming the command and the limit on the stream the caller captures (written to ours
    when it captures none)."""
    limit = wait_seconds("VERI_GH_TIMEOUT", 1)
    with contextlib.ExitStack() as cleanup:
        if argv[0] == "gh":
            argv = _redacted_argv(argv, cleanup)
            if isinstance(kwargs.get("input"), str):
                kwargs["input"] = redact(kwargs["input"])
            elif isinstance(kwargs.get("input"), bytes):
                kwargs["input"] = os.fsencode(redact(os.fsdecode(kwargs["input"])))
        try:
            return (run or subprocess.run)(argv, timeout=limit, **kwargs)
        except subprocess.TimeoutExpired:
            return _timed_out(argv, limit, kwargs)


# The ways a gh command line names a file whose contents gh sends: an option and its value (`--input f`), a long
# option glued with `=` (`--input=f`), and a typed field read from a file (`-F body=@f`, `-Fbody=@f`, `--field body=@f`,
# `--field=body=@f`).
_FILE_OPTIONS = ("--input", "--body-file")
_FIELD_OPTIONS = ("-F", "--field")


def _redacted_argv(argv, cleanup):
    """<argv>, a gh command line, with every argument redacted, and every file it hands gh whose contents hold
    something to redact replaced by a redacted copy in a private directory removed when <cleanup> closes; the files
    themselves are left as they were."""
    copies = _Copies(cleanup)
    out = []
    for flag, arg in zip([None] + list(argv), argv, strict=False):
        if flag in _FILE_OPTIONS:
            out.append(copies.of(arg) or redact(arg))
            continue
        head, path = _named_file(arg, typed=flag in _FIELD_OPTIONS)
        copy = copies.of(path) if path is not None else None
        out.append(redact(head) + copy if copy else redact(arg))
    return out


def _named_file(arg, typed):
    """(what precedes the file, the file) a single argument names, or (arg, None)."""
    for option in _FILE_OPTIONS:
        if arg.startswith(option + "="):
            return option + "=", arg[len(option) + 1:]
    for option in ("-F", "--field="):
        if arg.startswith(option) and "=@" in arg[len(option):]:
            field, _, path = arg[len(option):].partition("=@")
            return option + field + "=@", path
    if typed and "=@" in arg:
        field, _, path = arg.partition("=@")
        return field + "=@", path
    return arg, None


class _Copies:
    """Redacted copies of files, in one directory of their own (mode 0700, made by mkdtemp), removed with it."""

    def __init__(self, cleanup):
        self.cleanup, self.directory = cleanup, None

    def of(self, path):
        """A redacted copy of <path>, or None when it is not a file or holds nothing to redact."""
        if path == "-" or not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8", errors="surrogateescape") as f:
            text = f.read()
        redacted = redact(text)
        if redacted == text:
            return None
        if self.directory is None:
            self.directory = tempfile.mkdtemp(prefix="veri-redacted-")
            self.cleanup.callback(shutil.rmtree, self.directory, True)
        copy = os.path.join(self.directory, "%d-%s" % (len(os.listdir(self.directory)), os.path.basename(path)))
        with open(copy, "w", encoding="utf-8", errors="surrogateescape") as f:
            f.write(redacted)
        return copy


def bounded_group(argv, limit_name="VERI_GH_TIMEOUT", **kwargs):
    """bounded, for a child that starts children of its own (git over ssh): it runs in a session of its own, and at
    <limit_name>'s seconds (VERI_GH_TIMEOUT unless named) its whole process group is killed, so no ssh outlives it.
    Same exit 124 and line, the line naming <limit_name>."""
    limit = wait_seconds(limit_name, 1)
    with subprocess.Popen(argv, start_new_session=True, **kwargs) as child:
        try:
            out, err = child.communicate(timeout=limit)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(child.pid, signal.SIGKILL)
            child.communicate()
            return _timed_out(argv, limit, kwargs, limit_name)
    return subprocess.CompletedProcess(argv, child.returncode, out, err)


class TimedOut(subprocess.CompletedProcess):
    """The answer of a call killed at its bound (exit 124); isinstance tells it from a child that exited 124 itself."""


def _timed_out(argv, limit, kwargs, limit_name="VERI_GH_TIMEOUT"):
    """The failed call a timed-out <argv> is answered as: exit 124, with a line naming the command and the limit on
    the stream the caller captures (written to ours when it captures none)."""
    said = "%s: no answer after %ds (%s)\n" % (" ".join(argv), limit, limit_name)
    stdout = "" if kwargs.get("capture_output") or kwargs.get("stdout") == subprocess.PIPE else None
    if kwargs.get("stderr") == subprocess.STDOUT:
        return TimedOut(argv, 124, said, None)
    if kwargs.get("capture_output") or kwargs.get("stderr") == subprocess.PIPE:
        return TimedOut(argv, 124, stdout, said)
    sys.stderr.write(said)
    return TimedOut(argv, 124, stdout, None)


def run_gh(*args, stderr=None):
    first_miss = None
    while True:
        try:
            return bounded(["gh", *args], stdout=subprocess.PIPE, stderr=stderr, text=True)
        except FileNotFoundError:
            retry_sleep = wait_seconds("VERI_TOOL_RETRY_SLEEP", 1)
            fast_wait = wait_seconds("VERI_TOOL_FAST_WAIT", 0)
            slow_sleep = wait_seconds("VERI_TOOL_SLOW_SLEEP", 1)
            total_wait = wait_seconds("VERI_TOOL_WAIT", 0)
            now = time.monotonic()
            if first_miss is None:
                first_miss = now
            elapsed = now - first_miss
            if elapsed >= total_wait:
                print("gh: command not found; gave up after %gs" % elapsed, file=sys.stderr)
                raise NoAnswer("")
            if elapsed < fast_wait:
                wait = retry_sleep
            else:
                wait = slow_sleep
            print("gh: command not found; waiting %gs" % wait, file=sys.stderr)
            time.sleep(wait)


def gh_probe(*args):
    return bounded(["gh", *args], capture_output=True, text=True)


def rate_limit_reset(run=subprocess.run):
    done = bounded(["gh", "api", "rate_limit", "--jq", ".resources.core.reset"], run=run,
                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        return int(done.stdout.strip())
    except ValueError:
        return None


def gh_api(path, stderr=None):
    return run_gh("api", path, stderr=stderr)


def gh_run_rerun_failed(run_id):
    """`gh run rerun <run_id> --failed`: re-runs a CI run's failed jobs; the CompletedProcess, stderr captured."""
    return run_gh("run", "rerun", run_id, "--failed", stderr=subprocess.PIPE)


def gh_api_delete(path):
    return run_gh("api", "-X", "DELETE", path, stderr=subprocess.PIPE)


def gh_label_create(name):
    return run_gh("api", "-X", "POST", "-f", "name=%s" % name, "-f", "color=ededed",
                  "-f", "description=Claimed by a veri run", "repos/{owner}/{repo}/labels", stderr=subprocess.PIPE)


def gh_api_add_label(path, name):
    return run_gh("api", "-X", "POST", "-f", "labels[]=%s" % name, path, stderr=subprocess.PIPE)


_ISSUES = "repos/{owner}/{repo}/issues"
_EMPTY_PAGE = r"^\[\]$"


def _issue(number):
    return "%s/%s" % (_ISSUES, number)


def _pages(path):
    sep = "&" if "?" in path else "?"
    page = 1
    while True:
        yield _gh_api_said("%s%spage=%d" % (path, sep, page))
        page += 1


def _comments(number):
    bodies = ""
    for run in _pages("%s/comments" % _issue(number)):
        if run.returncode != 0:
            raise NoAnswer("", run.stderr)
        comments = json.loads(run.stdout)
        if not comments:
            return bodies
        bodies += "".join(c["body"] + "\n" for c in comments)


def rest_items(path):
    """The items of every page of the REST list <path>, read with gh's stderr captured and not echoed; NoAnswer whose
    detail is that stderr when a page fails."""
    items = []
    sep = "&" if "?" in path else "?"
    page = 1
    while True:
        run = gh_api("%s%spage=%d" % (path, sep, page), stderr=subprocess.PIPE)
        if run.returncode != 0:
            raise NoAnswer("", run.stderr or "")
        found = json.loads(run.stdout or "[]")
        if not found:
            return items
        items += found
        page += 1


def issue_comments(number):
    """Issue <number>'s comments as REST records (`id`, `body`, ...), oldest first; NoAnswer as rest_items."""
    return rest_items("%s/comments?per_page=100" % _issue(number))


def authenticated_login():
    """The login `gh` is authenticated as (`gh api user`), read with gh's stderr captured and not echoed; NoAnswer whose
    detail is that stderr when it cannot be read."""
    run = gh_api("user", stderr=subprocess.PIPE)
    try:
        login = json.loads(run.stdout or "null").get("login") if run.returncode == 0 else None
    except (ValueError, AttributeError):
        login = None
    if not login:
        raise NoAnswer("", run.stderr or "gh api user named no login")
    return login


TRUSTED_ASSOCIATIONS = ("OWNER", "COLLABORATOR")
# Who may author a takeable issue (PRD 022.4, "Author policy at selection"): MEMBER counts here, unlike for comments,
# since an issue is taken only after someone with triage access applied the opt-in label.
ISSUE_AUTHOR_ASSOCIATIONS = ("OWNER", "MEMBER", "COLLABORATOR")
_TRUSTING_LOGIN = {}


def author_association(record):
    """The REST record's `author_association`, the field GitHub sets, or "unknown" when it cannot be read (no field, not
    text, not an object)."""
    association = record.get("author_association") if isinstance(record, dict) else None
    return association if isinstance(association, str) and association else "unknown"


def trusted_author(record, associations=TRUSTED_ASSOCIATIONS):
    """Whether the REST record's author is trusted by association: its `author_association` is one of <associations>.
    The one author rule every reader shares; fail closed: an author that cannot be read is not trusted."""
    return author_association(record) in associations


def _trusting_login():
    """The authenticated gh login trusted_comment compares against, kept once read so it is read at most once per
    process; None when gh gave none, so the association alone answers and the caller is not stopped. A failed read is
    not kept: a long-lived reader (the dispatcher) trusts its own comments again once gh answers."""
    if "login" not in _TRUSTING_LOGIN:
        try:
            _TRUSTING_LOGIN["login"] = authenticated_login()
        except NoAnswer:
            return None
    return _TRUSTING_LOGIN["login"]


def trusted_comment(comment):
    """Whether the REST comment object <comment> may speak for a run (PRD 022.3): its `author_association` is OWNER or
    COLLABORATOR, or its `user.login` is the authenticated gh user's. Decided from the fields GitHub sets, never from
    the body; fail closed: a record whose author cannot be read (not an object, no user, a deleted user, no login) is
    not trusted, nor is an association the rule does not list."""
    user = comment.get("user") if isinstance(comment, dict) else None
    login = user.get("login") if isinstance(user, dict) else None
    if not isinstance(login, str) or not login:
        return False
    return trusted_author(comment) or login == _trusting_login()


def _quiet_write(*args):
    run = run_gh("api", *args, stderr=subprocess.PIPE)
    if run.returncode != 0:
        raise NoAnswer("", run.stderr or "")


def gh_comment_post(number, body):
    """Post <body> as a new comment on issue <number>; NoAnswer whose detail is gh's stderr, not echoed."""
    _quiet_write("-X", "POST", "%s/comments" % _issue(number), "-f", "body=%s" % body)


def gh_comment_edit(comment_id, body):
    """Replace the body of the issue comment <comment_id>; NoAnswer whose detail is gh's stderr, not echoed."""
    _quiet_write("-X", "PATCH", "%s/comments/%s" % (_ISSUES, comment_id), "-f", "body=%s" % body)


class GraphQLAdapter:
    def _run(self, *args):
        run = _retry_refused(lambda: run_gh(*args, stderr=subprocess.PIPE), "stderr")
        if run.returncode != 0:
            raise NoAnswer("", run.stderr)
        return run.stdout

    def list(self, *args):
        return self._run(*args)

    def issue_view(self, number, field):
        if field == "comments":
            return _comments(number)
        if field not in ("body", "labels"):
            raise NoAnswer("")
        query = ".body" if field == "body" else ".labels[].name"
        return self._run("issue", "view", number, "--json", field, "-q", query)


class RestAdapter:
    def list(self, path, empty=_EMPTY_PAGE):
        answer = ""
        for run in _pages(path):
            if run.returncode != 0:
                raise NoAnswer(answer, run.stderr or "")
            body = run.stdout.rstrip("\n")
            if not body or re.search(empty, body):
                return answer
            answer += body

    def issue_view(self, number, field):
        if field == "comments":
            return _comments(number)
        rest = _retry_refused(lambda: _gh_api_said(_issue(number)), "stderr")
        try:
            issue = json.loads(rest.stdout)
        except json.JSONDecodeError as error:
            print("json.decoder.JSONDecodeError: %s" % error, file=sys.stderr)
            raise NoAnswer("", rest.stderr or "")
        if rest.returncode != 0:
            raise NoAnswer("", rest.stderr or "")
        if field == "labels":
            return "".join(label["name"] + "\n" for label in issue["labels"])
        if field != "body":
            raise NoAnswer("")
        return (issue["body"] or "") + "\n"

    def issue_edit(self, number, body_file):
        run = run_gh("api", "-X", "PATCH", _issue(number), "-F", "body=@%s" % body_file)
        if run.returncode != 0:
            raise NoAnswer("")

    def issue_comment(self, number, body):
        run = run_gh("api", _issue(number) + "/comments", "-f", "body=%s" % body, "-q", ".html_url")
        if run.returncode != 0:
            raise NoAnswer("")
        return run.stdout

    def issue_create(self, title, body, *labels):
        run = run_gh("api", _ISSUES, "-f", "title=%s" % title,
                  "-f", "body=%s" % body,
                  *[a for label in labels for a in ("-f", "labels[]=%s" % label)], "-q", ".html_url")
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

    def issue_comment(self, number, body):
        return self.rest.issue_comment(number, body)

    def issue_create(self, title, body, *labels):
        return self.rest.issue_create(title, body, *labels)

    def json(self, fixture, path, *args):
        if args:
            return self.list(path, *args)
        return self.rest_list(path)

    def page(self, fixture, path, *args):
        run = gh_api(path)
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
        if not args:
            return RestOnlyAdapter.page(self, fixture, path)
        return self.graphql.list(*args)

    def issue_view(self, number, field):
        return self.graphql.issue_view(number, field)


class FallbackAdapter(GraphQLOnlyAdapter):
    def _fallback(self, graphql, rest):
        try:
            return graphql()
        except NoAnswer:
            return rest()

    def list(self, path, *args):
        return self._fallback(lambda: GraphQLOnlyAdapter.list(self, path, *args),
                              lambda: RestOnlyAdapter.list(self, path))

    def page(self, fixture, path, *args):
        if not args:
            return RestOnlyAdapter.page(self, fixture, path)
        return self._fallback(lambda: GraphQLOnlyAdapter.page(self, fixture, path, *args),
                              lambda: RestOnlyAdapter.page(self, fixture, path, *args))

    def issue_view(self, number, field):
        return self._fallback(lambda: GraphQLOnlyAdapter.issue_view(self, number, field),
                              lambda: RestOnlyAdapter.issue_view(self, number, field))


class FixtureAdapter:
    def __init__(self, directory):
        self.directory = directory

    def json(self, fixture, path, *args):
        with open(os.path.join(self.directory, fixture)) as f:
            return f.read()

    def page(self, fixture, path, *args):
        return self.json(fixture, path, *args)


def _select(operation):
    fixtures = tunables.read("VERI_GH_JSON") or None
    if operation == "json" and fixtures:
        return FixtureAdapter(fixtures)
    driver = tunables.get("VERI_GH_DRIVER")
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


def _search_issues(args):
    issues = []
    state = args[args.index("--state") + 1]
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    wanted = args[args.index("--json") + 1].split(",") if "--json" in args else []
    words, order = [], ""
    for word in args[args.index("--search") + 1].split():
        if word.startswith("sort:"):
            field, _, direction = word[5:].partition("-")
            order = "&sort=%s&order=%s" % (field, direction)
        else:
            words.append(word)
    # gh api substitutes only a literal {owner}/{repo}: encoded, it reaches GitHub as is and the search is HTTP 422.
    # GitHub search has no state:all and answers it with no rows: all states is no state qualifier.
    q = "is:issue %s%s" % ("" if state == "all" else "state:%s " % state, " ".join(words))
    for run in _pages("search/issues?q=repo:{owner}/{repo}+%s%s" % (urllib.parse.quote_plus(q.strip()), order)):
        if run.returncode != 0:
            raise NoAnswer("", run.stderr or "")
        items = json.loads(run.stdout)["items"]
        if not items:
            break
        for i in items:
            row = {"state": (i.get("state") or "").upper(),
                   "labels": [{"name": l["name"]} for l in i.get("labels") or []],
                   "closedAt": i.get("closed_at"), "updatedAt": i.get("updated_at"),
                   "createdAt": i.get("created_at"), "body": i.get("body")}
            if "comments" in wanted:
                row["comments"] = [{"body": c["body"]} for c in rest_items("%s/comments" % _issue(i["number"]))]
            issues.append({"number": i["number"], "title": i["title"], "url": i["html_url"],
                           **{k: row[k] for k in wanted if k in row}})
        if limit is not None and len(issues) >= limit:
            issues = issues[:limit]
            break
    return json.dumps(issues)


def gh_issue_list(*args):
    if type(_select("list")) is not GraphQLOnlyAdapter:
        if "--search" in args:
            return _search_issues(args)
        issues = []
        query = "state=%s" % (args[args.index("--state") + 1] if "--state" in args else "all")
        if "--label" in args:
            query += "&labels=%s" % args[args.index("--label") + 1]
        for run in _pages("%s?%s&per_page=100" % (_ISSUES, query)):
            if run.returncode != 0:
                raise NoAnswer("", run.stderr or "")
            page = json.loads(run.stdout)
            if not page:
                break
            issues += [{"number": i["number"], "state": i["state"].upper()}
                       for i in page if "pull_request" not in i]
        return json.dumps(issues)
    run = _retry_refused(lambda: run_gh("issue", "list", *args, stderr=subprocess.PIPE), "stderr")
    if run.returncode != 0:
        raise NoAnswer(" ".join(run.stderr.split()))
    return run.stdout


def gh_json(fixture, path, *args):
    return _select("json").json(fixture, path, *args)


def gh_json_page(fixture, path, *args):
    return _select("json").page(fixture, path, *args)


class Pull(NamedTuple):
    """One pull request, whichever route answered. A record carrying both draft spellings reads isDraft. Fields the answer did not carry read as: draft None,
    url and html_url None, head_sha None (an empty or null one reads ""), head_ref, body and state "", labels (). <url> and <html_url> are what
    the answer called them (a REST url is the API's; GraphQL has only url); <state> is upper-cased."""
    number: Optional[int]
    url: Optional[str]
    html_url: Optional[str]
    draft: Optional[bool]
    head_ref: str
    head_sha: Optional[str]
    body: str
    state: str
    labels: tuple
    mergeable: Optional[bool] = None
    cross_repository: bool = True


def _cross_repository(raw):
    """Whether the PR's head is in another repository than its base (PRD 022.14), read from the fields GitHub sets:
    `isCrossRepository` (gh pr list --json), else REST head.repo.full_name against base.repo.full_name. Fail closed: a
    null head repository (a deleted fork), a missing name or a record carrying neither shape reads as another."""
    if "isCrossRepository" in raw:
        return raw["isCrossRepository"] is not False
    names = [((raw.get(side) or {}).get("repo") or {}).get("full_name") for side in ("head", "base")]
    return not (isinstance(names[0], str) and names[0] and names[0] == names[1])


def _pull(raw):
    head = raw.get("head") or {}
    draft = raw["isDraft"] if "isDraft" in raw else raw.get("draft")
    return Pull(number=raw.get("number"), url=raw.get("url"), html_url=raw.get("html_url"), draft=draft,
                head_ref=raw.get("headRefName") or head.get("ref") or "",
                head_sha=raw.get("headRefOid") or (head["sha"] or "" if "sha" in head else None),
                body=raw.get("body") or "", state=str(raw.get("state", "")).upper(),
                labels=tuple(label.get("name") for label in raw.get("labels") or []),
                mergeable=raw.get("mergeable"), cross_repository=_cross_repository(raw))


def pulls_in(text):
    """The pull requests in <text>, as open_pulls_text returns it; ValueError when it is not JSON."""
    return [_pull(raw) for raw in json_documents.items(text)]


def open_pulls_text(fields, state="open", head=None, limit=10000, repo=None):
    """The pull request listing as text, REST pages concatenated, for a caller that decides over a
    partial answer (NoAnswer.answer) or a list that is not JSON; open_pulls reads it. <fields> are the
    GraphQL --json fields, <limit> its --limit (None leaves gh's default), <repo> owner/name (default:
    this repository), <head> one branch. With VERI_GH_JSON set it is prs.json, filtered to <head> by the
    REST shape's head.ref."""
    path = "repos/%s/pulls?state=%s&per_page=100" % (repo or "{owner}/{repo}", state)
    if head:
        path += "&head={owner}:" + head
    args = ["pr", "list", *(["--head", head] if head else []), "--state", state,
            *(["--limit", str(limit)] if limit else []), "--json", fields]
    answer = gh_json("prs.json", path, *args)
    if head and tunables.read("VERI_GH_JSON"):
        answer = json.dumps([raw for raw in json_documents.items(answer) if (raw.get("head") or {}).get("ref") == head])
    return answer


def open_pulls(fields, state="open", head=None, limit=10000, repo=None):
    """The open pull requests (<state> "all" adds the closed) as Pull records; arguments as open_pulls_text."""
    return pulls_in(open_pulls_text(fields, state, head, limit, repo))


def pull(url_or_number, repo=None):
    """One pull request (its URL or number; <repo> owner/name, default this repository) as a Pull, read
    over REST under every driver. NoAnswer whose detail is gh's stderr, which it does not echo, when the
    read fails; ValueError when the answer is not JSON."""
    path = "repos/%s/pulls/%s" % (repo or "{owner}/{repo}", str(url_or_number).rsplit("/pull/", 1)[-1])
    run = gh_api(path, stderr=subprocess.PIPE)
    if run.returncode != 0:
        raise NoAnswer("", run.stderr or "")
    return _pull(json.loads(run.stdout))


def joined_issues(base, repo=None):
    """The issue numbers (ints) a `Closes #n` line names in the body of a pull request merged into <base>: closed pull
    requests against <base>, kept only when the answer itself names <base> as the base and says merged (GraphQL state
    MERGED, REST merged_at set), and its head is in this repository (Pull.cross_repository, PRD 022.14): the query's own
    filter is not trusted, and a fork's PR a collaborator merged is a stranger's text. The read is not bounded by the open issues it
    can matter to: it grows with every pull request merged into <base>. NoAnswer
    when GitHub gave none; ValueError when the answer is not JSON."""
    return {int(n) for pr in merged_pulls(base, repo) if not pr.cross_repository for n in closed_issues(pr.body)}


def merged_pulls(base, repo=None):
    """The pull requests merged into <base> as Pull records (number, body, cross_repository among them): closed pull
    requests against <base>, kept only when the answer itself names <base> as the base and says merged (GraphQL state
    MERGED, REST merged_at set); a fork's is kept too, its cross_repository True, for the caller to decide. NoAnswer when
    GitHub gave none; ValueError when the answer is not JSON."""
    path = "repos/%s/pulls?state=closed&base=%s&per_page=100" % (repo or "{owner}/{repo}", base)
    answer = gh_json("stack-prs.json", path, "pr", "list", "--base", base, "--state", "merged", "--limit", "10000",
                     "--json", "number,body,state,baseRefName,isCrossRepository", *(["--repo", repo] if repo else []))
    return [_pull(raw) for raw in json_documents.items(answer)
            if (raw.get("baseRefName") or (raw.get("base") or {}).get("ref")) == base
            and (str(raw.get("state", "")).upper() == "MERGED" or raw.get("merged_at") or raw.get("mergedAt"))]


def pr_body_edit(number, body):
    """Replace the body of pull request <number> over REST; NoAnswer whose detail is gh's stderr, not echoed."""
    _quiet_write("-X", "PATCH", "repos/{owner}/{repo}/pulls/%s" % number, "-f", "body=%s" % body)


PULL_PAGES = 10
_PULL_URL = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/pull/\d+")


def _json_answer(run, what):
    """The JSON <run> printed; NoAnswer naming <what> when the call failed or printed something that is not JSON."""
    if run.returncode != 0:
        raise NoAnswer("", "%s: %s" % (what, " ".join((run.stderr or "").split())[:200] or "exit %d" % run.returncode))
    try:
        return json.loads(run.stdout or "")
    except ValueError:
        raise NoAnswer("", "%s: the answer is not JSON (%r)" % (what, (run.stdout or "")[:80])) from None


def _same_repository(raw, head):
    """Whether pull request record <raw>'s head branch lives in its base repository: head.repo.full_name is the base
    repository's and head.label is `<its owner>:<head>`. A fork's, or a deleted fork's (head.repo null), is not."""
    def full_name(side):
        repo = raw[side].get("repo")
        name = repo.get("full_name") if isinstance(repo, dict) else None
        return name if isinstance(name, str) and "/" in name else None
    base_repo = full_name("base")
    return (base_repo is not None and full_name("head") == base_repo
            and raw["head"].get("label") == "%s:%s" % (base_repo.split("/", 1)[0], head))


def stack_pulls(head, base):
    """The open pull requests from <head> to <base> as Pull records, read over REST 100 to a page, a page short of 100
    being the last, at most PULL_PAGES pages; kept only when the answer itself names <head> as the head ref and <base>
    as the base ref, since the query's own filter is not trusted. NoAnswer, its detail naming why, when a read fails,
    a page is not a JSON list of objects, or the pages run past the bound."""
    found = []
    for page in range(1, PULL_PAGES + 1):
        path = "%s?state=open&head={owner}:%s&base=%s&per_page=100&page=%d" % (_PULLS, head, base, page)
        items = _json_answer(gh_api(path, stderr=subprocess.PIPE), "reading the open pull requests from %s" % head)
        if not isinstance(items, list) or not all(isinstance(raw, dict) for raw in items):
            raise NoAnswer("", "the open pull requests from %s: the answer is not a list of objects" % head)
        for raw in items:
            if not all(isinstance(raw.get(side), dict) for side in ("head", "base")):
                raise NoAnswer("", "the open pull requests from %s: a record without head and base objects" % head)
        kept = [_pull(raw) for raw in items if raw["head"].get("ref") == head and raw["base"].get("ref") == base
                and _same_repository(raw, head)]
        for pr in kept:
            if not isinstance(pr.html_url, str) or not _PULL_URL.fullmatch(pr.html_url):
                raise NoAnswer("", "the open pull requests from %s: a record names no pull request url (%r)" % (
                    head, repr(pr.html_url)[:80]))
        found += kept
        if len(items) < 100:
            return found
    raise NoAnswer("", "the open pull requests from %s ran past %d pages of 100" % (head, PULL_PAGES))


def pr_open(head, base, title, body):
    """Open a pull request from <head> to <base>, ready (not a draft), over REST; its html url. NoAnswer, its detail
    naming why, when the call fails or the answer names no pull request url."""
    run = run_gh("api", "-X", "POST", _PULLS, "-f", "head=" + head, "-f", "base=" + base, "-f", "title=" + title,
                 "-f", "body=" + body, "-F", "draft=false", stderr=subprocess.PIPE)
    answer = _json_answer(run, "opening a pull request from %s to %s" % (head, base))
    url = answer.get("html_url") if isinstance(answer, dict) else None
    if not isinstance(url, str) or not _PULL_URL.fullmatch(url):
        raise NoAnswer("", "opening a pull request from %s: the answer names no pull request url (%r)" % (
            head, repr(url)[:80]))
    return url


CHECK_RUN_PAGES = 10


def check_runs(sha):
    """The check runs of commit <sha>, read by sha, as [(status, conclusion)] (conclusion None until completed): GitHub's
    `filter=latest`, so a check re-run counts by its latest attempt only, an older one never listed. Read 100 to a page
    until the answer's total_count is read, at most CHECK_RUN_PAGES pages. ValueError for a <sha> that is not 7 to 40 hex
    digits, before any read; NoAnswer, its detail naming why, for a failed read, an answer not of that shape, a page
    that ends short of the total, or a total past the bound."""
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha or ""):
        raise ValueError("not a commit sha: %r" % (sha,))
    found, total = [], None
    for page in range(1, CHECK_RUN_PAGES + 1):
        path = "repos/{owner}/{repo}/commits/%s/check-runs?filter=latest&per_page=100&page=%d" % (sha, page)
        answer = _json_answer(gh_api(path, stderr=subprocess.PIPE), "reading the check runs of %s" % sha)
        runs = answer.get("check_runs") if isinstance(answer, dict) else None
        count = answer.get("total_count") if isinstance(answer, dict) else None
        if not isinstance(runs, list) or not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise NoAnswer("", "the check runs of %s: the answer is not {total_count, check_runs}" % sha)
        if count > CHECK_RUN_PAGES * 100:
            raise NoAnswer("", "the check runs of %s: %d of them, past the %d this reads" % (sha, count, CHECK_RUN_PAGES * 100))
        total = count if total is None else total
        for raw in runs:
            status = raw.get("status") if isinstance(raw, dict) else None
            conclusion = raw.get("conclusion") if isinstance(raw, dict) else None
            if not isinstance(status, str) or not (conclusion is None or isinstance(conclusion, str)):
                raise NoAnswer("", "the check runs of %s: a check run without a status or with a garbled conclusion" % sha)
            found.append((status, conclusion))
        if len(found) >= total:
            return found
        if not runs:
            break
    raise NoAnswer("", "the check runs of %s: the answer ended at %d of the %d it counts" % (sha, len(found), total))


_RUN_URL = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/actions/runs/\d+")
_CREATED = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")


def workflow_runs(branch):
    """The newest 100 workflow runs GitHub lists for <branch>, one read, as [(head_sha, html_url, status, conclusion,
    created_at, run_attempt, workflow_id)] (conclusion None until completed; run_attempt 1, or more once re-run), kept only when the run's head repository is the repository it ran
    in: a fork's branch of the same name lists under it too. NoAnswer, its detail naming why, for a failed read or an
    answer not of the workflow-runs shape."""
    what = "the workflow runs of %s" % branch
    answer = _json_answer(gh_api("repos/{owner}/{repo}/actions/runs?branch=%s&per_page=100" % branch,
                                 stderr=subprocess.PIPE), "reading " + what)
    runs = answer.get("workflow_runs") if isinstance(answer, dict) else None
    if not isinstance(runs, list) or not all(isinstance(raw, dict) for raw in runs):
        raise NoAnswer("", "%s: the answer is not {workflow_runs: [...]}" % what)
    found = []
    for raw in runs:
        head, url, status, conclusion, created, attempt, workflow = (raw.get(key) for key in (
            "head_sha", "html_url", "status", "conclusion", "created_at", "run_attempt", "workflow_id"))
        if not (isinstance(head, str) and re.fullmatch(r"[0-9a-f]{40}", head) and isinstance(url, str)
                and _RUN_URL.fullmatch(url) and isinstance(status, str)
                and (conclusion is None or isinstance(conclusion, str))
                and isinstance(created, str) and _CREATED.fullmatch(created) and _attempt(attempt)
                and isinstance(workflow, int) and not isinstance(workflow, bool)):
            raise NoAnswer("", "%s: a run without a head sha, url, status, creation time, attempt or workflow, or with a"
                           " garbled one" % what)
        repos = [(raw.get(side) or {}).get("full_name") if isinstance(raw.get(side) or {}, dict) else None
                 for side in ("repository", "head_repository")]
        if repos[0] and repos[0] == repos[1]:
            found.append((head, url, status, conclusion, created, attempt, workflow))
    return found


def _attempt(value):
    """Whether <value> is a run attempt as GitHub states one: a whole number of at least 1, not a bool."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def run_attempt(run_id, attempt):
    """(status, conclusion) of attempt <attempt> of workflow run <run_id>
    (`repos/{owner}/{repo}/actions/runs/<run_id>/attempts/<attempt>`), conclusion None until completed. NoAnswer, its
    detail naming why, for a <run_id> not a whole number or an <attempt> below 1 (before any call), a failed read, or an
    answer that is not that attempt's record."""
    if not re.fullmatch(r"[0-9]+", str(run_id)) or not _attempt(attempt):
        raise NoAnswer("", "not a workflow run id and attempt: %r, %r" % (run_id, attempt))
    what = "attempt %d of run %s" % (attempt, run_id)
    answer = _json_answer(gh_api("repos/{owner}/{repo}/actions/runs/%s/attempts/%d" % (run_id, attempt),
                                 stderr=subprocess.PIPE), "reading " + what)
    status = answer.get("status") if isinstance(answer, dict) else None
    conclusion = answer.get("conclusion") if isinstance(answer, dict) else None
    if not (isinstance(status, str) and (conclusion is None or isinstance(conclusion, str))
            and answer.get("run_attempt") == attempt):
        raise NoAnswer("", "%s: the answer is not that attempt's record with a status" % what)
    return status, conclusion


def run_failed_log(run_id, attempt=None):
    """The failed-job log of workflow run <run_id> (`gh run view <run_id> --log-failed`, of attempt <attempt> when given:
    `--attempt <n>`), as gh prints it. NoAnswer, its detail naming why, for a <run_id> that is not a whole number or an
    <attempt> below 1 (before any call) or a call that fails."""
    if not re.fullmatch(r"[0-9]+", str(run_id)) or not (attempt is None or _attempt(attempt)):
        raise NoAnswer("", "not a workflow run id and attempt: %r, %r" % (run_id, attempt))
    run = run_gh("run", "view", str(run_id), "--log-failed", *(["--attempt", str(attempt)] if attempt else []),
                 stderr=subprocess.PIPE)
    if run.returncode != 0:
        raise NoAnswer("", "the failed log of run %s: %s" % (run_id, " ".join((run.stderr or "").split())[:200]
                                                              or "exit %d" % run.returncode))
    return run.stdout or ""


def closed_issues(body, loose=False):
    """The issue numbers (strings) <body> closes, in order: `Closes #n`; <loose> also reads `closes #n`
    and `disCloses #n`, the spelling of status --recover."""
    return re.findall(r"[Cc]loses #(\d+)" if loose else r"\bCloses #(\d+)", body or "")


def gh_pr_diff_names(number):
    """The paths open PR <number> changes, from `gh api repos/{owner}/{repo}/pulls/<number>/files`, every page."""
    return [f["filename"] for f in rest_items("repos/{owner}/{repo}/pulls/%s/files" % number)]


def gh_issue_view(number, field):
    return _select("issue_view").issue_view(number, field)


def gh_issue_edit(number, body_file):
    _select("issue_edit").issue_edit(number, body_file)


def gh_issue_create(title, body, *labels):
    return _select("issue_create").issue_create(title, body, *labels)


def gh_issue_comment(number, body):
    return _select("issue_comment").issue_comment(number, body)


def gh_issue_add_label(number, label):
    run = run_gh("api", _issue(number) + "/labels", "-f", "labels[]=%s" % label)
    if run.returncode != 0:
        raise NoAnswer("")


def gh_issue_remove_label(number, label):
    run = gh_api_delete(_issue(number) + "/labels/" + label)
    if run.returncode != 0 and "HTTP 404" not in run.stderr:
        raise NoAnswer("")


def gh_label_exists(label):
    """Whether the repository has label <label>: False on a 404, NoAnswer on any other failure."""
    run = run_gh("api", "repos/{owner}/{repo}/labels/" + urllib.parse.quote(label, safe=""), stderr=subprocess.PIPE)
    if run.returncode == 0:
        return True
    if "HTTP 404" in run.stderr:
        return False
    raise NoAnswer(" ".join(run.stderr.split()))


def gh_label_ensure(label):
    run = run_gh("api", "repos/{owner}/{repo}/labels", "-f", "name=%s" % label, stderr=subprocess.PIPE)
    if run.returncode != 0 and "HTTP 422" not in run.stderr and "already_exists" not in run.stderr:
        sys.stderr.write(run.stderr)
        raise NoAnswer(" ".join(run.stderr.split()))


_PULLS = "repos/{owner}/{repo}/pulls"
_READY_MUTATION = ("mutation($id: ID!) { markPullRequestReadyForReview(input: {pullRequestId: $id})"
                   " { pullRequest { isDraft } } }")


def gh_pr_create(head, base, title, body):
    """Open a pull request from branch <head> against <base> (REST); its URL. NoAnswer whose detail is gh's stderr."""
    run = run_gh("api", "-X", "POST", _PULLS, "-f", "head=%s" % head, "-f", "base=%s" % base,
                 "-f", "title=%s" % title, "-f", "body=%s" % body, "-q", ".html_url", stderr=subprocess.PIPE)
    if run.returncode != 0:
        raise NoAnswer("", run.stderr or "")
    return run.stdout.strip()


def _route_open(driver, route):
    if route == "graphql":
        return driver in ("auto", "graphql")
    return driver != "graphql"


def _poll_sleep():
    raw = tunables.read("VERI_POLL", "10", unless_empty="10")
    try:
        time.sleep(float(raw))
    except ValueError:
        print("sleep: invalid time interval '%s'" % raw, file=sys.stderr)


def _api_graphql_ready(number):
    node = run_gh("api", "%s/%s" % (_PULLS, number), "-q", ".node_id")
    if node.returncode != 0:
        return False
    return run_gh("api", "graphql", "-f", "query=" + _READY_MUTATION,
               "-f", "id=" + node.stdout.rstrip("\n")).returncode == 0


def _retry_refused(call, stream):
    refusals = 0
    while True:
        done = call()
        text = getattr(done, stream) or ""
        marked = refusal_kind(text) == "rate-limit"
        if done.returncode == 0 or not marked:
            return done
        if refusals >= refusal_retries():
            return done
        refusals += 1
        time.sleep(wait_seconds("VERI_GH_REFUSAL_SLEEP", 0))


def push_dry_run(refspec, env):
    """`git push --dry-run --no-verify origin <refspec>` under <env>, bounded like every other call to origin: at
    VERI_GH_TIMEOUT its process group is killed and it answers exit 124 with a line naming the limit on stderr."""
    return bounded_group(["git", "push", "--dry-run", "--no-verify", "origin", refspec],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


def _refuse_unpushed(number, head_sha):
    ref = run_gh("api", "%s/%s" % (_PULLS, number), "--jq", ".head.ref")
    branch = ref.stdout.rstrip("\n")
    listed = bounded_group(["git", "ls-remote", "origin", "refs/heads/" + branch],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    fields = listed.stdout.split()
    if not fields or fields[0] == head_sha:
        return
    print("gh_pr_ready: remote branch %s holds %s, not %s" % (branch, fields[0], head_sha), file=sys.stderr)
    raise NoAnswer("")


def gh_pr_ready(number, head_sha=""):
    """Mark draft PR <number> ready for review; given <head_sha>, only once pulls/<number> reports it
    as the head, reading it again every VERI_POLL seconds (default 10), at most 30 times. NoAnswer
    when GitHub gave no answer on any open route, or the head never matched."""
    driver = tunables.get("VERI_GH_DRIVER")
    if driver not in ("auto", "rest", "graphql"):
        print("VERI_GH_DRIVER is '%s': expected auto, rest or graphql" % driver, file=sys.stderr)
        raise NoAnswer("")
    tries = 0
    while head_sha:
        read = run_gh("api", "%s/%s" % (_PULLS, number), "--jq", ".head.sha")
        if read.returncode != 0:
            raise NoAnswer("")
        head = read.stdout.rstrip("\n")
        if head == head_sha:
            break
        if tries == 0:
            _refuse_unpushed(number, head_sha)
        tries += 1
        if tries >= 30:
            print("gh_pr_ready: PR %s head is %s after %d reads, expected %s" % (number, head, tries, head_sha),
                  file=sys.stderr)
            raise NoAnswer("")
        _poll_sleep()
    gql_err = ccr_err = ""
    if _route_open(driver, "graphql"):
        ready = _retry_refused(lambda: run_gh("pr", "ready", number, stderr=subprocess.PIPE), "stderr")
        sys.stdout.write(ready.stdout)
        if ready.returncode == 0:
            return
        gql_err = ready.stderr.rstrip("\n")
    if _route_open(driver, "rest"):
        ccr = _retry_refused(lambda: run_gh("api", "-X", "POST", "%s/%s/ccr/ready_for_review" % (_PULLS, number),
                                         stderr=subprocess.STDOUT), "stdout")
        if ccr.returncode == 0:
            return
        ccr_err = ccr.stdout.rstrip("\n")
        if _api_graphql_ready(number):
            return
    for err in sorted((gql_err, ccr_err), key=lambda err: refusal_kind(err) == "rate-limit"):
        if err:
            print(err, file=sys.stderr)
    raise NoAnswer("")
