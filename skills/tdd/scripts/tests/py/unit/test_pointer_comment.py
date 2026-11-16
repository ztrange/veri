"""In-process cases for veri/pointer_comment.py, the module pointer-comment.sh is a shim over."""
import importlib
import json
import re

HEADING = "### 📍 Run state"


class FakeIssue:
    """GitHub as `gh api` sees it for one issue: its comments, the pull requests on the run's branch, and a switch that
    makes every gh call fail. Answers git's branch read and `hostname -s` too."""

    def __init__(self, fake_processes, comments=(), pulls=(), branch="tdd/7-pointer", host="box"):
        self.comments = [{"id": 100 + i, "body": body} for i, body in enumerate(comments)]
        self.pulls = list(pulls)
        self.fail = False
        self.fake = fake_processes.answers({
            "gh": self.gh,
            "git rev-parse --abbrev-ref HEAD": (0, branch + "\n", ""),
            "hostname -s": (0, host + "\n", ""),
        })

    def bodies(self):
        return [c["body"] for c in self.comments if c["body"].startswith(HEADING)]

    def gh(self, line, **kwargs):
        argv = [str(a) for a in self.fake.argvs[-1]]
        if self.fail:
            return 1, "", "gh: Server Error (HTTP 502)\nsecond line of gh's words\n"
        method = argv[argv.index("-X") + 1] if "-X" in argv else "GET"
        path = next(a for a in argv[2:] if a.startswith("repos/"))
        body = next((a[len("body="):] for a in argv if a.startswith("body=")), None)
        if method == "GET":
            page = int(path.rpartition("page=")[2]) if "&page=" in path else 1
            items = self.pulls if "/pulls" in path else self.comments
            return 0, json.dumps(items if page == 1 else []), ""
        if method == "POST" and path.endswith("/comments"):
            self.comments.append({"id": 100 + len(self.comments), "body": body})
            return 0, "{}", ""
        if method == "PATCH" and "/issues/comments/" in path:
            wanted = int(path.rpartition("/")[2])
            for comment in self.comments:
                if comment["id"] == wanted:
                    comment["body"] = body
            return 0, "{}", ""
        raise AssertionError("unexpected gh call: %s" % argv)


def test_veri_machine_name_is_a_tunable_parsed_as_text_with_an_empty_default():
    tunables = importlib.import_module("veri.tunables")
    entry = tunables.TUNABLES.get("VERI_MACHINE_NAME")

    assert (entry is not None and entry.parse is tunables.text, entry and entry.default) == (True, "")


def test_the_comment_states_the_machine_as_veri_machine_name_else_the_short_host_name_when_unset_or_empty(tmp_path, monkeypatch, fake_processes):
    monkeypatch.chdir(tmp_path)
    issue = FakeIssue(fake_processes, host="studio")
    stated = {}
    for case, value in (("named", "lab-1"), ("empty", ""), ("unset", None)):
        if value is None:
            monkeypatch.delenv("VERI_MACHINE_NAME", raising=False)
        else:
            monkeypatch.setenv("VERI_MACHINE_NAME", value)
        _module().main(["7"])
        stated[case] = next(line for line in issue.bodies()[0].splitlines() if line.startswith("Machine:"))

    assert stated == {"named": "Machine: lab-1", "empty": "Machine: studio", "unset": "Machine: studio"}


def _module():
    return importlib.import_module("veri.pointer_comment")


def test_two_calls_leave_exactly_one_run_state_comment_posted_then_edited_in_place(tmp_path, monkeypatch, fake_processes):
    monkeypatch.chdir(tmp_path)
    issue = FakeIssue(fake_processes, comments=["an unrelated comment"])

    first = _module().main(["7"])
    posted = issue.bodies()
    second = _module().main(["7"])

    assert (first, len(posted), second, len(issue.bodies()), len(issue.comments)) == (0, 1, 0, 1, 2)


def test_the_comment_states_the_branch_the_pr_url_or_none_and_the_resume_command(tmp_path, monkeypatch, fake_processes):
    monkeypatch.chdir(tmp_path)
    url = "https://github.com/o/r/pull/9"
    with_pr = FakeIssue(fake_processes, pulls=[{"number": 9, "html_url": url, "head": {"ref": "tdd/7-pointer"}}])
    _module().main(["7"])
    stated = with_pr.bodies()[0].splitlines()
    without = FakeIssue(fake_processes)
    _module().main(["7"])
    bare = without.bodies()[0].splitlines()

    assert ("Branch: tdd/7-pointer" in stated, "PR: " + url in stated, "PR: none" in bare,
            "Resume: $S/run-conductor.sh 7" in stated) == (True, True, True, True)


def test_the_comment_states_the_current_step_as_k_of_n_and_the_phase_of_the_issues_last_event_naming_one(tmp_path, monkeypatch, fake_processes):
    monkeypatch.chdir(tmp_path)
    issue = FakeIssue(fake_processes)
    _module().main(["7"])
    bare = issue.bodies()[0].splitlines()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] one\n- [ ] two\n- [ ] three\n")
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in [
        {"issue": "7", "phase": "green", "event": "leaf-start"},
        {"issue": "7", "phase": "red", "event": "leaf-start"},
        {"issue": "8", "phase": "refactor", "event": "leaf-start"},
        {"issue": "7", "phase": "", "event": "step-start"},
    ]))
    _module().main(["7"])
    stated = issue.bodies()[0].splitlines()

    assert ("Step: none" in bare, "Phase: none" in bare, "Step: 2/3" in stated, "Phase: red" in stated) == (
        True, True, True, True)


def test_the_comment_states_a_push_time_with_its_offset_and_a_write_with_no_push_keeps_the_last_one(tmp_path, monkeypatch, fake_processes):
    monkeypatch.chdir(tmp_path)
    issue = FakeIssue(fake_processes)
    module = _module()
    module.main(["7"])
    never = issue.bodies()[0].splitlines()
    module.write("7", pushed_at=module.now())
    pushed = next(line for line in issue.bodies()[0].splitlines() if line.startswith("Last push: "))
    module.main(["7"])
    kept = issue.bodies()[0].splitlines()

    assert ("Last push: none" in never, bool(re.fullmatch(r"Last push: \d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d", pushed)),
            pushed in kept) == (True, True, True)
