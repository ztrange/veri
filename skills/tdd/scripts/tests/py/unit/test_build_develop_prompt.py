"""In-process cases for veri/build_develop_prompt.py, the module build-develop-prompt.sh is a shim over."""
import importlib
import importlib.util
import io
import os
import re
import sys

import pytest

from conftest import SCRIPTS

PHASES = b"red|green|refactor|cover|transform|diff|structural|predicate|revise|reconcile|exhausted|over-budget|rebase|replaces-report|red-contradicted|red-repair|red-missing|red-supersede|expand|cover-new|migrate|contract-a|contract-b"
USAGE = b"build-develop-prompt.sh: usage: " + PHASES + b" <issue-spec-file> <step-text> <test-cmd> ...\n"
NAMED_REVISABLE = {"expand", "migrate", "contract-a", "contract-b", "rebase"}


def want_revise(module):
    assert NAMED_REVISABLE <= set(module.REVISABLE_PHASES)
    return "|".join(module.REVISABLE_PHASES)


def _fragment(name, after_include=False):
    text = (SCRIPTS / "prompts" / name).read_bytes()
    if after_include:
        text = text.split(b"}}", 1)[1]
    return re.sub(rb"\s+", b" ", text).strip()


@pytest.fixture
def build_develop_prompt():
    return importlib.import_module("veri.build_develop_prompt")


def test_main_refuses_no_argument_an_unknown_phase_a_short_count_an_unknown_revise_phase_and_a_missing_fast_cmd_with_exit_2_and_its_message_then_the_usage_line(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    s, r = str(spec), str(reason)
    results = {}
    for argv in ([], ["bogus", s, "s", "c"], ["green", s, "s", "c"],
                 ["revise", "bogus", s, "s", "c", r], ["diff", s, "s", "c"],
                 ["revise", "diff", s, "s", "c", r]):
        code = build_develop_prompt.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("bogus", s, "s", "c"): (
            2, b"", b"build-develop-prompt.sh: unknown phase 'bogus' (want " + PHASES + b")\n" + USAGE),
        ("green", s, "s", "c"): (2, b"", b"build-develop-prompt: green needs 7 arguments, got 4\n" + USAGE),
        ("revise", "bogus", s, "s", "c", r): (
            2, b"", b"build-develop-prompt.sh: unknown phase to revise 'bogus' (want "
            + want_revise(build_develop_prompt).encode() + b")\n" + USAGE),
        ("diff", s, "s", "c"): (2, b"", b"build-develop-prompt: diff needs 5 arguments, got 4\n" + USAGE),
        ("revise", "diff", s, "s", "c", r): (2, b"", b"build-develop-prompt: missing <fast-cmd>\n" + USAGE),
    }


def test_main_refuses_an_unknown_phase_to_revise_with_exit_2_naming_every_phase_it_accepts_interface_phases_included_1457(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")

    code = build_develop_prompt.main(["revise", "bogus", str(spec), "s", "c", str(reason)])

    assert (code, *capsysbinary.readouterr()) == (
        2, b"", b"build-develop-prompt.sh: unknown phase to revise 'bogus' "
        b"(want " + want_revise(build_develop_prompt).encode() + b")\n" + USAGE)


def test_main_builds_a_revise_prompt_naming_transform_as_the_phase_redone_instead_of_refusing_it_2137(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")

    code = build_develop_prompt.main(["revise", "transform", str(spec), "s", "make test", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, err, b"(redoing transform)" in out, b"(redoing refactor)" in out) == (0, b"", True, False)


def test_main_refuses_a_revise_prompt_whose_template_is_empty_with_exit_2_naming_the_phase_2137(
        tmp_path, capsysbinary, monkeypatch, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    read = build_develop_prompt._read
    monkeypatch.setattr(build_develop_prompt, "_read",
                        lambda path: b"" if str(path).endswith("develop-revise.md") else read(path))

    code = build_develop_prompt.main(["revise", "transform", str(spec), "s", "make test", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, out, b"transform" in err) == (2, b"", True)


def test_main_names_in_its_unknown_phase_refusal_and_its_usage_line_every_phase_it_accepts_the_replaces_and_red_repair_phases_included_1890(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    accepted = ["replaces-report", "red-contradicted", "red-repair", "red-missing", "red-supersede"]

    code = build_develop_prompt.main(["bogus", str(spec), "s", "c"])
    _, err = capsysbinary.readouterr()
    refusal, usage = err.decode().splitlines()

    assert (code, [(p, p in refusal.split("(want ")[1].rstrip(")").split("|"),
                    p in usage.split("usage: ")[1].split(" ")[0].split("|")) for p in accepted]) == (
        2, [(p, True, True) for p in accepted])


def test_main_refuses_in_the_check_order_each_missing_argument_by_its_own_name_and_ignores_arguments_past_the_count(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    s, r = str(spec), str(reason)

    def refused(message):
        return (2, b"", b"build-develop-prompt" + message + b"\n" + USAGE)

    expected = {
        ("", s, "s", "c"): refused(b".sh: unknown phase '' (want " + PHASES + b")"),
        ("revise", "bogus", "a", "b", "c"): refused(b": revise needs 6 arguments, got 5"),
        ("red", s, "s"): refused(b": red needs 4 arguments, got 3"),
        ("cover", s, "s"): refused(b": cover needs 4 arguments, got 3"),
        ("transform", s, "s"): refused(b": transform needs 4 arguments, got 3"),
        ("diff", s, "s", "c"): refused(b": diff needs 5 arguments, got 4"),
        ("refactor", s, "s", "c"): refused(b": refactor needs 5 arguments, got 4"),
        ("structural", s, "s", "c"): refused(b": structural needs 5 arguments, got 4"),
        ("predicate", s, "s", "c"): refused(b": predicate needs 5 arguments, got 4"),
        ("exhausted", s, "s", "c"): refused(b": exhausted needs 5 arguments, got 4"),
        ("revise", "red", s, "s", "c"): refused(b": revise needs 6 arguments, got 5"),
        ("reconcile", s, "s", "c", "b"): refused(b": reconcile needs 6 arguments, got 5"),
        ("over-budget", s, "s", "c", "1"): refused(b": over-budget needs 6 arguments, got 5"),
        ("green", s, "s", "c", "tp", "tt"): refused(b": green needs 7 arguments, got 6"),
        ("rebase", s, "s", "c", "a", "b"): refused(b": rebase needs 7 arguments, got 6"),
        ("revise", "", s, "s", "c", r): refused(b": missing <phase> being revised"),
        ("red", "", "", ""): refused(b": missing <issue-spec-file>"),
        ("red", s, "", ""): refused(b": missing <step-text>"),
        ("red", s, "s", ""): refused(b": missing <test-cmd>"),
        ("revise", "red", "", "s", "c", r): refused(b": missing <issue-spec-file>"),
        ("revise", "diff", s, "s", "", "", ""): refused(b": missing <test-cmd>"),
        ("green", s, "s", "c", "", "", ""): refused(b": missing <test-path>"),
        ("green", s, "s", "c", "tp", "", ""): refused(b": missing <target-test>"),
        ("green", s, "s", "c", "tp", "tt", ""): refused(b": missing <fast-cmd>"),
        ("diff", s, "s", "c", ""): refused(b": missing <fast-cmd>"),
        ("structural", s, "s", "c", ""): refused(b": missing <issue-touched-files>"),
        ("predicate", s, "s", "c", ""): refused(b": missing <issue-touched-files>"),
        ("refactor", s, "s", "c", ""): refused(b": missing <touched-files>"),
        ("revise", "red", s, "s", "c", ""): refused(b": missing <reason-file>"),
        ("exhausted", s, "s", "c", ""): refused(b": missing <reason-file>"),
        ("revise", "diff", s, "s", "c", "", ""): refused(b": missing <reason-file>"),
        ("revise", "diff", s, "s", "c", r, ""): refused(b": missing <fast-cmd>"),
        ("reconcile", s, "s", "c", "", ""): refused(b": missing <branch>"),
        ("reconcile", s, "s", "c", "b", ""): refused(b": missing <remote-sha>"),
        ("rebase", s, "s", "c", "", "", ""): refused(b": missing <onto-sha>"),
        ("rebase", s, "s", "c", "a", "", ""): refused(b": missing <pre-rebase-sha>"),
        ("rebase", s, "s", "c", "a", "b", ""): refused(b": missing <conflicting-files>"),
        ("over-budget", s, "s", "c", "", ""): refused(b": missing <spent>"),
        ("over-budget", s, "s", "c", "1", ""): refused(b": missing <budget>"),
    }
    results = {}
    for argv in expected:
        code = build_develop_prompt.main(list(argv))
        results[argv] = (code, *capsysbinary.readouterr())

    complete = [("red", s, "s", "c"), ("cover", s, "s", "c"), ("transform", s, "s", "c"),
                ("diff", s, "s", "c", "f"), ("refactor", s, "s", "c", "t"), ("structural", s, "s", "c", "t"),
                ("predicate", s, "s", "c", "t"), ("exhausted", s, "s", "c", r),
                ("revise", "red", s, "s", "c", r), ("revise", "green", s, "s", "c", r),
                ("revise", "refactor", s, "s", "c", r), ("revise", "transform", s, "s", "c", r),
                ("revise", "diff", s, "s", "c", r, "f"), ("reconcile", s, "s", "c", "b", "sha"), ("over-budget", s, "s", "c", "1", "2"),
                ("green", s, "s", "c", "tp", "tt", "f"), ("rebase", s, "s", "c", "a", "b", "x")]
    ignored = {}
    for argv in complete:
        answers = []
        for extra in ((), ("",), ("past", "the", "count")):
            code = build_develop_prompt.main(list(argv + extra))
            answers.append((code, *capsysbinary.readouterr()))
        ignored[argv] = (answers[0][0], answers[1] == answers[0], answers[2] == answers[0])

    assert results == expected
    assert ignored == {argv: (0, True, True) for argv in complete}
    assert type(build_develop_prompt.PHASES) is tuple
    assert "|".join(build_develop_prompt.PHASES).encode() == PHASES
    assert set(build_develop_prompt.REVISE_PHASES) == {"red", "green", "refactor", "transform", "diff"}


def test_main_refuses_a_spent_then_a_budget_that_is_not_a_whole_string_non_negative_decimal_before_any_file_is_read_and_a_revised_phase_with_a_trailing_newline(
        tmp_path, capsysbinary):
    module = tmp_path / "scripts" / "veri" / "build_develop_prompt.py"
    module.parent.mkdir(parents=True)
    module.write_bytes((SCRIPTS / "veri" / "build_develop_prompt.py").read_bytes())
    loader = importlib.util.spec_from_file_location("build_develop_prompt_without_prompts", module)
    no_prompts = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(no_prompts)
    s = str(tmp_path / "no-such-spec.md")
    r = str(tmp_path / "no-such-reason.md")

    def refused(message):
        return (2, b"", message.encode() + b"\n" + USAGE)

    def not_decimal(name, value):
        return refused(f"build-develop-prompt: <{name}> '{value}' is not a non-negative decimal number")

    expected = {}
    for bad in ("-1", "3,", "qwixnum", "1e3", ".5", "3.47 because", "3\n", "3.47\n", "٣", "3.٤"):
        expected[("over-budget", s, "s", "c", bad, "2.50")] = not_decimal("spent", bad)
        expected[("over-budget", s, "s", "c", "3.47", bad)] = not_decimal("budget", bad)
    expected[("over-budget", s, "s", "c", "qwixnum", "zork")] = not_decimal("spent", "qwixnum")
    expected[("revise", "red\n", s, "s", "c", r)] = refused(
        "build-develop-prompt.sh: unknown phase to revise 'red\n' (want " + want_revise(no_prompts) + ")")
    results = {}
    for argv in expected:
        code = no_prompts.main(list(argv))
        results[argv] = (code, *capsysbinary.readouterr())

    assert results == expected


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_refuses_the_first_unreadable_file_in_the_bash_order_with_no_usage_line_and_reads_only_the_files_the_phase_spec_and_step_select(
        tmp_path, capsysbinary):
    templates = ("develop-red.md", "develop-green.md", "develop-revise.md", "develop-revise-diff.md")
    partials = ("_develop-shared.md", "_develop-red-bug.md", "_develop-green-replaces-case.md",
                "_develop-green-suite-repair.md")

    def scripts_with(name, present):
        scripts = tmp_path / name / "scripts"
        (scripts / "veri").mkdir(parents=True)
        for source in (SCRIPTS / "veri").glob("*.py"):
            (scripts / "veri" / source.name).write_bytes(source.read_bytes())
        (scripts / "prompts").mkdir()
        for prompt in present:
            (scripts / "prompts" / prompt).write_bytes(prompt.encode() + b"\n")
        loader = importlib.util.spec_from_file_location(f"build_develop_prompt_{name}",
                                                        scripts / "veri" / "build_develop_prompt.py")
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        return module, scripts / "prompts"

    def answer(module, argv):
        code = module.main(argv)
        return (code, *capsysbinary.readouterr())

    def cannot_read(path):
        return (2, b"", f"build-develop-prompt: cannot read '{path}'\n".encode())

    spec = tmp_path / "bug-spec.md"
    reason = tmp_path / "reason.md"
    step = "pin it ⟦replaces-case⟧ ⟦suite-repair⟧"
    argv = ["revise", "green", str(spec), step, "make test", str(reason)]
    order = ("develop-revise.md", "_develop-shared.md", str(spec), str(reason), "_develop-red-bug.md",
             "_develop-green-replaces-case.md", "_develop-green-suite-repair.md")
    results, expected = {}, {}
    for count, missing in enumerate(order):
        present = [name for name in order[:count] if not name.startswith(str(tmp_path))]
        module, prompts = scripts_with(f"order-{count}", present)
        if count == 3:
            spec.write_bytes(b"# spec\n\n## Bug \t\nit breaks\n")
        if count == 4:
            reason.write_bytes(b"rejected\n")
        results[("order", missing)] = answer(module, list(argv))
        expected[("order", missing)] = cannot_read(missing if missing.startswith(str(tmp_path))
                                                   else prompts / missing)

    module, prompts = scripts_with("no-bug-partial", (*templates, "_develop-shared.md",
                                                      "_develop-green-replaces-case.md",
                                                      "_develop-green-suite-repair.md"))
    green = ["green", str(spec), "pin it", "make test", "t.sh", "case", "make unit"]
    results[("bug", "green")] = answer(module, green)
    expected[("bug", "green")] = cannot_read(prompts / "_develop-red-bug.md")
    for heading in (b"## Bugs\n", b" ## Bug\n", b"## Bug report\n"):
        other = tmp_path / "other-spec.md"
        other.write_bytes(b"# spec\n\n" + heading + b"text\n")
        code, out, err = answer(module, ["green", str(other)] + green[2:])
        results[("not-bug", heading)] = (code, err)
        expected[("not-bug", heading)] = (0, b"")

    plain = tmp_path / "plain-spec.md"
    plain.write_bytes(b"# spec\n")
    module, prompts = scripts_with("no-green-partials", (*templates, *partials[:2]))
    for marker, partial in (("⟦replaces-case⟧", "_develop-green-replaces-case.md"),
                            ("⟦suite-repair⟧", "_develop-green-suite-repair.md")):
        for call in (["green", str(plain), f"x {marker}", "make test", "t.sh", "case", "make unit"],
                     ["revise", "green", str(plain), f"x {marker}", "make test", str(reason)]):
            results[("needs", marker, call[1])] = answer(module, call)
            expected[("needs", marker, call[1])] = cannot_read(prompts / partial)
        for call in (["red", str(plain), f"x {marker}", "make test"],
                     ["revise", "red", str(plain), f"x {marker}", "make test", str(reason)]):
            code, out, err = answer(module, call)
            results[("ignores", marker, call[1])] = (code, err)
            expected[("ignores", marker, call[1])] = (0, b"")

    for revised in ("red", "green", "refactor", "diff"):
        wanted = "develop-revise-diff.md" if revised == "diff" else "develop-revise.md"
        module, prompts = scripts_with(f"template-{revised}",
                                       [name for name in templates if name != wanted] + list(partials))
        call = ["revise", revised, str(plain), "s", "make test", str(reason), "make unit"]
        results[("template", revised)] = answer(module, call)
        expected[("template", revised)] = cannot_read(prompts / wanted)

    module, prompts = scripts_with("exhausted", ("develop-exhausted.md", "_develop-shared.md"))
    unread = tmp_path / "no-reason.md"
    results[("exhausted", "reason")] = answer(module, ["exhausted", str(plain), "s", "make test", str(unread)])
    expected[("exhausted", "reason")] = cannot_read(unread)

    assert results == expected
    module, prompts = scripts_with("directory-spec", (*templates, *partials))
    with pytest.raises(IsADirectoryError):
        module.main(["red", str(tmp_path), "s", "make test"])


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_renders_a_red_prompt_with_each_file_stripped_of_trailing_newlines_the_timed_test_run_path_as_reached_and_non_utf8_bytes_passed_through(
        tmp_path, capsysbinary):
    real = tmp_path / "real" / "scripts"
    (real / "veri").mkdir(parents=True)
    for source in (SCRIPTS / "veri").glob("*.py"):
        (real / "veri" / source.name).write_bytes(source.read_bytes())
    (real / "prompts").mkdir()
    (real / "prompts" / "develop-red.md").write_bytes(
        b"{{SHARED}}\n[{{STEP}}]\n[{{ISSUE_SPEC}}]\n[{{TEST_CMD}}]\n[{{TIMED_TEST_RUN}}]\n\n\n")
    (real / "prompts" / "_develop-shared.md").write_bytes(b"shared rules\n\n")
    link = tmp_path / "link"
    link.symlink_to(tmp_path / "real")
    loader = importlib.util.spec_from_file_location("build_develop_prompt_via_symlink",
                                                    link / "scripts" / "veri" / "build_develop_prompt.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec \xff\n\nbody\n\n\n")
    step = os.fsdecode(b"pin \xfe it")

    code = module.main(["red", str(spec), step, "make test"])

    assert (code, *capsysbinary.readouterr()) == (
        0,
        b"shared rules\n[pin \xfe it]\n[# spec \xff\n\nbody]\n[make test]\n["
        + os.fsencode(str(link / "scripts" / "timed-test-run.sh")) + b"]\n",
        b"")


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_drops_nul_bytes_from_the_template_the_shared_rules_and_the_spec_it_renders(tmp_path, capsysbinary):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    for source in (SCRIPTS / "veri").glob("*.py"):
        (scripts / "veri" / source.name).write_bytes(source.read_bytes())
    (scripts / "prompts").mkdir()
    (scripts / "prompts" / "develop-red.md").write_bytes(b"te\x00mplate\n{{SHARED}}\n[{{ISSUE_SPEC}}]\n")
    (scripts / "prompts" / "_develop-shared.md").write_bytes(b"sha\x00red\n")
    loader = importlib.util.spec_from_file_location("build_develop_prompt_nul",
                                                    scripts / "veri" / "build_develop_prompt.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# sp\x00ec\x00\n")

    code = module.main(["red", str(spec), "s", "make test"])

    assert (code, *capsysbinary.readouterr()) == (0, b"template\nshared\n[# spec]\n", b"")


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_resolves_includes_in_the_template_the_shared_rules_and_the_green_paragraphs_before_substituting_and_leaves_them_literal_in_the_spec_step_reason_and_bug_paragraph(
        tmp_path, capsysbinary):
    def scripts_with(name, prompts):
        scripts = tmp_path / name / "scripts"
        (scripts / "veri").mkdir(parents=True)
        for source in (SCRIPTS / "veri").glob("*.py"):
            (scripts / "veri" / source.name).write_bytes(source.read_bytes())
        (scripts / "prompts").mkdir()
        for file, content in prompts.items():
            (scripts / "prompts" / file).write_bytes(content)
        loader = importlib.util.spec_from_file_location(f"build_develop_prompt_{name}",
                                                        scripts / "veri" / "build_develop_prompt.py")
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        return module, os.fsencode(str(scripts / "prompts"))

    literal = b"{{INCLUDE:_s.md}}"
    prompts = {
        "develop-green.md": b"{{INCLUDE:_t.md}}\n{{SHARED}}\n[{{ISSUE_SPEC}}]\n[{{BUG_REPRODUCTION}}]\n"
                            b"[{{REPLACES_CASE}}]\n[{{SUITE_REPAIR}}]\n[{{STEP}}]\n",
        "develop-revise.md": b"[{{REJECTION_REASON}}]\n",
        "_t.md": b"tpl {{STEP}}\n",
        "_s.md": b"S\n",
        "_develop-shared.md": b"shared " + literal + b"\n",
        "_develop-red-bug.md": b"bug " + literal + b"\n",
        "_develop-green-replaces-case.md": b"rc " + literal + b"\n",
        "_develop-green-suite-repair.md": b"sr " + literal + b"\n",
    }
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"## Bug\nspec " + literal + b"\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"why " + literal + b"\n")
    step = "x {{INCLUDE:_s.md}} ⟦replaces-case⟧ ⟦suite-repair⟧"
    step_b = step.encode()
    results, expected = {}, {}

    def answer(key, module, argv):
        code = module.main(argv)
        results[key] = (code, *capsysbinary.readouterr())

    module, _ = scripts_with("render", prompts)
    answer("green", module, ["green", str(spec), step, "make test", "tp", "tt", "make unit"])
    expected["green"] = (0, b"tpl " + step_b + b"\nshared S\n[## Bug\nspec " + literal + b"]\n[bug " + literal
                         + b"]\n[\n\nrc S]\n[\n\nsr S]\n[" + step_b + b"]\n", b"")
    answer("plain green", module, ["green", str(spec), "plain", "make test", "tp", "tt", "make unit"])
    expected["plain green"] = (0, b"tpl plain\nshared S\n[## Bug\nspec " + literal + b"]\n[bug " + literal
                               + b"]\n[]\n[]\n[plain]\n", b"")
    answer("revise", module, ["revise", "red", str(spec), "s", "make test", str(reason)])
    expected["revise"] = (0, b"[why " + literal + b"]\n", b"")

    module, p = scripts_with("missing", {**prompts, "_develop-shared.md": b"shared {{INCLUDE:_gone.md}}\n"})
    answer("missing", module, ["green", str(spec), "plain", "make test", "tp", "tt", "make unit"])
    expected["missing"] = (2, b"", b"missing partial: " + p + b"/_gone.md\n")

    module, p = scripts_with("loop", {**prompts, "_develop-green-suite-repair.md": b"sr {{INCLUDE:_loop.md}}\n",
                                      "_loop.md": b"{{INCLUDE:_loop.md}}\n"})
    answer("loop", module, ["green", str(spec), step, "make test", "tp", "tt", "make unit"])
    expected["loop"] = (2, b"", b"partial includes itself: " + p + b"/_loop.md\n")

    assert results == expected


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_substitutes_every_placeholder_sequentially_globally_and_literally_in_the_bash_order_for_every_phase(
        tmp_path, capsysbinary, monkeypatch, build_develop_prompt):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    names = ("SHARED", "ISSUE_SPEC", "BUG_REPRODUCTION", "REPLACES_CASE", "SUITE_REPAIR", "STEP", "TEST_CMD",
             "TEST_PATH", "TARGET_TEST", "FAST_CMD", "TIMED_TEST_RUN", "TOUCHED_FILES", "REFACTOR_BUDGET",
             "REVISE_PHASE", "REJECTION_REASON", "BRANCH", "REMOTE_SHA", "SPENT", "BUDGET", "ONTO_SHA",
             "PRE_REBASE_SHA", "CONFLICTING_FILES")
    template = b"".join(b"%s=[{{%s}}]\n" % (name.encode(), name.encode()) for name in names) + b"again {{STEP}}\n"
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    for source in (SCRIPTS / "veri").glob("*.py"):
        (scripts / "veri" / source.name).write_bytes(source.read_bytes())
    (scripts / "prompts").mkdir()
    for phase in ("red", "green", "refactor", "cover", "transform", "diff", "structural", "predicate", "revise",
                  "revise-diff", "reconcile", "exhausted", "over-budget", "rebase"):
        (scripts / "prompts" / f"develop-{phase}.md").write_bytes(template)
    (scripts / "prompts" / "_develop-shared.md").write_bytes(b"shared & \\1\n")
    loader = importlib.util.spec_from_file_location("build_develop_prompt_cascade",
                                                    scripts / "veri" / "build_develop_prompt.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"spec {{STEP}} & \\1\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"why {{STEP}} {{BRANCH}} & \\1\n")
    s, r = str(spec), str(reason)
    step, cmd, fast = "step & \\1", "make test A=1&2 \\x", "make unit F=a&b/c \\y"

    common = {"SHARED": b"shared & \\1", "ISSUE_SPEC": b"spec step & \\1 & \\1", "STEP": step.encode(),
              "TEST_CMD": cmd.encode(), "TIMED_TEST_RUN": os.fsencode(str(scripts / "timed-test-run.sh"))}
    cases = {
        "red": (["red", s, step, cmd], {}),
        "cover": (["cover", s, step, cmd], {}),
        "transform": (["transform", s, step, cmd], {}),
        "diff": (["diff", s, step, cmd, fast], {"FAST_CMD": fast.encode()}),
        "green": (["green", s, step, cmd, "t/p&\\", "tt&\\", fast],
                  {"TEST_PATH": b"t/p&\\", "TARGET_TEST": b"tt&\\", "FAST_CMD": fast.encode()}),
        "refactor": (["refactor", s, step, cmd, "a.sh&\\"], {"TOUCHED_FILES": b"a.sh&\\", "REFACTOR_BUDGET": b"5"}),
        "structural": (["structural", s, step, cmd, "b.sh&\\"], {"TOUCHED_FILES": b"b.sh&\\"}),
        "predicate": (["predicate", s, step, cmd, "c.sh&\\"], {"TOUCHED_FILES": b"c.sh&\\"}),
        "revise green": (["revise", "green", s, step, cmd, r],
                         {"REVISE_PHASE": b"green", "REJECTION_REASON": b"why {{STEP}}  & \\1"}),
        "revise diff": (["revise", "diff", s, step, cmd, r, fast],
                        {"REVISE_PHASE": b"diff", "REJECTION_REASON": b"why {{STEP}}  & \\1",
                         "FAST_CMD": fast.encode()}),
        "exhausted": (["exhausted", s, step, cmd, r], {"REJECTION_REASON": b"why {{STEP}}  & \\1"}),
        "reconcile": (["reconcile", s, step, cmd, "tdd/1&\\", "abc&\\"],
                      {"BRANCH": b"tdd/1&\\", "REMOTE_SHA": b"abc&\\"}),
        "over-budget": (["over-budget", s, step, cmd, "1.5", "2"], {"SPENT": b"1.5", "BUDGET": b"2"}),
        "rebase": (["rebase", s, step, cmd, "onto&\\", "pre&\\", "x.sh&\\"],
                   {"ONTO_SHA": b"onto&\\", "PRE_REBASE_SHA": b"pre&\\", "CONFLICTING_FILES": b"x.sh&\\"}),
    }
    results, expected = {}, {}
    for key, (argv, values) in cases.items():
        code = module.main(argv)
        results[key] = (code, *capsysbinary.readouterr())
        values = {**common, **values}
        expected[key] = (0, b"".join(b"%s=[%s]\n" % (name.encode(), values.get(name, b"")) for name in names)
                         + b"again " + step.encode() + b"\n", b"")

    here = os.fsencode(str(SCRIPTS))
    for key, argv in (("real diff", ["diff", s, step, cmd, fast]),
                      ("real revise diff", ["revise", "diff", s, step, cmd, r, fast])):
        code = build_develop_prompt.main(argv)
        out, err = capsysbinary.readouterr()
        lines = out.split(b"\n")
        at = next((i for i, line in enumerate(lines) if b"timed-test-run.sh fast" in line), len(lines))
        results[key] = (code, lines[at:at + 2], err)
        expected[key] = (0, [b"       " + here + b"/timed-test-run.sh fast '' " + fast.encode(),
                             b"       " + here + b"/timed-test-run.sh affected '<the suites you ran>' make test TESTS=\"<those paths>\""], b"")

    assert results == expected


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_reads_veri_refactor_budget_for_the_refactor_phase_only_rendering_5_when_unset_or_empty_and_any_other_value_verbatim(
        tmp_path, capsysbinary, monkeypatch):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    for source in (SCRIPTS / "veri").glob("*.py"):
        (scripts / "veri" / source.name).write_bytes(source.read_bytes())
    (scripts / "prompts").mkdir()
    for phase in ("red", "green", "refactor", "cover", "transform", "diff", "structural", "predicate", "revise",
                  "revise-diff", "reconcile", "exhausted", "over-budget", "rebase"):
        (scripts / "prompts" / f"develop-{phase}.md").write_bytes(b"budget=[{{REFACTOR_BUDGET}}]\n")
    (scripts / "prompts" / "_develop-shared.md").write_bytes(b"shared\n")
    loader = importlib.util.spec_from_file_location("build_develop_prompt_budget",
                                                    scripts / "veri" / "build_develop_prompt.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"why\n")
    s, r = str(spec), str(reason)

    def render(argv, budget):
        if budget is None:
            monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
        else:
            monkeypatch.setenv("VERI_REFACTOR_BUDGET", budget)
        code = module.main(argv)
        return (code, *capsysbinary.readouterr())

    refactor = ["refactor", s, "step", "make test", "a.sh"]
    results = {budget: render(refactor, budget) for budget in (None, "", "3", "lots & \\1")}
    others = {
        "red": ["red", s, "step", "make test"],
        "green": ["green", s, "step", "make test", "t.sh", "case", "make unit"],
        "cover": ["cover", s, "step", "make test"],
        "transform": ["transform", s, "step", "make test"],
        "diff": ["diff", s, "step", "make test", "make unit"],
        "structural": ["structural", s, "step", "make test", "a.sh"],
        "predicate": ["predicate", s, "step", "make test", "a.sh"],
        "revise refactor": ["revise", "refactor", s, "step", "make test", r],
        "revise diff": ["revise", "diff", s, "step", "make test", r, "make unit"],
        "reconcile": ["reconcile", s, "step", "make test", "tdd/1", "abc"],
        "exhausted": ["exhausted", s, "step", "make test", r],
        "over-budget": ["over-budget", s, "step", "make test", "1", "2"],
        "rebase": ["rebase", s, "step", "make test", "onto", "pre", "x.sh"],
    }
    results.update({key: render(argv, "9") for key, argv in others.items()})

    assert results == {
        None: (0, b"budget=[5]\n", b""),
        "": (0, b"budget=[5]\n", b""),
        "3": (0, b"budget=[3]\n", b""),
        "lots & \\1": (0, b"budget=[lots & \\1]\n", b""),
        **{key: (0, b"budget=[]\n", b"") for key in others},
    }


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_answers_what_the_bash_contract_cases_before_the_out_of_scope_class_asserted(
        tmp_path, capsysbinary, monkeypatch, build_develop_prompt):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" \xe2\x80\x94 see {ref}\\n done.\n')
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    cmd = 'make test ZORBLAT=1 -- --only "frob & nitz/quux"'
    test_path, target = "tests/zorblat/test_frob & nitz.sh", "qwixtle seeds a newline-terminated block"
    touched = "scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh"
    reason_text = "REJECT: the case asserts on zorblat()'s log line, not its return value — & {tricky}\\chars."
    reason = tmp_path / "reason.md"
    reason.write_bytes(reason_text.encode() + b"\n")
    s, r = str(spec), str(reason)

    def answer(module, argv):
        code = module.main(argv)
        return (code, *capsysbinary.readouterr())

    prompts = {}
    for phase, argv in (("red", ["red", s, step, cmd]),
                        ("green", ["green", s, step, cmd, test_path, target, "make unit"]),
                        ("refactor", ["refactor", s, step, cmd, touched]),
                        ("revise", ["revise", "red", s, step, cmd, r])):
        code, out, err = answer(build_develop_prompt, argv)
        assert (phase, code) == (phase, 0)
        prompts[phase] = out
    red, green, refactor, revise = (prompts[p] for p in ("red", "green", "refactor", "revise"))

    def folded(prompt):
        return prompt.replace(b"\n", b" ")

    def says(prompt, pattern, flags=re.I):
        return re.search(pattern, folded(prompt), flags) is not None

    def any_line(prompt, pattern, flags=re.I):
        return any(re.search(pattern, line, flags) for line in prompt.split(b"\n"))

    checks = {
        "red carries spec, step, test command and AGAINST_UNMODIFIED": all(
            part in red for part in (b'zorblat("Frob & Nitz/Quux")', step.encode(), cmd.encode(),
                                     b"AGAINST_UNMODIFIED")),
        "green names the test path and target": test_path.encode() in green and target.encode() in green,
        "refactor carries touched files, the no-generality rule and RESULT:": (
            touched.encode() in refactor and b"RESULT:" in refactor),
        "revise carries the reason verbatim and IMPOSSIBLE": reason_text.encode() in revise and b"IMPOSSIBLE" in revise,
        "refactor requires a CANDIDATES: line, one per line, or none": any_line(refactor, rb"^CANDIDATES:", 0),
    }

    no_prompts = tmp_path / "no-prompts" / "veri"
    no_prompts.mkdir(parents=True)
    for source in (SCRIPTS / "veri").glob("*.py"):
        (no_prompts / source.name).write_bytes(source.read_bytes())
    loader = importlib.util.spec_from_file_location("build_develop_prompt_no_prompts",
                                                    no_prompts / "build_develop_prompt.py")
    without = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(without)
    absent = str(tmp_path / "absent.md")
    refusals = {
        "unknown phase": answer(build_develop_prompt, ["bogus", s, step, cmd]),
        "missing spec": answer(build_develop_prompt, ["red", absent, step, cmd]),
        "missing reason": answer(build_develop_prompt, ["revise", "red", s, step, cmd, absent]),
        "missing template": answer(without, ["red", s, step, cmd]),
        "unknown phase to revise": answer(build_develop_prompt, ["revise", "bogus", s, step, cmd, r]),
        "missing positionals": answer(build_develop_prompt, ["red", s]),
        "no arguments": answer(build_develop_prompt, []),
    }
    for label, (code, out, err) in refusals.items():
        checks[f"{label} exits 2 with a diagnostic and no prompt"] = code == 2 and out == b"" and err != b""
    checks["no arguments names build-develop-prompt.sh on a usage line"] = any(
        b"usage" in line.lower() and b"build-develop-prompt.sh" in line
        for line in refusals["no arguments"][2].split(b"\n"))

    assert checks == dict.fromkeys(checks, True)


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_answers_what_the_bash_contract_cases_from_the_out_of_scope_class_to_the_over_budget_reason_asserted(
        tmp_path, capsysbinary, monkeypatch, build_develop_prompt):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    build_verify_prompt = importlib.import_module("veri.build_verify_prompt")
    spec = tmp_path / "spec.md"
    spec_bytes = b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" \xe2\x80\x94 see {ref}\\n done.\n'
    spec.write_bytes(spec_bytes)
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    cmd = 'make test ZORBLAT=1 -- --only "frob & nitz/quux"'
    test_path, target = "tests/zorblat/test_frob & nitz.sh", "qwixtle seeds a newline-terminated block"
    touched = "scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh"
    reason_text = "REJECT: the case asserts on zorblat()'s log line, not its return value — & {tricky}\\chars."
    reason = tmp_path / "reason.md"
    reason.write_bytes(reason_text.encode() + b"\n")
    s, r = str(spec), str(reason)
    absent = str(tmp_path / "absent.md")

    def answer(module, argv):
        code = module.main(argv)
        return (code, *capsysbinary.readouterr())

    def rendered(argv):
        code, out, _ = answer(build_develop_prompt, argv)
        return out if code == 0 else None

    def refused(argv):
        code, out, err = answer(build_develop_prompt, argv)
        return code == 2 and out == b"" and err != b""

    def folded(prompt):
        return prompt.replace(b"\n", b" ")

    def says(prompt, pattern, flags=re.I):
        return prompt is not None and re.search(pattern, folded(prompt), flags) is not None

    def any_line(prompt, pattern, flags=0):
        return prompt is not None and any(re.search(pattern, line, flags) for line in prompt.split(b"\n"))

    def both_ways(prompt, gap, a, b):
        return says(prompt, rb"%s[^.]{0,%d}%s|%s[^.]{0,%d}%s" % (a, gap, b, b, gap, a))

    def carries(prompt, *parts):
        return prompt is not None and all(
            (part.encode() if isinstance(part, str) else part) in prompt for part in parts)

    red = rendered(["red", s, step, cmd])
    green = rendered(["green", s, step, cmd, test_path, target, "make unit"])
    refactor = rendered(["refactor", s, step, cmd, touched])
    revise = rendered(["revise", "red", s, step, cmd, r])

    monkeypatch.setenv("VERI_REFACTOR_BUDGET", "37")
    budgeted = rendered(["refactor", s, step, cmd, touched])
    monkeypatch.delenv("VERI_REFACTOR_BUDGET")

    rc_branch, rc_sha = "tdd/232-zorblat-frob", "3f9a1c0b7e2d4a6f8c1b3e5d7f9a0c2e4b6d8f01"
    reconcile = rendered(["reconcile", s, step, cmd, rc_branch, rc_sha])

    fast_cmd = 'make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
    fast_green = rendered(["green", s, step, cmd, test_path, target, fast_cmd])
    revise_green = rendered(["revise", "green", s, step, cmd, r])

    replaces_step = ('tests/zorblat.test.sh: "zorblat frobs a nitz" moves to '
                     'tests/py/test_zorblat.py ⟦replaces-case⟧ ⟦criterion 1⟧')
    prompts_dir = SCRIPTS / "prompts"
    replaces_text = (prompts_dir / "_develop-green-replaces-case.md").read_bytes().split(b"}}", 1)[1].strip()
    suite_repair_text = (prompts_dir / "_develop-green-suite-repair.md").read_bytes().strip()
    replaces_green = rendered(["green", s, replaces_step, cmd, "tests/py/test_zorblat.py",
                               "test_zorblat_frobs_a_nitz", "make unit"])

    repair_step = ("fix the full-suite failure: skills/tdd/scripts/tests/zorblat.test.sh — FAIL - zorblat frobs a nitz; "
                   "skills/tdd/scripts/tests/quux.test.sh — FAIL - quux & {nitz} round-trips ⟦suite-repair⟧")
    repair_named = ("skills/tdd/scripts/tests/zorblat.test.sh", "zorblat frobs a nitz",
                    "skills/tdd/scripts/tests/quux.test.sh", "quux & {nitz} round-trips")
    repair_green = rendered(["green", s, repair_step, "make test", repair_named[0], repair_named[1], "make unit"])
    repair_revise = rendered(["revise", "green", s, repair_step, "make test", r])
    single_step = ("fix the full-suite failure: skills/tdd/scripts/tests/zorblat.test.sh — FAIL - zorblat frobs a nitz "
                   "⟦suite-repair⟧")
    single_green = rendered(["green", s, single_step, "make test", repair_named[0], repair_named[1], "make unit"])
    verify_code, single_verify, _ = answer(build_verify_prompt, [
        "--step", single_step, "--fast-cmd", "make unit", "green", s, repair_named[0], repair_named[1]])

    unmodified = tmp_path / "unmodified"
    (unmodified / "veri").mkdir(parents=True)
    for source in (SCRIPTS / "veri").glob("*.py"):
        (unmodified / "veri" / source.name).write_bytes(source.read_bytes())
    (unmodified / "prompts").mkdir()
    for tpl in (SCRIPTS / "prompts").glob("*.md"):
        if tpl.name not in ("_develop-green-suite-repair.md", "_verify-green-suite-repair.md"):
            (unmodified / "prompts" / tpl.name).write_bytes(tpl.read_bytes().replace(b"{{SUITE_REPAIR}}", b""))

    def load(name):
        loader = importlib.util.spec_from_file_location(f"{name}_unmodified", unmodified / "veri" / f"{name}.py")
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        return module

    scripts_dir = os.fsencode(os.path.dirname(os.path.dirname(os.path.abspath(build_develop_prompt.__file__))))

    def as_built_here(result):
        code, out, err = result
        return (code, out.replace(os.fsencode(str(unmodified)), scripts_dir),
                err.replace(os.fsencode(str(unmodified)), scripts_dir))

    plain = ["green", s, step, cmd, test_path, target, "make unit"]
    verify_plain = ["--step", step, "--fast-cmd", "make unit", "green", s, test_path, target]

    exhausted = rendered(["exhausted", s, step, cmd, r])

    over_budget = rendered(["over-budget", s, step, cmd, "3.47", "2.50"])
    over_budget_extra = rendered(["over-budget", s, step, cmd, "3.47", "2.50", r])

    checks = {
        "refactor carries VERI_REFACTOR_BUDGET as the budget": both_ways(budgeted, 80, rb"budget", rb"37"),
        "red predicts before the run and carries the prediction footer": (
            carries(red, b"PREDICTED_FAILURE:", b"PREDICTION_NOTE:")
            and says(red, rb"PREDICTION:[^.]{0,20}MATCHED", 0) and says(red, rb"PREDICTION:[^.]{0,20}DIVERGED", 0)),
        "reconcile carries sha, branch and a pinned --force-with-lease, no bare --force, refusing a missing sha": (
            carries(reconcile, rc_sha, rc_branch, f"--force-with-lease={rc_branch}:{rc_sha}")
            and refused(["reconcile", s, step, cmd, rc_branch, ""])),
        "green carries <fast-cmd> verbatim and refuses an empty one": (
            carries(fast_green, fast_cmd) and refused(["green", s, step, cmd, test_path, target, ""])),
        "revise ends with PREDICTED_FAILURE: and PREDICTION: MATCHED | DIVERGED": (
            carries(revise, b"PREDICTED_FAILURE:") and says(revise, rb"PREDICTION:[^.]{0,20}MATCHED", 0)
            and says(revise, rb"PREDICTION:[^.]{0,20}DIVERGED", 0)),
        "green offers SPLIT: lines": (
            any_line(green, rb"^SPLIT:")),
        "revise green offers the same SPLIT: lines": (
            any_line(revise_green, rb"^SPLIT:")),
        "green for a replaces-case step carries the replaces-case text and the plain green does not": (
            replaces_text in replaces_green and replaces_text not in green),
        "#690 green for a two-suite repair names both suites and cases and asks every listed suite green": (
            carries(repair_green, *repair_named) and suite_repair_text in repair_green),
        "#690 revise green for a two-suite repair does the same": (
            carries(repair_revise, *repair_named) and suite_repair_text in repair_revise),
        "#690 a one-suite repair names that suite and case in develop-green and verify-green": (
            carries(single_green, *repair_named[:2]) and verify_code == 0
            and carries(single_verify, *repair_named[:2])),
        "#690 develop-green without suite repair is byte-identical to the builder without it": (
            answer(build_develop_prompt, plain) == as_built_here(answer(load("build_develop_prompt"), plain))),
        "#690 verify-green without suite repair is byte-identical to the builder without it": (
            answer(build_verify_prompt, verify_plain) == as_built_here(answer(load("build_verify_prompt"), verify_plain))),
        "exhausted carries the step, the reason and the spec, refusing a missing reason": (
            carries(exhausted, step, reason_text, b'zorblat("Frob & Nitz/Quux")')
            and refused(["exhausted", s, step, cmd, absent])),
        "refactor reports FLAGS: lines in the three classes or none, no NEW_STEP:, defining each class": (
            any_line(refactor, rb"^FLAGS:") and not any_line(refactor, rb"^NEW_STEP:")),
        "over-budget carries the step, both figures and the spec": carries(
            over_budget, step, b"3.47", b"2.50", b'zorblat("Frob & Nitz/Quux")'),
        "over-budget asks for SPLIT: or NEEDS_USER:": (
            any_line(over_budget, rb"^SPLIT:") and any_line(over_budget, rb"^NEEDS_USER:")),
        "over-budget with fewer than five arguments after the phase refuses": all(
            refused(["over-budget", *args]) for args in ([], [s], [s, step], [s, step, cmd], [s, step, cmd, "3.47"])),
        "over-budget ignores a reason file past <budget>": (
            over_budget is not None and over_budget_extra == over_budget
            and reason_text.encode() not in over_budget_extra),
    }

    assert checks == dict.fromkeys(checks, True)


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_answers_what_the_bash_contract_cases_from_the_rebase_prompt_to_the_end_asserted(
        tmp_path, capsysbinary, monkeypatch, build_develop_prompt):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    build_verify_prompt = importlib.import_module("veri.build_verify_prompt")
    refactor_owed = importlib.import_module("veri.refactor_owed")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" \xe2\x80\x94 see {ref}\\n done.\n')
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    cmd = 'make test ZORBLAT=1 -- --only "frob & nitz/quux"'
    test_path, target = "tests/zorblat/test_frob & nitz.sh", "qwixtle seeds a newline-terminated block"
    touched = "scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh"
    reason_text = "REJECT: the case asserts on zorblat()'s log line, not its return value — & {tricky}\\chars."
    reason = tmp_path / "reason.md"
    reason.write_bytes(reason_text.encode() + b"\n")
    s, r = str(spec), str(reason)

    def answer(module, argv):
        code = module.main(argv)
        return (code, *capsysbinary.readouterr())

    def rendered(argv):
        code, out, _ = answer(build_develop_prompt, argv)
        return out if code == 0 else None

    def refused(argv):
        code, out, err = answer(build_develop_prompt, argv)
        return code == 2 and out == b"" and err != b""

    def folded(prompt):
        return prompt.replace(b"\n", b" ")

    def says(prompt, pattern, flags=re.I):
        return prompt is not None and re.search(pattern, folded(prompt), flags) is not None

    def lacks(prompt, pattern, flags=re.I):
        return prompt is not None and re.search(pattern, folded(prompt), flags) is None

    def any_line(prompt, pattern, flags=0):
        return prompt is not None and any(re.search(pattern, line, flags) for line in prompt.split(b"\n"))

    def both_ways(prompt, gap, a, b):
        return says(prompt, rb"%s[^.]{0,%d}%s|%s[^.]{0,%d}%s" % (a, gap, b, b, gap, a))

    def carries(prompt, *parts):
        return prompt is not None and all(
            (part.encode() if isinstance(part, str) else part) in prompt for part in parts)

    def scripts_with(name, prompts):
        scripts = tmp_path / name / "scripts"
        (scripts / "veri").mkdir(parents=True)
        for source in (SCRIPTS / "veri").glob("*.py"):
            (scripts / "veri" / source.name).write_bytes(source.read_bytes())
        (scripts / "prompts").mkdir()
        for tpl in (SCRIPTS / "prompts").glob("*.md"):
            (scripts / "prompts" / tpl.name).write_bytes(tpl.read_bytes())
        for file, content in prompts.items():
            (scripts / "prompts" / file).write_bytes(content)
        loader = importlib.util.spec_from_file_location(f"build_develop_prompt_{name}",
                                                        scripts / "veri" / "build_develop_prompt.py")
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        return module, os.fsencode(str(scripts / "prompts"))

    red = rendered(["red", s, step, cmd])
    green = rendered(["green", s, step, cmd, test_path, target, "make unit"])
    refactor = rendered(["refactor", s, step, cmd, touched])
    revise = rendered(["revise", "red", s, step, cmd, r])

    rb_onto, rb_pre = "7c1e9a3f5b2d4e6a8c0f1b3d5e7a9c2e4f6b8d0a", "e2b4d6f8a0c1e3b5d7f9a1c3e5b7d9f0a2c4e6b8"
    rb_files = "skills/tdd/SKILL.md\nscripts/zorblat frob & nitz.sh"
    rebase = rendered(["rebase", s, step, cmd, rb_onto, rb_pre, rb_files])
    rb_lines = [line for line in (rebase or b"").split(b"\n") if line.strip()]

    cover = rendered(["cover", s, step, cmd])
    transform = rendered(["transform", s, step, cmd])

    structural_candidate = "extract the zorblat parser into its own module & {rename} it"
    issue_touched = "scripts/zorblat.sh, scripts/lib/frob & nitz.sh"
    structural = rendered(["structural", s, structural_candidate, cmd, issue_touched])
    predicate = rendered(["predicate", s, structural_candidate, cmd, issue_touched])

    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(
        b"RESULT: nothing left to tidy\nCANDIDATES: structural | extract the zorblat parser into its own module\n"
        b"FLAGS: none\n")))
    owed_code = refactor_owed.main(["append", str(owed), step])
    capsysbinary.readouterr()
    owed_lines = owed.read_text().split("\n") if owed.exists() else []
    step_at = owed_lines.index(f"### {step}") if f"### {step}" in owed_lines else None
    candidate_line = "- extract the zorblat parser into its own module"
    candidate_at = owed_lines.index(candidate_line) if candidate_line in owed_lines else None

    rk_step = 'grep -q "zorblat_parse" scripts/lib/zorblat-parser.sh'
    rk_predicate = tmp_path / "rk-predicate.md"
    rk_predicate.write_bytes(rk_step.encode() + b"\n")
    rk_dev = rendered(["transform", s, rk_step, cmd])
    rk_ver_code, rk_ver, _ = answer(build_verify_prompt, ["--step", rk_step, "transform", s, str(rk_predicate),
                                                          "0123abcdef"])
    rk_ver = rk_ver if rk_ver_code == 0 else None

    dd_step = "the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧"
    dd = rendered(["diff", s, dd_step, cmd, "make unit"])
    dd_empty_cmd = answer(build_develop_prompt, ["diff", s, dd_step, "", "make unit"])
    bogus_revise = answer(build_develop_prompt, ["revise", "bogus", s, step, cmd, r])
    revise_diff = rendered(["revise", "diff", s, dd_step, cmd, r, "make unit"])

    includes = {}
    module, _ = scripts_with("included", {"develop-red.md": b"before {{INCLUDE:_probe-partial.md}} after\n",
                                          "_probe-partial.md": b"partial runs {{TEST_CMD}}\n\n\n"})
    includes["included"] = answer(module, ["red", s, step, cmd])
    module, _ = scripts_with("nested", {"develop-red.md": b"before {{INCLUDE:_probe-outer.md}} after\n",
                                        "_probe-outer.md": b"outer {{INCLUDE:_probe-inner.md}} end\n",
                                        "_probe-inner.md": b"inner runs {{TEST_CMD}}\n"})
    includes["nested"] = answer(module, ["red", s, step, cmd])
    module, dangling = scripts_with("dangling", {"develop-red.md": b"before {{INCLUDE:_probe-absent.md}} after\n"})
    includes["dangling"] = answer(module, ["red", s, step, cmd])
    module, _ = scripts_with("cycle", {"develop-red.md": b"before {{INCLUDE:_probe-cycle-a.md}} after\n",
                                       "_probe-cycle-a.md": b"a {{INCLUDE:_probe-cycle-b.md}}\n",
                                       "_probe-cycle-b.md": b"b {{INCLUDE:_probe-cycle-a.md}}\n"})
    includes["cycle"] = answer(module, ["red", s, step, cmd])

    dd_fast = 'make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(build_develop_prompt.__file__)))
    timed = os.fsencode(os.path.join(scripts_dir, "timed-test-run.sh"))
    fast_line = timed + b" fast '' " + dd_fast.encode()

    def runs_fast_then_affected(prompt):
        return (prompt is not None and fast_line in prompt
                and timed + b" affected " in prompt[prompt.index(fast_line) + len(fast_line):])

    ddf = rendered(["diff", s, dd_step, cmd, dd_fast])
    rdf = rendered(["revise", "diff", s, dd_step, cmd, r, dd_fast])

    checks = {
        "develop-rebase names both shas, every conflicting file and the test command, resolves by git rebase "
        "<onto-sha>, leaves the ledger's ticks and marks untouched, ends with REBASE: RESOLVED | FAILED, "
        "and refuses a missing argument": (
            carries(rebase, rb_onto, rb_pre, *rb_files.split("\n"), cmd)
            and rb_lines[-1].startswith(b"REBASE: RESOLVED | FAILED")
            and refused(["rebase", s, step, cmd, rb_onto, rb_pre, ""])
            and refused(["rebase", s, step, cmd, rb_onto, "", rb_files])),
        "cover and transform each print their own prompt carrying the step, and an unknown phase is refused": (
            carries(cover, step) and carries(transform, step) and cover not in (red, transform)
            and transform != red and refused(["covers", s, step, cmd])),
        "#679 develop-cover allows COVERED: unreachable only for a step that only deletes code no caller reaches": (
            any_line(cover, rb"^COVERED:.*unreachable")
),
        "#679 develop-cover allows COVERED: type-only only for a step that changes only types": (
            any_line(cover, rb"^COVERED:.*type-only")
),
        "#679 develop-cover says reshaped runtime code is never unreachable or type-only, and carries PROOF:": (
            any_line(cover, rb"^PROOF:")),
        "develop-refactor reports every other structural candidate on CANDIDATES: structural, which "
        "refactor-owed append records under the step's name": (
            owed_code == 0 and step_at is not None and candidate_at is not None and step_at < candidate_at),
        "develop-structural is bounded to the issue's touched files, one refactor: commit, no test file": (
            carries(structural, structural_candidate, issue_touched)),
        "#691 develop-predicate asks for one shell predicate, false now and true once applied, and refuses "
        "a missing argument": (
            carries(predicate, structural_candidate, issue_touched, cmd,
                    "PREDICATE: <command>", "PREDICATE: NONE — <why>")
            and refused(["predicate", s, structural_candidate, cmd, ""])),
        "#691 a refactor-kind step's transform prompts build from the step and its predicate record alone": (
            carries(rk_dev, rk_step) and carries(rk_ver, rk_step, str(rk_predicate))
            and all(lacks(p, rb"structural-predicate", 0) and lacks(p, rb"predicate leaf")
                    and lacks(p, rb"PREDICATE: NONE", 0) and lacks(p, rb"structural[* ]+pass")
                    for p in (rk_ver,))),
        "develop-diff makes and commits the change, no commit when unchanged, and adds no test": (
            carries(dd, dd_step, 'zorblat("Frob & Nitz/Quux")') and dd != red),
        "#995 develop-diff with an empty <test-cmd> exits 2 with 'missing <test-cmd>' first on stderr": (
            dd_empty_cmd[0] == 2 and dd_empty_cmd[1] == b""
            and dd_empty_cmd[2].split(b"\n")[0] == b"build-develop-prompt: missing <test-cmd>"),
        "#880 a revise of an unknown phase names red, green, refactor, transform and diff": (
            bogus_revise[0] == 2 and bogus_revise[1] == b""
            and all(p in bogus_revise[2].split(b"(want ")[1].split(b")")[0].split(b"|")
                    for p in (b"red", b"green", b"refactor", b"transform", b"diff"))),
        "#880 a revise of a diff-checked step carries the step and the rejection reason": carries(
            revise_diff, dd_step, reason_text),
        "#880 a revise of a diff-checked step asks for no test": (
            not carries(revise_diff, "AGAINST_UNMODIFIED:") and revise_diff is not None
            and b"PREDICTED_FAILURE:" not in revise_diff),
        "#703 an include is replaced by its partial, trailing newlines stripped, before the placeholders": (
            includes["included"][:2] == (0, f"before partial runs {cmd} after\n".encode())),
        "#703 an include inside an included partial is resolved recursively": (
            includes["nested"][:2] == (0, f"before outer inner runs {cmd} end after\n".encode())),
        "#703 an include naming an absent partial exits 2 naming its path, nothing on stdout": (
            includes["dangling"][:2] == (2, b"") and dangling + b"/_probe-absent.md" in includes["dangling"][2]),
        "#703 a partial including itself through another exits 2 naming it, nothing on stdout": (
            includes["cycle"][:2] == (2, b"") and b"_probe-cycle-a.md" in includes["cycle"][2]),
        "#974 the diff prompt runs the fast command through timed-test-run.sh fast, then the affected suites, "
        "both green": runs_fast_then_affected(ddf),
        "#974 diff with the fast command left out exits 2 with a diagnostic and no prompt": refused(
            ["diff", s, dd_step, cmd, ""]),
        "#974 the revise-diff prompt runs the fast command, then the affected suites, both green": (
            runs_fast_then_affected(rdf)),
        "#974 revise diff with the fast command left out exits 2 with a diagnostic and no prompt": refused(
            ["revise", "diff", s, dd_step, cmd, r]),
        "#990 the red prompt spells affected-suites.sh HEAD": carries(red, "affected-suites.sh HEAD"),
        "#990 the green prompt spells affected-suites.sh HEAD": carries(green, "affected-suites.sh HEAD"),
        "#990 the revise prompt spells affected-suites.sh HEAD": carries(revise, "affected-suites.sh HEAD"),
    }

    assert checks == dict.fromkeys(checks, True)


def test_main_names_the_surviving_cases_in_a_replaces_case_green_prompt_rebuilt_after_the_first_green_left_them_issue_1406(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    step = ('tests/zorblat.test.sh: "zorblat frobs a nitz", "zorblat quuxes a frob" move to '
            'tests/py/test_zorblat.py ⟦replaces-case⟧ ⟦criterion 1⟧')
    survivors = "still present in tests/zorblat.test.sh: zorblat quuxes a frob"
    code = build_develop_prompt.main(["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                                      "test_zorblat_frobs_a_nitz", "make unit", survivors])
    out, _ = capsysbinary.readouterr()
    prompt = re.sub(rb"\s+", b" ", out)

    assert (code, survivors.encode() in prompt) == (0, True), prompt


def test_main_renders_a_revise_prompt_for_each_interface_phase_naming_it_and_carrying_the_rejection_reason_verbatim_1448(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    reason_text = b"REJECT: the migrate phase left a caller on the old name & {tricky}\\chars."
    reason = tmp_path / "reason.md"
    reason.write_bytes(reason_text + b"\n")

    results = {}
    for phase in ("expand", "migrate", "contract-a", "contract-b"):
        code = build_develop_prompt.main(
            ["revise", phase, str(spec), "QWIXTLE: zorblat quuxes", "make test", str(reason), "make unit"])
        out, err = capsysbinary.readouterr()
        results[phase] = (code, f"(redoing {phase})".encode() in out, reason_text in out, err)

    assert results == {phase: (0, True, True, b"") for phase in ("expand", "migrate", "contract-a", "contract-b")}


def test_main_states_each_interface_phases_freeze_rule_in_its_revise_prompt_1448(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"REJECT: the phase left a caller on the old name.\n")

    test_fragment = (SCRIPTS / "prompts" / "_develop-revise-freeze-test.md").read_bytes().rstrip(b"\n")
    production_fragment = (SCRIPTS / "prompts" / "_develop-revise-freeze-production.md").read_bytes().rstrip(b"\n")
    frozen = {}
    for phase in ("expand", "migrate", "contract-a", "contract-b"):
        code = build_develop_prompt.main(
            ["revise", phase, str(spec), "QWIXTLE: zorblat quuxes", "make test", str(reason), "make unit"])
        out, _ = capsysbinary.readouterr()
        frozen[phase] = (code, test_fragment in out, production_fragment in out)

    assert frozen == {"expand": (0, True, False), "migrate": (0, True, False),
                      "contract-a": (0, False, True), "contract-b": (0, True, False)}


def test_main_freezes_production_in_a_cover_new_revise_prompt_as_contract_a_does_and_tests_in_expand_migrate_and_contract_b_2034(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"REJECT: the new cases do not call the new interface.\n")

    test_fragment = (SCRIPTS / "prompts" / "_develop-revise-freeze-test.md").read_bytes().rstrip(b"\n")
    production_fragment = (SCRIPTS / "prompts" / "_develop-revise-freeze-production.md").read_bytes().rstrip(b"\n")
    frozen = {}
    for phase in ("cover-new", "contract-a", "expand", "migrate", "contract-b"):
        code = build_develop_prompt.main(
            ["revise", phase, str(spec), "QWIXTLE: zorblat quuxes", "make test", str(reason), "make unit"])
        out, _ = capsysbinary.readouterr()
        frozen[phase] = (code, test_fragment in out, production_fragment in out)

    assert frozen == {"cover-new": (0, False, True), "contract-a": (0, False, True),
                      "expand": (0, True, False), "migrate": (0, True, False), "contract-b": (0, True, False)}


def test_main_renders_a_red_prompt_taking_a_ci_repair_steps_quoted_ci_log_as_its_evidence_of_failure_and_a_local_pass_as_no_pin_only_for_the_mark_1431(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    marked = ("CI job gates is red on a1b2c3d: tests/zorblat.test.sh — FAIL - zorblat frobs a nitz "
              "-frob-nitz +frob_nitz ⟦ci-repair⟧")
    plain = "zorblat frobs a nitz ⟦criterion 1⟧"

    def rendered(step):
        code = build_develop_prompt.main(["red", str(spec), step, "make test"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(rb"\s+", b" ", out)

    probe = _fragment("_develop-red-ci-repair.md").split(b". ")[0]

    results = {}
    for name, step in (("marked", marked), ("plain", plain)):
        code, prompt = rendered(step)
        results[name] = (code, probe in prompt)

    assert results == {"marked": (0, True), "plain": (0, False)}


def test_main_renders_a_red_prompt_for_a_replaces_case_step_asking_one_pytest_replacement_per_named_case_and_a_replaces_report_line_for_each_not_one_criterion_one_case_1521(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    marked = ('tests/zorblat.test.sh: "zorblat frobs a nitz", "zorblat quuxes a frob", '
              '"zorblat refuses an empty nitz" move to tests/py/test_zorblat.py ⟦replaces-case⟧ ⟦criterion 1⟧')
    plain = "zorblat frobs a nitz ⟦criterion 1⟧"

    def rendered(step):
        code = build_develop_prompt.main(["red", str(spec), step, "make test"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(rb"\s+", b" ", out)

    replaces = _fragment("_develop-red-cases-replaces-case.md").split(b". ")[0]
    ordinary = _fragment("_develop-red-cases.md")

    code, prompt = rendered(marked)
    marked_result = (code, replaces in prompt, ordinary in prompt)
    code, prompt = rendered(plain)
    plain_result = (code, replaces in prompt, ordinary in prompt)

    assert (marked_result, plain_result) == ((0, True, False), (0, False, True))


def test_main_renders_a_red_prompt_for_a_replaces_case_step_stating_the_replaces_test_id_is_the_pytest_node_id_and_the_line_starts_at_column_0_with_no_bullet_and_one_without_the_mark_unchanged_1660(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    marked = ("replaces 'zorblat frobs a nitz', 'zorblat quuxes a frob' in tests/zorblat.test.sh "
              "⟦replaces-case⟧ ⟦criterion 1⟧")
    plain = "zorblat frobs a nitz ⟦criterion 1⟧"
    rule = _fragment("_develop-node-id-rule.md")

    def rendered(step):
        code = build_develop_prompt.main(["red", str(spec), step, "make test"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(rb"\s+", b" ", out)

    code, prompt = rendered(marked)
    marked_result = (code, rule in prompt)
    code, prompt = rendered(plain)
    plain_result = (code, rule in prompt)

    assert (marked_result, plain_result) == ((0, True), (0, False))


def test_main_renders_a_develop_replaces_report_prompt_stating_the_replaces_test_id_is_the_pytest_node_id_and_the_line_starts_at_column_0_with_no_bullet_1660(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    report = tmp_path / "red-report.txt"
    report.write_bytes(b"- REPLACES: zorblat frobs a nitz => test_zorblat_frobs\n")
    missing = tmp_path / "missing-cases.txt"
    missing.write_bytes(b"zorblat frobs a nitz\n")
    step = "\u27e6replaces-case\u27e7 replaces 'zorblat frobs a nitz' in tests/zorblat.test.sh \u27e6criterion 1\u27e7"
    rule = _fragment("_develop-node-id-rule.md")

    code = build_develop_prompt.main(["replaces-report", str(spec), step, "make test", str(report), str(missing)])
    out, _ = capsysbinary.readouterr()
    prompt = re.sub(rb"\s+", b" ", out)

    assert (code, rule in prompt) == (0, True)


def test_main_renders_a_revise_red_prompt_for_a_replaces_case_step_with_the_replaces_report_line_and_one_without_the_mark_unchanged_1521(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"REJECT: the second named case has no replacement.\n")
    marked = ('tests/zorblat.test.sh: "zorblat frobs a nitz", "zorblat quuxes a frob" '
              'move to tests/py/test_zorblat.py ⟦replaces-case⟧ ⟦criterion 1⟧')
    plain = "zorblat frobs a nitz ⟦criterion 1⟧"
    replaces = _fragment("_develop-red-cases-replaces-case.md").split(b". ")[0]

    def rendered(step):
        code = build_develop_prompt.main(["revise", "red", str(spec), step, "make test", str(reason)])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(rb"\s+", b" ", out)

    code, prompt = rendered(marked)
    marked_result = (code, replaces in prompt)
    code, prompt = rendered(plain)
    plain_result = (code, replaces in prompt)

    assert (marked_result, plain_result) == ((0, True), (0, False))


def test_main_renders_a_red_prompt_for_a_replaces_case_step_without_the_exactly_one_new_failing_test_case_instruction_and_one_without_the_mark_unchanged_1537(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    marked = ('tests/zorblat.test.sh: "zorblat frobs a nitz", "zorblat quuxes a frob" '
              'move to tests/py/test_zorblat.py ⟦replaces-case⟧ ⟦criterion 1⟧')
    plain = "zorblat frobs a nitz ⟦criterion 1⟧"
    lead = _fragment("_develop-red-lead.md")

    def rendered(step):
        code = build_develop_prompt.main(["red", str(spec), step, "make test"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(rb"\s+", b" ", out)

    code, prompt = rendered(marked)
    marked_result = (code, lead in prompt)
    code, prompt = rendered(plain)
    plain_result = (code, lead in prompt)

    assert (marked_result, plain_result) == ((0, False), (0, True))


def test_main_renders_a_revise_red_prompt_for_a_replaces_case_step_without_an_instruction_to_add_a_single_case_and_one_without_the_mark_unchanged_1537(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"REJECT: the second named case has no replacement.\n")
    marked = ('tests/zorblat.test.sh: "zorblat frobs a nitz", "zorblat quuxes a frob" '
              'move to tests/py/test_zorblat.py ⟦replaces-case⟧ ⟦criterion 1⟧')
    plain = "zorblat frobs a nitz ⟦criterion 1⟧"
    fragment_line = re.sub(rb"\s+", b" ", (SCRIPTS / "prompts" / "_develop-red-cases-replaces-case.md")
                           .read_bytes()).split(b". ")[0]
    single = rb"(exactly \*\*ONE\*\* new failing test case|add (exactly )?(one|a single) (new )?(failing )?(test )?case)"

    def rendered(step):
        code = build_develop_prompt.main(["revise", "red", str(spec), step, "make test", str(reason)])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(rb"\s+", b" ", out)

    code, prompt = rendered(marked)
    marked_result = (code, re.search(single, prompt, re.I) is None)
    code, prompt = rendered(plain)
    plain_result = (code, re.search(single, prompt, re.I) is None, fragment_line not in prompt)

    assert (marked_result, plain_result) == ((0, True), (0, True, True))


def _staged_builder(root, drop, strip=()):
    (root / "veri").mkdir(parents=True)
    for source in (SCRIPTS / "veri").glob("*.py"):
        (root / "veri" / source.name).write_bytes(source.read_bytes())
    (root / "prompts").mkdir()
    for tpl in (SCRIPTS / "prompts").glob("*.md"):
        if tpl.name not in drop:
            body = tpl.read_bytes()
            for placeholder in strip:
                body = body.replace(placeholder, b"")
            (root / "prompts" / tpl.name).write_bytes(body)
    loader = importlib.util.spec_from_file_location(f"staged_{root.name}", root / "veri" / "build_develop_prompt.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


def _spec_and_reason(tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_REFACTOR_BUDGET", "5")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    return spec, reason


def _render_both(build_develop_prompt, staged, root, capsysbinary, argv):
    here = (build_develop_prompt.main(argv), *capsysbinary.readouterr())
    code, out, err = (staged.main(argv), *capsysbinary.readouterr())
    scripts_dir = os.fsencode(os.path.dirname(os.path.dirname(os.path.abspath(build_develop_prompt.__file__))))
    return here, (code, out.replace(os.fsencode(str(root)), scripts_dir), err.replace(os.fsencode(str(root)), scripts_dir))


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_renders_every_phase_other_than_over_budget_without_reading_the_over_budget_template_1468(
        tmp_path, capsysbinary, monkeypatch, build_develop_prompt):
    spec, reason = _spec_and_reason(tmp_path, monkeypatch)
    rc_sha = "3f9a1c0b7e2d4a6f8c1b3e5d7f9a0c2e4b6d8f01"
    staged = _staged_builder(tmp_path / "no-over-budget", drop=("develop-over-budget.md",))
    s, r, step = str(spec), str(reason), "frob a nitz"
    argvs = {
        "red": ["red", s, step, "make test"],
        "green": ["green", s, step, "make test", "tests/t.py", "test_a", "make unit"],
        "refactor": ["refactor", s, step, "make test", "a.py"],
        "revise red": ["revise", "red", s, step, "make test", r],
        "revise green": ["revise", "green", s, step, "make test", r],
        "revise refactor": ["revise", "refactor", s, step, "make test", r],
        "exhausted": ["exhausted", s, step, "make test", r],
        "reconcile": ["reconcile", s, step, "make test", "tdd/1-x", rc_sha],
    }

    differing = {}
    for label, argv in argvs.items():
        here, without = _render_both(build_develop_prompt, staged, tmp_path / "no-over-budget", capsysbinary, argv)
        if here[0] != 0 or here != without:
            differing[label] = (here[0], without[0])

    assert differing == {}


@pytest.mark.tree_audit("the modules under veri/ and the templates under prompts/")
def test_main_renders_revise_green_for_an_unmarked_step_as_the_builder_without_the_replaces_case_paragraph_does_1468(
        tmp_path, capsysbinary, monkeypatch, build_develop_prompt):
    spec, reason = _spec_and_reason(tmp_path, monkeypatch)
    staged = _staged_builder(tmp_path / "no-replaces", drop=("_develop-green-replaces-case.md",),
                             strip=(b"{{REPLACES_CASE}}",))
    step = 'tests/zorblat.test.sh: "zorblat frobs a nitz" replaces-case moves to tests/py ⟦added⟧ ⟦criterion 2⟧'

    here, without = _render_both(build_develop_prompt, staged, tmp_path / "no-replaces", capsysbinary,
                                 ["revise", "green", str(spec), step, "make test", str(reason)])

    assert here[0] == 0 and here == without


def test_main_renders_a_revise_of_green_with_develop_greens_do_not_modify_the_test_and_wrong_test_rule_and_a_revise_of_red_without_it_1586(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    freeze = _fragment("_develop-green-freeze-rule.md")

    answers = {}
    for revised in ("green", "red"):
        code = build_develop_prompt.main(["revise", revised, str(spec), "s", "make test", str(reason)])
        out, err = capsysbinary.readouterr()
        answers[revised] = (code, freeze in re.sub(rb"\s+", b" ", out))

    assert answers == {"green": (0, True), "red": (0, False)}


def test_main_renders_a_revise_of_green_declaring_a_suite_exempt_wrong_test_report_and_skill_md_routes_it_to_verify_green_1586(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")

    code = build_develop_prompt.main(["revise", "green", str(spec), "s", "make test", str(reason)])
    out = capsysbinary.readouterr().out.decode()

    declared = [l for l in out.splitlines() if l.startswith("REPORT-FORMAT ") and "keys WRONG_TEST:" in l]
    assert (code, len(declared), "suite exempt" in " ".join(declared)) == (
        0, 1, True)


def test_main_asks_green_and_revise_green_prompts_to_name_the_contradicted_case_in_the_wrong_test_line_1621(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    ask = _fragment("_develop-wrong-test-report.md")

    code = build_develop_prompt.main(["revise", "green", str(spec), "s", "make test", str(reason)])
    out, _ = capsysbinary.readouterr()

    assert (code, re.sub(rb"\s+", b" ", out).count(ask)) == (0, 1)


def test_main_grants_a_test_rewrite_in_a_revise_prompt_only_when_the_revised_phase_is_red_1586(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    run_state = os.fsencode(os.path.join(build_develop_prompt.event.toplevel() or os.getcwd(), ".tdd"))
    grant = (SCRIPTS / "prompts" / "_develop-test-rewrite-grant.md").read_bytes().rstrip(b"\n")
    for name in (b"red-prediction.md", b"red-run-output.txt"):
        grant = grant.replace(b"`.tdd/" + name + b"`", b"`" + run_state + b"/" + name + b"`")

    granted = {}
    for revised in build_develop_prompt.REVISABLE_PHASES:
        fast = ["make unit"] if revised == "diff" else []
        code = build_develop_prompt.main(["revise", revised, str(spec), "s", "make test", str(reason)] + fast)
        out, _ = capsysbinary.readouterr()
        granted[revised] = (code, grant in out)

    assert granted == {revised: (0, revised == "red") for revised in build_develop_prompt.REVISABLE_PHASES}


def test_main_tells_a_revise_of_contract_a_to_move_the_old_interfaces_tests_without_a_new_prediction_1586(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    move = (SCRIPTS / "prompts" / "_develop-test-move-contract-a.md").read_bytes().rstrip(b"\n")

    told = {}
    for revised in build_develop_prompt.REVISABLE_PHASES:
        fast = ["make unit"] if revised == "diff" else []
        code = build_develop_prompt.main(["revise", revised, str(spec), "s", "make test", str(reason)] + fast)
        out, _ = capsysbinary.readouterr()
        told[revised] = (code, move in out)

    assert told == {revised: (0, revised == "contract-a") for revised in build_develop_prompt.REVISABLE_PHASES}


def test_main_declares_a_wrong_test_report_format_in_a_revise_prompt_only_for_green_1586(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")

    seen = {}
    for revised in ("red", "green", "refactor"):
        code = build_develop_prompt.main(["revise", revised, str(spec), "s", "make test", str(reason)])
        out = capsysbinary.readouterr().out
        formats = [l for l in out.splitlines() if l.startswith(b"REPORT-FORMAT ") and b"keys WRONG_TEST:" in l]
        seen[revised] = (code, len(formats), b"WRONG_TEST" in out)

    assert seen == {"red": (0, 0, False), "green": (0, 1, True), "refactor": (0, 0, False)}


def _spec(tmp_path, extra=""):
    spec = tmp_path / "spec.md"
    spec.write_text('zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" — see {ref}\\n done.\n' + extra)
    return str(spec)


def test_cli_red_carries_spec_step_and_test_command_verbatim_and_the_against_unmodified_report_line(
        tmp_path, run_cli, build_develop_prompt):
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    test_cmd = 'make test ZORBLAT=1 -- --only "frob & nitz/quux"'

    code, out, err = run_cli(build_develop_prompt, ["red", _spec(tmp_path), step, test_cmd])

    assert (code, err) == (0, "")
    assert [needle in out for needle in ('zorblat("Frob & Nitz/Quux")', step, test_cmd, "AGAINST_UNMODIFIED")] == [True] * 4


def test_cli_red_contradicted_builds_a_prompt_naming_the_case_to_update_and_the_red_footer_and_refuses_an_empty_case_or_missing_spec_1621(
        tmp_path, run_cli, build_develop_prompt):
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    case = "zorblat frobs a nitz"

    code, out, err = run_cli(build_develop_prompt, ["red-contradicted", _spec(tmp_path), step, "make test", case])
    empty = run_cli(build_develop_prompt, ["red-contradicted", _spec(tmp_path), step, "make test", ""])
    missing = run_cli(build_develop_prompt, ["red-contradicted", str(tmp_path / "absent.md"), step, "make test", case])

    footer = ("TEST_PATH:", "TARGET_TEST:", "AGAINST_UNMODIFIED:", "WHY:", "FAIL_OUTPUT:", "PREDICTED_FAILURE:", "PREDICTION:")
    assert (code, [needle in out for needle in (step, case, *footer)], empty[0], empty[1], missing[0], missing[1]) == (
        0, [True] * (2 + len(footer)), 2, "", 2, "")


def test_cli_red_repair_prompt_carries_the_named_case_and_the_wrong_test_reason_and_tells_the_leaf_to_edit_that_case_only_never_create_a_suite_1765(
        tmp_path, run_cli, build_develop_prompt):
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    case = "zorblat frobs a nitz"
    report = tmp_path / "green-report.md"
    report.write_text("noise\nWRONG_TEST: the stub matches GLORPNAK pages it must not\nVERDICT: none\n")

    code, out, err = run_cli(build_develop_prompt, ["red-repair", _spec(tmp_path), step, "make test", case, str(report)])

    flat = " ".join(out.split())
    assert (code, err) == (0, "")
    assert [needle in flat for needle in (step, case, "the stub matches GLORPNAK pages it must not")] == [True] * 3


def test_cli_red_repair_prompt_names_every_superseded_case_listed_after_the_report_file_1932(
        tmp_path, run_cli, build_develop_prompt):
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    case = "zorblat frobs a nitz"
    first, second = "zorblat prints the usage on a bad flag", "zorblat prints the usage on no arguments"
    report = tmp_path / "green-report.md"
    report.write_text("WRONG_TEST: the stub matches GLORPNAK pages it must not\n")

    code, out, err = run_cli(build_develop_prompt, ["red-repair", _spec(tmp_path), step, "make test", case, str(report), first, second])

    flat = " ".join(out.split())
    assert (code, err) == (0, "")
    assert [needle in flat for needle in (case, first, second)] == [True] * 3


def test_cli_red_missing_prompt_carries_the_reason_files_missing_test_line_verbatim_and_tells_the_leaf_to_add_one_case_and_a_missing_reason_file_exits_2_with_the_usage_1808(
        tmp_path, run_cli, build_develop_prompt):
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    line = "MISSING_TEST: no case requires GLORPNAK to be counted once when the session is closed"
    reason = tmp_path / "reason.md"
    reason.write_text(f"noise\n{line}\nVERDICT: REJECT\n")

    code, out, err = run_cli(build_develop_prompt, ["red-missing", _spec(tmp_path), step, "make test", str(reason)])
    short = run_cli(build_develop_prompt, ["red-missing", _spec(tmp_path), step, "make test"])

    flat = " ".join(out.split())
    assert (code, err) == (0, "")
    assert [needle in flat for needle in (step, line)] == [True] * 2
    assert (short[0], short[1], "red-missing needs" in short[2], "Usage:" in short[2] or "usage:" in short[2]) == (2, "", True, True)


def test_cli_red_supersede_prompt_names_every_listed_case_lets_the_leaf_update_those_only_and_forbids_new_cases_and_production_code_1862(
        tmp_path, run_cli, build_develop_prompt):
    step = "QWIXTLE: the usage line gains --not-zorblat"
    first, second = "zorblat prints the usage on a bad flag", "zorblat prints the usage on no arguments"
    report = tmp_path / "green-report.md"
    report.write_text("SUPERSEDED: " + first + "\nSUPERSEDED: " + second + "\n")

    code, out, err = run_cli(build_develop_prompt, ["red-supersede", _spec(tmp_path), step, "make test", str(report), first, second])

    flat = " ".join(out.split())
    assert (code, err) == (0, "")
    assert [needle in flat for needle in (step, first, second)] == [True] * 3


def test_cli_unknown_phase_with_no_further_arguments_exits_2_names_the_phase_on_stderr_and_prints_no_prompt(
        run_cli, build_develop_prompt):
    code, out, err = run_cli(build_develop_prompt, ["bogus"])

    assert (code, out, err) == (
        2, "", "build-develop-prompt.sh: unknown phase 'bogus' (want " + PHASES.decode() + ")\n" + USAGE.decode())


def test_cli_red_tells_a_bugs_leaf_to_write_from_expected_drive_with_steps_and_fail_as_what_happened_describes_and_a_leaf_with_no_bug_section_none_of_it(
        tmp_path, run_cli, build_develop_prompt):
    bug = ('\n## Bug\n\n### What happened\n\nzorblat returned "FROB_NITZ" on the quuxed seed.\n\n### Expected\n\n'
           'zorblat returns "frob-nitz-quux".\n\n### Steps to reproduce\n\nRun zorblat --seed "Frob & Nitz/Quux".\n\n'
           '### Environment\n\nveri on bash 5.2, macOS 15.\n')
    probe = _fragment("_develop-red-bug.md").split(b". ")[0].decode()
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    test_cmd = 'make test ZORBLAT=1 -- --only "frob & nitz/quux"'

    def told(extra):
        code, out, err = run_cli(build_develop_prompt, ["red", _spec(tmp_path, extra), step, test_cmd])
        return code, err, out, probe in " ".join(out.split())

    bug_code, bug_err, bug_out, bug_told = told(bug)
    plain_code, plain_err, _, plain_told = told("")

    assert (bug_code, plain_code, bug_err, plain_err) == (0, 0, "", "")
    assert 'zorblat returned "FROB_NITZ" on the quuxed seed.' in bug_out
    assert (bug_told, plain_told) == (True, False)


def test_cli_over_budget_refuses_a_spent_or_budget_that_is_not_a_non_negative_decimal_number_with_exit_2_a_diagnostic_and_no_prompt_before_any_template_is_read(
        tmp_path, run_cli, build_develop_prompt):
    module = tmp_path / "scripts" / "veri" / "build_develop_prompt.py"
    module.parent.mkdir(parents=True)
    module.write_bytes((SCRIPTS / "veri" / "build_develop_prompt.py").read_bytes())
    loader = importlib.util.spec_from_file_location("build_develop_prompt_cli_without_prompts", module)
    no_prompts = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(no_prompts)
    spec = _spec(tmp_path)
    step, test_cmd = "QWIXTLE: a seed ending in a newline gains the block", "make test"
    results = {}
    for bad in ("-1", "3,", "qwixnum", "1e3", ".5", "3.47 because"):
        for module_, label, argv in (
                (build_develop_prompt, "spent", ["over-budget", spec, step, test_cmd, bad, "2.50"]),
                (build_develop_prompt, "budget", ["over-budget", spec, step, test_cmd, "3.47", bad]),
                (no_prompts, "spent without a template", ["over-budget", spec, step, test_cmd, bad, "2.50"])):
            code, out, err = run_cli(module_, argv)
            results[(bad, label)] = (code, out, bad in err and "cannot read" not in err)

    assert results == {key: (2, "", True) for key in results} and len(results) == 18


def test_cli_develop_diff_given_every_argument_but_an_empty_test_cmd_exits_2_with_no_prompt_and_missing_test_cmd_on_stderr(
        tmp_path, run_cli, build_develop_prompt):
    step = "the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧"

    code, out, err = run_cli(build_develop_prompt, ["diff", _spec(tmp_path), step, "", "make unit"])

    assert (code, out, err.splitlines()[0]) == (2, "", "build-develop-prompt: missing <test-cmd>")


def test_cli_red_given_a_directory_as_the_issue_spec_file_exits_2_with_nothing_on_stdout_and_a_non_empty_stderr(
        tmp_path, run_cli, build_develop_prompt):
    spec_dir = tmp_path / "spec-dir"
    spec_dir.mkdir()

    code, out, err = run_cli(build_develop_prompt, ["red", str(spec_dir), "QWIXTLE: a seed gains the block", "make test"])

    assert (code, out, err != "") == (2, "", True)


def test_cli_develop_replaces_report_names_every_case_in_the_missing_cases_file_points_at_the_report_file_and_asks_for_a_replaces_line_each_and_a_missing_report_or_cases_file_exits_2_with_no_stdout(
        tmp_path, run_cli, build_develop_prompt):
    spec, step, test_cmd = _spec(tmp_path), "QWIXTLE: a seed ending in a newline gains the block", "make test"
    report, cases = tmp_path / "red-report.txt", tmp_path / "missing-cases.txt"
    report.write_text("wrote the replacements\n")
    cases.write_text("zibble case alpha\nzibble case beta\n")

    ok = run_cli(build_develop_prompt, ["replaces-report", spec, step, test_cmd, str(report), str(cases)])
    no_report = run_cli(build_develop_prompt,
                        ["replaces-report", spec, step, test_cmd, str(tmp_path / "no-such-report.txt"), str(cases)])
    no_cases = run_cli(build_develop_prompt,
                       ["replaces-report", spec, step, test_cmd, str(report), str(tmp_path / "no-such-cases.txt")])

    assert ok[0] == 0
    assert [needle in ok[1] for needle in ("zibble case alpha", "zibble case beta", str(report))] == [True] * 3
    assert (no_report[0], no_report[1], no_cases[0], no_cases[1]) == (2, "", 2, "")


def test_main_builds_the_ordinary_red_and_green_prompts_for_a_step_that_only_mentions_the_replaces_case_mark_in_its_prose_or_backticks_and_the_replaces_case_ones_for_a_step_whose_trailing_marks_carry_it_1538(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    tail = "in tests/zorblat.test.sh"
    steps = {
        "prose": f"a step quoting ⟦replaces-case⟧ in its prose replaces 'zorblat frobs a nitz' {tail} ⟦criterion 2⟧",
        "backticks": f"a step quoting `⟦replaces-case⟧` replaces 'zorblat frobs a nitz' {tail} ⟦criterion 2⟧",
        "marked": f"replaces 'zorblat frobs a nitz' {tail} ⟦replaces-case⟧ ⟦criterion 2⟧",
    }
    red_ordinary = rb"Add exactly \*\*ONE\*\* new failing test case"
    red_replaces = rb"Add the replacement test cases the step names"
    green_replaces = rb"permitted, and it is required for the step to pass, to delete exactly the cases it names"

    results = {}
    for name, step in steps.items():
        build_develop_prompt.main(["red", str(spec), step, "make test"])
        red = re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)
        build_develop_prompt.main(["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                                   "test_zorblat_frobs_a_nitz", "make unit"])
        green = re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)
        results[name] = (re.search(red_ordinary, red) is not None, re.search(red_replaces, red) is not None,
                         re.search(green_replaces, green) is not None)

    assert results == {"prose": (True, False, False), "backticks": (True, False, False),
                       "marked": (False, True, True)}


def test_main_builds_the_replaces_case_red_and_green_prompts_for_a_step_whose_text_begins_with_the_mark_1538(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    step = "⟦replaces-case⟧ replaces 'zorblat frobs a nitz' in tests/zorblat.test.sh ⟦criterion 2⟧"

    build_develop_prompt.main(["red", str(spec), step, "make test"])
    red = re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)
    build_develop_prompt.main(["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                               "test_zorblat_frobs_a_nitz", "make unit"])
    green = re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)

    assert ([b"Add the replacement test cases the step names" in red,
             b"permitted, and it is required for the step to pass, to delete exactly the cases it names" in green]
            == [True, True])


def test_cli_verify_green_prompt_asks_a_missing_test_reject_for_a_missing_test_line_and_revise_green_asks_it_of_an_impossible_with_no_test_edit_1808(
        tmp_path, run_cli, build_develop_prompt):
    verify = importlib.import_module("veri.build_verify_prompt")
    reason = tmp_path / "reason.md"
    reason.write_text("rejected\n")
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"

    v_code, v_out, v_err = run_cli(verify, ["--fast-cmd", "make unit", "green", _spec(tmp_path), "tests/slug_cases.py", "case one"])
    r_code, r_out, r_err = run_cli(build_develop_prompt, ["revise", "green", _spec(tmp_path), step, "make test", str(reason)])

    verify_flat, revise_flat = " ".join(v_out.split()), " ".join(r_out.split())
    verify_rule = next((s for s in re.split(r"(?<=\.) ", verify_flat) if "MISSING_TEST: <behaviour>" in s), "")
    revise_rule = next((s for s in re.split(r"(?<=\.) ", revise_flat) if "MISSING_TEST: <behaviour>" in s), "")
    assert (v_code, v_err, r_code, r_err) == (0, "", 0, "")
    assert [word in verify_rule for word in ("REJECT", "no test pins")] == [True, True]
    assert [word in revise_rule for word in ("IMPOSSIBLE", "edit no test")] == [True, True]


def test_main_renders_a_green_prompt_for_a_suite_repair_or_ci_repair_step_permitting_the_failing_tests_edit_with_every_other_test_frozen_and_without_the_freeze_rule_1653(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    steps = {
        "suite-repair": "fix the full-suite failure: tests/zorblat.test.sh — FAIL - zorblat frobs a nitz ⟦suite-repair⟧",
        "ci-repair": "CI job gates is red on a1b2c3d: tests/zorblat.test.sh — FAIL - zorblat frobs a nitz ⟦ci-repair⟧",
    }
    freeze = _fragment("_develop-green-freeze-rule.md")
    edit = _fragment("_develop-repair-test-edit.md")

    results = {}
    for name, step in steps.items():
        code = build_develop_prompt.main(["green", str(spec), step, "make test", "tests/zorblat.test.sh",
                                          "zorblat frobs a nitz", "make unit"])
        out, _ = capsysbinary.readouterr()
        prompt = re.sub(rb"\s+", b" ", out)
        results[name] = (code, freeze in prompt, edit in prompt)

    assert results == {"suite-repair": (0, False, True), "ci-repair": (0, False, True)}


def test_main_renders_a_revise_green_prompt_for_a_suite_repair_or_ci_repair_step_without_the_leave_the_tests_rule_or_the_freeze_rule_and_permitting_the_failing_tests_edit_1653(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected: the roster still lists a deleted suite\n")
    steps = {
        "suite-repair": "fix the full-suite failure: tests/zorblat.test.sh — FAIL - zorblat frobs a nitz ⟦suite-repair⟧",
        "ci-repair": "CI job gates is red on a1b2c3d: tests/zorblat.test.sh — FAIL - zorblat frobs a nitz ⟦ci-repair⟧",
    }
    leave = _fragment("_develop-test-rewrite-none.md")
    freeze = _fragment("_develop-green-freeze-rule.md")
    edit = re.search(rb"Redoing green on a .{0,40}suite-repair.*?test stays frozen\.", _fragment("develop-revise.md")).group()
    results = {}
    for name, step in steps.items():
        code = build_develop_prompt.main(["revise", "green", str(spec), step, "make test", str(reason)])
        out, _ = capsysbinary.readouterr()
        prompt = re.sub(rb"\s+", b" ", out)
        results[name] = (code, prompt.count(edit), leave in prompt, freeze in prompt)

    assert results == {"suite-repair": (0, 1, False, False), "ci-repair": (0, 1, False, False)}


def test_main_renders_the_ordinary_freeze_rule_in_a_green_prompt_for_a_step_naming_suite_repair_mid_sentence_1919(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    step = "zorblat quotes ⟦suite-repair⟧ mid-sentence in its prose ⟦criterion 1⟧"

    code = build_develop_prompt.main(["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                                      "test_zorblat_frobs_a_nitz", "make unit"])
    prompt = re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)

    assert (code, b"**Do not modify the test.**" in prompt, b"You may edit the failing test" in prompt) == (0, True, False)


def test_main_renders_the_ordinary_freeze_rule_in_a_green_prompt_for_a_step_naming_ci_repair_mid_sentence_1919(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    step = "zorblat quotes ⟦ci-repair⟧ mid-sentence in its prose ⟦criterion 1⟧"

    code = build_develop_prompt.main(["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                                      "test_zorblat_frobs_a_nitz", "make unit"])
    prompt = re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)

    assert (code, b"**Do not modify the test.**" in prompt, b"You may edit the failing test" in prompt) == (0, True, False)


def test_main_renders_no_suite_repair_paragraph_in_a_green_prompt_for_a_step_naming_suite_repair_mid_sentence_1919(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    step = "zorblat quotes ⟦suite-repair⟧ mid-sentence in its prose ⟦criterion 1⟧"

    code = build_develop_prompt.main(["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                                      "test_zorblat_frobs_a_nitz", "make unit"])
    prompt = re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)

    assert (code, b"This step repairs the full run.** Its text lists every suite" in prompt) == (0, False)


def test_main_renders_no_fixture_repair_paragraph_in_a_green_prompt_for_a_step_naming_fixture_repair_mid_sentence_1989(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    step = "zorblat quotes ⟦fixture-repair⟧ mid-sentence in its prose ⟦criterion 3⟧"

    code = build_develop_prompt.main(["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                                      "test_zorblat_frobs_a_nitz", "make unit"])
    prompt = re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)

    assert (code, b"This step repairs a fixture.**" in prompt) == (0, False)


def test_main_renders_the_fixture_repair_paragraph_in_a_green_prompt_for_a_step_ending_in_fixture_repair_1989(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    step = "repairs the fixture 'quux' in tests/fx.sh, reproduced by a case in tests/t.sh ⟦fixture-repair⟧ ⟦added⟧ ⟦criterion 3⟧"

    code = build_develop_prompt.main(["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                                      "test_zorblat_frobs_a_nitz", "make unit"])
    prompt = re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)

    assert (code, b"This step repairs a fixture.**" in prompt) == (0, True)


def test_mid_line_marks_render_todays_prompts(tmp_path, capsysbinary, build_develop_prompt):
    verify = importlib.import_module("veri.build_verify_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    step = "zorblat quotes ⟦ci-repair⟧ and ⟦suite-repair⟧ mid-line in its prose ⟦criterion 1⟧"

    def flat(module, argv):
        assert module.main(argv) == 0
        return re.sub(rb"\s+", b" ", capsysbinary.readouterr().out)

    red = flat(build_develop_prompt, ["red", str(spec), step, "make test"])
    green = flat(build_develop_prompt, ["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                                        "test_zorblat_frobs_a_nitz", "make unit"])
    verified = flat(verify, ["--step", step, "--fast-cmd", "make unit", "green", str(spec),
                             "tests/py/test_zorblat.py", "test_zorblat_frobs_a_nitz"])

    ci_red = b"This step repairs a red CI run.**"
    suite_develop = b"This step repairs the full run.** Its text lists every suite"
    ci_verify = b"This step repairs a failure that reproduces only on CI.**"
    assert ([ci_red in red, suite_develop in red, ci_red in green, suite_develop in green,
             ci_verify in verified, suite_develop in verified]
            == [False, False, False, False, False, False])


@pytest.mark.parametrize("doc", ["SKILL.md", "SCRIPTS.md"])
def test_the_red_missing_call_shape_documented_in_each_doc_filled_in_runs_to_exit_0_with_a_prompt_1865(
        doc, tmp_path, run_cli, build_develop_prompt):
    import shlex
    text = (SCRIPTS.parent / doc).read_text()
    spans = re.findall(r"`((?:\S*build-develop-prompt\.sh )?red-missing [^`]*)`", text)
    assert spans, f"{doc} documents no red-missing call"
    reason = tmp_path / "reason.md"
    reason.write_text("MISSING_TEST: no case requires GLORPNAK to be counted once\n")
    step = "QWIXTLE: a seed gains the block"
    fills = {"<test-cmd>": "make test", "<reason-file>": str(reason), "<step-text>": step, "<spec-file>": _spec(tmp_path)}
    for span in spans:
        argv = []
        for tok in shlex.split(span.split("red-missing", 1)[0] and span[span.index("red-missing"):]):
            if "$(" in tok:
                tok = step
            elif "spec" in tok and tok not in fills:
                tok = _spec(tmp_path)
            argv.append(fills.get(tok, tok))
        code, out, err = run_cli(build_develop_prompt, argv)
        assert (code, bool(out.strip())) == (0, True), f"{doc}: `{span}` -> exit {code}: {err}"


def test_main_renders_the_fixture_repair_paragraph_in_green_and_revise_green_for_a_marked_step_permitting_the_named_fixture_only_and_in_no_other_prompt_1021(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    s, r = str(spec), str(reason)
    marked = ("the case passes under load: repairs the fixture 'awake-clock' in tests/zorblat.test.sh, "
              "reproduced by a case in tests/zorblat.test.sh ⟦fixture-repair⟧ ⟦criterion 1⟧")
    unmarked = "the case passes under load ⟦criterion 1⟧"

    def rendered(argv):
        code = build_develop_prompt.main(argv)
        out, _ = capsysbinary.readouterr()
        return re.sub(rb"\s+", b" ", out) if code == 0 else None

    prompts = {
        ("marked", "green"): rendered(["green", s, marked, "make test", "t.py", "test_x", "make unit"]),
        ("marked", "revise green"): rendered(["revise", "green", s, marked, "make test", r]),
        ("unmarked", "green"): rendered(["green", s, unmarked, "make test", "t.py", "test_x", "make unit"]),
        ("marked", "red"): rendered(["red", s, marked, "make test"]),
        ("marked", "refactor"): rendered(["refactor", s, marked, "make test", "t.py"]),
        ("marked", "revise refactor"): rendered(["revise", "refactor", s, marked, "make test", r]),
    }
    fixture = _fragment("_develop-green-fixture-repair.md")

    assert {key: prompt is not None and fixture in prompt for key, prompt in prompts.items()} == {
        ("marked", "green"): True,
        ("marked", "revise green"): True,
        ("unmarked", "green"): False,
        ("marked", "red"): False,
        ("marked", "refactor"): False,
        ("marked", "revise refactor"): False,
    }


def test_main_refuses_a_fixture_repair_step_in_green_with_exit_2_naming_the_fixture_repair_partial_when_it_is_missing_1021(
        tmp_path, capsysbinary):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    (scripts / "prompts").mkdir()
    (scripts / "veri" / "build_develop_prompt.py").write_bytes((SCRIPTS / "veri" / "build_develop_prompt.py").read_bytes())
    for name in ("develop-green.md", "_develop-shared.md"):
        (scripts / "prompts" / name).write_bytes(b"x\n")
    loader = importlib.util.spec_from_file_location("build_develop_prompt_no_fixture_partial",
                                                    scripts / "veri" / "build_develop_prompt.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    step = ("the case passes under load: repairs the fixture 'awake-clock' in tests/zorblat.test.sh, "
            "reproduced by a case in tests/zorblat.test.sh ⟦fixture-repair⟧ ⟦criterion 1⟧")

    code = module.main(["green", str(spec), step, "make test", "t.py", "test_x", "make unit"])

    assert (code, *capsysbinary.readouterr()) == (
        2, b"", f"build-develop-prompt: cannot read '{scripts / 'prompts' / '_develop-green-fixture-repair.md'}'\n".encode())


def test_main_accepts_exactly_the_phases_in_phases_and_want_has_exactly_their_keys_1890(capsysbinary, build_develop_prompt):
    unknown = {}
    for phase in (*build_develop_prompt.PHASES, "bogus"):
        build_develop_prompt.main([phase])
        unknown[phase] = b"unknown phase" in capsysbinary.readouterr().err

    assert unknown == {**dict.fromkeys(build_develop_prompt.PHASES, False), "bogus": True}
    assert set(build_develop_prompt.WANT) == set(build_develop_prompt.PHASES)
    assert len(build_develop_prompt.PHASES) == len(set(build_develop_prompt.PHASES))


def test_main_tells_a_green_prompt_of_a_guard_subject_step_it_may_edit_the_guard_subject_file_and_no_other_test_file_1775(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    step = ("each guard's scanner-failure output names the guard "
            "⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 5⟧")
    build_develop_prompt.main(["green", str(spec), step, "make test", "tests/py/test_zorblat.py",
                               "test_zorblat_frobs_a_nitz", "make unit"])
    out, _ = capsysbinary.readouterr()
    prompt = re.sub(rb"\s+", b" ", out)

    assert _fragment("_develop-guard-subject-grant.md") in prompt, prompt


def test_cli_red_red_supersede_red_missing_and_revise_red_prompts_built_from_a_subdirectory_name_red_prediction_and_red_run_output_by_absolute_paths_under_the_repo_root_tdd_1895(
        tmp_path, monkeypatch, run_cli, build_develop_prompt):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    sub = repo / "skills"
    sub.mkdir()
    monkeypatch.chdir(sub)
    root = os.path.realpath(repo)
    step = "QWIXTLE: a seed ending in a newline gains the block and reports added"
    reason = tmp_path / "reason.md"
    reason.write_text("MISSING_TEST: no case requires GLORPNAK\nWRONG_TEST: nope\nVERDICT: REJECT\n")
    spec = _spec(tmp_path)
    calls = {
        "red": ["red", spec, step, "make test"],
        "red-supersede": ["red-supersede", spec, step, "make test", "test_old_case", "test_other_case"],
        "red-missing": ["red-missing", spec, step, "make test", str(reason)],
        "revise-red": ["revise", "red", spec, step, "make test", str(reason)],
    }
    problems = []
    for label, argv in calls.items():
        code, out, err = run_cli(build_develop_prompt, argv, cwd=str(sub))
        assert code == 0, err
        for name in ("red-prediction.md", "red-run-output.txt"):
            bare = re.findall(rf"(?<![\w/.-]){re.escape('.tdd/' + name)}", out)
            absolute = re.findall(rf"{re.escape(root + '/.tdd/' + name)}", out)
            if bare or not absolute:
                problems.append(f"{label}: {name} bare={len(bare)} absolute={len(absolute)}")

    assert problems == []


def test_main_builds_a_revise_prompt_for_the_rebase_phase_and_exits_0_instead_of_refusing_it_as_an_unknown_phase_to_revise_2127(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rebase rejected\n")

    code = build_develop_prompt.main(["revise", "rebase", str(spec), "s", "make test", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, err) == (0, b"")
    assert out


def test_every_phase_revise_md_sends_to_build_develop_prompt_revise_passes_the_scripts_argument_check_with_no_exit_2_2127(
        tmp_path, capsysbinary, build_develop_prompt):
    text = (SCRIPTS.parent / "REVISE.md").read_text()
    listed = re.search(r"phases sent to `build-develop-prompt\.sh revise <phase>` are ([^;]+);", text)
    assert listed, "REVISE.md names no list of the phases it sends to build-develop-prompt.sh revise"
    phases = set(re.findall(r"[a-z][a-z-]*", listed.group(1).replace(" and the interface phases", ",")))
    phases -= {"and", "the", "interface", "phases"}
    phases |= set(re.findall(r"build-develop-prompt\.sh revise ([a-z][a-z-]*) ", text))
    phases |= set(re.findall(r"`revise ([a-z][a-z-]*)`", text))
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")

    codes = {}
    for phase in sorted(phases):
        codes[phase] = build_develop_prompt.main(
            ["revise", phase, str(spec), "s", "make test", str(reason), "make unit"])
        capsysbinary.readouterr()

    assert "rebase" in codes
    assert {p: c for p, c in codes.items() if c == 2} == {}


def test_main_builds_a_predicate_prompt_from_the_spec_the_candidate_the_test_command_and_the_bound_file_list_2194(
        tmp_path, run_cli, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    bound = "zorblat_one.sh zorblat_two.sh"

    code, out, _ = run_cli(build_develop_prompt, ["predicate", str(spec), "QWIXTLE: hoist the quux", "make unit", bound])

    assert (code, bound in out, "QWIXTLE: hoist the quux" in out, "make unit" in out) == (0, True, True, True)
