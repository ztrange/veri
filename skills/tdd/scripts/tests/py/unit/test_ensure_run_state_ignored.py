"""In-process cases for veri/ensure_run_state_ignored.py, the module ensure-run-state-ignored.sh is a shim over."""
import importlib
import pathlib
import subprocess

import pytest

from conftest import SCRIPTS

RULE = (".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-*.md\n!.tdd/issue-*-added.md\n"
        "!.tdd/issue-*-refactor-owed.md\n!.tdd/issue-*-metrics.md\n")


@pytest.fixture
def ensure_run_state_ignored():
    return importlib.import_module("veri.ensure_run_state_ignored")


def fake_rev_parse(fake_processes, code, stdout):
    """subprocess.run answering `git -C <root> rev-parse --git-common-dir` with <code> and <stdout>."""
    def rev_parse(line, **kwargs):
        words = line.split()
        if words[:2] != ["git", "-C"] or words[3:] != ["rev-parse", "--git-common-dir"]:
            raise AssertionError("unexpected command: %s" % line)
        return code, stdout if kwargs.get("stdout") == subprocess.PIPE else None, None

    return fake_processes.answers({"git": rev_parse})


def test_main_adds_the_rule_to_both_files_and_returns_2_when_rev_parse_fails(tmp_path, monkeypatch, capsys,
                                                                              ensure_run_state_ignored, fake_processes):
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    fake_rev_parse(fake_processes, 0, ".git\n")

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (0, ("added\n", ""))
    assert (root / ".gitignore").read_text() == RULE
    assert (root / ".git" / "info" / "exclude").read_text() == RULE

    broken = tmp_path / "broken"
    (broken / ".git").mkdir(parents=True)
    fake_rev_parse(fake_processes, 128, "")

    assert ensure_run_state_ignored.main([str(broken)]) == 2
    assert not (broken / ".gitignore").exists()
    assert not (broken / ".git" / "info" / "exclude").exists()


def test_main_does_not_refuse_a_gitignore_holding_other_lines_but_not_the_rules_last_line(tmp_path, monkeypatch, capsys,
                                                                                     ensure_run_state_ignored, fake_processes):
    fake_rev_parse(fake_processes, 0, ".git\n")
    for name, original in (("node_modules", b"node_modules/\n"), ("non_utf8", b"\xff\xfe\n")):
        root = tmp_path / name
        (root / ".git").mkdir(parents=True)
        (root / ".gitignore").write_bytes(original)

        code = ensure_run_state_ignored.main([str(root)])

        assert (code, capsys.readouterr()[:]) == (0, ("added\n", ""))
        assert (root / ".gitignore").read_bytes() == original + RULE.encode()


def test_4338_an_unrelated_gitignore_gains_exactly_the_run_state_lines_veris_own_gitignore_carries(
        tmp_path, capsys, ensure_run_state_ignored, fake_processes):
    main_lines = [line for line in (SCRIPTS.parents[2] / ".gitignore").read_text().splitlines()
                  if line.startswith((".tdd/", "!.tdd/"))]
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    (root / ".gitignore").write_bytes(b"node_modules/\n")
    fake_rev_parse(fake_processes, 0, ".git\n")

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr().out) == (0, "added\n")
    assert (root / ".gitignore").read_text().splitlines() == ["node_modules/", *main_lines]


def test_main_refuses_a_gitignore_holding_only_the_rules_last_line(tmp_path, monkeypatch, capsys, ensure_run_state_ignored, fake_processes):
    root = tmp_path / "repo"
    (root / ".git" / "info").mkdir(parents=True)
    (root / ".gitignore").write_bytes(b"!.tdd/issue-*-metrics.md\n")
    (root / ".git" / "info" / "exclude").write_bytes(b"")
    fake_rev_parse(fake_processes, 0, ".git\n")

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (2, ("", "ensure-run-state-ignored: %s/.gitignore carries veri's run-state "
                                                      "rule only in part, or with its lines out of order — fix it by "
                                                      "hand\n" % root))
    assert (root / ".gitignore").read_bytes() == b"!.tdd/issue-*-metrics.md\n"
    assert (root / ".git" / "info" / "exclude").read_bytes() == b""


def test_main_reports_already_present_from_the_gitignore_alone_and_leaves_both_files_on_a_second_run(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored, fake_processes):
    fake_rev_parse(fake_processes, 0, ".git\n")
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    assert ensure_run_state_ignored.main([str(root)]) == 0
    capsys.readouterr()

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (0, ("already present\n", ""))
    assert (root / ".gitignore").read_text() == RULE
    assert (root / ".git" / "info" / "exclude").read_text() == RULE

    carried = tmp_path / "carried"
    (carried / ".git" / "info").mkdir(parents=True)
    (carried / ".gitignore").write_text(RULE)
    (carried / ".git" / "info" / "exclude").write_text("")

    code = ensure_run_state_ignored.main([str(carried)])

    assert (code, capsys.readouterr()[:]) == (0, ("already present\n", ""))
    assert (carried / ".gitignore").read_text() == RULE
    assert (carried / ".git" / "info" / "exclude").read_text() == RULE


def test_4741_the_rule_names_no_mutations_file(ensure_run_state_ignored):
    assert [line for line in ensure_run_state_ignored.RULE if "mutations" in line] == []


def test_4741_a_gitignore_carrying_the_rule_with_the_retired_mutations_line_is_already_present(
        tmp_path, capsys, ensure_run_state_ignored, fake_processes):
    fake_rev_parse(fake_processes, 0, ".git\n")
    retired = RULE.replace("!.tdd/issue-*-added.md\n", "!.tdd/issue-*-added.md\n!.tdd/issue-*-mutations.md\n")
    root = tmp_path / "repo"
    (root / ".git" / "info").mkdir(parents=True)
    (root / ".gitignore").write_text(retired)
    (root / ".git" / "info" / "exclude").write_text(retired)

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (0, ("already present\n", ""))
    assert (root / ".gitignore").read_text() == retired
    assert (root / ".git" / "info" / "exclude").read_text() == retired

def test_main_appends_after_a_newline_only_where_one_is_missing_and_refuses_a_misordered_rule(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored, fake_processes):
    fake_rev_parse(fake_processes, 0, ".git\n")
    appended = (
        ("newline_terminated", b"node_modules/\n", b"node_modules/\n"),
        ("misordered", b".tdd/*\n!.tdd/issue-*-metrics.md\n!.tdd/issue-*.md\n.tdd/issue-*-*.md\n!.tdd/issue-*-added.md\n"
                       b"!.tdd/issue-*-refactor-owed.md\n", None),
        ("no_trailing_newline", b"node_modules/", b"node_modules/\n"),
        ("crlf", b"node_modules/\r\n", b"node_modules/\r\n"),
        ("empty", b"", b""),
        ("trailing_space", RULE.encode()[:-1] + b" \n", RULE.encode()[:-1] + b" \n"),
        ("trailing_cr", RULE.replace("\n", "\r\n").encode(), RULE.replace("\n", "\r\n").encode()),
        ("ignore_all_only", b".tdd/*\n", b".tdd/*\n"),
    )
    for name, original, before_rule in appended:
        root = tmp_path / name
        (root / ".git").mkdir(parents=True)
        (root / ".gitignore").write_bytes(original)
        if before_rule is None:
            (root / ".git" / "info").mkdir()
            (root / ".git" / "info" / "exclude").write_bytes(b"")

        code = ensure_run_state_ignored.main([str(root)])

        if before_rule is None:
            assert (name, code, capsys.readouterr()[:]) == (name, 2, (
                "", "ensure-run-state-ignored: %s/.gitignore carries veri's run-state rule only in part, or with its "
                    "lines out of order — fix it by hand\n" % root))
            assert (root / ".gitignore").read_bytes() == original
            assert (root / ".git" / "info" / "exclude").read_bytes() == b""
        else:
            assert (name, code, capsys.readouterr()[:]) == (name, 0, ("added\n", ""))
            assert (name, (root / ".gitignore").read_bytes()) == (name, before_rule + RULE.encode())
            assert (name, (root / ".git" / "info" / "exclude").read_bytes()) == (name, RULE.encode())


def test_main_builds_paths_by_concatenation_checks_gitignore_then_exclude_and_writes_exclude_first(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored, fake_processes):
    refusal = ("ensure-run-state-ignored: %s carries veri's run-state rule only in part, or with its lines out of "
               "order — fix it by hand\n")
    fakes = []

    def answer(stdout):
        fakes.append(fake_rev_parse(fake_processes, 0, stdout))

    monkeypatch.chdir(tmp_path)
    common = tmp_path / "common"
    (common / "info").mkdir(parents=True)
    (common / "info" / "exclude").write_bytes(b"!.tdd/issue-*-metrics.md\n")
    pathlib.Path("a").mkdir()
    answer(str(common) + "\n")
    assert (ensure_run_state_ignored.main(["a"]), capsys.readouterr()[:]) == (2, ("", refusal % (str(common) +
                                                                                                "/info/exclude")))
    assert not pathlib.Path("a/.gitignore").exists()

    pathlib.Path("r/sub").mkdir(parents=True)
    pathlib.Path("r/.git/info").mkdir(parents=True)
    pathlib.Path("r/.git/info/exclude").write_bytes(b"!.tdd/issue-*-metrics.md\n")
    pathlib.Path("r/.gitignore").write_bytes(b"!.tdd/issue-*-metrics.md\n")
    answer(".git\n")
    assert (ensure_run_state_ignored.main(["r/"]), capsys.readouterr()[:]) == (2, ("", refusal % "r//.gitignore"))
    answer("../.git\n")
    assert (ensure_run_state_ignored.main(["r/sub", "--bogus", "x"]), capsys.readouterr()[:]) == (
        2, ("", refusal % "r/sub/../.git/info/exclude"))
    assert not pathlib.Path("r/sub/.gitignore").exists()
    assert pathlib.Path("r/.git/info/exclude").read_bytes() == b"!.tdd/issue-*-metrics.md\n"

    monkeypatch.chdir(tmp_path / "r")
    answer(".git\n")
    for argv in ([""], []):
        assert (ensure_run_state_ignored.main(argv), capsys.readouterr()[:]) == (2, ("", refusal % "./.gitignore"))
    roots = [argv[2] for fake in fakes for argv in fake.argvs]
    assert roots == ["a", "r/", "r/sub", ".", "."]

    monkeypatch.chdir(tmp_path)
    pathlib.Path("w/.gitignore").mkdir(parents=True)
    answer(".git\n")
    assert ensure_run_state_ignored.main(["w"]) == 2
    assert not pathlib.Path("w/.git/info/exclude").exists()

    patched = "monkeypatch.setattr(" + "ensure_run_state_ignored"
    assert patched not in pathlib.Path(__file__).read_text()


def test_main_leaves_info_exclude_byte_identical_and_returns_2_when_the_gitignore_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored, fake_processes):
    root = tmp_path / "repo"
    (root / ".git" / "info").mkdir(parents=True)
    (root / ".git" / "info" / "exclude").write_bytes(b"*.swp\n")
    (root / ".gitignore").mkdir()
    fake_rev_parse(fake_processes, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__

    assert ((root / ".git" / "info" / "exclude").read_bytes(), outcome) == (b"*.swp\n", 2)


def test_main_leaves_gitignore_byte_identical_and_fails_on_stderr_when_the_info_exclude_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored, fake_processes):
    root = tmp_path / "repo"
    (root / ".git" / "info" / "exclude").mkdir(parents=True)
    (root / ".gitignore").write_bytes(b"node_modules/\n")
    fake_rev_parse(fake_processes, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__
    stderr = capsys.readouterr().err

    assert ((root / ".gitignore").read_bytes(), isinstance(outcome, int) and outcome != 0,
            stderr.startswith("ensure-run-state-ignored: ") and "info/exclude" in stderr) == (
        b"node_modules/\n", True, True)


def test_main_leaves_no_gitignore_and_fails_on_stderr_when_there_was_none_and_the_info_exclude_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored, fake_processes):
    root = tmp_path / "repo"
    (root / ".git" / "info" / "exclude").mkdir(parents=True)
    fake_rev_parse(fake_processes, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__
    stderr = capsys.readouterr().err

    assert ((root / ".gitignore").exists(), isinstance(outcome, int) and outcome != 0,
            stderr.startswith("ensure-run-state-ignored: ") and "info/exclude" in stderr) == (
        False, True, True)


def test_main_leaves_a_gitignore_already_carrying_the_rule_byte_identical_when_the_info_exclude_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored, fake_processes):
    root = tmp_path / "repo"
    (root / ".git" / "info" / "exclude").mkdir(parents=True)
    carried = b"node_modules/\n" + RULE.encode()
    (root / ".gitignore").write_bytes(carried)
    fake_rev_parse(fake_processes, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__
    stderr = capsys.readouterr().err
    after = (root / ".gitignore").read_bytes() if (root / ".gitignore").exists() else None

    assert (after, isinstance(outcome, int) and outcome != 0,
            stderr.startswith("ensure-run-state-ignored: ") and "info/exclude" in stderr) == (
        carried, True, True)


def test_main_returns_2_when_the_info_exclude_write_fails_as_when_the_gitignore_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored, fake_processes):
    root = tmp_path / "repo"
    (root / ".git" / "info" / "exclude").mkdir(parents=True)
    fake_rev_parse(fake_processes, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__

    assert outcome == 2


def test_a_gitignore_that_is_a_directory_exits_2_says_why_on_stderr_and_leaves_info_exclude_unchanged(
        tmp_path, monkeypatch, run_cli, ensure_run_state_ignored, fake_processes):
    root = tmp_path / "repo"
    (root / ".git" / "info").mkdir(parents=True)
    (root / ".git" / "info" / "exclude").write_bytes(b"*.swp\n")
    (root / ".gitignore").mkdir()
    fake_rev_parse(fake_processes, 0, ".git\n")

    code, out, err = run_cli(ensure_run_state_ignored, [str(root)])

    assert (code, out, err != "") == (2, "", True)
    assert (root / ".git" / "info" / "exclude").read_bytes() == b"*.swp\n"


def test_a_symlink_beside_no_scripts_still_finds_the_real_scripts_directory(tmp_path, capsys):
    import importlib.util
    import os
    farm = tmp_path.resolve() / "farm" / "veri"
    farm.mkdir(parents=True)
    os.symlink(SCRIPTS / "veri" / "ensure_run_state_ignored.py", farm / "ensure_run_state_ignored.py")
    spec = importlib.util.spec_from_file_location("symlinked_ensure_run_state_ignored",
                                                  farm / "ensure_run_state_ignored.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)

    assert (loaded.main([str(SCRIPTS)]), capsys.readouterr().err) == (
        2, "ensure-run-state-ignored: name the target repository, not the skill's own scripts directory\n")
