"""In-process cases for veri/verify.py, the module verify.sh is a shim over."""
import importlib
import io
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys

import pytest


from conftest import SCRIPTS
from test_supervise import checked_head, checked_step, committed_head

@pytest.fixture(autouse=True)
def no_ambient_leaf_args(monkeypatch):
    monkeypatch.delenv("VERIFY_LEAF_ARGS", raising=False)


USAGE = (b"usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file>"
         b" <test-path> [<target-test-id>]")


def write_inputs(directory):
    directory = pathlib.Path(directory)
    (directory / "tests").mkdir(exist_ok=True)
    (directory / "spec.md").write_text("the behavior spec\n")
    (directory / "tests" / "x.test.sh").write_text("test\n")


def assert_prompt_rendered(directory="."):
    prompts = sorted((pathlib.Path(directory) / ".tdd").glob("verify-*.prompt"))
    assert [b"the behavior spec" in prompt.read_bytes() for prompt in prompts] == [True]


def record(event, *pairs, issue="", step="", phase="green"):
    return {"issue": issue, "actor": "verifier", "phase": phase, "step": step, "event": event, "attempt": "1",
            "skill_commit": "", **dict(pair.split("=", 1) for pair in pairs)}


@pytest.mark.parametrize("argv", [[], ["green", "spec"], ["--step", "x", "green"]])
def test_main_with_fewer_than_three_positionals_returns_2_with_the_usage_line_alone_and_starts_no_process(
        argv, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes()
    verify = importlib.import_module("veri.verify")

    code = verify.main(list(argv))

    captured = capfdbinary.readouterr()
    assert len(USAGE) == 112
    assert (code, captured.out, captured.err, calls) == (2, b"", USAGE + b"\n", [])


@pytest.mark.parametrize("argv, flag", [(["--step"], b"--step"), (["--step", ""], b"--step"),
                                        (["--fast-cmd", "", "green", "s", "t"], b"--fast-cmd")])
def test_main_with_a_flag_missing_its_value_returns_2_naming_the_flag_then_the_usage_line_and_starts_no_process(
        argv, flag, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes()
    verify = importlib.import_module("veri.verify")

    code = verify.main(list(argv))

    captured = capfdbinary.readouterr()
    assert (code, captured.out, captured.err, calls) == (
        2, b"", b"verify: " + flag + b" needs a value\n" + USAGE + b"\n", [])


@pytest.mark.parametrize("argv, stderr", [
    (["green", "missing-spec.md", "tests/x.test.sh"], b"build-verify-prompt: cannot read 'missing-spec.md'\n"),
    (["bogus", "spec.md", "tests/x.test.sh"], b"build-verify-prompt: unknown phase 'bogus'"),
])
def test_main_returns_the_builders_refusal_mapped_into_the_contract_with_its_stderr_and_launches_no_leaf(
        argv, stderr, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    launched = []

    def fake(args, *_, **__):
        launched.append(os.path.basename(str(args[0])))
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", *argv])

    captured = capfdbinary.readouterr()
    assert (code, captured.out, stderr in captured.err, launched,
            (tmp_path / ".tdd" / "verify-green.prompt").exists()) == (2, b"", True, [], False)


def test_main_calls_the_builder_beside_the_shim_as_called_with_the_consumed_pairs_and_every_positional_and_writes_its_stdout_as_the_prompt_file(
        tmp_path, monkeypatch):
    link = tmp_path / "skill-link"
    link.symlink_to(SCRIPTS, target_is_directory=True)
    for name, module in list(sys.modules.items()):
        where = getattr(module, "__file__", None) or ""
        if name == "veri" or (where and pathlib.Path(where).resolve().is_relative_to(SCRIPTS)):
            monkeypatch.delitem(sys.modules, name)
    monkeypatch.syspath_prepend(str(link / "veri"))
    monkeypatch.syspath_prepend(str(link))
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    monkeypatch.setenv("VERI_STEP", "AMBIENT-STEP-SENTINEL")
    answering_leaf(monkeypatch, b"VERDICT: PASS\nfine")
    before = set(sys.modules)
    try:
        verify = importlib.import_module("veri.verify")
        argv = ["--step", "--fast-cmd", "--fast-cmd", "make unit",
                "green", "spec.md", "tests/x.test.sh", "--step"]
        (work / "spec.md").write_text("an earlier, longer spec that must not survive in the prompt\n")
        verify.main(list(argv))
        prompt_file = work / ".tdd" / "verify-green.prompt"
        first = prompt_file.read_bytes() if prompt_file.exists() else None
        (work / "spec.md").write_text("blind spec\n")
        verify.main(list(argv))
    finally:
        for name in set(sys.modules) - before:
            del sys.modules[name]

    prompt = prompt_file.read_bytes() if prompt_file.exists() else None
    assert first is not None and b"an earlier, longer spec" in first
    assert prompt is not None and b"blind spec" in prompt and b"an earlier, longer spec" not in prompt
    assert not prompt.endswith(b"\n")
    assert b"### The step under judgement\n\n--fast-cmd\n" in prompt
    assert b"make unit" in prompt and b"tests/x.test.sh" in prompt
    assert str(link / "timed-test-run.sh").encode() in prompt
    assert b"AMBIENT-STEP-SENTINEL" not in prompt


@pytest.mark.parametrize("leaf_args", [None, ""])
def test_main_launches_the_verifier_leaf_through_supervise_with_the_default_flags_stdin_inherited_stderr_captured_and_starts_no_ported_helper_process(
        leaf_args, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    if leaf_args is not None:
        monkeypatch.setenv("VERIFY_LEAF_ARGS", leaf_args)
    started = []

    def fake(args, *_, **kwargs):
        words = [str(a) for a in (args if isinstance(args, (list, tuple)) else [args])]
        started.append((words, kwargs.get("stdin"), kwargs.get("stderr")))
        name = os.path.basename(words[0])
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, fake)
    verify = importlib.import_module("veri.verify")
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(verify.__file__)))

    verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    supervised = [call for call in started if os.path.basename(call[0][0]) == "supervise.sh"]
    assert supervised == [([os.path.join(scripts, "supervise.sh"), "verify-green",
                            os.path.join(scripts, "run-leaf.sh"), ".tdd/verify-green.prompt",
                            "--permission-mode", "bypassPermissions",
                            "--disallowedTools", "Write", "Edit", "MultiEdit", "NotebookEdit"],
                           None, subprocess.PIPE)]
    forbidden = {"parse-verdict.sh", "leaf-role.sh", "leaf-model.sh"}
    assert [words for words, _, _ in started
            if os.path.basename(words[0]) in forbidden
            or os.path.basename(words[0]).startswith("python")] == []


@pytest.mark.parametrize("phase", ["green", "pin"])
@pytest.mark.parametrize("leaf_out, expected", [
    (b"VERDICT: PASS\nthe whole\nreason\n\n", (0, b"the whole\nreason\n")),
    (b"VERDICT: REJECT\nthe whole\nreason", (1, b"the whole\nreason\n")),
    (b"VERDICT: PASS\n", (0, b"\n")),
    (b"VERDICT: REJECT\nnot \xff utf-8\n", (1, b"not \xff utf-8\n")),
    (b"no verdict here\nat all\n", (2, b"\n")),
])
def test_main_reads_the_verdict_from_supervises_stdout_and_prints_the_whole_reason_with_one_newline(
        phase, leaf_out, expected, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    answering_leaf(monkeypatch, leaf_out)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", phase, "spec.md", "tests/x.test.sh",
                           *(["0123abc"] if phase == "refactor" else [])])

    assert (code, capfdbinary.readouterr().out) == expected


def test_main_drops_nul_bytes_from_the_leafs_output_so_a_verdict_carrying_them_is_read_as_the_same_verdict_without_them(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    answering_leaf(monkeypatch, "VER\x00DICT: REJ\x00ECT\nthe \x00whole\nreason\x00")
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, capfdbinary.readouterr().out) == (1, b"the whole\nreason\n")


@pytest.mark.parametrize("phase", ["green", "refactor"])
@pytest.mark.parametrize("leaf_out, word, reason_line", [
    (b"VERDICT: PASS\nfirst line\nsecond line\n", "PASS", "first line"),
    (b"VERDICT: REJECT\nwhy it fails\nmore\n", "REJECT", "why it fails"),
    (b"VERDICT: MAYBE\nundecided\n", "malformed", ""),
])
def test_main_appends_one_verdict_record_with_the_verdict_word_and_the_reasons_first_line_under_the_verifier_role(
        phase, leaf_out, word, reason_line, tmp_path, monkeypatch, events):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_ISSUE", "931")
    monkeypatch.setenv("VERI_STEP", "5")
    answering_leaf(monkeypatch, leaf_out)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    verify.main(["--fast-cmd", "make unit", phase, "spec.md", "tests/x.test.sh",
                           *(["0123abc"] if phase == "refactor" else [])])

    assert events.records() == [
        record("verdict", "verdict=" + word, "reason=" + reason_line, issue="931", step="5", phase=phase)]


def test_main_launches_the_leaf_with_verify_leaf_args_words_split_on_whitespace_and_glob_expanded_in_the_working_directory(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("b.flag", "a.flag", "c.other"):
        (tmp_path / name).write_text("")
    monkeypatch.setenv("VERIFY_LEAF_ARGS", "--one two\t*.flag\n nomatch-*.zz  --three")
    supervised = []
    answering_leaf(monkeypatch, b"VERDICT: PASS\nfine", supervised=supervised)
    verify = importlib.import_module("veri.verify")
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(verify.__file__)))

    verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert supervised == [[os.path.join(scripts, "supervise.sh"), "verify-green",
                           os.path.join(scripts, "run-leaf.sh"), ".tdd/verify-green.prompt",
                           "--one", "two", "a.flag", "b.flag", "nomatch-*.zz", "--three"]]


CLASH = ("verify: VERIFY_LEAF_ARGS carries its own --model and a role model variable resolved"
         " '%s' — which one the leaf would run on is flag order; unset one of them\n")


WITH_MODEL = "--permission-mode bypassPermissions --model sonnet"


@pytest.mark.parametrize("leaf_args, models, expected_code, expected_err, launches", [
    (WITH_MODEL, {"VERI_MODEL_VERIFIER": "opus", "VERI_MODEL": "haiku"}, 2, CLASH % "opus", False),
    (WITH_MODEL, {"VERI_MODEL": "haiku"}, 2, CLASH % "haiku", False),
    (WITH_MODEL, {"VERI_MODEL_VERIFIER": "two words"}, 0,
     "leaf-model: model 'two words' contains whitespace (a model id or alias is one word)\n", True),
    (WITH_MODEL, {"VERI_MODEL_VERIFIER": "-n"}, 0, "", True),
    ("--permission-mode bypassPermissions", {"VERI_MODEL_VERIFIER": "opus"}, 0, "", True),
    (None, {"VERI_MODEL": "two words"}, 0, "", True),
])
def test_main_refuses_a_literal_model_word_in_verify_leaf_args_beside_a_resolved_role_model_before_the_builder_runs(
        leaf_args, models, expected_code, expected_err, launches, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    for name, value in models.items():
        monkeypatch.setenv(name, value)
    if leaf_args is not None:
        monkeypatch.setenv("VERIFY_LEAF_ARGS", leaf_args)
    started = []

    def fake(args, *_, **__):
        name = os.path.basename(str(args[0]))
        started.append(name)
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    if launches:
        assert_prompt_rendered()
    else:
        assert list((tmp_path / ".tdd").glob("verify-*.prompt")) == []

    captured = capfdbinary.readouterr()
    assert (code, captured.err.decode("utf-8"), "supervise.sh" in started) == (
        expected_code, expected_err, launches)
    if not launches:
        assert (captured.out, started) == (b"", [])


def test_main_lets_a_literal_model_word_in_verify_leaf_args_stand_when_no_model_variable_is_set(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERIFY_LEAF_ARGS", "--model x")
    supervised = []
    answering_leaf(monkeypatch, b"VERDICT: PASS\nfine", supervised=supervised)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.err, [words[-2:] for words in supervised]) == (0, b"", [["--model", "x"]])


def test_main_still_refuses_a_literal_model_word_in_verify_leaf_args_when_veri_model_verifier_is_also_set(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_MODEL_VERIFIER", "opus")
    monkeypatch.setenv("VERIFY_LEAF_ARGS", "--model x")
    started = []

    def fake(args, *_, **__):
        started.append(os.path.basename(str(args[0])))
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["green", "spec.md", "tests/x.test.sh"])

    captured = capfdbinary.readouterr()
    assert (code, captured.err.decode("utf-8"), captured.out, started) == (2, CLASH % "opus", b"", [])


@pytest.mark.parametrize("supervise, expected", [
    (2, (2, "verifier leaf killed-stuck — no verdict rendered (see .tdd/verify-green.log)\n")),
    (FileNotFoundError, (2, "\n")),
])
def test_main_returns_2_on_a_killed_stuck_leaf_with_no_tamper_check_event_or_preservation_and_reads_an_unstartable_supervise_as_no_answer(
        supervise, expected, tmp_path, monkeypatch, capfdbinary, events):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_ISSUE", "931")
    monkeypatch.setenv("VERI_STEP", "7")
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    started = []

    def fake(args, *_, **__):
        words = [str(a) for a in (args if isinstance(args, (list, tuple)) else [args])]
        started.append(words)
        name = os.path.basename(words[0])
        if name == "supervise.sh":
            if supervise is FileNotFoundError:
                raise FileNotFoundError(2, "No such file or directory", words[0])
            return subprocess.CompletedProcess(args, supervise, b"VERDICT: PASS\nfine\n", None)
        if name == "git" and "write-tree" in words:
            return subprocess.CompletedProcess(args, 0, b"0123456789abcdef0123456789abcdef01234567\n", b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.out.decode("utf-8")) == expected
    if supervise == 2:
        launch = [os.path.basename(words[0]) for words in started].index("supervise.sh")
        assert [words for words in started[launch + 1:] if os.path.basename(words[0]) == "git"] == []
        assert events.records() == []


REFUSAL = ("supervise: refusing to launch verify-green: step 7 has no current check-earlier pass marker"
           " (run tests-frozen.sh check-earlier first)")


def test_2206_a_verify_green_supervise_refuses_to_launch_exits_2_naming_the_refusal_not_killed_stuck(
        tmp_path, monkeypatch, capfdbinary, events):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_ISSUE", "931")
    monkeypatch.setenv("VERI_STEP", "7")
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")

    def fake(args, *_, **kwargs):
        words = [str(a) for a in (args if isinstance(args, (list, tuple)) else [args])]
        if os.path.basename(words[0]) == "supervise.sh":
            if kwargs.get("stderr") == subprocess.PIPE:
                return subprocess.CompletedProcess(args, 2, b"", (REFUSAL + "\n").encode())
            os.write(2, (REFUSAL + "\n").encode())
            return subprocess.CompletedProcess(args, 2, b"", None)
        if words[0] == "git" and "write-tree" in words:
            return subprocess.CompletedProcess(args, 0, b"0123456789abcdef0123456789abcdef01234567\n", b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    captured = capfdbinary.readouterr()
    out, err = captured.out.decode("utf-8"), captured.err.decode("utf-8")
    assert (code, "killed-stuck" in out, REFUSAL in out, err.count(REFUSAL)) == (2, False, True, 1), (out, err)


NO_VERDICT = b"I looked around and have no opinion\n"
NO_LINE = b"parse-verdict: no VERDICT: line found\n"


@pytest.mark.parametrize("retries, leaf_outs, launches, marks, expected_code, expected_err", [
    (None, [NO_VERDICT, b"VERDICT: PASS\nfine\n"], 2,
     [["relaunch", "cause=no-verdict"], ["verdict", "verdict=PASS", "reason=fine"]], 0, NO_LINE),
    ("", [NO_VERDICT, NO_VERDICT], 2,
     [["relaunch", "cause=no-verdict"],
      ["verdict", "verdict=malformed", "reason=", "cause=no-verdict"]], 2, NO_LINE * 2),
    ("2", [NO_VERDICT, NO_VERDICT, NO_VERDICT], 3,
     [["relaunch", "cause=no-verdict"], ["relaunch", "cause=no-verdict"],
      ["verdict", "verdict=malformed", "reason=", "cause=no-verdict"]], 2, NO_LINE * 3),
    ("0", [NO_VERDICT], 1,
     [["verdict", "verdict=malformed", "reason=", "cause=no-verdict"]], 2, NO_LINE),
    (None, [b"VERDICT: MAYBE\nundecided\n", b"VERDICT: PASS\nfine\n"], 1,
     [["verdict", "verdict=malformed", "reason="]], 2,
     b"parse-verdict: unrecognised verdict word 'MAYBE'\n"),
])
def test_main_relaunches_a_leaf_with_no_verdict_line_up_to_the_no_verdict_budget_marking_each_relaunch_and_the_last_verdict_while_an_unrecognised_word_is_malformed_and_not_relaunched(
        retries, leaf_outs, launches, marks, expected_code, expected_err, tmp_path, monkeypatch,
        capfdbinary, events):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    if retries is not None:
        monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", retries)
    supervised = answering_leaf(monkeypatch, *leaf_outs)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, len(supervised), events.records(), capfdbinary.readouterr().err) == (
        expected_code, launches, [record(*mark) for mark in marks], expected_err)


def test_main_returns_2_when_the_relaunch_record_cannot_be_appended_and_makes_no_relaunch(
        tmp_path, monkeypatch, capfdbinary, events):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    events.unappendable()
    supervised = answering_leaf(monkeypatch, NO_VERDICT, b"VERDICT: PASS\nfine\n")
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, len(supervised), capfdbinary.readouterr().out) == (2, 1, b"")


def test_main_returns_2_when_the_verdict_record_cannot_be_appended_with_no_preservation_and_nothing_on_stdout(
        tmp_path, monkeypatch, capfdbinary, events):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_ISSUE", "931")
    monkeypatch.setenv("VERI_STEP", "7")
    events.unappendable()
    preserved = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        name = os.path.basename(words[0])
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: REJECT\nnot pinned\n", None)
        if name == "git" and "write-tree" in words:
            return subprocess.CompletedProcess(args, 0, b"a" * 40 + b"\n", b"")
        if name == "git" and "rev-parse" in words:
            return subprocess.CompletedProcess(args, 0, b"1" * 40 + b"\n", b"")
        if name == "git" and "update-ref" in words and words[2].startswith("refs/veri/attempts/"):
            preserved.append(words)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, preserved, capfdbinary.readouterr().out) == (2, [], b"")


@pytest.mark.parametrize("retries, launches", [("", 2), ("010", 9), ("08", 1)])
def test_main_reads_an_empty_no_verdict_budget_as_1_and_a_leading_zero_as_octal_so_010_allows_8_relaunches_and_08_none(
        retries, launches, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", retries)
    supervised = answering_leaf(monkeypatch, NO_VERDICT)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, len(supervised)) == (2, launches)


def test_main_copies_parse_verdicts_stderr_to_its_own_stderr_after_every_launch_relaunched_ones_included(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "2")
    leaf_outs = [NO_VERDICT, NO_VERDICT, b"VERDICT: MAYBE\nundecided\n"]
    supervised = []

    def fake(args, *_, **__):
        name = os.path.basename(str(args[0]))
        if name == "supervise.sh":
            supervised.append(args)
            os.write(2, b"launch %d\n" % len(supervised))
            return subprocess.CompletedProcess(args, 0, leaf_outs[len(supervised) - 1], None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, capfdbinary.readouterr().err) == (
        2, b"launch 1\n" + NO_LINE + b"launch 2\n" + NO_LINE
        + b"launch 3\nparse-verdict: unrecognised verdict word 'MAYBE'\n")


@pytest.mark.parametrize("retries", ["x", "-1", " 1"])
def test_main_refuses_a_no_verdict_budget_that_is_not_a_non_negative_integer_after_the_prompt_file_is_written_and_launches_no_leaf(
        retries, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", retries)
    launched = answering_leaf(monkeypatch, b"VERDICT: PASS\nfine\n")
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    prompt = tmp_path / ".tdd" / "verify-green.prompt"
    assert (code, captured.out, captured.err, b"the behavior spec" in prompt.read_bytes(),
            launched) == (
        2, b"",
        b"verify: VERI_NO_VERDICT_RETRIES must be a non-negative integer, got '"
        + retries.encode() + b"'\n",
        True, [])


def test_main_snapshots_the_tree_through_a_temporary_index_and_head_around_the_launch_and_returns_2_naming_the_changed_paths_then_head_with_no_verdict_event_or_preservation(
        tmp_path, monkeypatch, capfdbinary, events):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("VERI_ISSUE", "7")
    monkeypatch.setenv("VERI_STEP", "2")
    trees = [b"a" * 40 + b"\n", b"b" * 40 + b"\n"]
    heads = [b"1" * 40 + b"\n", b"2" * 40 + b"\n"]
    order = []
    updated = []
    indexes = []
    diffed = []

    def fake(args, *_, **kwargs):
        words = [str(a) for a in args]
        env = dict(kwargs.get("env") or os.environ)
        if os.path.basename(words[0]) == "env":
            words = words[1:]
            while words and "=" in words[0]:
                key, _, value = words.pop(0).partition("=")
                env[key] = value
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            order.append(verb)
            if verb == "update-ref":
                updated.append(words[2])
            if verb in ("add", "write-tree"):
                indexes.append((verb, env.get("GIT_INDEX_FILE")))
            if verb == "write-tree":
                return subprocess.CompletedProcess(args, 0, trees[order.count("write-tree") - 1], b"")
            if verb == "rev-parse":
                return subprocess.CompletedProcess(args, 0, heads[order.count("rev-parse") - 1], b"")
            if verb == "diff-tree":
                diffed.append(words[2:])
                return subprocess.CompletedProcess(args, 0, b"src.txt\nnew.txt\n", b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        order.append(name)
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: REJECT\nbad\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.out) == (
        2, "verifier leaf modified the repository — verdict not accepted"
           " (see .tdd/verify-green.log); changed:\nsrc.txt\nnew.txt\nHEAD\n".encode())
    launch = order.index("supervise.sh")
    assert [v for v in order[:launch] if v in ("add", "write-tree", "rev-parse")] == [
        "add", "write-tree", "rev-parse"]
    assert [v for v in order[launch:] if v in ("add", "write-tree", "rev-parse")][:3] == [
        "add", "write-tree", "rev-parse"]
    assert diffed == [["-r", "--name-only", "--no-commit-id", "a" * 40, "b" * 40]]
    snapshots = indexes[:4]
    assert all(index and not pathlib.Path(index).is_relative_to(tmp_path) for _, index in snapshots)
    assert (snapshots[0][1] == snapshots[1][1], snapshots[2][1] == snapshots[3][1]) == (True, True)
    assert ([r for r in updated if r.startswith("refs/veri/attempts/")], events.records()) == ([], [])


@pytest.mark.parametrize("failing", ["add", "git-missing", "write-tree", "diff-tree"])
def test_main_takes_a_git_call_that_fails_as_no_snapshot_or_no_change_whatever_it_printed_and_returns_the_verdict(
        failing, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    trees = [b"a" * 40 + b"\n", b"b" * 40 + b"\n"]
    verbs = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            verbs.append(verb)
            if failing == "git-missing":
                raise FileNotFoundError(2, "No such file or directory", "git")
            code = 128 if verb == failing else 0
            if verb == "write-tree":
                return subprocess.CompletedProcess(args, code, trees[verbs.count("write-tree") - 1], b"")
            if verb == "rev-parse":
                return subprocess.CompletedProcess(args, 0, b"1" * 40 + b"\n", b"")
            if verb == "diff-tree":
                return subprocess.CompletedProcess(args, code, b"src.txt\n", b"")
            return subprocess.CompletedProcess(args, code, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    no_snapshot = failing in ("add", "git-missing", "write-tree")
    assert (code, captured.out, "diff-tree" in verbs, "write-tree" in verbs) == (
        0, b"fine\n", not no_snapshot, failing in ("write-tree", "diff-tree"))


@pytest.mark.parametrize("head_moved", [True, False])
def test_main_restores_a_modified_tree_through_a_fresh_temporary_index_and_a_moved_head_with_update_ref(
        head_moved, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    trees = [b"a" * 40 + b"\n", b"b" * 40 + b"\n"]
    heads = [b"1" * 40 + b"\n", (b"2" if head_moved else b"1") * 40 + b"\n"]
    verbs = []
    indexes = []
    restored = []

    def fake(args, *_, **kwargs):
        words = [str(a) for a in args]
        env = dict(kwargs.get("env") or os.environ)
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            verbs.append(verb)
            if verb in ("add", "write-tree", "read-tree"):
                indexes.append((verb, env.get("GIT_INDEX_FILE")))
            if verb in ("read-tree", "update-ref"):
                restored.append(words[1:])
            if verb == "write-tree":
                return subprocess.CompletedProcess(args, 0, trees[verbs.count("write-tree") - 1], b"")
            if verb == "rev-parse":
                return subprocess.CompletedProcess(args, 0, heads[verbs.count("rev-parse") - 1], b"")
            if verb == "diff-tree":
                return subprocess.CompletedProcess(args, 0, b"src.txt\n", b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    capfdbinary.readouterr()
    expected = [["read-tree", "-u", "--reset", "a" * 40]]
    if head_moved:
        expected.append(["update-ref", "HEAD", "1" * 40])
    assert (code, restored) == (2, expected)
    snapshot_indexes = {index for verb, index in indexes if verb == "write-tree"}
    read_tree_index = [index for verb, index in indexes if verb == "read-tree"][0]
    assert read_tree_index and read_tree_index not in snapshot_indexes
    assert not pathlib.Path(read_tree_index).is_relative_to(tmp_path)


def test_main_runs_the_tamper_check_after_a_relaunchs_launch_and_refuses_a_relaunched_leaf_that_modified_the_repository(
        tmp_path, monkeypatch, capfdbinary, events):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    trees = [b"a" * 40 + b"\n", b"a" * 40 + b"\n", b"b" * 40 + b"\n"]
    leaf_outs = [b"no verdict here\n", b"VERDICT: PASS\nfine\n"]
    supervised = []
    writes = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            if verb == "write-tree":
                writes.append(verb)
                return subprocess.CompletedProcess(args, 0, trees[min(len(writes), 3) - 1], b"")
            if verb == "rev-parse":
                return subprocess.CompletedProcess(args, 0, b"1" * 40 + b"\n", b"")
            if verb == "diff-tree":
                out = b"src.txt\n" if words[-2] != words[-1] else b""
                return subprocess.CompletedProcess(args, 0, out, b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            supervised.append(words)
            return subprocess.CompletedProcess(args, 0, leaf_outs[len(supervised) - 1], None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, len(supervised), captured.out, events.records()) == (
        2, 2, "verifier leaf modified the repository — verdict not accepted"
              " (see .tdd/verify-green.log); changed:\nsrc.txt\n".encode(),
        [record("relaunch", "cause=no-verdict")])


@pytest.mark.parametrize("where", ["not-a-repository", "git-missing", "add-fails"])
def test_main_outside_a_repository_without_git_or_with_a_failing_add_takes_no_snapshot_runs_no_tamper_check_or_preservation_and_returns_the_verdict(
        where, tmp_path, monkeypatch, capfdbinary, events):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("VERI_ISSUE", "7")
    monkeypatch.setenv("VERI_STEP", "2")
    verbs = []
    started = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            verbs.append(verb)
            if where == "git-missing":
                raise FileNotFoundError(2, "No such file or directory", "git")
            if where == "not-a-repository" or verb == "add":
                return subprocess.CompletedProcess(args, 128, b"", b"fatal: not a git repository\n")
            if verb == "write-tree":
                return subprocess.CompletedProcess(args, 0, b"a" * 40 + b"\n", b"")
            if verb == "rev-parse":
                return subprocess.CompletedProcess(args, 0, b"1" * 40 + b"\n", b"")
            if verb == "diff-tree":
                return subprocess.CompletedProcess(args, 0, b"src.txt\n", b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        started.append(words)
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: REJECT\nbad\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    names = [os.path.basename(words[0]) for words in started]
    assert (code, captured.out) == (1, b"bad\n")
    assert [v for v in verbs if v in ("write-tree", "diff-tree", "read-tree", "update-ref")] == []
    assert events.records() == [record("verdict", "verdict=REJECT", "reason=bad", issue="7", step="2")]


def test_main_in_a_repository_with_no_commit_reports_a_leaf_that_commits_as_head_and_makes_no_update_ref_call(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    heads = [subprocess.CompletedProcess([], 128, b"", b"fatal: Needed a single revision\n"),
             subprocess.CompletedProcess([], 0, b"2" * 40 + b"\n", b"")]
    reads = []
    updated = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            if verb == "update-ref":
                updated.append(words[1:])
            if verb == "write-tree":
                return subprocess.CompletedProcess(args, 0, b"a" * 40 + b"\n", b"")
            if verb == "rev-parse":
                reads.append(verb)
                return heads[min(len(reads), 2) - 1]
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.out, updated) == (
        2, "verifier leaf modified the repository — verdict not accepted"
           " (see .tdd/verify-green.log); changed:\nHEAD\n".encode(), [])


def test_main_returns_2_with_no_traceback_when_the_update_ref_restoring_head_fails_1183(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    trees = [b"a" * 40 + b"\n", b"b" * 40 + b"\n"]
    heads = [b"1" * 40 + b"\n", b"2" * 40 + b"\n"]
    verbs = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            verbs.append(verb)
            if verb == "write-tree":
                return subprocess.CompletedProcess(args, 0, trees[verbs.count("write-tree") - 1], b"")
            if verb == "rev-parse":
                return subprocess.CompletedProcess(args, 0, heads[verbs.count("rev-parse") - 1], b"")
            if verb == "diff-tree":
                return subprocess.CompletedProcess(args, 0, b"src.txt\n", b"")
            if verb == "update-ref":
                return subprocess.CompletedProcess(args, 128, None, None)
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert ("update-ref" in verbs, code, b"Traceback" in captured.err) == (True, 2, False)


def test_main_returns_2_not_1_when_the_update_ref_restoring_head_exits_1_1183(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    trees = [b"a" * 40 + b"\n", b"b" * 40 + b"\n"]
    heads = [b"1" * 40 + b"\n", b"2" * 40 + b"\n"]
    verbs = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            verbs.append(verb)
            if verb == "write-tree":
                return subprocess.CompletedProcess(args, 0, trees[verbs.count("write-tree") - 1], b"")
            if verb == "rev-parse":
                return subprocess.CompletedProcess(args, 0, heads[verbs.count("rev-parse") - 1], b"")
            if verb == "diff-tree":
                return subprocess.CompletedProcess(args, 0, b"src.txt\n", b"")
            if verb == "update-ref":
                return subprocess.CompletedProcess(args, 1, None, None)
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert ("update-ref" in verbs, code) == (True, 2)


def test_main_returns_2_with_no_traceback_when_git_cannot_be_started_to_restore_head_1183(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    trees = [b"a" * 40 + b"\n", b"b" * 40 + b"\n"]
    heads = [b"1" * 40 + b"\n", b"2" * 40 + b"\n"]
    verbs = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            verbs.append(verb)
            if verb == "write-tree":
                return subprocess.CompletedProcess(args, 0, trees[verbs.count("write-tree") - 1], b"")
            if verb == "rev-parse":
                return subprocess.CompletedProcess(args, 0, heads[verbs.count("rev-parse") - 1], b"")
            if verb == "diff-tree":
                return subprocess.CompletedProcess(args, 0, b"src.txt\n", b"")
            if verb == "update-ref":
                raise FileNotFoundError(2, "No such file or directory", "git")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    raised = None
    try:
        code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    except OSError as error:
        code, raised = None, type(error).__name__

    captured = capfdbinary.readouterr()
    assert ("update-ref" in verbs, code, raised, b"Traceback" in captured.err) == (True, 2, None, False)


@pytest.mark.parametrize("before, after", [(b"[user]\n\tname = op\n", b"[user]\n\tname = leaf\n"),
                                           (None, b"[user]\n\tname = leaf\n"),
                                           (b"[user]\n\tname = op\n", None)])
def test_main_returns_2_naming_home_gitconfig_when_the_leaf_changed_created_or_deleted_it_and_restores_nothing(
        before, after, tmp_path, monkeypatch, capfdbinary, events):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    gitconfig = home / ".gitconfig"
    if before is not None:
        gitconfig.write_bytes(before)
    monkeypatch.setenv("VERI_ISSUE", "931")
    monkeypatch.setenv("VERI_STEP", "7")
    started = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        started.append(" ".join(words) if name == "git" else name)
        if name == "git":
            return subprocess.CompletedProcess(args, 128, b"", b"fatal: not a git repository\n")
        if name == "supervise.sh":
            if after is None:
                gitconfig.unlink()
            else:
                gitconfig.write_bytes(after)
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    left = gitconfig.read_bytes() if gitconfig.exists() else None
    assert (code, captured.out) == (
        2, ("verifier leaf modified the operator's global git config — verdict not accepted"
            " (see .tdd/verify-green.log); changed:\n%s\n" % os.path.join(str(home), ".gitconfig")).encode())
    assert (left, events.records(), any(" update-ref refs/veri/attempts/" in w for w in started)) == (after, [], False)


def test_main_reports_a_leaf_that_changed_both_the_repository_and_home_gitconfig_for_the_repository_only(
        tmp_path, monkeypatch, capfdbinary):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    gitconfig = home / ".gitconfig"
    gitconfig.write_bytes(b"[user]\n\tname = op\n")
    trees = [b"a" * 40 + b"\n", b"b" * 40 + b"\n"]
    writes = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            verb = words[1]
            if verb == "write-tree":
                writes.append(verb)
                return subprocess.CompletedProcess(args, 0, trees[min(len(writes), 2) - 1], b"")
            if verb == "rev-parse":
                return subprocess.CompletedProcess(args, 0, b"1" * 40 + b"\n", b"")
            if verb == "diff-tree":
                return subprocess.CompletedProcess(args, 0, b"src.txt\n", b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            gitconfig.write_bytes(b"[user]\n\tname = leaf\n")
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.out) == (
        2, "verifier leaf modified the repository — verdict not accepted"
           " (see .tdd/verify-green.log); changed:\nsrc.txt\n".encode())


def test_main_returns_2_before_any_leaf_launches_when_reading_home_gitconfig_a_regular_file_raises_oserror_1183(
        tmp_path, monkeypatch, capfdbinary):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    gitconfig = home / ".gitconfig"
    gitconfig.write_bytes(b"[user]\n\tname = op\n")
    launched = answering_leaf(monkeypatch, b"VERDICT: PASS\nfine\n")
    real_open = open

    def unreadable(path, *args, **kwargs):
        if os.fspath(path) == str(gitconfig):
            raise PermissionError(13, "Permission denied", os.fspath(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", unreadable)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.out, launched) == (2, b"", [])


def test_main_returning_2_because_reading_home_gitconfig_raised_oserror_names_that_path_on_stderr_1183(
        tmp_path, monkeypatch, capfdbinary):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    gitconfig = home / ".gitconfig"
    gitconfig.write_bytes(b"[user]\n\tname = op\n")
    answering_leaf(monkeypatch, b"")
    real_open = open

    def unreadable(path, *args, **kwargs):
        if os.fspath(path) == str(gitconfig):
            raise PermissionError(13, "Permission denied", os.fspath(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", unreadable)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, str(gitconfig).encode() in captured.err) == (2, True)


def test_main_returns_2_naming_home_gitconfig_on_stderr_without_launching_a_leaf_when_it_is_a_directory_1183(
        tmp_path, monkeypatch, capfdbinary):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    gitconfig = home / ".gitconfig"
    gitconfig.mkdir()
    launched = answering_leaf(monkeypatch, b"VERDICT: PASS\nfine\n")
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, str(gitconfig).encode() in captured.err, b"Traceback" in captured.err,
            launched) == (2, True, False, [])


def test_main_returns_2_naming_home_gitconfig_on_stderr_when_the_leaf_left_it_a_directory_1183(
        tmp_path, monkeypatch, capfdbinary):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    gitconfig = home / ".gitconfig"
    gitconfig.write_bytes(b"[user]\n\tname = op\n")

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            return subprocess.CompletedProcess(args, 128, b"", b"fatal: not a git repository\n")
        if name == "supervise.sh":
            gitconfig.unlink()
            gitconfig.mkdir()
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, str(gitconfig).encode() in captured.err, b"Traceback" in captured.err) == (2, True, False)


def test_main_returns_2_naming_home_gitconfig_on_stderr_when_the_leaf_left_it_unreadable_1183(
        tmp_path, monkeypatch, capfdbinary):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    gitconfig = home / ".gitconfig"
    gitconfig.write_bytes(b"[user]\n\tname = op\n")
    leaf_ran = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if "=" not in w]
        name = os.path.basename(words[0])
        if name == "git":
            return subprocess.CompletedProcess(args, 128, b"", b"fatal: not a git repository\n")
        if name == "supervise.sh":
            leaf_ran.append(name)
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    real_open = open

    def unreadable_after_the_leaf(path, *args, **kwargs):
        if leaf_ran and os.fspath(path) == str(gitconfig):
            raise PermissionError(13, "Permission denied", os.fspath(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", unreadable_after_the_leaf)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, str(gitconfig).encode() in captured.err, b"Traceback" in captured.err,
            leaf_ran) == (2, True, False, ["supervise.sh"])


@pytest.mark.parametrize("leaf_out, issue, step, preserver, expected_code, expected_mark", [
    (b"VERDICT: REJECT\nbad\n", "931", "7", 0, 1, "reject"),
    (b"VERDICT: MAYBE\nundecided\n", "931", "7", 0, 2, "malformed"),
    (NO_VERDICT, "931", "7", 0, 2, "no-verdict"),
    (b"VERDICT: REJECT\nbad\n", "931", "7", 1, 1, "reject"),
    (NO_VERDICT, "931", "7", 1, 2, "no-verdict"),
    (b"VERDICT: PASS\nfine\n", "931", "7", 0, 0, None),
    (b"VERDICT: REJECT\nbad\n", "", "7", 0, 1, None),
    (b"VERDICT: REJECT\nbad\n", "931", "", 0, 1, None),
])
def test_main_preserves_a_reject_malformed_or_no_verdict_attempt_under_its_attempts_ref_naming_a_failed_update_ref_and_still_returning_the_verdicts_code(
        leaf_out, issue, step, preserver, expected_code, expected_mark, tmp_path, monkeypatch,
        capfdbinary):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_ISSUE", issue)
    monkeypatch.setenv("VERI_STEP", step)
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    preserved = []

    def fake(args, *_, **kwargs):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = words[1:]
            while words and "=" in words[0]:
                words.pop(0)
        name = os.path.basename(words[0])
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, leaf_out, None)
        if name == "preserve-attempt.sh":
            raise AssertionError(f"preserve-attempt.sh started as a process: {words}")
        if name == "git" and "--show-toplevel" in words:
            return subprocess.CompletedProcess(args, 0, os.getcwd() + "\n", "")
        if name == "git" and "commit-tree" in words:
            return subprocess.CompletedProcess(args, 0, "c" * 40 + "\n", "")
        if name == "git" and "update-ref" in words:
            preserved.append(words)
            return subprocess.CompletedProcess(args, preserver, b"", b"")
        if name == "git" and "write-tree" in words:
            return subprocess.CompletedProcess(args, 0, "a" * 40 + "\n" if kwargs.get("text") else b"a" * 40 + b"\n", b"")
        if name == "git" and "rev-parse" in words:
            return subprocess.CompletedProcess(args, 0, b"1" * 40 + b"\n", b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert code == expected_code
    if expected_mark is None:
        assert preserved == []
        return
    assert preserved == [["git", "update-ref", f"refs/veri/attempts/{issue}/{step}/verify-green-1", "c" * 40]]
    could_not = ("verify: could not preserve the %s attempt (issue %s step %s verify-green attempt 1)\n"
                 % (expected_mark, issue, step)).encode()
    assert (could_not in captured.err) == (preserver != 0)


def test_main_writes_every_line_it_prints_the_em_dash_in_its_refusals_included_as_utf8_bytes_under_lc_all_c(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("LC_ALL", "C")
    answer = {}

    def fake(args, *_, **__):
        name = os.path.basename(str(args[0]))
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, answer["code"], answer["out"], None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    def run(code, out, env):
        answer.update(code=code, out=out)
        stdout, stderr = io.BytesIO(), io.BytesIO()
        with monkeypatch.context() as scoped:
            for variable, value in env.items():
                scoped.setenv(variable, value)
            scoped.setattr(sys, "stdout", io.TextIOWrapper(stdout, encoding="ascii", write_through=True))
            scoped.setattr(sys, "stderr", io.TextIOWrapper(stderr, encoding="ascii", write_through=True))
            try:
                status = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
            except Exception as error:
                status = type(error).__name__
            return status, stdout.getvalue(), stderr.getvalue()

    seen = [run(2, b"", {}),
            run(0, b"", {"VERIFY_LEAF_ARGS": "--model x", "VERI_MODEL_VERIFIER": "sonnet"}),
            run(0, "VERDICT: PASS\nfine — ok\n".encode(), {})]

    assert seen == [
        (2, "verifier leaf killed-stuck — no verdict rendered (see .tdd/verify-green.log)\n".encode(), b""),
        (2, b"", ("verify: VERIFY_LEAF_ARGS carries its own --model and a role model variable resolved"
                  " 'sonnet' — which one the leaf would run on is flag order; unset one of them\n").encode()),
        (0, "fine — ok\n".encode(), b""),
    ]


HUNG_LEAF = "#!/bin/sh\necho thinking...\nexec sleep 60\n"


def build_prompt(words, monkeypatch):
    built, captured = io.BytesIO(), sys.stdout
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(built, write_through=True))
    code = importlib.import_module("veri.build_verify_prompt").main(words)
    monkeypatch.setattr(sys, "stdout", captured)
    return code, built.getvalue()


SPEC = "slugify must lowercase the title and join words with hyphens."


def answering_leaf(monkeypatch, *leaf_outs, supervised=None):
    launches = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        name = os.path.basename(words[0])
        if name == "supervise.sh":
            launches.append((words[1], pathlib.Path(words[3]).read_text()))
            if supervised is not None:
                supervised.append(words)
            out = leaf_outs[min(len(launches), len(leaf_outs)) - 1]
            return subprocess.CompletedProcess(args, 0, out if isinstance(out, bytes) else (out + "\n").encode(), None)
        return subprocess.CompletedProcess(args, 128 if name == "git" else 0, b"", None)

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    return launches



def test_verify_sh_red_with_a_suite_command_failing_only_on_the_target_test_still_launches_the_verifier_and_its_pass_stands(
        run_cli, tmp_path, monkeypatch):
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")
    launches = answering_leaf(monkeypatch, "VERDICT: PASS\nREASON: ok")
    env = {"HOME": str(tmp_path),
           "VERI_TEST_CMD": "echo 'FAILED tests/test_slugify.py::test_lowercases - assert 1 == 2'; exit 1"}

    code, out, _ = run_cli(verify, ["red", str(tmp_path / "spec.md"), "tests/test_slugify.py", "test_lowercases"],
                           env=env, cwd=tmp_path)

    assert (code, [phase for phase, _ in launches], out.startswith("ok")) == (0, ["verify-red"], True)

HUNG = pytest.mark.process("a hung verifier leaf killed by the real supervise.sh")


@pytest.mark.parametrize("leaf, ambient", [
    ("answers", None),
    pytest.param("hangs", None, marks=HUNG),
    pytest.param("hangs", "3", marks=HUNG),
])
def test_verify_sh_passes_the_blind_prompt_carrying_the_spec_to_the_leaf_and_a_hung_leaf_runs_once_killed_stuck_with_exit_2(
        leaf, ambient, run_cli, tmp_path, monkeypatch):
    if ambient is not None:
        monkeypatch.setenv("VERI_STUCK_RETRIES", ambient)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")
    argv = ["red", str(tmp_path / "spec.md"), "tests/test_slugify.py", "test_lowercases"]
    env = {"HOME": str(tmp_path)}
    if leaf == "answers":
        launches = answering_leaf(monkeypatch, "VERDICT: PASS\nREASON: ok")
    else:
        claude = tmp_path / "claude-hang"
        claude.write_text(HUNG_LEAF)
        claude.chmod(0o755)
        env.update(CLAUDE_BIN=str(claude), VERI_STUCK_RETRIES="0", VERI_TIMEOUT="0",
                   VERI_POLL="0.02", VERI_KILL_POLL="0.01")
        (tmp_path / ".gitignore").write_text(".tdd/\n")
        env.update(checked_step(tmp_path, committed_head(tmp_path)))

    code, out, err = run_cli(verify, argv, env=env, cwd=tmp_path)

    if leaf == "answers":
        assert (code, len(launches), SPEC in launches[0][1]) == (0, 1, True)
    else:
        assert (code, "killed-stuck" in out,
                err.count("supervise[verify-red]: killed-stuck"), "retry " in err) == (2, True, 1, False)


def stream(*results):
    records = ['{"type":"system","subtype":"init","session_id":"s"}']
    records += ['{"type":"result","subtype":"success","is_error":false,"result":%s}' % json.dumps(r)
                for r in results]
    return "\n".join(records)


FAST = ["--fast-cmd", "make unit"]
WAITING = "Waiting for the background `make test` run to complete before rendering a verdict."
GREEN_REASON = "Target test and full suite are green."
GREEN = "VERDICT: PASS\nREASON: " + GREEN_REASON
DELIVERED = "No action needed — verdict already delivered for this verification."
NO_LINE_TEXT = NO_LINE.decode()
RELAUNCH = ["relaunch", "cause=no-verdict"]
NO_VERDICT_MARK = ["verdict", "verdict=malformed", "reason=", "cause=no-verdict"]
GREEN_MARK = ["verdict", "verdict=PASS", "reason=" + GREEN_REASON]
KILLED_OUT = "verifier leaf killed-stuck — no verdict rendered (see .tdd/verify-green.log)\n"
EXHAUSTED = (2, "\n", NO_LINE_TEXT * 2, 2, [RELAUNCH, NO_VERDICT_MARK])
KILLED = (2, KILLED_OUT, "", 1, [])


@pytest.mark.parametrize("env, leaf_outs, supervise_code, expected", [
    pytest.param({}, [stream(WAITING, GREEN, DELIVERED)], 0,
                 (0, GREEN_REASON + "\n", "", 1, [GREEN_MARK]), id="earlier-record"),
    pytest.param({}, [stream(WAITING, DELIVERED)], 0,
                 EXHAUSTED, id="no-record-verdict"),
    pytest.param({}, [stream("VERDICT: REJECT\nREASON: Missing edge case.",
                             "VERDICT: PASS\nREASON: Revised: target and full suite green.", DELIVERED)], 0,
                 (0, "Revised: target and full suite green.\n", "", 1,
                  [["verdict", "verdict=PASS", "reason=Revised: target and full suite green."]]), id="newest-wins"),
    pytest.param({}, [WAITING, GREEN], 0,
                 (0, GREEN_REASON + "\n", NO_LINE_TEXT, 2, [RELAUNCH, GREEN_MARK]),
                 id="relaunched-second-verdict"),
    pytest.param({}, [WAITING], 0,
                 EXHAUSTED, id="budget-default"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "0"}, [WAITING], 0,
                 (2, "\n", NO_LINE_TEXT, 1, [NO_VERDICT_MARK]), id="budget-0"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "2"}, [WAITING], 0,
                 (2, "\n", NO_LINE_TEXT * 3, 3, [RELAUNCH, RELAUNCH, NO_VERDICT_MARK]), id="budget-2"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "many"}, [WAITING], 0,
                 (2, "", "verify: VERI_NO_VERDICT_RETRIES must be a non-negative integer, got 'many'\n", 0, []),
                 id="budget-not-an-integer"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "3", "VERI_STUCK_RETRIES": "1"}, [GREEN], 2,
                 KILLED, id="killed-not-relaunched"),
    pytest.param({"VERI_STUCK_RETRIES": "3"}, [WAITING], 0,
                 EXHAUSTED, id="stuck-retries-leave-no-verdict-count"),
    pytest.param({"VERI_NO_VERDICT_RETRIES": "3", "VERI_STUCK_RETRIES": "0"}, [GREEN], 2,
                 KILLED, id="no-verdict-retries-leave-stuck-count"),
])
def test_verify_sh_reads_the_newest_verdict_across_result_records_and_relaunches_only_a_clean_no_verdict_exit_within_its_own_budget_marking_it_no_verdict(
        env, leaf_outs, supervise_code, expected, run_cli, tmp_path, monkeypatch, events):
    write_inputs(tmp_path)
    extract = importlib.import_module("veri.extract_result").extract
    stuck_seen = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        name = os.path.basename(words[0])
        if name == "supervise.sh":
            stuck_seen.append(os.environ.get("VERI_STUCK_RETRIES"))
            leaf = leaf_outs[min(len(stuck_seen), len(leaf_outs)) - 1]
            return subprocess.CompletedProcess(args, supervise_code, (leaf + "\n" + extract(leaf)).encode(), None)
        return subprocess.CompletedProcess(args, 128 if name == "git" else 0, b"", None)

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code, out, err = run_cli(verify, [*FAST, "green", "spec.md", "tests/test_slugify.py", "test_lowercases"],
                             env={"HOME": str(tmp_path), **env}, cwd=tmp_path)

    assert (code, out, err, len(stuck_seen), events.records(tmp_path)) == (
        *expected[:4], [record(*mark) for mark in expected[4]])
    assert stuck_seen == [env.get("VERI_STUCK_RETRIES")] * len(stuck_seen)


FLAG_STEP = "FLAG-STEP slugify joins words with hyphens"
AMBIENT_STEP = "AMBIENT-STEP-must-not-appear"


@pytest.mark.parametrize("flags, phase, fourth, leaf_out, expected_code, launches, present, absent", [
    pytest.param(FAST, "green", "test_lowercases", WAITING, 2, 2, [SPEC], [], id="relaunch-byte-identical"),
    pytest.param(FAST, "refactor", "0123abc", GREEN, 0, 1, ["git diff 0123abc..HEAD"], [], id="refactor-base-sha"),
    pytest.param(["--step", FLAG_STEP, *FAST], "green", "test_lowercases", GREEN, 0, 1, [FLAG_STEP],
                 [AMBIENT_STEP], id="step-flag-not-ambient"),
    *[pytest.param(FAST if phase in ("green", "refactor") else [], phase,
                   "0123abc" if phase == "refactor" else "test_lowercases", GREEN, 0, 1, [SPEC, "VERDICT:"], [],
                   id="no-step-" + phase) for phase in ("red", "green", "refactor", "pin")],
])
def test_verify_sh_hands_every_launch_the_builders_own_prompt_for_its_arguments_carrying_base_sha_and_step_flag_not_ambient_veri_step_with_no_unfilled_placeholder(
        flags, phase, fourth, leaf_out, expected_code, launches, present, absent, run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_STEP", AMBIENT_STEP)
    (tmp_path / "spec.md").write_text(SPEC)
    argv = [*flags, phase, str(tmp_path / "spec.md"), "tests/test_slugify.py", fourth]
    launched = answering_leaf(monkeypatch, leaf_out)
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, argv, env={"HOME": str(tmp_path)}, cwd=tmp_path)

    expected = build_prompt(argv, monkeypatch)[1].decode().rstrip("\n")
    assert (code, [prompt for _, prompt in launched]) == (expected_code, [expected] * launches)
    assert [text for text in present if text not in expected] == []
    assert [text for text in absent if text in expected] == []
    assert re.findall(r"\{\{[A-Z_]*\}\}", expected) == []


def git_state(repo):
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout.decode()

    files = sorted(git("ls-files", "-co", "--exclude-standard").splitlines())
    return ["HEAD " + git("rev-parse", "HEAD").strip()] + [
        "%s %s" % (f, git("hash-object", "--", f).strip()) for f in files]


def tamper_scratch(tmp_path, monkeypatch, gitignore, tracked):
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    (repo / "src.txt").write_text("the developer committed this\n")
    (repo / ".gitignore").write_bytes(gitignore)
    for path, text in tracked.items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text(text)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "initial"], check=True)
    (tmp_path / "spec.md").write_text(SPEC)
    claude = tmp_path / "claude-mutate"
    claude.write_text('#!/bin/sh\neval "${FAKE_MUTATE:-}" >/dev/null 2>&1\nprintf \'%s\' "${FAKE_OUT_TEXT:-}"\nexit 0\n')
    claude.chmod(0o755)
    return repo, claude


@pytest.mark.process("a real git scratch repository whose state the verifier leaf changes")
@pytest.mark.parametrize("mutation, leaf_args, expected_code, named", [
    ('printf "the verifier rewrote this\\n" > src.txt', None, 2, "src.txt"),
    ('printf "the verifier left this behind\\n" > leftover.txt', None, 2, "leftover.txt"),
    ('git commit -q -a -m "the verifier committed the developer\'s work"', None, 2, "HEAD"),
    ('b="$(mktemp)"; cp src.txt "$b"; printf "the verifier broke this\\n" > src.txt; cp "$b" src.txt; rm -f "$b"',
     None, 0, "full suite are green"),
    ('printf "%s\\n" "$@" > "$LEAFARGS_OUT"; printf "the verifier rewrote this\\n" > src.txt',
     "--permission-mode bypassPermissions --disallowedTools Write", 2, "src.txt"),
])
def test_verify_sh_refuses_a_verifier_leaf_that_changed_the_tree_or_head_with_exit_2_naming_it_and_restores_what_it_was_handed(
        mutation, leaf_args, expected_code, named, run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    (repo / "src.txt").write_text("the developer is still editing this\n")
    (repo / "new.txt").write_text("the developer has not committed this yet\n")
    leafargs_out = tmp_path / "leafargs"
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "LEAFARGS_OUT": str(leafargs_out), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}
    if leaf_args is not None:
        env["VERIFY_LEAF_ARGS"] = leaf_args
    env.update(checked_head(repo))
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, named in out, git_state(repo)) == (expected_code, True, before)
    if leaf_args is not None:
        reached = leafargs_out.read_text().splitlines()
        assert ("--disallowedTools" in reached, "MultiEdit" in reached) == (True, False)


@pytest.mark.process("a real git scratch repository whose verifier leaf edits a tracked file and makes an untracked one unreadable")
def test_verify_sh_does_not_accept_a_pass_from_a_verifier_leaf_that_left_an_unreadable_file_in_the_tree_2764(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'printf "the verifier rewrote this\\n" > src.txt; printf "secret\\n" > hidden.txt; chmod 000 hidden.txt'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository whose verifier leaf edits a tracked file and makes an untracked one unreadable")
def test_verify_sh_restores_a_tracked_file_the_leaf_edited_when_it_refuses_for_an_unreadable_file_2773(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'printf "the verifier rewrote this\\n" > src.txt; printf "secret\\n" > hidden.txt; chmod 000 hidden.txt'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, (repo / "src.txt").read_text()) == (2, "the developer committed this\n")


@pytest.mark.process("a real git scratch repository whose verifier leaf edits a tracked file and makes an untracked one unreadable")
def test_verify_sh_names_the_unreadable_file_on_stderr_when_it_refuses_for_one_the_leaf_left_2773(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'printf "the verifier rewrote this\\n" > src.txt; printf "secret\\n" > hidden.txt; chmod 000 hidden.txt'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, _, err = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "hidden.txt" in err) == (2, True)


@pytest.mark.process("a real git scratch repository whose verifier leaf adds a file and makes an untracked one unreadable")
def test_verify_sh_removes_a_file_the_leaf_added_when_it_refuses_for_an_unreadable_file_2784(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'printf "added\\n" > added.txt; printf "secret\\n" > hidden.txt; chmod 000 hidden.txt'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, (repo / "added.txt").exists()) == (2, False)


@pytest.mark.process("a real git scratch repository whose pin verifier leaf rewrites its mutation record and makes it unreadable")
def test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_rewrote_its_mutation_record_and_made_it_unreadable_2764(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2764")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2764-mutations.md\n",
                                  {".tdd/issue-2764-mutations.md": "mutation one\n"})
    mutation = 'printf "rewritten\\n" > .tdd/issue-2764-mutations.md; chmod 000 .tdd/issue-2764-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository whose pin verifier leaf replaces a mutation record that was unreadable before it ran")
def test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_left_a_regular_file_where_the_mutation_record_was_unreadable_2764(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2764")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2764-mutations.md\n",
                                  {".tdd/issue-2764-mutations.md": "mutation one\n"})
    subprocess.run(["chmod", "000", str(repo / ".tdd" / "issue-2764-mutations.md")], check=True)
    mutation = 'rm -f .tdd/issue-2764-mutations.md; printf "mutation one\\n" > .tdd/issue-2764-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository whose pin verifier leaf creates a mutation record that was absent before it ran")
def test_verify_sh_accepts_a_pass_from_a_pin_verifier_leaf_that_created_the_mutation_record_that_was_absent_2764(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2764")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2764-mutations.md\n", {})
    mutation = 'mkdir -p .tdd; printf "mutation one\\n" > .tdd/issue-2764-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo, issue="2764")}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (0, True)


@pytest.mark.process("a real git scratch repository whose pin verifier leaf replaces a mutation record that was a symlink before it ran")
def test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_replaced_a_symlinked_mutation_record_with_a_regular_file_2772(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2772")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2772-mutations.md\n", {})
    (tmp_path / "elsewhere.md").write_text("mutation one\n")
    (repo / ".tdd").mkdir(exist_ok=True)
    (repo / ".tdd" / "issue-2772-mutations.md").symlink_to(tmp_path / "elsewhere.md")
    mutation = 'rm -f .tdd/issue-2772-mutations.md; printf "mutation one\\n" > .tdd/issue-2772-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo, issue="2772")}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository holding an unreadable file, and a git wrapper translating Permission denied")
def test_verify_sh_does_not_accept_a_pass_from_a_verifier_leaf_that_left_an_unreadable_file_when_git_translates_its_messages_2772(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    wrapper = tmp_path / "translating-bin"
    wrapper.mkdir()
    (wrapper / "git").write_text(
        '#!/bin/sh\nerr="$(mktemp)"\n%s "$@" 2>"$err"\nrc=$?\n'
        'case "$LC_ALL" in de_*) sed "s/Permission denied/Zugriff verweigert/" "$err" >&2 ;; *) cat "$err" >&2 ;; esac\n'
        'rm -f "$err"\nexit $rc\n' % shutil.which("git"))
    (wrapper / "git").chmod(0o755)
    (repo / "hidden.txt").write_text("secret\n")
    subprocess.run(["chmod", "000", str(repo / "hidden.txt")], check=True)
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", "LC_ALL": "de_DE.UTF-8",
           "PATH": "%s:%s" % (wrapper, os.environ["PATH"]), **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository whose global config sets an external diff driver, color.ui=always and a textconv filter")
def test_verify_sh_saves_the_same_refusal_diff_whatever_the_global_git_config_says_1846(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {".gitattributes": "*.txt diff=shout\n"})
    driver = tmp_path / "external-driver"
    driver.write_text("#!/bin/sh\necho EXTERNAL-DRIVER-OUTPUT\n")
    driver.chmod(0o755)
    (tmp_path / ".gitconfig").write_text(
        "[diff]\n\texternal = %s\n[color]\n\tui = always\n[diff \"shout\"]\n\ttextconv = tr a-z A-Z <\n" % driver)
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "FAKE_MUTATE": 'printf "the verifier rewrote this\\n" > src.txt',
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    saved = list((repo / ".tdd").glob("*.diff"))
    text = saved[0].read_text() if saved else ""
    assert (code, [l for l in text.splitlines() if not l.startswith("index ")]) == (2, [
        "diff --git a/src.txt b/src.txt", "--- a/src.txt", "+++ b/src.txt", "@@ -1 +1 @@",
        "-the developer committed this", "+the verifier rewrote this"])


@pytest.mark.process("a real git scratch repository under the repo's own .gitignore that the verifier leaf writes into")
@pytest.mark.parametrize("tracked, mutation, verdict, expected_code, named", [
    ({}, 'mkdir -p projects/docs/.tdd && printf "{}\\n" > projects/docs/.tdd/events.jsonl',
     "VERDICT: PASS\nREASON: Target test and full suite are green.", 0, ["full suite are green"]),
    ({}, 'mkdir -p a/b/.tdd && printf "log\\n" > a/b/.tdd/run.log',
     "VERDICT: REJECT\nREASON: The target test still fails.", 1, ["target test still fails"]),
    ({".tdd/issue-569.md": "- [ ] a step\n"},
     'printf -- "- [x] a step\\n" > .tdd/issue-569.md && mkdir -p projects/docs/.tdd'
     ' && printf "{}\\n" > projects/docs/.tdd/events.jsonl',
     "VERDICT: PASS\nREASON: Target test and full suite are green.", 2,
     ["modified the repository", ".tdd/issue-569.md"]),
    ({"projects/docs/doomed.txt": "the developer committed this too\n"},
     'printf "the verifier rewrote this\\n" > src.txt && rm projects/docs/doomed.txt'
     ' && printf "new\\n" > projects/docs/added.txt && mkdir -p projects/docs/.tdd'
     ' && printf "{}\\n" > projects/docs/.tdd/events.jsonl',
     "VERDICT: PASS\nREASON: Target test and full suite are green.", 2,
     ["modified the repository", "src.txt", "projects/docs/doomed.txt", "projects/docs/added.txt"]),
])
def test_verify_sh_under_the_repos_own_gitignore_accepts_nested_run_state_and_refuses_an_edited_root_ledger_or_tracked_path_naming_each_569(
        tracked, mutation, verdict, expected_code, named, run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, (SCRIPTS.parents[2] / ".gitignore").read_bytes(), tracked)
    ignored = [subprocess.run(["git", "-C", str(repo), "check-ignore", "--no-index", "-q", path]).returncode == 0
               for path in (".tdd/issue-569.md", ".tdd/issue-569-spec.md")]
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation, "FAKE_OUT_TEXT": verdict,
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (ignored, code, [n for n in named if n not in out], "modified the repository" in out) == (
        [False, True], expected_code, [], expected_code == 2)



@pytest.mark.process("a real git scratch repository whose first verifier launch leaves an untracked file and whose second does not")
def test_verify_sh_relaunches_a_verifier_that_left_an_untracked_file_and_returns_the_relaunched_verdict_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "1")
    mutation = '[ -e .tdd/second-launch ] || { : > .tdd/second-launch; printf "stray\\n" > riting.ts; }'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, _, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    saved = list((repo / ".tdd").glob("*.diff"))
    diff = saved[0].read_text() if saved else ""
    log_events = repo / ".tdd" / "events.jsonl"
    relaunches = [json.loads(line) for line in log_events.read_text().splitlines()
                  if '"relaunch"' in line] if log_events.is_file() else []
    assert (code, git_state(repo), "riting.ts" in diff,
            [(r["event"], r.get("cause") != "no-verdict") for r in relaunches]) == (
        0, before, True, [("relaunch", True)])


@pytest.mark.process("a real git scratch repository whose first verifier launch edits a tracked file and whose second does not")
def test_verify_sh_relaunches_a_verifier_that_edited_a_tracked_file_and_returns_the_relaunched_verdict_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "1")
    mutation = '[ -e .tdd/second-launch ] || { : > .tdd/second-launch; printf "the verifier rewrote this\\n" > src.txt; }'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, _, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    log_events = repo / ".tdd" / "events.jsonl"
    relaunches = [json.loads(line) for line in log_events.read_text().splitlines()
                  if '"relaunch"' in line] if log_events.is_file() else []
    assert (code, git_state(repo), (repo / "src.txt").read_text(), [r.get("cause") for r in relaunches]) == (
        0, before, "the developer committed this\n", ["tree-change"])


@pytest.mark.process("a real git scratch repository whose first verifier launch commits and whose second does not")
def test_verify_sh_relaunches_a_verifier_that_moved_head_and_restores_head_and_the_tree_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "1")
    mutation = ('[ -e .tdd/second-launch ] || { : > .tdd/second-launch; printf "the verifier committed this\\n" > src.txt;'
                ' git commit -q -a -m "the verifier committed"; }')
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, _, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                  "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    log_events = repo / ".tdd" / "events.jsonl"
    relaunches = [json.loads(line) for line in log_events.read_text().splitlines()
                  if '"relaunch"' in line] if log_events.is_file() else []
    assert (code, git_state(repo), [r.get("cause") for r in relaunches]) == (0, before, ["tree-change"])


@pytest.mark.process("a real git scratch repository whose only verifier launch leaves an untracked file")
def test_verify_sh_refuses_a_verifier_that_left_an_untracked_file_without_a_relaunch_when_the_no_verdict_budget_is_0_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    mutation = 'echo launch >> .tdd/launches; printf "stray\\n" > riting.ts'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    launches = (repo / ".tdd" / "launches").read_text().splitlines()
    assert (code, "verifier leaf modified the repository — verdict not accepted" in out, launches,
            git_state(repo)) == (2, True, ["launch"], before)


@pytest.mark.process("a real git scratch repository whose every verifier launch leaves a new untracked file")
def test_verify_sh_writes_one_tree_change_relaunch_then_refuses_when_every_launch_leaves_an_untracked_file_2561(
        run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "1")
    mutation = 'echo launch >> .tdd/launches; printf "stray\\n" > "riting-$(wc -l < .tdd/launches).ts"'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo)}
    verify = importlib.import_module("veri.verify")
    before = git_state(repo)

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "green", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    log_events = repo / ".tdd" / "events.jsonl"
    relaunches = [json.loads(line) for line in log_events.read_text().splitlines()
                  if '"relaunch"' in line] if log_events.is_file() else []
    assert (code, "verifier leaf modified the repository — verdict not accepted" in out,
            [r.get("cause") for r in relaunches], git_state(repo)) == (2, True, ["tree-change"], before)


def attempts_trace(repo, phase):
    refs = subprocess.run(["git", "-C", str(repo), "for-each-ref", "--format=%(refname)", "refs/veri/attempts/"],
                          capture_output=True, check=True).stdout.decode().splitlines()
    shown = [subprocess.run(["git", "-C", str(repo), "show", ref + ":src.txt"],
                            capture_output=True).stdout.decode() for ref in refs]
    attempts = repo / ".tdd" / "attempts"
    copies = sorted(attempts.iterdir()) if attempts.is_dir() else []
    log = (repo / ".tdd" / ("verify-%s.log" % phase)).read_bytes()
    log_events = repo / ".tdd" / "events.jsonl"
    events = [json.loads(line) for line in log_events.read_text().splitlines()] if log_events.is_file() else []
    return refs, shown, [c.name for c in copies], [c.read_bytes() == log for c in copies], events


PRIVATE = "The test asserts on a private helper, not observable behavior."
REJECT_PRIVATE = "VERDICT: REJECT\nREASON: " + PRIVATE
RAMBLE = "the leaf rambled and never rendered a verdict"
JUDGED = "the work the verifier judged\n"
BLOCKER = "refs/veri/attempts/625/6"


@pytest.mark.process("a real git scratch repository whose rejected attempts land under refs/veri/attempts/,"
                     " behind the real supervise.sh, every event appended in-process")
@pytest.mark.parametrize("phase, leaf, text, env, expected", [
    pytest.param("green", "answers", "VERDICT: REJECT\nREASON: the helper it asserts on is still private.",
                 {"VERI_ISSUE": "409", "VERI_STEP": "4"},
                 (1, "the helper it asserts on is still private.\n", [("REJECT", "409", "4", None)],
                  ["refs/veri/attempts/409/4/verify-green-{attempt}"], ["4-verify-green-{attempt}-reject.log"], False),
                 id="reject-preserved"),
    pytest.param("green", "answers", RAMBLE, {"VERI_ISSUE": "409", "VERI_STEP": "5", "VERI_NO_VERDICT_RETRIES": "0"},
                 (2, "\n", [("malformed", "409", "5", "no-verdict")],
                  ["refs/veri/attempts/409/5/verify-green-{attempt}"], ["5-verify-green-{attempt}-no-verdict.log"],
                  False), id="no-verdict-preserved"),
    pytest.param("green", "answers", GREEN, {"VERI_ISSUE": "409", "VERI_STEP": "7"},
                 (0, GREEN_REASON + "\n", [("PASS", "409", "7", None)], [], [], False), id="pass-nothing"),
    pytest.param("green", "fails", GREEN, {"VERI_ISSUE": "409", "VERI_STEP": "7"},
                 (0, GREEN_REASON + "\n", [("PASS", "409", "7", None)], [], [], False), id="clean-failure-nothing"),
    pytest.param("red", "answers", REJECT_PRIVATE, {"VERI_ISSUE": "625", "VERI_STEP": "6"},
                 (1, PRIVATE + "\n", [("REJECT", "625", "6", None)], [BLOCKER], [], True),
                 id="unpreservable-reason-alone"),
    pytest.param("red", "hangs", REJECT_PRIVATE, {"VERI_ISSUE": "409", "VERI_STEP": "8"},
                 (2, "verifier leaf killed-stuck — no verdict rendered (see .tdd/verify-red.log)\n", [],
                  ["refs/veri/attempts/409/8/verify-red-1"], ["8-verify-red-1-stuck.log"], False),
                 id="killed-leaves-no-verdict"),
])
def test_verify_sh_preserves_a_rejected_or_no_verdict_attempt_under_its_ref_and_a_copy_its_verdict_event_names_and_answers_the_verdicts_reason_and_code_alone(
        phase, leaf, text, env, expected, run_cli, tmp_path, monkeypatch):
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/\n", {})
    (repo / "src.txt").write_text(JUDGED)
    if BLOCKER in expected[3]:
        subprocess.run(["git", "-C", str(repo), "update-ref", BLOCKER, "HEAD"], check=True)
    if leaf != "answers":
        claude = tmp_path / ("claude-" + leaf)
        claude.write_text({"fails": "#!/bin/sh\nprintf '%s' \"$FAKE_OUT_TEXT\"\nexit 1\n",
                           "hangs": HUNG_LEAF}[leaf])
        claude.chmod(0o755)
    step = checked_head(repo, issue=env["VERI_ISSUE"], step=int(env["VERI_STEP"])) if "VERI_STEP" in env else {}
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_OUT_TEXT": text,
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **step, **env}
    if leaf == "hangs":
        env.update(VERI_STUCK_RETRIES="0", VERI_TIMEOUT="0")
    verify = importlib.import_module("veri.verify")

    code, out, err = run_cli(verify, [*(FAST if phase == "green" else []), phase, str(tmp_path / "spec.md"),
                                      "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    refs, shown, copies, paired, events = attempts_trace(repo, phase)
    verdicts = [e for e in events if e.get("event") == "verdict"]
    attempt = verdicts[0].get("attempt") if verdicts else None
    want_code, want_out, want_verdicts, want_refs, want_copies, unpreserved = expected
    assert (code, out, [(e.get("verdict"), e.get("issue"), e.get("step"), e.get("cause")) for e in verdicts],
            refs, copies, "verify: could not preserve the reject attempt" in err) == (
        want_code, want_out, want_verdicts, [r.format(attempt=attempt) for r in want_refs],
        [c.format(attempt=attempt) for c in want_copies], unpreserved)
    assert (shown, paired) == ([JUDGED if r != BLOCKER else "the developer committed this\n" for r in refs],
                               [True] * len(copies))
    assert [e.get("event") for e in events if e.get("event") == "exit"] != []
    if leaf == "fails":
        assert (repo / ".tdd" / "verify-green.rc").read_text().strip() == "1"


DIFF_STEP = "DIFF-STEP the old cases are gone"
DIFF = ["--step", DIFF_STEP, *FAST, "diff", "{spec}", "0123abc", "0123abc"]
REBASE = ["rebase", "{spec}", "0123abc", "4567def"]
NO_STEP = "build-verify-prompt: diff needs --step '<STEP>'"
NON_HEX = "build-verify-prompt: diff needs <base-sha> as 7-40 lowercase hex characters, got 'not-a-sha'"
TOO_MANY = "build-verify-prompt: too many arguments"
STEP_VALUE = "verify: --step needs a value"


@pytest.mark.parametrize("entry, argv, leaf_out, expected", [
    pytest.param("run_verdict", REBASE, "VERDICT: PASS\nREASON: both sides kept.",
                 (0, None, ["verify-rebase"], []), id="rebase-pass"),
    pytest.param("run_verdict", REBASE, "VERDICT: REJECT\nREASON: the onto side is dropped.",
                 (1, None, ["verify-rebase"], []), id="rebase-reject"),
    pytest.param("run_verdict", REBASE, "VERDICT: MAYBE\nREASON: might be fine.",
                 (2, None, ["verify-rebase"], []), id="rebase-malformed"),
    *[pytest.param(entry, DIFF, text, (code, None, ["verify-diff"], ["git diff 0123abc..HEAD", DIFF_STEP, SPEC]),
                   id="diff-%s-%s" % (word, entry))
      for entry in ("verify", "run_verdict")
      for word, text, code in (("pass", "VERDICT: PASS\nREASON: the diff removes the cases.", 0),
                               ("reject", "VERDICT: REJECT\nREASON: the diff leaves a case behind.", 1))],
    *[pytest.param(entry, argv, GREEN, (2, message, [], []), id="%s-%s" % (label, entry))
      for entry in ("verify", "run_verdict")
      for label, argv, message in (
          ("no-step", [*FAST, "diff", "{spec}", "0123abc", "0123abc"], NO_STEP),
          ("non-hex", ["--step", DIFF_STEP, *FAST, "diff", "{spec}", "not-a-sha", "0123abc"], NON_HEX),
          ("extra", [*DIFF, "extra"], TOO_MANY))],
    pytest.param("verify", ["--step", "", "red", "{spec}", "tests/test_slugify.py", "test_lowercases"], GREEN,
                 (2, STEP_VALUE, [], []), id="empty-step"),
    pytest.param("verify", ["--step"], GREEN, (2, STEP_VALUE, [], []), id="trailing-step"),
])
def test_verify_sh_and_run_verdict_sh_answer_a_rebase_or_diff_verdict_from_one_leaf_named_for_the_phase_and_refuse_a_bad_step_sha_or_extra_argument_with_exit_2_the_named_checks_message_first_and_no_leaf(
        entry, argv, leaf_out, expected, run_cli, tmp_path, monkeypatch):
    (tmp_path / "spec.md").write_text(SPEC)
    argv = [word.format(spec=tmp_path / "spec.md") for word in argv]
    verify = importlib.import_module("veri.verify")
    launches = answering_leaf(monkeypatch, leaf_out)

    def exec_verify(path, words):
        assert os.path.basename(path) == "verify.sh"
        raise SystemExit(verify.main(list(words[1:])))

    monkeypatch.setattr(os, "execv", exec_verify)
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    code, _, err = run_cli(importlib.import_module("veri." + entry), argv,
                           env={"HOME": str(tmp_path)}, cwd=tmp_path)

    want_code, want_first, want_leaves, present = expected
    first = err.splitlines()[0] if err else ""
    assert (code, first if want_first is not None else None, [leaf for leaf, _ in launches]) == (
        want_code, want_first, want_leaves)
    assert [text for text in present for _, prompt in launches if text not in prompt] == []


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_verify_sh_diff_exits_1_without_launching_the_leaf_naming_the_pytest_case_a_step_deleted_that_an_earlier_step_added_1486(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_refuses_start():\n    pass\n")
    step_base = commit("an earlier step adds test_refuses_start")
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    commit("this step deletes test_refuses_start")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "no test fakes X any longer ⟦diff-checked⟧", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "tests/test_start.py::test_refuses_start" in out, started.exists()) == (1, True, False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_verify_sh_diff_still_launches_the_leaf_for_a_pytest_case_an_earlier_step_added_and_this_step_moved_to_another_file_under_the_same_name_1486(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    (repo / "tests" / "test_moved.py").write_text("def test_other():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_refuses_start():\n    pass\n")
    step_base = commit("an earlier step adds test_refuses_start")
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    (repo / "tests" / "test_moved.py").write_text(
        "def test_other():\n    pass\n\n\ndef test_refuses_start():\n    pass\n")
    commit("this step moves test_refuses_start to test_moved.py")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "no test fakes X any longer ⟦diff-checked⟧", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "test_refuses_start" in out, started.exists()) == (0, False, True)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2329_verify_sh_diff_launches_the_leaf_for_a_pytest_case_an_earlier_step_added_and_this_step_renamed_with_its_text_otherwise_unchanged(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_exits_with_the_command_code():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds test_exits_with_the_command_code")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_exits_1():\n    assert 1 == 1\n")
    commit("this step renames the case, its body unchanged")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "test_exits_with_the_command_code" in out, started.exists()) == (0, False, True)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2329_verify_sh_diff_exits_1_naming_a_renamed_case_whose_body_or_def_line_also_changed_and_a_removed_case_without_launching_the_leaf(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_body_alpha():\n    assert 1 == 1\n"
        "\n\ndef test_head_beta():\n    assert 2 == 2\n"
        "\n\ndef test_gone_gamma():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds three cases")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_body_renamed():\n    assert 1 == 2\n"
        "\n\ndef test_head_renamed(tmp_path):\n    assert 2 == 2\n")
    commit("this step renames two cases and changes a line of each, and removes the third")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, started.exists()) == (1, False)
    for vanished in ("test_body_alpha", "test_gone_gamma", "test_head_beta"):
        assert "tests/test_start.py::" + vanished in out


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2329_verify_sh_diff_exits_1_naming_a_renamed_case_whose_decorator_line_also_changed_without_launching_the_leaf(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\n@pytest.mark.timeout(5)\ndef test_decorated_old():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds test_decorated_old")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\n@pytest.mark.timeout(60)\ndef test_decorated_new():\n    assert 1 == 1\n")
    commit("this step renames the case and changes its decorator")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, started.exists()) == (1, False)
    assert "tests/test_start.py::test_decorated_old" in out


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2594_verify_sh_diff_exits_1_with_a_line_naming_a_case_renamed_and_changed_to_be_split_without_launching_the_leaf(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_defaults_to_3_2594():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds test_defaults_to_3_2594")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_defaults_to_5_2594():\n    assert 5 == 5\n")
    commit("this step renames the case and changes its body")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    named = [line for line in out.splitlines()
             if "tests/test_start.py::test_defaults_to_3_2594 -> " in line and "test_defaults_to_5_2594" in line]
    assert (code, started.exists(), len(named)) == (1, False, 1)
    assert "renamed" in named[0] and "split" in named[0]


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2594_verify_sh_diff_launches_the_leaf_and_exits_0_on_its_pass_printing_no_renamed_and_changed_line_for_a_case_renamed_with_its_body_and_def_line_unchanged(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_defaults_to_3_2594():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds test_defaults_to_3_2594")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_defaults_to_5_2594():\n    assert 3 == 3\n")
    commit("this step renames the case, its body unchanged")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, started.exists(), "renamed" in out or "split" in out) == (0, True, False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2594_verify_sh_diff_exits_1_with_the_deleted_cases_line_and_no_traceback_for_an_async_case_removed_with_no_counterpart(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\nasync def test_async_2594():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds test_async_2594")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_unrelated_2594():\n    assert 1 == 1\n")
    commit("this step removes the async case and adds an unrelated one")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, err = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists(), "Traceback" in err) == (
        1, "step deleted pytest cases an earlier step added: tests/test_start.py::test_async_2594", False, False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2594_verify_sh_diff_exits_1_with_the_deleted_cases_line_alone_for_a_removed_case_whose_def_line_no_added_case_shares_but_for_the_name(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_dropped_2594():\n    assert 3 == 3\n")
    step_base = commit("an earlier step adds test_dropped_2594")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_other_2594(tmp_path):\n    assert 5 == 5\n")
    commit("this step drops the case and adds one with another def line")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted pytest cases an earlier step added: tests/test_start.py::test_dropped_2594", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2419_verify_sh_diff_exits_1_naming_exactly_one_of_two_identical_removed_cases_when_one_added_case_carries_their_text(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_alpha():\n    assert 1 == 1\n"
        "\n\ndef test_beta():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds two identical cases")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_gamma():\n    assert 1 == 1\n")
    commit("this step removes both and adds one case with their text")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted pytest cases an earlier step added: tests/test_start.py::test_beta", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2419_verify_sh_diff_exits_1_naming_exactly_the_third_of_three_identical_removed_cases_when_two_added_cases_carry_their_text(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_alpha():\n    assert 1 == 1\n"
        "\n\ndef test_beta():\n    assert 1 == 1\n"
        "\n\ndef test_delta():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds three identical cases")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_gamma():\n    assert 1 == 1\n"
        "\n\ndef test_epsilon():\n    assert 1 == 1\n")
    commit("this step removes all three and adds two cases with their text")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted pytest cases an earlier step added: tests/test_start.py::test_delta", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2419_verify_sh_diff_launches_the_leaf_for_a_single_removed_case_renamed_to_one_added_case_while_an_identical_twin_stays(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_alpha():\n    assert 1 == 1\n"
        "\n\ndef test_twin():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds two identical cases")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_gamma():\n    assert 1 == 1\n"
        "\n\ndef test_twin():\n    assert 1 == 1\n")
    commit("this step renames one case; its identical twin stays")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts \u27e6diff-checked\u27e7", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "test_alpha" in out, started.exists()) == (0, False, True)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_2329_verify_sh_diff_exits_1_naming_a_removed_case_whose_text_reappears_under_another_name_in_another_file(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    (repo / "tests" / "test_other.py").write_text("def test_other_keeps():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_moved_old():\n    assert 1 == 1\n")
    step_base = commit("an earlier step adds test_moved_old")
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    (repo / "tests" / "test_other.py").write_text(
        "def test_other_keeps():\n    pass\n\n\ndef test_moved_new():\n    assert 1 == 1\n")
    commit("this step removes the case and adds an identical one under another name in another file")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the case names what it asserts ⟦diff-checked⟧", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, out.strip(), started.exists()) == (
        1, "step deleted pytest cases an earlier step added: tests/test_start.py::test_moved_old", False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_verify_sh_diff_exits_2_without_launching_the_leaf_when_the_step_base_sha_does_not_resolve_1486(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "test_start.py").write_text("def test_keeps():\n    pass\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "branch base"], check=True)
    branch_base = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                                 capture_output=True).stdout.decode().strip()
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "no test fakes X any longer ⟦diff-checked⟧", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, "0123456789abcdef0123456789abcdef01234567"],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "VERDICT" in out, started.exists()) == (2, False, False)


@pytest.mark.process("a real git scratch repository whose history the diff check reads, and a stub claude that records any start")
def test_verify_sh_diff_still_launches_the_leaf_and_returns_its_verdict_when_the_step_deletes_only_a_pytest_case_that_existed_at_the_branch_base_1486(
        run_cli, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_start.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_fakes_x():\n    pass\n")
    branch_base = commit("branch base")
    (repo / "tests" / "test_other.py").write_text("def test_added_earlier():\n    pass\n")
    step_base = commit("an earlier step adds an unrelated case")
    (repo / "tests" / "test_start.py").write_text("def test_keeps():\n    pass\n")
    commit("this step deletes test_fakes_x, which predates the branch")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "no test fakes X any longer ⟦diff-checked⟧", "--fast-cmd", "make unit", "diff",
                 str(tmp_path / "spec.md"), branch_base, step_base],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "test_fakes_x" in out, started.exists(), out == "fine.\n") == (0, False, True, True)


def test_verify_sh_green_exits_2_when_the_named_cases_check_cannot_read_the_suite_after_a_pass_1507(
        run_cli, tmp_path, monkeypatch):
    write_inputs(tmp_path)
    answering_leaf(monkeypatch, "VERDICT: PASS\nREASON: the named cases are gone.")
    verify = importlib.import_module("veri.verify")
    monkeypatch.setattr(verify.replaces_case_survivors, "main", lambda argv: 2)

    code, out, _ = run_cli(
        verify, ["--step", "the replacement takes over: replaces 'stale first' in tests/demo.test.sh"
                 " ⟦replaces-case⟧ ⟦criterion 1⟧", "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert code == 2


def test_verify_sh_green_returns_the_leafs_pass_unchanged_on_a_step_without_replaces_case_even_when_its_text_names_a_surviving_case_1507(
        run_cli, tmp_path, monkeypatch):
    write_inputs(tmp_path)
    (tmp_path / "tests" / "demo.test.sh").write_text('verdict "stale first" 0\n')
    answering_leaf(monkeypatch, "VERDICT: PASS\nREASON: fine.")
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the replacement takes over: replaces 'stale first' in tests/demo.test.sh"
                 " ⟦criterion 2⟧", "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (0, "fine.\n")


def test_verify_sh_green_returns_the_leafs_pass_with_exit_0_on_a_replaces_case_step_whose_every_named_case_is_gone_1507(
        run_cli, tmp_path, monkeypatch):
    write_inputs(tmp_path)
    (tmp_path / "tests" / "demo.test.sh").write_text('verdict "kept case" 0\n')
    answering_leaf(monkeypatch, "VERDICT: PASS\nREASON: the named cases are gone.")
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the replacement takes over: replaces 'stale first', 'stale second' in tests/demo.test.sh"
                 " ⟦replaces-case⟧ ⟦criterion 2⟧", "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (0, "the named cases are gone.\n")


def test_verify_sh_green_returns_the_leafs_pass_with_exit_0_on_a_step_naming_the_replaces_case_mark_without_a_replaces_clause_1603(
        run_cli, tmp_path, monkeypatch):
    write_inputs(tmp_path)
    answering_leaf(monkeypatch, "VERDICT: PASS\nREASON: fine.")
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the Red prompt describes the \u27e6replaces-case\u27e7 mark \u27e6criterion 1\u27e7",
                 "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (0, "fine.\n")


def test_verify_sh_green_returns_the_leafs_pass_with_exit_0_on_a_replaces_case_step_with_a_quoted_case_but_no_suite_path_1603(
        run_cli, tmp_path, monkeypatch):
    write_inputs(tmp_path)
    answering_leaf(monkeypatch, "VERDICT: PASS\nREASON: fine.")
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["--step", "the Red prompt says replaces 'stale first' \u27e6replaces-case\u27e7 \u27e6criterion 4\u27e7",
                 "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (0, "fine.\n")


@pytest.mark.parametrize("suite, check", [
    ('verdict "kept case" 0\n', None),
    ('verdict "stale first" 0\n', None),
    ('verdict "kept case" 0\n', 2),
], ids=["every-named-case-gone", "a-named-case-survives", "the-check-cannot-answer"])
def test_verify_sh_green_returns_the_leafs_reject_with_exit_1_and_its_own_reason_on_a_replaces_case_step_whatever_the_named_cases_check_would_say_1507(
        suite, check, run_cli, tmp_path, monkeypatch):
    write_inputs(tmp_path)
    (tmp_path / "tests" / "demo.test.sh").write_text(suite)
    answering_leaf(monkeypatch, "VERDICT: REJECT\nREASON: the replacement asserts nothing.")
    verify = importlib.import_module("veri.verify")
    if check is not None:
        monkeypatch.setattr(verify.replaces_case_survivors, "main", lambda argv: check)

    code, out, _ = run_cli(
        verify, ["--step", "the replacement takes over: replaces 'stale first' in tests/demo.test.sh"
                 " ⟦replaces-case⟧ ⟦criterion 1⟧", "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"],
        env={"HOME": str(tmp_path)},
        cwd=tmp_path)

    assert (code, out) == (1, "the replacement asserts nothing.\n")


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that rewrites a tracked file")
def test_main_saves_the_content_diff_of_a_verifier_that_modified_a_tracked_file_under_dot_tdd_named_after_the_leaf_and_names_it_in_the_refusal_1846(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    expected = []
    verify = importlib.import_module("veri.verify")
    real_start = verify.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\nTWO\nthree\n")
        expected.append(git("diff", "HEAD", "--", "tracked.txt"))
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify, "start", stub_start)

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    out = capfd.readouterr().out
    named = [m for m in re.findall(r"\.tdd/verify-green[\w.-]*", out)
             if not m.endswith((".log", ".prompt"))]
    saved = [(repo / m).read_bytes() for m in named if (repo / m).is_file()]
    assert (code, len(named), saved, (repo / "tracked.txt").read_text()) == (
        2, 1, expected, "one\ntwo\nthree\n")


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that changes only a tracked file's mode")
def test_main_saves_a_mode_only_change_of_a_verifier_in_the_diff_byte_exactly_1846(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.sh").write_text("echo hi\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    git("init", "-q")
    git("config", "core.fileMode", "true")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    expected = []
    verify = importlib.import_module("veri.verify")
    real_start = verify.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        os.chmod(repo / "tracked.sh", 0o755)
        expected.append(git("diff", "HEAD", "--", "tracked.sh"))
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify, "start", stub_start)

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    out = capfd.readouterr().out
    named = [m for m in re.findall(r"\.tdd/verify-green[\w.-]*", out)
             if not m.endswith((".log", ".prompt"))]
    saved = [(repo / m).read_bytes() for m in named if (repo / m).is_file()]
    assert (code, len(named), saved, b"new mode 100755" in expected[0]) == (2, 1, expected, True)


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that changes a tracked binary file")
def test_main_saves_a_binary_change_of_a_verifier_in_a_diff_that_applies_with_binary_1846(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    before = bytes([0, 1, 2, 255, 254, 0, 7]) * 40
    after = bytes([0, 9, 8, 255, 0, 0, 3, 128]) * 40
    (repo / "blob.bin").write_bytes(before)
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    verify = importlib.import_module("veri.verify")
    real_start = verify.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "blob.bin").write_bytes(after)
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify, "start", stub_start)

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    out = capfd.readouterr().out
    named = [m for m in re.findall(r"\.tdd/verify-green[\w.-]*", out)
             if not m.endswith((".log", ".prompt"))]
    applied = None
    if len(named) == 1 and (repo / named[0]).is_file():
        patch = (repo / named[0]).resolve()
        subprocess.run(["git", "apply", "--binary", str(patch)], cwd=repo,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        applied = (repo / "blob.bin").read_bytes()
    assert (code, len(named), applied) == (2, 1, after)


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that rewrites a tracked file and leaves a directory at the diff path")
def test_main_still_refuses_with_2_and_resets_the_tree_saying_the_diff_could_not_be_saved_when_its_path_is_a_directory_1846(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    verify = importlib.import_module("veri.verify")
    real_start = verify.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\nTWO\nthree\n")
        (repo / ".tdd" / "verify-green.diff").mkdir()
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify, "start", stub_start)

    try:
        code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    except OSError as error:
        code = repr(error)

    out = capfd.readouterr().out
    assert (code, "verifier leaf modified the repository" in out,
            bool(re.search(r"diff could not be saved", out)),
            (repo / "tracked.txt").read_text()) == (2, True, True, "one\ntwo\nthree\n")


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that rewrites a tracked file while git diff is made to fail")
def test_main_still_refuses_with_2_saying_the_diff_could_not_be_saved_and_writes_no_diff_when_git_diff_fails_1878(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    verify = importlib.import_module("veri.verify")
    real_start = verify.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\nTWO\nthree\n")
        git("config", "diff.orderFile", str(tmp_path / "no-such-order-file"))
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify, "start", stub_start)

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    out = capfd.readouterr().out
    assert (code, "verifier leaf modified the repository" in out,
            bool(re.search(r"diff could not be saved to \.tdd/verify-green\.diff", out)),
            sorted(p.name for p in (repo / ".tdd").glob("*.diff"))) == (2, True, True, [])


@pytest.mark.process("a real git scratch repository and a stub verifier leaf that rewrites a tracked file while git diff is made to fail over an earlier refusal's diff")
def test_main_removes_an_earlier_refusals_diff_when_this_refusals_diff_could_not_be_saved_1878(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    (repo / ".tdd").mkdir(exist_ok=True)
    (repo / ".tdd" / "verify-green.diff").write_text("an earlier refusal's diff\n")
    verify = importlib.import_module("veri.verify")
    real_start = verify.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\nTWO\nthree\n")
        git("config", "diff.orderFile", str(tmp_path / "no-such-order-file"))
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify, "start", stub_start)

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    out = capfd.readouterr().out
    assert (code, bool(re.search(r"diff could not be saved to \.tdd/verify-green\.diff", out)),
            sorted(p.name for p in (repo / ".tdd").glob("*.diff"))) == (2, True, [])


@pytest.mark.process("a real git scratch repository, a stub verifier leaf that rewrites a tracked file, and a real git apply --check")
def test_main_saves_a_diff_that_passes_git_apply_check_whatever_the_users_prefix_context_and_abbreviation_config_says_1878(
        tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    (tmp_path / "home").mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    write_inputs(repo)
    (repo / "tracked.txt").write_text("one\ntwo\nthree\nfour\nfive\n")
    (repo / ".gitignore").write_text(".tdd/\n")

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo, stdout=subprocess.PIPE, check=True).stdout

    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    verify = importlib.import_module("veri.verify")
    real_start = verify.start

    def stub_start(args, **kwargs):
        if os.path.basename(str(args[0])) != "supervise.sh":
            return real_start(args, **kwargs)
        (repo / "tracked.txt").write_text("one\ntwo\nTHREE\nfour\nfive\n")
        git("config", "diff.noprefix", "true")
        git("config", "diff.context", "0")
        git("config", "core.abbrev", "4")
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nREASON: ok\n")

    monkeypatch.setattr(verify, "start", stub_start)

    code = verify.main(["--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    capfd.readouterr()
    saved = list((repo / ".tdd").glob("*.diff"))
    checked = None
    if len(saved) == 1:
        checked = subprocess.run(["git", "apply", "--check", str(saved[0])], cwd=repo,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode
    assert (code, len(saved), checked) == (2, 1, 0)


@pytest.mark.process("a real git scratch repository whose rebased range the marker check reads, and a stub claude that records any start")
def test_verify_sh_rebase_exits_1_without_launching_the_leaf_naming_the_commit_and_file_that_added_a_conflict_marker_a_later_commit_removed_2516(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 2 |\n")
    onto = commit("onto")
    (repo / "docs" / "backend.md").write_text(
        "| a | b |\n|---|---|\n<<<<<<< HEAD\n| 1 | 2 |\n=======\n| 1 | 3 |\n>>>>>>> topic\n")
    marked = commit("rebase resolution keeping the markers")
    (repo / "notes.txt").write_text("unrelated\n")
    commit("an unrelated commit")
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 3 |\n")
    commit("a later commit removes the markers")
    pre_rebase = onto
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["rebase", str(tmp_path / "spec.md"), onto, pre_rebase],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, marked in out, "docs/backend.md" in out, started.exists()) == (1, True, True, False)


@pytest.mark.process("a real git scratch repository whose rebased range the marker check reads, and a stub claude that records any start")
def test_verify_sh_rebase_exits_1_without_launching_the_leaf_when_a_commit_added_only_a_closing_conflict_marker_2516(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 2 |\n")
    onto = commit("onto")
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 2 |\n>>>>>>> topic\n")
    marked = commit("rebase resolution keeping a closing marker")
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 3 |\n")
    commit("a later commit removes the marker")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["rebase", str(tmp_path / "spec.md"), onto, onto],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, marked in out, "docs/backend.md" in out, started.exists()) == (1, True, True, False)


@pytest.mark.process("a real git scratch repository whose rebased range the marker check reads, and a stub claude that records any start")
def test_verify_sh_rebase_launches_the_leaf_and_returns_its_verdict_when_no_commit_of_the_range_adds_a_conflict_marker_2516(
        run_cli, tmp_path):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.name", "veri"), ("user.email", "veri@example.test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)

    def commit(message):
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True)
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True).stdout.decode().strip()

    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "backend.md").write_text("| a | b |\n|---|---|\n| 1 | 2 |\n")
    onto = commit("onto")
    (repo / "docs" / "backend.md").write_text("Title\n=======\n| a | b |\n|---|---|\n| 1 | 3 |\n")
    commit("a clean resolution with a setext heading")
    (repo / "notes.txt").write_text("unrelated\n")
    commit("an unrelated commit")
    started = tmp_path / "started"
    claude = tmp_path / "claude-record"
    claude.write_text('#!/bin/sh\necho started >> "%s"\nprintf \'VERDICT: PASS\\nREASON: fine.\'\n' % started)
    claude.chmod(0o755)
    (tmp_path / "spec.md").write_text(SPEC)
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(
        verify, ["rebase", str(tmp_path / "spec.md"), onto, onto],
        env={"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"},
        cwd=repo)

    assert (code, "docs/backend.md" in out, started.exists()) == (0, False, True)


@pytest.mark.process("a real git scratch repository whose pin verifier leaf replaces a mutation record that was a directory before it ran")
def test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_replaced_a_directory_mutation_record_with_a_regular_file_2772(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2772")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2772-mutations.md\n", {})
    (repo / ".tdd" / "issue-2772-mutations.md").mkdir(parents=True)
    mutation = 'rmdir .tdd/issue-2772-mutations.md; printf "mutation one\\n" > .tdd/issue-2772-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo, issue="2772")}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (2, False)


@pytest.mark.process("a real git scratch repository whose pin verifier leaf creates a mutation record that was truly absent before it ran")
def test_verify_sh_still_accepts_a_pass_from_a_pin_verifier_leaf_that_created_a_truly_absent_mutation_record_2772(
        run_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "2772")
    repo, claude = tamper_scratch(tmp_path, monkeypatch, b".tdd/*\n!.tdd/issue-2772-mutations.md\n", {})
    mutation = 'mkdir -p .tdd; printf "mutation one\\n" > .tdd/issue-2772-mutations.md'
    env = {"HOME": str(tmp_path), "CLAUDE_BIN": str(claude), "FAKE_MUTATE": mutation,
           "FAKE_OUT_TEXT": "VERDICT: PASS\nREASON: Target test and full suite are green.",
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **checked_head(repo, issue="2772")}
    verify = importlib.import_module("veri.verify")

    code, out, _ = run_cli(verify, ["--fast-cmd", "make unit", "pin", str(tmp_path / "spec.md"),
                                    "tests/test_slugify.py", "test_lowercases"], env=env, cwd=repo)

    assert (code, "full suite are green" in out) == (0, True)
