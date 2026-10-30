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


def fake_git(touched, diff_code=0):
    def run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(args, 0, "abc\n", "")
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
    (tmp_path / "skills/tdd/scripts/tests/py").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/test_.sh.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_.sh.py\n", "")


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


def test_main_prints_the_pytest_files_naming_readme_md_for_a_readme_change(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["README.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_skill_conductor_launch.py").write_text('README = ROOT / "README.md"\n')
    (tests / "py/unit/test_skill_commit.py").write_text('README = parents[6] / "README.md"\n')
    (tests / "py/unit/test_other.py").write_text('text = open("CONTRIBUTING.md").read()\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0,
        "skills/tdd/scripts/tests/py/unit/test_skill_commit.py\n"
        "skills/tdd/scripts/tests/py/unit/test_skill_conductor_launch.py\n",
        "")


def test_main_widens_a_file_no_rule_handles_to_every_pytest_file_1812(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["docs/notes.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
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
    (scripts / "tests/py").mkdir(parents=True)
    (scripts / "tests/py/test_user.py").write_text("")
    assert affected.main(["base..head"]) == 0
    assert capsys.readouterr().out == "skills/tdd/scripts/tests/py/test_user.py\n"


def test_main_prints_the_emitted_text_check_for_a_partial_1622(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/_shared.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_emitted_text.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_emitted_text.py\n", "")


def test_main_prints_the_emitted_text_check_for_a_prompt_1024(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/unnamed.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_emitted_text.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_emitted_text.py\n", "")


def test_main_prints_the_four_prompt_renderer_suites_for_a_develop_template_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    renderers = ["py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py"]
    for name in renderers:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in renderers))


def test_main_prints_the_develop_prompt_process_suite_for_a_develop_template_1338(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    present = ["py/test_build_develop_prompt_process.py"]
    for name in present:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in present))


def test_main_prints_the_verify_prompt_process_suite_for_a_verify_template_1341(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/verify-green.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    present = ["py/test_build_verify_prompt_process.py"]
    for name in present:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in present))


def test_main_prints_the_four_prompt_renderer_suites_for_a_verify_template_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/verify-green.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    renderers = ["py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py"]
    for name in renderers:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in renderers))


def test_main_prints_the_four_prompt_renderer_suites_for_a_partial_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/_leaf-safety.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    renderers = ["py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py"]
    for name in renderers:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in renderers))


def test_main_prints_only_the_prompt_renderer_suites_that_exist_for_a_template_change_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    present = ["py/unit/test_build_develop_prompt.py"]
    for name in present:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in present))


def test_main_prints_none_of_the_prompt_renderer_suites_for_a_change_outside_the_prompts_directory_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/foo.sh"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    renderers = ["py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py"]
    for name in renderers + ["py/unit/test_foo.py"]:
        (tests / name).write_text("")
    (tmp_path / "skills/tdd/scripts/foo.sh").write_text("#!/usr/bin/env bash\n")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, ["skills/tdd/scripts/tests/py/unit/test_foo.py"])


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


def test_main_attributes_an_edit_by_the_fence_answer_of_the_markdown_sections_reader_1976(
        tmp_path, monkeypatch, capsys, affected):
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
    (tmp_path / skill).write_text("## Alpha\n```\n## x\nalpha body\n```\n## Beta\nbeta body\n")
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_x.py").write_text('section(SKILL, "## x")\n')
    sections = importlib.import_module("veri.markdown_sections")
    monkeypatch.setattr(sections, "fenced_lines", lambda text: [False] * len(text.splitlines()))
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_x.py\n", "")


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
    spelled = sorted(set(re.findall(r'["/]((?:py/(?:unit/)?)?test_\w+\.py)"', source)))
    return spelled, [p for p in spelled if not (tests / p).is_file()]


def test_every_suite_path_affected_suites_names_exists():
    """Its subject is source text: the suite paths veri/affected_suites.py spells."""
    spelled, missing = spelled_suites_missing((SCRIPTS / "veri" / "affected_suites.py").read_text(encoding="utf-8"), SCRIPTS / "tests")
    assert spelled and missing == [], "affected_suites.py names suites that are not files: %s" % ", ".join(missing)


SCRIPTS_REL = "skills/tdd/scripts/"
SUITES = SCRIPTS_REL + "tests/"


def cli_git(touched, unresolvable=None):
    def run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            bad = unresolvable is not None and unresolvable in args[-1]
            return subprocess.CompletedProcess(args, 1 if bad else 0, "" if bad else "abc\n", "")
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


def affected_by(monkeypatch, run_cli, affected, tmp_path, touched, files, range_="base..head"):
    monkeypatch.setattr(subprocess, "run", cli_git(touched))
    plant(tmp_path, files)
    return run_cli(affected, [range_], cwd=tmp_path)


def test_resolvable_range_prints_one_suite_per_line_sorted_with_no_duplicate(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path,
        [SCRIPTS_REL + "wolf.sh", SCRIPTS_REL + "zulu.sh", SCRIPTS_REL + "tests/py/test_wolf.py"],
        {SCRIPTS_REL + "zulu.sh": "zulu\n", SCRIPTS_REL + "wolf.sh": "wolf\n",
         SCRIPTS_REL + "tests/py/test_wolf.py": "", SCRIPTS_REL + "tests/py/unit/test_zulu.py": ""},
    ) == (0, SUITES + "py/test_wolf.py\n" + SUITES + "py/unit/test_zulu.py\n", "")


def test_malformed_range_exits_2_with_the_usage_line(monkeypatch, run_cli, affected, tmp_path):
    results = []
    for range_ in ("abc..no-such-rev", "no-such-rev..abc"):
        monkeypatch.setattr(subprocess, "run", cli_git([], unresolvable="no-such-rev"))
        results.append(run_cli(affected, [range_], cwd=tmp_path))
    refusal = (2, "", "affected-suites: cannot resolve revision 'no-such-rev'\n" + USAGE)
    assert results == [refusal, refusal]


def test_empty_diff_exits_3_and_prints_nothing(monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(monkeypatch, run_cli, affected, tmp_path, [], {}) == (3, "", "")


def test_rule_2_a_lib_prints_the_suite_of_every_script_that_sources_it_and_no_others(
        monkeypatch, run_cli, affected, tmp_path):
    sourcing = '#!/usr/bin/env bash\nsource "$HERE/lib/bar.sh"\n'
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { :; }\n",
         SCRIPTS_REL + "alpha.sh": sourcing, SCRIPTS_REL + "beta.sh": sourcing,
         SCRIPTS_REL + "gamma.sh": "echo gamma\n", SCRIPTS_REL + "bar.sh": "echo bar\n",
         **{SCRIPTS_REL + "tests/py/test_%s.py" % n: "" for n in ("alpha", "beta", "gamma", "bar")}},
    ) == (0, SUITES + "py/test_alpha.py\n" + SUITES + "py/test_beta.py\n", "")


def test_rule_3_a_changed_fixture_widens_to_every_pytest_file(monkeypatch, run_cli, affected, tmp_path):
    code, out, err = affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "tests/fixtures/plan.md"],
        {SCRIPTS_REL + "tests/fixtures/plan.md": "# plan\n",
         SCRIPTS_REL + "tests/py/test_alpha.py": "", SCRIPTS_REL + "tests/py/unit/test_beta.py": ""})
    assert (code, out, err) == (
        0, SUITES + "py/test_alpha.py\n" + SUITES + "py/unit/test_beta.py\n",
        "affected-suites: no rule places " + SCRIPTS_REL + "tests/fixtures/plan.md; widening to every suite\n")


def test_rule_4_skill_md_prints_the_pytest_files_naming_it_and_claude_md_and_makefile_place_none(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, ["CLAUDE.md", "skills/tdd/SKILL.md", "Makefile"],
        {"CLAUDE.md": "# veri\n", "skills/tdd/SKILL.md": "# tdd\n", "Makefile": "test:\n",
         SCRIPTS_REL + "gamma.sh": "gamma\n",
         SCRIPTS_REL + "tests/py/test_skill_md_guard.py": 'SKILL = "skills/tdd/SKILL.md"\n',
         SCRIPTS_REL + "tests/py/test_gamma.py": "def test_gamma(): pass\n"},
    ) == (0, SUITES + "py/test_skill_md_guard.py\n", "")


def test_claude_md_and_makefile_alone_place_no_suite_and_exit_3(monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, ["CLAUDE.md", "Makefile", "skills/merge/SKILL.md"],
        {"CLAUDE.md": "# veri\n", "Makefile": "test:\n", "skills/merge/SKILL.md": "# merge\n",
         SCRIPTS_REL + "tests/py/test_gamma.py": 'ROOT / "CLAUDE.md"\n'},
    ) == (3, "", "")


def test_rule_5_a_rule_1_file_plus_a_file_no_rule_matches_prints_every_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "foo.sh", "docs/notes.md"],
        {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "baz.sh": "baz\n",
         "docs/notes.md": "# notes\n",
         SCRIPTS_REL + "tests/py/test_foo.py": "", SCRIPTS_REL + "tests/py/unit/test_baz.py": ""},
    ) == (0, SCRIPTS_REL + "tests/py/test_foo.py\n" + SCRIPTS_REL + "tests/py/unit/test_baz.py\n",
          "affected-suites: no rule places docs/notes.md; widening to every suite\n")


def test_rule_5_a_diff_touching_only_files_rules_1_to_4_match_never_falls_back_to_the_full_suite(
        monkeypatch, run_cli, affected, tmp_path):
    sourcing = '#!/usr/bin/env bash\nsource "$HERE/lib/bar.sh"\n'
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path,
        [SCRIPTS_REL + "foo.sh", SCRIPTS_REL + "lib/bar.sh", "CLAUDE.md"],
        {"CLAUDE.md": "# veri\n", SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "lib/bar.sh": "bar_fn() { :; }\n",
         SCRIPTS_REL + "alpha.sh": sourcing, SCRIPTS_REL + "beta.sh": "beta\n",
         SCRIPTS_REL + "gamma.sh": "gamma\n", SCRIPTS_REL + "zeta.sh": "zeta\n",
         SCRIPTS_REL + "tests/py/test_foo.py": "", SCRIPTS_REL + "tests/py/test_alpha.py": "",
         SCRIPTS_REL + "tests/py/test_beta.py": "", SCRIPTS_REL + "tests/py/test_gamma.py": "",
         SCRIPTS_REL + "tests/py/unit/test_zeta.py": ""},
    ) == (0, suites("py/test_alpha.py", "py/test_foo.py"), "")


def test_a_widening_caused_by_two_unplaced_files_names_both_on_stderr(monkeypatch, run_cli, affected, tmp_path):
    code, out, err = affected_by(
        monkeypatch, run_cli, affected, tmp_path, ["notes.md", "memo.md"],
        {"notes.md": "# notes\n", "memo.md": "# memo\n", SCRIPTS_REL + "foo.sh": "foo\n",
         SCRIPTS_REL + "tests/py/test_foo.py": ""})
    assert (code, out, "notes.md" in err, "memo.md" in err) == (
        0, SCRIPTS_REL + "tests/py/test_foo.py\n", True, True)


def test_run_state_a_tdd_ledger_alongside_a_script_change_prints_exactly_that_scripts_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [".tdd/issue-416.md", SCRIPTS_REL + "foo.sh"],
        {".tdd/issue-416.md": "- [x] step one\n", SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         SCRIPTS_REL + "tests/py/test_foo.py": "", SCRIPTS_REL + "tests/py/test_bar.py": ""},
    ) == (0, suites("py/test_foo.py"), "")


def test_run_state_alone_exits_3_and_prints_nothing(monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [".tdd/issue-416.md", ".tdd/issue-416-refactor-owed.md"],
        {".tdd/issue-416.md": "- [x] step one\n", ".tdd/issue-416-refactor-owed.md": "refactor owed [x]\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/py/test_foo.py": ""},
    ) == (3, "", "")


def test_fail_closed_run_state_alongside_a_file_no_rule_places_still_prints_every_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [".tdd/issue-416.md", "notes.md"],
        {".tdd/issue-416.md": "- [x] step one\n", "notes.md": "# notes\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
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
         SCRIPTS_REL + "tests/py/test_foo.py": "", SCRIPTS_REL + "tests/py/test_bar.py": ""},
    ) == (0, suites("py/test_foo.py"), "")


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
    level = "###" if name in ("Sub", "Sib") else "##"
    plant(root, {SCRIPTS_REL + "tests/py/unit/test_skill_%s.py" % name.lower():
                 'from skill_sections import section\nDOC = "%s"\nsection(DOC, "%s %s")\n' % (doc, level, name)})


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
def test_an_edit_inside_one_section_of_skill_md_prints_the_pytest_files_reading_that_section_not_one_reading_only_another(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n")})
    for name in ("Alpha", "Beta"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo,
                      {SKILL: skill_text("## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text\n")}
                      ) == (0, suites("py/unit/test_skill_alpha.py"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_inside_one_section_of_skill_md_still_prints_a_pytest_file_reading_skill_md_unsliced(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n"),
                 SCRIPTS_REL + "tests/py/unit/test_skill_whole.py":
                 'from pathlib import Path\ntext = Path("skills/tdd/SKILL.md").read_text()\n'})
    section_suite(repo, SKILL, "Beta")
    assert edit_range(run_cli, affected, repo,
                      {SKILL: skill_text("## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text\n")}
                      ) == (0, suites("py/unit/test_skill_whole.py"), "")


SUBSECTIONS = "## Alpha\n\nalpha text\n\n### Sub\n\nsub text%s\n\n### Sib\n\nsib text%s\n\n## Beta\n\nbeta text\n"


@GIT_DIFF_OF_SKILL
def test_an_edit_inside_one_subsection_of_skill_md_prints_the_pytest_files_reading_it_and_its_enclosing_section_not_one_reading_only_a_sibling(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text(SUBSECTIONS % ("", ""))})
    for name in ("Alpha", "Sub", "Sib", "Beta"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo, {SKILL: skill_text(SUBSECTIONS % (" 2", ""))}
                      ) == (0, suites("py/unit/test_skill_alpha.py", "py/unit/test_skill_sub.py"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_inside_a_subsection_after_a_sibling_prints_the_pytest_files_reading_it_and_its_enclosing_section_not_one_reading_the_earlier_sibling(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text(SUBSECTIONS % (" 2", ""))})
    for name in ("Alpha", "Sub", "Sib", "Beta"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo, {SKILL: skill_text(SUBSECTIONS % (" 2", " 2"))}
                      ) == (0, suites("py/unit/test_skill_alpha.py", "py/unit/test_skill_sib.py"), "")


THREE = "## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n\n## Gamma\n\ngamma text\n"


@GIT_DIFF_OF_SKILL
def test_an_edit_changing_a_heading_line_of_skill_md_prints_every_pytest_file_naming_skill_md(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n")})
    for name in ("Alpha", "Beta"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo,
                      {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Gamma\n\nbeta text\n")}
                      ) == (0, suites("py/unit/test_skill_alpha.py", "py/unit/test_skill_beta.py"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_only_deleting_a_heading_line_of_skill_md_prints_every_pytest_file_naming_skill_md(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text(THREE)})
    for name in ("Alpha", "Beta", "Gamma"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo,
                      {SKILL: skill_text("## Alpha\n\nalpha text\n\n\nbeta text\n\n## Gamma\n\ngamma text\n")}
                      ) == (0, suites("py/unit/test_skill_alpha.py", "py/unit/test_skill_beta.py", "py/unit/test_skill_gamma.py"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_whose_changed_lines_of_skill_md_span_two_sections_prints_every_pytest_file_naming_skill_md(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text(THREE)})
    for name in ("Alpha", "Beta", "Gamma"):
        section_suite(repo, SKILL, name)
    assert edit_range(run_cli, affected, repo, {SKILL: skill_text(
        "## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text 2\n\n## Gamma\n\ngamma text\n")}
    ) == (0, suites("py/unit/test_skill_alpha.py", "py/unit/test_skill_beta.py", "py/unit/test_skill_gamma.py"), "")


@GIT_DIFF_OF_SKILL
def test_an_edit_to_skill_md_that_cannot_be_placed_in_a_section_prints_every_pytest_file_naming_skill_md(
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
    want = (0, suites("py/unit/test_skill_alpha.py", "py/unit/test_skill_beta.py"), "")
    assert results == {"added": want, "above the first ##": want, "deleted": want}


DOC_EDIT_FILES = {
    "SCRIPTS.md": "test_catalogue.py", "PREFLIGHT.md": "test_preflight_file.py", "STOPPING.md": "test_stopping_file.py",
    "RECONCILE.md": "test_reconcile_file.py", "BAIL.md": "test_bail_file.py", "PIN.md": "test_pin_file.py",
    "SKILL-EDIT.md": "test_skill_edit_file.py", "RESUME.md": "test_resume_file.py", "REVISE.md": "test_revise_file.py",
    "STRUCTURAL.md": "test_structural_file.py", "PHASED.md": "test_phased_file.py",
    "REFACTOR-KIND.md": "test_refactor_kind_file.py",
}


@pytest.mark.parametrize("doc", sorted(DOC_EDIT_FILES))
def test_an_edit_to_a_companion_md_prints_exactly_the_pytest_file_mentioning_it_without_widening_or_unplaced(
        monkeypatch, run_cli, affected, tmp_path, doc):
    files = {"skills/tdd/" + d: "# doc\n\nstep 2\n" for d in DOC_EDIT_FILES}
    files.update({SCRIPTS_REL + "tests/py/unit/" + t: 'def test_step():\n    open("%s").read()\n' % d
                  for d, t in DOC_EDIT_FILES.items()})
    assert affected_by(monkeypatch, run_cli, affected, tmp_path, ["skills/tdd/" + doc], files) == (
        0, SUITES + "py/unit/" + DOC_EDIT_FILES[doc] + "\n", "")


REAL_EDITS = [
    ("stop-requested.sh renamed in SCRIPTS.md", "py/unit/test_skill_stopping.py", ""),
    ("### 2c. Verify the plan (blind)", "", ""),
    ("### 3. The cycle loop", "py/unit/test_skill_draft_pr.py", ""),
    ("REVISE.md", "py/unit/test_skill_revise_exhausted.py", ""),
    ("STOPPING.md", "py/test_skill_leaf_env.py", ""),
    ("RECONCILE.md", "py/unit/test_skill_resume_pointers.py", ""),
    ("BAIL.md", "py/test_skill_leaf_env.py", ""),
    ("RESUME.md", "py/test_skill_leaf_env.py", ""),
    ("### 4. Draft PR", "py/unit/test_skill_draft_pr.py", ""),
]


@pytest.mark.process("real git: the changed lines come from git diff -U0 between two commits of a copy of the real files")
@pytest.mark.tree_audit("every pytest file under skills/tdd/scripts/tests that names or reads SKILL.md")
def test_on_the_real_skill_md_and_suites_a_one_section_edit_selects_the_suites_reading_that_section_through_a_slicing_helper_and_every_suite_reading_skill_md_any_other_way_and_not_a_suite_slicing_only_other_sections(
        run_cli, affected, tmp_path, tests_py_index):
    import re
    repo = new_git_repo(tmp_path)
    tdd = ROOT / "skills/tdd"
    for doc in ("SKILL.md", "SCRIPTS.md", "STOPPING.md", "RECONCILE.md", "BAIL.md", "RESUME.md", "REVISE.md"):
        plant(repo, {"skills/tdd/" + doc: (tdd / doc).read_text(encoding="utf-8")})
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


HEADER = '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\n'


def test_487_a_lib_file_whose_callers_source_line_ends_in_a_continuation_maps_to_that_callers_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n",
         SCRIPTS_REL + "alpha.sh": HEADER + 'source "$HERE/lib/bar.sh" \\\n  || { echo "alpha: cannot read lib/bar.sh" >&2; exit 2; }\n',
         SCRIPTS_REL + "gamma.sh": "echo gamma\n",
         SCRIPTS_REL + "tests/py/test_alpha.py": "", SCRIPTS_REL + "tests/py/test_gamma.py": ""},
    ) == (0, SUITES + "py/test_alpha.py\n", "")


def test_487_a_caller_whose_source_line_ends_at_the_lib_path_with_or_without_a_trailing_quote_and_spaces_still_maps_to_its_suite(
        monkeypatch, run_cli, affected, tmp_path):
    callers = {"alpha": 'source "$HERE/lib/bar.sh"\n', "beta": 'source "$HERE/lib/bar.sh"   \n',
               "delta": "source $HERE/lib/bar.sh\n", "epsilon": "source $HERE/lib/bar.sh  \n"}
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n", SCRIPTS_REL + "gamma.sh": "echo gamma\n",
         **{SCRIPTS_REL + n + ".sh": HEADER + line for n, line in callers.items()},
         **{SCRIPTS_REL + "tests/py/test_%s.py" % n: "" for n in (*callers, "gamma")}},
    ) == (0, suites("py/test_alpha.py", "py/test_beta.py", "py/test_delta.py", "py/test_epsilon.py"), "")


def test_487_a_comment_that_names_a_lib_file_is_still_not_a_dependency(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n",
         SCRIPTS_REL + "alpha.sh": HEADER + 'source "$HERE/lib/bar.sh"\n',
         SCRIPTS_REL + "beta.sh": HEADER + '# source "$HERE/lib/bar.sh" \\\n',
         SCRIPTS_REL + "gamma.sh": HEADER + '  # . "$HERE/lib/bar.sh"\n',
         **{SCRIPTS_REL + "tests/py/test_%s.py" % n: "" for n in ("alpha", "beta", "gamma")}},
    ) == (0, SUITES + "py/test_alpha.py\n", "")


def test_a_touched_veri_module_prints_its_pytest_file_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "veri/event_log.py"],
        {SCRIPTS_REL + "veri/event_log.py": "def main(): return 2\n",
         SCRIPTS_REL + "tests/py/test_event_log.py": "def test_main(): pass\n",
         SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/py/test_bar.py": "def test_bar(): pass\n"},
    ) == (0, SUITES + "py/test_event_log.py\n", "")


def test_a_touched_veri_module_with_no_pytest_file_places_no_suite_and_exits_3(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "veri/probe_queue.py"],
        {SCRIPTS_REL + "veri/probe_queue.py": "def main(): return 2\n",
         SCRIPTS_REL + "probe-queue.sh": '#!/bin/sh\nexec python3 -m veri.probe_queue "$@"\n'},
    ) == (3, "", "")


def test_a_touched_pytest_file_under_tests_py_prints_itself_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "tests/py/test_status.py"],
        {SCRIPTS_REL + "tests/py/test_status.py": "def test_main(): assert False\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/py/test_foo.py": "# foo suite\n",
         SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/py/test_bar.py": "# bar suite\n"},
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
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/py/test_foo.py": "# foo suite\n",
                 SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/py/test_bar.py": "# bar suite\n"})
    commit_all(repo, "base")
    sh_git(repo, "checkout", "-q", "-b", "topic")
    return repo


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_non_suite_file_the_base_changed_or_deleted_after_the_branch_point_contributes_no_suite(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/py/test_foo.py": "# foo suite\n",
                 SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/py/test_bar.py": "# bar suite\n",
                 SCRIPTS_REL + "prompts/p.md": "a prompt\n",
                 SCRIPTS_REL + "tests/py/test_baz.py": "# reads prompts/p.md\n"})
    commit_all(repo, "base")
    sh_git(repo, "checkout", "-q", "-b", "topic")
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    commit_all(repo, "head")
    sh_git(repo, "checkout", "-q", "main")
    plant(repo, {SCRIPTS_REL + "bar.sh": "bar 2\n"})
    (repo / SCRIPTS_REL / "prompts/p.md").unlink()
    commit_all(repo, "main changes a script and deletes a prompt")
    sh_git(repo, "checkout", "-q", "topic")
    assert topic_range(run_cli, affected, repo) == (0, SUITES + "py/test_foo.py\n", "")


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_suite_the_base_added_or_deleted_after_the_branch_point_is_not_printed(
        run_cli, affected, tmp_path):
    repo = foo_bar_repo_on_topic(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    commit_all(repo, "head")
    sh_git(repo, "checkout", "-q", "main")
    plant(repo, {SCRIPTS_REL + "tests/py/test_baz.py": "# baz suite\n"})
    (repo / SCRIPTS_REL / "tests/py/test_bar.py").unlink()
    commit_all(repo, "main adds one suite and deletes another")
    sh_git(repo, "checkout", "-q", "topic")
    assert topic_range(run_cli, affected, repo) == (0, SUITES + "py/test_foo.py\n", "")


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_suite_the_branch_itself_deleted_is_not_printed(run_cli, affected, tmp_path):
    repo = foo_bar_repo_on_topic(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    (repo / SCRIPTS_REL / "tests/py/test_bar.py").unlink()
    commit_all(repo, "head")
    assert topic_range(run_cli, affected, repo) == (0, SUITES + "py/test_foo.py\n", "")


def working_tree_git(touched=(), untracked_=()):
    lines = lambda names: "".join(n + "\n" for n in names)

    def run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(args, 0, "abc\n", "")
        if list(args[:3]) == ["git", "diff", "--name-only"]:
            return subprocess.CompletedProcess(args, 0, lines(touched), "")
        if list(args[:3]) == ["git", "diff", "-U0"]:
            return subprocess.CompletedProcess(args, 1, "", "")
        if list(args[:3]) == ["git", "ls-files", "--others"]:
            return subprocess.CompletedProcess(args, 0, lines(untracked_), "")
        raise AssertionError("unexpected command: %r" % (args,))
    return run


def git_state(repo):
    return [sh_git(repo, *args) for args in (("stash", "list"), ("worktree", "list"), ("rev-parse", "HEAD"))]


@pytest.mark.process("git")
def test_working_tree_an_uncommitted_edit_to_a_script_prints_its_suite_and_leaves_stash_worktrees_and_head(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/py/test_foo.py": "# foo suite\n",
                 SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "tests/py/test_bar.py": "# bar suite\n"})
    base = commit_all(repo, "base")
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    before = git_state(repo)
    assert run_cli(affected, [base], cwd=repo) == (0, SUITES + "py/test_foo.py\n", "")
    assert git_state(repo) == before


@pytest.mark.process("git")
def test_working_tree_an_uncommitted_edit_inside_one_section_of_skill_md_prints_the_pytest_files_reading_it_or_skill_md_unsliced(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n"),
                 SCRIPTS_REL + "tests/py/unit/test_skill_whole.py":
                 'from pathlib import Path\ntext = Path("skills/tdd/SKILL.md").read_text()\n'})
    for name in ("Alpha", "Beta"):
        section_suite(repo, SKILL, name)
    base = commit_all(repo, "base")
    plant(repo, {SKILL: skill_text("## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text\n")})
    assert run_cli(affected, [base], cwd=repo) == (
        0, suites("py/unit/test_skill_alpha.py", "py/unit/test_skill_whole.py"), "")


def untracked_baz_suite(monkeypatch, tmp_path, extra=None):
    baz = SCRIPTS_REL + "tests/py/test_baz.py"
    monkeypatch.setattr(subprocess, "run", working_tree_git(untracked_=[baz]))
    plant(tmp_path, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "tests/py/test_foo.py": "# foo suite\n",
                     baz: "# baz suite\n", **(extra or {})})


def test_working_tree_a_new_untracked_suite_is_printed(monkeypatch, run_cli, affected, tmp_path):
    untracked_baz_suite(monkeypatch, tmp_path)
    code, out, err = run_cli(affected, ["base"], cwd=tmp_path)
    assert (code, SUITES + "py/test_baz.py" in out.splitlines()) == (0, True)


def test_working_tree_with_nothing_changed_since_base_exits_3_and_prints_nothing(
        monkeypatch, run_cli, affected, tmp_path):
    monkeypatch.setattr(subprocess, "run", working_tree_git())
    assert run_cli(affected, ["base"], cwd=tmp_path) == (3, "", "")


def test_main_prints_the_pytest_file_of_a_touched_script(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/foo.sh"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/test_foo.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_foo.py\n", "")
