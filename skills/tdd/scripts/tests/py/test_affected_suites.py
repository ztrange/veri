"""In-process cases for veri/affected_suites.py, the module affected-suites.sh is a shim over."""
import importlib
import subprocess

import pytest

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


def test_main_prints_the_four_prompt_renderer_suites_for_a_develop_template_no_suite_names_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py").mkdir()
    renderers = ["build-develop-prompt.test.sh", "build-verify-prompt.test.sh",
                 "py/test_build_develop_prompt.py", "py/test_build_verify_prompt.py"]
    for name in renderers + ["other.test.sh"]:
        (tests / name).write_text("")
    (tests / "unit/emitted-text.test.sh").write_text('cksum < "$out"\n')
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in renderers + ["unit/emitted-text.test.sh"]))


def test_main_prints_the_four_prompt_renderer_suites_for_a_verify_template_no_suite_names_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/verify-green.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py").mkdir()
    renderers = ["build-develop-prompt.test.sh", "build-verify-prompt.test.sh",
                 "py/test_build_develop_prompt.py", "py/test_build_verify_prompt.py"]
    for name in renderers + ["other.test.sh"]:
        (tests / name).write_text("")
    (tests / "unit/emitted-text.test.sh").write_text('cksum < "$out"\n')
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in renderers + ["unit/emitted-text.test.sh"]))


def test_main_prints_the_four_prompt_renderer_suites_for_a_partial_no_suite_names_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/_leaf-safety.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py").mkdir()
    renderers = ["build-develop-prompt.test.sh", "build-verify-prompt.test.sh",
                 "py/test_build_develop_prompt.py", "py/test_build_verify_prompt.py"]
    for name in renderers + ["other.test.sh"]:
        (tests / name).write_text("")
    (tests / "unit/emitted-text.test.sh").write_text('cksum < "$out"\n')
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in renderers + ["unit/emitted-text.test.sh"]))


def test_main_prints_only_the_prompt_renderer_suites_that_exist_for_a_template_change_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py").mkdir()
    present = ["build-develop-prompt.test.sh", "py/test_build_develop_prompt.py"]
    for name in present + ["other.test.sh"]:
        (tests / name).write_text("")
    (tests / "unit/emitted-text.test.sh").write_text('cksum < "$out"\n')
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in present + ["unit/emitted-text.test.sh"]))


def test_main_prints_none_of_the_prompt_renderer_suites_for_a_change_outside_the_prompts_directory_1572(
        tmp_path, monkeypatch, capsys, affected):
    monkeypatch.setattr(subprocess, "run", fake_git(["skills/tdd/scripts/foo.sh"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py").mkdir()
    renderers = ["build-develop-prompt.test.sh", "build-verify-prompt.test.sh",
                 "py/test_build_develop_prompt.py", "py/test_build_verify_prompt.py"]
    for name in renderers + ["foo.test.sh"]:
        (tests / name).write_text("")
    (tests / "unit/emitted-text.test.sh").write_text('cksum < "$out"\n')
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
