"""In-process cases for veri/render_leaf_log.py, the module render-leaf-log.sh is a shim over."""
import importlib
import io
import json
import pathlib
import subprocess
import sys

import pytest


@pytest.fixture
def render_leaf_log():
    return importlib.import_module("veri.render_leaf_log")


def test_main_discards_the_records_already_rendered_and_returns_2_on_a_line_that_is_not_json(monkeypatch, capsys, render_leaf_log):
    record = {"type": "assistant", "message": {"content": [{"type": "text", "text": "hello"}]}}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(record) + "\nnot json at all\n"))
    code = render_leaf_log.main([])
    assert (code, capsys.readouterr().out) == (2, "")


def test_main_renders_text_tool_calls_and_truncated_results_one_per_line_and_returns_0(monkeypatch, capsys, render_leaf_log):
    fixture = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "render-leaf-log" / "leaf.out"
    monkeypatch.setattr(sys, "stdin", io.StringIO(fixture.read_text(encoding="utf-8")))
    code = render_leaf_log.main([])
    assert (code, capsys.readouterr().out) == (0, (
        "Reading the suite before adding the case.\n"
        "> Bash: cat skills/tdd/scripts/tests/extract-result.test.sh\n"
        "< #!/usr/bin/env bash…\n"
        "> Read: /repo/README.md\n"
        "< # veri — a Claude Code skill suite that solves one GitHub issue under strict TDD…\n"
        "> Bash: make test\n"
        "< 3 passed, 0 failed\n"
        "The case is added and fails as predicted.\n"
    ))


def test_main_keeps_the_quirks_of_the_bash_it_was_ported_from(monkeypatch, capsys, render_leaf_log):
    def run(stdin, argv=()):
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
        code = render_leaf_log.main(list(argv))
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    def record(*blocks):
        return json.dumps({"type": "assistant", "message": {"content": list(blocks)}}) + "\n"

    assert run("\n") == (2, "", "render-leaf-log.sh: not JSON: \n")
    assert run("not json at all\n") == (2, "", "render-leaf-log.sh: not JSON: not json at all\n")
    for stdin in ("[1, 2]\n", record({"type": "text"}), record({"type": "tool_use", "input": {"command": "ls"}})):
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
        with pytest.raises(Exception):
            render_leaf_log.main([])
    capsys.readouterr()
    content = [{"type": "text", "text": "x"}]
    assert run(record({"type": "tool_result", "content": content})) == (0, "< " + str(content) + "\n", "")
    assert run(record({"type": "tool_use", "name": "Bash", "input": {}})) == (0, "> Bash: \n", "")
    assert run(record({"type": "text", "text": "one\ntwo"})) == (0, "one\ntwo\n", "")
    assert run(record({"type": "text", "text": "hello"}), ["--extra", "arg"]) == (0, "hello\n", "")


LEAF_OUT = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "render-leaf-log" / "leaf.out"
SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
RENDERED_LEAF_OUT = (
    "Reading the suite before adding the case.\n"
    "> Bash: cat skills/tdd/scripts/tests/extract-result.test.sh\n"
    "< #!/usr/bin/env bash…\n"
    "> Read: /repo/README.md\n"
    "< # veri — a Claude Code skill suite that solves one GitHub issue under strict TDD…\n"
    "> Bash: make test\n"
    "< 3 passed, 0 failed\n"
    "The case is added and fails as predicted.\n"
)


def test_cli_renders_text_tool_calls_and_truncated_results_one_per_line(run_cli, render_leaf_log):
    assert run_cli(render_leaf_log, [], stdin=LEAF_OUT.read_text(encoding="utf-8")) == (0, RENDERED_LEAF_OUT, "")


def test_cli_exits_2_with_nothing_on_stdout_on_a_line_that_is_not_json(run_cli, render_leaf_log):
    record = json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "hi"}]}})
    assert run_cli(render_leaf_log, [], stdin=record + "\nnot json at all\n") == (
        2, "", "render-leaf-log.sh: not JSON: not json at all\n")


def test_cli_exits_2_on_a_json_line_that_is_not_an_object_and_ignores_an_extra_argument_rendering_the_stdin_with_exit_0(
        run_cli, render_leaf_log):
    code, out, err = run_cli(render_leaf_log, [], stdin="[1, 2]\n")
    assert (code, out) == (2, "")
    assert err.startswith("render-leaf-log.sh: ")
    assert run_cli(render_leaf_log, ["extra-arg"], stdin=LEAF_OUT.read_text(encoding="utf-8")) == (0, RENDERED_LEAF_OUT, "")


@pytest.mark.process("render-leaf-log.sh run through a symlink to the skills directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_renders_as_it_does_in_place(
        run_cli, render_leaf_log, tmp_path):
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    stdin = LEAF_OUT.read_text(encoding="utf-8")

    ran = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "render-leaf-log.sh")],
                         cwd=tmp_path / "elsewhere", input=stdin, capture_output=True, text=True)
    in_place = run_cli(render_leaf_log, [], stdin=stdin)

    assert (ran.returncode, ran.stdout, ran.stderr) == in_place == (0, RENDERED_LEAF_OUT, "")
