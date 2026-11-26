"""In-process cases for veri/verify.py, the module verify.sh is a shim over."""
import importlib
import io
import json
import os
import pathlib
import re
import signal
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.fixture(autouse=True)
def no_ambient_leaf_args(monkeypatch):
    monkeypatch.delenv("VERIFY_LEAF_ARGS", raising=False)


BRANCH = ["--branch-base", "0123abc"]  # the run's recorded branch base every phase takes (#4375, #4376)
USAGE = (b"usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] [--supersede-base <sha>|--frozen-edit <sha>] [--step-green <sha>]"
         b" --branch-base <sha> <phase> <issue-spec-file> <test-path> [<target-test-id>]"
         b"\n       verify.sh --fast-cmd '<CMD>' --branch-base <sha> branch <issue-spec-file>")


def write_inputs(directory):
    directory = pathlib.Path(directory)
    (directory / "tests").mkdir(exist_ok=True)
    (directory / "spec.md").write_text("the behavior spec\n")
    (directory / "tests" / "x.test.sh").write_text("test\n")


def assert_prompt_rendered(directory="."):
    prompts = sorted((pathlib.Path(directory) / ".tdd").glob("verify-*.prompt"))
    assert [b"the behavior spec" in prompt.read_bytes() for prompt in prompts] == [True]


def record(event, *pairs, issue="", step="", phase="green"):
    named = {"name": "verify-" + phase} if event == "verdict" else {}
    return {"issue": issue, "actor": "verifier", "phase": phase, "step": step, "event": event, "attempt": "1",
            "skill_commit": "", **dict(pair.split("=", 1) for pair in pairs), **named}


def through_fixture(fake_processes, fake):
    """Hand the local <fake>(args, *rest, **kwargs), which answers with a CompletedProcess, to fake_processes as one callable answer."""
    holder = []

    def answer(line, **kwargs):
        done = holder[0].argvs[-1]
        done = fake(done, **kwargs)
        if not isinstance(done, subprocess.CompletedProcess):
            return 0, done, b""
        return done.returncode, done.stdout, done.stderr

    holder.append(fake_processes.answers({"": answer}))
    return holder[0]


@pytest.mark.parametrize("argv", [[], ["green", "spec"], ["--step", "x", "green"]])
def test_main_with_fewer_than_three_positionals_returns_2_with_the_usage_line_alone_and_starts_no_process(
        argv, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes()
    verify = importlib.import_module("veri.verify")

    code = verify.main(list(argv))

    captured = capfdbinary.readouterr()
    assert len(USAGE) == 279
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


@pytest.mark.parametrize("phase", ["red", "green", "refactor", "pin", "surround", "plan", "rebase", "diff"])
@pytest.mark.parametrize("flag, got", [([], b""), (["--branch-base", "not-a-sha"], b"not-a-sha"),
                                       (["--branch-base", "ABC1234"], b"ABC1234"), (["--branch-base", "abc123"], b"abc123"),
                                       (["--branch-base", "abc1234z"], b"abc1234z")])
def test_main_with_branch_base_missing_or_not_hex_returns_2_naming_the_flag_then_the_usage_line_and_starts_no_process_4375(
        phase, flag, got, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*flag, phase, "spec.md", "tests/test_x.py"])

    captured = capfdbinary.readouterr()
    assert (code, captured.out, captured.err, calls) == (
        2, b"", b"verify: %s needs --branch-base <sha> as 7-40 lowercase hex characters, got '%s'\n" % (
            phase.encode(), got) + USAGE + b"\n", [])


@pytest.mark.parametrize("argv, stderr", [
    (["green", "missing-spec.md", "tests/x.test.sh"], b"build-verify-prompt: cannot read 'missing-spec.md'\n"),
    (["bogus", "spec.md", "tests/x.test.sh"], b"build-verify-prompt: unknown phase 'bogus'"),
])
def test_main_returns_the_builders_refusal_mapped_into_the_contract_with_its_stderr_and_launches_no_leaf(
        argv, stderr, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    launched = []

    def fake(args, *_, **__):
        launched.append(os.path.basename(str(args[0])))
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", *argv])

    captured = capfdbinary.readouterr()
    assert (code, captured.out, stderr in captured.err, launched,
            (tmp_path / ".tdd" / "verify-green.prompt").exists()) == (2, b"", True, [], False)


def test_main_calls_the_builder_beside_the_shim_as_called_with_the_consumed_pairs_and_every_positional_and_writes_its_stdout_as_the_prompt_file(
        tmp_path, monkeypatch, fake_processes):
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
    answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine")
    before = set(sys.modules)
    try:
        verify = importlib.import_module("veri.verify")
        argv = [*BRANCH, "--step", "--fast-cmd", "--fast-cmd", "make unit",
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
        leaf_args, tmp_path, monkeypatch, fake_processes):
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

    through_fixture(fake_processes, fake)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, fake)
    verify = importlib.import_module("veri.verify")
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(verify.__file__)))

    verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    supervised = [call for call in started if os.path.basename(call[0][0]) == "supervise.sh"]
    assert supervised == [([os.path.join(scripts, "supervise.sh"), "verify-green",
                            os.path.join(scripts, "run-leaf.sh"), ".tdd/verify-green.prompt",
                            "--permission-mode", "bypassPermissions",
                            "--settings", json.dumps({"hooks": verify.WRITE_BAN})],
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
        phase, leaf_out, expected, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    answering_leaf(monkeypatch, fake_processes, leaf_out)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", *(["--step-green", "0123abc"] if phase == "refactor" else []),
                        phase, "spec.md", "tests/x.test.sh", *(["0123abc"] if phase == "refactor" else [])])

    assert (code, capfdbinary.readouterr().out) == expected


def test_main_drops_nul_bytes_from_the_leafs_output_so_a_verdict_carrying_them_is_read_as_the_same_verdict_without_them(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    answering_leaf(monkeypatch, fake_processes, "VER\x00DICT: REJ\x00ECT\nthe \x00whole\nreason\x00")
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, capfdbinary.readouterr().out) == (1, b"the whole\nreason\n")


@pytest.mark.parametrize("phase", ["green", "refactor"])
@pytest.mark.parametrize("leaf_out, word, reason_line", [
    (b"VERDICT: PASS\nfirst line\nsecond line\n", "PASS", "first line"),
    (b"VERDICT: REJECT\nwhy it fails\nmore\n", "REJECT", "why it fails"),
    (b"VERDICT: MAYBE\nundecided\n", "malformed", ""),
])
def test_main_appends_one_verdict_record_with_the_verdict_word_and_the_reasons_first_line_under_the_verifier_role(
        phase, leaf_out, word, reason_line, tmp_path, monkeypatch, events, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_ISSUE", "931")
    monkeypatch.setenv("VERI_STEP", "5")
    answering_leaf(monkeypatch, fake_processes, leaf_out)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    verify.main([*BRANCH, "--fast-cmd", "make unit", *(["--step-green", "0123abc"] if phase == "refactor" else []),
                 phase, "spec.md", "tests/x.test.sh", *(["0123abc"] if phase == "refactor" else [])])

    assert events.records() == [
        record("verdict", "verdict=" + word, "reason=" + reason_line, issue="931", step="5", phase=phase)]


@pytest.mark.parametrize("verdict_lines, word, code", [
    ("VERDICT: REJECT\nREASON: the pass is not genuine\n", "REJECT", 1),
    ("VERDICT: PASS\nREASON: the pass is not genuine\n", "PASS", 0),
    ("VERDICT: MAYBE\nREASON: the pass is not genuine\n", "malformed", 2),
])
@pytest.mark.parametrize("check_line, check", [
    ("CHECK: 3\n", ["check=3"]), ("CHECK: 1\n", ["check=1"]), ("CHECK: 5\n", ["check=5"]),
    ("", []), ("CHECK: 0\n", []), ("CHECK: 6\n", []), ("CHECK: three\n", []), ("CHECK: 3 and 4\n", []),
    ("CHECK:\n", []), ("CHECK: 33\n", []),
])
def test_main_puts_a_check_from_1_to_5_on_a_green_verdict_event_and_none_for_an_absent_or_other_value_leaving_the_verdict_and_code_as_without_the_line(
        verdict_lines, word, code, check_line, check, tmp_path, monkeypatch, events, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_ISSUE", "931")
    monkeypatch.setenv("VERI_STEP", "5")
    answering_leaf(monkeypatch, fake_processes, (check_line + verdict_lines).encode())
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    returned = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    reason = "" if word == "malformed" else "the pass is not genuine"
    assert (returned, events.records()) == (code, [
        record("verdict", "verdict=" + word, "reason=" + reason, *check, issue="931", step="5")])


@pytest.mark.parametrize("leaf_out", [
    b"CHECK: 3\nVERDICT: REJECT\nREASON: the pass is not genuine\nsee the diff\n",
    b"VERDICT: REJECT\nCHECK: 3\nREASON: the pass is not genuine\nsee the diff\n",
    b"VERDICT: REJECT\nREASON: the pass is not genuine\n  CHECK: 7\nsee the diff\n",
    b"REASON: the pass is not genuine\nCHECK: 3\nsee the diff\nVERDICT: REJECT\n",
])
def test_main_prints_a_green_reason_holding_no_check_line_wherever_the_verifier_put_it(
        leaf_out, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    answering_leaf(monkeypatch, fake_processes, leaf_out)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    assert (code, capfdbinary.readouterr().out) == (1, b"the pass is not genuine\nsee the diff\n")


def test_main_launches_the_leaf_with_verify_leaf_args_words_split_on_whitespace_and_glob_expanded_in_the_working_directory(
        tmp_path, monkeypatch, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("b.flag", "a.flag", "c.other"):
        (tmp_path / name).write_text("")
    monkeypatch.setenv("VERIFY_LEAF_ARGS", "--one two\t*.flag\n nomatch-*.zz  --three")
    supervised = []
    answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine", supervised=supervised)
    verify = importlib.import_module("veri.verify")
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(verify.__file__)))

    verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
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
        leaf_args, models, expected_code, expected_err, launches, tmp_path, monkeypatch, capfdbinary, fake_processes):
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

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    if launches:
        assert_prompt_rendered()
    else:
        assert list((tmp_path / ".tdd").glob("verify-*.prompt")) == []

    captured = capfdbinary.readouterr()
    assert (code, captured.err.decode("utf-8"), "supervise.sh" in started) == (
        expected_code, expected_err, launches)
    if not launches:
        assert (captured.out, started) == (b"", [])


@pytest.mark.parametrize("effort", ["HIGH", " high", "high\n", "max "])
def test_4013_a_veri_effort_verifier_outside_the_five_levels_exits_2_naming_the_knob_and_the_levels_and_launches_nothing(
        effort, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_EFFORT_VERIFIER", effort)
    supervised = []
    answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine", supervised=supervised)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    err = capfdbinary.readouterr().err.decode("utf-8")
    assert (code, supervised, "VERI_EFFORT_VERIFIER" in err,
            all(level in err for level in ("low", "medium", "high", "xhigh", "max"))) == (2, [], True, True), err


def test_main_lets_a_literal_model_word_in_verify_leaf_args_stand_when_no_model_variable_is_set(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERIFY_LEAF_ARGS", "--model x")
    supervised = []
    answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine", supervised=supervised)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.err, [words[-2:] for words in supervised]) == (0, b"", [["--model", "x"]])


@pytest.mark.parametrize("leaf_args", [None, "--permission-mode bypassPermissions"])
@pytest.mark.parametrize("effort, expected", [(None, []), ("", []), ("high", ["--effort", "high"]),
                                              ("low", ["--effort", "low"])])
def test_4013_a_verifier_leaf_carries_effort_and_veri_effort_verifiers_value_only_when_it_is_set_and_not_empty(
        effort, expected, leaf_args, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    if effort is not None:
        monkeypatch.setenv("VERI_EFFORT_VERIFIER", effort)
    if leaf_args is not None:
        monkeypatch.setenv("VERIFY_LEAF_ARGS", leaf_args)
    supervised = []
    answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine", supervised=supervised)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    efforts = [words[words.index("--effort"):words.index("--effort") + 2] if "--effort" in words else []
               for words in supervised]
    assert (code, supervised[0][1], efforts) == (0, "verify-green", [expected])


@pytest.mark.parametrize("effort, leaf_args, refused", [
    ("high", "--permission-mode bypassPermissions --effort low", True),
    ("high", "--effort", True),
    ("high", "--permission-mode bypassPermissions --effort=low", True),
    ("", "--effort=low", False),
    ("", "--effort low", False),
    (None, "--effort low", False),
    ("high", "--permission-mode bypassPermissions", False),
])
def test_4013_verify_leaf_args_carrying_effort_beside_a_set_veri_effort_verifier_exits_2_naming_both_and_launches_nothing(
        effort, leaf_args, refused, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    if effort is not None:
        monkeypatch.setenv("VERI_EFFORT_VERIFIER", effort)
    monkeypatch.setenv("VERIFY_LEAF_ARGS", leaf_args)
    supervised = []
    answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine", supervised=supervised)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    err = capfdbinary.readouterr().err.decode("utf-8")
    if refused:
        assert (code, len(err.splitlines()), "VERIFY_LEAF_ARGS" in err, "--effort" in err,
                "VERI_EFFORT_VERIFIER" in err, supervised) == (2, 1, True, True, True, [])
    else:
        assert (code, err, len(supervised)) == (0, "", 1)


def test_main_still_refuses_a_literal_model_word_in_verify_leaf_args_when_veri_model_verifier_is_also_set(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_MODEL_VERIFIER", "opus")
    monkeypatch.setenv("VERIFY_LEAF_ARGS", "--model x")
    started = []

    def fake(args, *_, **__):
        started.append(os.path.basename(str(args[0])))
        return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine", b"")

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "green", "spec.md", "tests/x.test.sh"])

    captured = capfdbinary.readouterr()
    assert (code, captured.err.decode("utf-8"), captured.out, started) == (2, CLASH % "opus", b"", [])


@pytest.mark.parametrize("supervise, expected", [
    (2, (2, "verifier leaf killed-stuck — no verdict rendered (see .tdd/verify-green.log)\n")),
    (FileNotFoundError, (2, "\n")),
])
def test_main_returns_2_on_a_killed_stuck_leaf_with_no_tamper_check_event_or_preservation_and_reads_an_unstartable_supervise_as_no_answer(
        supervise, expected, tmp_path, monkeypatch, capfdbinary, events, fake_processes):
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

    through_fixture(fake_processes, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
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
        tmp_path, monkeypatch, capfdbinary, events, fake_processes):
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

    through_fixture(fake_processes, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

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
        capfdbinary, events, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    if retries is not None:
        monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", retries)
    supervised = answering_leaf(monkeypatch, fake_processes, *leaf_outs)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, len(supervised), events.records(), capfdbinary.readouterr().err) == (
        expected_code, launches, [record(*mark) for mark in marks], expected_err)


def test_main_returns_2_when_the_relaunch_record_cannot_be_appended_and_makes_no_relaunch(
        tmp_path, monkeypatch, capfdbinary, events, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    events.unappendable()
    supervised = answering_leaf(monkeypatch, fake_processes, NO_VERDICT, b"VERDICT: PASS\nfine\n")
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, len(supervised), capfdbinary.readouterr().out) == (2, 1, b"")


def test_main_returns_2_when_the_verdict_record_cannot_be_appended_with_no_preservation_and_nothing_on_stdout(
        tmp_path, monkeypatch, capfdbinary, events, fake_processes):
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

    through_fixture(fake_processes, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, preserved, capfdbinary.readouterr().out) == (2, [], b"")


@pytest.mark.parametrize("retries, launches", [("", 2), ("010", 11), ("09", 10), ("08", 9)])
def test_main_reads_an_empty_no_verdict_budget_as_1_and_a_leading_zero_as_decimal_so_010_allows_10_relaunches_and_09_allows_9(
        retries, launches, tmp_path, monkeypatch, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", retries)
    supervised = answering_leaf(monkeypatch, fake_processes, NO_VERDICT)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, len(supervised)) == (2, launches)


def test_main_copies_parse_verdicts_stderr_to_its_own_stderr_after_every_launch_relaunched_ones_included(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
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

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    assert (code, capfdbinary.readouterr().err) == (
        2, b"launch 1\n" + NO_LINE + b"launch 2\n" + NO_LINE
        + b"launch 3\nparse-verdict: unrecognised verdict word 'MAYBE'\n")


@pytest.mark.parametrize("retries", ["x", "-1", " 1"])
def test_main_refuses_a_no_verdict_budget_that_is_not_a_non_negative_integer_after_the_prompt_file_is_written_and_launches_no_leaf(
        retries, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", retries)
    launched = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine\n")
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
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
        tmp_path, monkeypatch, capfdbinary, events, fake_processes):
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
                return subprocess.CompletedProcess(args, 0, b"src.txt\0new.txt\0", b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        order.append(name)
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: REJECT\nbad\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
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
    assert diffed == [["-r", "-z", "--name-only", "--no-commit-id", "a" * 40, "b" * 40]]
    snapshots = indexes[:4]
    assert all(index and not pathlib.Path(index).is_relative_to(tmp_path) for _, index in snapshots)
    assert (snapshots[0][1] == snapshots[1][1], snapshots[2][1] == snapshots[3][1]) == (True, True)
    assert ([r for r in updated if r.startswith("refs/veri/attempts/")], events.records()) == ([], [])


@pytest.mark.parametrize("failing", ["add", "git-missing", "write-tree", "diff-tree"])
def test_main_takes_a_git_call_that_fails_as_no_snapshot_or_no_change_whatever_it_printed_and_returns_the_verdict(
        failing, tmp_path, monkeypatch, capfdbinary, fake_processes):
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

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    no_snapshot = failing in ("add", "git-missing", "write-tree")
    assert (code, captured.out, "diff-tree" in verbs, "write-tree" in verbs) == (
        0, b"fine\n", not no_snapshot, failing in ("write-tree", "diff-tree"))


@pytest.mark.parametrize("head_moved", [True, False])
def test_main_restores_a_modified_tree_through_a_fresh_temporary_index_and_a_moved_head_with_update_ref(
        head_moved, tmp_path, monkeypatch, capfdbinary, fake_processes):
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
                return subprocess.CompletedProcess(args, 0, b"src.txt\0", b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
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
        tmp_path, monkeypatch, capfdbinary, events, fake_processes):
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
                out = b"src.txt\0" if words[-2] != words[-1] else b""
                return subprocess.CompletedProcess(args, 0, out, b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            supervised.append(words)
            return subprocess.CompletedProcess(args, 0, leaf_outs[len(supervised) - 1], None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, len(supervised), captured.out, events.records()) == (
        2, 2, "verifier leaf modified the repository — verdict not accepted"
              " (see .tdd/verify-green.log); changed:\nsrc.txt\n".encode(),
        [record("relaunch", "cause=no-verdict")])


@pytest.mark.parametrize("where", ["not-a-repository", "git-missing", "add-fails"])
def test_main_outside_a_repository_without_git_or_with_a_failing_add_takes_no_snapshot_runs_no_tamper_check_or_preservation_and_returns_the_verdict(
        where, tmp_path, monkeypatch, capfdbinary, events, fake_processes):
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
                return subprocess.CompletedProcess(args, 0, b"src.txt\0", b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        started.append(words)
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: REJECT\nbad\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    names = [os.path.basename(words[0]) for words in started]
    assert (code, captured.out) == (1, b"bad\n")
    assert [v for v in verbs if v in ("write-tree", "diff-tree", "read-tree", "update-ref")] == []
    assert events.records() == [record("verdict", "verdict=REJECT", "reason=bad", issue="7", step="2")]


def test_4221_main_names_on_the_verdict_event_the_tree_the_guard_took_before_the_leaf_it_judged(
        tmp_path, monkeypatch, events, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VERI_ISSUE", "7")
    monkeypatch.setenv("VERI_STEP", "2")

    def fake(args, *_, **__):
        words = [w for w in (str(a) for a in args) if os.path.basename(w) != "env" and "=" not in w]
        name = os.path.basename(words[0])
        if name == "git" and words[1] == "write-tree":
            return subprocess.CompletedProcess(args, 0, b"c" * 40 + b"\n", b"")
        if name == "git" and words[1] == "rev-parse":
            return subprocess.CompletedProcess(args, 0, b"1" * 40 + b"\n", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])

    assert (code, events.records()) == (
        0, [record("verdict", "verdict=PASS", "reason=fine", "tree=" + "c" * 40, issue="7", step="2")])


def test_main_in_a_repository_with_no_commit_reports_a_leaf_that_commits_as_head_and_makes_no_update_ref_call(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
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

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.out, updated) == (
        2, "verifier leaf modified the repository — verdict not accepted"
           " (see .tdd/verify-green.log); changed:\nHEAD\n".encode(), [])


def test_main_returns_2_with_no_traceback_when_the_update_ref_restoring_head_fails_1183(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
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
                return subprocess.CompletedProcess(args, 0, b"src.txt\0", b"")
            if verb == "update-ref":
                return subprocess.CompletedProcess(args, 128, None, None)
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert ("update-ref" in verbs, code, b"Traceback" in captured.err) == (True, 2, False)


def test_main_returns_2_not_1_when_the_update_ref_restoring_head_exits_1_1183(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
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
                return subprocess.CompletedProcess(args, 0, b"src.txt\0", b"")
            if verb == "update-ref":
                return subprocess.CompletedProcess(args, 1, None, None)
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert ("update-ref" in verbs, code) == (True, 2)


def test_main_returns_2_with_no_traceback_when_git_cannot_be_started_to_restore_head_1183(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
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
                return subprocess.CompletedProcess(args, 0, b"src.txt\0", b"")
            if verb == "update-ref":
                raise FileNotFoundError(2, "No such file or directory", "git")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    raised = None
    try:
        code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    except OSError as error:
        code, raised = None, type(error).__name__

    captured = capfdbinary.readouterr()
    assert ("update-ref" in verbs, code, raised, b"Traceback" in captured.err) == (True, 2, None, False)


@pytest.mark.parametrize("before, after", [(b"[user]\n\tname = op\n", b"[user]\n\tname = leaf\n"),
                                           (None, b"[user]\n\tname = leaf\n"),
                                           (b"[user]\n\tname = op\n", None)])
def test_main_returns_2_naming_home_gitconfig_when_the_leaf_changed_created_or_deleted_it_and_restores_nothing(
        before, after, tmp_path, monkeypatch, capfdbinary, events, fake_processes):
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

    through_fixture(fake_processes, fake)
    events.refuse_event_sh()
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    left = gitconfig.read_bytes() if gitconfig.exists() else None
    assert (code, captured.out) == (
        2, ("verifier leaf modified the operator's global git config — verdict not accepted"
            " (see .tdd/verify-green.log); changed:\n%s\n" % os.path.join(str(home), ".gitconfig")).encode())
    assert (left, events.records(), any(" update-ref refs/veri/attempts/" in w for w in started)) == (after, [], False)


def test_main_reports_a_leaf_that_changed_both_the_repository_and_home_gitconfig_for_the_repository_only(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
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
                return subprocess.CompletedProcess(args, 0, b"src.txt\0", b"")
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if name == "supervise.sh":
            gitconfig.write_bytes(b"[user]\n\tname = leaf\n")
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine\n", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.out) == (
        2, "verifier leaf modified the repository — verdict not accepted"
           " (see .tdd/verify-green.log); changed:\nsrc.txt\n".encode())


def test_main_returns_2_before_any_leaf_launches_when_reading_home_gitconfig_a_regular_file_raises_oserror_1183(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    gitconfig = home / ".gitconfig"
    gitconfig.write_bytes(b"[user]\n\tname = op\n")
    launched = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine\n")
    real_open = open

    def unreadable(path, *args, **kwargs):
        if os.fspath(path) == str(gitconfig):
            raise PermissionError(13, "Permission denied", os.fspath(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", unreadable)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, captured.out, launched) == (2, b"", [])


def test_main_returning_2_because_reading_home_gitconfig_raised_oserror_names_that_path_on_stderr_1183(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    gitconfig = home / ".gitconfig"
    gitconfig.write_bytes(b"[user]\n\tname = op\n")
    answering_leaf(monkeypatch, fake_processes, b"")
    real_open = open

    def unreadable(path, *args, **kwargs):
        if os.fspath(path) == str(gitconfig):
            raise PermissionError(13, "Permission denied", os.fspath(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", unreadable)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, str(gitconfig).encode() in captured.err) == (2, True)


def test_main_returns_2_naming_home_gitconfig_on_stderr_without_launching_a_leaf_when_it_is_a_directory_1183(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    write_inputs(work)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    gitconfig = home / ".gitconfig"
    gitconfig.mkdir()
    launched = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nfine\n")
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, str(gitconfig).encode() in captured.err, b"Traceback" in captured.err,
            launched) == (2, True, False, [])


def test_main_returns_2_naming_home_gitconfig_on_stderr_when_the_leaf_left_it_a_directory_1183(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
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

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
    assert_prompt_rendered()

    captured = capfdbinary.readouterr()
    assert (code, str(gitconfig).encode() in captured.err, b"Traceback" in captured.err) == (2, True, False)


def test_main_returns_2_naming_home_gitconfig_on_stderr_when_the_leaf_left_it_unreadable_1183(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
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

    through_fixture(fake_processes, fake)
    real_open = open

    def unreadable_after_the_leaf(path, *args, **kwargs):
        if leaf_ran and os.fspath(path) == str(gitconfig):
            raise PermissionError(13, "Permission denied", os.fspath(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", unreadable_after_the_leaf)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
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
        capfdbinary, fake_processes):
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

    through_fixture(fake_processes, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
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
        tmp_path, monkeypatch, fake_processes):
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

    through_fixture(fake_processes, fake)
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
                status = verify.main([*BRANCH, "--fast-cmd", "make unit", "green", "spec.md", "tests/x.test.sh"])
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


def build_prompt(words, monkeypatch):
    built, captured = io.BytesIO(), sys.stdout
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(built, write_through=True))
    pinned = (["--branch-base", FAKE_BASE] if ("pin" in words or "surround" in words) and "--branch-base" not in words
              else [])
    code = importlib.import_module("veri.build_verify_prompt").main([*pinned, *words])
    monkeypatch.setattr(sys, "stdout", captured)
    return code, built.getvalue()


FAKE_BASE = "3f9a1c0d5e7b4a2896fd01c3b5e7a9d2c4f60812"


SPEC = "slugify must lowercase the title and join words with hyphens."


def answering_leaf(monkeypatch, fake_processes, *leaf_outs, supervised=None):
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
        if name == "git" and "merge-base" in words:
            return subprocess.CompletedProcess(args, 0, (FAKE_BASE + "\n").encode(), None)
        return subprocess.CompletedProcess(args, 128 if name == "git" else 0, b"", None)

    through_fixture(fake_processes, fake)
    return launches


FAST = ["--fast-cmd", "make unit"]


WAITING = "Waiting for the background `make test` run to complete before rendering a verdict."


GREEN_REASON = "Target test and full suite are green."


GREEN = "VERDICT: PASS\nREASON: " + GREEN_REASON


FLAG_STEP = "FLAG-STEP slugify joins words with hyphens"


AMBIENT_STEP = "AMBIENT-STEP-must-not-appear"


@pytest.mark.parametrize("flags, phase, fourth, leaf_out, expected_code, launches, present, absent", [
    pytest.param(FAST, "green", "test_lowercases", WAITING, 2, 2, [SPEC], [], id="relaunch-byte-identical"),
    pytest.param([*FAST, "--step-green", "0123abc"], "refactor", "0123abc", GREEN, 0, 1, ["git diff 0123abc..HEAD"], [], id="refactor-base-sha"),
    pytest.param(["--step", FLAG_STEP, *FAST], "green", "test_lowercases", GREEN, 0, 1, [FLAG_STEP],
                 [AMBIENT_STEP], id="step-flag-not-ambient"),
    *[pytest.param([*(FAST if phase in ("green", "refactor") else []),
                    *(["--step-green", "0123abc"] if phase == "refactor" else [])], phase,
                   "0123abc" if phase == "refactor" else "test_lowercases", GREEN, 0, 1, [SPEC, "VERDICT:"], [],
                   id="no-step-" + phase) for phase in ("red", "green", "refactor", "pin", "surround")],
])
def test_verify_sh_hands_every_launch_the_builders_own_prompt_for_its_arguments_carrying_base_sha_and_step_flag_not_ambient_veri_step_with_no_unfilled_placeholder(
        flags, phase, fourth, leaf_out, expected_code, launches, present, absent, run_cli, tmp_path, monkeypatch, fake_processes):
    monkeypatch.setenv("VERI_STEP", AMBIENT_STEP)
    (tmp_path / "spec.md").write_text(SPEC)
    argv = [*BRANCH, *flags, phase, str(tmp_path / "spec.md"), "tests/test_slugify.py", fourth]
    launched = answering_leaf(monkeypatch, fake_processes, leaf_out)
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, argv, env={"HOME": str(tmp_path)}, cwd=tmp_path)

    expected = build_prompt(argv, monkeypatch)[1].decode().rstrip("\n")
    assert (code, [prompt for _, prompt in launched]) == (expected_code, [expected] * launches)
    assert [text for text in present if text not in expected] == []
    assert [text for text in absent if text in expected] == []
    assert re.findall(r"\{\{[A-Z_]*\}\}", expected) == []


def test_3104_verify_sh_hands_supersede_base_to_the_diff_prompt_so_the_leaf_judges_only_git_diff_of_that_sha(
        run_cli, tmp_path, monkeypatch, fake_processes):
    (tmp_path / "spec.md").write_text(SPEC)
    sha = "abcdef1234567"
    argv = ["--step", FLAG_STEP, "--fast-cmd", "make unit", "--supersede-base", sha,
            "--branch-base", "0123abc", "diff", str(tmp_path / "spec.md"), "0123abd"]
    launched = answering_leaf(monkeypatch, fake_processes, GREEN)
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, argv, env={"HOME": str(tmp_path)}, cwd=tmp_path)

    prompts = [" ".join(prompt.split()) for _, prompt in launched]
    assert code == 0
    assert len(prompts) == 1
    assert f"git diff {sha}" in prompts[0]


def test_verify_sh_hands_frozen_edit_to_the_diff_prompt_so_the_leaf_judges_the_snapshot_pair_4730(
        run_cli, tmp_path, monkeypatch, fake_processes):
    (tmp_path / "spec.md").write_text(SPEC)
    sha = "abcdef1234567"
    argv = ["--step", FLAG_STEP, "--fast-cmd", "make unit", "--frozen-edit", sha,
            "--branch-base", "0123abc", "diff", str(tmp_path / "spec.md"), "0123abd"]
    launched = answering_leaf(monkeypatch, fake_processes, GREEN)
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, argv, env={"HOME": str(tmp_path)}, cwd=tmp_path)

    prompts = [" ".join(prompt.split()) for _, prompt in launched]
    assert (code, [name for name, _ in launched]) == (0, ["verify-diff"])
    assert f"git diff {sha}~1 {sha}" in prompts[0]
    assert "when verify-red judged it" in prompts[0]


def test_4544_verify_sh_hands_step_green_to_the_refactor_prompt_as_the_steps_green_commit_not_the_base_sha(
        run_cli, tmp_path, monkeypatch, fake_processes):
    (tmp_path / "spec.md").write_text(SPEC)
    green = "abcdef1234567"
    argv = [*BRANCH, *FAST, "--step-green", green, "refactor", str(tmp_path / "spec.md"), "tests/test_slugify.py",
            "0123abc"]
    launched = answering_leaf(monkeypatch, fake_processes, GREEN)
    verify = importlib.import_module("veri.verify")

    code, _, _ = run_cli(verify, argv, env={"HOME": str(tmp_path)}, cwd=tmp_path)

    prompts = [" ".join(prompt.split()) for _, prompt in launched]
    assert (code, len(prompts)) == (0, 1)
    assert f"the step's green commit is `{green}`" in prompts[0]


def test_3104_verify_sh_names_the_leaf_verify_diff_when_supersede_base_precedes_the_diff_phase(
        run_cli, tmp_path, monkeypatch, fake_processes):
    (tmp_path / "spec.md").write_text(SPEC)
    argv = ["--step", FLAG_STEP, "--fast-cmd", "make unit", "--supersede-base", "abcdef1234567", "--branch-base", "0123abc", "diff", str(tmp_path / "spec.md"), "0123abd"]
    launched = answering_leaf(monkeypatch, fake_processes, GREEN)
    verify = importlib.import_module("veri.verify")

    run_cli(verify, argv, env={"HOME": str(tmp_path)}, cwd=tmp_path)

    assert [name for name, _ in launched] == ["verify-diff"]


DIFF_STEP = "DIFF-STEP the old cases are gone"


DIFF = ["--step", DIFF_STEP, *FAST, "--branch-base", "0123abc", "diff", "{spec}", "0123abc"]


REBASE = [*BRANCH, "rebase", "{spec}", "0123abc", "4567def"]


NO_STEP = "build-verify-prompt: diff needs --step '<STEP>'"


NON_HEX = "build-verify-prompt: diff needs <step-base-sha> as 7-40 lowercase hex characters, got 'not-a-sha'"


TOO_MANY = "build-verify-prompt: too many arguments"


STEP_VALUE = "verify: --step needs a value"


DIFF_NO_BASE = ["--step", DIFF_STEP, *FAST, "diff", "{spec}", "0123abc"]


@pytest.mark.parametrize("entry", ["verify", "run_verdict"])
@pytest.mark.parametrize("argv, named", [
    pytest.param(DIFF_NO_BASE, "--branch-base", id="missing"),
    pytest.param(["--branch-base", "", *DIFF_NO_BASE], "--branch-base", id="empty"),
    *[pytest.param(["--branch-base", value, *DIFF_NO_BASE], "--branch-base", id="not-hex-" + label)
      for label, value in (("HEAD", "HEAD"), ("short", "abc"), ("uppercase", "0123ABC"))],
    pytest.param([*DIFF, "4567def"], "<spec-file> <step-base-sha>", id="third-positional"),
])
def test_4376_the_diff_verifier_with_branch_base_missing_or_malformed_or_a_third_positional_exits_2_naming_it_before_any_prompt_or_leaf(
        entry, argv, named, run_cli, tmp_path, monkeypatch, fake_processes):
    (tmp_path / "spec.md").write_text(SPEC)
    argv = [word.format(spec=tmp_path / "spec.md") for word in argv]
    verify = importlib.import_module("veri.verify")
    launches = answering_leaf(monkeypatch, fake_processes, GREEN)

    def exec_verify(path, words):
        raise SystemExit(verify.main(list(words[1:])))

    monkeypatch.setattr(os, "execv", exec_verify)
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    code, _, err = run_cli(importlib.import_module("veri." + entry), argv, env={"HOME": str(tmp_path)}, cwd=tmp_path)

    first = err.splitlines()[0] if err else ""
    assert (code, named in first, launches, sorted((tmp_path / ".tdd").glob("*.prompt"))) == (2, True, [], []), err


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
          ("no-step", [*FAST, "--branch-base", "0123abc", "diff", "{spec}", "0123abc"], NO_STEP),
          ("non-hex", ["--step", DIFF_STEP, *FAST, "--branch-base", "0123abc", "diff", "{spec}", "not-a-sha"], NON_HEX),
          ("extra", [*DIFF, "extra", "extra"], TOO_MANY))],
    pytest.param("verify", ["--step", "", *BRANCH, "red", "{spec}", "tests/test_slugify.py", "test_lowercases"], GREEN,
                 (2, STEP_VALUE, [], []), id="empty-step"),
    pytest.param("verify", ["--step"], GREEN, (2, STEP_VALUE, [], []), id="trailing-step"),
])
def test_verify_sh_and_run_verdict_sh_answer_a_rebase_or_diff_verdict_from_one_leaf_named_for_the_phase_and_refuse_a_bad_step_sha_or_extra_argument_with_exit_2_the_named_checks_message_first_and_no_leaf(
        entry, argv, leaf_out, expected, run_cli, tmp_path, monkeypatch, fake_processes):
    (tmp_path / "spec.md").write_text(SPEC)
    argv = [word.format(spec=tmp_path / "spec.md") for word in argv]
    verify = importlib.import_module("veri.verify")
    launches = answering_leaf(monkeypatch, fake_processes, leaf_out)

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


def test_4472_the_argv_verify_branch_launches_run_verdict_with_passes_verifys_argument_parsing_and_reaches_the_leaf(
        tmp_path, monkeypatch, run_cli, fake_processes):
    """verify_branch.launch hands run-verdict.sh, which passes argv to verify.sh unexamined, `branch <spec>` with no
    <test-path>; run #4698 bailed when verify.main refused that arity with its usage line, exit 2."""
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    base = "abc1234def5678"
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("the behavior spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(base + "\n")
    launched = []

    def launch(where, wt_, name, command, *args, env, out, err, clear=()):
        launched.append((command, list(args)))

    monkeypatch.setattr(fused, "launch", launch)
    monkeypatch.setattr(fused, "call", lambda *a, **kw: (0, "", ""))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert [command for command, _ in launched] == ["run-verdict.sh"]

    (tmp_path / ".git").rmdir()  # no git tree around the verifier, so the builder reads nothing at the fake base
    monkeypatch.chdir(wt)
    leaves = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\nthe branch holds")
    verify = importlib.import_module("veri.verify")
    code = verify.main(launched[0][1])

    assert (code, [name for name, _ in leaves]) == (0, ["verify-branch"])
    assert "the behavior spec" in leaves[0][1]
