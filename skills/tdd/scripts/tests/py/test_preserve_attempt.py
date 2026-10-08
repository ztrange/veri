"""In-process cases for veri/preserve_attempt.py, the module preserve-attempt.sh is a shim over."""
import importlib
import os
import subprocess
import sys
import tempfile

import pytest


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


def test_main_keeps_the_argument_for_a_step_only_a_substring_of_ledger_steps_or_when_the_ledger_gives_none_issue_1031(
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
        ("two-matches", 0, ["refs/veri/attempts/409/abcd/develop-green-1"], ""),
        ("no-match", 0, ["refs/veri/attempts/409/zzz/develop-green-1"], ""),
        ("no-ledger", 0, ["refs/veri/attempts/409/zzz/develop-green-1"], ""),
        ("nul", 0, ["refs/veri/attempts/409/2/develop-green-1"], ""),
        ("directory", 0, ["refs/veri/attempts/409/zzz/develop-green-1"], ""),
        ("unreadable", 0, ["refs/veri/attempts/409/abcd/develop-green-1"],
         "preserve-attempt.sh: .tdd/issue-409.md: Input/output error\n"),
    ]


def test_main_reads_a_digits_only_step_as_the_ledger_index_past_an_earlier_step_containing_the_digit_issue_1031(
        monkeypatch, tmp_path, preserve_attempt):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / ".tdd" / "issue-409.md").write_text(
        "# Plan for #409\n"
        "- [x] say what #125 owes ⟦criterion 1⟧\n"
        "- [ ] keep the leaf's output under refs/veri ⟦criterion 2⟧\n"
    )
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

    code = preserve_attempt.main(["409", "2", "develop-green", "1"])

    assert (code, update_refs) == (0, ["refs/veri/attempts/409/2/develop-green-1"])


def test_main_reads_a_step_equal_to_a_later_steps_full_text_as_that_index_past_an_earlier_step_containing_it_issue_1031(
        monkeypatch, tmp_path, preserve_attempt):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / ".tdd" / "issue-409.md").write_text(
        "# Plan for #409\n"
        "- [x] keep the leaf's output under refs/veri\n"
        "- [ ] keep the leaf's output\n"
    )
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

    code = preserve_attempt.main(["409", "keep the leaf's output", "develop-green", "1"])

    assert (code, update_refs) == (0, ["refs/veri/attempts/409/2/develop-green-1"])


def test_main_reads_a_step_equal_to_a_later_steps_text_without_its_trailing_marks_as_that_index_issue_1031(
        monkeypatch, tmp_path, preserve_attempt):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / ".tdd" / "issue-409.md").write_text(
        "# Plan for #409\n"
        "- [x] keep the leaf's output under refs/veri ⟦criterion 1⟧\n"
        "- [x] keep the leaf's output ⟦criterion 2⟧ ⟂ refactor pending\n"
    )
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

    code = preserve_attempt.main(["409", "keep the leaf's output", "refactor", "1"])

    assert (code, update_refs) == (0, ["refs/veri/attempts/409/2/refactor-1"])


def test_main_names_the_step_ref_and_its_attempts_files_the_same_under_every_locale_issue_1032(
        monkeypatch, tmp_path, preserve_attempt):
    update_refs = []

    def scenario(name, lc_all):
        for variable in ("LC_ALL", "LC_CTYPE", "LANG"):
            monkeypatch.delenv(variable, raising=False)
        if lc_all is not None:
            monkeypatch.setenv("LC_ALL", lc_all)
        repo = tmp_path / name
        tdd = repo / ".tdd"
        tdd.mkdir(parents=True)
        (tdd / "develop-green.log").write_text("log\n")
        monkeypatch.chdir(repo)

        def fake_run(args, *_, **__):
            if args[1] == "rev-parse":
                return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
            if args[1] == "write-tree":
                return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
            if args[1] == "commit-tree":
                return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
            if args[1] == "update-ref":
                update_refs.append(str(args[2]))
            return subprocess.CompletedProcess(args, 0, "", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        del update_refs[:]
        code = preserve_attempt.main(["409", "a—b ⟦x⟧/c'd", "develop-green", "1", "stuck"])
        attempts = tdd / "attempts"
        files = sorted(os.listdir(attempts)) if attempts.is_dir() else None
        return code, list(update_refs), files

    answers = [
        scenario("c", "C"),
        scenario("utf8", "en_US.UTF-8"),
        scenario("codeset-less", "en_US"),
        scenario("unset", None),
    ]

    assert answers[0][0] == 0 and len(answers[0][1]) == 1 and answers[0][2]
    assert answers == [answers[0]] * 4


def test_main_names_the_step_ref_and_its_attempts_files_by_the_steps_bytes_under_a_non_utf8_locale_issue_1047(
        monkeypatch, tmp_path, preserve_attempt):
    update_refs = []
    real_fsencode = os.fsencode

    def scenario(name, lc_all, charset):
        for variable in ("LC_ALL", "LC_CTYPE", "LANG"):
            monkeypatch.delenv(variable, raising=False)
        monkeypatch.setenv("LC_ALL", lc_all)
        if charset is None:
            monkeypatch.setattr(os, "fsencode", real_fsencode)
            monkeypatch.setattr(sys, "getfilesystemencoding", lambda: "utf-8")
            step = "a—b"
        else:
            monkeypatch.setattr(os, "fsencode", lambda s: s.encode(charset, "surrogateescape")
                                if isinstance(s, str) else real_fsencode(s))
            monkeypatch.setattr(sys, "getfilesystemencoding", lambda: charset)
            step = "a—b".encode("utf-8").decode(charset, "surrogateescape")
        repo = tmp_path / name
        tdd = repo / ".tdd"
        tdd.mkdir(parents=True)
        (tdd / "develop-green.log").write_text("log\n")
        monkeypatch.chdir(repo)

        def fake_run(args, *_, **__):
            if args[1] == "rev-parse":
                return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
            if args[1] == "write-tree":
                return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
            if args[1] == "commit-tree":
                return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
            if args[1] == "update-ref":
                update_refs.append(str(args[2]))
            return subprocess.CompletedProcess(args, 0, "", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        del update_refs[:]
        code = preserve_attempt.main(["409", step, "develop-green", "1", "stuck"])
        attempts = tdd / "attempts"
        files = sorted(os.listdir(attempts)) if attempts.is_dir() else None
        return code, list(update_refs), files

    answers = [
        scenario("c", "C", None),
        scenario("utf8", "en_US.UTF-8", None),
        scenario("latin1", "en_US.ISO8859-1", "iso-8859-1"),
    ]

    assert answers[0][0] == 0 and len(answers[0][1]) == 1 and answers[0][2]
    assert answers == [answers[0]] * 3


def test_main_runs_git_from_the_top_level_with_a_fresh_index_for_the_snapshot_and_the_raw_step_in_the_message(
        monkeypatch, tmp_path, preserve_attempt):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / "sub" / "dir").mkdir(parents=True)
    step = "keep it/ok's"
    (repo / ".tdd" / "issue-409.md").write_text(f"# Plan\n- [x] an earlier step\n- [ ] {step}\n")
    scratch_parent = tmp_path / "tmp"
    scratch_parent.mkdir()
    monkeypatch.setenv("TMPDIR", str(scratch_parent))
    monkeypatch.setattr(tempfile, "tempdir", None)
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Inherited Author")
    monkeypatch.delenv("GIT_INDEX_FILE", raising=False)
    monkeypatch.chdir(repo / "sub" / "dir")
    calls = []

    def fake_run(args, *_, env=None, **__):
        effective = dict(os.environ if env is None else env)
        index = effective.get("GIT_INDEX_FILE")
        calls.append({
            "argv": [os.path.basename(str(args[0]))] + [str(a) for a in args[1:]],
            "cwd": os.getcwd(),
            "env": effective,
            "index_existed": index is not None and os.path.exists(index),
            "index_dir_existed": index is not None and os.path.isdir(os.path.dirname(index)),
        })
        if args[1] == "rev-parse":
            return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
        if args[1] == "write-tree":
            return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
        if args[1] == "commit-tree":
            return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    inherited = dict(os.environ)

    code = preserve_attempt.main(["409", step, "develop-green", "1"])

    by_verb = {call["argv"][1]: call for call in calls}
    index = by_verb["add"]["env"].get("GIT_INDEX_FILE", "")
    assert code == 0
    assert [call["argv"][1] for call in calls] == [
        "rev-parse", "read-tree", "add", "write-tree", "commit-tree", "update-ref"]
    assert [call["cwd"] for call in calls[1:]] == [str(repo)] * 5
    assert os.path.dirname(os.path.dirname(index)) == str(scratch_parent)
    assert (by_verb["add"]["index_dir_existed"], by_verb["add"]["index_existed"]) == (True, False)
    assert by_verb["read-tree"]["argv"] == ["git", "read-tree", "HEAD"]
    assert by_verb["read-tree"]["env"] == {**inherited, "GIT_INDEX_FILE": index}
    assert by_verb["add"]["env"] == {**inherited, "GIT_INDEX_FILE": index}
    assert by_verb["write-tree"]["env"] == {**inherited, "GIT_INDEX_FILE": index}
    for verb in ("rev-parse", "commit-tree", "update-ref"):
        assert by_verb[verb]["env"] == inherited, verb
    assert by_verb["commit-tree"]["argv"] == [
        "git", "commit-tree", "4b825dc642cb6eb9a060e54bf8d69288fbee4904", "-p", "HEAD",
        "-m", f"attempt: issue 409 step {step} develop-green attempt 1"]
    assert by_verb["update-ref"]["argv"][2] == "refs/veri/attempts/409/2/develop-green-1"


def test_main_returns_2_outside_a_work_tree_and_maps_a_failing_add_or_write_tree_with_the_scratch_gone_issue_1030(
        monkeypatch, tmp_path, capsys, preserve_attempt):
    repo = tmp_path / "repo"
    repo.mkdir()
    scratch_parent = tmp_path / "tmp"
    scratch_parent.mkdir()
    monkeypatch.setenv("TMPDIR", str(scratch_parent))
    monkeypatch.setattr(tempfile, "tempdir", None)

    def scenario(failing_verb, status):
        monkeypatch.chdir(repo)
        verbs = []

        def fake_run(args, *_, **__):
            verbs.append(str(args[1]))
            if args[1] == failing_verb:
                return subprocess.CompletedProcess(args, status, "", None)
            if args[1] == "rev-parse":
                return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
            if args[1] == "write-tree":
                return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
            if args[1] == "commit-tree":
                return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
            return subprocess.CompletedProcess(args, 0, "", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = preserve_attempt.main(["409", "3", "develop-green", "1"])
        captured = capsys.readouterr()
        return (failing_verb, status, code, verbs, captured.out, captured.err.splitlines()[-1:],
                sorted(os.listdir(scratch_parent)))

    answers = [
        scenario("rev-parse", 128),
        scenario("add", 1),
        scenario("add", 128),
        scenario("write-tree", 1),
        scenario("write-tree", 128),
    ]

    assert answers == [
        ("rev-parse", 128, 2, ["rev-parse"], "",
         ["preserve-attempt.sh: not in a git work tree"], []),
        ("add", 1, 1, ["rev-parse", "read-tree", "add"], "", [], []),
        ("add", 128, 2, ["rev-parse", "read-tree", "add"], "", [], []),
        ("write-tree", 1, 1, ["rev-parse", "read-tree", "add", "write-tree"], "", [], []),
        ("write-tree", 128, 2, ["rev-parse", "read-tree", "add", "write-tree"], "", [], []),
    ]


def test_main_copies_each_regular_leaf_file_under_its_mark_and_returns_1_when_a_copy_fails(
        monkeypatch, tmp_path, preserve_attempt):
    def scenario(name, argv, plant):
        repo = tmp_path / name
        tdd = repo / ".tdd"
        tdd.mkdir(parents=True)
        plant(tdd)
        monkeypatch.chdir(repo)

        def fake_run(args, *_, **__):
            if args[1] == "rev-parse":
                return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
            if args[1] == "write-tree":
                return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
            if args[1] == "commit-tree":
                return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
            return subprocess.CompletedProcess(args, 0, "", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = preserve_attempt.main(argv)
        attempts = tdd / "attempts"
        listing = None
        if attempts.is_dir():
            listing = {
                entry.name: (entry.read_text(), oct(entry.stat().st_mode & 0o777)) if entry.is_file() else "dir"
                for entry in sorted(attempts.iterdir())
            }
        return name, code, listing

    def leaf_files(tdd):
        (tdd / "develop-green.log").write_text("new log\n")
        (tdd / "develop-green.log").chmod(0o640)
        (tdd / "develop-green.out").write_text("new out\n")
        (tdd / "develop-green.out").chmod(0o750)
        (tdd / "attempts").mkdir()
        (tdd / "attempts" / "3-develop-green-1-reject.log").write_text("earlier log\n")
        (tdd / "attempts" / "3-develop-green-1-reject.log").chmod(0o640)

    def log_and_a_directory_named_out(tdd):
        (tdd / "develop-green.log").write_text("new log\n")
        (tdd / "develop-green.log").chmod(0o640)
        (tdd / "develop-green.out").mkdir()

    def blocked_copy(tdd):
        (tdd / "develop-green.log").write_text("new log\n")
        (tdd / "attempts" / "3-develop-green-1-reject.log" / "develop-green.log").mkdir(parents=True)

    answers = [
        scenario("neither", ["409", "3", "develop-green", "1", "reject"], lambda tdd: None),
        scenario("both", ["409", "3", "develop-green", "1", "reject", "ignored", "too"], leaf_files),
        scenario("not-regular", ["409", "3", "develop-green", "1", "reject"], log_and_a_directory_named_out),
        scenario("no-mark", ["409", "3", "develop-green", "1", ""],
                 lambda tdd: (tdd / "develop-green.log").write_text("new log\n")),
        scenario("blocked", ["409", "3", "develop-green", "1", "reject"], blocked_copy)[:2],
    ]

    assert answers == [
        ("neither", 0, {}),
        ("both", 0, {
            "3-develop-green-1-reject.log": ("new log\n", "0o640"),
            "3-develop-green-1-reject.out": ("new out\n", "0o750"),
        }),
        ("not-regular", 0, {"3-develop-green-1-reject.log": ("new log\n", "0o640")}),
        ("no-mark", 0, None),
        ("blocked", 1),
    ]


def test_main_writes_nothing_on_stdout_preserved_refused_arguments_update_ref_refused_or_git_failure(
        monkeypatch, tmp_path, capfd, preserve_attempt):
    def scenario(name, argv, failing_verb):
        repo = tmp_path / name
        (repo / ".tdd").mkdir(parents=True)
        (repo / ".tdd" / "develop-green.log").write_text("log\n")
        (repo / ".tdd" / "develop-green.out").write_text("out\n")
        monkeypatch.chdir(repo)

        def fake_run(args, *_, **__):
            if args[1] == failing_verb:
                return subprocess.CompletedProcess(args, 128, "", None)
            if args[1] == "rev-parse":
                return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
            if args[1] == "write-tree":
                return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
            if args[1] == "commit-tree":
                return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
            return subprocess.CompletedProcess(args, 0, "", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = preserve_attempt.main(argv)
        return name, code, capfd.readouterr().out

    answers = [
        scenario("preserved", ["409", "3", "develop-green", "1", "reject"], None),
        scenario("refused-arguments", ["409", "3", "develop-green"], None),
        scenario("update-ref-refused", ["409", "3", "develop-green", "1", "reject"], "update-ref"),
        scenario("git-failure", ["409", "3", "develop-green", "1", "reject"], "commit-tree"),
    ]

    assert answers == [
        ("preserved", 0, ""),
        ("refused-arguments", 2, ""),
        ("update-ref-refused", 1, ""),
        ("git-failure", 2, ""),
    ]
