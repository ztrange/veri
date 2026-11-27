"""github-queue.sh replay (#4803): the queued issue writes posted in file order once GitHub answers again."""
import fcntl
import importlib
import json

import pytest

BODY = "## Acceptance criteria\n\n- [ ] first criterion alpha\n- [ ] second criterion bravo\n"


def lock_is_free(root):
    """Whether `.tdd/github-queue.lock` can be taken right now by another open file."""
    with open(root / ".tdd" / "github-queue.lock", "a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        fcntl.flock(handle, fcntl.LOCK_UN)
        return True


class Hub:
    """A fake GitHub: comments per issue, issue bodies, and the calls that get no answer once a first comment landed."""

    def __init__(self, monkeypatch, tmp_path):
        self.github = importlib.import_module("github")
        self.tick = importlib.import_module("tick_issue_criterion")
        self.queue = importlib.import_module("veri.github_queue")
        self.root = tmp_path
        self.comments, self.posted, self.edited, self.dead = {}, [], [], set()
        self.bodies = {"7": BODY}
        self.during = None
        (tmp_path / ".git").mkdir()
        (tmp_path / ".tdd").mkdir()
        for module, name in ((self.github, "gh_issue_comment"), (self.github, "issue_comments"),
                             (self.github, "gh_issue_view"), (self.tick, "gh_issue_view"),
                             (self.tick, "gh_issue_edit")):
            monkeypatch.setattr(module, name, getattr(self, name))
        monkeypatch.setattr(self.github, "trusted_comment", lambda c: c.get("trusted", True))
        monkeypatch.setattr(self.queue, "incident", lambda: False)

    def gate(self, what):
        if self.during:
            self.during()
        if what in self.dead and self.posted:
            raise self.github.NoAnswer("")

    def gh_issue_comment(self, number, body):
        self.gate("post")
        self.posted.append((str(number), body))
        return "https://x/%d" % len(self.posted)

    def issue_comments(self, number):
        self.gate("comments")
        return self.comments.get(str(number), [])

    def gh_issue_view(self, number, field):
        self.gate("view")
        return self.bodies[str(number)]

    def gh_issue_edit(self, number, body_file):
        self.gate("edit")
        with open(body_file) as f:
            self.bodies[str(number)] = f.read()
        self.edited.append(str(number))

    def enqueue(self, *entries):
        with open(self.root / ".tdd" / "github-queue", "a") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

    def left(self):
        path = self.root / ".tdd" / "github-queue"
        return [json.loads(line)["key"] for line in path.read_text().splitlines()] if path.exists() else None


def comment(key, issue="7", text="hello"):
    return {"type": "comment", "issue": issue, "kind": "step-done",
            "body": "%s\n\n<!-- veri-queued %s -->" % (text, key), "key": key}


def tick(key, k, issue="7"):
    return {"type": "tick", "issue": issue, "criterion": k, "key": key}


@pytest.fixture
def hub(monkeypatch, tmp_path):
    return Hub(monkeypatch, tmp_path)


def test_4803_replay_posts_the_queued_comments_in_file_order_removes_them_and_exits_0(hub, run_cli):
    hub.enqueue(comment("a1", text="first"), comment("b2", issue="8", text="second"))

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert [(n, b.split("\n")[0]) for n, b in hub.posted] == [("7", "first"), ("8", "second")]
    assert hub.posted[0][1].endswith("<!-- veri-queued a1 -->")
    assert hub.left() is None


def test_4803_replay_posts_a_queued_body_through_github_published_so_no_local_path_leaves_the_machine(hub, run_cli):
    hub.enqueue(comment("a1", text="see /home/someone/run/.tdd/issue-7.md"))

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert "/home/someone" not in hub.posted[0][1]
    assert "<path>" in hub.posted[0][1]


def test_4803_replay_skips_a_comment_whose_key_a_trusted_comment_already_carries(hub, run_cli):
    hub.comments["7"] = [{"body": "landed\n\n<!-- veri-queued a1 -->", "trusted": True}]
    hub.enqueue(comment("a1"), comment("b2"))

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert [b.endswith("b2 -->") for _, b in hub.posted] == [True]
    assert hub.left() is None


def test_4803_replay_posts_a_comment_whose_key_only_an_untrusted_comment_carries(hub, run_cli):
    hub.comments["7"] = [{"body": "forged <!-- veri-queued a1 -->", "trusted": False}]
    hub.enqueue(comment("a1"))

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert len(hub.posted) == 1


def test_4803_replay_ticks_a_queued_criterion_through_tick_issue_criterion(hub, run_cli):
    hub.enqueue(tick("t1", 2))

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert "- [x] second criterion bravo" in hub.bodies["7"]
    assert "- [ ] first criterion alpha" in hub.bodies["7"]
    assert hub.left() is None


def test_4803_replay_counts_a_tick_whose_criterion_is_already_ticked_as_done(hub, run_cli):
    hub.bodies["7"] = BODY.replace("- [ ] second", "- [x] second")
    hub.enqueue(tick("t1", 2), comment("b2"))

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert hub.edited == []
    assert len(hub.posted) == 1
    assert hub.left() is None


def test_4803_replay_with_no_queue_exits_3(hub, run_cli):
    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert (code, hub.posted) == (3, [])


@pytest.mark.parametrize("dead", ["post", "comments", "view", "edit"])
def test_4803_replay_stops_at_the_first_entry_with_no_answer_naming_it_and_keeps_it_and_the_rest(hub, run_cli, dead):
    first = tick("t0", 1) if dead in ("view", "edit") else comment("c0")
    hub.enqueue(comment("a1"), first, comment("b2"), tick("t3", 2))
    hub.dead = {dead}

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 2
    assert hub.left() == [first["key"], "b2", "t3"]
    assert first["key"] in err and err.count("\n") == 1
    assert len(hub.posted) == 1 and hub.posted[0][1].endswith("a1 -->")


def test_4803_replay_holds_the_queue_lock_while_it_posts(hub, run_cli):
    hub.enqueue(comment("a1"))
    seen = []
    hub.during = lambda: seen.append(lock_is_free(hub.root))

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert seen and not any(seen)
    assert lock_is_free(hub.root)


def test_4803_an_append_holds_the_queue_lock_while_it_writes(hub, monkeypatch):
    seen = []
    real_fsync = hub.queue.os.fsync

    def fsync(fd):
        seen.append(lock_is_free(hub.root))
        return real_fsync(fd)

    monkeypatch.setattr(hub.queue.os, "fsync", fsync)

    hub.queue.queue_tick(str(hub.root), "7", 2)

    assert seen == [False]
    assert hub.left() is not None and len(hub.left()) == 1


def test_4803_replay_with_any_other_argument_exits_2_with_the_usage(hub, run_cli):
    code, out, err = run_cli(hub.queue, ["replay", "extra"], cwd=hub.root)

    assert code == 2 and "usage: github-queue.sh replay" in err


def test_4803_replay_of_an_unreadable_line_exits_2_keeping_the_queue(hub, run_cli):
    (hub.root / ".tdd" / "github-queue").write_text("not json\n")

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 2
    assert (hub.root / ".tdd" / "github-queue").read_text() == "not json\n"


def test_4803_the_outage_file_the_queue_checks_is_the_one_github_outage_sh_writes():
    queue = importlib.import_module("veri.github_queue")
    assert queue.OUTAGE_FILE == importlib.import_module("veri.github_outage").FILE


@pytest.mark.parametrize("separator", [" ", " ", "\u0085"])
def test_4803_a_queued_body_holding_a_unicode_line_separator_replays_whole(hub, run_cli, separator):
    hub.queue.queue_comment(str(hub.root), "7", "step-done", "one%stwo" % separator)

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert hub.posted[0][1].startswith("one%stwo" % separator)
    assert hub.left() is None


def test_4803_replay_names_a_tick_whose_criterion_left_the_body_on_stderr_and_drops_it(hub, run_cli):
    hub.enqueue(tick("t1", 5), comment("b2"))

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert "t1" in err and "criterion 5" in err and "#7" in err
    assert hub.edited == [] and len(hub.posted) == 1
    assert hub.left() is None


@pytest.mark.parametrize("answer, counted", [((0, []), False), ((1, ["an incident"]), True)])
def test_4803_incident_counts_only_a_status_read_that_reports_one(monkeypatch, answer, counted):
    monkeypatch.setattr(importlib.import_module("github_status"), "default_read", lambda: answer)

    assert importlib.import_module("veri.github_queue").incident() is counted


def test_4803_replay_of_a_queue_of_blank_lines_only_removes_the_file_and_exits_0(hub, run_cli):
    (hub.root / ".tdd" / "github-queue").write_text("\n\n")

    code, out, err = run_cli(hub.queue, ["replay"], cwd=hub.root)

    assert code == 0, err
    assert not (hub.root / ".tdd" / "github-queue").exists()
    assert hub.posted == []


def test_4803_a_queued_comment_is_redacted_on_disk_so_no_local_path_sits_in_the_queue(hub):
    hub.queue.queue_comment(str(hub.root), "7", "step-done", "see /home/someone/run/.tdd/issue-7.md")

    on_disk = (hub.root / ".tdd" / "github-queue").read_text()
    assert "/home/someone" not in on_disk
    assert "<path>" in on_disk
