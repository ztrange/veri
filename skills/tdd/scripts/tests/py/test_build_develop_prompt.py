"""In-process cases for veri/build_develop_prompt.py, the module build-develop-prompt.sh is a shim over."""
import importlib
import importlib.util
import os
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

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
