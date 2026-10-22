"""In-process cases for veri/affected_suites.py, the module affected-suites.sh is a shim over."""
import importlib
import subprocess

import pytest

from conftest import ROOT, SCRIPTS

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
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_skill_conductor_launch.py").write_text('README = ROOT / "README.md"\n')
    (tests / "py/unit/test_skill_commit.py").write_text('README = parents[6] / "README.md"\n')
    (tests / "py/unit/test_other.py").write_text('text = open("CONTRIBUTING.md").read()\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0,
        "skills/tdd/scripts/tests/py/unit/test_skill_commit.py\n"
        "skills/tdd/scripts/tests/py/unit/test_skill_conductor_launch.py\n",
        "")


def test_main_widens_a_file_no_rule_handles_to_every_bash_suite_file_and_not_a_directory_named_like_one_1812(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["docs/notes.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit/dir.test.sh").mkdir(parents=True)
    (tests / "dir2.test.sh").mkdir()
    (tests / "a.test.sh").write_text("")
    (tests / "unit/b.test.sh").write_text("")
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_other.py").write_text("")
    (tests / "py/test_top.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0,
        "skills/tdd/scripts/tests/py/test_top.py\n"
        "skills/tdd/scripts/tests/py/unit/test_other.py\n",
        "affected-suites: no rule places docs/notes.md; widening to every suite\n")


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


def test_main_keeps_a_longer_fence_open_past_a_shorter_fence_line_when_attributing_an_edit_1687(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -5 +5 @@\n-old body\n+alpha body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\n````\n```\n## x\nalpha body\n````\n## Beta\nbeta body\n")
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_x.py").write_text('section(SKILL, "## x")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\n", "")


def test_main_reads_a_heading_after_a_fence_line_indented_four_spaces_as_a_heading_1687(
        tmp_path, monkeypatch, capsys, affected):
    skill = "skills/tdd/SKILL.md"

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            stdout = "abc\n"
        elif list(args[:3]) == ["git", "diff", "--name-only"]:
            stdout = "" if "--diff-filter=AD" in args else skill + "\n"
        elif list(args[:3]) == ["git", "diff", "-U0"]:
            stdout = "@@ -5 +5 @@\n-old body\n+beta body\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\n    ```\n## Beta\nx\nbeta body\n## Gamma\n")
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_beta.py\n", "")


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


SCRIPTS_REL = "skills/tdd/scripts/"
SUITES = SCRIPTS_REL + "tests/"


def cli_git(touched, unresolvable=None, counted=()):
    def run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            bad = unresolvable is not None and unresolvable in args[-1]
            return subprocess.CompletedProcess(args, 1 if bad else 0, "" if bad else "abc\n", "")
        if list(args[:3]) == ["git", "diff", "--name-only"] and "--diff-filter=AD" in args:
            return subprocess.CompletedProcess(args, 0, "".join(f + "\n" for f in counted), "")
        if list(args[:3]) == ["git", "diff", "--name-only"]:
            return subprocess.CompletedProcess(args, 0, "".join(f + "\n" for f in touched), "")
        if list(args[:3]) == ["git", "diff", "-U0"]:
            return subprocess.CompletedProcess(args, 1, "", "")
        raise AssertionError("unexpected command: %r" % (args,))
    return run


def plant(root, files):
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)


def affected_by(monkeypatch, run_cli, affected, tmp_path, touched, files, range_="base..head", counted=()):
    monkeypatch.setattr(subprocess, "run", cli_git(touched, counted=counted))
    plant(tmp_path, files)
    return run_cli(affected, [range_], cwd=tmp_path)


def test_resolvable_range_prints_one_suite_per_line_sorted_with_no_duplicate(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path,
        [SCRIPTS_REL + "wolf.sh", SCRIPTS_REL + "zulu.sh", SCRIPTS_REL + "tests/wolf.test.sh"],
        {SCRIPTS_REL + "zulu.sh": "zulu\n", SCRIPTS_REL + "wolf.sh": "wolf\n",
         SCRIPTS_REL + "tests/wolf.test.sh": "", SCRIPTS_REL + "tests/unit/zulu.test.sh": ""},
    ) == (0, SUITES + "unit/zulu.test.sh\n" + SUITES + "wolf.test.sh\n", "")


def test_malformed_range_exits_2_with_the_usage_line(monkeypatch, run_cli, affected, tmp_path):
    results = []
    for range_ in ("abc..no-such-rev", "no-such-rev..abc"):
        monkeypatch.setattr(subprocess, "run", cli_git([], unresolvable="no-such-rev"))
        results.append(run_cli(affected, [range_], cwd=tmp_path))
    refusal = (2, "", "affected-suites: cannot resolve revision 'no-such-rev'\n" + USAGE)
    assert results == [refusal, refusal]


def test_empty_diff_exits_3_and_prints_nothing(monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(monkeypatch, run_cli, affected, tmp_path, [], {}) == (3, "", "")


def test_rule_1_a_script_prints_exactly_its_same_named_suite(monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "foo.sh"],
        {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         SCRIPTS_REL + "tests/foo.test.sh": "", SCRIPTS_REL + "tests/bar.test.sh": ""},
    ) == (0, SUITES + "foo.test.sh\n", "")


def test_rule_1_a_script_prints_exactly_its_same_named_suite_under_tests_unit(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "foo.sh"],
        {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         SCRIPTS_REL + "tests/unit/foo.test.sh": "", SCRIPTS_REL + "tests/bar.test.sh": ""},
    ) == (0, SUITES + "unit/foo.test.sh\n", "")


def test_a_script_with_no_same_named_suite_prints_no_path_that_does_not_exist_1011(
        monkeypatch, run_cli, affected, tmp_path):
    code, out, _ = affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "runner.sh"],
        {SCRIPTS_REL + "runner.sh": "run\n",
         SCRIPTS_REL + "tests/runner-venv.test.sh": 'RUN="$HERE/../runner.sh"\n'})
    assert (code in (0, 3), [p for p in out.splitlines() if not (tmp_path / p).exists()]) == (True, [])


def test_a_script_with_no_same_named_suite_prints_the_existing_suites_that_name_its_file_1011(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "runner.sh"],
        {SCRIPTS_REL + "runner.sh": "run\n", SCRIPTS_REL + "gamma.sh": "gamma\n",
         SCRIPTS_REL + "tests/runner-venv.test.sh": 'RUN="$HERE/../runner.sh"\n',
         SCRIPTS_REL + "tests/gamma.test.sh": 'GAMMA="$HERE/../gamma.sh"\n'},
    ) == (0, SUITES + "runner-venv.test.sh\n", "")


def test_rule_2_a_lib_prints_the_suite_of_every_script_that_sources_it_and_no_others(
        monkeypatch, run_cli, affected, tmp_path):
    sourcing = '#!/usr/bin/env bash\nsource "$HERE/lib/bar.sh"\n'
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { :; }\n",
         SCRIPTS_REL + "alpha.sh": sourcing, SCRIPTS_REL + "beta.sh": sourcing,
         SCRIPTS_REL + "gamma.sh": "echo gamma\n", SCRIPTS_REL + "bar.sh": "echo bar\n",
         **{SCRIPTS_REL + "tests/%s.test.sh" % n: "" for n in ("alpha", "beta", "gamma", "bar")}},
    ) == (0, SUITES + "alpha.test.sh\n" + SUITES + "beta.test.sh\n", "")


def test_rule_3_a_changed_suite_prints_exactly_itself(monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "tests/foo.test.sh"],
        {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         SCRIPTS_REL + "tests/foo.test.sh": "", SCRIPTS_REL + "tests/bar.test.sh": ""},
    ) == (0, SUITES + "foo.test.sh\n", "")


def test_rule_3_a_changed_fixture_prints_every_suite_that_references_it_by_name(
        monkeypatch, run_cli, affected, tmp_path):
    plan = 'cat "$HERE/fixtures/plan.md"\n'
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "tests/fixtures/plan.md"],
        {SCRIPTS_REL + "tests/fixtures/plan.md": "# plan\n", SCRIPTS_REL + "tests/fixtures/other.md": "# other\n",
         SCRIPTS_REL + "tests/alpha.test.sh": plan, SCRIPTS_REL + "tests/beta.test.sh": plan,
         SCRIPTS_REL + "tests/gamma.test.sh": 'cat "$HERE/fixtures/other.md"\n'},
    ) == (0, SUITES + "alpha.test.sh\n" + SUITES + "beta.test.sh\n", "")


def test_rule_4_skill_md_claude_md_and_makefile_print_their_guard_suites(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, ["CLAUDE.md", "skills/tdd/SKILL.md", "Makefile"],
        {"CLAUDE.md": "# veri\n", "skills/tdd/SKILL.md": "# tdd\n", "Makefile": "test:\n",
         SCRIPTS_REL + "gamma.sh": "gamma\n",
         SCRIPTS_REL + "tests/claude-md-guard.test.sh": 'claude_md="CLAUDE.md"\n',
         SCRIPTS_REL + "tests/skill-md-guard.test.sh": 'skill_md="skills/tdd/SKILL.md"\n',
         SCRIPTS_REL + "tests/makefile-guard.test.sh": 'MAKEFILE="$ROOT/Makefile"\n',
         SCRIPTS_REL + "tests/gamma.test.sh": "echo gamma\n"},
    ) == (0, SUITES + "claude-md-guard.test.sh\n" + SUITES + "makefile-guard.test.sh\n"
          + SUITES + "skill-md-guard.test.sh\n", "")


def test_rule_5_a_rule_1_file_plus_a_file_no_rule_matches_prints_every_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "foo.sh", "docs/notes.md"],
        {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "baz.sh": "baz\n",
         SCRIPTS_REL + "tests/foo.test.sh": "", SCRIPTS_REL + "tests/bar.test.sh": "",
         SCRIPTS_REL + "tests/unit/baz.test.sh": "", "docs/notes.md": "# notes\n",
         SCRIPTS_REL + "tests/py/test_foo.py": "", SCRIPTS_REL + "tests/py/unit/test_baz.py": ""},
    ) == (0, SCRIPTS_REL + "tests/py/test_foo.py\n" + SCRIPTS_REL + "tests/py/unit/test_baz.py\n",
          "affected-suites: no rule places docs/notes.md; widening to every suite\n")


def test_rule_5_a_diff_touching_only_files_rules_1_to_4_match_never_falls_back_to_the_full_suite(
        monkeypatch, run_cli, affected, tmp_path):
    sourcing = '#!/usr/bin/env bash\nsource "$HERE/lib/bar.sh"\n'
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path,
        [SCRIPTS_REL + "foo.sh", SCRIPTS_REL + "lib/bar.sh", SCRIPTS_REL + "tests/fixtures/plan.md", "CLAUDE.md"],
        {"CLAUDE.md": "# veri\n", SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "lib/bar.sh": "bar_fn() { :; }\n",
         SCRIPTS_REL + "alpha.sh": sourcing, SCRIPTS_REL + "beta.sh": "beta\n",
         SCRIPTS_REL + "gamma.sh": "gamma\n", SCRIPTS_REL + "zeta.sh": "zeta\n",
         SCRIPTS_REL + "tests/fixtures/plan.md": "# plan\n",
         SCRIPTS_REL + "tests/foo.test.sh": "", SCRIPTS_REL + "tests/alpha.test.sh": "",
         SCRIPTS_REL + "tests/beta.test.sh": 'cat "$HERE/fixtures/plan.md"\n',
         SCRIPTS_REL + "tests/claude-md-guard.test.sh": 'claude_md="CLAUDE.md"\n',
         SCRIPTS_REL + "tests/gamma.test.sh": "", SCRIPTS_REL + "tests/unit/zeta.test.sh": ""},
    ) == (0, suites("alpha.test.sh", "beta.test.sh", "claude-md-guard.test.sh", "foo.test.sh"), "")


def test_rule_6_a_change_to_the_prompt_prompts_develop_red_md_prints_every_suite_that_names_it_and_no_others(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "prompts/develop-red.md"],
        {SCRIPTS_REL + "prompts/develop-red.md": "# red\n", SCRIPTS_REL + "prompts/develop-green.md": "# green\n",
         SCRIPTS_REL + "tests/alpha.test.sh": 'cat "$HERE/../prompts/develop-red.md"\n',
         SCRIPTS_REL + "tests/beta.test.sh": 'cat "$HERE/../prompts/develop-green.md"\n',
         SCRIPTS_REL + "tests/gamma.test.sh": ""},
    ) == (0, suites("alpha.test.sh"), "")


def test_rule_6_a_prompt_and_a_suite_in_one_range_print_that_suite_and_the_prompts_suites_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path,
        [SCRIPTS_REL + "prompts/develop-red.md", SCRIPTS_REL + "tests/delta.test.sh"],
        {SCRIPTS_REL + "prompts/develop-red.md": "# red\n",
         SCRIPTS_REL + "tests/alpha.test.sh": 'cat "$HERE/../prompts/develop-red.md"\n',
         SCRIPTS_REL + "tests/delta.test.sh": "", SCRIPTS_REL + "tests/gamma.test.sh": ""},
    ) == (0, suites("alpha.test.sh", "delta.test.sh"), "")


def test_a_widening_caused_by_two_unplaced_files_names_both_on_stderr(monkeypatch, run_cli, affected, tmp_path):
    code, out, err = affected_by(
        monkeypatch, run_cli, affected, tmp_path, ["notes.md", "memo.md"],
        {"notes.md": "# notes\n", "memo.md": "# memo\n", SCRIPTS_REL + "foo.sh": "foo\n",
         SCRIPTS_REL + "tests/foo.test.sh": "", SCRIPTS_REL + "tests/py/test_foo.py": ""})
    assert (code, out, "notes.md" in err, "memo.md" in err) == (
        0, SCRIPTS_REL + "tests/py/test_foo.py\n", True, True)


def test_run_state_a_tdd_ledger_alongside_a_script_change_prints_exactly_that_scripts_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [".tdd/issue-416.md", SCRIPTS_REL + "foo.sh"],
        {".tdd/issue-416.md": "- [x] step one\n", SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         SCRIPTS_REL + "tests/foo.test.sh": "", SCRIPTS_REL + "tests/bar.test.sh": ""},
    ) == (0, suites("foo.test.sh"), "")


def test_run_state_alone_exits_3_and_prints_nothing(monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [".tdd/issue-416.md", ".tdd/issue-416-refactor-owed.md"],
        {".tdd/issue-416.md": "- [x] step one\n", ".tdd/issue-416-refactor-owed.md": "refactor owed [x]\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/foo.test.sh": ""},
    ) == (3, "", "")


def test_fail_closed_run_state_alongside_a_file_no_rule_places_still_prints_every_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [".tdd/issue-416.md", "notes.md"],
        {".tdd/issue-416.md": "- [x] step one\n", "notes.md": "# notes\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         SCRIPTS_REL + "tests/foo.test.sh": "", SCRIPTS_REL + "tests/bar.test.sh": "",
         SCRIPTS_REL + "tests/py/test_foo.py": "", SCRIPTS_REL + "tests/py/unit/test_bar.py": ""},
    ) == (0, SCRIPTS_REL + "tests/py/test_foo.py\n" + SCRIPTS_REL + "tests/py/unit/test_bar.py\n",
          "affected-suites: no rule places notes.md; widening to every suite\n")


def test_a_green_commits_shape_ledger_refactor_owed_file_and_a_source_change_prints_exactly_that_scripts_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path,
        [".tdd/issue-416.md", ".tdd/issue-416-refactor-owed.md", SCRIPTS_REL + "foo.sh"],
        {".tdd/issue-416.md": "- [x] step one\n", ".tdd/issue-416-refactor-owed.md": "refactor owed [x]\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         SCRIPTS_REL + "tests/foo.test.sh": "", SCRIPTS_REL + "tests/bar.test.sh": ""},
    ) == (0, suites("foo.test.sh"), "")


SKILL = "skills/tdd/SKILL.md"
GIT_DIFF_OF_SKILL = pytest.mark.process("real git: the changed lines of SKILL.md come from git diff -U0 between two commits")


def sh_git(repo, *args):
    done = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
    return done.stdout.strip()


def new_git_repo(root):
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    return root


def commit_all(repo, message):
    sh_git(repo, "add", "-A")
    sh_git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return sh_git(repo, "rev-parse", "HEAD")


def section_suite(root, doc, name):
    plant(root, {SCRIPTS_REL + "tests/skill-%s.test.sh" % name.lower():
                 '#!/usr/bin/env bash\nskill_md="%s"\nload_section \'%s\'\n' % (doc, name)})


def skill_text(*parts):
    return "# tdd\n\n" + "".join(parts)


def edit_range(run_cli, affected, repo, files):
    base = commit_all(repo, "base")
    plant(repo, files)
    head = commit_all(repo, "head")
    return run_cli(affected, [base + ".." + head], cwd=repo)


def suites(*names):
    return "".join(SUITES + n + "\n" for n in names)


@GIT_DIFF_OF_SKILL
def test_an_edit_inside_one_section_of_skill_md_prints_the_suites_reading_that_section_not_one_reading_only_another(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n")})
    for name in ("Alpha", "Beta"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo,
                      {SKILL: skill_text("## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text\n")}
                      ) == (0, suites("skill-alpha.test.sh"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_inside_one_section_of_skill_md_still_prints_a_suite_reading_skill_md_unsliced(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n"),
                 SCRIPTS_REL + "tests/skill-whole.test.sh":
                 '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\ngrep -F text "$skill_md"\n'})
    section_suite(repo, SKILL, "Beta")
    assert edit_range(run_cli, affected, repo,
                      {SKILL: skill_text("## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text\n")}
                      ) == (0, suites("skill-whole.test.sh"), "")


SUBSECTIONS = "## Alpha\n\nalpha text\n\n### Sub\n\nsub text%s\n\n### Sib\n\nsib text%s\n\n## Beta\n\nbeta text\n"


@GIT_DIFF_OF_SKILL
def test_an_edit_inside_one_subsection_of_skill_md_prints_the_suites_reading_it_and_its_enclosing_section_not_one_reading_only_a_sibling(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text(SUBSECTIONS % ("", ""))})
    for name in ("Alpha", "Sub", "Sib", "Beta"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo, {SKILL: skill_text(SUBSECTIONS % (" 2", ""))}
                      ) == (0, suites("skill-alpha.test.sh", "skill-sub.test.sh"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_inside_a_subsection_after_a_sibling_prints_the_suites_reading_it_and_its_enclosing_section_not_one_reading_the_earlier_sibling(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text(SUBSECTIONS % (" 2", ""))})
    for name in ("Alpha", "Sub", "Sib", "Beta"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo, {SKILL: skill_text(SUBSECTIONS % (" 2", " 2"))}
                      ) == (0, suites("skill-alpha.test.sh", "skill-sib.test.sh"), "")


THREE = "## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n\n## Gamma\n\ngamma text\n"


@GIT_DIFF_OF_SKILL
def test_an_edit_changing_a_heading_line_of_skill_md_prints_every_suite_naming_skill_md(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n")})
    for name in ("Alpha", "Beta"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo,
                      {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Gamma\n\nbeta text\n")}
                      ) == (0, suites("skill-alpha.test.sh", "skill-beta.test.sh"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_only_deleting_a_heading_line_of_skill_md_prints_every_suite_naming_skill_md(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text(THREE)})
    for name in ("Alpha", "Beta", "Gamma"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo,
                      {SKILL: skill_text("## Alpha\n\nalpha text\n\n\nbeta text\n\n## Gamma\n\ngamma text\n")}
                      ) == (0, suites("skill-alpha.test.sh", "skill-beta.test.sh", "skill-gamma.test.sh"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_whose_changed_lines_of_skill_md_span_two_sections_prints_every_suite_naming_skill_md(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text(THREE)})
    for name in ("Alpha", "Beta", "Gamma"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo, {SKILL: skill_text(
        "## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text 2\n\n## Gamma\n\ngamma text\n")}
    ) == (0, suites("skill-alpha.test.sh", "skill-beta.test.sh", "skill-gamma.test.sh"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_to_skill_md_that_cannot_be_placed_in_a_section_prints_every_suite_naming_skill_md(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    for name in ("Alpha", "Beta"):
        section_suite(repo, SKILL, name)
    results = {}
    results["added"] = edit_range(
        run_cli, affected, repo,
        {SKILL: skill_text("intro\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n")})
    results["above the first ##"] = edit_range(
        run_cli, affected, repo,
        {SKILL: skill_text("intro 2\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n")})
    (repo / SKILL).unlink()
    base = commit_all(repo, "base")
    results["deleted"] = run_cli(affected, [base + "~1.." + base], cwd=repo)
    want = (0, suites("skill-alpha.test.sh", "skill-beta.test.sh"), "")
    assert results == {"added": want, "above the first ##": want, "deleted": want}


def doc_edit_with_suites(monkeypatch, run_cli, affected, tmp_path, doc, bash_suite, pytest_file):
    return affected_by(
        monkeypatch, run_cli, affected, tmp_path, [doc],
        {doc: "# doc\n\nstep 2\n",
         SCRIPTS_REL + "tests/" + bash_suite: 'procedure="%s"\ngrep -F step "$procedure"\n' % doc,
         SCRIPTS_REL + "tests/py/unit/" + pytest_file: 'def test_step():\n    open("%s").read()\n' % doc})


def test_an_edit_to_scripts_md_prints_the_bash_suite_naming_it_and_the_pytest_file_mentioning_it_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert doc_edit_with_suites(monkeypatch, run_cli, affected, tmp_path, "skills/tdd/SCRIPTS.md",
                                "catalogue.test.sh", "test_catalogue.py") == (
        0, SUITES + "catalogue.test.sh\n" + SUITES + "py/unit/test_catalogue.py\n", "")


def test_an_edit_to_stopping_md_prints_the_bash_suite_naming_it_and_the_pytest_file_mentioning_it_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert doc_edit_with_suites(monkeypatch, run_cli, affected, tmp_path, "skills/tdd/STOPPING.md",
                                "stopping.test.sh", "test_stopping_file.py") == (
        0, SUITES + "py/unit/test_stopping_file.py\n" + SUITES + "stopping.test.sh\n", "")


def test_an_edit_to_reconcile_md_prints_the_bash_suite_naming_it_and_the_pytest_file_mentioning_it_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert doc_edit_with_suites(monkeypatch, run_cli, affected, tmp_path, "skills/tdd/RECONCILE.md",
                                "reconcile.test.sh", "test_reconcile_file.py") == (
        0, SUITES + "py/unit/test_reconcile_file.py\n" + SUITES + "reconcile.test.sh\n", "")


def test_an_edit_to_bail_md_prints_the_bash_suite_naming_it_and_the_pytest_file_mentioning_it_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert doc_edit_with_suites(monkeypatch, run_cli, affected, tmp_path, "skills/tdd/BAIL.md",
                                "bail.test.sh", "test_bail_file.py") == (
        0, SUITES + "bail.test.sh\n" + SUITES + "py/unit/test_bail_file.py\n", "")


def test_an_edit_to_pin_md_prints_the_bash_suite_naming_it_and_the_pytest_file_mentioning_it_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    code, out, err = doc_edit_with_suites(monkeypatch, run_cli, affected, tmp_path, "skills/tdd/PIN.md",
                                          "pin.test.sh", "test_pin_file.py")
    assert (code, set(out.splitlines()), err) == (
        0, {SUITES + "pin.test.sh", SUITES + "py/unit/test_pin_file.py"}, "")


def test_an_edit_to_skill_edit_md_prints_the_bash_suite_naming_it_and_the_pytest_file_mentioning_it_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    code, out, err = doc_edit_with_suites(monkeypatch, run_cli, affected, tmp_path, "skills/tdd/SKILL-EDIT.md",
                                          "skill-edit.test.sh", "test_skill_edit_file.py")
    assert (code, set(out.splitlines()), err) == (
        0, {SUITES + "skill-edit.test.sh", SUITES + "py/unit/test_skill_edit_file.py"}, "")


def test_an_edit_to_resume_md_prints_the_bash_suite_naming_it_and_the_pytest_file_mentioning_it_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    code, out, err = doc_edit_with_suites(monkeypatch, run_cli, affected, tmp_path, "skills/tdd/RESUME.md",
                                          "resume.test.sh", "test_resume_file.py")
    assert (code, set(out.splitlines()), err) == (
        0, {SUITES + "resume.test.sh", SUITES + "py/unit/test_resume_file.py"}, "")


def test_an_edit_to_revise_md_prints_the_bash_suite_naming_it_and_the_pytest_file_mentioning_it_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    code, out, err = doc_edit_with_suites(monkeypatch, run_cli, affected, tmp_path, "skills/tdd/REVISE.md",
                                          "revise.test.sh", "test_revise_file.py")
    assert (code, set(out.splitlines()), err) == (
        0, {SUITES + "revise.test.sh", SUITES + "py/unit/test_revise_file.py"}, "")


@pytest.mark.process("real git: the changed lines come from git diff -U0 between two commits")
def test_an_edit_inside_one_section_of_claude_md_makefile_a_skill_md_other_than_tdds_or_a_prompt_prints_every_suite_naming_it_file_wide(
        run_cli, affected, tmp_path):
    paths = ["CLAUDE.md", "Makefile", "skills/merge/SKILL.md", "skills/tdd/scripts/prompts/develop.md"]
    text = "# doc\n\n## Alpha\n\nalpha text%s\n\n## Beta\n\nbeta text\n"
    repo = new_git_repo(tmp_path)
    for path in paths:
        plant(repo, {path: text % ""})
        for name in ("Alpha", "Beta"):
            plant(repo, {SCRIPTS_REL + "tests/%s-%s.test.sh" % (path.rsplit("/", 1)[-1].lower().replace(".", "-"), name.lower()):
                         '#!/usr/bin/env bash\ndoc="%s"\nload_section \'%s\'\n' % (path, name)})
    results, wanted = {}, {}
    for path in paths:
        stem = path.rsplit("/", 1)[-1].lower().replace(".", "-")
        results[path] = edit_range(run_cli, affected, repo, {path: text % " 2"})
        wanted[path] = (0, suites(stem + "-alpha.test.sh", stem + "-beta.test.sh"), "")
    assert results == wanted


REAL_EDITS = [
    ("stop-requested.sh renamed in SCRIPTS.md", "py/unit/test_skill_stopping.py", ""),
    ("### 2c. Verify the plan (blind)", "", ""),
    ("### 3. The cycle loop", "py/unit/test_skill_draft_pr.py", ""),
    ("REVISE.md", "py/unit/test_skill_revise_exhausted.py", ""),
    ("STOPPING.md", "py/unit/test_skill_stopping.py", ""),
    ("RECONCILE.md", "py/unit/test_skill_push_reconcile.py", ""),
    ("BAIL.md", "py/unit/test_skill_metrics.py", ""),
    ("RESUME.md", "py/unit/test_skill_refactor_pending.py", ""),
    ("### 4. Draft PR", "py/unit/test_skill_metrics.py", ""),
]


@pytest.mark.process("real git: the changed lines come from git diff -U0 between two commits of a copy of the real files")
@pytest.mark.tree_audit("every suite under skills/tdd/scripts/tests that names or reads SKILL.md")
def test_on_the_real_skill_md_and_suites_a_one_section_edit_selects_the_suites_reading_that_section_through_a_slicing_helper_and_every_suite_reading_skill_md_any_other_way_and_not_a_suite_slicing_only_other_sections(
        run_cli, affected, tmp_path, tests_py_index):
    import re
    repo = new_git_repo(tmp_path)
    tdd = ROOT / "skills/tdd"
    for doc in ("SKILL.md", "SCRIPTS.md", "STOPPING.md", "RECONCILE.md", "BAIL.md", "RESUME.md", "REVISE.md"):
        plant(repo, {"skills/tdd/" + doc: (tdd / doc).read_text(encoding="utf-8")})
    tests = SCRIPTS / "tests"
    for suite in [*tests.glob("*.test.sh"), *tests.glob("unit/*.test.sh")]:
        if re.search(r'"(?:[^"]*/)?skills/tdd/SKILL\.md"', suite.read_text(encoding="utf-8")):
            plant(repo, {str(suite.relative_to(ROOT)): suite.read_text(encoding="utf-8")})
    for entry in tests_py_index:
        if "SKILL.md" in entry.text:
            plant(repo, {str(entry.path.relative_to(ROOT)): entry.text})
    original = {doc: (repo / "skills/tdd" / doc).read_text(encoding="utf-8")
                for doc in ("SKILL.md", "SCRIPTS.md", "STOPPING.md", "RECONCILE.md", "BAIL.md", "RESUME.md", "REVISE.md")}
    wrong = []
    for label, want, unwanted in REAL_EDITS:
        base = commit_all(repo, "base")
        if label.startswith("stop-requested"):
            doc = "SCRIPTS.md"
            edited = re.sub(r"^(- `\$S/)stop-requested\.sh", r"\1stop-asked.sh", original[doc], flags=re.M)
        elif label in ("STOPPING.md", "RECONCILE.md", "BAIL.md", "RESUME.md", "REVISE.md"):
            doc, edited = label, original[label] + "an edited line\n"
        else:
            doc, lines = "SKILL.md", original["SKILL.md"].split("\n")
            at = lines.index(label)
            edited = "\n".join(lines[:at + 2] + ["an edited line"] + lines[at + 2:])
        (repo / "skills/tdd" / doc).write_text(edited, encoding="utf-8")
        head = commit_all(repo, "head")
        code, out, _ = run_cli(affected, [base + ".." + head], cwd=repo)
        printed = out.splitlines()
        if code != 0:
            wrong.append("%s(code=%s)" % (label, code))
        wrong += ["%s: %s not selected" % (label, s) for s in want.split()
                  if "skills/tdd/scripts/tests/" + s not in printed]
        wrong += ["%s: %s selected" % (label, s) for s in unwanted.split()
                  if "skills/tdd/scripts/tests/" + s in printed]
        (repo / "skills/tdd" / doc).write_text(original[doc], encoding="utf-8")
    assert wrong == []


COUNTS = SUITES + "py/unit/test_claude_md_counts.py\n"
HEADER = '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\n'


def test_a_range_that_adds_a_suite_file_under_tests_or_tests_unit_pulls_in_the_claude_md_counts_suite(
        monkeypatch, run_cli, affected, tmp_path):
    added = [SCRIPTS_REL + "tests/newbie.test.sh", SCRIPTS_REL + "tests/unit/rookie.test.sh"]
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, added,
        {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/foo.test.sh": "",
         SCRIPTS_REL + "tests/py/unit/test_claude_md_counts.py": "", **{a: "" for a in added}},
        counted=added,
    ) == (0, SUITES + "newbie.test.sh\n" + COUNTS + SUITES + "unit/rookie.test.sh\n", "")


def test_editing_an_existing_suites_contents_does_not_pull_in_the_claude_md_counts_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "tests/foo.test.sh"],
        {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/foo.test.sh": "# foo suite 2\n",
         SCRIPTS_REL + "tests/py/unit/test_claude_md_counts.py": ""},
    ) == (0, SUITES + "foo.test.sh\n", "")


def test_a_range_that_adds_or_deletes_a_script_under_scripts_pulls_in_the_claude_md_counts_suite(
        monkeypatch, run_cli, affected, tmp_path):
    touched = [SCRIPTS_REL + "bar.sh", SCRIPTS_REL + "newbie.sh", SCRIPTS_REL + "tests/newbie.test.sh"]
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, touched,
        {SCRIPTS_REL + "newbie.sh": "newbie\n", SCRIPTS_REL + "tests/newbie.test.sh": "",
         SCRIPTS_REL + "tests/bar.test.sh": "", SCRIPTS_REL + "tests/py/unit/test_claude_md_counts.py": ""},
        counted=[SCRIPTS_REL + "bar.sh", SCRIPTS_REL + "newbie.sh", SCRIPTS_REL + "tests/newbie.test.sh"],
    ) == (0, SUITES + "bar.test.sh\n" + SUITES + "newbie.test.sh\n" + COUNTS, "")


def test_487_a_lib_file_whose_callers_source_line_ends_in_a_continuation_maps_to_that_callers_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n",
         SCRIPTS_REL + "alpha.sh": HEADER + 'source "$HERE/lib/bar.sh" \\\n  || { echo "alpha: cannot read lib/bar.sh" >&2; exit 2; }\n',
         SCRIPTS_REL + "gamma.sh": "echo gamma\n",
         SCRIPTS_REL + "tests/alpha.test.sh": "", SCRIPTS_REL + "tests/gamma.test.sh": ""},
    ) == (0, SUITES + "alpha.test.sh\n", "")


def test_487_a_caller_whose_source_line_ends_at_the_lib_path_with_or_without_a_trailing_quote_and_spaces_still_maps_to_its_suite(
        monkeypatch, run_cli, affected, tmp_path):
    callers = {"alpha": 'source "$HERE/lib/bar.sh"\n', "beta": 'source "$HERE/lib/bar.sh"   \n',
               "delta": "source $HERE/lib/bar.sh\n", "epsilon": "source $HERE/lib/bar.sh  \n"}
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n", SCRIPTS_REL + "gamma.sh": "echo gamma\n",
         **{SCRIPTS_REL + n + ".sh": HEADER + line for n, line in callers.items()},
         **{SCRIPTS_REL + "tests/%s.test.sh" % n: "" for n in (*callers, "gamma")}},
    ) == (0, suites("alpha.test.sh", "beta.test.sh", "delta.test.sh", "epsilon.test.sh"), "")


def test_487_a_comment_that_names_a_lib_file_is_still_not_a_dependency(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n",
         SCRIPTS_REL + "alpha.sh": HEADER + 'source "$HERE/lib/bar.sh"\n',
         SCRIPTS_REL + "beta.sh": HEADER + '# source "$HERE/lib/bar.sh" \\\n',
         SCRIPTS_REL + "gamma.sh": HEADER + '  # . "$HERE/lib/bar.sh"\n',
         **{SCRIPTS_REL + "tests/%s.test.sh" % n: "" for n in ("alpha", "beta", "gamma")}},
    ) == (0, SUITES + "alpha.test.sh\n", "")


def module_shim(module):
    return '#!/bin/sh\nexec python3 -m veri.%s "$@"\n' % module


def test_a_touched_veri_module_prints_its_pytest_file_and_its_shims_bash_suite_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "veri/event_log.py"],
        {SCRIPTS_REL + "veri/event_log.py": "def main(): return 2\n",
         SCRIPTS_REL + "tests/py/test_event_log.py": "def test_main(): pass\n",
         SCRIPTS_REL + "event-log.sh": module_shim("event_log"),
         SCRIPTS_REL + "tests/event-log.test.sh": "# event-log suite\n",
         SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/bar.test.sh": "# bar suite\n"},
    ) == (0, SUITES + "event-log.test.sh\n" + SUITES + "py/test_event_log.py\n", "")


def test_a_touched_veri_module_with_no_pytest_file_prints_only_its_shims_bash_suite_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "veri/probe_queue.py"],
        {SCRIPTS_REL + "veri/probe_queue.py": "def main(): return 2\n",
         SCRIPTS_REL + "probe-queue.sh": module_shim("probe_queue"),
         SCRIPTS_REL + "tests/probe-queue.test.sh": "# probe-queue suite\n"},
    ) == (0, SUITES + "probe-queue.test.sh\n", "")


def test_a_touched_pytest_file_under_tests_py_prints_itself_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "tests/py/test_status.py"],
        {SCRIPTS_REL + "tests/py/test_status.py": "def test_main(): assert False\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/foo.test.sh": "# foo suite\n",
         SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/bar.test.sh": "# bar suite\n"},
    ) == (0, SUITES + "py/test_status.py\n", "")


@pytest.mark.process("a real sh shim run through a symlink to the skill directory, over real git")
def test_the_shim_run_through_a_symlink_to_the_skill_directory_answers_as_it_does_in_place(tmp_path):
    repo = new_git_repo(tmp_path / "repo")
    plant(repo, {SCRIPTS_REL + "tests/py/test_status.py": "def test_main(): pass\n"})
    base = commit_all(repo, "base")
    plant(repo, {SCRIPTS_REL + "tests/py/test_status.py": "def test_main(): assert False\n"})
    head = commit_all(repo, "head")
    link = tmp_path / "linked-skill"
    link.symlink_to(SCRIPTS.parent)

    def answer(shim):
        done = subprocess.run(["/bin/sh", str(shim), base + ".." + head], cwd=repo,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return done.returncode, done.stdout

    assert answer(link / "scripts/affected-suites.sh") == answer(SCRIPTS / "affected-suites.sh") == (
        0, SUITES + "py/test_status.py\n")


def topic_range(run_cli, affected, repo):
    return run_cli(affected, ["main..HEAD"], cwd=repo)


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_suite_the_base_gained_after_the_branch_point_is_not_printed_only_the_branchs_own(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SCRIPTS_REL + "tests/py/test_a.py": "# a suite\n"})
    commit_all(repo, "base")
    sh_git(repo, "checkout", "-q", "-b", "topic")
    plant(repo, {SCRIPTS_REL + "tests/py/test_a.py": "# a suite 2\n"})
    commit_all(repo, "head")
    sh_git(repo, "checkout", "-q", "main")
    plant(repo, {SCRIPTS_REL + "tests/py/test_orchestrate.py": "# orchestrate suite\n"})
    commit_all(repo, "main gains a suite")
    sh_git(repo, "checkout", "-q", "topic")
    assert topic_range(run_cli, affected, repo) == (0, SUITES + "py/test_a.py\n", "")


def foo_bar_repo_on_topic(tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/foo.test.sh": "# foo suite\n",
                 SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/bar.test.sh": "# bar suite\n",
                 SCRIPTS_REL + "tests/py/unit/test_claude_md_counts.py": "# counts suite\n"})
    commit_all(repo, "base")
    sh_git(repo, "checkout", "-q", "-b", "topic")
    return repo


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_non_suite_file_the_base_changed_or_deleted_after_the_branch_point_contributes_no_suite(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/foo.test.sh": "# foo suite\n",
                 SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/bar.test.sh": "# bar suite\n",
                 SCRIPTS_REL + "prompts/p.md": "a prompt\n",
                 SCRIPTS_REL + "tests/baz.test.sh": "# reads prompts/p.md\n"})
    commit_all(repo, "base")
    sh_git(repo, "checkout", "-q", "-b", "topic")
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    commit_all(repo, "head")
    sh_git(repo, "checkout", "-q", "main")
    plant(repo, {SCRIPTS_REL + "bar.sh": "bar 2\n"})
    (repo / SCRIPTS_REL / "prompts/p.md").unlink()
    commit_all(repo, "main changes a script and deletes a prompt")
    sh_git(repo, "checkout", "-q", "topic")
    assert topic_range(run_cli, affected, repo) == (0, SUITES + "foo.test.sh\n", "")


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_suite_the_base_added_or_deleted_after_the_branch_point_does_not_pull_in_the_claude_md_counts_suite(
        run_cli, affected, tmp_path):
    repo = foo_bar_repo_on_topic(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    commit_all(repo, "head")
    sh_git(repo, "checkout", "-q", "main")
    plant(repo, {SCRIPTS_REL + "tests/baz.test.sh": "# baz suite\n"})
    (repo / SCRIPTS_REL / "tests/bar.test.sh").unlink()
    commit_all(repo, "main adds one suite and deletes another")
    sh_git(repo, "checkout", "-q", "topic")
    assert topic_range(run_cli, affected, repo) == (0, SUITES + "foo.test.sh\n", "")


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_suite_the_branch_itself_deleted_is_not_printed(run_cli, affected, tmp_path):
    repo = foo_bar_repo_on_topic(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    (repo / SCRIPTS_REL / "tests/bar.test.sh").unlink()
    commit_all(repo, "head")
    assert topic_range(run_cli, affected, repo) == (
        0, SUITES + "foo.test.sh\n" + SUITES + "py/unit/test_claude_md_counts.py\n", "")


def working_tree_git(touched=(), untracked_=(), counted=(), counted_untracked=()):
    lines = lambda names: "".join(n + "\n" for n in names)

    def run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(args, 0, "abc\n", "")
        if list(args[:3]) == ["git", "diff", "--name-only"]:
            return subprocess.CompletedProcess(args, 0, lines(counted if "--diff-filter=AD" in args else touched), "")
        if list(args[:3]) == ["git", "diff", "-U0"]:
            return subprocess.CompletedProcess(args, 1, "", "")
        if list(args[:3]) == ["git", "ls-files", "--others"]:
            return subprocess.CompletedProcess(args, 0, lines(counted_untracked if "--" in args else untracked_), "")
        raise AssertionError("unexpected command: %r" % (args,))
    return run


def git_state(repo):
    return [sh_git(repo, *args) for args in (("stash", "list"), ("worktree", "list"), ("rev-parse", "HEAD"))]


@pytest.mark.process("git")
def test_working_tree_an_uncommitted_edit_to_a_script_prints_its_suite_and_leaves_stash_worktrees_and_head(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/foo.test.sh": "# foo suite\n",
                 SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/bar.test.sh": "# bar suite\n"})
    base = commit_all(repo, "base")
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    before = git_state(repo)
    assert run_cli(affected, [base], cwd=repo) == (0, SUITES + "foo.test.sh\n", "")
    assert git_state(repo) == before


@pytest.mark.process("git")
def test_working_tree_an_uncommitted_edit_inside_one_section_of_skill_md_prints_the_suites_reading_it_or_skill_md_unsliced(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n"),
                 SCRIPTS_REL + "tests/skill-whole.test.sh":
                 '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\ngrep -F text "$skill_md"\n'})
    for name in ("Alpha", "Beta"):
        section_suite(repo, SKILL, name)
    base = commit_all(repo, "base")
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text\n")})
    assert run_cli(affected, [base], cwd=repo) == (
        0, suites("skill-alpha.test.sh", "skill-whole.test.sh"), "")


def untracked_baz_suite(monkeypatch, tmp_path, extra=None):
    baz = SCRIPTS_REL + "tests/baz.test.sh"
    monkeypatch.setattr(subprocess, "run", working_tree_git(untracked_=[baz], counted_untracked=[baz]))
    plant(tmp_path, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/foo.test.sh": "# foo suite\n",
                     baz: "# baz suite\n", **(extra or {})})


def test_working_tree_a_new_untracked_suite_is_printed(monkeypatch, run_cli, affected, tmp_path):
    untracked_baz_suite(monkeypatch, tmp_path)
    code, out, err = run_cli(affected, ["base"], cwd=tmp_path)
    assert (code, SUITES + "baz.test.sh" in out.splitlines()) == (0, True)


def test_working_tree_a_new_untracked_suite_also_prints_the_claude_md_counts_suite(
        monkeypatch, run_cli, affected, tmp_path):
    untracked_baz_suite(monkeypatch, tmp_path,
                        {SCRIPTS_REL + "tests/py/unit/test_claude_md_counts.py": "# counts suite\n"})
    assert run_cli(affected, ["base"], cwd=tmp_path) == (0, SUITES + "baz.test.sh\n" + COUNTS, "")


def test_working_tree_a_committed_added_suite_with_no_untracked_file_still_prints_the_claude_md_counts_suite(
        monkeypatch, run_cli, affected, tmp_path):
    monkeypatch.setattr(subprocess, "run", working_tree_git(
        touched=[SCRIPTS_REL + "tests/baz.test.sh"], counted=[SCRIPTS_REL + "tests/baz.test.sh"]))
    plant(tmp_path, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/foo.test.sh": "# foo suite\n",
                     SCRIPTS_REL + "tests/py/unit/test_claude_md_counts.py": "# counts suite\n",
                     SCRIPTS_REL + "tests/baz.test.sh": "# baz suite\n"})
    assert run_cli(affected, ["base"], cwd=tmp_path) == (0, SUITES + "baz.test.sh\n" + COUNTS, "")


def test_working_tree_with_nothing_changed_since_base_exits_3_and_prints_nothing(
        monkeypatch, run_cli, affected, tmp_path):
    monkeypatch.setattr(subprocess, "run", working_tree_git())
    assert run_cli(affected, ["base"], cwd=tmp_path) == (3, "", "")


def test_main_prints_the_pytest_file_of_a_touched_script_and_never_a_bash_suite(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/foo.sh"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/foo.test.sh").write_text("")
    (tmp_path / "skills/tdd/scripts/tests/py/test_foo.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_foo.py\n", "")
