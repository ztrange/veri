"""In-process cases for veri/park_issue.py, park-issue.sh's work: `--blocked-by` naming the blocker under `## Blocked by`,
and main through run_cli with gh faked at its process boundary."""
import fnmatch
import importlib
import re

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
    monkeypatch.setattr(github, "gh_label_exists", lambda label: True)
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
    assert len([line for line in lines if line.startswith("Blocked by:")]) == 1


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


def test_issue_4081_park_issue_exits_2_naming_the_parked_label_and_writes_nothing_when_reading_it_gets_no_answer(
        tmp_path, park_issue, run_cli, fake_processes):
    fake = gh_stub(fake_processes,
                   ("*/issues/*/comments", (0, "{}\n", "")),
                   ("*/issues/*/labels", (0, "{}\n", "")),
                   ("*/labels/parked", (1, "", "gh: Resource not accessible by integration (HTTP 403)\n")))

    code, out, err = run_cli(park_issue, ["7", "held for review", "a human merges"], cwd=tmp_path)

    assert code == 2, (code, err, gh_log(fake))
    assert "parked label" in err, err
    assert "/issues/" not in gh_log(fake), gh_log(fake)


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


@pytest.mark.parametrize("heading", ["#### Question", "#### Options", "#### Found", "#### Recommendation"])
def test_issue_4076_a_question_file_lacking_one_heading_exits_2_naming_it_and_writes_nothing(
        park, run_cli, tmp_path, heading):
    park_issue, calls, edited = park
    question = tmp_path / "question.md"
    question.write_text(QUESTION.replace(heading + "\n", "In prose, not a heading: %s\n" % heading))

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--blocked-by", "9", "--question-file", str(question)])

    assert code == 2
    assert heading in err
    assert (calls, edited) == ([], [])


def test_issue_4076_a_question_too_long_for_one_comment_is_cut_in_the_middle_and_the_comment_says_how_much(
        park, run_cli, monkeypatch, tmp_path):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))
    long_question = QUESTION.replace("#### Found\n", "#### Found\n" + "leaf output line\n" * 5000)
    question = tmp_path / "question.md"
    question.write_text(long_question)

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--question-file", str(question)])

    assert (code, err) == (0, "")
    [comment] = comments
    assert len(comment) <= 65536
    assert comment.startswith("### ⏸ Parked\nCause: cause\nUnblock: unblock\n\n#### Question\nKeep the shim or drop it?\n")
    assert comment.endswith("#### Recommendation\nKeep it.\n")
    marker = re.search(r"\n\[(\d+) characters of the question file cut here[^\n]*\]\n", comment)
    full = "### ⏸ Parked\nCause: cause\nUnblock: unblock\n\n" + long_question
    assert len(comment) == len(full) - int(marker.group(1)) + len(marker.group(0))


@pytest.mark.parametrize("tail", [
    ["--question-file"],
    ["--question-file", "{dir}/absent.md"],
    ["--question-file", "{dir}"],
    ["--question-file", "{dir}/question.md", "--question-file", "{dir}/question.md"],
])
def test_issue_4076_a_question_file_that_is_missing_unreadable_or_repeated_exits_2_naming_the_flag_and_writes_nothing(
        park, run_cli, tmp_path, tail):
    park_issue, calls, edited = park
    (tmp_path / "question.md").write_text(QUESTION)

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock"] + [t.format(dir=tmp_path) for t in tail])

    assert code == 2
    assert "--question-file" in err
    assert (calls, edited) == ([], [])


def test_issue_4076_a_binary_question_file_exits_2_naming_the_file_and_that_it_is_not_utf_8_text(park, run_cli, tmp_path):
    park_issue, calls, edited = park
    question = tmp_path / "question.bin"
    question.write_bytes(b"#### Question\n\xff\xfe\x00binary\n")

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--question-file", str(question)])

    assert (code, calls, edited) == (2, [], [])
    assert err.startswith("park-issue.sh: cannot read the --question-file %s: not UTF-8 text (" % question), err


def test_issue_4076_a_question_of_four_byte_characters_is_cut_to_120000_utf8_bytes_on_a_character_boundary(
        park, run_cli, monkeypatch, tmp_path):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))
    long_question = QUESTION.replace("#### Found\n", "#### Found\n" + "😀" * 40000 + "\n")
    question = tmp_path / "question.md"
    question.write_text(long_question, encoding="utf-8")

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--question-file", str(question)])

    assert (code, err) == (0, "")
    [comment] = comments
    assert len(comment.encode("utf-8")) <= 120000
    assert comment.startswith("### ⏸ Parked\nCause: cause\nUnblock: unblock\n\n#### Question\n")
    assert comment.endswith("#### Recommendation\nKeep it.\n")
    marker = re.search(r"\n\[(\d+) characters of the question file cut here[^\n]*\]\n", comment)
    full = "### ⏸ Parked\nCause: cause\nUnblock: unblock\n\n" + long_question
    assert len(comment) == len(full) - int(marker.group(1)) + len(marker.group(0))


def test_issue_4076_a_question_cut_to_the_cap_stays_within_it_after_redaction_lengthens_short_secrets(
        park, run_cli, monkeypatch, tmp_path):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))
    long_question = QUESTION.replace("#### Found\n", "#### Found\n" + "s3cr3t-v " * 9000 + "\n")
    question = tmp_path / "question.md"
    question.write_text(long_question)

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--question-file", str(question)],
                             env={"GH_TOKEN": "s3cr3t-v"})

    assert (code, err) == (0, "")
    [comment] = comments
    posted = importlib.import_module("veri.redaction").redact(comment)
    assert "s3cr3t-v" not in posted
    assert len(posted) <= 65536 and len(posted.encode("utf-8")) <= 120000
    assert posted.endswith("#### Recommendation\nKeep it.\n")


@pytest.mark.parametrize("found", ["```\n#### Found\n```\n", "~~~\n#### Found\n~~~\n", "#### found\n", "#### Found \n"])
def test_issue_4076_a_heading_only_inside_a_code_fence_or_in_another_case_or_with_a_trailing_space_is_not_found(
        park, run_cli, tmp_path, found):
    park_issue, calls, edited = park
    question = tmp_path / "question.md"
    question.write_text(QUESTION.replace("#### Found\n", found))

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--question-file", str(question)])

    assert (code, calls, edited) == (2, [], [])
    assert "#### Found" in err


def test_the_parked_comment_publishes_cause_unblock_and_question_with_no_absolute_local_path_4270(
        park, run_cli, monkeypatch, tmp_path):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))
    monkeypatch.setenv("HOME", "/Users/someone-else")
    question = tmp_path / "question.md"
    question.write_text(QUESTION.replace("Keep it.\n", "Keep it: zulu leak in /Users/someone/x.py and /tmp/y\n"))

    code, out, err = run_cli(park_issue, ["42", "cause zulu at /Users/someone/x.py", "unblock zulu by /tmp/y",
                                          "--question-file", str(question)], cwd=tmp_path)

    [comment] = comments
    assert (code, [p for p in ("/Users/someone", "/tmp/y") if p in comment]) == (0, []), err
    assert comment.count("zulu") == 3


def test_a_question_dense_with_local_paths_is_cut_on_its_redacted_text_and_the_posted_body_stays_within_the_margin_4270(
        park, run_cli, monkeypatch, tmp_path):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))
    question = tmp_path / "question.md"
    question.write_text(QUESTION.replace("#### Found\n", "#### Found\n" + "/tmp " * 13000 + "\n"))

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--question-file", str(question)], cwd=tmp_path)

    assert (code, err) == (0, "")
    [comment] = comments
    assert (len(comment) <= park_issue.COMMENT_LIMIT - park_issue.MARGIN,
            len(comment.encode("utf-8")) <= park_issue.BYTE_LIMIT - park_issue.MARGIN) == (True, True), len(comment)
    assert "characters of the question file cut here" in comment
