"""In-process cases for veri/build_adjudicate_prompt.py, the module build-adjudicate-prompt.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def build_adjudicate_prompt():
    return importlib.import_module("veri.build_adjudicate_prompt")


def test_main_with_no_argument_exits_2_printing_the_usage_line_on_stderr(run_cli, build_adjudicate_prompt):
    code, out, err = run_cli(build_adjudicate_prompt, [])
    assert (code, out, err) == (
        2,
        "",
        "usage: build-adjudicate-prompt.sh <n> <cause> <exit-code> <stderr-file> <command…>\n",
    )


def test_ci_timeout_prints_one_prompt_carrying_the_cause_command_exit_code_stderr_and_ledger_step(
    run_cli, build_adjudicate_prompt, tmp_path
):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text(
        "# Plan for #7\n\n- [x] first done step\n- [ ] the current step to judge\n- [ ] a later step\n"
    )
    stderr_file = tmp_path / "wait-ci.err"
    stderr_file.write_text("waiting on checks\nstill pending at the deadline\n")
    code, out, err = run_cli(
        build_adjudicate_prompt,
        ["7", "ci-timeout", "2", str(stderr_file), "wait-ci.sh", "abc1234"],
        cwd=tmp_path,
    )
    assert code == 0
    assert err == ""
    for expected in (
        "ci-timeout",
        "wait-ci.sh abc1234",
        "still pending at the deadline",
        "waiting on checks",
        "the current step to judge",
        "ADJUDICATION:",
    ):
        assert expected in out
    assert "a later step" not in out


def test_with_every_step_checked_the_prompt_carries_the_last_done_steps_ledger_line(
    run_cli, build_adjudicate_prompt, tmp_path
):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text(
        "# Plan for #7\n\n- [x] first done step\n- [x] second done step\n- [x] the last done step\n"
    )
    stderr_file = tmp_path / "wait-ci.err"
    stderr_file.write_text("still pending\n")
    code, out, err = run_cli(
        build_adjudicate_prompt,
        ["7", "ci-timeout", "2", str(stderr_file), "wait-ci.sh", "abc1234"],
        cwd=tmp_path,
    )
    assert code == 0
    assert "the last done step" in out
    assert "first done step" not in out
    assert "second done step" not in out


def test_the_prompt_carries_the_exit_code_argument(run_cli, build_adjudicate_prompt, tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [ ] the current step\n")
    stderr_file = tmp_path / "wait-ci.err"
    stderr_file.write_text("still pending\n")
    code, out, err = run_cli(
        build_adjudicate_prompt,
        ["7", "ci-timeout", "124", str(stderr_file), "wait-ci.sh", "abc1234"],
        cwd=tmp_path,
    )
    assert code == 0
    assert "124" in out


def test_a_stderr_file_of_more_than_50_lines_carries_exactly_its_last_50(
    run_cli, build_adjudicate_prompt, tmp_path
):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [ ] the current step\n")
    stderr_file = tmp_path / "wait-ci.err"
    stderr_file.write_text("".join(f"errline-{i:02d}\n" for i in range(1, 61)))
    code, out, err = run_cli(
        build_adjudicate_prompt,
        ["7", "ci-timeout", "2", str(stderr_file), "wait-ci.sh", "abc1234"],
        cwd=tmp_path,
    )
    assert code == 0
    carried = [f"errline-{i:02d}" for i in range(1, 61) if f"errline-{i:02d}" in out]
    assert carried == [f"errline-{i:02d}" for i in range(11, 61)]


def test_a_cause_adjudicate_md_does_not_list_exits_2_with_nothing_on_stdout_and_stderr_naming_it(
    run_cli, build_adjudicate_prompt, tmp_path
):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [ ] the current step\n")
    stderr_file = tmp_path / "wait-ci.err"
    stderr_file.write_text("killed\n")
    code, out, err = run_cli(
        build_adjudicate_prompt,
        ["7", "killed-stuck", "2", str(stderr_file), "wait-ci.sh", "abc1234"],
        cwd=tmp_path,
    )
    assert code == 2
    assert out == ""
    assert "killed-stuck" in err


def test_ci_timeout_prompt_carries_the_word_none_as_its_route_tokens(run_cli, build_adjudicate_prompt, tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [ ] the current step\n")
    stderr_file = tmp_path / "wait-ci.err"
    stderr_file.write_text("still pending\n")
    code, out, err = run_cli(
        build_adjudicate_prompt,
        ["7", "ci-timeout", "2", str(stderr_file), "wait-ci.sh", "abc1234"],
        cwd=tmp_path,
    )
    assert code == 0
    assert "Routes: none\n" in out


def test_a_cause_whose_bullet_lists_route_tokens_prints_them_unquoted_and_comma_separated(
    run_cli, build_adjudicate_prompt, tmp_path, monkeypatch
):
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "ADJUDICATE.md").write_text(
        "### Eligible causes\n\n- `some-cause`: `route-a`, `route-b`\n- `ci-timeout`: none\n"
    )
    monkeypatch.setattr(build_adjudicate_prompt, "__file__", str(skill / "scripts" / "veri" / "build_adjudicate_prompt.py"))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [ ] the current step\n")
    stderr_file = tmp_path / "wait-ci.err"
    stderr_file.write_text("still pending\n")
    code, out, err = run_cli(
        build_adjudicate_prompt,
        ["7", "some-cause", "2", str(stderr_file), "wait-ci.sh", "abc1234"],
        cwd=tmp_path,
    )
    assert code == 0
    assert "Routes: route-a, route-b\n" in out
    assert "`" not in out.split("Stderr:")[0]
