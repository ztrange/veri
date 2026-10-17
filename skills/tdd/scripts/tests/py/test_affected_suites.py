"""In-process cases for veri/affected_suites.py, the module affected-suites.sh is a shim over."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS

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


def test_main_places_the_ported_counts_check_for_an_added_suite_and_no_longer_the_bash_one(tmp_path, monkeypatch, capsys, affected):
    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"] and "--diff-filter=AD" in args:
            stdout = "skills/tdd/scripts/tests/newbie.test.sh\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "skills/tdd/scripts/tests/newbie.test.sh\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/newbie.test.sh").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/newbie.test.sh\nskills/tdd/scripts/tests/py/unit/test_claude_md_counts.py\n", "")


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


def test_main_maps_a_touched_module_to_its_pytest_file_in_the_fast_tier(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/veri/foo.py"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py/unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/unit/test_foo.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_foo.py\n", "")


def test_main_selects_a_changed_pytest_file_in_the_fast_tier_as_itself(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/tests/py/unit/test_bar.py"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py/unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/unit/test_bar.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_bar.py\n", "")


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


def test_main_prints_the_emitted_text_check_for_a_template_a_suite_names_1622(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_emitted_text.py").write_text("")
    (tests / "unit/names.test.sh").write_text('cat "$scripts/prompts/develop-red.md"\n')
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, ["skills/tdd/scripts/tests/py/unit/test_emitted_text.py", "skills/tdd/scripts/tests/unit/names.test.sh"])


def test_main_prints_the_emitted_text_check_for_a_partial_no_suite_names_1622(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/_shared.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_emitted_text.py").write_text("")
    (tests / "other.test.sh").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_emitted_text.py\n", "")


def test_main_prints_the_emitted_text_check_for_a_prompt_no_suite_names_1024(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/unnamed.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_emitted_text.py").write_text("")
    (tests / "other.test.sh").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_emitted_text.py\n", "")


def test_main_prints_the_four_prompt_renderer_suites_for_a_develop_template_no_suite_names_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    renderers = ["py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py"]
    for name in renderers + ["other.test.sh"]:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in renderers))


def test_main_prints_the_develop_prompt_process_suite_for_a_develop_template_no_suite_names_1338(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    present = ["py/test_build_develop_prompt_process.py"]
    for name in present + ["other.test.sh"]:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in present))


def test_main_prints_the_verify_prompt_process_suite_for_a_verify_template_no_suite_names_1341(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/verify-green.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    present = ["py/test_build_verify_prompt_process.py"]
    for name in present + ["other.test.sh"]:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in present))


def test_main_prints_the_four_prompt_renderer_suites_for_a_verify_template_no_suite_names_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/verify-green.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    renderers = ["py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py"]
    for name in renderers + ["other.test.sh"]:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in renderers))


def test_main_prints_the_four_prompt_renderer_suites_for_a_partial_no_suite_names_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/_leaf-safety.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    renderers = ["py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py"]
    for name in renderers + ["other.test.sh"]:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in renderers))


def test_main_prints_only_the_prompt_renderer_suites_that_exist_for_a_template_change_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    present = ["py/unit/test_build_develop_prompt.py"]
    for name in present + ["other.test.sh"]:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in present))


def test_main_prints_none_of_the_prompt_renderer_suites_for_a_change_outside_the_prompts_directory_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/foo.sh"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    renderers = ["py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py"]
    for name in renderers + ["foo.test.sh"]:
        (tests / name).write_text("")
    (tmp_path / "skills/tdd/scripts/foo.sh").write_text("#!/usr/bin/env bash\n")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, ["skills/tdd/scripts/tests/foo.test.sh"])


def test_main_skips_a_suite_that_names_only_the_lib_of_the_same_name_for_a_script_with_no_suite_1024(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/orphan.sh"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/orphan.sh").write_text("#!/usr/bin/env bash\n")
    (tests / "lib-only.test.sh").write_text('source "$scripts/lib/orphan.sh"\n')
    (tests / "names.test.sh").write_text('"$scripts/orphan.sh"\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/names.test.sh\n", "")


def test_main_prints_the_pytest_files_that_read_the_edited_skill_section_through_the_helper_only(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -2 +2 @@\n-old body\n+alpha body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\n", "")


@pytest.mark.parametrize("fence", ["```", "~~~"])
def test_main_attributes_an_edit_below_a_fenced_heading_shaped_line_to_the_real_enclosing_section_1569(
        fence, tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -4 +4 @@\n-old body\n+alpha body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\n%s\n## x\nalpha body\n%s\n## Beta\nbeta body\n" % (fence, fence))
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\n", "")


def test_main_prints_a_pytest_file_whose_helper_call_spans_lines_with_the_heading_on_its_own(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -2 +2 @@\n-old body\n+alpha body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_alpha.py").write_text('section(\n    SKILL,\n    "## Alpha",\n)\n')
    (py / "test_beta.py").write_text('section(\n    SKILL,\n    "## Beta",\n)\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\n", "")


def test_main_prints_a_fast_tier_pytest_file_that_reads_the_edited_skill_section_or_renders_an_edited_prompt_1633(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"
    touched = {"files": [skill]}

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else "".join(f + "\n" for f in touched["files"])
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -2 +2 @@\n-old body\n+alpha body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    unit = tmp_path / "skills/tdd/scripts/tests/py/unit"
    unit.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (unit / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (unit / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    (unit / "test_whole.py").write_text('text = open("skills/tdd/SKILL.md").read()\n')
    (unit / "test_build_develop_prompt.py").write_text("")
    skill_edit = (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),)
    touched["files"] = ["skills/tdd/scripts/prompts/develop-red.md"]
    prompt_edit = (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),)
    prefix = "skills/tdd/scripts/tests/py/unit/"
    assert (skill_edit, prompt_edit) == (
        (0, [prefix + "test_alpha.py", prefix + "test_whole.py"]),
        (0, [prefix + "test_build_develop_prompt.py"]),
    )


def test_main_prints_a_pytest_file_that_reads_skill_md_without_the_helper_on_any_skill_edit(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -2 +2 @@\n-old body\n+alpha body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    (py / "test_whole.py").write_text('text = open("skills/tdd/SKILL.md").read()\n')
    (py / "test_other.py").write_text('text = open("README.md").read()\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\nskills/tdd/scripts/tests/py/test_whole.py\n", "")


def test_main_prints_every_pytest_file_reading_skill_md_when_the_edit_spans_more_than_one_section(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -2 +2 @@\n-old body\n+alpha body\n@@ -4 +4 @@\n-old body\n+beta body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n## Gamma\ngamma body\n")
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    (py / "test_gamma.py").write_text('section(SKILL, "## Gamma")\n')
    (py / "test_whole.py").write_text('text = open("skills/tdd/SKILL.md").read()\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\nskills/tdd/scripts/tests/py/test_beta.py\n"
        "skills/tdd/scripts/tests/py/test_gamma.py\nskills/tdd/scripts/tests/py/test_whole.py\n", "")


def test_main_prints_a_pytest_file_that_names_the_edited_heading_outside_the_helper_call_1581(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -2 +2 @@\n-old body\n+alpha body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_a_param.py").write_text(
        '@pytest.mark.parametrize("heading", ["## Alpha", "## Gamma"])\n'
        "def test_x(heading):\n    section(SKILL, heading)\n")
    (py / "test_b_bound.py").write_text('heading = "## Alpha"\nsection(SKILL, heading)\n')
    (py / "test_c_beta.py").write_text('heading = "## Beta"\nsection(SKILL, heading)\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_a_param.py\nskills/tdd/scripts/tests/py/test_b_bound.py\n"
        "skills/tdd/scripts/tests/py/test_c_beta.py\n", "")


def test_main_prints_a_pytest_file_that_passes_the_helper_a_heading_it_never_spells(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -2 +2 @@\n-old body\n+alpha body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_computed.py").write_text('heading = "#" * 2 + " Al" + "pha"\nsection(SKILL, heading)\n')
    (py / "test_literal_beta.py").write_text('section(SKILL, "## Beta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_computed.py\n", "")


@pytest.mark.parametrize("direct_read", [
    'open("skills/tdd/SKILL.md").read()',
    'Path("skills/tdd/SKILL.md").read_text()',
])
def test_main_prints_a_pytest_file_that_reads_skill_md_directly_and_also_calls_the_helper_on_a_section_it_does_not_name(
        tmp_path, monkeypatch, capsys, affected, direct_read):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -2 +2 @@\n-old body\n+alpha body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_both.py").write_text("text = " + direct_read + '\nsection(SKILL, "## Beta")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\nskills/tdd/scripts/tests/py/test_both.py\n", "")


def test_main_narrows_a_pytest_file_with_only_literal_heading_calls_to_the_sections_it_names_1581(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -6 +6 @@\n-old body\n+gamma body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n## Gamma\ngamma body\n")
    (py / "test_alpha_gamma.py").write_text('section(SKILL, "## Alpha")\nsection(SKILL, "## Gamma")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha_gamma.py\n", "")


def test_main_prints_a_pytest_file_with_a_literal_and_a_built_heading_for_an_edit_in_a_section_neither_names_1581(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -4 +4 @@\n-old body\n+beta body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_mixed.py").write_text('section(SKILL, "## Alpha")\nsection(SKILL, "## " + "Be" + "ta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_mixed.py\n", "")


def test_main_prints_a_pytest_file_with_a_literal_and_an_expression_heading_for_an_edit_in_a_section_no_literal_names_1581(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -4 +4 @@\n-old body\n+beta body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_expr.py").write_text('section(SKILL, "## Alpha")\nsection(SKILL, h.strip())\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_expr.py\n", "")


def test_main_prints_a_pytest_file_importing_the_section_helper_under_another_name_for_an_edit_in_a_section_its_literal_does_not_name_1581(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -4 +4 @@\n-old body\n+beta body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_alias.py").write_text(
        'from helpers import section as sec\nsec(SKILL, "## Alpha")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alias.py\n", "")


@pytest.mark.parametrize("read", [
    'open("fixture.json").read()',
    'pathlib.Path("fixture.json").read_text()',
    'pathlib.Path("fixture.json").read_bytes()',
])
def test_main_prints_a_pytest_file_with_a_literal_heading_and_an_unrelated_file_read_for_an_edit_in_a_section_the_call_does_not_name_1581(
        tmp_path, monkeypatch, capsys, affected, read):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -4 +4 @@\n-old body\n+beta body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_open.py").write_text('section(SKILL, "## Alpha")\ndata = %s\n' % read)
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_open.py\n", "")


def spelled_suites_missing(source, tests):
    import re
    spelled = sorted(set(re.findall(r'["/]((?:unit/|py/)?[\w-]+\.test\.sh|(?:py/(?:unit/)?)?test_\w+\.py)"', source)))
    return spelled, [p for p in spelled if not (tests / p).is_file()]


def test_every_suite_path_affected_suites_names_exists():
    """Its subject is source text: the suite paths veri/affected_suites.py spells."""
    spelled, missing = spelled_suites_missing((SCRIPTS / "veri" / "affected_suites.py").read_text(encoding="utf-8"), SCRIPTS / "tests")
    assert spelled and missing == [], "affected_suites.py names suites that are not files: %s" % ", ".join(missing)


@pytest.mark.parametrize("rename", [
    ('"py/unit/test_build_develop_prompt.py"', '"py/unit/test_build_gone_prompt.py"'),
    ('/tests/py/unit/test_claude_md_counts.py"', '/tests/py/unit/test_claude_md_gone.py"'),
])
def test_the_suite_path_check_names_a_renderer_or_tests_path_planted_into_a_copy_of_affected_suites_that_is_not_a_file(rename):
    """Its subject is source text: a copy of veri/affected_suites.py's source with one suite path renamed to a file that does not exist."""
    source = (SCRIPTS / "veri" / "affected_suites.py").read_text(encoding="utf-8")
    assert source.count(rename[0]) == 1
    _, missing = spelled_suites_missing(source.replace(rename[0], rename[1]), SCRIPTS / "tests")
    assert missing == [rename[1].strip('"/').removeprefix("tests/")]
