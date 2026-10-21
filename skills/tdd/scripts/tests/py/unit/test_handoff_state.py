"""In-process cases for veri/handoff_state.py, the module behind handoff-state.sh."""
import importlib
import json

SHA = "2222222222222222222222222222222222222222"


def test_main_prints_main_sha_and_the_first_tag_git_lists_by_version_as_its_first_line(tmp_path, monkeypatch, run_cli, fake_processes):
    handoff_state = importlib.import_module("veri.handoff_state")
    monkeypatch.chdir(tmp_path)

    def answer(line, **kwargs):
        if line.startswith("git rev-parse") and "main" in line:
            return 0, SHA + "\n", ""
        if line.startswith("git tag"):
            tags = ["v0.10", "v0.9"] if "--sort=-v:refname" in line else ["v0.9", "v0.10"]
            return 0, "".join(tag + "\n" for tag in tags), ""
        return 0, "", ""

    fake_processes(answer)
    code, out, err = run_cli(handoff_state, [])
    assert (code, out.splitlines()[0]) == (0, "main %s v0.10" % SHA)


def test_main_names_none_for_the_tag_on_its_first_line_when_git_lists_no_tags_1819(tmp_path, monkeypatch, run_cli, fake_processes):
    handoff_state = importlib.import_module("veri.handoff_state")
    monkeypatch.chdir(tmp_path)

    def answer(line, **kwargs):
        if line.startswith("git rev-parse") and "main" in line:
            return 0, SHA + "\n", ""
        if line.startswith("gh"):
            return 0, "[]", ""
        return 0, "", ""

    fake_processes(answer)
    code, out, err = run_cli(handoff_state, [])
    assert (code, out.splitlines()[0], "Traceback" in err) == (0, "main %s (none)" % SHA, False)


def test_main_lists_under_running_one_line_per_live_run_and_none_for_any_other_state(tmp_path, monkeypatch, run_cli, fake_processes):
    handoff_state = importlib.import_module("veri.handoff_state")
    status = importlib.import_module("veri.status")
    monkeypatch.chdir(tmp_path)
    runs = [
        {"issue": 41, "title": "Live run alpha", "step": "2 of 5", "phase": "green", "state": "running",
         "dollars": 1.23, "elapsed_seconds": 95},
        {"issue": 42, "title": "Bailed run beta", "step": "1 of 3", "phase": "red", "state": "bailed",
         "dollars": 4.56, "elapsed_seconds": 7777},
        {"issue": 43, "title": "Stale run gamma", "step": "3 of 4", "phase": "refactor", "state": "stale",
         "dollars": 7.89, "elapsed_seconds": 8888},
    ]
    document = json.dumps({"runs": runs, "scope": None})

    def answer(line, **kwargs):
        if line.startswith("git rev-parse"):
            return 0, SHA + "\n", ""
        if line.startswith("git tag"):
            return 0, "v0.9\n", ""
        if "status.sh" in line:
            return 0, document, ""
        return 0, "", ""

    fake_processes(answer)
    monkeypatch.setattr(status, "json_document", lambda scope=None: (0, document))
    code, out, err = run_cli(handoff_state, [])
    lines = out.splitlines()
    section = lines[lines.index("## Running") + 1:] if "## Running" in lines else []
    section = section[:next((i for i, line in enumerate(section) if line.startswith("## ")), len(section))]
    live = section[0] if len(section) == 1 else ""
    assert (code, len(section), all(word in live for word in ("41", "Live run alpha", "2 of 5", "green", "1.23", "95")),
            any(word in out for word in ("Bailed run beta", "Stale run gamma"))) == (0, 1, True, False)


def test_main_lists_under_parked_each_bailed_stopped_or_stale_run_with_an_open_pr_and_its_reason(tmp_path, monkeypatch, run_cli, fake_processes):
    handoff_state = importlib.import_module("veri.handoff_state")
    status = importlib.import_module("veri.status")
    monkeypatch.chdir(tmp_path)
    runs = [
        {"issue": 51, "title": "Bailed with pr", "branch": "tdd/51-a", "step": "1 of 3", "phase": "red", "state": "bailed",
         "bail_phase": "verify-green", "classification": "process-failure", "stop_mode": "", "dollars": 1, "elapsed_seconds": 1},
        {"issue": 52, "title": "Stopped with pr", "branch": "tdd/52-b", "step": "1 of 3", "phase": "red", "state": "stopped",
         "bail_phase": "", "classification": "", "stop_mode": "drain", "dollars": 1, "elapsed_seconds": 1},
        {"issue": 53, "title": "Stale with pr", "branch": "tdd/53-c", "step": "1 of 3", "phase": "red", "state": "stale",
         "bail_phase": "", "classification": "", "stop_mode": "", "dollars": 1, "elapsed_seconds": 1},
        {"issue": 54, "title": "Bailed without pr", "branch": "tdd/54-d", "step": "1 of 3", "phase": "red", "state": "bailed",
         "bail_phase": "develop-red", "classification": "system-failure", "stop_mode": "", "dollars": 1, "elapsed_seconds": 1},
    ]
    document = json.dumps({"runs": runs, "scope": None})
    open_pr = {"tdd/51-a": 101, "tdd/52-b": 102, "tdd/53-c": 103}

    def answer(line, **kwargs):
        if line.startswith("git rev-parse"):
            return 0, SHA + "\n", ""
        if line.startswith("git tag"):
            return 0, "v0.9\n", ""
        if line.startswith("gh"):
            found = [{"number": n} for branch, n in open_pr.items() if branch in line]
            return 0, json.dumps(found), ""
        return 0, "", ""

    fake_processes(answer)
    monkeypatch.setattr(status, "json_document", lambda scope=None: (0, document))
    code, out, err = run_cli(handoff_state, [])
    lines = out.splitlines()
    section = lines[lines.index("## Parked") + 1:] if "## Parked" in lines else []
    section = section[:next((i for i, line in enumerate(section) if line.startswith("## ")), len(section))]

    def has(line, *words):
        return all(word in line for word in words)

    assert (code, len(section), has(section[0], "51", "bailed", "verify-green", "process-failure"),
            has(section[1], "52", "stopped", "drain"), has(section[2], "53", "stale"),
            "Bailed without pr" in out or "54" in " ".join(section)) == (0, 3, True, True, True, False)


def test_main_lists_under_ready_to_merge_each_open_non_draft_pr_that_closes_an_issue_and_no_other(tmp_path, monkeypatch, run_cli, fake_processes):
    handoff_state = importlib.import_module("veri.handoff_state")
    status = importlib.import_module("veri.status")
    monkeypatch.chdir(tmp_path)
    document = json.dumps({"runs": [], "scope": None})
    prs = [
        {"number": 201, "isDraft": False, "body": "Summary\n\nCloses #301", "title": "Ready one"},
        {"number": 202, "isDraft": True, "body": "Closes #302", "title": "Draft two"},
        {"number": 203, "isDraft": False, "body": "Refactor only, no issue", "title": "Plain three"},
    ]

    def answer(line, **kwargs):
        if line.startswith("git rev-parse"):
            return 0, SHA + "\n", ""
        if line.startswith("git tag"):
            return 0, "v0.9\n", ""
        if line.startswith("gh"):
            return 0, json.dumps(prs), ""
        return 0, "", ""

    fake_processes(answer)
    monkeypatch.setattr(status, "json_document", lambda scope=None: (0, document))
    code, out, err = run_cli(handoff_state, [])
    lines = out.splitlines()
    section = lines[lines.index("## Ready to merge") + 1:] if "## Ready to merge" in lines else []
    section = section[:next((i for i, line in enumerate(section) if line.startswith("## ")), len(section))]
    ready = section[0] if len(section) == 1 else ""
    assert (code, len(section), "201" in ready and "301" in ready,
            any(word in out for word in ("202", "302", "203"))) == (0, 1, True, False)


def test_main_writes_no_file_and_makes_only_read_calls_to_github(tmp_path, monkeypatch, run_cli, fake_processes):
    handoff_state = importlib.import_module("veri.handoff_state")
    status = importlib.import_module("veri.status")
    monkeypatch.chdir(tmp_path)
    runs = [
        {"issue": 61, "title": "Live", "branch": "tdd/61-a", "step": "1 of 2", "phase": "red", "state": "running",
         "dollars": 1, "elapsed_seconds": 1},
        {"issue": 62, "title": "Bailed", "branch": "tdd/62-b", "step": "1 of 2", "phase": "red", "state": "bailed",
         "bail_phase": "verify-red", "classification": "process-failure", "stop_mode": "", "dollars": 1, "elapsed_seconds": 1},
    ]
    document = json.dumps({"runs": runs, "scope": None})
    prs = [{"number": 211, "isDraft": False, "body": "Closes #311", "title": "Ready"}]

    def answer(line, **kwargs):
        if line.startswith("git rev-parse"):
            return 0, SHA + "\n", ""
        if line.startswith("git tag"):
            return 0, "v0.9\n", ""
        if line.startswith("gh"):
            return 0, json.dumps(prs), ""
        return 0, "", ""

    calls = fake_processes(answer)
    monkeypatch.setattr(status, "json_document", lambda scope=None: (0, document))
    code, out, err = run_cli(handoff_state, [])
    writes = [line for line in calls if line.startswith("gh") and (
        any(flag in line.split() for flag in ("-X", "--method", "-f", "-F", "--field", "--raw-field", "--input"))
        or any(verb in line.split()[:3] for verb in ("create", "edit", "merge", "close", "comment", "review", "ready")))]
    git_writes = [line for line in calls if line.startswith("git") and line.split()[1] not in ("rev-parse", "tag")]
    assert (code, "## Ready to merge" in out, writes, git_writes, sorted(tmp_path.iterdir())) == (0, True, [], [], [])


def test_main_reads_parked_and_ready_prs_over_the_rest_pulls_route_and_starts_no_gh_pr_1974(tmp_path, monkeypatch, run_cli, fake_processes):
    handoff_state = importlib.import_module("veri.handoff_state")
    status = importlib.import_module("veri.status")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    runs = [
        {"issue": 62, "title": "Bailed", "branch": "tdd/62-b", "step": "1 of 2", "phase": "red", "state": "bailed",
         "bail_phase": "verify-red", "classification": "process-failure", "stop_mode": "", "dollars": 1, "elapsed_seconds": 1},
        {"issue": 63, "title": "Bailed too", "branch": "tdd/63-c", "step": "1 of 2", "phase": "red", "state": "bailed",
         "bail_phase": "verify-red", "classification": "process-failure", "stop_mode": "", "dollars": 1, "elapsed_seconds": 1},
    ]
    document = json.dumps({"runs": runs, "scope": None})
    prs = [
        {"number": 212, "draft": False, "body": "Closes #312", "head": {"ref": "tdd/62-b"}},
        {"number": 213, "draft": True, "body": "Closes #313", "head": {"ref": "tdd/64-d"}},
    ]

    def answer(line, **kwargs):
        if line.startswith("git rev-parse"):
            return 0, SHA + "\n", ""
        if line.startswith("git tag"):
            return 0, "v0.9\n", ""
        if line.startswith("gh api") and "/pulls" in line and "state=open" in line:
            if "page=2" in line:
                return 0, "[]\n", ""
            wanted = [pr for pr in prs if "head=" not in line or pr["head"]["ref"] in line]
            return 0, json.dumps(wanted) + "\n", ""
        return 1, "", "no such route"

    calls = fake_processes(answer)
    monkeypatch.setattr(status, "json_document", lambda scope=None: (0, document))
    code, out, err = run_cli(handoff_state, [])
    lines = out.splitlines()
    parked = lines[lines.index("## Parked") + 1:lines.index("## Ready to merge")]
    ready = lines[lines.index("## Ready to merge") + 1:]
    started_pr = [line for line in calls if line.startswith("gh pr")]
    assert (code, started_pr, parked, ready) == (
        0, [], ["#62 bailed verify-red process-failure"], ["PR #212 closes #312"])


def test_main_reads_its_open_prs_from_the_gh_json_fixture_and_starts_no_gh_1974(tmp_path, monkeypatch, run_cli, fake_processes):
    handoff_state = importlib.import_module("veri.handoff_state")
    status = importlib.import_module("veri.status")
    monkeypatch.chdir(tmp_path)
    fixtures = tmp_path / "gh"
    fixtures.mkdir()
    monkeypatch.setenv("VERI_GH_JSON", str(fixtures))
    prs = [
        {"number": 212, "isDraft": False, "body": "Closes #312"},
        {"number": 213, "isDraft": True, "body": "Closes #313"},
    ]
    (fixtures / "prs.json").write_text(json.dumps(prs))

    def answer(line, **kwargs):
        if line.startswith("git rev-parse"):
            return 0, SHA + "\n", ""
        if line.startswith("git tag"):
            return 0, "v0.9\n", ""
        if line.startswith("gh") and "page=2" in line:
            return 0, "[]\n", ""
        if line.startswith("gh"):
            return 0, json.dumps([{"number": 999, "isDraft": False, "draft": False, "body": "Closes #998"}]) + "\n", ""
        return 1, "", "no such route"

    calls = fake_processes(answer)
    monkeypatch.setattr(status, "json_document", lambda scope=None: (0, json.dumps({"runs": [], "scope": None})))
    code, out, err = run_cli(handoff_state, [])
    lines = out.splitlines()
    ready = lines[lines.index("## Ready to merge") + 1:]
    started_gh = [line for line in calls if line.startswith("gh")]
    assert (code, started_gh, ready) == (0, [], ["PR #212 closes #312"])
