"""In-process cases for veri/affected_suites.py, the module affected-suites.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: affected-suites.sh <base>..<head>\n"


@pytest.fixture
def affected():
    return importlib.import_module("veri.affected_suites")


def test_main_returns_2_with_the_usage_line_for_no_argument_and_names_an_unresolvable_base(
        monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", lambda args, **kwargs: subprocess.CompletedProcess(args, 1, "", ""))
    missing = (affected.main([]),) + tuple(capsys.readouterr())
    unresolvable = (affected.main(["no-range"]),) + tuple(capsys.readouterr())
    assert (missing, unresolvable) == (
        (2, "", USAGE),
        (2, "", "affected-suites: cannot resolve revision 'no-range'\n" + USAGE),
    )


def test_main_treats_an_empty_argument_as_missing(capsys, affected):
    assert (affected.main([""]),) + tuple(capsys.readouterr()) == (2, "", USAGE)


def test_main_prints_the_suite_of_a_touched_script_and_returns_0(tmp_path, monkeypatch, capsys, affected):
    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"] and "--diff-filter=AD" in args:
            stdout = ""
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "skills/tdd/scripts/foo.sh\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/foo.sh").write_text("#!/usr/bin/env bash\n")
    (tmp_path / "skills/tdd/scripts/tests/foo.test.sh").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/foo.test.sh\n", "")


def fake_git(touched, diff_code=0):
    def run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(args, 0, "abc\n", "")
        if list(args[:3]) == ["git", "diff", "--name-only"] and "--diff-filter=AD" in args:
            return subprocess.CompletedProcess(args, 0, "", "")
        if list(args[:3]) == ["git", "diff", "--name-only"]:
            return subprocess.CompletedProcess(args, diff_code, "".join(f + "\n" for f in touched), "")
        raise AssertionError("unexpected command: %r" % (args,))
    return run


@pytest.mark.parametrize("diff_code, returned", [(1, 1), (128, 2)])
def test_main_returns_a_failed_git_diff_status_mapped_into_0_to_3(
        tmp_path, monkeypatch, capsys, affected, diff_code, returned):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/foo.sh"], diff_code))
    monkeypatch.chdir(tmp_path)
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (returned, "", "")


def test_main_keeps_the_suffix_of_a_script_named_only_by_its_suffix(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/.sh"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/.sh.test.sh").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/.sh.test.sh\n", "")


def test_main_skips_a_directory_named_like_a_suite_when_reading_suites(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["CLAUDE.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "dir.test.sh").mkdir(parents=True)
    (tests / "names.test.sh").write_text('cat "$root/CLAUDE.md"\n')
    assert affected.main(["base..head"]) == 0
    assert capsys.readouterr().out == "skills/tdd/scripts/tests/names.test.sh\n"


def test_main_widens_to_every_suite_file_but_not_a_directory_named_like_one(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["README.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit/dir.test.sh").mkdir(parents=True)
    (tests / "a.test.sh").write_text("")
    (tests / "unit/b.test.sh").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0,
        "skills/tdd/scripts/tests/a.test.sh\nskills/tdd/scripts/tests/unit/b.test.sh\n",
        "affected-suites: no rule places README.md; widening to every suite\n")


def test_main_skips_a_directory_named_like_a_script_when_reading_lib_callers(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/lib/x.sh"]))
    monkeypatch.chdir(tmp_path)
    scripts = tmp_path / "skills/tdd/scripts"
    (scripts / "dir.sh").mkdir(parents=True)
    (scripts / "user.sh").write_text('source "$here/lib/x.sh"\n')
    (scripts / "tests").mkdir()
    (scripts / "tests/user.test.sh").write_text("")
    assert affected.main(["base..head"]) == 0
    assert capsys.readouterr().out == "skills/tdd/scripts/tests/user.test.sh\n"


def test_main_prints_a_unit_suite_that_names_a_changed_prompt_1024(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    unit = tmp_path / "skills/tdd/scripts/tests/unit"
    unit.mkdir(parents=True)
    (unit / "names.test.sh").write_text('cat "$scripts/prompts/develop-red.md"\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/unit/names.test.sh\n", "")


def test_main_prints_a_unit_suite_that_alone_names_a_changed_fixture_1024(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/tests/fixtures/sample.txt"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "other.test.sh").write_text("")
    (tests / "unit/names.test.sh").write_text('cat "$here/../fixtures/sample.txt"\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/unit/names.test.sh\n", "")


def test_main_prints_a_unit_suite_that_alone_names_a_script_with_no_suite_of_its_own_1024(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/orphan.sh"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/orphan.sh").write_text("#!/usr/bin/env bash\n")
    (tests / "other.test.sh").write_text("")
    (tests / "unit/names.test.sh").write_text('source "$scripts/orphan.sh"\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/unit/names.test.sh\n", "")


def test_main_prints_the_emitted_text_suite_for_a_prompt_no_suite_names_1024(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/unnamed.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "other.test.sh").write_text("")
    (tests / "unit/emitted-text.test.sh").write_text('cksum < "$out"\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/unit/emitted-text.test.sh\n", "")
