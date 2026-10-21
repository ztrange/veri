"""Cases for run_finished's PR body read, in-process."""
import importlib
import json


def test_main_reads_the_pr_body_over_the_rest_pulls_route_and_starts_no_gh_pr_1974(tmp_path, monkeypatch, run_cli, fake_processes):
    run_finished = importlib.import_module("veri.run_finished")
    ledger = tmp_path / ".tdd" / "wt" / "4242" / ".tdd"
    ledger.mkdir(parents=True)
    (ledger / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n- [x] first step ⟦criterion 1⟧\n")
    run = {"issue": "4242", "state": "done", "pr": "https://github.com/o/r/pull/7"}
    monkeypatch.setattr(run_finished, "main_working_tree", lambda: str(tmp_path))
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
    monkeypatch.setattr(run_finished, "main_working_tree", lambda: str(tmp_path))
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
    monkeypatch.setattr(run_finished, "main_working_tree", lambda: str(tmp_path))
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
    monkeypatch.setattr(run_finished, "main_working_tree", lambda: str(tmp_path))
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
    monkeypatch.setattr(run_finished, "main_working_tree", lambda: str(tmp_path))
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
