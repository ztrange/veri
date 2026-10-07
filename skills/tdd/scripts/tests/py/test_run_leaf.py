"""In-process cases for veri/run_leaf.py, the module run-leaf.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_main_without_a_prompt_argument_refuses_with_the_usage_line_before_any_temp_file_or_launch(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, home, tmp = (tmp_path / name for name in ("work", "home", "tmp"))
    for path in (work, home, tmp):
        path.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(tmp))
    launches = []
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: launches.append((args, kwargs)))

    answers = []
    for argv in ([], [""]):
        code = run_leaf.main(argv)
        captured = capfd.readouterr()
        answers.append((code, captured.out, captured.err))

    usage = "usage: run-leaf.sh <prompt-file|-> [claude args...]\n"
    assert (answers, launches, sorted(tmp.iterdir()), sorted(work.iterdir())) == (
        [(2, "", usage), (2, "", usage)], [], [], [])


class _FakeLeaf:
    def __init__(self, launches, argv, **kwargs):
        launches.append(list(argv))
        read_end, write_end = os.pipe()
        os.close(write_end)
        self.stdout = open(read_end, "rb", buffering=0)
        self.returncode = 0
        self.pid = 0

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.stdout.close()
        return False


def test_main_launches_one_leaf_with_the_prompt_the_model_only_when_non_empty_and_the_callers_arguments_in_order(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, home, tmp = (tmp_path / name for name in ("work", "home", "tmp"))
    for path in (work, home, tmp):
        path.mkdir()
    (work / "prompt.txt").write_text("do the step\n")
    monkeypatch.chdir(work)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(tmp))
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    head = ["-p", "do the step", "--output-format", "stream-json", "--verbose"]

    launched = []
    for claude_bin, model, extra, want in (
            (None, None, [], ["claude", *head]),
            ("", "", ["--x"], ["claude", *head, "--x"]),
            ("/stub/claude", "a model", ["--a", "", "b"],
             ["/stub/claude", *head, "--model", "a model", "--a", "", "b"])):
        for name, value in (("CLAUDE_BIN", claude_bin), ("VERI_LEAF_MODEL", model)):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)
        launches = []
        monkeypatch.setattr(subprocess, "Popen",
                            lambda argv, *args, **kwargs: _FakeLeaf(launches, argv, **kwargs))
        run_leaf.main(["prompt.txt", *extra])
        capfd.readouterr()
        launched.append((launches, [want]))

    assert [got for got, _ in launched] == [want for _, want in launched]
