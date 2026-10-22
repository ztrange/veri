"""In-process cases for veri/preserve_attempt.py, the module preserve-attempt.sh is a shim over."""
import importlib
import importlib.util
import os
import subprocess
import sys
import tempfile

import pytest


@pytest.fixture
def preserve_attempt():
    return importlib.import_module("veri.preserve_attempt")


def test_main_refuses_missing_or_empty_arguments_with_its_usage_line_and_no_git_call(
        monkeypatch, capsys, preserve_attempt, fake_processes):
    calls = fake_processes()

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
    for verb in ("rev-parse", "update-ref"):
        assert by_verb[verb]["env"] == inherited, verb
    assert by_verb["commit-tree"]["env"] == preserve_attempt.IDENTITY | inherited
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

        def fake_run(args, *_, **kwargs):
            verbs.append(str(args[1]))
            if args[1] == failing_verb:
                if args[1] == "rev-parse" and kwargs.get("stderr") is None:
                    print("fatal: not a git repository (or any of the parent directories): .git",
                          file=sys.stderr)
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
        return (failing_verb, status, code, verbs, captured.out, captured.err.splitlines(),
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


REF = "refs/veri/attempts/409/3/develop-green-1"
IDENT = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@example.test",
         "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@example.test"}
REJECTED = "rejected work"


def git_in(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          env={**os.environ, **IDENT})


def make_repo(root):
    root.mkdir(parents=True)
    git_in(root, "init", "-q", "-b", "main")
    (root / "stop-run.sh").write_text("committed\n")
    git_in(root, "add", "stop-run.sh")
    git_in(root, "commit", "-q", "-m", "initial")
    return root


def dirty_repo(root):
    make_repo(root)
    (root / "stop-run.sh").write_text(REJECTED + "\n")
    return root


def write_ledger(repo, *steps):
    (repo / ".tdd").mkdir(exist_ok=True)
    lines = ["# Plan for #409", ""]
    lines += [f"- [{'x' if i == 0 else ' '}] {step}" for i, step in enumerate(steps)]
    (repo / ".tdd" / "issue-409.md").write_text("\n".join(lines) + "\n")
    git_in(repo, "add", ".tdd/issue-409.md")
    git_in(repo, "commit", "-q", "-m", "plan: scope #409")


def leaf_output(repo, log_text, out_text=None):
    (repo / ".tdd").mkdir(exist_ok=True)
    (repo / ".tdd" / "develop-green.log").write_text(log_text + "\n")
    if out_text is not None:
        (repo / ".tdd" / "develop-green.out").write_text(out_text + "\n")


def preserve_in(run_cli, preserve_attempt, monkeypatch, repo, *args):
    for name, value in IDENT.items():
        monkeypatch.setenv(name, value)
    return run_cli(preserve_attempt, list(args), cwd=repo)


def ref_resolves(repo, ref=REF):
    return git_in(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}").returncode == 0


def attempts(repo):
    directory = repo / ".tdd" / "attempts"
    return sorted(os.listdir(directory)) if directory.exists() else []


@pytest.mark.process("real git repository and its side ref")
def test_commits_the_worktree_to_the_ref_and_git_show_reads_it_back(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    shown = git_in(repo, "show", f"{REF}:stop-run.sh").stdout.rstrip("\n")
    assert (code, out, err, ref_resolves(repo), shown) == (0, "", "", True, REJECTED)


@pytest.mark.process("real git repository and its side ref")
def test_leaves_head_the_index_and_git_log_untouched(tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    (repo / "staged.txt").write_text("staged\n")
    git_in(repo, "add", "staged.txt")

    def state():
        return (git_in(repo, "rev-parse", "HEAD").stdout, git_in(repo, "ls-files", "-s").stdout,
                git_in(repo, "log", "--oneline").stdout)

    before = state()
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert (code, out, err, state()) == (0, "", "", before)


@pytest.mark.process("real git repository and the leaf's files")
def test_copies_the_leafs_log_and_final_output_to_names_carrying_step_phase_attempt_and_mark(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = make_repo(tmp_path / "repo")
    leaf_output(repo, "streamed progress", "final result text")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "3", "develop-green", "1", "reject")
    copies = repo / ".tdd" / "attempts"
    assert (code, out, err) == (0, "", "")
    assert (copies / "3-develop-green-1-reject.log").read_text() == "streamed progress\n"
    assert (copies / "3-develop-green-1-reject.out").read_text() == "final result text\n"
    assert (repo / ".tdd" / "develop-green.log").is_file()
    assert (repo / ".tdd" / "develop-green.out").is_file()


@pytest.mark.process("real git repository and the leaf's files")
def test_preserves_the_log_of_a_leaf_that_wrote_no_final_output_with_exit_0(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = make_repo(tmp_path / "repo")
    leaf_output(repo, "streamed progress")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "3", "develop-green", "1", "stuck")
    assert (code, out, err) == (0, "", "")
    assert (repo / ".tdd" / "attempts" / "3-develop-green-1-stuck.log").read_text() == "streamed progress\n"
    assert attempts(repo) == ["3-develop-green-1-stuck.log"]


@pytest.mark.process("real git repository and its side ref")
def test_preserves_the_tree_and_exits_0_when_the_leaf_wrote_neither_log_nor_output(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "3", "develop-green", "1", "bail")
    assert (code, out, err, ref_resolves(repo), attempts(repo)) == (0, "", "", True, [])


@pytest.mark.process("real git repository and the leaf's files")
def test_copies_nothing_when_no_mark_is_given_log_present(tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    leaf_output(repo, "streamed progress", "final result text")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert (code, out, err, ref_resolves(repo)) == (0, "", "", True)
    assert not (repo / ".tdd" / "attempts").exists()
    assert attempts(repo) == []


@pytest.mark.process("real git repository and ancestry of the side ref")
def test_leaves_the_preserved_commit_unreachable_from_head_with_a_message_carrying_no_rationale(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    rationale = "I used a helper because the verifier rejected the inline version"
    leaf_output(repo, rationale, rationale)
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "3", "develop-green", "1", "reject")
    reachable = git_in(repo, "merge-base", "--is-ancestor", REF, "HEAD").returncode == 0
    message = git_in(repo, "log", "-1", "--format=%B", REF).stdout.strip()
    assert (code, out, err, reachable, message) == (
        0, "", "", False, "attempt: issue 409 step 3 develop-green attempt 1")


@pytest.mark.process("real git repository and its side ref")
def test_names_the_ref_by_the_steps_ledger_index_not_its_prose(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    prose = "A leaf's output is kept under refs/veri, not the branch"
    write_ledger(repo, "The first step, already done", prose, "A third step nobody is on")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", prose, "develop-green", "1")
    refs = git_in(repo, "for-each-ref", "--format=%(refname)", "refs/veri/attempts").stdout.split()
    assert (code, out, err, refs) == (0, "", "", ["refs/veri/attempts/409/2/develop-green-1"])


@pytest.mark.process("real git repository and git check-ref-format")
def test_preserves_the_attempt_under_a_ref_git_accepts_when_the_step_title_carries_spaces_an_apostrophe_and_a_slash(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    prose = "A leaf's tree is kept under refs/veri, not the branch"
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", prose, "develop-green", "1")
    found = git_in(repo, "for-each-ref", "--count=1", "--format=%(refname)", "refs/veri/attempts/409").stdout.strip()
    legal = git_in(repo, "check-ref-format", found).returncode == 0
    shown = git_in(repo, "show", f"{found}:stop-run.sh").stdout.rstrip("\n")
    assert (code, out, err, bool(found), legal, shown) == (0, "", "", True, True, REJECTED)


@pytest.mark.process("real git repository and the leaf's files")
def test_names_the_leafs_copies_by_the_steps_ledger_index_so_a_title_carrying_a_slash_writes_no_nested_path(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = make_repo(tmp_path / "repo")
    prose = "A leaf's output is kept under refs/veri, not the branch"
    write_ledger(repo, "The first step, already done", prose)
    leaf_output(repo, "streamed progress", "final result text")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", prose, "develop-green", "1", "reject")
    copies = repo / ".tdd" / "attempts"
    assert (code, out, err) == (0, "", "")
    assert (copies / "2-develop-green-1-reject.log").read_text() == "streamed progress\n"
    assert (copies / "2-develop-green-1-reject.out").read_text() == "final result text\n"
    assert attempts(repo) == ["2-develop-green-1-reject.log", "2-develop-green-1-reject.out"]


@pytest.mark.process("real git repository whose ref store refuses the write")
def test_says_on_stderr_that_it_could_not_preserve_the_attempt_when_the_ref_write_fails_for_another_reason(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    git_in(repo, "update-ref", "refs/veri/attempts/409/3", "HEAD")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert code != 0
    assert "preserve-attempt.sh" in err and "409" in err and "develop-green" in err


@pytest.mark.process("real git repository whose ref store refuses the write")
def test_exits_exactly_1_with_the_could_not_preserve_line_last_on_stderr_when_an_existing_ref_refuses_the_ref_write(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    git_in(repo, "update-ref", "refs/veri/attempts/409/3", "HEAD")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    expected = f"preserve-attempt.sh: could not preserve issue 409 step 3 develop-green attempt 1 to {REF}"
    assert (code, err.splitlines()[-1:]) == (1, [expected])


@pytest.mark.process("real git repository carrying a copy of the skill, left without a side ref")
def test_refuses_from_the_skills_own_scripts_directory_with_exit_2_one_stderr_line_and_no_ref_or_attempts_entry(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    decoy = make_repo(tmp_path / "decoy")
    write_ledger(decoy, "The first step, already done", "A step the decoy is on")
    leaf_output(decoy, "decoy progress", "decoy result")
    ledger_before = (decoy / ".tdd" / "issue-409.md").read_text()
    scripts = decoy / "skills" / "tdd" / "scripts"
    (scripts / "veri").mkdir(parents=True)
    (scripts / "tests").mkdir()
    copy = scripts / "veri" / "preserve_attempt.py"
    with open(preserve_attempt.__file__) as source:
        copy.write_text(source.read())
    spec = importlib.util.spec_from_file_location("preserve_attempt_scratch_copy", copy)
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    expected = ("preserve-attempt.sh: type this from the run's worktree,"
                " not from the skill's own scripts directory\n")
    answers = [preserve_in(run_cli, subject, monkeypatch, where, "409", "3", "develop-green", "1", "reject")
               for where in (scripts, scripts / "tests")]
    refs = git_in(decoy, "for-each-ref", "--format=%(refname)", "refs/veri").stdout
    assert answers == [(2, "", expected), (2, "", expected)]
    assert (refs, attempts(decoy), (decoy / ".tdd" / "issue-409.md").read_text()) == ("", [], ledger_before)


@pytest.mark.process("real git refusing a directory that is not a work tree")
def test_outside_a_work_tree_with_a_mark_exits_2_and_writes_no_attempts_entry_copy_or_ref(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    leaf_output(outside, "leaf log", "leaf output")

    def tree():
        return sorted(str(p.relative_to(outside)) for p in outside.rglob("*"))

    before = tree()
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, outside,
                                 "409", "3", "develop-green", "1", "reject")
    assert (code, out, err) == (2, "", "preserve-attempt.sh: not in a git work tree\n")
    assert attempts(outside) == []
    assert tree() == before
    assert not (outside / ".git").exists()


@pytest.mark.process("real git repository with an unborn HEAD")
def test_exits_2_when_the_repository_has_an_unborn_head(tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = tmp_path / "unborn"
    repo.mkdir()
    git_in(repo, "init", "-q", "-b", "main")
    (repo / "stop-run.sh").write_text(REJECTED + "\n")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert code == 2


@pytest.mark.process("real symlinked shim run from a subdirectory of another repository")
def test_preserves_the_same_ref_tree_and_exit_code_through_a_symlink_to_the_skill_from_a_subdirectory(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    skill = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(preserve_attempt.__file__))))
    link = tmp_path / "skill-link"
    link.symlink_to(skill)
    inplace = dirty_repo(tmp_path / "inplace")
    linked = dirty_repo(tmp_path / "linked")
    for repo in (inplace, linked):
        (repo / "sub").mkdir()
        (repo / "sub" / "nested.txt").write_text("nested\n")
    code_inplace, _, _ = preserve_in(run_cli, preserve_attempt, monkeypatch, inplace,
                                     "409", "3", "develop-green", "1")
    ran = subprocess.run([str(link / "scripts" / "preserve-attempt.sh"), "409", "3", "develop-green", "1"],
                         cwd=linked / "sub", capture_output=True, text=True, env={**os.environ, **IDENT})
    tree_inplace = git_in(inplace, "rev-parse", "--verify", "--quiet", REF + "^{tree}").stdout.strip()
    tree_linked = git_in(linked, "rev-parse", "--verify", "--quiet", REF + "^{tree}").stdout.strip()
    assert (ran.returncode, code_inplace) == (0, 0)
    assert tree_inplace and tree_linked == tree_inplace


@pytest.mark.process("real git repository and git check-ref-format")
def test_makes_one_ref_git_accepts_for_a_step_holding_multi_byte_characters_a_slash_an_apostrophe_and_spaces(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "a—b ⟦x⟧/c'd e", "develop-green", "1")
    made = git_in(repo, "for-each-ref", "--format=%(refname)", "refs/veri/attempts/409/").stdout.split("\n")[:-1]
    legal = [git_in(repo, "check-ref-format", ref).returncode == 0 for ref in made]
    assert (code, len(made), legal) == (0, 1, [True])


def tracked_ignored_repo(root):
    make_repo(root)
    (root / "t.txt").write_text("committed\n")
    (root / "gone.txt").write_text("committed\n")
    git_in(root, "add", "t.txt", "gone.txt")
    git_in(root, "commit", "-q", "-m", "track t.txt and gone.txt")
    return root


@pytest.mark.process("real git repository and its side ref")
def test_keeps_a_file_tracked_in_head_and_matched_by_gitignore_in_the_preserved_tree_with_its_worktree_content(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = tracked_ignored_repo(tmp_path / "repo")
    (repo / ".gitignore").write_text("t.txt\n")
    (repo / "t.txt").write_text("edited by the leaf\n")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    shown = git_in(repo, "show", f"{REF}:t.txt").stdout.rstrip("\n")
    assert (code, shown) == (0, "edited by the leaf")


@pytest.mark.process("real git repository and its side ref")
def test_beside_a_tracked_ignored_file_leaves_an_untracked_ignored_and_a_deleted_tracked_file_out_and_keeps_an_untracked_one(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = tracked_ignored_repo(tmp_path / "repo")
    (repo / ".gitignore").write_text("t.txt\nscratch.log\n")
    (repo / "scratch.log").write_text("ignored\n")
    (repo / "fresh.txt").write_text("new\n")
    (repo / "gone.txt").unlink()
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    listed = git_in(repo, "ls-tree", "--name-only", REF).stdout.split()
    assert (code, listed) == (0, [".gitignore", "fresh.txt", "stop-run.sh", "t.txt"])


@pytest.mark.process("real git repository and its index")
def test_leaves_the_callers_index_head_and_branch_untouched_when_the_worktree_holds_a_tracked_ignored_file(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = tracked_ignored_repo(tmp_path / "repo")
    (repo / ".gitignore").write_text("t.txt\n")
    (repo / "t.txt").write_text("edited by the leaf\n")
    (repo / "staged.txt").write_text("staged\n")
    git_in(repo, "add", "staged.txt")

    def state():
        return (git_in(repo, "rev-parse", "HEAD").stdout, git_in(repo, "symbolic-ref", "HEAD").stdout,
                git_in(repo, "ls-files", "-s").stdout)

    before = state()
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert (code, state()) == (0, before)


def no_identity(monkeypatch, tmp_path):
    for name in (*IDENT, "EMAIL"):
        monkeypatch.delenv(name, raising=False)
    config = tmp_path / "noidentity.gitconfig"
    config.write_text("[user]\n\tuseConfigOnly = true\n")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(config))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


@pytest.mark.process("real git repository with no identity in any git config")
def test_writes_the_ref_and_exits_0_with_no_user_name_or_email_in_any_git_config(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    no_identity(monkeypatch, tmp_path)
    code, out, err = run_cli(preserve_attempt, ["409", "3", "develop-green", "1"], cwd=repo)
    assert (code, ref_resolves(repo)) == (0, True)


@pytest.mark.process("real git repository with no identity in any git config")
def test_copies_the_leafs_log_and_output_for_a_mark_with_no_user_name_or_email_in_any_git_config(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    leaf_output(repo, "streamed progress", "final result text")
    no_identity(monkeypatch, tmp_path)
    code, out, err = run_cli(preserve_attempt, ["409", "3", "develop-green", "1", "reject"], cwd=repo)
    copies = repo / ".tdd" / "attempts"
    assert (copies / "3-develop-green-1-reject.log").read_text() == "streamed progress\n"
    assert (copies / "3-develop-green-1-reject.out").read_text() == "final result text\n"


def test_a_symlink_beside_no_scripts_still_finds_the_real_scripts_directory(tmp_path, monkeypatch, preserve_attempt):
    real = os.path.realpath(preserve_attempt.__file__)
    farm = tmp_path.resolve() / "farm" / "veri"
    farm.mkdir(parents=True)
    os.symlink(real, farm / "preserve_attempt.py")
    spec = importlib.util.spec_from_file_location("symlinked_preserve_attempt", farm / "preserve_attempt.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    monkeypatch.chdir(os.path.dirname(os.path.dirname(real)))

    assert loaded.inside_own_scripts() is True
