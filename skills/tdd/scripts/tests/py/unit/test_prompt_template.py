"""In-process cases for veri/prompt_template.py, the template mechanics the prompt builders share."""
import importlib

import pytest


@pytest.fixture
def prompt_template():
    return importlib.import_module("veri.prompt_template")


def test_read_returns_a_files_bytes_without_its_trailing_newlines(tmp_path, prompt_template):
    path = tmp_path / "a.md"
    path.write_bytes(b"line one\n\nline two\n\n\n")

    assert prompt_template.read(str(path)) == b"line one\n\nline two"


def test_read_raises_oserror_for_a_missing_file(tmp_path, prompt_template):
    with pytest.raises(OSError):
        prompt_template.read(str(tmp_path / "missing.md"))


def test_spec_text_of_returns_the_spec_bytes_and_empty_bytes_when_it_is_unreadable(tmp_path, prompt_template):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n\nbody\n")

    assert prompt_template.spec_text_of(str(spec)) == b"# spec\n\nbody"
    assert prompt_template.spec_text_of(str(tmp_path / "missing.md")) == b""


def test_has_heading_matches_a_whole_level_two_heading_line_only(prompt_template):
    text = b"# Bug\n\n## Bugs\nprose ## Bug\n### Bug\n## Bug \t\n"

    assert prompt_template.has_heading(text, b"Bug") is True
    assert prompt_template.has_heading(b"## Bugs\n## bug\nx ## Bug\n", b"Bug") is False


def test_expand_includes_inlines_each_partial_recursively_and_leaves_other_text(tmp_path, prompt_template):
    (tmp_path / "a.md").write_bytes(b"A[{{INCLUDE:b.md}}]\n")
    (tmp_path / "b.md").write_bytes(b"B\n")
    prompts = str(tmp_path).encode()

    out = prompt_template.expand_includes(b"head {{INCLUDE:a.md}} mid {{INCLUDE:b.md}} tail {{X}}", prompts)

    assert out == b"head A[B] mid B tail {{X}}"


def test_expand_includes_raises_include_refused_naming_a_missing_partial(tmp_path, prompt_template):
    prompts = str(tmp_path).encode()

    with pytest.raises(prompt_template.IncludeRefused) as refusal:
        prompt_template.expand_includes(b"{{INCLUDE:gone.md}}", prompts)

    assert refusal.value.args[0] == b"missing partial: " + prompts + b"/gone.md"


def test_expand_includes_raises_include_refused_for_a_partial_that_includes_itself(tmp_path, prompt_template):
    (tmp_path / "loop.md").write_bytes(b"{{INCLUDE:loop.md}}")
    prompts = str(tmp_path).encode()

    with pytest.raises(prompt_template.IncludeRefused) as refusal:
        prompt_template.expand_includes(b"{{INCLUDE:loop.md}}", prompts)

    assert refusal.value.args[0] == b"partial includes itself: " + prompts + b"/loop.md"


def test_expand_includes_of_a_directory_partial_inlines_nothing_and_reports_it_on_stderr(
        tmp_path, capsysbinary, prompt_template):
    (tmp_path / "dir").mkdir()
    prompts = str(tmp_path).encode()

    out = prompt_template.expand_includes(b"a{{INCLUDE:dir}}b", prompts)

    assert out == b"ab"
    assert capsysbinary.readouterr().err == b"cat: " + prompts + b"/dir: Is a directory\n"


def test_fill_replaces_each_named_placeholder_in_order_so_a_value_may_carry_a_later_placeholder(prompt_template):
    text = b"{{A}} {{B}} {{A}} {{C}}"

    out = prompt_template.fill(text, [(b"A", b"<{{B}}>"), (b"B", b"b"), (b"Z", b"unused")])

    assert out == b"<b> b <b> {{C}}"


def test_fill_calls_a_callable_value_only_when_its_placeholder_is_still_in_the_text(prompt_template):
    calls = []

    def lazy():
        calls.append(1)
        return b"lazy"

    assert prompt_template.fill(b"{{L}}!", [(b"L", lazy)]) == b"lazy!"
    assert prompt_template.fill(b"none", [(b"L", lazy)]) == b"none"
    assert len(calls) == 1


def test_fill_lets_a_callable_values_include_refusal_escape(prompt_template):
    def refuses():
        raise prompt_template.IncludeRefused(b"missing partial: x")

    with pytest.raises(prompt_template.IncludeRefused):
        prompt_template.fill(b"{{L}}", [(b"L", refuses)])
