"""In-process cases for veri/park_issue.py, park-issue.sh's work: `--blocked-by` naming the blocker under `## Blocked by`,
and main through run_cli with gh faked at its process boundary."""
import fnmatch
import importlib

import pytest

BODY = "## What happened\n\nIt broke.\n\n## Blocked by\n\nNone.\n\nTest command: make test\n"


@pytest.fixture
def park(monkeypatch):
    """park_issue with every gh write faked; returns (module, calls, edited bodies)."""
    park_issue = importlib.import_module("veri.park_issue")
    github = park_issue.github
    calls, edited = [], []

    def edit(number, body_file):
        calls.append(("edit", number))
        edited.append(open(body_file).read())

    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: calls.append(("view", number, field)) or BODY)
    monkeypatch.setattr(github, "gh_issue_edit", edit)
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: calls.append(("ensure", label)))
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: calls.append(("label", number, label)))
    monkeypatch.setattr(github, "gh_issue_remove_label", lambda number, label: calls.append(("unlabel", number, label)))
    monkeypatch.setattr(github, "gh_issue_comment", lambda number, body: calls.append(("comment", number)))
    return park_issue, calls, edited


def test_blocked_by_replaces_none_with_the_blocker_keeps_test_command_last_and_still_parks(park, run_cli):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, ["42", "pin-recheck exit 2", "#9 lands", "--blocked-by", "9"])

    assert (code, err) == (0, "")
    assert edited == ["## What happened\n\nIt broke.\n\n## Blocked by\n\n- #9\n\nTest command: make test\n"]
    assert ("label", "42", "parked") in calls and ("comment", "42") in calls


def test_blocked_by_may_come_before_the_pr_argument(park, run_cli):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, ["42", "--blocked-by", "9", "cause", "unblock", "77"])

    assert (code, err) == (0, "")
    assert "- #9" in edited[0]
    assert ("label", "77", "parked") in calls


def test_a_blocker_already_listed_is_not_written_again(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    monkeypatch.setattr(park_issue.github, "gh_issue_view", lambda number, field: BODY.replace("None.", "- #9"))

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--blocked-by", "9"])

    assert (code, edited) == (0, [])
    assert ("label", "42", "parked") in calls


def test_without_the_flag_the_body_is_never_read_or_written(park, run_cli):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock"])

    assert code == 0
    assert [call for call in calls if call[0] in ("view", "edit")] == []


@pytest.mark.parametrize("argv", [
    ["42", "cause", "unblock", "--blocked-by"],
    ["42", "cause", "unblock", "--blocked-by", "x9"],
    ["42", "cause", "unblock", "--blocked-by", "0"],
    ["42", "cause", "unblock", "--blocked-by", "9", "--blocked-by", "10"],
    ["42", "cause", "unblock", "--blocked-by", "42"],
])
def test_a_malformed_or_self_blocker_exits_2_and_writes_nothing(park, run_cli, argv):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, argv)

    assert code == 2
    assert calls == []
    assert err


def test_no_answer_on_the_body_edit_exits_2_before_the_issue_is_labelled_parked(park, run_cli, monkeypatch):
    park_issue, calls, edited = park

    def refuse(number, body_file):
        raise park_issue.github.NoAnswer("")

    monkeypatch.setattr(park_issue.github, "gh_issue_edit", refuse)

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--blocked-by", "9"])

    assert code == 2
    assert "no answer from gh to the Blocked by write" in err
    assert not [call for call in calls if call[0] in ("label", "comment")]


def test_issue_3683_the_parked_comment_carries_one_blocked_by_line_beside_cause_and_unblock(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))

    code, out, err = run_cli(park_issue, ["42", "pin-recheck exit 2", "#9 lands", "--blocked-by", "9"])

    assert (code, err) == (0, "")
    assert len(comments) == 1
    lines = comments[0].splitlines()
    assert "Cause: pin-recheck exit 2" in lines
    assert "Unblock: #9 lands" in lines
    assert lines.count("Blocked by: #9") == 1


def test_issue_3683_a_comma_separated_blocker_list_names_every_blocker_under_blocked_by(park, run_cli):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, ["42", "cause", "#9 and #10 land", "--blocked-by", "9,10"])

    assert (code, err) == (0, "")
    assert len(edited) == 1
    assert park_issue.blocked_by.blockers(edited[0], "") == [9, 10]
    assert "None." not in edited[0]


def test_issue_3683_a_comma_separated_blocker_list_is_one_blocked_by_line_in_the_parked_comment(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))

    code, out, err = run_cli(park_issue, ["42", "cause", "#9 and #10 land", "--blocked-by", "9,10"])

    assert (code, err) == (0, "")
    assert len(comments) == 1
    lines = comments[0].splitlines()
    assert lines.count("Blocked by: #9, #10") == 1
    assert len([l for l in lines if l.startswith("Blocked by:")]) == 1


def test_issue_3683_the_parked_comment_with_a_pr_argument_carries_both_the_pr_line_and_the_blocked_by_line(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))

    code, out, err = run_cli(park_issue, ["42", "cause", "#9 lands", "77", "--blocked-by", "9"])

    assert (code, err) == (0, "")
    assert len(comments) == 1
    lines = comments[0].splitlines()
    assert lines.count("PR: 77") == 1
    assert lines.count("Blocked by: #9") == 1


def test_issue_3683_without_blocked_by_the_parked_comment_is_exactly_cause_and_unblock(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))

    code, out, err = run_cli(park_issue, ["42", "pin-recheck exit 2", "#9 lands"])

    assert (code, err) == (0, "")
    assert comments == ["### ⏸ Parked\nCause: pin-recheck exit 2\nUnblock: #9 lands\n"]


def test_issue_3702_a_malformed_blocked_by_message_names_the_comma_list_form(park, run_cli):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--blocked-by", "x9"])

    assert code == 2
    assert "<n>[,<n>…]" in err.splitlines()[0]


# main through run_cli as `park-issue.sh`, gh faked at its process boundary; git is never started, so a case that reached
# it would fail as an unexpected process. gh_stub answers each gh call as the shell stub
# `for a in "$@"; do case "$a" in <pattern>) <answer>;; esac; done; echo '{}'` would: the first argument a pattern matches,
# patterns tried in order, takes that pattern's answer; no match answers `{}`. gh_log(fake) is what that stub's
# `echo "ARGS: $*" >> "$GH_LOG"` recorded: one line per call, in order.

def gh_stub(fake_processes, *cases):
    def answer(line, **kwargs):
        for arg in fake.argvs[-1][1:]:
            for pattern, reply in cases:
                if fnmatch.fnmatchcase(str(arg), pattern):
                    return reply() if callable(reply) else reply
        return 0, "{}\n", ""

    fake = fake_processes.answers({"gh": answer})
    return fake


def gh_log(fake):
    return "".join("ARGS: %s\n" % " ".join(argv[1:]) for argv in fake.argvs)


@pytest.fixture
def park_issue():
    return importlib.import_module("veri.park_issue")


def test_park_issue_labels_the_issue_parked_and_posts_one_comment_with_the_cause_and_the_unblock(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes)

    code, out, err = run_cli(park_issue, ["7", "second bail on the verifier", "a human reads the diff"], cwd=tmp_path)

    recorded = gh_log(fake)
    assert code == 0, err
    assert "parked" in recorded
    assert "7" in recorded
    assert recorded.count("### ⏸ Parked") == 1
    assert "### ⏸ Parked\nCause: second bail on the verifier\n" in recorded
    assert "Unblock: a human reads the diff" in recorded


def test_park_issue_with_the_wrong_number_of_arguments_prints_usage_exits_2_and_calls_no_gh(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes)

    for args in ([], ["7", "cause"], ["7", "cause", "unblock", "12", "extra"]):
        code, out, err = run_cli(park_issue, args, cwd=tmp_path)

        assert code == 2, (args, err)
        assert "usage: park-issue.sh <issue-number> <cause> <unblock> [" in err
        assert gh_log(fake) == ""


def test_park_issue_comment_carries_a_pr_line_only_when_given_a_pr(tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes)

    def park(*args):
        before = len(gh_log(fake))
        code, out, err = run_cli(park_issue, list(args), cwd=tmp_path)
        assert code == 0, err
        return gh_log(fake)[before:]

    assert "\nPR: 12\n" in park("7", "held for review", "a human merges", "12")
    assert "PR:" not in park("7", "held for review", "a human merges")


def test_park_issue_creates_the_parked_label_when_the_repository_lacks_it_then_labels_the_issue_and_exits_0(
        tmp_path, park_issue, run_cli, fake_processes):
    created, labelled = [], []

    def label_state(line, **kwargs):
        args = fake.argvs[-1][1:]
        for arg in args:
            if fnmatch.fnmatchcase(arg, "*/issues/*/labels"):
                if not created:
                    return 1, "", "label parked not found\n"
                labelled.append(arg)
                return 0, "{}\n", ""
            if fnmatch.fnmatchcase(arg, "*/labels/parked"):
                return (0, "{}\n", "") if created else (1, "", "HTTP 404: Not Found\n")
        for arg in args:
            if arg == "label" or fnmatch.fnmatchcase(arg, "*/labels"):
                created.append(arg)
                return 0, "{}\n", ""
        return 0, "{}\n", ""

    fake = fake_processes.answers({"gh": label_state})

    code, out, err = run_cli(park_issue, ["7", "held for review", "a human merges"], cwd=tmp_path)

    assert created, "no call created the parked label:\n" + gh_log(fake)
    assert labelled, "the issue was never labelled parked:\n" + gh_log(fake)
    assert code == 0, err


def test_park_issue_with_a_bad_argument_exits_2_naming_which_argument_and_calls_no_gh(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes)

    for args, named in ((["seven", "cause", "unblock"], "issue number"),
                        (["7", "", "unblock"], "cause"),
                        (["7", "cause", ""], "unblock"),
                        (["7", "cause", "unblock", "12", "extra"], "too many")):
        code, out, err = run_cli(park_issue, args, cwd=tmp_path)

        assert code == 2, (args, err)
        assert named in err, (args, err)
        assert gh_log(fake) == "", args


def test_park_issue_exits_2_naming_the_comment_call_when_gh_gives_no_answer_to_it(
        tmp_path, park_issue, run_cli, fake_processes):
    gh_stub(fake_processes, ("*/comments", (1, "", "")))

    code, out, err = run_cli(park_issue, ["7", "held for review", "a human merges"], cwd=tmp_path)

    assert code == 2, err
    assert "comment" in err, err


def test_park_issue_exits_2_naming_the_label_call_when_gh_gives_no_answer_to_it(
        tmp_path, park_issue, run_cli, fake_processes):
    gh_stub(fake_processes, ("*/labels", (1, "", "")))

    code, out, err = run_cli(park_issue, ["7", "held for review", "a human merges"], cwd=tmp_path)

    assert code == 2, err
    assert "label call" in err, err


def test_park_issue_on_an_issue_already_labelled_parked_posts_the_new_comment_and_exits_0(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes,
                   ("*/issues/*/comments", (0, "{}\n", "")),
                   ("*/issues/*/labels", (0, '[{"name":"parked"}]\n', "")),
                   ("*/labels", (1, "", '{"message":"Validation Failed","errors":[{"code":"already_exists"}]}\n')))

    code, out, err = run_cli(park_issue, ["7", "second park, new cause", "a human reads the diff"], cwd=tmp_path)

    recorded = gh_log(fake)
    assert code == 0, err
    assert recorded.count("### ⏸ Parked\nCause: second park, new cause\n") == 1, recorded


def test_park_issue_refuses_the_issue_number_0_exiting_2_naming_the_number_and_calls_no_gh(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes)

    code, out, err = run_cli(park_issue, ["0", "held for review", "a human merges"], cwd=tmp_path)

    assert code == 2, err
    assert "0" in err, err
    assert gh_log(fake) == ""


def test_park_issue_refuses_an_issue_number_with_a_non_ascii_digit_exiting_2_naming_the_number_and_calls_no_gh(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes)

    for number in ("١٢", "１２"):
        code, out, err = run_cli(park_issue, [number, "held for review", "a human merges"], cwd=tmp_path)

        assert code == 2, (number, err)
        assert number in err, (number, err)
        assert gh_log(fake) == "", number


def test_park_issue_refuses_an_all_zero_issue_number_exiting_2_naming_the_number_and_calls_no_gh(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes)

    code, out, err = run_cli(park_issue, ["00", "held for review", "a human merges"], cwd=tmp_path)

    assert code == 2, err
    assert "00" in err, err
    assert gh_log(fake) == ""


def test_park_issue_exits_2_naming_the_pr_write_when_gh_fails_only_that_write_2343(
        tmp_path, park_issue, run_cli, fake_processes):
    refused = (1, "", "gh: Validation Failed (HTTP 422)\n")
    fake = gh_stub(fake_processes, ("12", refused), ("*/12", refused), ("*/12/*", refused))

    code, out, err = run_cli(park_issue, ["7", "held for review", "a human merges", "12"], cwd=tmp_path)

    assert code == 2, (code, err, gh_log(fake))
    assert "PR" in err, err


def test_park_issue_labels_comments_and_exits_0_when_gh_answers_the_label_creation_with_422_2343(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes,
                   ("*/issues/*/comments", (0, "{}\n", "")),
                   ("*/issues/*/labels", (0, '[{"name":"parked"}]\n', "")),
                   ("*/labels", (1, "", "gh: Validation Failed (HTTP 422)\n")))

    code, out, err = run_cli(park_issue, ["7", "held for review", "a human merges"], cwd=tmp_path)

    recorded = gh_log(fake)
    assert "repos/{owner}/{repo}/issues/7/labels" in recorded, recorded
    assert recorded.count("### ⏸ Parked\nCause: held for review\n") == 1, recorded
    assert code == 0, err


def test_park_issue_exits_2_naming_the_label_write_when_gh_fails_to_create_the_missing_label_2343(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes,
                   ("*/issues/*/comments", (0, "{}\n", "")),
                   ("*/issues/*/labels", (0, "{}\n", "")),
                   ("*/labels", (1, "", "gh: Resource not accessible by integration (HTTP 403)\n")))

    code, out, err = run_cli(park_issue, ["7", "held for review", "a human merges"], cwd=tmp_path)

    assert code == 2, (code, err, gh_log(fake))
    assert "label" in err, err


def test_park_issue_with_a_pr_that_is_neither_a_number_nor_a_pr_url_exits_2_with_usage_naming_both_and_calls_no_gh_2429(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes)

    for pr in ("pull/12", "#12", "https://github.com/o/r/issues/12"):
        code, out, err = run_cli(park_issue, ["7", "held for review", "a human merges", pr], cwd=tmp_path)

        usage = [line for line in err.splitlines() if line.startswith("usage:")]
        assert code == 2, (pr, code, err)
        assert usage and "number" in usage[0] and "URL" in usage[0], (pr, err)
        assert gh_log(fake) == "", pr


QUESTION = ("#### Question\nKeep the shim or drop it?\n\n#### Options\n- keep: one more file, no cost\n- drop: $0, one revert\n\n"
            "#### Found\nThe investigation found `run-leaf.sh --x` | tee out\n\n#### Recommendation\nKeep it.\n")


def test_issue_4076_a_question_file_goes_verbatim_into_the_parked_comment_after_cause_and_unblock(
        park, run_cli, monkeypatch, tmp_path):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))
    question = tmp_path / "question.md"
    question.write_text(QUESTION)

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--question-file", str(question)])

    assert (code, err) == (0, "")
    assert comments == ["### ⏸ Parked\nCause: cause\nUnblock: unblock\n\n" + QUESTION]
