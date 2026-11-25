"""In-process cases for veri/affected_suites.py, the module affected-suites.sh is a shim over."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS

USAGE = "usage: affected-suites.sh <base>..<head>\n"


@pytest.fixture
def affected():
    return importlib.import_module("veri.affected_suites")


def _install(fake_processes, fake_run):
    """Answers every git call through <fake_run>(args, **kwargs), which returns a CompletedProcess, and records it; the
    base commit is veri's own tree (`git cat-file -t <base>:skills/tdd/scripts/tests/py` is `tree`) when the working
    directory holds that directory, as the commit the case's tree stands for would."""
    def answer(line, **kwargs):
        args = fake.argvs[-1]
        if list(args[:3]) == ["git", "cat-file", "-t"]:
            own = args[3].endswith(":skills/tdd/scripts/tests/py") and os.path.isdir("skills/tdd/scripts/tests/py")
            return (0, b"tree\n", b"") if own else (128, b"", b"fatal: not a valid object name\n")
        done = fake_run(args, **kwargs)
        return done.returncode, done.stdout, done.stderr

    fake = fake_processes.answers({"git": answer})
    return fake


def test_main_returns_2_with_the_usage_line_for_no_argument_and_names_an_unresolvable_base(
        fake_processes, capsys, affected):
    _install(fake_processes, lambda args, **kwargs: subprocess.CompletedProcess(args, 1, "", ""))
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
        tmp_path, monkeypatch, capsys, affected, diff_code, returned, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/foo.sh"], diff_code))
    monkeypatch.chdir(tmp_path)
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (returned, "", "")


def test_main_maps_a_touched_module_to_its_pytest_file_in_the_fast_tier(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/veri/foo.py"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py/unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/unit/test_foo.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_foo.py\n", "")


def test_main_also_lists_the_pyflakes_gate_case_for_a_changed_veri_module(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/veri/foo.py"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py/unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/unit/test_foo.py").write_text("")
    (tmp_path / "skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0,
        "skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py\n"
        "skills/tdd/scripts/tests/py/unit/test_foo.py\n",
        "")


def test_main_selects_a_changed_pytest_file_in_the_fast_tier_as_itself(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/tests/py/unit/test_bar.py"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py/unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/unit/test_bar.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_bar.py\n", "")


def test_main_also_lists_the_pyflakes_gate_case_for_a_changed_unit_test_file(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/tests/py/unit/test_bar.py"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py/unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/unit/test_bar.py").write_text("")
    (tmp_path / "skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0,
        "skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py\n"
        "skills/tdd/scripts/tests/py/unit/test_bar.py\n",
        "")


def test_main_leaves_out_the_pyflakes_gate_case_for_a_range_changing_only_a_markdown_file(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["README.md"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py/unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/unit/test_readme.py").write_text('README = ROOT / "README.md"\n')
    (tmp_path / "skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_readme.py\n", "")


def test_main_leaves_out_the_pyflakes_gate_case_for_a_range_changing_only_a_shim(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/foo-bar.sh"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/veri").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/veri/foo_bar.py").write_text("")
    (tmp_path / "skills/tdd/scripts/tests/py/unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/unit/test_foo_bar.py").write_text("")
    (tmp_path / "skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/unit/test_foo_bar.py\n", "")


def test_main_leaves_out_the_pyflakes_gate_case_for_a_foreign_trees_range_changing_a_py_file(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    gate = "skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py"
    tracked = ["src/foo.py", "tests/test_foo.py", gate]

    def answer(line, **kwargs):  # the base commit has no skills/tdd/scripts/tests/py: a foreign tree (#4263)
        args = fake.argvs[-1]
        if list(args[:2]) == ["git", "rev-parse"]:
            return 0, "abc\n", ""
        if list(args[:3]) == ["git", "cat-file", "-t"]:
            return 128, b"", b"fatal: not a valid object name\n"
        if list(args[:3]) == ["git", "diff", "--name-only"]:
            return 0, "src/foo.py\n", ""
        if list(args[:2]) == ["git", "ls-files"]:
            return 0, "".join(f + "\0" for f in tracked), ""
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({"git": answer})
    monkeypatch.chdir(tmp_path)
    for name, text in {"src/foo.py": "x = 1\n", "tests/test_foo.py": "import foo\n", gate: ""}.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text)
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (0, "tests/test_foo.py\n", "")


def test_main_maps_a_readme_edit_to_the_suite_files_naming_it_and_not_a_directory_named_like_one(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["README.md"]))
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


def test_main_exits_3_naming_a_file_no_rule_handles_and_never_widens_to_every_suite_4333(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["docs/notes.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_other.py").write_text("")
    (tests / "py/test_top.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        3, "", "affected-suites: no rule places docs/notes.md; no test file covers them, so the full suite at the PR runs them\n")


def test_main_lists_the_pyflakes_gate_case_for_a_changed_py_file_no_rule_places(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["projects/other/serve.py"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py/unit").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py\n",
        "affected-suites: no rule places projects/other/serve.py; no test file covers them, so the full suite at the PR runs them\n")


def test_main_treats_a_file_under_a_projects_directory_like_any_file_no_rule_places_and_prints_none_of_its_tests(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["projects/other/serve.py"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    (tests / "py/unit/test_other.py").write_text("")
    (tests / "py/test_top.py").write_text("")
    project = tmp_path / "projects/other/tests"
    project.mkdir(parents=True)
    (project / "test_serve_get_root.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        3, "", "affected-suites: no rule places projects/other/serve.py; no test file covers them, so the full suite at the PR runs them\n")


def test_main_prints_the_four_prompt_renderer_suites_for_a_develop_template_no_suite_names_1572(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/prompts/verify-green.md"]))
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/prompts/verify-green.md"]))
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/prompts/_leaf-safety.md"]))
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "unit").mkdir(parents=True)
    (tests / "py/unit").mkdir(parents=True)
    present = ["py/unit/test_build_develop_prompt.py"]
    for name in present:
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (sorted(capsys.readouterr().out.splitlines()),) == (
        0, sorted("skills/tdd/scripts/tests/" + n for n in present))


def test_a_prompts_md_change_does_not_select_test_emitted_text_3128(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/prompts/develop-red.md"]))
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "skills/tdd/scripts/tests"
    (tests / "py/unit").mkdir(parents=True)
    for name in ("py/unit/test_build_develop_prompt.py", "py/unit/test_emitted_text.py"):
        (tests / name).write_text("")
    assert (affected.main(["base..head"]),) + (capsys.readouterr().out.splitlines(),) == (
        0, ["skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py"])


def test_main_prints_the_pytest_files_that_read_the_edited_skill_section_through_the_helper_only(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
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
        fence, tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\n%s\n## x\nalpha body\n%s\n## Beta\nbeta body\n" % (fence, fence))
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\n", "")


def test_main_attributes_an_edit_by_the_fence_answer_of_the_markdown_sections_reader_1976(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\n````\n```\n## x\nalpha body\n````\n## Beta\nbeta body\n")
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_x.py").write_text('section(SKILL, "## x")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\n", "")


def test_main_reads_a_heading_after_a_fence_line_indented_four_spaces_as_a_heading_1687(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\n    ```\n## Beta\nx\nbeta body\n## Gamma\n")
    (py / "test_alpha.py").write_text('section(SKILL, "## Alpha")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_beta.py\n", "")


def test_main_prints_a_pytest_file_whose_helper_call_spans_lines_with_the_heading_on_its_own(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_alpha.py").write_text('section(\n    SKILL,\n    "## Alpha",\n)\n')
    (py / "test_beta.py").write_text('section(\n    SKILL,\n    "## Beta",\n)\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha.py\n", "")


def test_main_prints_a_fast_tier_pytest_file_that_reads_the_edited_skill_section_or_renders_an_edited_prompt_1633(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
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
        tmp_path, monkeypatch, capsys, affected, direct_read, fake_processes):
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

    _install(fake_processes, fake_run)
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
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n## Gamma\ngamma body\n")
    (py / "test_alpha_gamma.py").write_text('section(SKILL, "## Alpha")\nsection(SKILL, "## Gamma")\n')
    (py / "test_beta.py").write_text('section(SKILL, "## Beta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_alpha_gamma.py\n", "")


def test_main_prints_a_pytest_file_with_a_literal_and_a_built_heading_for_an_edit_in_a_section_neither_names_1581(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_mixed.py").write_text('section(SKILL, "## Alpha")\nsection(SKILL, "## " + "Be" + "ta")\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_mixed.py\n", "")


def test_main_prints_a_pytest_file_with_a_literal_and_an_expression_heading_for_an_edit_in_a_section_no_literal_names_1581(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
    monkeypatch.chdir(tmp_path)
    py = tmp_path / "skills/tdd/scripts/tests/py"
    py.mkdir(parents=True)
    (tmp_path / skill).write_text("## Alpha\nalpha body\n## Beta\nbeta body\n")
    (py / "test_expr.py").write_text('section(SKILL, "## Alpha")\nsection(SKILL, h.strip())\n')
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_expr.py\n", "")


def test_main_prints_a_pytest_file_importing_the_section_helper_under_another_name_for_an_edit_in_a_section_its_literal_does_not_name_1581(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
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

    _install(fake_processes, fake_run)
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
        tmp_path, monkeypatch, capsys, affected, read, fake_processes):
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

    _install(fake_processes, fake_run)
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


def affected_by(fake_processes, run_cli, affected, tmp_path, touched, files, range_="base..head", counted=()):
    _install(fake_processes, cli_git(touched, counted=counted))
    plant(tmp_path, files)
    return run_cli(affected, [range_], cwd=tmp_path)


def test_malformed_range_exits_2_with_the_usage_line(fake_processes, run_cli, affected, tmp_path):
    results = []
    for range_ in ("abc..no-such-rev", "no-such-rev..abc"):
        _install(fake_processes, cli_git([], unresolvable="no-such-rev"))
        results.append(run_cli(affected, [range_], cwd=tmp_path))
    refusal = (2, "", "affected-suites: cannot resolve revision 'no-such-rev'\n" + USAGE)
    assert results == [refusal, refusal]


def test_empty_diff_exits_3_and_prints_nothing(fake_processes, run_cli, affected, tmp_path):
    assert affected_by(fake_processes, run_cli, affected, tmp_path, [], {}) == (3, "", "")


def test_a_placed_file_plus_a_file_no_rule_places_prints_only_the_placed_files_suites_and_names_the_other_4333(
        fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [SCRIPTS_REL + "foo.sh", "docs/notes.md"],
        {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n", SCRIPTS_REL + "baz.sh": "baz\n",
         "docs/notes.md": "# notes\n",
         SCRIPTS_REL + "tests/py/test_foo.py": "", SCRIPTS_REL + "tests/py/unit/test_baz.py": ""},
    ) == (0, SCRIPTS_REL + "tests/py/test_foo.py\n",
          "affected-suites: no rule places docs/notes.md; no test file covers them, so the full suite at the PR runs them\n")


def test_two_unplaced_files_alone_exit_3_naming_both_on_stderr(fake_processes, run_cli, affected, tmp_path):
    code, out, err = affected_by(
        fake_processes, run_cli, affected, tmp_path, ["notes.md", "memo.md"],
        {"notes.md": "# notes\n", "memo.md": "# memo\n", SCRIPTS_REL + "foo.sh": "foo\n",
         SCRIPTS_REL + "tests/py/test_foo.py": ""})
    assert (code, out, "notes.md" in err, "memo.md" in err) == (3, "", True, True)


def test_run_state_alone_exits_3_and_prints_nothing(fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [".tdd/issue-416.md", ".tdd/issue-416-refactor-owed.md"],
        {".tdd/issue-416.md": "- [x] step one\n", ".tdd/issue-416-refactor-owed.md": "refactor owed [x]\n",
         SCRIPTS_REL + "foo.sh": "foo\n"},
    ) == (3, "", "")


def test_run_state_alongside_a_file_no_rule_places_exits_3_naming_that_file(
        fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [".tdd/issue-416.md", "notes.md"],
        {".tdd/issue-416.md": "- [x] step one\n", "notes.md": "# notes\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         SCRIPTS_REL + "tests/py/test_foo.py": "", SCRIPTS_REL + "tests/py/unit/test_bar.py": ""},
    ) == (3, "", "affected-suites: no rule places notes.md; no test file covers them, so the full suite at the PR runs them\n")


SKILL = "skills/tdd/SKILL.md"


def doc_edit_with_pytest_file(fake_processes, run_cli, affected, tmp_path, doc, pytest_file):
    return affected_by(
        fake_processes, run_cli, affected, tmp_path, [doc],
        {doc: "# doc\n\nstep 2\n",
         SCRIPTS_REL + "tests/py/unit/" + pytest_file: 'def test_step():\n    open("%s").read()\n' % doc,
         SCRIPTS_REL + "tests/py/unit/test_decoy_not_mentioning_it.py": "def test_other():\n    pass\n"})


@pytest.mark.parametrize("doc, pytest_file", [
    ("SCRIPTS", "test_catalogue.py"), ("PREFLIGHT", "test_preflight_file.py"),
    ("STOPPING", "test_stopping_file.py"), ("RECONCILE", "test_reconcile_file.py"),
    ("BAIL", "test_bail_file.py"), ("PIN", "test_pin_file.py"), ("SKILL-EDIT", "test_skill_edit_file.py"),
    ("RESUME", "test_resume_file.py"), ("REVISE", "test_revise_file.py"),
    ("STRUCTURAL", "test_structural_file.py"), ("PHASED", "test_phased_file.py"),
    ("REFACTOR-KIND", "test_refactor_kind_file.py"), ("LEGACY", "test_legacy_file.py"),
])
def test_an_edit_to_a_skill_doc_prints_exactly_the_pytest_file_mentioning_it_without_widening(
        fake_processes, run_cli, affected, tmp_path, doc, pytest_file):
    assert doc_edit_with_pytest_file(fake_processes, run_cli, affected, tmp_path, "skills/tdd/%s.md" % doc,
                                     pytest_file) == (0, SUITES + "py/unit/" + pytest_file + "\n", "")


def test_an_edit_to_draft_pr_md_prints_the_two_pytest_files_naming_it_and_neither_unplaced_nor_every_suite(
        fake_processes, run_cli, affected, tmp_path):
    doc = "skills/tdd/DRAFT-PR.md"
    unit = SCRIPTS_REL + "tests/py/unit/"
    code, out, err = affected_by(
        fake_processes, run_cli, affected, tmp_path, [doc],
        {doc: "# doc\n\nstep 2\n",
         unit + "test_reads_draft_pr_a.py": 'def test_a():\n    open("%s").read()\n' % doc,
         unit + "test_reads_draft_pr_b.py": 'def test_b():\n    open("%s").read()\n' % doc,
         unit + "test_decoy_one.py": "def test_c():\n    pass\n",
         unit + "test_decoy_two.py": "def test_d():\n    pass\n"})
    assert (code, set(out.splitlines()), err) == (
        0, {unit + "test_reads_draft_pr_a.py", unit + "test_reads_draft_pr_b.py"}, "")


def test_an_edit_to_suite_repair_md_prints_the_two_pytest_files_naming_it_and_neither_unplaced_nor_every_suite(
        fake_processes, run_cli, affected, tmp_path):
    doc = "skills/tdd/SUITE-REPAIR.md"
    unit = SCRIPTS_REL + "tests/py/unit/"
    code, out, err = affected_by(
        fake_processes, run_cli, affected, tmp_path, [doc],
        {doc: "# doc\n\nstep 2\n",
         unit + "test_reads_suite_repair_a.py": 'def test_a():\n    open("%s").read()\n' % doc,
         unit + "test_reads_suite_repair_b.py": 'def test_b():\n    open("%s").read()\n' % doc,
         unit + "test_decoy_one.py": "def test_c():\n    pass\n",
         unit + "test_decoy_two.py": "def test_d():\n    pass\n"})
    assert (code, set(out.splitlines()), err) == (
        0, {unit + "test_reads_suite_repair_a.py", unit + "test_reads_suite_repair_b.py"}, "")


def test_an_edit_to_diff_checked_md_prints_the_two_pytest_files_naming_it_and_neither_unplaced_nor_every_suite(
        fake_processes, run_cli, affected, tmp_path):
    doc = "skills/tdd/DIFF-CHECKED.md"
    unit = SCRIPTS_REL + "tests/py/unit/"
    code, out, err = affected_by(
        fake_processes, run_cli, affected, tmp_path, [doc],
        {doc: "# doc\n\nstep 2\n",
         unit + "test_reads_diff_checked_a.py": 'def test_a():\n    open("%s").read()\n' % doc,
         unit + "test_reads_diff_checked_b.py": 'def test_b():\n    open("%s").read()\n' % doc,
         unit + "test_decoy_one.py": "def test_c():\n    pass\n",
         unit + "test_decoy_two.py": "def test_d():\n    pass\n"})
    assert (code, set(out.splitlines()), err) == (
        0, {unit + "test_reads_diff_checked_a.py", unit + "test_reads_diff_checked_b.py"}, "")


def test_every_changed_input_prints_its_pytest_file_and_no_test_sh_path_beside_planted_bash_suites(
        fake_processes, run_cli, affected, tmp_path):
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
    code, out, err = affected_by(fake_processes, run_cli, affected, tmp_path, touched, files)
    assert (code, out.splitlines(), err) == (0, sorted([
        py + "test_alpha_tool.py", py + "unit/test_beta.py",
        py + "unit/test_reads_preflight.py", py + "unit/test_reads_skill.py"]), "")


HEADER = '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\n'


def pytest_plants(*names):
    return {SCRIPTS_REL + "tests/py/test_%s.py" % n: "def test_x(): pass\n" for n in names}


def pytest_paths(*names):
    return "".join(SUITES + "py/test_%s.py\n" % n for n in names)


def test_rule_2_a_lib_prints_the_pytest_file_of_every_script_that_sources_it_and_no_others(
        fake_processes, run_cli, affected, tmp_path):
    sourcing = '#!/usr/bin/env bash\nsource "$HERE/lib/bar.sh"\n'
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { :; }\n",
         SCRIPTS_REL + "alpha.sh": sourcing, SCRIPTS_REL + "beta.sh": sourcing,
         SCRIPTS_REL + "gamma.sh": "echo gamma\n", SCRIPTS_REL + "bar.sh": "echo bar\n",
         **pytest_plants("alpha", "beta", "gamma", "bar")},
    ) == (0, pytest_paths("alpha", "beta"), "")


def test_487_a_lib_file_whose_callers_source_line_ends_in_a_continuation_maps_to_that_callers_pytest_file(
        fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n",
         SCRIPTS_REL + "alpha.sh": HEADER + 'source "$HERE/lib/bar.sh" \\\n  || { echo "alpha: cannot read lib/bar.sh" >&2; exit 2; }\n',
         SCRIPTS_REL + "gamma.sh": "echo gamma\n", **pytest_plants("alpha", "gamma")},
    ) == (0, pytest_paths("alpha"), "")


def test_487_a_caller_whose_source_line_ends_at_the_lib_path_with_or_without_a_trailing_quote_and_spaces_still_maps_to_its_pytest_file(
        fake_processes, run_cli, affected, tmp_path):
    callers = {"alpha": 'source "$HERE/lib/bar.sh"\n', "beta": 'source "$HERE/lib/bar.sh"   \n',
               "delta": "source $HERE/lib/bar.sh\n", "epsilon": "source $HERE/lib/bar.sh  \n"}
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n", SCRIPTS_REL + "gamma.sh": "echo gamma\n",
         **{SCRIPTS_REL + n + ".sh": HEADER + line for n, line in callers.items()},
         **pytest_plants(*callers, "gamma")},
    ) == (0, pytest_paths("alpha", "beta", "delta", "epsilon"), "")


def test_487_a_comment_that_names_a_lib_file_is_still_not_a_dependency(
        fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [SCRIPTS_REL + "lib/bar.sh"],
        {SCRIPTS_REL + "lib/bar.sh": "bar_fn() { echo 2; }\n",
         SCRIPTS_REL + "alpha.sh": HEADER + 'source "$HERE/lib/bar.sh"\n',
         SCRIPTS_REL + "beta.sh": HEADER + '# source "$HERE/lib/bar.sh" \\\n',
         SCRIPTS_REL + "gamma.sh": HEADER + '  # . "$HERE/lib/bar.sh"\n',
         **pytest_plants("alpha", "beta", "gamma")},
    ) == (0, pytest_paths("alpha"), "")


def module_shim(module):
    return '#!/bin/sh\nexec python3 -m veri.%s "$@"\n' % module


def test_a_touched_veri_module_prints_its_pytest_file_without_widening(
        fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [SCRIPTS_REL + "veri/event_log.py"],
        {SCRIPTS_REL + "veri/event_log.py": "def main(): return 2\n",
         SCRIPTS_REL + "tests/py/test_event_log.py": "def test_main(): pass\n",
         SCRIPTS_REL + "event-log.sh": module_shim("event_log"), SCRIPTS_REL + "bar.sh": "bar\n"},
    ) == (0, SUITES + "py/test_event_log.py\n", "")


def test_a_touched_pytest_file_under_tests_py_prints_itself_without_widening(
        fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [SCRIPTS_REL + "tests/py/test_status.py"],
        {SCRIPTS_REL + "tests/py/test_status.py": "def test_main(): assert False\n",
         SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n"},
    ) == (0, SUITES + "py/test_status.py\n", "")


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
        fake_processes, run_cli, affected, tmp_path):
    _install(fake_processes, working_tree_git())
    assert run_cli(affected, ["base"], cwd=tmp_path) == (3, "", "")


def test_main_prints_the_pytest_file_of_a_touched_script_and_never_a_bash_suite(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/foo.sh"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py").mkdir(parents=True)
    (tmp_path / "skills/tdd/scripts/tests/py/test_foo.py").write_text("")
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "skills/tdd/scripts/tests/py/test_foo.py\n", "")


def test_main_skips_a_directory_named_like_a_script_when_reading_lib_callers(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/lib/x.sh"]))
    monkeypatch.chdir(tmp_path)
    scripts = tmp_path / "skills/tdd/scripts"
    (scripts / "dir.sh").mkdir(parents=True)
    (scripts / "user.sh").write_text('source "$here/lib/x.sh"\n')
    plant(tmp_path, pytest_plants("user"))
    assert affected.main(["base..head"]) == 0
    assert capsys.readouterr().out == pytest_paths("user")


def test_main_keeps_the_suffix_of_a_script_named_only_by_its_suffix(tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/.sh"]))
    monkeypatch.chdir(tmp_path)
    plant(tmp_path, {SUITES + "py/test_.sh.py": "", SUITES + "py/test_.py": ""})
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (0, SUITES + "py/test_.sh.py\n", "")


def test_main_skips_a_directory_named_like_a_pytest_file_when_mapping_a_module(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    _install(fake_processes, fake_git(["skills/tdd/scripts/veri/foo.py"]))
    monkeypatch.chdir(tmp_path)
    (tmp_path / SUITES / "py/test_foo.py").mkdir(parents=True)
    plant(tmp_path, {SUITES + "py/unit/test_foo.py": ""})
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (0, SUITES + "py/unit/test_foo.py\n", "")


def test_working_tree_a_new_untracked_suite_is_printed(fake_processes, run_cli, affected, tmp_path):
    baz = SUITES + "py/test_baz.py"
    _install(fake_processes, working_tree_git(untracked_=[baz], counted_untracked=[baz]))
    plant(tmp_path, {SCRIPTS_REL + "foo.sh": "foo\n", SUITES + "py/test_foo.py": "", baz: ""})
    assert run_cli(affected, ["base"], cwd=tmp_path) == (0, baz + "\n", "")


def test_run_state_a_tdd_ledger_alongside_a_script_change_prints_exactly_that_scripts_suite(
        fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [".tdd/issue-416.md", SCRIPTS_REL + "foo.sh"],
        {".tdd/issue-416.md": "- [x] step one\n", SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
         **pytest_plants("foo", "bar")},
    ) == (0, pytest_paths("foo"), "")


def test_a_changed_makefile_or_claude_md_alone_places_without_widening_and_prints_no_suite(
        fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, ["Makefile"],
        {"Makefile": "test:\n", **pytest_plants("foo")}) == (3, "", "")
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, ["CLAUDE.md"],
        {"CLAUDE.md": "# veri\n"}) == (3, "", "")


def test_a_changed_fixture_alone_places_without_widening_and_prints_no_suite(
        fake_processes, run_cli, affected, tmp_path):
    assert affected_by(
        fake_processes, run_cli, affected, tmp_path, [SUITES + "fixtures/plan.md"],
        {SUITES + "fixtures/plan.md": "# plan\n", **pytest_plants("foo")}) == (3, "", "")


@pytest.mark.parametrize("name", ["pytest_leg", "network_guard", "small_case_guard", "serial_seen", "private_tmp_path"])
def test_a_changed_leg_module_under_tests_leg_selects_what_it_selected_under_veri_4051(affected, tmp_path, monkeypatch,
                                                                                         name):
    """The leg moved from veri/ to tests/leg/ (#4051); a changed leg module still selects its own test files."""
    monkeypatch.chdir(tmp_path)
    for test in ("skills/tdd/scripts/tests/py/test_%s.py" % name, "skills/tdd/scripts/tests/py/unit/test_%s.py" % name):
        (tmp_path / test).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / test).write_text("def test_x():\n    pass\n")

    selected = affected.suite_of("skills/tdd/scripts/tests/leg/%s.py" % name)

    assert selected == affected.suite_of("skills/tdd/scripts/veri/%s.py" % name) == [
        "skills/tdd/scripts/tests/py/test_%s.py" % name, "skills/tdd/scripts/tests/py/unit/test_%s.py" % name]


PY = "skills/tdd/scripts/tests/py/"


def test_a_changed_module_lists_its_process_test_file_beside_its_other_test_files_4425(affected, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plant(tmp_path, {PY + "test_foo.py": "", PY + "unit/test_foo.py": "", PY + "test_foo_process.py": "",
                     PY + "unit/test_foo_process.py": ""})

    assert sorted(affected.suite_of("skills/tdd/scripts/veri/foo.py")) == [
        PY + "test_foo.py", PY + "test_foo_process.py", PY + "unit/test_foo.py"]


def test_a_changed_shim_lists_the_process_test_file_of_its_name_with_underscores_4425(affected, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plant(tmp_path, {PY + "unit/test_foo_bar.py": "", PY + "test_foo_bar_process.py": "",
                     PY + "test_foo-bar_process.py": ""})

    assert sorted(affected.suite_of("skills/tdd/scripts/foo-bar.sh")) == [
        PY + "test_foo_bar_process.py", PY + "unit/test_foo_bar.py"]


NAMING = {
    PY + "test_imports_it_process.py": 'step = importlib.import_module("veri.foo_bar")\n',
    PY + "test_runs_its_shim_process.py": 'subprocess.run([str(SCRIPTS / "foo-bar.sh")])\n',
    PY + "test_runs_its_module_process.py": 'subprocess.run(["python3", "skills/tdd/scripts/veri/foo_bar.py"])\n',
    PY + "test_names_neither_process.py": 'run("foo_bar")\nimportlib.import_module("veri.foo_bar_baz")\n'
                                          'subprocess.run([str(SCRIPTS / "foo-bar-baz.sh")])\n',
    PY + "unit/test_unit_imports_it.py": 'importlib.import_module("veri.foo_bar")\n',
    PY + "test_imports_it.py": 'importlib.import_module("veri.foo_bar")\n',
}
NAMED = [PY + "test_imports_it_process.py", PY + "test_runs_its_module_process.py", PY + "test_runs_its_shim_process.py"]


@pytest.mark.parametrize("changed", ["skills/tdd/scripts/veri/foo_bar.py", "skills/tdd/scripts/foo-bar.sh"])
def test_a_changed_module_or_shim_lists_every_process_test_file_importing_or_running_it_by_name_and_no_other_4425(
        affected, tmp_path, monkeypatch, changed):
    monkeypatch.chdir(tmp_path)
    plant(tmp_path, NAMING)

    assert sorted(set(affected.suite_of(changed))) == NAMED


HOP = {
    "skills/tdd/scripts/veri/helper.py": "def go():\n    pass\n",
    "skills/tdd/scripts/veri/user.py": "import os\nimport helper\n",
    "skills/tdd/scripts/veri/other_user.py": "from helper import go\n",
    "skills/tdd/scripts/veri/mentions.py": "# helper is not imported here\nimport os\n",
    PY + "test_halves_process.py": 'subprocess.run([str(SCRIPTS / "user.sh")])\n',
    PY + "test_other_halves_process.py": 'importlib.import_module("veri.other_user")\n',
    PY + "test_mentions_process.py": 'importlib.import_module("veri.mentions")\n',
    PY + "unit/test_user.py": 'importlib.import_module("veri.user")\n',
}


def test_a_changed_module_no_process_file_names_lists_the_process_files_naming_a_module_importing_it_4425(
        affected, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plant(tmp_path, HOP)

    assert sorted(set(affected.suite_of("skills/tdd/scripts/veri/helper.py"))) == [
        PY + "test_halves_process.py", PY + "test_other_halves_process.py"]


def test_a_changed_module_a_process_file_names_lists_no_process_file_of_its_importers_4425(
        affected, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plant(tmp_path, {**HOP, PY + "test_names_helper_process.py": 'importlib.import_module("veri.helper")\n'})

    assert sorted(set(affected.suite_of("skills/tdd/scripts/veri/helper.py"))) == [PY + "test_names_helper_process.py"]


def test_a_changed_module_lists_the_process_files_running_a_shim_of_another_name_that_execs_it_4425(
        affected, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plant(tmp_path, {
        "skills/tdd/scripts/veri/prd_tally.py": "def main():\n    pass\n",
        "skills/tdd/scripts/tally-up.sh": '#!/bin/sh\n# tally-up.sh: a shim\nexec "$py" "$(dirname "$0")/veri/prd_tally.py" "$@"\n',
        "skills/tdd/scripts/mentions-tally.sh": '#!/bin/sh\n# reads what veri/prd_tally.py writes\nexec "$py" "$(dirname "$0")/veri/other.py"\n',
        PY + "test_tally_process.py": 'subprocess.run([str(SCRIPTS / "tally-up.sh")])\n',
        PY + "test_mentions_tally_process.py": 'subprocess.run([str(SCRIPTS / "mentions-tally.sh")])\n',
    })

    assert sorted(set(affected.suite_of("skills/tdd/scripts/veri/prd_tally.py"))) == [PY + "test_tally_process.py"]
