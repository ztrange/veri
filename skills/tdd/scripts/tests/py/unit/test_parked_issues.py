"""In-process cases for veri/parked_issues.py, the reader of the parked set."""
import fnmatch
import importlib
import json
import subprocess

import pytest

# The author fields of a comment github.trusted_comment trusts: veri's own parked comments carry them (#3972).
OWNER = {"author_association": "OWNER", "user": {"login": "veri-operator"}}


def first_four(out):
    return "".join("\t".join(line.split("\t")[:4]) + "\n" for line in out.splitlines())


@pytest.fixture
def parked_issues():
    return importlib.import_module("veri.parked_issues")


def test_main_2420_lists_only_the_parked_issue_and_exits_0_when_a_parked_pull_request_carries_no_parked_comment(
        monkeypatch, parked_issues, run_cli):
    listing = [
        {"number": 2403, "title": "A pull request", "pull_request": {"url": "x"}},
        {"number": 2373, "title": "An issue"},
    ]
    comments = {
        2373: [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: upstream ships"}],
        2403: [],
    }

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments[int(path.split("/issues/")[1].split("/")[0])])
        return json.dumps(listing)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)

    code, out, err = run_cli(parked_issues, [])

    assert (code, first_four(out), "2403" in err) == (0, "2373\tAn issue\twaiting on upstream\tupstream ships\n", False)


def test_main_2420_still_exits_2_naming_a_parked_issue_with_no_parked_comment_listed_beside_a_parked_pull_request(
        monkeypatch, parked_issues, run_cli):
    listing = [
        {"number": 2403, "title": "A pull request", "pull_request": {"url": "x"}},
        {"number": 2373, "title": "An issue"},
    ]

    def fake_rest_list(path, *args):
        return json.dumps([] if "/comments" in path else listing)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, err) == (2, "", "parked-issues.sh: issue #2373 has no parked comment\n")


def test_main_2420_exits_3_writing_nothing_when_only_pull_requests_carry_the_parked_label(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 2403, "title": "A pull request", "pull_request": {"url": "x"}}]

    def fake_rest_list(path, *args):
        return json.dumps([] if "/comments" in path else listing)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (3, "")


def test_main_3683_prints_a_dash_fifth_field_for_a_parked_comment_with_no_blocked_by_line(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: upstream ships"}]

    def fake_rest_list(path, *args):
        return json.dumps(comments if "/comments" in path else listing)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\tupstream ships\t-\t-\n")


def test_main_3683_prints_waiting_as_the_fifth_field_when_the_blocked_by_line_names_an_open_issue(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3420 merges\nBlocked by: #3420"}]

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "/issues/3420" in path or "/pulls/3420" in path:
            return json.dumps([{"number": 3420, "state": "open", "merged": False}])
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        assert "3420" in path
        return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=json.dumps({"number": 3420, "state": "open", "merged": False}), stderr="")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3420 merges\twaiting\t-\n")


def test_main_3683_exits_2_naming_the_blocker_and_printing_nothing_when_gh_gives_no_answer_for_a_blocker(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3420 merges\nBlocked by: #3420"}]

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3420" in path:
            raise parked_issues.github.NoAnswer("")
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        raise parked_issues.github.NoAnswer("")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, "3420" in err) == (2, "", True)


def test_main_3683_prints_ready_as_the_fifth_field_when_the_blocked_by_line_names_only_closed_issues(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3420 merges\nBlocked by: #3420"}]
    closed = json.dumps({"number": 3420, "state": "closed"})

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3420" in path:
            return closed
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        assert "3420" in path
        return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=closed, stderr="")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3420 merges\tready\t-\n")


def test_main_3683_prints_ready_as_the_fifth_field_when_the_blocked_by_line_names_a_merged_pull_request(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3309 merges\nBlocked by: #3309"}]
    as_issue = json.dumps({"number": 3309, "state": "closed", "pull_request": {"url": "x"}})
    as_pull = json.dumps({"number": 3309, "state": "closed", "merged": True})

    def answer(path):
        assert "3309" in path
        return as_pull if "/pulls/" in path else as_issue

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3309" in path:
            return answer(path)
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=answer(path), stderr="")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3309 merges\tready\t-\n")


def test_main_3683_prints_waiting_as_the_fifth_field_when_the_blocked_by_line_names_a_pull_request_closed_unmerged(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3309 merges\nBlocked by: #3309"}]
    as_issue = json.dumps({"number": 3309, "state": "closed", "pull_request": {"url": "x"}})
    as_pull = json.dumps({"number": 3309, "state": "closed", "merged": False})

    def answer(path):
        assert "3309" in path
        return as_pull if "/pulls/" in path else as_issue

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3309" in path:
            return answer(path)
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=answer(path), stderr="")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3309 merges\twaiting\t-\n")


def test_main_3683_prints_waiting_as_the_fifth_field_when_the_blocked_by_line_names_an_open_pull_request(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3309 merges\nBlocked by: #3309"}]
    as_issue = json.dumps({"number": 3309, "state": "open", "pull_request": {"url": "x"}})
    as_pull = json.dumps({"number": 3309, "state": "open", "merged": False})

    def answer(path):
        assert "3309" in path
        return as_pull if "/pulls/" in path else as_issue

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3309" in path:
            return answer(path)
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=answer(path), stderr="")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3309 merges\twaiting\t-\n")


def test_main_3683_exits_2_naming_the_blocker_and_printing_no_row_when_gh_gives_no_answer_to_the_merged_state_read(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3309 merges\nBlocked by: #3309"}]
    as_issue = json.dumps({"number": 3309, "state": "closed", "pull_request": {"url": "x"}})

    def fake_rest_list(path, *args):
        return json.dumps(comments if "/comments" in path else listing)

    def fake_api(path, *args, **kwargs):
        if "/pulls/3309" in path:
            raise parked_issues.github.NoAnswer("")
        return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=as_issue, stderr="")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, err) == (
        2, "", "parked-issues.sh: no answer from gh to reading the merged state of #3309\n")


def test_main_3739_prints_ready_when_gh_api_returns_a_completed_process_for_a_merged_pull_request_blocker(
        monkeypatch, parked_issues, run_cli):
    import subprocess

    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3309 merges\nBlocked by: #3309"}]
    as_issue = json.dumps({"number": 3309, "state": "closed", "pull_request": {"url": "x"}})
    as_pull = json.dumps({"number": 3309, "state": "closed", "merged": True})

    def fake_rest_list(path, *args):
        return json.dumps(comments if "/comments" in path else listing)

    def fake_api(path, *args, **kwargs):
        body = as_pull if "/pulls/" in path else as_issue
        return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=body, stderr="")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3309 merges\tready\t-\n")


def test_main_3739_prints_waiting_when_gh_api_returns_a_completed_process_for_an_open_issue_blocker(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3711, "title": "A parked issue"}]
    comments = [{**OWNER, "body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3737 merges\nBlocked by: #3737"}]

    def fake_rest_list(path, *args):
        return json.dumps(comments if "/comments" in path else listing)

    def fake_api(path, *args, **kwargs):
        return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=json.dumps({"number": 3737, "state": "open"}), stderr="")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3711\tA parked issue\twaiting on upstream\t#3737 merges\twaiting\t-\n")


# main through run_cli as `parked-issues.sh`, gh faked at its process boundary. gh_stub answers each gh call as the shell stub
# `for a in "$@"; do case "$a" in <pattern>) <answer>;; esac; done; echo '[]'` would: the first argument a pattern matches,
# patterns tried in order, takes that pattern's answer; no match answers `[]`.

def gh_stub(fake_processes, *cases):
    def answer(line, **kwargs):
        for arg in fake.argvs[-1][1:]:
            for pattern, reply in cases:
                if fnmatch.fnmatchcase(str(arg), pattern):
                    return reply
        return 0, "[]\n", ""

    fake = fake_processes.answers({"gh": answer})
    return fake


def ok(value):
    return 0, json.dumps(value) + "\n", ""


NO_ANSWER = (1, "", "")
PARKED = "### ⏸ Parked\n"
ISSUE_7 = {"number": 7, "title": "Teach the verifier to refuse", "labels": [{"name": "parked"}]}
ISSUE_8 = {"number": 8, "title": "Hold the PR", "labels": [{"name": "parked"}]}


def comments(*bodies):
    return ok([{**OWNER, "body": body} for body in bodies])


def listing_7_with(*bodies):
    return [("*page=[2-9]*", ok([])), ("*/issues/7/comments*", comments(*bodies)), ("*/issues*", ok([ISSUE_7]))]


def two_issues_the_second(body_8):
    return [("*/issues/7/comments*page=1", comments(PARKED + "Cause: bail on the verifier\nUnblock: a human reads the diff")),
            ("*/issues/8/comments*page=1", comments(body_8)),
            ("*/comments*", ok([])),
            ("*/issues*page=1", ok([ISSUE_7, ISSUE_8]))]


def test_parked_issues_prints_one_tab_separated_line_per_parked_issue_with_the_cause_and_unblock_of_its_parked_comment_and_exits_0(
        tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes, *listing_7_with(PARKED + "Cause: first bail\nUnblock: old",
                                             PARKED + "Cause: second bail on the verifier\nUnblock: a human reads the diff"))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert code == 0, err
    assert first_four(out) == "7\tTeach the verifier to refuse\tsecond bail on the verifier\ta human reads the diff\n"


def test_parked_issues_given_any_argument_prints_its_usage_line_on_stderr_and_exits_2_without_calling_gh(
        tmp_path, parked_issues, run_cli, fake_processes):
    fake = gh_stub(fake_processes)

    code, out, err = run_cli(parked_issues, ["--all"], cwd=tmp_path)

    assert code == 2, err
    assert "usage: parked-issues.sh" in err
    assert first_four(out) == ""
    assert fake.calls == []


def test_parked_issues_when_the_final_comment_is_not_a_parked_comment_still_prints_the_cause_and_unblock_of_the_parked_comment(
        tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes, *listing_7_with(PARKED + "Cause: second bail on the verifier\nUnblock: a human reads the diff",
                                             "Still waiting on the human."))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert code == 0, err
    assert first_four(out) == "7\tTeach the verifier to refuse\tsecond bail on the verifier\ta human reads the diff\n"


def test_parked_issues_does_not_read_a_comment_that_quotes_the_parked_heading_mid_body_as_the_parked_comment(
        tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes, *listing_7_with(PARKED + "Cause: second bail on the verifier\nUnblock: a human reads the diff",
                                             "Quoting the old note:\n" + PARKED + "Cause: quoted cause\nUnblock: quoted unblock"))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert code == 0, err
    assert first_four(out) == "7\tTeach the verifier to refuse\tsecond bail on the verifier\ta human reads the diff\n"


def test_parked_issues_when_an_issue_carries_several_parked_comments_prints_the_cause_and_unblock_of_the_latest(
        tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes, *listing_7_with(PARKED + "Cause: first bail\nUnblock: old", "chatter",
                                             PARKED + "Cause: held PR\nUnblock: the human merges",
                                             PARKED + "Cause: third bail\nUnblock: fix the fixture", "Still waiting."))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert code == 0, err
    assert first_four(out) == "7\tTeach the verifier to refuse\tthird bail\tfix the fixture\n"


def test_parked_issues_with_no_open_issue_labelled_parked_prints_nothing_and_exits_3(tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes)

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert code == 3, err
    assert first_four(out) == ""


def test_parked_issues_exits_2_naming_the_listing_call_when_gh_gives_no_answer_to_it(tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes, ("*", NO_ANSWER))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert code == 2, err
    assert "listing the issues" in err, err


def test_parked_issues_exits_2_naming_the_comments_call_when_gh_answers_the_listing_but_not_an_issues_comments(
        tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes, ("*page=[2-9]*", ok([])), ("*/issues/7/comments*", NO_ANSWER), ("*/issues*", ok([ISSUE_7])))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert code == 2, err
    assert "reading the comments" in err, err


def test_parked_issues_reads_the_parked_comment_served_on_the_second_page_of_an_issues_comments(
        tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes,
            ("*/issues/7/comments*page=1", comments("chatter on page one")),
            ("*/issues/7/comments*page=2", comments(PARKED + "Cause: bail found on page two\nUnblock: a human reads page two")),
            ("*page=[3-9]*", ok([])),
            ("*/issues*page=1", ok([ISSUE_7])))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert code == 0, err
    assert first_four(out) == "7\tTeach the verifier to refuse\tbail found on page two\ta human reads page two\n"


def test_parked_issues_prints_the_parked_issue_served_on_the_second_page_of_the_listing(tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes,
            ("*/issues/7/comments*page=1", comments(PARKED + "Cause: bail on the first page\nUnblock: a human reads page one")),
            ("*/issues/8/comments*page=1", comments(PARKED + "Cause: held PR on the second page\nUnblock: the human merges")),
            ("*/comments*", ok([])),
            ("*/issues*page=1", ok([ISSUE_7])),
            ("*/issues*page=2", ok([ISSUE_8])))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert code == 0, err
    assert first_four(out) == ("7\tTeach the verifier to refuse\tbail on the first page\ta human reads page one\n"
                               "8\tHold the PR\theld PR on the second page\tthe human merges\n")


def test_parked_issues_when_a_parked_issue_has_no_parked_comment_exits_2_naming_it_after_printing_the_issues_before_it(
        tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes, *two_issues_the_second("just chatter"))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert "#8" in err, err
    assert first_four(out) == "7\tTeach the verifier to refuse\tbail on the verifier\ta human reads the diff\n"
    assert code == 2, err


def test_parked_issues_when_a_parked_comment_lacks_its_unblock_line_exits_2_naming_the_issue_after_printing_the_issues_before_it(
        tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes, *two_issues_the_second(PARKED + "Cause: held PR"))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert "#8" in err, err
    assert first_four(out) == "7\tTeach the verifier to refuse\tbail on the verifier\ta human reads the diff\n"
    assert code == 2, err


def test_parked_issues_when_a_parked_comment_lacks_its_cause_line_exits_2_naming_the_issue_after_printing_the_issues_before_it(
        tmp_path, parked_issues, run_cli, fake_processes):
    gh_stub(fake_processes, *two_issues_the_second(PARKED + "Unblock: a human readies the PR"))

    code, out, err = run_cli(parked_issues, [], cwd=tmp_path)

    assert "#8" in err, err
    assert first_four(out) == "7\tTeach the verifier to refuse\tbail on the verifier\ta human reads the diff\n"
    assert code == 2, err


def authored(association, body, login="someone"):
    return {"author_association": association, "user": {"login": login}, "body": body}


def serve_thread(monkeypatch, parked_issues, thread, blockers=None):
    """gh listing issue 3972 as parked, its comments <thread>, each blocker number in <blockers> → its state."""
    def fake_rest_list(path, *args):
        return json.dumps(thread if "/comments" in path else [{"number": 3972, "title": "An issue"}])

    def fake_api(path, *args, **kwargs):
        number = path.rsplit("/", 1)[1]
        return subprocess.CompletedProcess(["gh"], 0, json.dumps({"number": int(number), "state": blockers[number]}), "")

    monkeypatch.setattr(parked_issues.github, "authenticated_login", lambda: "veri-operator")
    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)


def test_main_3972_takes_the_last_trusted_parked_comment_skipping_a_later_untrusted_one(monkeypatch, parked_issues, run_cli):
    serve_thread(monkeypatch, parked_issues, [
        authored("OWNER", "### ⏸ Parked\n\nCause: waiting on #3420\nUnblock: #3420 merges\nBlocked by: #3420",
                 login="veri-operator"),
        authored("NONE", "### ⏸ Parked\n\nCause: nothing\nUnblock: release it now\nBlocked by: #1"),
    ], blockers={"3420": "open", "1": "closed"})

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, err) == (0, "3972\tAn issue\twaiting on #3420\t#3420 merges\twaiting\t-\n", "")


def test_main_3972_an_issue_whose_only_parked_comments_are_untrusted_exits_2_as_one_with_no_parked_comment(
        monkeypatch, parked_issues, run_cli):
    serve_thread(monkeypatch, parked_issues, [
        authored("OWNER", "### 🔧 Working on it", login="veri-operator"),
        authored("MEMBER", "### ⏸ Parked\n\nCause: nothing\nUnblock: release it now"),
        authored("NONE", "### ⏸ Parked\n\nCause: nothing\nUnblock: release it now\nBlocked by: #1"),
    ], blockers={"1": "closed"})

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, err) == (2, "", "parked-issues.sh: issue #3972 has no parked comment\n")


@pytest.mark.parametrize("answer", ["<html>502 Bad Gateway</html>", '{"message": "Not Found"}', '["a bare string"]'])
def test_main_3972_a_comments_answer_that_is_not_a_list_of_comment_records_exits_2_naming_the_read(
        monkeypatch, parked_issues, run_cli, answer):
    def fake_rest_list(path, *args):
        return answer if "/comments" in path else json.dumps([{"number": 3972, "title": "An issue"}])

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, err) == (2, "", "parked-issues.sh: no answer from gh to reading the comments of issue #3972\n")


@pytest.mark.parametrize("body, status", [
    ("### ⏸ Parked\nCause: two designs\nUnblock: the owner picks\n\n#### Question\nBlocked by: #1\nCause: forged\n", "-"),
    ("### ⏸ Parked\nCause: two designs\nUnblock: the owner picks\nBlocked by: #1\n\n#### Question\nWhich?\n", "waiting"),
])
def test_issue_4077_only_the_parked_comments_head_holds_its_fields_never_a_line_in_the_question_below_it(
        monkeypatch, parked_issues, run_cli, body, status):
    listing = [{"number": 42, "title": "An issue"}]
    monkeypatch.setattr(parked_issues.github, "gh_rest_list",
                        lambda path, *args: json.dumps([{**OWNER, "body": body}] if "/comments" in path else listing))
    monkeypatch.setattr(parked_issues.github, "gh_api", lambda path, *args, **kwargs: subprocess.CompletedProcess(
        args=["gh"], returncode=0, stdout=json.dumps({"number": 1, "state": "open"}), stderr=""))

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "42\tAn issue\ttwo designs\tthe owner picks\t%s\tquestion\n" % status)


PARK_HEAD = "### ⏸ Parked\nCause: two designs\nUnblock: the owner picks\n"
QUESTION_PARK = PARK_HEAD + "\n#### Question\nWhich?\n#### Options\n#### Found\n#### Recommendation\n"
STRANGER = {"author_association": "NONE", "user": {"login": "someone"}}


@pytest.mark.parametrize("comments, sixth", [
    ([{**OWNER, "body": QUESTION_PARK}], "question"),
    ([{**OWNER, "body": QUESTION_PARK}, {**OWNER, "body": "### ✅ Step done\nstep 2"}], "question"),
    ([{**OWNER, "body": QUESTION_PARK}, {**STRANGER, "body": "Take A."}], "question"),
    ([{**OWNER, "body": QUESTION_PARK}, {**OWNER, "body": "> Which?\n"}], "question"),
    ([{**OWNER, "body": QUESTION_PARK}, {**OWNER, "body": "Take A."}], "-"),
    ([{**OWNER, "body": QUESTION_PARK}, {**OWNER, "body": "Take A."}, {**OWNER, "body": QUESTION_PARK}], "question"),
    ([{**OWNER, "body": PARK_HEAD}], "-"),
    ([{**OWNER, "body": PARK_HEAD + "\n```\n#### Question\n```\n"}], "-"),
])
def test_issue_4100_the_sixth_field_says_question_while_the_newest_parks_question_has_no_trusted_answer(
        monkeypatch, parked_issues, run_cli, comments, sixth):
    listing = [{"number": 42, "title": "An issue"}]
    monkeypatch.setattr(parked_issues.github, "_trusting_login", lambda: "veri-operator")
    monkeypatch.setattr(parked_issues.github, "gh_rest_list",
                        lambda path, *args: json.dumps(comments if "/comments" in path else listing))

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, err) == (0, "42\tAn issue\ttwo designs\tthe owner picks\t-\t%s\n" % sixth, "")
