"""In-process cases for veri/record_answer.py, record-answer.sh's work: the owner's answer to an issue-bound question
posted on the issue as one comment, read back by issue_decisions and park_decision, with gh faked at
github.issue_comments and github.gh_comment_post."""
import importlib

import pytest

ME = {"author_association": "NONE", "user": {"login": "veri-bot"}}
OWNER = {"author_association": "OWNER", "user": {"login": "the-owner"}}
STRANGER = {"author_association": "NONE", "user": {"login": "someone"}}
PARK = {**ME, "body": "### ⏸ Parked\nCause: two designs\nUnblock: the owner picks one\n"}
QUESTION = ("#### Question\n\nShould the cap be 3 or 4?\n\n#### Options\n\n- 3: cheaper\n- 4: faster\n\n"
            "#### Found\n\nLoad timeouts at 4.\n\n#### Recommendation\n\n3.\n")


@pytest.fixture
def world(monkeypatch, tmp_path):
    """(record_answer, comments, posted, write_file): issue 42's comments (oldest first, a post appended as the gh user
    veri-bot), the bodies posted, and a writer of the question file that returns its path."""
    record_answer = importlib.import_module("veri.record_answer")
    github = record_answer.github
    comments, posted = [PARK], []

    def post(number, body):
        posted.append((number, body))
        comments.append({**ME, "body": body})
    monkeypatch.setattr(github, "_trusting_login", lambda: "veri-bot")
    monkeypatch.setattr(github, "issue_comments", lambda number: list(comments))
    monkeypatch.setattr(github, "gh_comment_post", post)

    def write_file(text):
        path = tmp_path / "main-42.md"
        path.write_text(text, encoding="utf-8")
        return str(path)
    return record_answer, comments, posted, write_file


def test_issue_4252_posts_the_question_and_the_owners_answer_as_one_comment_and_exits_0(world, run_cli):
    record_answer, comments, posted, write_file = world
    path = write_file(QUESTION + "\n## Answer\n\nTake 3.\n")

    assert run_cli(record_answer, ["42", path]) == (0, "", "")
    assert posted == [("42", "Question: Should the cap be 3 or 4?\n\nOwner's answer: Take 3.")]


def test_issue_4252_the_posted_comment_reads_as_an_owner_decision_and_as_the_answer_to_the_park(world, run_cli):
    record_answer, comments, posted, write_file = world
    run_cli(record_answer, ["42", write_file(QUESTION + "\n## Answer\n\nTake 3.\n")])
    issue_decisions = importlib.import_module("veri.issue_decisions")
    park_decision = importlib.import_module("veri.park_decision")

    assert issue_decisions.decision(comments[-1]) == "owner: Question: Should the cap be 3 or 4?\n\nOwner's answer: Take 3."
    assert run_cli(park_decision, ["42"]) == (
        0, "Question: Should the cap be 3 or 4?\n\nOwner's answer: Take 3.\n", "")


BODY = "Question: Should the cap be 3 or 4?\n\nOwner's answer: Take 3."


@pytest.mark.parametrize("author", [ME, OWNER])
def test_issue_4252_a_trusted_comment_already_holding_that_body_posts_nothing_and_exits_3(world, run_cli, author):
    record_answer, comments, posted, write_file = world
    comments.append({**author, "body": BODY + "\n"})

    code, out, err = run_cli(record_answer, ["42", write_file(QUESTION + "\n## Answer\n\nTake 3.\n")])

    assert (code, out, posted) == (3, "", [])
    assert err == "record-answer.sh: issue #42 already has this answer\n"


def test_issue_4252_a_strangers_comment_with_that_body_does_not_count_and_the_answer_is_posted(world, run_cli):
    record_answer, comments, posted, write_file = world
    comments.append({**STRANGER, "body": BODY})

    assert run_cli(record_answer, ["42", write_file(QUESTION + "\n## Answer\n\nTake 3.\n")])[0] == 0
    assert posted == [("42", BODY)]


def test_issue_4252_a_second_run_after_a_post_posts_nothing_and_exits_3(world, run_cli):
    record_answer, comments, posted, write_file = world
    path = write_file(QUESTION + "\n## Answer\n\nTake 3.\n")

    assert [run_cli(record_answer, ["42", path])[0] for _ in range(2)] == [0, 3]
    assert len(posted) == 1


USAGE = "usage: record-answer.sh <issue-number> <question-file>\n"


@pytest.mark.parametrize("argv", [[], ["42"], ["42", "{path}", "extra"], ["0", "{path}"], ["01", "{path}"],
                                  ["-1", "{path}"], ["x", "{path}"], ["4.2", "{path}"]])
def test_issue_4252_bad_arguments_exit_2_with_the_usage_and_post_nothing(world, run_cli, argv):
    record_answer, comments, posted, write_file = world
    path = write_file(QUESTION + "\n## Answer\n\nTake 3.\n")

    assert run_cli(record_answer, [a.format(path=path) for a in argv]) == (2, "", USAGE)
    assert posted == []


@pytest.mark.parametrize("text, why", [
    ("## Answer\n\nTake 3.\n", "has no #### Question heading"),
    (QUESTION, "has no ## Answer heading"),
    ("```\n#### Question\n```\n\n## Answer\n\nTake 3.\n", "has no #### Question heading"),
    (QUESTION + "\n## Answer\n\n  \n", "has an empty answer"),
    (QUESTION + "\n## Answer\n\n" + "y" * 2001 + "\n", "has an answer of 2001 characters, over 2000"),
])
def test_issue_4252_an_incomplete_file_exits_2_naming_the_cause_in_one_line_and_posts_nothing(
        world, run_cli, text, why):
    record_answer, comments, posted, write_file = world
    path = write_file(text)

    assert run_cli(record_answer, ["42", path]) == (2, "", "record-answer.sh: the question file %s %s\n" % (path, why))
    assert posted == []


def test_issue_4252_an_answer_of_exactly_2000_characters_is_posted_whole(world, run_cli):
    record_answer, comments, posted, write_file = world

    assert run_cli(record_answer, ["42", write_file(QUESTION + "\n## Answer\n\n" + "y" * 2000 + "\n")])[0] == 0
    assert posted[0][1].endswith("Owner's answer: " + "y" * 2000)


def test_issue_4252_a_question_over_2000_characters_is_cut_there_with_an_ellipsis(world, run_cli):
    record_answer, comments, posted, write_file = world
    long = "q" * 1990 + "0123456789ABC"

    assert run_cli(record_answer, ["42", write_file("#### Question\n\n%s\n\n## Answer\n\nYes.\n" % long)])[0] == 0
    assert posted == [("42", "Question: %s…\n\nOwner's answer: Yes." % long[:2000])]


@pytest.mark.parametrize("content", [None, b"#### Question\n\nq\xff\n\n## Answer\n\nYes.\n"])
def test_issue_4252_an_unreadable_file_exits_2_naming_it_and_posts_nothing(world, run_cli, tmp_path, content):
    record_answer, comments, posted, write_file = world
    path = tmp_path / "main-42.md"
    if content is not None:
        path.write_bytes(content)

    code, out, err = run_cli(record_answer, ["42", str(path)])

    assert (code, out, posted) == (2, "", [])
    assert err.startswith("record-answer.sh: cannot read the question file %s: " % path) and err.count("\n") == 1


@pytest.mark.parametrize("failing, why", [("issue_comments", "reading the comments of"),
                                          ("gh_comment_post", "posting the answer on")])
def test_issue_4252_no_answer_from_gh_exits_2_naming_the_call(world, run_cli, monkeypatch, failing, why):
    record_answer, comments, posted, write_file = world

    def no_answer(*args):
        raise record_answer.github.NoAnswer("", "HTTP 502")
    monkeypatch.setattr(record_answer.github, failing, no_answer)

    assert run_cli(record_answer, ["42", write_file(QUESTION + "\n## Answer\n\nTake 3.\n")]) == (
        2, "", "record-answer.sh: no answer from gh %s issue #42\n" % why)
    assert posted == []


@pytest.mark.parametrize("answer", [None, {"body": "x"}, [{"no": "body"}], ["text"]])
def test_issue_4252_a_comments_answer_that_is_not_comment_records_exits_2(world, run_cli, monkeypatch, answer):
    record_answer, comments, posted, write_file = world
    monkeypatch.setattr(record_answer.github, "issue_comments", lambda number: answer)

    assert run_cli(record_answer, ["42", write_file(QUESTION + "\n## Answer\n\nTake 3.\n")]) == (
        2, "", "record-answer.sh: no answer from gh reading the comments of issue #42\n")
    assert posted == []
