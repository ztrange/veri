"""In-process cases for veri/handoff_state.py, the module behind handoff-state.sh."""
import importlib

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
