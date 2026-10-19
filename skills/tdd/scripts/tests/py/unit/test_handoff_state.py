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
