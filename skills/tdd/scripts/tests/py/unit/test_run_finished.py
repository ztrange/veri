"""Cases for run_finished's PR body read, in-process."""
import importlib
import json
import re


def test_main_reads_the_pr_body_over_the_rest_pulls_route_and_starts_no_gh_pr_1974(tmp_path, monkeypatch, run_cli, fake_processes):
    run_finished = importlib.import_module("veri.run_finished")
    ledger = tmp_path / ".tdd" / "wt" / "4242" / ".tdd"
    ledger.mkdir(parents=True)
    (ledger / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n- [x] first step ⟦criterion 1⟧\n")
    run = {"issue": "4242", "state": "done", "pr": "https://github.com/o/r/pull/7"}
    monkeypatch.setattr(run_finished.layout, "main_tree", lambda **_: str(tmp_path))
    monkeypatch.setattr(run_finished, "json_document", lambda scope=None: (0, json.dumps({"runs": [run]})))
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    body = "Closes #4242\n\n- [ ] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧"

    def answer(line, **kwargs):
        if line.startswith("gh api repos/{owner}/{repo}/pulls/7"):
            return 0, json.dumps({"number": 7, "body": body}) + "\n", ""
        return 1, "", "no such route"

    calls = fake_processes(answer)
    code, out, err = run_cli(run_finished, ["4242"])
    started_pr = [line for line in calls if line.startswith("gh pr")]
    assert (code, started_pr, out) == (
        1, [], "human-owed a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧\n")


def test_main_reads_the_pr_body_from_the_gh_json_fixture_and_starts_no_gh_1974(tmp_path, monkeypatch, run_cli, fake_processes):
    run_finished = importlib.import_module("veri.run_finished")
    ledger = tmp_path / ".tdd" / "wt" / "4242" / ".tdd"
    ledger.mkdir(parents=True)
    (ledger / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n- [x] first step ⟦criterion 1⟧\n")
    run = {"issue": "4242", "state": "done", "pr": "https://github.com/o/r/pull/7"}
    monkeypatch.setattr(run_finished.layout, "main_tree", lambda **_: str(tmp_path))
    monkeypatch.setattr(run_finished, "json_document", lambda scope=None: (0, json.dumps({"runs": [run]})))
    fixtures = tmp_path / "gh"
    fixtures.mkdir()
    monkeypatch.setenv("VERI_GH_JSON", str(fixtures))
    body = "Closes #4242\n\n- [ ] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧"
    (fixtures / "pr.json").write_text(json.dumps({"number": 7, "body": body}))

    def answer(line, **kwargs):
        if line.startswith("gh"):
            return 0, json.dumps({"body": "Closes #4242"}) + "\n", ""
        return 1, "", "no such route"

    calls = fake_processes(answer)
    code, out, err = run_cli(run_finished, ["4242"])
    started_gh = [line for line in calls if line.startswith("gh")]
    assert (code, started_gh, out) == (
        1, [], "human-owed a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧\n")


def test_main_reads_the_pr_body_over_gh_pr_view_with_the_driver_graphql_and_answers_as_under_rest_1974(tmp_path, monkeypatch, run_cli, fake_processes):
    run_finished = importlib.import_module("veri.run_finished")
    ledger = tmp_path / ".tdd" / "wt" / "4242" / ".tdd"
    ledger.mkdir(parents=True)
    (ledger / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n- [x] first step ⟦criterion 1⟧\n")
    run = {"issue": "4242", "state": "done", "pr": "https://github.com/o/r/pull/7"}
    monkeypatch.setattr(run_finished.layout, "main_tree", lambda **_: str(tmp_path))
    monkeypatch.setattr(run_finished, "json_document", lambda scope=None: (0, json.dumps({"runs": [run]})))
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    body = "Closes #4242\n\n- [ ] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧"

    def answer(line, **kwargs):
        if line.startswith("gh pr view https://github.com/o/r/pull/7") and "body" in line:
            return 0, (body + "\n" if "-q" in line else json.dumps({"body": body}) + "\n"), ""
        return 1, "", "no such route"

    fake_processes(answer)
    code, out, err = run_cli(run_finished, ["4242"])
    assert (code, out) == (1, "human-owed a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧\n")


def test_main_falls_back_to_the_rest_pulls_route_when_gh_pr_view_is_refused_with_the_driver_auto_1974(tmp_path, monkeypatch, run_cli, fake_processes):
    run_finished = importlib.import_module("veri.run_finished")
    ledger = tmp_path / ".tdd" / "wt" / "4242" / ".tdd"
    ledger.mkdir(parents=True)
    (ledger / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n- [x] first step ⟦criterion 1⟧\n")
    run = {"issue": "4242", "state": "done", "pr": "https://github.com/o/r/pull/7"}
    monkeypatch.setattr(run_finished.layout, "main_tree", lambda **_: str(tmp_path))
    monkeypatch.setattr(run_finished, "json_document", lambda scope=None: (0, json.dumps({"runs": [run]})))
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    body = "Closes #4242\n\n- [ ] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧"

    def answer(line, **kwargs):
        if line.startswith("gh api repos/{owner}/{repo}/pulls/7"):
            return 0, json.dumps({"number": 7, "body": body}) + "\n", ""
        return 1, "", "GraphQL: refused"

    calls = fake_processes(answer)
    code, out, err = run_cli(run_finished, ["4242"])
    tried = [line.split()[1] for line in calls if line.startswith("gh")]
    assert (code, out, tried[0], "api" in tried) == (
        1, "human-owed a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧\n", "pr", True)


def test_main_exits_2_saying_the_pr_body_could_not_be_read_when_gh_answers_non_zero_or_no_pr_body_under_every_driver_1974(tmp_path, monkeypatch, run_cli, fake_processes):
    run_finished = importlib.import_module("veri.run_finished")
    ledger = tmp_path / ".tdd" / "wt" / "4242" / ".tdd"
    ledger.mkdir(parents=True)
    (ledger / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n- [x] first step ⟦criterion 1⟧\n")
    run = {"issue": "4242", "state": "done", "pr": "https://github.com/o/r/pull/7"}
    monkeypatch.setattr(run_finished.layout, "main_tree", lambda **_: str(tmp_path))
    monkeypatch.setattr(run_finished, "json_document", lambda scope=None: (0, json.dumps({"runs": [run]})))
    answers = {"refused": (1, "", "HTTP 403"), "not json": (0, "<html>oops</html>\n", ""),
               "no body": (0, json.dumps({"number": 7}) + "\n", "")}
    outcomes = {}
    for driver in ("rest", "graphql", "auto"):
        monkeypatch.setenv("VERI_GH_DRIVER", driver)
        for name, reply in answers.items():
            fake_processes(lambda line, **kwargs: reply)
            code, out, err = run_cli(run_finished, ["4242"])
            outcomes[driver, name] = (code, out, "the PR body could not be read" in err, "Traceback" in err)
    assert outcomes == {key: (2, "", True, False) for key in outcomes}


def test_main_lists_a_pr_body_line_human_owed_only_for_a_leading_or_trailing_mark_not_one_quoted_mid_prose_2288(tmp_path, monkeypatch, run_cli, fake_processes):
    run_finished = importlib.import_module("veri.run_finished")
    ledger = tmp_path / ".tdd" / "wt" / "4242" / ".tdd"
    ledger.mkdir(parents=True)
    (ledger / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n- [x] first step ⟦criterion 1⟧\n")
    run = {"issue": "4242", "state": "done", "pr": "https://github.com/o/r/pull/7"}
    monkeypatch.setattr(run_finished.layout, "main_tree", lambda **_: str(tmp_path))
    monkeypatch.setattr(run_finished, "json_document", lambda scope=None: (0, json.dumps({"runs": [run]})))
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    body = "\n".join(["Closes #4242", "", "- [ ] a ⟦human-owed⟧ x",
                      "- [ ] measure X ⟦human-owed⟧", "- [ ] ⟦human-owed⟧ measure X"])

    def answer(line, **kwargs):
        if line.startswith("gh api repos/{owner}/{repo}/pulls/7"):
            return 0, json.dumps({"number": 7, "body": body}) + "\n", ""
        return 1, "", "no such route"

    fake_processes(answer)
    code, out, err = run_cli(run_finished, ["4242"])
    assert (code, out) == (1, "human-owed measure X ⟦human-owed⟧\nhuman-owed ⟦human-owed⟧ measure X\n")


# main through run_cli as `run-finished.sh 4242`, run from a repository holding the run under .tdd/wt/4242, its state derived
# by status from the run's events. git and gh are faked at their process boundary: git names `repo` the main working tree
# and the run's branch `main`; gh answers every call as GH says (by default, the PR body BODY holds).

LAUNCH = '{"ts":%s,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}'
DONE = '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}'
STEP = "- [x] first step ⟦criterion 1⟧\n"


def make_run(tmp_path, events, steps=STEP):
    repo = tmp_path / "repo"
    run = repo / ".tdd" / "wt" / "4242" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text("".join(e + "\n" for e in events))
    (run / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n" + steps)
    return repo


def finish_with_gh(run_cli, fake_processes, repo, gh):
    fake = fake_processes.answers({"git worktree list --porcelain": (0, "worktree %s\n" % repo, ""),
                                   "git -C %s symbolic-ref --short HEAD" % (repo / ".tdd" / "wt" / "4242"): (0, "main\n", ""),
                                   "gh": gh})
    return (*run_cli(importlib.import_module("veri.run_finished"), ["4242"], cwd=repo), fake)


def finish(run_cli, fake_processes, repo, body=None):
    gh = (0, json.dumps({"body": body}) + "\n", "") if body is not None else AssertionError("gh started")
    return finish_with_gh(run_cli, fake_processes, repo, gh)[:3]


def test_an_issue_with_no_run_exits_2_and_says_on_stderr_there_is_no_run_for_it(tmp_path, run_cli, fake_processes):
    repo = tmp_path / "repo"
    (repo / ".tdd" / "wt").mkdir(parents=True)

    code, _, err = finish(run_cli, fake_processes, repo)

    assert code == 2
    assert "no run for issue 4242" in err


def assert_done_and_silent(tmp_path, run_cli, fake_processes, body, steps=STEP):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE], steps)

    assert finish(run_cli, fake_processes, repo, body) == (0, "", "")


def assert_not_done(tmp_path, run_cli, fake_processes, events, state):
    repo = make_run(tmp_path, events)

    code, out, _ = finish(run_cli, fake_processes, repo)

    assert code == 1
    assert out.startswith("not-done %s" % state)


def test_a_done_run_with_every_step_ticked_and_its_human_owed_line_ticked_exits_0_and_prints_nothing(tmp_path, run_cli, fake_processes):
    assert_done_and_silent(
        tmp_path, run_cli, fake_processes, "Closes #4242\n\n- [x] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧",
        STEP + "- [x] second step ⟦criterion 2⟧\n")


def test_a_done_run_whose_pr_body_holds_an_unticked_checkbox_that_is_not_human_owed_exits_0_and_prints_nothing(
        tmp_path, run_cli, fake_processes):
    assert_done_and_silent(tmp_path, run_cli, fake_processes, "Closes #4242\n\n- [ ] a follow-up someone may file later")


def test_a_done_run_whose_pr_body_holds_star_bulleted_and_indented_checkboxes_exits_0_and_prints_nothing(tmp_path, run_cli, fake_processes):
    assert_done_and_silent(
        tmp_path, run_cli, fake_processes,
        "Closes #4242\n\n* [ ] a star-bulleted follow-up someone may file later\n"
        "  - [ ] an indented follow-up someone may file later\n"
        "  - [x] a reviewer checked the indented page ⟦human-owed⟧ ⟦criterion 3⟧")


def test_a_stopped_run_with_a_clean_ledger_exits_1_and_prints_a_not_done_line_naming_stopped(tmp_path, run_cli, fake_processes):
    assert_not_done(tmp_path, run_cli, fake_processes,
                    [LAUNCH % 1000, '{"ts":1001,"event":"stop","mode":"graceful"}'], "stopped")


def test_a_run_whose_state_is_not_done_exits_1_and_prints_a_not_done_line_naming_the_state(tmp_path, run_cli, fake_processes):
    assert_not_done(
        tmp_path, run_cli, fake_processes,
        [LAUNCH % 1000, '{"ts":1001,"event":"bail","phase":"red","classification":"process"}'], "bailed")


def test_a_stale_run_exits_1_and_prints_a_not_done_line_naming_the_stale_state(tmp_path, run_cli, fake_processes):
    assert_not_done(tmp_path, run_cli, fake_processes, [LAUNCH % 1000], "stale")


def test_a_done_run_whose_ledger_has_unchecked_steps_exits_1_and_prints_one_unchecked_line_per_step(tmp_path, run_cli, fake_processes):
    steps = STEP + "- [ ] second step ⟦criterion 2⟧\n- [ ] third step ⟦criterion 3⟧\n"
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE], steps)

    code, out, _ = finish(run_cli, fake_processes, repo, "Closes #4242")

    lines = out.splitlines()
    assert code == 1
    assert len(lines) == 2
    assert lines[0].startswith("unchecked ") and "second step" in lines[0]
    assert lines[1].startswith("unchecked ") and "third step" in lines[1]
    assert "first step" not in out


def test_a_done_run_whose_ledger_has_a_step_still_refactor_pending_exits_1_and_prints_one_refactor_pending_line_per_such_step(
        tmp_path, run_cli, fake_processes):
    steps = (STEP + "- [x] second step ⟦criterion 2⟧ ⟂ refactor pending\n"
             "- [x] third step ⟦criterion 3⟧ ⟂ refactor pending\n")
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE], steps)

    code, out, _ = finish(run_cli, fake_processes, repo, "Closes #4242")

    lines = out.splitlines()
    assert code == 1
    assert len(lines) == 2
    assert lines[0].startswith("refactor-pending ") and "second step" in lines[0]
    assert lines[1].startswith("refactor-pending ") and "third step" in lines[1]
    assert "first step" not in out


def test_a_done_run_whose_pr_body_holds_unticked_human_owed_lines_exits_1_and_prints_one_human_owed_line_per_unticked_line(
        tmp_path, run_cli, fake_processes):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])
    body = ("Closes #4242\n\n- [ ] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧\n"
            "- [x] a reviewer checks the ticked one ⟦human-owed⟧ ⟦criterion 4⟧\n"
            "- [ ] a reviewer reads the docs ⟦human-owed⟧ ⟦criterion 5⟧")

    code, out, _ = finish(run_cli, fake_processes, repo, body)

    lines = out.splitlines()
    assert code == 1
    assert len(lines) == 2
    assert lines[0].startswith("human-owed ") and "checks the page" in lines[0]
    assert lines[1].startswith("human-owed ") and "reads the docs" in lines[1]
    assert "ticked one" not in out


def test_a_done_run_whose_pr_body_cannot_be_read_exits_2_and_says_on_stderr_the_pr_body_could_not_be_read(tmp_path, run_cli, fake_processes):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])

    code, _, err, _ = finish_with_gh(run_cli, fake_processes, repo, (1, "", "gh: HTTP 502\n"))

    assert code == 2
    assert "PR body" in err


def tree_digest(repo):
    return {str(path): path.read_bytes() for path in sorted(repo.rglob("*")) if path.is_file()}


def test_a_run_of_it_changes_no_file_in_the_repository_and_every_gh_call_it_makes_is_a_read(tmp_path, run_cli, fake_processes):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE], STEP + "- [ ] second step ⟦criterion 2⟧\n")
    before = tree_digest(repo)

    *_, fake = finish_with_gh(run_cli, fake_processes, repo, (0, '{"body": "Closes #4242"}\n', ""))

    assert tree_digest(repo) == before
    made = [call[len("gh "):] for call in fake.calls if call.startswith("gh ")]
    assert made
    for call in made:
        assert call.startswith("pr view ") or re.fullmatch(r"api repos/\S+/pulls/\d+", call)
        for write in ("POST", "PATCH", "PUT", "DELETE", "-X", "--method", "--input", "-f ", "-F "):
            assert write.lower() not in call.lower()
    assert [c for c in fake.calls if c.startswith("git ")] == [
        "git worktree list --porcelain", "git worktree list --porcelain",
        "git -C %s symbolic-ref --short HEAD" % (repo / ".tdd" / "wt" / "4242")]


def test_a_done_run_with_an_empty_recorded_pr_url_exits_2_with_one_stderr_line_saying_no_pr_is_recorded_and_never_calls_gh_pr_view(
        tmp_path, run_cli, fake_processes):
    repo = make_run(tmp_path, [LAUNCH % 1000, '{"ts":1001,"event":"done","pr":""}'])

    code, _, err, fake = finish_with_gh(run_cli, fake_processes, repo, (0, '{"body": "Closes #4242"}\n', ""))

    assert code == 2
    assert "no PR" in err
    assert len(err.splitlines()) == 1
    assert not [c for c in fake.calls if c.startswith("gh ")]


def test_a_done_run_whose_pr_body_holds_an_indented_unticked_human_owed_checkbox_exits_1_and_prints_its_human_owed_line(
        tmp_path, run_cli, fake_processes):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])

    code, out, _ = finish(
        run_cli, fake_processes, repo, "Closes #4242\n\n  - [ ] a reviewer checks the nested page ⟦human-owed⟧ ⟦criterion 3⟧")

    assert code == 1
    assert out.startswith("human-owed ") and "checks the nested page" in out


def test_a_done_run_whose_pr_body_holds_a_star_bulleted_unticked_human_owed_checkbox_exits_1_and_prints_its_human_owed_line(
        tmp_path, run_cli, fake_processes):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])

    code, out, _ = finish(
        run_cli, fake_processes, repo, "Closes #4242\n\n* [ ] a reviewer checks the starred page ⟦human-owed⟧ ⟦criterion 3⟧")

    assert code == 1
    assert out.startswith("human-owed ") and "checks the starred page" in out


def test_a_done_run_whose_ledger_is_missing_exits_2_with_one_stderr_line_naming_the_file_and_no_traceback(tmp_path, run_cli, fake_processes):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])
    (repo / ".tdd" / "wt" / "4242" / ".tdd" / "issue-4242.md").unlink()

    code, _, err = finish(run_cli, fake_processes, repo, "Closes #4242")

    assert code == 2
    assert "issue-4242.md" in err
    assert len(err.splitlines()) == 1
    assert "Traceback" not in err


def test_a_done_run_whose_mutation_record_names_old_text_its_file_no_longer_holds_exits_1_with_one_stale_pin_line_per_live_entry_4513(
        tmp_path, run_cli, fake_processes):
    mutation_record = importlib.import_module("veri.mutation_record")
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])
    worktree = repo / ".tdd" / "wt" / "4242"
    (worktree / "lib").mkdir()
    (worktree / "lib" / "calc.py").write_text("def add(a, b):\n    return a + b\n")
    (worktree / ".tdd" / "issue-4242-mutations.md").write_text(
        mutation_record.format_record([("file", "lib/calc.py"), ("old", "    return a - b\n"), ("new", "    return 0\n")])
        + mutation_record.format_record([("file", "lib/calc.py"), ("old", "    return a * b\n"), ("new", "    return 0\n"),
                                         ("retired", "superseded")])
        + mutation_record.format_record([("file", "lib/calc.py"), ("old", "    return a + b\n"), ("new", "    return 0\n")]))

    code, out, _ = finish(run_cli, fake_processes, repo, "Closes #4242")

    assert (code, out.splitlines()) == (1, ["stale-pin lib/calc.py return a - b"])


def test_a_before_entry_and_an_entry_whose_file_is_gone_add_no_stale_pin_line_and_the_hint_names_the_record_4513(
        tmp_path, run_cli, fake_processes):
    mutation_record = importlib.import_module("veri.mutation_record")
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])
    worktree = repo / ".tdd" / "wt" / "4242"
    (worktree / "lib").mkdir()
    (worktree / "lib" / "calc.py").write_text("def add(a, b):\n    return a + b\n")
    (worktree / ".tdd" / "issue-4242-mutations.md").write_text(
        mutation_record.format_record([("before", "abc1234"), ("keep", "1"), ("command", "make test")])
        + mutation_record.format_record([("file", "lib/gone.py"), ("old", "    return 1\n"), ("new", "    return 0\n")])
        + mutation_record.format_record([("file", "lib/calc.py"), ("old", "    return a - b\n"), ("new", "    return 0\n")]))

    code, out, err = finish(run_cli, fake_processes, repo, "Closes #4242")

    assert (code, out.splitlines(), err.splitlines()) == (1, ["stale-pin lib/calc.py return a - b"], [
        "run-finished.sh: retire a stale pin's entry (a `retired <reason>` field) in %s" % (worktree / ".tdd" / "issue-4242-mutations.md")])
