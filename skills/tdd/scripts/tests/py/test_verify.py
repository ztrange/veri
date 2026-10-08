"""In-process cases for veri/verify.py, the module verify.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = (b"usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file>"
         b" <test-path> [<target-test-id>]")


def fake_processes(monkeypatch):
    """Every process entry point recording each command it is asked to start."""
    calls = []

    def record(args, *_, **__):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, record)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, record)
    return calls


@pytest.mark.parametrize("argv", [[], ["green", "spec"], ["--step", "x", "green"]])
def test_main_with_fewer_than_three_positionals_returns_2_with_the_usage_line_alone_and_starts_no_process(
        argv, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(monkeypatch)
    verify = importlib.import_module("veri.verify")

    code = verify.main(list(argv))

    captured = capfdbinary.readouterr()
    assert len(USAGE) == 112
    assert (code, captured.out, captured.err, calls) == (2, b"", USAGE + b"\n", [])


@pytest.mark.parametrize("argv, flag", [(["--step"], b"--step"), (["--step", ""], b"--step"),
                                        (["--fast-cmd", "", "green", "s", "t"], b"--fast-cmd")])
def test_main_with_a_flag_missing_its_value_returns_2_naming_the_flag_then_the_usage_line_and_starts_no_process(
        argv, flag, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(monkeypatch)
    verify = importlib.import_module("veri.verify")

    code = verify.main(list(argv))

    captured = capfdbinary.readouterr()
    assert (code, captured.out, captured.err, calls) == (
        2, b"", b"verify: " + flag + b" needs a value\n" + USAGE + b"\n", [])


@pytest.mark.parametrize("builder, expected", [(1, 1), (5, 2), (FileNotFoundError, 2)])
def test_main_returns_the_builders_refusal_mapped_into_the_contract_with_its_stderr_and_launches_no_leaf(
        builder, expected, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    launched = []
    builder_err = b"build-verify-prompt: unknown phase 'bogus'\n"

    def fake(args, *_, **kwargs):
        name = os.path.basename(str(args[0]))
        launched.append(name)
        if name != "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if builder is FileNotFoundError:
            raise FileNotFoundError(2, "No such file or directory", str(args[0]))
        if kwargs.get("stderr") is None:
            os.write(2, builder_err)
            return subprocess.CompletedProcess(args, builder, b"", None)
        return subprocess.CompletedProcess(args, builder, b"", builder_err)

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["bogus", "spec.md", "tests/x.test.sh"])

    captured = capfdbinary.readouterr()
    passed_through = builder is FileNotFoundError or builder_err in captured.err
    assert (code, captured.out, passed_through, "build-verify-prompt.sh" in launched,
            "supervise.sh" in launched) == (expected, b"", True, True, False)


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
    monkeypatch.setenv("VERI_STEP", "AMBIENT-STEP-SENTINEL")
    outputs = [b"an earlier, longer prompt that must not survive\n", b"blind\nprompt\n\n\n"]
    built = []

    def fake(args, *_, **__):
        name = os.path.basename(str(args[0]))
        if name == "build-verify-prompt.sh":
            built.append([str(a) for a in args])
            return subprocess.CompletedProcess(args, 0, outputs[len(built) - 1], b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine", b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    before = set(sys.modules)
    try:
        verify = importlib.import_module("veri.verify")
        argv = ["--step", "--fast-cmd", "--fast-cmd", "make unit",
                "green", "spec.md", "tests/x.test.sh", "--step", "extra"]
        verify.main(list(argv))
        prompt_file = work / ".tdd" / "verify-green.prompt"
        first = prompt_file.read_bytes() if prompt_file.exists() else None
        verify.main(list(argv))
    finally:
        for name in set(sys.modules) - before:
            del sys.modules[name]

    expected = [str(link / "build-verify-prompt.sh"), *argv]
    assert built == [expected, expected]
    assert not any("AMBIENT-STEP-SENTINEL" in word for word in built[0])
    prompt = prompt_file.read_bytes() if prompt_file.exists() else None
    assert (first, prompt) == (b"an earlier, longer prompt that must not survive", b"blind\nprompt")
    assert b"AMBIENT-STEP-SENTINEL" not in prompt


@pytest.mark.parametrize("leaf_args", [None, ""])
def test_main_launches_the_verifier_leaf_through_supervise_with_the_default_flags_streams_inherited_and_starts_no_ported_helper_process(
        leaf_args, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    if leaf_args is None:
        monkeypatch.delenv("VERIFY_LEAF_ARGS", raising=False)
    else:
        monkeypatch.setenv("VERIFY_LEAF_ARGS", leaf_args)
    started = []

    def fake(args, *_, **kwargs):
        words = [str(a) for a in (args if isinstance(args, (list, tuple)) else [args])]
        started.append((words, kwargs.get("stdin"), kwargs.get("stderr")))
        name = os.path.basename(words[0])
        if name == "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"blind prompt", b"")
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

    verify.main(["green", "spec.md", "tests/x.test.sh"])

    supervised = [call for call in started if os.path.basename(call[0][0]) == "supervise.sh"]
    assert supervised == [([os.path.join(scripts, "supervise.sh"), "verify-green",
                            os.path.join(scripts, "run-leaf.sh"), ".tdd/verify-green.prompt",
                            "--permission-mode", "bypassPermissions",
                            "--disallowedTools", "Write", "Edit", "MultiEdit", "NotebookEdit"],
                           None, None)]
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
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("VERIFY_LEAF_ARGS", "VERI_ISSUE", "VERI_STEP", "VERI_NO_VERDICT_RETRIES"):
        monkeypatch.delenv(name, raising=False)

    def fake(args, *_, **__):
        name = os.path.basename(str(args[0]))
        if name == "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"blind prompt", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, leaf_out, None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main([phase, "spec.md", "tests/x.test.sh"])

    assert (code, capfdbinary.readouterr().out) == expected


@pytest.mark.parametrize("phase", ["green", "refactor"])
@pytest.mark.parametrize("leaf_out, word, reason_line", [
    (b"VERDICT: PASS\nfirst line\nsecond line\n", "PASS", "first line"),
    (b"VERDICT: REJECT\nwhy it fails\nmore\n", "REJECT", "why it fails"),
    (b"VERDICT: MAYBE\nundecided\n", "malformed", ""),
])
def test_main_calls_event_sh_once_with_the_verdict_word_and_the_reasons_first_line_under_the_verifier_role(
        phase, leaf_out, word, reason_line, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("VERIFY_LEAF_ARGS", "VERI_NO_VERDICT_RETRIES",
                 "VERI_ACTOR", "VERI_PHASE", "VERI_ATTEMPT"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("VERI_ISSUE", "931")
    monkeypatch.setenv("VERI_STEP", "5")
    monkeypatch.setenv("VERI_INHERITED_SENTINEL", "kept")
    events = []

    def fake(args, *_, **kwargs):
        words = [str(a) for a in args]
        env = dict(os.environ if kwargs.get("env") is None else kwargs["env"])
        if os.path.basename(words[0]) == "env":
            words = words[1:]
            while words and "=" in words[0]:
                key, _, value = words.pop(0).partition("=")
                env[key] = value
        name = os.path.basename(words[0])
        if name == "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"blind prompt", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, leaf_out, None)
        if name == "event.sh":
            events.append((words, env))
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(verify.__file__)))
    expected_env = {**os.environ, "VERI_ACTOR": "verifier", "VERI_PHASE": phase, "VERI_ATTEMPT": "1"}

    verify.main([phase, "spec.md", "tests/x.test.sh"])

    assert [words for words, _ in events] == [
        [os.path.join(scripts, "event.sh"), "verdict", "verdict=" + word, "reason=" + reason_line]]
    assert events[0][1] == expected_env


def test_main_launches_the_leaf_with_verify_leaf_args_words_split_on_whitespace_and_glob_expanded_in_the_working_directory(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("VERI_MODEL", "VERI_MODEL_VERIFIER", "VERI_MODEL_DEVELOPER",
                 "VERI_ISSUE", "VERI_STEP", "VERI_NO_VERDICT_RETRIES"):
        monkeypatch.delenv(name, raising=False)
    for name in ("b.flag", "a.flag", "c.other"):
        (tmp_path / name).write_text("")
    monkeypatch.setenv("VERIFY_LEAF_ARGS", "--one two\t*.flag\n nomatch-*.zz  --three")
    supervised = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        name = os.path.basename(words[0])
        if name == "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"blind prompt", b"")
        if name == "supervise.sh":
            supervised.append(words)
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(verify.__file__)))

    verify.main(["green", "spec.md", "tests/x.test.sh"])

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
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("VERI_MODEL", "VERI_MODEL_VERIFIER", "VERI_MODEL_DEVELOPER",
                 "VERI_ISSUE", "VERI_STEP", "VERI_NO_VERDICT_RETRIES"):
        monkeypatch.delenv(name, raising=False)
    for name, value in models.items():
        monkeypatch.setenv(name, value)
    if leaf_args is None:
        monkeypatch.delenv("VERIFY_LEAF_ARGS", raising=False)
    else:
        monkeypatch.setenv("VERIFY_LEAF_ARGS", leaf_args)
    started = []

    def fake(args, *_, **__):
        name = os.path.basename(str(args[0]))
        started.append(name)
        if name == "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"blind prompt", b"")
        if name == "supervise.sh":
            return subprocess.CompletedProcess(args, 0, b"VERDICT: PASS\nfine", None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["green", "spec.md", "tests/x.test.sh"])

    captured = capfdbinary.readouterr()
    assert (code, captured.err.decode("utf-8"), "supervise.sh" in started) == (
        expected_code, expected_err, launches)
    if not launches:
        assert (captured.out, started) == (b"", [])


@pytest.mark.parametrize("supervise, expected", [
    (2, (2, "verifier leaf killed-stuck — no verdict rendered (see .tdd/verify-green.log)\n")),
    (FileNotFoundError, (2, "\n")),
])
def test_main_returns_2_on_a_killed_stuck_leaf_with_no_tamper_check_event_or_preservation_and_reads_an_unstartable_supervise_as_no_answer(
        supervise, expected, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("VERIFY_LEAF_ARGS", "VERI_MODEL", "VERI_MODEL_VERIFIER"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("VERI_ISSUE", "931")
    monkeypatch.setenv("VERI_STEP", "7")
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    started = []

    def fake(args, *_, **__):
        words = [str(a) for a in (args if isinstance(args, (list, tuple)) else [args])]
        started.append(words)
        name = os.path.basename(words[0])
        if name == "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"blind prompt", b"")
        if name == "supervise.sh":
            if supervise is FileNotFoundError:
                raise FileNotFoundError(2, "No such file or directory", words[0])
            return subprocess.CompletedProcess(args, supervise, b"VERDICT: PASS\nfine\n", None)
        if name == "git" and "write-tree" in words:
            return subprocess.CompletedProcess(args, 0, b"0123456789abcdef0123456789abcdef01234567\n", b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["green", "spec.md", "tests/x.test.sh"])

    captured = capfdbinary.readouterr()
    assert (code, captured.out.decode("utf-8")) == expected
    if supervise == 2:
        launch = [os.path.basename(words[0]) for words in started].index("supervise.sh")
        assert [words for words in started[launch + 1:]
                if {os.path.basename(w) for w in words} & {"git", "event.sh", "preserve-attempt.sh"}] == []


NO_VERDICT = b"I looked around and have no opinion\n"
NO_LINE = b"parse-verdict: no VERDICT: line found\n"


@pytest.mark.parametrize("retries, leaf_outs, launches, events, expected_code, expected_err", [
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
        retries, leaf_outs, launches, events, expected_code, expected_err, tmp_path, monkeypatch,
        capfdbinary):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("VERIFY_LEAF_ARGS", "VERI_ISSUE", "VERI_STEP", "VERI_MODEL", "VERI_MODEL_VERIFIER"):
        monkeypatch.delenv(name, raising=False)
    if retries is None:
        monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    else:
        monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", retries)
    supervised = []
    marked = []

    def fake(args, *_, **__):
        words = [str(a) for a in args]
        if os.path.basename(words[0]) == "env":
            words = words[1:]
            while words and "=" in words[0]:
                words.pop(0)
        name = os.path.basename(words[0])
        if name == "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"blind prompt", b"")
        if name == "supervise.sh":
            supervised.append(words)
            out = leaf_outs[min(len(supervised), len(leaf_outs)) - 1]
            return subprocess.CompletedProcess(args, 0, out, None)
        if name == "event.sh":
            marked.append(words[1:])
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["green", "spec.md", "tests/x.test.sh"])

    assert (code, len(supervised), marked, capfdbinary.readouterr().err) == (
        expected_code, launches, events, expected_err)


@pytest.mark.parametrize("retries, launches", [("", 2), ("010", 9), ("08", 1)])
def test_main_reads_an_empty_no_verdict_budget_as_1_and_a_leading_zero_as_octal_so_010_allows_8_relaunches_and_08_none(
        retries, launches, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("VERIFY_LEAF_ARGS", "VERI_ISSUE", "VERI_STEP", "VERI_MODEL", "VERI_MODEL_VERIFIER"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", retries)
    supervised = []

    def fake(args, *_, **__):
        name = os.path.basename(str(args[0]))
        if name == "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"blind prompt", b"")
        if name == "supervise.sh":
            supervised.append(args)
            return subprocess.CompletedProcess(args, 0, NO_VERDICT, None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["green", "spec.md", "tests/x.test.sh"])

    assert (code, len(supervised)) == (2, launches)


def test_main_copies_parse_verdicts_stderr_to_its_own_stderr_after_every_launch_relaunched_ones_included(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    for name in ("VERIFY_LEAF_ARGS", "VERI_ISSUE", "VERI_STEP", "VERI_MODEL", "VERI_MODEL_VERIFIER"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "2")
    leaf_outs = [NO_VERDICT, NO_VERDICT, b"VERDICT: MAYBE\nundecided\n"]
    supervised = []

    def fake(args, *_, **__):
        name = os.path.basename(str(args[0]))
        if name == "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"blind prompt", b"")
        if name == "supervise.sh":
            supervised.append(args)
            os.write(2, b"launch %d\n" % len(supervised))
            return subprocess.CompletedProcess(args, 0, leaf_outs[len(supervised) - 1], None)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["green", "spec.md", "tests/x.test.sh"])

    assert (code, capfdbinary.readouterr().err) == (
        2, b"launch 1\n" + NO_LINE + b"launch 2\n" + NO_LINE
        + b"launch 3\nparse-verdict: unrecognised verdict word 'MAYBE'\n")
