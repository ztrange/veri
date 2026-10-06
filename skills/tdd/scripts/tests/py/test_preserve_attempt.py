"""In-process cases for veri/preserve_attempt.py, the module preserve-attempt.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys
import tempfile

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def preserve_attempt():
    return importlib.import_module("veri.preserve_attempt")


def fake_processes(monkeypatch):
    """Every subprocess entry point recording each command as one line, its program by basename."""
    calls = []

    def record(args, *_, **__):
        calls.append(" ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]]))
        return subprocess.CompletedProcess(args, 0, "", "")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, record)
    return calls


def test_main_refuses_missing_or_empty_arguments_with_its_usage_line_and_no_git_call(
        monkeypatch, capsys, preserve_attempt):
    calls = fake_processes(monkeypatch)

    answers = []
    for argv in ([], ["409", "3", "develop-green"], ["409", "3", "develop-green", ""]):
        code = preserve_attempt.main(argv)
        captured = capsys.readouterr()
        answers.append((argv, code, captured.out, captured.err))

    usage = "usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]\n"
    assert calls == []
    assert answers == [
        ([], 2, "", usage),
        (["409", "3", "develop-green"], 2, "", usage),
        (["409", "3", "develop-green", ""], 2, "", usage),
    ]


def test_main_returns_2_when_commit_tree_exits_128_with_the_scratch_directory_gone_and_no_update_ref(
        monkeypatch, tmp_path, preserve_attempt):
    repo = tmp_path / "repo"
    repo.mkdir()
    scratch_parent = tmp_path / "tmp"
    scratch_parent.mkdir()
    monkeypatch.chdir(repo)
    monkeypatch.setenv("TMPDIR", str(scratch_parent))
    monkeypatch.setattr(tempfile, "tempdir", None)
    calls = []

    def fake_run(args, *_, **__):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        calls.append(line)
        if line.startswith("git rev-parse --show-toplevel"):
            return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
        if line.startswith("git write-tree"):
            return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
        if line.startswith("git commit-tree"):
            return subprocess.CompletedProcess(args, 128, "", "")
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = preserve_attempt.main(["409", "3", "develop-green", "1"])

    update_refs = [line for line in calls if line.startswith("git update-ref")]
    assert (code, update_refs, sorted(os.listdir(scratch_parent))) == (2, [], [])


def test_main_returns_1_with_its_could_not_preserve_line_and_no_copy_when_update_ref_exits_128(
        monkeypatch, tmp_path, capsys, preserve_attempt):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / ".tdd" / "develop-green.log").write_text("log\n")
    (repo / ".tdd" / "develop-green.out").write_text("out\n")
    monkeypatch.chdir(repo)

    def fake_run(args, *_, **__):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        if line.startswith("git rev-parse --show-toplevel"):
            return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
        if line.startswith("git write-tree"):
            return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
        if line.startswith("git commit-tree"):
            return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
        if line.startswith("git update-ref"):
            return subprocess.CompletedProcess(args, 128, None, None)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = preserve_attempt.main(["409", "3", "develop-green", "1", "reject"])
    captured = capsys.readouterr()

    line = ("preserve-attempt.sh: could not preserve issue 409 step 3 develop-green attempt 1"
            " to refs/veri/attempts/409/3/develop-green-1")
    assert (code, captured.out, captured.err.splitlines()[-1:], (repo / ".tdd" / "attempts").exists()) == (
        1, "", [line], False)


def test_main_names_the_ref_by_the_ledger_index_ledger_steps_gives_the_step_past_prose_and_star_lines(
        monkeypatch, tmp_path, preserve_attempt):
    from veri.ledger import ledger_steps

    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    step = "keep the leaf's output under refs/veri"
    ledger = (
        "# Plan for #409\n"
        f"Prose first: {step}, never the branch.\n"
        f"* [ ] {step}\n"
        "- [x] an earlier step ⟦criterion 1⟧\n"
        f"- [ ] {step} ⟦criterion 2⟧\n"
    )
    (repo / ".tdd" / "issue-409.md").write_text(ledger)
    monkeypatch.chdir(repo)
    update_refs = []

    def fake_run(args, *_, **__):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        if line.startswith("git rev-parse --show-toplevel"):
            return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
        if line.startswith("git write-tree"):
            return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
        if line.startswith("git commit-tree"):
            return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
        if line.startswith("git update-ref"):
            update_refs.append(str(args[2]))
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = preserve_attempt.main(["409", step, "develop-green", "1"])

    index = next(record[0] for record in ledger_steps(ledger) if step in record[6])
    assert (index, code, update_refs) == ("2", 0, ["refs/veri/attempts/409/2/develop-green-1"])


def test_main_names_the_ref_by_the_first_matching_step_and_keeps_the_argument_when_the_ledger_gives_none(
        monkeypatch, tmp_path, capsys, preserve_attempt):
    import builtins
    import io

    real_open = builtins.open

    def refusing_open(file, mode="r", *args, **kwargs):
        if os.path.abspath(str(file)).endswith("unreadable/.tdd/issue-409.md") and "r" in mode:
            raise OSError(5, "Input/output error")
        return real_open(file, mode, *args, **kwargs)

    def scenario(name, ledger, step):
        repo = tmp_path / name
        (repo / ".tdd").mkdir(parents=True, exist_ok=True)
        if ledger is not None:
            (repo / ".tdd" / "issue-409.md").write_bytes(ledger)
        monkeypatch.chdir(repo)
        update_refs = []

        def fake_run(args, *_, **__):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            if line.startswith("git rev-parse --show-toplevel"):
                return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
            if line.startswith("git write-tree"):
                return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
            if line.startswith("git commit-tree"):
                return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
            if line.startswith("git update-ref"):
                update_refs.append(str(args[2]))
            return subprocess.CompletedProcess(args, 0, "", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = preserve_attempt.main(["409", step, "develop-green", "1"])
        return name, code, update_refs, capsys.readouterr().err

    two_matches = b"# Plan\n- [ ] unrelated\n- [ ] first abcd one\n- [ ] second abcd two\n"
    answers = [
        scenario("two-matches", two_matches, "abcd"),
        scenario("no-match", two_matches, "zzz"),
        scenario("no-ledger", None, "zzz"),
        scenario("nul", b"# Plan\n- [ ] unrelated\n- [ ] ab\0cd\n", "abcd"),
    ]
    (tmp_path / "directory" / ".tdd" / "issue-409.md").mkdir(parents=True)
    answers.append(scenario("directory", None, "zzz"))
    monkeypatch.setattr(builtins, "open", refusing_open)
    monkeypatch.setattr(io, "open", refusing_open)
    answers.append(scenario("unreadable", two_matches, "abcd"))

    assert answers == [
        ("two-matches", 0, ["refs/veri/attempts/409/2/develop-green-1"], ""),
        ("no-match", 0, ["refs/veri/attempts/409/zzz/develop-green-1"], ""),
        ("no-ledger", 0, ["refs/veri/attempts/409/zzz/develop-green-1"], ""),
        ("nul", 0, ["refs/veri/attempts/409/2/develop-green-1"], ""),
        ("directory", 0, ["refs/veri/attempts/409/zzz/develop-green-1"], ""),
        ("unreadable", 0, ["refs/veri/attempts/409/abcd/develop-green-1"],
         "preserve-attempt.sh: .tdd/issue-409.md: Input/output error\n"),
    ]


def test_main_sanitises_the_step_ref_per_byte_or_per_character_by_lc_all_then_lc_ctype_then_lang(
        monkeypatch, tmp_path, preserve_attempt):
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    update_refs = []

    def fake_run(args, *_, **__):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        if line.startswith("git rev-parse --show-toplevel"):
            return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
        if line.startswith("git write-tree"):
            return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
        if line.startswith("git commit-tree"):
            return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
        if line.startswith("git update-ref"):
            update_refs.append(str(args[2]))
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    def scenario(lc_all, lc_ctype, lang):
        for name, value in (("LC_ALL", lc_all), ("LC_CTYPE", lc_ctype), ("LANG", lang)):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)
        del update_refs[:]
        code = preserve_attempt.main(["409", "a—b ⟦x⟧/c'd", "develop-green", "1"])
        return code, list(update_refs)

    by_byte = (0, ["refs/veri/attempts/409/a---b----x----c-d/develop-green-1"])
    by_char = (0, ["refs/veri/attempts/409/a-b--x--c-d/develop-green-1"])
    answers = [
        scenario("C", "en_US.UTF-8", "en_US.UTF-8"),
        scenario("en_US.UTF-8", "C", "C"),
        scenario(None, "C", "en_US.UTF-8"),
        scenario(None, "en_US.UTF-8", "C"),
        scenario(None, None, "en_US.UTF-8"),
        scenario(None, None, None),
    ]

    assert answers == [by_byte, by_char, by_byte, by_char, by_char, by_byte]
