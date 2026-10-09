"""In-process cases for veri/build_develop_prompt.py, the module build-develop-prompt.sh is a shim over."""
import importlib
import importlib.util
import io
import os
import re
import sys

import pytest

from conftest import SCRIPTS

PHASES = b"red|green|refactor|cover|transform|diff|structural|predicate|revise|reconcile|exhausted|over-budget|rebase"
USAGE = b"build-develop-prompt.sh: usage: " + PHASES + b" <issue-spec-file> <step-text> <test-cmd> ...\n"


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
            2, b"", b"build-develop-prompt.sh: unknown phase to revise 'bogus' (want red|green|refactor|diff)\n"
            + USAGE),
        ("diff", s, "s", "c"): (2, b"", b"build-develop-prompt: diff needs 5 arguments, got 4\n" + USAGE),
        ("revise", "diff", s, "s", "c", r): (2, b"", b"build-develop-prompt: missing <fast-cmd>\n" + USAGE),
    }


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
                ("revise", "refactor", s, "s", "c", r), ("revise", "diff", s, "s", "c", r, "f"),
                ("reconcile", s, "s", "c", "b", "sha"), ("over-budget", s, "s", "c", "1", "2"),
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
    assert build_develop_prompt.REVISE_PHASES == ("red", "green", "refactor", "diff")


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
        "build-develop-prompt.sh: unknown phase to revise 'red\n' (want red|green|refactor|diff)")
    results = {}
    for argv in expected:
        code = no_prompts.main(list(argv))
        results[argv] = (code, *capsysbinary.readouterr())

    assert results == expected


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
        for call in (["green", str(plain), f"x{marker}y", "make test", "t.sh", "case", "make unit"],
                     ["revise", "green", str(plain), f"x{marker}y", "make test", str(reason)]):
            results[("needs", marker, call[1])] = answer(module, call)
            expected[("needs", marker, call[1])] = cannot_read(prompts / partial)
        for call in (["red", str(plain), f"x{marker}y", "make test"],
                     ["revise", "red", str(plain), f"x{marker}y", "make test", str(reason)]):
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
    step = "x ⟦replaces-case⟧ ⟦suite-repair⟧ {{INCLUDE:_s.md}}"
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
                             b"       " + here + b"/timed-test-run.sh affected '<the suites affected-suites.sh "
                             b"printed>' <the command that runs them>"], b"")

    assert results == expected


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

    def both_ways(prompt, gap, a, b):
        return says(prompt, rb"%s[^.]{0,%d}%s|%s[^.]{0,%d}%s" % (a, gap, b, b, gap, a))

    def offers(token, cls):
        return any_line(refactor, rb"^%s:.*%s[^|]{0,40}\|" % (token, cls), 0)

    checks = {
        "red carries spec, step, test command and AGAINST_UNMODIFIED": all(
            part in red for part in (b'zorblat("Frob & Nitz/Quux")', step.encode(), cmd.encode(),
                                     b"AGAINST_UNMODIFIED")),
        "green names the test path and target and forbids modifying the test": (
            test_path.encode() in green and target.encode() in green and any_line(
                green, rb"(do not|don't|never) (modify|change|edit|touch|weaken).{0,40}test"
                       rb"|test.{0,40}(must not|may not) be (modified|changed|edited|touched)")),
        "refactor carries touched files, the no-generality rule and RESULT:": (
            touched.encode() in refactor
            and any_line(refactor, rb"(no|not|never|without)[^.]{0,80}(generality|generali[sz]ation|abstraction)")
            and b"RESULT:" in refactor),
        "revise carries the reason verbatim and IMPOSSIBLE": reason_text.encode() in revise and b"IMPOSSIBLE" in revise,
        "refactor requires a CANDIDATES: line, one per line, or none": (
            any_line(refactor, rb"^CANDIDATES:", 0) and says(refactor, rb"one[^.]{0,20}per line")
            and any_line(refactor, rb"^CANDIDATES:.*none")),
        "red runs the suite holding the new case, not the full suite, falling back and saying so": (
            says(red, rb"suite (that |which )?(holds|contains|holding|containing)[^.]{0,40}case")
            and says(red, rb"(not|rather than|instead of|no need to|never|don't|do not)[^.]{0,40}(full|whole|entire) suite")
            and says(red, rb"(cannot|can.t|no way to|unable to|has no way)[^.]{0,60}(suite|file)")
            and says(red, rb"(say|says|saying|state|states|note|report) (so|it|this|that)[^.]{0,30}report")),
        "green iterates on the target suite and runs the full suite once before SUITE:": (
            says(green, rb"iterat[^.]{0,60}suite|suite[^.]{0,60}iterat")
            and says(green, rb"(full|whole|entire) suite[^.]{0,40}once|once[^.]{0,40}(full|whole|entire) suite")
            and says(green, rb"before[^.]{0,60}SUITE:")),
        "refactor runs the covering suites, not the full suite, naming the PR's full run and the trade-off": (
            says(refactor, rb"suites?[^.]{0,40}cover|cover[^.]{0,40}suites?")
            and says(refactor, rb"(not|rather than|instead of|no need to|never|don't|do not)[^.]{0,40}(full|whole|entire) suite")
            and not says(refactor, rb"verify-refactor[^.]{0,60}(full|whole|entire) suite"
                                   rb"|(full|whole|entire) suite[^.]{0,60}verify-refactor")
            and says(refactor, rb"(full|whole|entire) +suite +runs +once +per +PR")
            and says(refactor, rb"outside +the affected set +surfaces[^.]{0,80}repair step")),
        "every prompt runs tests in the foreground and reports only after they exit": all(
            says(p, rb"foreground") and says(p, rb"(only after|not until|never before)[^.]{0,60}(exit|exits|exited|finish)")
            for p in prompts.values()),
        "every prompt forbids ending the turn mid-run": all(
            says(p, rb"end(ing)?[^A-Za-z0-9]+(your|the|its)[^A-Za-z0-9]+turn") for p in prompts.values()),
        "every prompt forbids git stash and names a safe alternative": all(
            says(p, rb"(never|do not|don't|no)[^.]{0,60}stash") and says(p, rb"git show HEAD:|git worktree add", 0)
            for p in prompts.values()),
        "every prompt forbids git checkout -- <file> and git restore for a probe, naming cp/mv .orig": all(
            says(p, rb"(never|do not|don't|not)[^.]{0,120}git checkout -- <file>")
            and says(p, rb"(never|do not|don't|not)[^.]{0,160}git restore")
            and says(p, rb"(undo|restor)[^.]{0,60}(probe|mutat)")
            and b"cp <file> <file>.orig" in folded(p) and b"mv <file>.orig <file>" in folded(p)
            for p in prompts.values()),
        "refactor defines structural and cosmetic by what the transform changes": (
            both_ways(refactor, 160, rb"structural", rb"(duplication|extract|inline|dead code|rename|scope)")
            and both_ways(refactor, 160, rb"cosmetic", rb"(reword|re-word|re-cite|recite|reflow|re-flow|re-comment)")
            and says(refactor, rb" (without|not|never|leaves) [^.]{0,30}(duplication|identifier|structure)")),
        "refactor applies only structural and reports nothing left to tidy over cosmetic": (
            says(refactor, rb"only[^.]{0,60}structural|structural[^.]{0,60}only")
            and says(refactor, rb"nothing left to tidy[^.]{0,120}cosmetic|cosmetic[^.]{0,120}nothing left to tidy")),
        "every CANDIDATES: line carries its class": offers(b"CANDIDATES", b"structural") and offers(
            b"CANDIDATES", b"cosmetic"),
        "a tests/-only transform is a CANDIDATES: test-only line, never structural": (
            offers(b"CANDIDATES", b"test-only")
            and both_ways(refactor, 160, rb"test-only", rb"only (files|paths) under an? `?tests/")
            and both_ways(refactor, 160, rb"test-only", rb"(never|not)( on| as)? an? `?CANDIDATES: structural")),
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

    def offers(prompt, token, cls):
        return any_line(prompt, rb"^%s:.*%s[^|]{0,40}\|" % (token, cls))

    def carries(prompt, *parts):
        return prompt is not None and all(
            (part.encode() if isinstance(part, str) else part) in prompt for part in parts)

    red = rendered(["red", s, step, cmd])
    green = rendered(["green", s, step, cmd, test_path, target, "make unit"])
    refactor = rendered(["refactor", s, step, cmd, touched])
    revise = rendered(["revise", "red", s, step, cmd, r])
    prompts = (red, green, refactor, revise)

    monkeypatch.setenv("VERI_REFACTOR_BUDGET", "37")
    budgeted = rendered(["refactor", s, step, cmd, touched])
    monkeypatch.delenv("VERI_REFACTOR_BUDGET")

    rc_branch, rc_sha = "tdd/232-zorblat-frob", "3f9a1c0b7e2d4a6f8c1b3e5d7f9a0c2e4b6d8f01"
    reconcile = rendered(["reconcile", s, step, cmd, rc_branch, rc_sha])
    rc_tpl = (SCRIPTS / "prompts" / "develop-reconcile.md").read_bytes()

    fast_cmd = 'make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
    fast_green = rendered(["green", s, step, cmd, test_path, target, fast_cmd])
    revise_green = rendered(["revise", "green", s, step, cmd, r])

    replaces_step = ('⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz" moves to '
                     'tests/py/test_zorblat.py ⟦criterion 1⟧')
    licence = rb"(may|permitted|allowed|licen[cs]ed?)[^.]{0,60}delet|delet[^.]{0,60}(permitted|allowed|licen[cs]ed)"
    replaces_green = rendered(["green", s, replaces_step, cmd, "tests/py/test_zorblat.py",
                               "test_zorblat_frobs_a_nitz", "make unit"])

    repair_step = ("fix the full-suite failure: skills/tdd/scripts/tests/zorblat.test.sh — FAIL - zorblat frobs a nitz; "
                   "skills/tdd/scripts/tests/quux.test.sh — FAIL - quux & {nitz} round-trips ⟦suite-repair⟧")
    repair_named = ("skills/tdd/scripts/tests/zorblat.test.sh", "zorblat frobs a nitz",
                    "skills/tdd/scripts/tests/quux.test.sh", "quux & {nitz} round-trips")
    every_listed = rb"(every|each|all)( of the)? (listed|red|named) suites?"
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

    bug_spec = tmp_path / "bug-spec.md"
    bug_spec.write_bytes(spec_bytes + b"\n## Bug\n\n### What happened\n\nzorblat returned \"FROB_NITZ\" on the quuxed seed."
                         b"\n\n### Expected\n\nzorblat returns \"frob-nitz-quux\".\n\n### Steps to reproduce\n\n"
                         b"Run zorblat --seed \"Frob & Nitz/Quux\".\n\n### Environment\n\nveri on bash 5.2, macOS 15.\n")
    bug_red = rendered(["red", str(bug_spec), step, cmd])
    names_with_number = rb"(name|naming)[^.]{0,60}#<n>|#<n>[^.]{0,60}(name|naming)"

    over_budget = rendered(["over-budget", s, step, cmd, "3.47", "2.50"])
    over_budget_flat = re.sub(rb"\s+", b" ", over_budget or b"")
    _, mark, over_budget_report = over_budget_flat.partition(b"### Report")
    over_budget_extra = rendered(["over-budget", s, step, cmd, "3.47", "2.50", r])

    checks = {
        "refactor defines the out-of-scope class, reported instead of structural": (
            offers(refactor, b"CANDIDATES", b"out-of-scope")
            and both_ways(refactor, 160, rb"out-of-scope",
                          rb"outside the issue.s bounds[^.]{0,80}ruled out by (its|the) spec")
            and both_ways(refactor, 160, rb"out-of-scope",
                          rb"(instead of|rather than|never|not)( on| as)? an? `?(CANDIDATES: )?structural")),
        "refactor applies structural candidates up to its budget, one refactor: commit each, reverting red": (
            both_ways(refactor, 80, rb"budget", rb"structural")
            and both_ways(refactor, 80, rb"commit", rb"refactor:")
            and both_ways(refactor, 60, rb"(each|every|own|per)", rb"refactor:")
            and both_ways(refactor, 80, rb"suites?", rb"after each")
            and both_ways(refactor, 80, rb"revert", rb"red")
            and both_ways(refactor, 80, rb"applied", rb"(transforms|one per|each|every)")),
        "refactor carries VERI_REFACTOR_BUDGET as the budget": both_ways(budgeted, 80, rb"budget", rb"37"),
        "red predicts before the run and carries the prediction footer": (
            both_ways(red, 60, rb"predict", rb"before (you|issuing|any command)")
            and carries(red, b"PREDICTED_FAILURE:", b"PREDICTION_NOTE:")
            and says(red, rb"PREDICTION:[^.]{0,20}MATCHED", 0) and says(red, rb"PREDICTION:[^.]{0,20}DIVERGED", 0)),
        "red's pin path predicts what the break prints and checks it before restoring": (
            both_ways(red, 80, rb"break", rb"predict")
            and both_ways(red, 80, rb"break", rb"(check|compar|match)")
            and says(red, rb"before[^.]{0,40}restor|restor[^.]{0,40}(only after|not until)")),
        "revise asks for a new prediction before the re-run": (
            both_ways(revise, 80, rb"(rewrit|rewrote|new test)", rb"predict")
            and both_ways(revise, 60, rb"predict", rb"before (you|issuing|any command)")),
        "reconcile carries sha, branch and a pinned --force-with-lease, no bare --force, refusing a missing sha": (
            carries(reconcile, rc_sha, rc_branch, f"--force-with-lease={rc_branch}:{rc_sha}")
            and not any_line(rc_tpl, rb"--force($|[^-]|-($|[^w]))")
            and all(m.startswith(b"--force-with-lease=") for m in re.findall(rb"--force-with-lease[^\s`]*", rc_tpl))
            and refused(["reconcile", s, step, cmd, rc_branch, ""])),
        "every prompt forbids global config, naming environment variables and throwaway directories": all(
            says(p, rb"(never|do not|don't|not)[^.]{0,80}(global|user-level)[^.]{0,60}config")
            and says(p, rb"environment variables?") and says(p, rb"(throwaway|temporary|scratch)[^.]{0,20}director(y|ies)")
            for p in prompts),
        "red states behaviour over mechanism with the spy carve-out, make profile and UNTESTABLE": (
            says(red, rb"(process|fork)[^.]{0,20}count|timing") and says(red, rb"make profile")
            and says(red, rb"in-process spy") and says(red, rb"PATH[^.]{0,60}shim|shim[^.]{0,60}(count|real process)")
            and says(red, rb"UNTESTABLE")),
        "green carries <fast-cmd> verbatim and refuses an empty one": (
            carries(fast_green, fast_cmd) and refused(["green", s, step, cmd, test_path, target, ""])),
        "red names the missing name on PREDICTED_FAILURE:": both_ways(red, 60, rb"PREDICTED_FAILURE",
                                                                     rb"(missing|absent) name"),
        "revise ends with PREDICTED_FAILURE: and PREDICTION: MATCHED | DIVERGED": (
            carries(revise, b"PREDICTED_FAILURE:") and says(revise, rb"PREDICTION:[^.]{0,20}MATCHED", 0)
            and says(revise, rb"PREDICTION:[^.]{0,20}DIVERGED", 0)),
        "refactor leaves the touched-files list only to remove duplication": (
            both_ways(refactor, 60, rb"outside", rb"duplication") and both_ways(refactor, 60, rb"outside", rb"only")),
        "refactor runs the suites covering an out-of-list file": both_ways(refactor, 80, rb"outside", rb"suites?"),
        "green offers one to three SPLIT: lines changing no production code": (
            any_line(green, rb"^SPLIT:") and says(green, rb"one to three|1 to 3|(at most|no more than) three")
            and both_ways(green, 80, rb"SPLIT", rb"(no|any|without changing) production code")),
        "revise green offers the same SPLIT: lines": (
            any_line(revise_green, rb"^SPLIT:")
            and says(revise_green, rb"one to three|1 to 3|(at most|no more than) three")
            and both_ways(revise_green, 80, rb"SPLIT", rb"(no|any|without changing) production code")),
        "green for a replaces-case step permits deleting that case and no other": (
            says(replaces_green, licence) and not says(green, licence)
            and both_ways(replaces_green, 60, rb"(never|not|forbid|forbidden|must not|rejected)",
                          rb"(any|every) other (bash )?case")),
        "#690 green for a two-suite repair names both suites and cases and asks every listed suite green": (
            carries(repair_green, *repair_named) and both_ways(repair_green, 60, every_listed, rb"green")),
        "#690 revise green for a two-suite repair does the same": (
            carries(repair_revise, *repair_named) and both_ways(repair_revise, 60, every_listed, rb"green")),
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
        "red names a bug's case with #<n>, and a spec with no Bug section is not told to": (
            says(bug_red, names_with_number) and not says(red, names_with_number)),
        "refactor reports FLAGS: lines in the three classes or none, no NEW_STEP:, defining each class": (
            any_line(refactor, rb"^FLAGS:") and any_line(refactor, rb"^FLAGS:.*none")
            and not any_line(refactor, rb"^NEW_STEP:")
            and all(offers(refactor, b"FLAGS", c) for c in (b"overfit", b"uncovered-spec", b"beyond-spec"))
            and both_ways(refactor, 120, rb"overfit", rb"(without|rather than|instead of) implementing")
            and both_ways(refactor, 120, rb"uncovered-spec", rb"(spec (requires|asks)|required by the spec)")
            and both_ways(refactor, 120, rb"beyond-spec", rb"(does not|doesn.t|never) (ask|require)")),
        "over-budget carries the step, both figures and the spec": carries(
            over_budget, step, b"3.47", b"2.50", b'zorblat("Frob & Nitz/Quux")'),
        "over-budget asks for SPLIT: or NEEDS_USER:": (
            any_line(over_budget, rb"^SPLIT:") and any_line(over_budget, rb"^NEEDS_USER:")),
        "over-budget says a crossing is not a verdict and one behaviour, simply expensive, answers": (
            says(over_budget_flat, rb"not a verdict") and says(over_budget_flat, rb"one behaviour[^.]*simply expensive")),
        "over-budget gives the simply-expensive answer its own report shape": (
            mark == b"### Report"
            and says(over_budget_report, rb"simply expensive[^.]*(no|neither)[^.]*SPLIT:[^.]*NEEDS_USER:")),
        "over-budget with fewer than five arguments after the phase refuses": all(
            refused(["over-budget", *args]) for args in ([], [s], [s, step], [s, step, cmd], [s, step, cmd, "3.47"])),
        "over-budget ignores a reason file past <budget> and names no rejection reason or verdict": (
            over_budget is not None and over_budget_extra == over_budget
            and reason_text.encode() not in over_budget_extra
            and not says(over_budget_flat, rb"rejection reason")
            and not says(over_budget, rb"REJECT|VERDICT", 0)),
    }

    assert checks == dict.fromkeys(checks, True)


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
    every_phase = (red, green, refactor, revise)

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

    def commit_suffix(prompt):
        return prompt is not None and any(
            b"(#<issue>)" in line and b"commit" in line.lower() for line in prompt.split(b"\n"))

    dd_fast = 'make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(build_develop_prompt.__file__)))
    timed = os.fsencode(os.path.join(scripts_dir, "timed-test-run.sh"))
    fast_line = timed + b" fast '' " + dd_fast.encode()

    def runs_fast_then_affected(prompt):
        return (prompt is not None and fast_line in prompt
                and timed + b" affected " in prompt[prompt.index(fast_line) + len(fast_line):]
                and any_line(prompt, rb"both( runs)?( are| stay)? green", re.I))

    ddf = rendered(["diff", s, dd_step, cmd, dd_fast])
    rdf = rendered(["revise", "diff", s, dd_step, cmd, r, dd_fast])

    checks = {
        "develop-rebase names both shas, every conflicting file and the test command, resolves by git rebase "
        "<onto-sha>, leaves the ledger's ticks and marks untouched, ends with REBASE: RESOLVED | FAILED, "
        "and refuses a missing argument": (
            carries(rebase, rb_onto, rb_pre, *rb_files.split("\n"), cmd, f"git rebase {rb_onto}",
                    "ledger", "[x]", "⟂ refactor pending")
            and rb_lines[-1].startswith(b"REBASE: RESOLVED | FAILED")
            and refused(["rebase", s, step, cmd, rb_onto, rb_pre, ""])
            and refused(["rebase", s, step, cmd, rb_onto, "", rb_files])),
        "cover and transform each print their own prompt carrying the step, and an unknown phase is refused": (
            carries(cover, step) and carries(transform, step) and cover not in (red, transform)
            and transform != red and refused(["covers", s, step, cmd])),
        "#679 develop-cover allows COVERED: unreachable only for a step that only deletes code no caller reaches": (
            any_line(cover, rb"^COVERED:.*unreachable")
            and both_ways(cover, 120, rb"unreachable", rb"only delet")
            and both_ways(cover, 60, rb"no caller", rb"reach")
            and both_ways(cover, 120, rb"PROOF:", rb"every caller")
            and says(cover, rb"none exists") and says(cover, rb"every caller passes a no-op")
            and says(cover, rb"never read")),
        "#679 develop-cover allows COVERED: type-only only for a step that changes only types": (
            any_line(cover, rb"^COVERED:.*type-only")
            and both_ways(cover, 120, rb"type-only", rb"changes only types")
            and both_ways(cover, 120, rb"PROOF:", rb"type-check command")
            and says(cover, rb"type-check command[^.]{0,60}(ran|run) green")
            and carries(cover, "npx tsc --noEmit", "mypy")),
        "#679 develop-cover says reshaped runtime code is never unreachable or type-only, and carries PROOF:": (
            both_ways(cover, 40, rb"reshap", rb"runtime code")
            and both_ways(cover, 80, rb"runtime code", rb"never `?unreachable`? or `?type-only")
            and says(cover, rb"(^|[^a-z])reachable code[^.]{0,40}no test watches")
            and says(cover, rb"no test watches[^.]{0,60}COVERED: no")
            and any_line(cover, rb"^PROOF:")),
        "every built developer prompt states the comment rule": all(
            says(p, rb"contract header") and says(p, rb"usage line[^.]{0,40}exit[- ]code table")
            and says(p, rb"warning[^.]{0,60}shell itself is the hazard") and says(p, rb"succinct")
            and says(p, rb"no rationale") and says(p, rb"no issue archaeology")
            and says(p, rb"no restatement of the next line")
            for p in every_phase),
        "every built developer prompt states where rationale goes: a test first, an ADR second, nowhere third": all(
            says(p, rb"rationale[^.]{0,80}test first") and says(p, rb"ADR second") and says(p, rb"nowhere third")
            for p in every_phase),
        "develop-refactor applies only duplication removal against code this cycle wrote": (
            both_ways(refactor, 30, rb"only", rb"duplication removal")
            and says(refactor, rb"duplication[^.]{0,80}(this|the) cycle wrote")
            and says(refactor, rb"(no|never|not)[^.]{0,30}other structural transform")
            and says(refactor, rb"extract(ing)? a module") and says(refactor, rb"mov(e|ing) behaviou?r")
            and says(refactor, rb"renam(e|ing)[^.]{0,20}across files")),
        "develop-refactor reports every other structural candidate on CANDIDATES: structural, which "
        "refactor-owed append records under the step's name": (
            both_ways(refactor, 120, rb"every other structural candidate", rb"CANDIDATES: structural")
            and both_ways(refactor, 120, rb"structural candidate", rb"(rather than|instead of) apply(ing)?")
            and owed_code == 0 and step_at is not None and candidate_at is not None and step_at < candidate_at),
        "develop-structural is bounded to the issue's touched files, one refactor: commit, no test file": (
            carries(structural, structural_candidate, issue_touched)
            and both_ways(structural, 80, rb"(bound|limit|confine|only)", rb"(touched|files)")
            and both_ways(structural, 80, rb"commit", rb"refactor:")
            and both_ways(structural, 40, rb"(no|never|not|must not)", rb"test file")),
        "#691 develop-predicate asks for one shell predicate, false now and true once applied, and refuses "
        "a missing argument": (
            carries(predicate, structural_candidate, issue_touched, cmd,
                    "PREDICATE: <command>", "PREDICATE: NONE — <why>")
            and both_ways(predicate, 40, rb"(one|a single)", rb"(shell )?predicate")
            and both_ways(predicate, 60, rb"(fail|false|non-?zero)", rb"(current|unmodified|before)")
            and both_ways(predicate, 80, rb"(succeed|true|exit(s)? 0)", rb"(applied|after)")
            and refused(["predicate", s, structural_candidate, cmd, ""])),
        "#1058 develop-predicate reports an already-applied candidate by its end state, never PREDICATE: NONE": (
            both_ways(predicate, 120, rb"already applied", rb"(report|PREDICATE: <command>)[^.]{0,60}end state")
            and both_ways(predicate, 120, rb"already applied", rb"(succeed|exits? 0)")
            and both_ways(predicate, 120, rb"already applied", rb"(never|not)[^.]{0,30}PREDICATE: NONE")
            and both_ways(predicate, 120, rb"PREDICATE: NONE", rb"no single command can observe")),
        "#691 a refactor-kind step's transform prompts build from the step and its predicate record alone": (
            carries(rk_dev, rk_step) and carries(rk_ver, rk_step, str(rk_predicate))
            and all(lacks(p, rb"structural-predicate", 0) and lacks(p, rb"predicate leaf")
                    and lacks(p, rb"PREDICATE: NONE", 0) and lacks(p, rb"structural[* ]+pass")
                    for p in (rk_dev, rk_ver))),
        "develop-diff makes and commits the change, no commit when unchanged, and adds no test": (
            carries(dd, dd_step, 'zorblat("Frob & Nitz/Quux")') and dd != red
            and both_ways(dd, 80, rb"make", rb"change") and both_ways(dd, 120, rb"change", rb"commit")
            and both_ways(dd, 160, rb"(no|not|never)[^.]{0,20}commit", rb"unchanged")
            and says(dd, rb"(add|write)[^.]{0,20}(no|not a single) (new )?(test|case)"
                         rb"|(do not|don.t|never) (add|write)[^.]{0,20}(test|case)")),
        "#995 develop-diff with an empty <test-cmd> exits 2 with 'missing <test-cmd>' first on stderr": (
            dd_empty_cmd[0] == 2 and dd_empty_cmd[1] == b""
            and dd_empty_cmd[2].split(b"\n")[0] == b"build-develop-prompt: missing <test-cmd>"),
        "#880 a revise of an unknown phase names red|green|refactor|diff": (
            bogus_revise[0] == 2 and bogus_revise[1] == b"" and b"red|green|refactor|diff" in bogus_revise[2]),
        "#880 a revise of a diff-checked step carries the step and the rejection reason": carries(
            revise_diff, dd_step, reason_text),
        "#880 a revise of a diff-checked step asks for no test": (
            lacks(revise_diff, rb"rewritten test|rewrite (a|the) test")
            and not carries(revise_diff, "AGAINST_UNMODIFIED:") and revise_diff is not None
            and b"PREDICTED_FAILURE:" not in revise_diff),
        "#703 an include is replaced by its partial, trailing newlines stripped, before the placeholders": (
            includes["included"][:2] == (0, f"before partial runs {cmd} after\n".encode())),
        "#703 an include inside an included partial is resolved recursively": (
            includes["nested"][:2] == (0, f"before outer inner runs {cmd} end after\n".encode())),
        "#703 an include naming an absent partial exits 2 naming its path, nothing on stdout": (
            includes["dangling"][:2] == (2, b"") and dangling + b"/_probe-absent.md" in includes["dangling"][2]),
        "#703 a partial including itself through another exits 2 naming it, nothing on stdout": (
            includes["cycle"][:2] == (2, b"") and b"_probe-cycle-a.md" in includes["cycle"][2]),
        "#935 the transform prompt states the (#<issue>) commit suffix": commit_suffix(transform),
        "#935 the structural prompt states the (#<issue>) commit suffix": commit_suffix(
            rendered(["structural", s, "a candidate", cmd, "a.sh b.sh"])),
        "#935 the diff prompt states the (#<issue>) commit suffix": commit_suffix(
            rendered(["diff", s, step, cmd, "make unit"])),
        "#935 the revise-diff prompt states the (#<issue>) commit suffix": commit_suffix(revise_diff),
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


def test_main_tells_every_developer_prompt_to_signal_only_processes_it_started_by_recorded_pid_never_by_pattern_and_to_prefix_experiments_exp_1174(
        tmp_path, capsysbinary, monkeypatch, build_develop_prompt):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"REJECT: the case asserts on zorblat()'s log line.\n")
    s, r = str(spec), str(reason)
    step, cmd = "QWIXTLE: a seed ending in a newline gains the block", "make test"

    def rendered(argv):
        code = build_develop_prompt.main(argv)
        out, _ = capsysbinary.readouterr()
        return re.sub(rb"\s+", b" ", out) if code == 0 else None

    prompts = {
        "red": rendered(["red", s, step, cmd]),
        "green": rendered(["green", s, step, cmd, "tests/zorblat.test.sh", "qwixtle seeds", "make unit"]),
        "refactor": rendered(["refactor", s, step, cmd, "scripts/zorblat.sh"]),
        "revise": rendered(["revise", "red", s, step, cmd, r]),
        "exhausted": rendered(["exhausted", s, step, cmd, r]),
    }

    def says(prompt, pattern):
        return prompt is not None and re.search(pattern, prompt, re.I) is not None

    rules = {
        "signals only processes it started": rb"(signal|kill)s? only (the )?processes (it|you) (started|start)",
        "by the pid recorded when it started them": rb"pid (it|you) recorded when (it|you) started",
        "never by name or pattern": rb"never by name or (by )?pattern",
        "names pkill": rb"`pkill`",
        "names killall": rb"`killall`",
        "names kill $(pgrep": rb"`kill \$\(pgrep",
        "experiments carry the exp- prefix": rb"`exp-`[^.]{0,80}(prefix|no live run)|prefix[^.]{0,80}`exp-`",
        "no live run uses that prefix": rb"no live run uses",
    }

    assert {phase: [name for name, pattern in rules.items() if not says(prompt, pattern)]
            for phase, prompt in prompts.items()} == dict.fromkeys(prompts, [])


def test_main_permits_a_replaces_case_green_to_delete_exactly_the_cases_its_step_names_one_or_several_and_forbids_any_case_it_does_not_name(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"REJECT: the case asserts on zorblat()'s log line.\n")
    s, r = str(spec), str(reason)
    several = ('⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz", "zorblat quuxes a frob", '
               '"zorblat refuses an empty nitz" move to tests/py/test_zorblat.py ⟦criterion 1⟧')
    one = ('⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz" moves to '
           'tests/py/test_zorblat.py ⟦criterion 1⟧')

    def rendered(argv):
        code = build_develop_prompt.main(argv)
        out, _ = capsysbinary.readouterr()
        return re.sub(rb"\s+", b" ", out) if code == 0 else None

    prompts = {}
    for name, step in (("several", several), ("one", one)):
        prompts[(name, "green")] = rendered(["green", s, step, "make test", "tests/py/test_zorblat.py",
                                             "test_zorblat_frobs_a_nitz", "make unit"])
        prompts[(name, "revise green")] = rendered(["revise", "green", s, step, "make test", r])

    def says(prompt, pattern):
        return prompt is not None and re.search(pattern, prompt, re.I) is not None

    rules = {
        "permits deleting exactly the cases the step names": (
            rb"(may|permitted|allowed|licen[cs]ed?)[^.]{0,60}delet[^.]{0,60}"
            rb"(exactly|every|each|all)[^.]{0,30}cases?[^.]{0,30}(it|the step|its text) names"),
        "forbids modifying or deleting any case the step does not name": (
            rb"(never|not|forbid|forbidden|must not)[^.]{0,40}modify or delet[^.]{0,40}"
            rb"(any|a) case (it|the step|its text) does not name"),
    }
    one_only = rb"^(?!.*(names one bash case|that one case))"

    assert {key: [rule for rule, pattern in rules.items() if not says(prompt, pattern)]
            + (["never confines a several-case step to one case"]
               if key[0] == "several" and not says(prompt, one_only) else [])
            for key, prompt in prompts.items()} == dict.fromkeys(prompts, [])
