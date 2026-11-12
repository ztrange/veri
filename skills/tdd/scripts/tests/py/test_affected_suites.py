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


def test_main_widens_to_every_suite_file_but_not_a_directory_named_like_one(tmp_path, monkeypatch, capsys, affected):
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


def test_main_widens_a_file_no_rule_handles_to_every_bash_suite_file_and_not_a_directory_named_like_one_1812(
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


def test_main_widens_a_file_under_a_projects_directory_like_any_file_no_rule_places_and_prints_none_of_its_tests(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["projects/other/serve.py"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_other.py").write_text("")
    (tests / "py/test_top.py").write_text("")
    project = tmp_path / "projects/other/tests"
    project.mkdir(parents=True)
    (project / "test_serve_get_root.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0,
        "skills/tdd/scripts/tests/py/test_top.py\n"
        "skills/tdd/scripts/tests/py/unit/test_other.py\n",
        "affected-suites: no rule places projects/other/serve.py; widening to every suite\n")


def test_main_prints_the_four_prompt_renderer_suites_for_a_develop_template_no_suite_names_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    renderers = ["py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py"]
    for name in renderers:
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
    for name in present:
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
    for name in present:
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
    for name in renderers:
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
    for name in renderers:
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
    for name in present:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in present))


def test_a_prompts_md_change_does_not_select_test_emitted_text_3128(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    for name in ("py/unit/test_build_develop_prompt.py", "py/unit/test_emitted_text.py"):
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (capsys.readouterr().out.splitlines(),) == (
        0, ["skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py"])


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
    spelled = sorted(set(re.findall(r'["/]((?:unit/|py/)?[\w-]+\.test\.sh|(?:py/(?:unit/)?)?test_\w+\.py)"', source)))
    return spelled, [p for p in spelled if not (tests / p).is_file()]


def test_every_suite_path_affected_suites_names_exists():
    """Its subject is source text: the suite paths veri/affected_suites.py spells."""
    spelled, missing = spelled_suites_missing((SCRIPTS / "veri" / "affected_suites.py").read_text(encoding="utf-8"), SCRIPTS / "tests")
    assert spelled and missing == [], "affected_suites.py names suites that are not files: %s" % ", ".join(missing)


@pytest.mark.parametrize("rename", [
    ('"py/unit/test_build_develop_prompt.py"', '"py/unit/test_build_gone_prompt.py"'),
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


def test_malformed_range_exits_2_with_the_usage_line(monkeypatch, run_cli, affected, tmp_path):
    results = []
    for range_ in ("abc..no-such-rev", "no-such-rev..abc"):
        monkeypatch.setattr(subprocess, "run", cli_git([], unresolvable="no-such-rev"))
        results.append(run_cli(affected, [range_], cwd=tmp_path))
    refusal = (2, "", "affected-suites: cannot resolve revision 'no-such-rev'\n" + USAGE)
    assert results == [refusal, refusal]


def test_empty_diff_exits_3_and_prints_nothing(monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(monkeypatch, run_cli, affected, tmp_path, [], {}) == (3, "", "")


def test_rule_5_a_rule_1_file_plus_a_file_no_rule_matches_prints_every_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "foo.sh", "docs/notes.md"],
        {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "baz.sh": "baz\n",
         "docs/notes.md": "# notes\n",
         SCRIPTS_REL + "tests/py/test_foo.py": "", SCRIPTS_REL + "tests/py/unit/test_baz.py": ""},
    ) == (0, SCRIPTS_REL + "tests/py/test_foo.py\n" + SCRIPTS_REL + "tests/py/unit/test_baz.py\n",
          "affected-suites: no rule places docs/notes.md; widening to every suite\n")


def test_a_widening_caused_by_two_unplaced_files_names_both_on_stderr(monkeypatch, run_cli, affected, tmp_path):
    code, out, err = affected_by(
        monkeypatch, run_cli, affected, tmp_path, ["notes.md", "memo.md"],
        {"notes.md": "# notes\n", "memo.md": "# memo\n", SCRIPTS_REL + "foo.sh": "foo\n",
         SCRIPTS_REL + "tests/py/test_foo.py": ""})
    assert (code, out, "notes.md" in err, "memo.md" in err) == (
        0, SCRIPTS_REL + "tests/py/test_foo.py\n", True, True)


def test_run_state_alone_exits_3_and_prints_nothing(monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [".tdd/issue-416.md", ".tdd/issue-416-refactor-owed.md"],
        {".tdd/issue-416.md": "- [x] step one\n", ".tdd/issue-416-refactor-owed.md": "refactor owed [x]\n",
         SCRIPTS_REL + "foo.sh": "foo\n"},
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


SKILL = "skills/tdd/SKILL.md"
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


def doc_edit_with_pytest_file(monkeypatch, run_cli, affected, tmp_path, doc, pytest_file):
    return affected_by(
        monkeypatch, run_cli, affected, tmp_path, [doc],
        {doc: "# doc\n\nstep 2\n",
         SCRIPTS_REL + "tests/py/unit/" + pytest_file: 'def test_step():\n    open("%s").read()\n' % doc,
         SCRIPTS_REL + "tests/py/unit/test_decoy_not_mentioning_it.py": "def test_other():\n    pass\n"})


@pytest.mark.parametrize("doc, pytest_file", [
    ("SCRIPTS", "test_catalogue.py"), ("PREFLIGHT", "test_preflight_file.py"),
    ("STOPPING", "test_stopping_file.py"), ("RECONCILE", "test_reconcile_file.py"),
    ("BAIL", "test_bail_file.py"), ("PIN", "test_pin_file.py"), ("SKILL-EDIT", "test_skill_edit_file.py"),
    ("RESUME", "test_resume_file.py"), ("REVISE", "test_revise_file.py"),
    ("STRUCTURAL", "test_structural_file.py"), ("PHASED", "test_phased_file.py"),
    ("REFACTOR-KIND", "test_refactor_kind_file.py"),
])
def test_an_edit_to_a_skill_doc_prints_exactly_the_pytest_file_mentioning_it_without_widening(
        monkeypatch, run_cli, affected, tmp_path, doc, pytest_file):
    assert doc_edit_with_pytest_file(monkeypatch, run_cli, affected, tmp_path, "skills/tdd/%s.md" % doc,
                                     pytest_file) == (0, SUITES + "py/unit/" + pytest_file + "\n", "")


def test_an_edit_to_draft_pr_md_prints_the_two_pytest_files_naming_it_and_neither_unplaced_nor_every_suite(
        monkeypatch, run_cli, affected, tmp_path):
    doc = "skills/tdd/DRAFT-PR.md"
    unit = SCRIPTS_REL + "tests/py/unit/"
    code, out, err = affected_by(
        monkeypatch, run_cli, affected, tmp_path, [doc],
        {doc: "# doc\n\nstep 2\n",
         unit + "test_reads_draft_pr_a.py": 'def test_a():\n    open("%s").read()\n' % doc,
         unit + "test_reads_draft_pr_b.py": 'def test_b():\n    open("%s").read()\n' % doc,
         unit + "test_decoy_one.py": "def test_c():\n    pass\n",
         unit + "test_decoy_two.py": "def test_d():\n    pass\n"})
    assert (code, set(out.splitlines()), err) == (
        0, {unit + "test_reads_draft_pr_a.py", unit + "test_reads_draft_pr_b.py"}, "")


def test_an_edit_to_suite_repair_md_prints_the_two_pytest_files_naming_it_and_neither_unplaced_nor_every_suite(
        monkeypatch, run_cli, affected, tmp_path):
    doc = "skills/tdd/SUITE-REPAIR.md"
    unit = SCRIPTS_REL + "tests/py/unit/"
    code, out, err = affected_by(
        monkeypatch, run_cli, affected, tmp_path, [doc],
        {doc: "# doc\n\nstep 2\n",
         unit + "test_reads_suite_repair_a.py": 'def test_a():\n    open("%s").read()\n' % doc,
         unit + "test_reads_suite_repair_b.py": 'def test_b():\n    open("%s").read()\n' % doc,
         unit + "test_decoy_one.py": "def test_c():\n    pass\n",
         unit + "test_decoy_two.py": "def test_d():\n    pass\n"})
    assert (code, set(out.splitlines()), err) == (
        0, {unit + "test_reads_suite_repair_a.py", unit + "test_reads_suite_repair_b.py"}, "")


def test_an_edit_to_diff_checked_md_prints_the_two_pytest_files_naming_it_and_neither_unplaced_nor_every_suite(
        monkeypatch, run_cli, affected, tmp_path):
    doc = "skills/tdd/DIFF-CHECKED.md"
    unit = SCRIPTS_REL + "tests/py/unit/"
    code, out, err = affected_by(
        monkeypatch, run_cli, affected, tmp_path, [doc],
        {doc: "# doc\n\nstep 2\n",
         unit + "test_reads_diff_checked_a.py": 'def test_a():\n    open("%s").read()\n' % doc,
         unit + "test_reads_diff_checked_b.py": 'def test_b():\n    open("%s").read()\n' % doc,
         unit + "test_decoy_one.py": "def test_c():\n    pass\n",
         unit + "test_decoy_two.py": "def test_d():\n    pass\n"})
    assert (code, set(out.splitlines()), err) == (
        0, {unit + "test_reads_diff_checked_a.py", unit + "test_reads_diff_checked_b.py"}, "")


def test_every_changed_input_prints_its_pytest_file_and_no_test_sh_path_beside_planted_bash_suites(
        monkeypatch, run_cli, affected, tmp_path):
    py = SCRIPTS_REL + "tests/py/"
    touched = ["CLAUDE.md", "skills/tdd/SKILL.md", "skills/tdd/PREFLIGHT.md",
               SCRIPTS_REL + "tests/fixtures/sample.txt", SCRIPTS_REL + "prompts/develop.md",
               SCRIPTS_REL + "alpha-tool.sh", SCRIPTS_REL + "veri/beta.py"]
    files = {name: "x\n" for name in touched}
    files.update({
        py + "unit/test_reads_skill.py": 'open("skills/tdd/SKILL.md")\n',
        py + "unit/test_reads_preflight.py": 'open("skills/tdd/PREFLIGHT.md")\n',
        py + "test_alpha_tool.py": "def test_x(): pass\n",
        py + "unit/test_beta.py": "def test_x(): pass\n",
    })
    for bash in ("claude-md", "skill", "preflight", "fixtures", "prompts", "alpha-tool", "beta"):
        files[SUITES + bash + ".test.sh"] = "#!/bin/bash\n"
        files[SUITES + "unit/" + bash + ".test.sh"] = "#!/bin/bash\n"
    code, out, err = affected_by(monkeypatch, run_cli, affected, tmp_path, touched, files)
    assert (code, out.splitlines(), err) == (0, sorted([
        py + "test_alpha_tool.py", py + "unit/test_beta.py",
        py + "unit/test_reads_preflight.py", py + "unit/test_reads_skill.py"]), "")


HEADER = '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\n'


def pytest_plants(*names):
    return {SCRIPTS_REL + "tests/py/test_%s.py" % n: "def test_x(): pass\n" for n in names}


def pytest_paths(*names):
    return "".join(SUITES + "py/test_%s.py\n" % n for n in names)


def test_rule_2_a_lib_prints_the_pytest_file_of_every_script_that_sources_it_and_no_others(
        monkeypatch, run_cli, affected, tmp_path):
    sourcing = '#!/usr/bin/env bash\nsource "$HERE/lib/bar.sh"\n'
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { :; }\n",
         SCRIPTS_REL + "alpha.sh": sourcing, SCRIPTS_REL + "beta.sh": sourcing,
         SCRIPTS_REL + "gamma.sh": "echo gamma\n", SCRIPTS_REL + "bar.sh": "echo bar\n",
         **pytest_plants("alpha", "beta", "gamma", "bar")},
    ) == (0, pytest_paths("alpha", "beta"), "")


def test_487_a_lib_file_whose_callers_source_line_ends_in_a_continuation_maps_to_that_callers_pytest_file(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n",
         SCRIPTS_REL + "alpha.sh": HEADER + 'source "$HERE/lib/bar.sh" \\\n  || { echo "alpha: cannot read lib/bar.sh" >&2; exit 2; }\n',
         SCRIPTS_REL + "gamma.sh": "echo gamma\n", **pytest_plants("alpha", "gamma")},
    ) == (0, pytest_paths("alpha"), "")


def test_487_a_caller_whose_source_line_ends_at_the_lib_path_with_or_without_a_trailing_quote_and_spaces_still_maps_to_its_pytest_file(
        monkeypatch, run_cli, affected, tmp_path):
    callers = {"alpha": 'source "$HERE/lib/bar.sh"\n', "beta": 'source "$HERE/lib/bar.sh"   \n',
               "delta": "source $HERE/lib/bar.sh\n", "epsilon": "source $HERE/lib/bar.sh  \n"}
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n", SCRIPTS_REL + "gamma.sh": "echo gamma\n",
         **{SCRIPTS_REL + n + ".sh": HEADER + line for n, line in callers.items()},
         **pytest_plants(*callers, "gamma")},
    ) == (0, pytest_paths("alpha", "beta", "delta", "epsilon"), "")


def test_487_a_comment_that_names_a_lib_file_is_still_not_a_dependency(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n",
         SCRIPTS_REL + "alpha.sh": HEADER + 'source "$HERE/lib/bar.sh"\n',
         SCRIPTS_REL + "beta.sh": HEADER + '# source "$HERE/lib/bar.sh" \\\n',
         SCRIPTS_REL + "gamma.sh": HEADER + '  # . "$HERE/lib/bar.sh"\n',
         **pytest_plants("alpha", "beta", "gamma")},
    ) == (0, pytest_paths("alpha"), "")


def module_shim(module):
    return '#!/bin/sh\nexec python3 -m veri.%s "$@"\n' % module


def test_a_touched_veri_module_prints_its_pytest_file_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "veri/event_log.py"],
        {SCRIPTS_REL + "veri/event_log.py": "def main(): return 2\n",
         SCRIPTS_REL + "tests/py/test_event_log.py": "def test_main(): pass\n",
         SCRIPTS_REL + "event-log.sh": module_shim("event_log"), SCRIPTS_REL + "bar.sh": "bar\n"},
    ) == (0, SUITES + "py/test_event_log.py\n", "")


def test_a_touched_pytest_file_under_tests_py_prints_itself_without_widening(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SCRIPTS_REL + "tests/py/test_status.py"],
        {SCRIPTS_REL + "tests/py/test_status.py": "def test_main(): assert False\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n"},
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


@pytest.mark.process("real git: the changed lines come from git diff -U0 between two commits")
@pytest.mark.parametrize("path", ["CLAUDE.md", "Makefile", "skills/merge/SKILL.md"])
def test_an_edit_inside_one_section_of_claude_md_makefile_or_a_skill_md_other_than_tdds_is_not_section_scoped(
        run_cli, affected, tmp_path, path):
    text = "# doc\n\n## Alpha\n\nalpha text%s\n\n## Beta\n\nbeta text\n"
    repo = new_git_repo(tmp_path)
    py = SCRIPTS_REL + "tests/py/unit/"
    plant(repo, {path: text % "",
                 py + "test_section_reader.py": 'def test_a():\n    section(doc, "## Alpha")\n',
                 py + "test_whole_reader.py": 'def test_a():\n    open("skills/tdd/SKILL.md").read()\n'})
    base = commit_all(repo, "base")
    plant(repo, {path: text % " 2"})
    commit_all(repo, "head")
    assert run_cli(affected, [base + "..HEAD"], cwd=repo) == (3, "", "")


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


def test_working_tree_with_nothing_changed_since_base_exits_3_and_prints_nothing(
        monkeypatch, run_cli, affected, tmp_path):
    monkeypatch.setattr(subprocess, "run", working_tree_git())
    assert run_cli(affected, ["base"], cwd=tmp_path) == (3, "", "")


def test_main_prints_the_pytest_file_of_a_touched_script_and_never_a_bash_suite(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/foo.sh"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/test_foo.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_foo.py\n", "")


@pytest.mark.tree_audit("copies the real test_skill_*.py readers into a scratch tree")
def test_a_one_section_edit_to_the_real_skill_md_selects_the_pytest_files_that_read_that_section_2980(
        monkeypatch, capsys, affected, tmp_path):
    base = cli_git(["skills/tdd/SKILL.md"])
    skill_lines = (ROOT / "skills/tdd/SKILL.md").read_text().splitlines()
    in_draft_pr = skill_lines.index("### 4. Draft PR") + 3

    def run(args, **kwargs):
        if list(args[:3]) == ["git", "diff", "-U0"]:
            return subprocess.CompletedProcess(
                args, 0, "@@ -%d +%d @@\n-old\n+new\n" % (in_draft_pr, in_draft_pr), "")
        return base(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    prefix = "skills/tdd/scripts/tests/py/"
    for name in ["skills/tdd/SKILL.md"] + [
            str(f.relative_to(ROOT)) for f in (ROOT / prefix).rglob("test_skill_*.py")]:
        plant(tmp_path, {name: (ROOT / name).read_text()})
    monkeypatch.chdir(tmp_path)
    code = affected.main(["base..head"])
    selected = capsys.readouterr().out.split()
    assert code == 0
    assert prefix + "unit/test_skill_draft_pr.py" in selected
    assert prefix + "unit/test_skill_sections.py" not in selected


def test_main_skips_a_directory_named_like_a_script_when_reading_lib_callers(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/lib/x.sh"]))
    monkeypatch.chdir(tmp_path)
    scripts = tmp_path / "skills/tdd/scripts"
    (scripts / "dir.sh").mkdir(parents=True)
    (scripts / "user.sh").write_text('source "$here/lib/x.sh"\n')
    plant(tmp_path, pytest_plants("user"))
    assert affected.main(["base..head"]) == 0
    assert capsys.readouterr().out == pytest_paths("user")


def test_main_keeps_the_suffix_of_a_script_named_only_by_its_suffix(tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/.sh"]))
    monkeypatch.chdir(tmp_path)
    plant(tmp_path, {SUITES + "py/test_.sh.py": "", SUITES + "py/test_.py": ""})
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (0, SUITES + "py/test_.sh.py\n", "")


def test_main_skips_a_directory_named_like_a_pytest_file_when_mapping_a_module(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/veri/foo.py"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / SUITES / "py/test_foo.py").mkdir(parents=True)
    plant(tmp_path, {SUITES + "py/unit/test_foo.py": ""})
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (0, SUITES + "py/unit/test_foo.py\n", "")


def test_working_tree_a_new_untracked_suite_is_printed(monkeypatch, run_cli, affected, tmp_path):
    baz = SUITES + "py/test_baz.py"
    monkeypatch.setattr(subprocess, "run", working_tree_git(untracked_=[baz], counted_untracked=[baz]))
    plant(tmp_path, {SCRIPTS_REL + "foo.sh": "foo\n", SUITES + "py/test_foo.py": "", baz: ""})
    assert run_cli(affected, ["base"], cwd=tmp_path) == (0, baz + "\n", "")


def test_run_state_a_tdd_ledger_alongside_a_script_change_prints_exactly_that_scripts_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [".tdd/issue-416.md", SCRIPTS_REL + "foo.sh"],
        {".tdd/issue-416.md": "- [x] step one\n", SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         **pytest_plants("foo", "bar")},
    ) == (0, pytest_paths("foo"), "")


def test_a_changed_makefile_or_claude_md_alone_places_without_widening_and_prints_no_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, ["Makefile"],
        {"Makefile": "test:\n", **pytest_plants("foo")}) == (3, "", "")
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, ["CLAUDE.md"],
        {"CLAUDE.md": "# veri\n"}) == (3, "", "")


def test_a_changed_fixture_alone_places_without_widening_and_prints_no_suite(
        monkeypatch, run_cli, affected, tmp_path):
    assert affected_by(
        monkeypatch, run_cli, affected, tmp_path, [SUITES + "fixtures/plan.md"],
        {SUITES + "fixtures/plan.md": "# plan\n", **pytest_plants("foo")}) == (3, "", "")


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_non_suite_file_the_base_changed_or_deleted_after_the_branch_point_contributes_no_suite(
        run_cli, affected, tmp_path):
    repo = new_git_repo(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
                 SCRIPTS_REL + "prompts/p.md": "a prompt\n",
                 **pytest_plants("foo", "bar"), SUITES + "py/unit/test_build_develop_prompt.py": "# renders\n"})
    commit_all(repo, "base")
    sh_git(repo, "checkout", "-q", "-b", "topic")
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    commit_all(repo, "head")
    sh_git(repo, "checkout", "-q", "main")
    plant(repo, {SCRIPTS_REL + "bar.sh": "bar 2\n"})
    (repo / SCRIPTS_REL / "prompts/p.md").unlink()
    commit_all(repo, "main changes a script and deletes a prompt")
    sh_git(repo, "checkout", "-q", "topic")
    assert topic_range(run_cli, affected, repo) == (0, pytest_paths("foo"), "")
