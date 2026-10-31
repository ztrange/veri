"""In-process cases for veri/build_verify_prompt.py, the module build-verify-prompt.sh is a shim over."""
import importlib
import importlib.util
import re
import shutil

import pytest

from conftest import SCRIPTS

USAGE = b"usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]\n"


def scratch(tmp_path, name, drop=(), templates=None):
    scripts = tmp_path / name
    (scripts / "veri").mkdir(parents=True)
    module_path = scripts / "veri" / "build_verify_prompt.py"
    module_path.write_bytes((SCRIPTS / "veri" / "build_verify_prompt.py").read_bytes())
    shutil.copytree(SCRIPTS / "prompts", scripts / "prompts")
    for gone in drop:
        (scripts / "prompts" / gone).unlink()
    for template, text in (templates or {}).items():
        (scripts / "prompts" / template).write_bytes(text)
    loader = importlib.util.spec_from_file_location(f"{name}_build_verify_prompt", module_path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module, scripts / "prompts"


def rendered(tmp_path, capsysbinary, name, templates, argv):
    module, _ = scratch(tmp_path, name, templates=templates)
    code = module.main(argv)
    out, _ = capsysbinary.readouterr()
    assert code == 0
    return out.decode("utf-8", "surrogateescape")


@pytest.fixture
def build_verify_prompt():
    return importlib.import_module("veri.build_verify_prompt")


def test_main_refuses_a_missing_argument_an_option_with_no_value_an_unknown_phase_and_a_green_or_diff_call_without_fast_cmd_with_exit_2_and_its_message_then_the_usage_line(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    results = {}
    for argv in ([], ["red", "", "t"], ["--fast-cmd"], ["bogus", str(spec), "t"],
                 ["green", str(spec), "t", "x"],
                 ["--step", "s", "diff", str(spec), "0123abc", "0123abc"]):
        code = build_verify_prompt.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("red", "", "t"): (2, b"", USAGE),
        ("--fast-cmd",): (2, b"", b"build-verify-prompt: --fast-cmd needs a value\n" + USAGE),
        ("bogus", str(spec), "t"): (2, b"", b"build-verify-prompt: unknown phase 'bogus' "
                                    b"(want red|green|refactor|pin|plan|rebase|transform|diff|expand|cover-new|migrate|contract-a|contract-b)\n"
                                    + USAGE),
        ("green", str(spec), "t", "x"): (
            2, b"", b"build-verify-prompt: green needs --fast-cmd '<fast-tier test command>'\n" + USAGE),
        ("--step", "s", "diff", str(spec), "0123abc", "0123abc"): (
            2, b"", b"build-verify-prompt: diff needs --fast-cmd '<fast-tier test command>'\n" + USAGE),
    }


def test_main_parses_only_leading_options_in_either_order_the_last_winning_and_refuses_an_empty_option_too_many_arguments_and_refactor_without_fast_cmd_in_the_check_order(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    s = str(spec)

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    def refusal(message):
        return (2, b"", message + b"\n" + USAGE)

    refused = {tuple(argv): run(argv) for argv in (
        ["--step"],
        ["--step", "", "red", s, "t"],
        ["--fast-cmd", "", "green", s, "t"],
        ["--fast-cmd", "m", "--step", "", "green", s, "t"],
        ["--step", "", "bogus", "a", "b", "c", "d"],
        ["bogus", "a", "b", "c", "d"],
        ["refactor", s, "t", "0123abc", "x"],
        ["red", s, "t", "--step", "s"],
        ["refactor", s, "t", "0123abc"],
    )}
    assert refused == {
        ("--step",): refusal(b"build-verify-prompt: --step needs a value"),
        ("--step", "", "red", s, "t"): refusal(b"build-verify-prompt: --step needs a value"),
        ("--fast-cmd", "", "green", s, "t"): refusal(b"build-verify-prompt: --fast-cmd needs a value"),
        ("--fast-cmd", "m", "--step", "", "green", s, "t"): refusal(b"build-verify-prompt: --step needs a value"),
        ("--step", "", "bogus", "a", "b", "c", "d"): refusal(b"build-verify-prompt: --step needs a value"),
        ("bogus", "a", "b", "c", "d"): refusal(b"build-verify-prompt: too many arguments"),
        ("refactor", s, "t", "0123abc", "x"): refusal(b"build-verify-prompt: too many arguments"),
        ("red", s, "t", "--step", "s"): refusal(b"build-verify-prompt: too many arguments"),
        ("refactor", s, "t", "0123abc"): refusal(
            b"build-verify-prompt: refactor needs --fast-cmd '<fast-tier test command>'"),
    }

    step_first = run(["--step", "s", "--fast-cmd", "m", "green", s, "t"])
    fast_first = run(["--fast-cmd", "m", "--step", "s", "green", s, "t"])
    repeated = run(["--fast-cmd", "a", "--step", "r", "--fast-cmd", "m", "--step", "s", "green", s, "t"])
    assert (step_first[0], step_first[2]) == (0, b"")
    assert fast_first == step_first
    assert repeated == step_first
    assert build_verify_prompt.PHASES == (
        "red", "green", "refactor", "pin", "plan", "rebase", "transform", "diff")


def test_main_admits_every_sha_slot_only_as_a_whole_string_lowercase_hex_match_and_refuses_diff_without_step_ahead_of_its_shas(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    s = str(spec)

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    def refusal(message):
        return (2, b"", message + b"\n" + USAGE)

    def bad_sha(phase, label, value):
        return refusal(b"build-verify-prompt: " + phase + b" needs " + label
                       + b" as 7-40 lowercase hex characters, got '" + value + b"'")

    refused = {tuple(argv): run(argv) for argv in (
        ["--fast-cmd", "m", "refactor", s, "t", "0123ABC"],
        ["--fast-cmd", "m", "refactor", s, "t", "0123abc\n"],
        ["transform", s, "t", "012345"],
        ["--fast-cmd", "m", "diff", s, "zz", "zz"],
        ["--step", "s", "--fast-cmd", "m", "diff", s, "xyz", "0123abG"],
        ["--step", "s", "--fast-cmd", "m", "diff", s, "xyz", "0123abc"],
        ["rebase", s, "nothex", "0123abc"],
        ["rebase", s, "0123abc", "bad"],
        ["rebase", s, "0123abc"],
        ["--step", "s", "diff", s, "bad", "bad"],
        ["diff", s, "bad", "bad"],
    )}
    assert refused == {
        ("--fast-cmd", "m", "refactor", s, "t", "0123ABC"): bad_sha(b"refactor", b"<base-sha>", b"0123ABC"),
        ("--fast-cmd", "m", "refactor", s, "t", "0123abc\n"): bad_sha(b"refactor", b"<base-sha>", b"0123abc\n"),
        ("transform", s, "t", "012345"): bad_sha(b"transform", b"<base-sha>", b"012345"),
        ("--fast-cmd", "m", "diff", s, "zz", "zz"): refusal(b"build-verify-prompt: diff needs --step '<STEP>'"),
        ("--step", "s", "--fast-cmd", "m", "diff", s, "xyz", "0123abG"): bad_sha(
            b"diff", b"<step-base-sha>", b"0123abG"),
        ("--step", "s", "--fast-cmd", "m", "diff", s, "xyz", "0123abc"): bad_sha(b"diff", b"<base-sha>", b"xyz"),
        ("rebase", s, "nothex", "0123abc"): bad_sha(b"rebase", b"<onto-sha> <pre-rebase-sha>", b"nothex"),
        ("rebase", s, "0123abc", "bad"): bad_sha(b"rebase", b"<onto-sha> <pre-rebase-sha>", b"bad"),
        ("rebase", s, "0123abc"): bad_sha(b"rebase", b"<onto-sha> <pre-rebase-sha>", b""),
        ("--step", "s", "diff", s, "bad", "bad"): refusal(
            b"build-verify-prompt: diff needs --fast-cmd '<fast-tier test command>'"),
        ("diff", s, "bad", "bad"): refusal(
            b"build-verify-prompt: diff needs --fast-cmd '<fast-tier test command>'"),
    }

    admitted = [run(argv)[::2] for argv in (
        ["--fast-cmd", "m", "refactor", s, "t", "0123456789abcdef0123456789abcdef01234567"],
        ["transform", s, "t", "0123abc"],
        ["rebase", s, "0123abc", "0123abd"],
        ["--step", "s", "--fast-cmd", "m", "diff", s, "0123abc", "0123abd"],
    )]
    assert admitted == [(0, b"")] * 4


def test_main_checks_readability_before_any_output_in_the_order_template_shared_spec_chosen_paragraphs_then_the_plan_ledger_never_reads_the_transform_record_and_raises_on_a_directory_spec(
        tmp_path, capsysbinary):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    module_path = scripts / "veri" / "build_verify_prompt.py"
    module_path.write_bytes((SCRIPTS / "veri" / "build_verify_prompt.py").read_bytes())
    loader = importlib.util.spec_from_file_location("scratch_build_verify_prompt", module_path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    prompts = scripts / "prompts"
    prompts.mkdir()
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    bug_spec = tmp_path / "bug.md"
    bug_spec.write_bytes(b"# spec\n\n## Bug\n\nit broke\n")
    refactor_spec = tmp_path / "refactor.md"
    refactor_spec.write_bytes(b"# spec\n\n## Refactor\n\ntidy it\n")
    ledger = tmp_path / "ledger.md"
    missing = tmp_path / "missing.md"

    def run(argv):
        code = module.main(argv)
        return (code, *capsysbinary.readouterr())

    def unreadable(path):
        return (2, b"", b"build-verify-prompt: cannot read '" + str(path).encode() + b"'\n")

    red = ["red", str(spec), "t"]
    assert run(red) == unreadable(prompts / "verify-red.md")
    (prompts / "verify-red.md").write_bytes(b"red\n")
    assert run(red) == unreadable(prompts / "_shared.md")
    (prompts / "_shared.md").write_bytes(b"shared\n")
    assert run(["red", str(missing), "t"]) == unreadable(missing)

    for name in ("verify-green.md", "verify-plan.md", "verify-transform.md"):
        (prompts / name).write_bytes(name.encode() + b"\n")
    assert run(["--fast-cmd", "m", "green", str(bug_spec), "t"]) == unreadable(prompts / "_verify-red-bug.md")
    replaces = ["--step", "s ⟦replaces-case⟧", "--fast-cmd", "m", "green", str(spec), "t"]
    assert run(replaces) == unreadable(prompts / "_verify-green-replaces-case.md")
    repair = ["--step", "s ⟦suite-repair⟧", "--fast-cmd", "m", "green", str(spec), "t"]
    assert run(repair) == unreadable(prompts / "_verify-green-suite-repair.md")
    plan = ["plan", str(refactor_spec), str(ledger)]
    assert run(plan) == unreadable(prompts / "_verify-plan-refactor.md")
    (prompts / "_verify-plan-refactor.md").write_bytes(b"refactor plan\n")
    assert run(plan) == unreadable(ledger)

    transform = run(["transform", str(spec), str(missing), "0123abc"])
    assert (transform[0], transform[2]) == (0, b"")

    with pytest.raises(IsADirectoryError):
        module.main(["red", str(tmp_path), "t"])


def test_main_renders_a_red_prompt_with_shared_the_spec_the_test_path_the_target_or_its_default_and_the_step_block_naming_timed_test_run_through_the_scripts_directory_as_reached_and_reading_no_environment(
        tmp_path, capsysbinary, monkeypatch):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    (scripts / "veri" / "build_verify_prompt.py").write_bytes(
        (SCRIPTS / "veri" / "build_verify_prompt.py").read_bytes())
    (scripts / "prompts").mkdir()
    (scripts / "prompts" / "verify-red.md").write_bytes(
        b"{{SHARED}}\n{{STEP}}spec:\n{{ISSUE_SPEC}}\npath {{TEST_PATH}} target {{TARGET_TEST}}\n"
        b"run {{TIMED_TEST_RUN}} affected\n\n\n")
    (scripts / "prompts" / "_shared.md").write_bytes(b"shared rules\n\n")
    linked = tmp_path / "linked"
    linked.symlink_to(scripts, target_is_directory=True)
    loader = importlib.util.spec_from_file_location(
        "linked_build_verify_prompt", linked / "veri" / "build_verify_prompt.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n\nthe criteria\n\n")
    for name in ("VERI_STEP", "VERI_TEST_CMD", "VERI_PREDICTED_FAILURE", "VERI_RATIONALE"):
        monkeypatch.setenv(name, "ambient " + name)

    def run(argv):
        code = module.main(argv)
        return (code, *capsysbinary.readouterr())

    timed = str(linked / "timed-test-run.sh").encode()
    step_block = (b"### The step under judgement\n\nthe step\n\n"
                  b"Your verdict is about this criterion only: the spec below is the whole issue, and its other\n"
                  b"criteria belong to other steps of the plan.\n\n")
    assert [run(["red", str(spec), "tests/a.test.sh"]),
            run(["--step", "the step", "red", str(spec), "tests/a.test.sh", "case one"])] == [
        (0, b"shared rules\nspec:\n# spec\n\nthe criteria\npath tests/a.test.sh target the target test\n"
            b"run " + timed + b" affected\n", b""),
        (0, b"shared rules\n" + step_block + b"spec:\n# spec\n\nthe criteria\npath tests/a.test.sh target case one\n"
            b"run " + timed + b" affected\n", b""),
    ]


def test_main_resolves_includes_recursively_before_substitution_in_the_template_shared_and_the_replaces_case_and_suite_repair_paragraphs_leaves_them_literal_elsewhere_and_refuses_a_missing_or_self_including_partial(
        tmp_path, capsysbinary):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    module_path = scripts / "veri" / "build_verify_prompt.py"
    module_path.write_bytes((SCRIPTS / "veri" / "build_verify_prompt.py").read_bytes())
    loader = importlib.util.spec_from_file_location("include_build_verify_prompt", module_path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    prompts = scripts / "prompts"
    prompts.mkdir()
    for name, text in {
        "verify-red.md": b"{{SHARED}}\n{{STEP}}spec: {{ISSUE_SPEC}}\nbug: {{BUG_REPRODUCTION}}\n{{INCLUDE:_a.md}}\n",
        "_a.md": b"a[{{INCLUDE:_b.md}}{{INCLUDE:_b.md}}] {{TEST_PATH}}\n",
        "_b.md": b"b={{TARGET_TEST}}\n",
        "_shared.md": b"shared {{INCLUDE:_b.md}}\n",
        "_verify-red-bug.md": b"repro {{INCLUDE:_b.md}}\n",
        "verify-green.md": b"g{{REPLACES_CASE}}{{SUITE_REPAIR}}\n",
        "_verify-green-replaces-case.md": b"rc {{INCLUDE:_b.md}}\n",
        "_verify-green-suite-repair.md": b"sr {{INCLUDE:_b.md}}\n",
        "verify-plan.md": b"{{ISSUE_SPEC}}|{{REFACTOR_PLAN}}|{{LEDGER}}\n",
        "_verify-plan-refactor.md": b"plan {{INCLUDE:_b.md}}\n",
        "verify-pin.md": b"{{INCLUDE:_nope.md}}\n",
        "verify-rebase.md": b"{{INCLUDE:_loop1.md}}\n",
        "_loop1.md": b"{{INCLUDE:_loop2.md}}\n",
        "_loop2.md": b"{{INCLUDE:_loop1.md}}\n",
        "verify-transform.md": b"x{{INCLUDE:}}y\n",
    }.items():
        (prompts / name).write_bytes(text)
    bug_spec = tmp_path / "bug.md"
    bug_spec.write_bytes(b"## Bug\nspec {{INCLUDE:_b.md}}\n")
    refactor_spec = tmp_path / "refactor.md"
    refactor_spec.write_bytes(b"## Refactor\nspec {{INCLUDE:_b.md}}\n")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"spec\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(b"ledger {{INCLUDE:_b.md}}\n")
    p = str(prompts).encode()

    def run(argv):
        code = module.main(argv)
        return (code, *capsysbinary.readouterr())

    assert [
        run(["--step", "step {{INCLUDE:_b.md}}", "red", str(bug_spec), "tp", "tid"]),
        run(["--step", "⟦replaces-case⟧ ⟦suite-repair⟧", "--fast-cmd", "m", "green", str(spec), "tp", "tid"]),
        run(["--fast-cmd", "m", "green", str(spec), "tp", "tid"]),
        run(["plan", str(refactor_spec), str(ledger)]),
        run(["pin", str(spec), "t"]),
        run(["rebase", str(spec), "0123abc", "0123abd"]),
        run(["transform", str(spec), "rec", "0123abc"]),
    ] == [
        (0, b"shared b=tid\n### The step under judgement\n\nstep {{INCLUDE:_b.md}}\n\n"
            b"Your verdict is about this criterion only: the spec below is the whole issue, and its other\n"
            b"criteria belong to other steps of the plan.\n\n"
            b"spec: ## Bug\nspec {{INCLUDE:_b.md}}\nbug: repro {{INCLUDE:_b.md}}\na[b=tidb=tid] tp\n", b""),
        (0, b"g\n\nrc b=tid\n\nsr b=tid\n", b""),
        (0, b"g\n", b""),
        (0, b"## Refactor\nspec {{INCLUDE:_b.md}}|plan {{INCLUDE:_b.md}}|ledger {{INCLUDE:_b.md}}\n", b""),
        (2, b"", b"missing partial: " + p + b"/_nope.md\n"),
        (2, b"", b"partial includes itself: " + p + b"/_loop1.md\n"),
        (0, b"xy\n", b"cat: " + p + b"/: Is a directory\n"),
    ]

    (prompts / "_verify-green-replaces-case.md").write_bytes(b"rc {{INCLUDE:_gone.md}}\n")
    (prompts / "_verify-green-suite-repair.md").write_bytes(b"sr {{INCLUDE:_verify-green-suite-repair.md}}\n")
    replaces_case = run(["--step", "⟦replaces-case⟧", "--fast-cmd", "m", "green", str(spec), "tp", "tid"])
    suite_repair = run(["--step", "⟦suite-repair⟧", "--fast-cmd", "m", "green", str(spec), "tp", "tid"])
    (prompts / "_shared.md").write_bytes(b"shared {{INCLUDE:_gone.md}}\n")
    assert [replaces_case, suite_repair, run(["red", str(spec), "tp", "tid"])] == [
        (2, b"", b"missing partial: " + p + b"/_gone.md\n"),
        (2, b"", b"partial includes itself: " + p + b"/_verify-green-suite-repair.md\n"),
        (2, b"", b"missing partial: " + p + b"/_gone.md\n"),
    ]


def test_main_substitutes_sequentially_globally_and_literally_in_order_filling_each_slot_from_its_phases_argument_and_a_diff_render_runs_fast_cmd_then_the_affected_suites(
        tmp_path, capsysbinary, build_verify_prompt):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    module_path = scripts / "veri" / "build_verify_prompt.py"
    module_path.write_bytes((SCRIPTS / "veri" / "build_verify_prompt.py").read_bytes())
    loader = importlib.util.spec_from_file_location("substitution_build_verify_prompt", module_path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    prompts = scripts / "prompts"
    prompts.mkdir()
    template = (b"{{SHARED}}|{{STEP}}|{{ISSUE_SPEC}}|{{BUG_REPRODUCTION}}|{{REFACTOR_PLAN}}|{{REPLACES_CASE}}|"
                b"{{SUITE_REPAIR}}|{{LEDGER}}|{{TEST_PATH}}|{{TARGET_TEST}}|{{BASE_SHA}}|{{STEP_BASE_SHA}}|"
                b"{{FAST_CMD}}|{{ONTO_SHA}}|{{PRE_REBASE_SHA}}|{{TIMED_TEST_RUN}}\n")
    for phase in ("red", "green", "plan", "rebase", "diff"):
        (prompts / f"verify-{phase}.md").write_bytes(template)
    (prompts / "_shared.md").write_bytes(b"sh\n")
    (prompts / "_verify-green-replaces-case.md").write_bytes(b"rc\n")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"spec {{TEST_PATH}} {{STEP}} {{SHARED}} {{BASE_SHA}} & \\1\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(b"ledger & \\1 {{STEP}}\n\n")
    timed = str(scripts / "timed-test-run.sh").encode()

    def run(main, argv):
        code = main(argv)
        return (code, *capsysbinary.readouterr())

    def block(step):
        return (b"### The step under judgement\n\n" + step + b"\n\n"
                b"Your verdict is about this criterion only: the spec below is the whole issue, and its other\n"
                b"criteria belong to other steps of the plan.\n\n")

    def rendered(*fields):
        return b"|".join(fields) + b"|" + timed + b"\n"

    assert [
        run(module.main, ["--step", "st & \\0", "--fast-cmd", "a & b \\1 /x", "diff", str(spec), "0123abc", "4567def"]),
        run(module.main, ["rebase", str(spec), "89abcde", "fedcba9"]),
        run(module.main, ["plan", str(spec), str(ledger)]),
        run(module.main, ["red", str(spec), "tp"]),
        run(module.main, ["--step", "⟦replaces-case⟧", "--fast-cmd", "m", "green", str(spec), "tp", "tid"]),
    ] == [
        (0, rendered(b"sh", block(b"st & \\0"), b"spec 0123abc {{STEP}} {{SHARED}} 0123abc & \\1", b"", b"", b"", b"",
                     b"", b"0123abc", b"4567def", b"0123abc", b"4567def", b"a & b \\1 /x", b"", b""), b""),
        (0, rendered(b"sh", b"", b"spec 89abcde {{STEP}} {{SHARED}} fedcba9 & \\1", b"", b"", b"", b"",
                     b"", b"89abcde", b"fedcba9", b"fedcba9", b"", b"", b"89abcde", b"fedcba9"), b""),
        (0, rendered(b"sh", b"", b"spec " + str(ledger).encode() + b" {{STEP}} {{SHARED}}  & \\1", b"", b"", b"", b"",
                     b"ledger & \\1 {{STEP}}", str(ledger).encode(), b"the target test", b"", b"", b"", b"", b""), b""),
        (0, rendered(b"sh", b"", b"spec tp {{STEP}} {{SHARED}}  & \\1", b"", b"", b"", b"",
                     b"", b"tp", b"the target test", b"", b"", b"", b"", b""), b""),
        (0, rendered(b"sh", block("⟦replaces-case⟧".encode()), b"spec tp {{STEP}} {{SHARED}} tid & \\1", b"", b"",
                     b"\n\nrc", b"", b"", b"tp", b"tid", b"tid", b"", b"m", b"", b""), b""),
    ]

    code, out, err = run(build_verify_prompt.main, ["--step", "s", "--fast-cmd", "make unit && a/b", "diff",
                                                    str(spec), "0123abc", "4567def"])
    real_timed = f"{build_verify_prompt.HERE}/timed-test-run.sh".encode()
    assert (code, err, b"git diff 0123abc..HEAD" in out, b"git diff 4567def..HEAD" in out,
            b"       " + real_timed + b" fast '' make unit && a/b\n"
            b"       " + real_timed + b" affected '<the suites you ran>' make test TESTS=\"<those paths>\"\n"
            in out) == (0, b"", True, True, True)


def test_main_passes_a_non_utf8_byte_in_the_spec_and_in_the_step_value_through_to_stdout_unchanged(
        tmp_path, capsysbinary):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    module_path = scripts / "veri" / "build_verify_prompt.py"
    module_path.write_bytes((SCRIPTS / "veri" / "build_verify_prompt.py").read_bytes())
    loader = importlib.util.spec_from_file_location("bytes_build_verify_prompt", module_path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    (scripts / "prompts").mkdir()
    (scripts / "prompts" / "verify-red.md").write_bytes(b"{{STEP}}spec:{{ISSUE_SPEC}}\n")
    (scripts / "prompts" / "_shared.md").write_bytes(b"")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"spec \xff\xfe end\n")

    code = module.main(["--step", "step \udcff end", "red", str(spec), "tp"])

    assert (code, *capsysbinary.readouterr()) == (
        0,
        b"### The step under judgement\n\nstep \xff end\n\n"
        b"Your verdict is about this criterion only: the spec below is the whole issue, and its other\n"
        b"criteria belong to other steps of the plan.\n\n"
        b"spec:spec \xff\xfe end\n",
        b"",
    )


def test_main_renders_red_green_refactor_and_pin_prompts_carrying_the_test_path_the_blindness_contract_the_verdict_format_their_audits_and_the_foreground_and_git_stash_rules_reading_no_ambient_variable_and_refuses_an_extra_or_fifth_positional(
        tmp_path, capsysbinary, monkeypatch, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'slugify("Hello & World/Foo") must return "hello-world-foo" \xe2\x80\x94 see {ref}\\n done.\n')
    s, testpath = str(spec), "tests/test_slugify.py"
    prediction = 'the second assert fires: want "hello-world-foo", got "Hello & World/Foo"'
    calls = {
        "red": ["red", s, testpath, "test_slugify_lowercases"],
        "green": ["--fast-cmd", "make unit", "green", s, testpath, "test_slugify_lowercases"],
        "refactor": ["--fast-cmd", "make unit", "refactor", s, testpath, "0123abc"],
        "pin": ["pin", s, testpath, "test_slugify_lowercases"],
    }

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    monkeypatch.delenv("VERI_TEST_CMD", raising=False)
    monkeypatch.delenv("VERI_PREDICTED_FAILURE", raising=False)
    plain = {phase: run(argv) for phase, argv in calls.items()}
    monkeypatch.setenv("VERI_TEST_CMD", "pytest -k leaked_channel")
    monkeypatch.setenv("VERI_PREDICTED_FAILURE", prediction)
    ambient = {phase: run(argv) for phase, argv in calls.items()}
    fifth = {phase: run(argv + [prediction]) for phase, argv in calls.items()}
    bogus = run(["bogus", s, testpath])
    prompts = {phase: out.decode("utf-8", "surrogateescape") for phase, (_, out, _) in plain.items()}
    folded = {phase: " ".join(text.split("\n")) for phase, text in prompts.items()}

    def has(phase, pattern, flags=re.I):
        return re.search(pattern, folded[phase], flags) is not None

    every = ("red", "green", "refactor", "pin")
    assert {
        "exits": {phase: (code, err) for phase, (code, _, err) in plain.items()},
        "ambient reaches nothing": ambient == plain,
        "test path": all(testpath in prompts[p] for p in every),
        "verdict format": has("red", r"VERDICT:", 0) and has("red", "pass") and has("red", "reject"),
        "pin checks": "slugify(\"Hello & World/Foo\")" in prompts["pin"],
        "no prediction": all(prediction not in prompts[p] and not has(p, "PREDICTED_FAILURE|PREDICTION")
                             for p in every),
        "fifth positional": {phase: (code, out) for phase, (code, out, _) in fifth.items()},
        "unknown phase": bogus[0] != 0,
    } == {
        "exits": {p: (0, b"") for p in every},
        "ambient reaches nothing": True,
        "test path": True,
        "verdict format": True,
        "pin checks": True,
        "no prediction": True,
        "fifth positional": {p: (2, b"") for p in every},
        "unknown phase": True,
    }


def test_main_carries_and_checks_refactors_base_sha_scopes_every_prompt_to_its_step_ignoring_veri_step_and_renders_the_configuration_mechanism_fast_cmd_name_error_unrequired_code_restore_and_checkout_rules(
        tmp_path, capsysbinary, monkeypatch, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'slugify("Hello & World/Foo") must return "hello-world-foo" \xe2\x80\x94 see {ref}\\n done.\n')
    s, testpath, base_sha = str(spec), "tests/test_slugify.py", "3f9a1c07e2b4"
    step = "frobnicate --dry-run prints the plan and writes nothing ⟦criterion 3⟧"
    ambient_step = "frobnicate --dry-run prints the plan and writes nothing ⟦criterion 9⟧"
    fast_cmd = 'make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
    every = ("red", "green", "refactor", "pin")

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    def call(phase, step_args=()):
        fast = ["--fast-cmd", "make unit"] if phase in ("green", "refactor") else []
        slot4 = "0123abc" if phase == "refactor" else "test_slugify_lowercases"
        return [*step_args, *fast, phase, s, testpath, slot4]

    def has(out, pattern, flags=re.I):
        return re.search(pattern.encode(), out.replace(b"\n", b" "), flags) is not None

    monkeypatch.delenv("VERI_STEP", raising=False)
    prompts = {phase: run(call(phase))[1] for phase in every}
    with_base = run(["--fast-cmd", "make unit", "refactor", s, testpath, base_sha])
    refusals = {label: run(["--fast-cmd", "make unit", "refactor", s, testpath, *sha])[::2]
                for label, sha in (("missing", []), ("short", ["abc123"]), ("uppercase", ["3F9A1C07E2B4"]),
                                   ("with-text", ["3f9a1c07e2b4 because it tidies"]),
                                   ("too-long", ["3f9a1c07e2b43f9a1c07e2b43f9a1c07e2b43f9a1"]))}
    stepped = {phase: run(call(phase, ["--step", step])) for phase in every}
    monkeypatch.setenv("VERI_STEP", ambient_step)
    ambient = {phase: run(call(phase))[1] for phase in every}
    fast_green = run(["--fast-cmd", fast_cmd, "green", s, testpath, "test_slugify_lowercases"])
    no_fast = run(["green", s, testpath, "test_slugify_lowercases"])

    refactor = with_base[1]
    assert {
        "base sha carried": (with_base[0], base_sha.encode() in refactor),
        "base sha refusals": {label: (code, bool(err)) for label, (code, err) in refusals.items()},
        "diff range": f"git diff {base_sha}..HEAD".encode() in refactor,
        "step scoping": {phase: (code, step.encode() in out, has(
            out, r"verdict[^.]{0,160}(criterion|step)[^.]{0,40}only|verdict[^.]{0,160}only[^.]{0,40}(criterion|step)"))
            for phase, (code, out, _) in stepped.items()},
        "VERI_STEP reaches nothing": {phase: ambient[phase] == prompts[phase]
                                      and ambient_step.encode() not in ambient[phase] for phase in every},
        "fast-cmd": (fast_green[0], fast_cmd.encode() in fast_green[1], no_fast[0], bool(no_fast[2])),
    } == {
        "base sha carried": (0, True),
        "base sha refusals": {label: (2, True) for label in refusals},
        "diff range": True,
        "step scoping": {phase: (0, True, True) for phase in every},
        "VERI_STEP reaches nothing": {phase: True for phase in every},
        "fast-cmd": (0, True, 2, True),
    }


def test_main_scopes_refactor_to_the_cycles_files_with_flags_lines_checks_plan_refusals_and_criteria_rebase_transform_and_diff_rendering_test_adding_and_fast_cmd_rules(
        tmp_path, monkeypatch, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'slugify("Hello & World/Foo") must return "hello-world-foo" \xe2\x80\x94 see {ref}\\n done.\n')
    predicate = tmp_path / "predicate.md"
    predicate.write_bytes(b'grep -q "extract_helper" lib/foo.sh\n')
    s, testpath, base_sha = str(spec), "tests/test_slugify.py", "3f9a1c07e2b4"
    diff_step = "the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧"
    diff_fast = 'make unit ZORBLAT=diff -- --only "frob & nitz/quux"'

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    def diff(base, step_base, fast="make unit"):
        return run(["--step", diff_step, "--fast-cmd", fast, "diff", s, base, step_base])

    monkeypatch.delenv("VERI_STEP", raising=False)
    monkeypatch.delenv("VERI_RATIONALE", raising=False)
    with_base = run(["--fast-cmd", "make unit", "refactor", s, testpath, base_sha])[1]
    no_ledger = run(["plan", s])[:2]
    missing_ledger = run(["plan", s, str(tmp_path / "absent-ledger.md")])[:2]
    rb_onto, rb_pre = "8d05a4410c2e", "278252a1b9f3"
    rebase = run(["rebase", s, rb_onto, rb_pre])
    rebase_refusals = {label: run(["rebase", s, *shas])[:2] for label, shas in (
        ("short onto", ["abc123", rb_pre]), ("uppercase onto", ["8D05A4410C2E", rb_pre]),
        ("onto with text", [f"{rb_onto} because it merged", rb_pre]),
        ("short pre-rebase", [rb_onto, "abc123"]), ("uppercase pre-rebase", [rb_onto, "278252A1B9F3"]),
        ("pre-rebase with text", [rb_onto, f"{rb_pre} because it was green"]))}
    transform = run(["transform", s, str(predicate), "0123abcdef"])
    transform_bad_base = run(["transform", s, str(predicate), "tidied the helper"])[0]
    transforms = run(["transforms", s, str(predicate), "0123abcdef"])[0]
    dp = diff("0123abcdef", "0123abcdef")
    monkeypatch.setenv("VERI_STEP", "I tidied the helper because it was ugly")
    monkeypatch.setenv("VERI_RATIONALE", "the author meant well")
    dp_ambient = diff("0123abcdef", "0123abcdef")[1]
    monkeypatch.delenv("VERI_STEP")
    monkeypatch.delenv("VERI_RATIONALE")
    dp_other = diff("fedcba9876", "fedcba9876")[1]
    ds = diff("0123abcdef", "4567abcdef")
    df = diff("0123abcdef", "4567abcdef", diff_fast)
    fast_line = f"timed-test-run.sh fast '' {diff_fast}".encode()
    _, found, after_fast = df[1].partition(fast_line)
    assert {
        "refactor file scope": f"git diff --name-only {base_sha}^ {base_sha}".encode() in with_base,
        "plan ledger refusals": (no_ledger, missing_ledger),
        "rebase": (rebase[0], b'slugify("Hello & World/Foo")' in rebase[1], rb_onto.encode() in rebase[1],
                   rb_pre.encode() in rebase[1], b"{{" in rebase[1]),
        "rebase sha refusals": rebase_refusals,
        "transform": (transform[0], b'slugify("Hello & World/Foo")' in transform[1],
                      b"git diff 0123abcdef..HEAD" in transform[1],
                      transform_bad_base, transforms),
        "diff rendering": (dp[0], diff_step.encode() in dp[1], b"git diff 0123abcdef..HEAD" in dp[1]),
        "diff blind": (b"{{" in dp[1],
                       b"the target test" in dp[1], dp_ambient == dp[1],
                       dp_other.replace(b"fedcba9876", b"0123abcdef") == dp[1]),
        "diff step base": (ds[0], b"git diff 0123abcdef..HEAD" in ds[1]),
        "diff fast-cmd": (df[0], bool(found), b"affected '<the suites you ran>'" in after_fast),
    } == {
        "refactor file scope": True,
        "plan ledger refusals": ((2, b""), (2, b"")),
        "rebase": (0, True, True, True, False),
        "rebase sha refusals": {label: (2, b"") for label in rebase_refusals},
        "transform": (0, True, True, 2, 2),
        "diff rendering": (0, True, True),
        "diff blind": (False, False, True, True),
        "diff step base": (0, True),
        "diff fast-cmd": (0, True, True),
    }


@pytest.mark.tree_audit("the templates under prompts/")
def test_main_refuses_diff_without_fast_cmd_reads_the_refactor_plan_replaces_case_and_suite_repair_paragraphs_for_their_phase_alone_renders_the_comment_rules_byte_identical_unmarked_green_and_resolves_or_refuses_includes(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'slugify("Hello & World/Foo") must return "hello-world-foo" \xe2\x80\x94 see {ref}\\n done.\n')
    refactor_spec = tmp_path / "refactor-spec.md"
    refactor_spec.write_bytes(spec.read_bytes() + b"\n## Refactor\n\nRun kind: refactor. This issue changes structure, not behaviour.\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes("# Plan for #426\n\n- [ ] A verdict launcher script runs verify.sh with the step title"
                       " as an argument ⟦criterion 1⟧\n".encode())
    s, rs, testpath = str(spec), str(refactor_spec), "tests/test_slugify.py"
    replaces_step = '⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz" moves to tests/py/test_zorblat.py ⟦criterion 1⟧'
    repair_step = ("fix the full-suite failure: skills/tdd/scripts/tests/zorblat.test.sh — FAIL - zorblat frobs a nitz; "
                   "skills/tdd/scripts/tests/quux.test.sh — FAIL - quux & {nitz} round-trips ⟦suite-repair⟧")
    unmarked_step = 'tests/zorblat.test.sh: "zorblat frobs a nitz" replaces-case moves to tests/py ⟦added⟧ ⟦criterion 4⟧'
    green_args = ["--fast-cmd", "make unit", "green", s, testpath, "test_slugify_lowercases"]

    def run(main, argv):
        code = main(argv)
        return (code, *capsysbinary.readouterr())

    def has(out, pattern, flags=re.I):
        return re.search(pattern.encode(), out.replace(b"\n", b" "), flags) is not None

    def cksum(data):
        crc = 0
        tail, n = b"", len(data)
        while n:
            tail, n = tail + bytes([n & 0xFF]), n >> 8
        for byte in data + tail:
            crc ^= byte << 24
            for _ in range(8):
                crc = ((crc << 1) ^ 0x04C11DB7 if crc & 0x80000000 else crc << 1) & 0xFFFFFFFF
        return f"{~crc & 0xFFFFFFFF} {len(data)}"

    def green_sum(step_args):
        code, out, _ = run(build_verify_prompt.main, [*step_args, *green_args])
        body = out.rstrip(b"\n").replace(build_verify_prompt.HERE.encode(), b"@SCRIPTS@") + b"\n"
        return code, cksum(body)

    def unreadable_paragraph(name, paragraph, marked, unmarked):
        module, _ = scratch(tmp_path, name, drop=[paragraph])
        refused = run(module.main, marked)
        return (refused[0], refused[1], paragraph.encode() in refused[2],
                [run(module.main, argv)[0] for argv in unmarked])

    diff_no_fast = run(build_verify_prompt.main, ["--step", "s", "diff", s, "0123abcdef", "4567abcdef"])
    plan = run(build_verify_prompt.main, ["plan", s, str(ledger)])[1]
    rf_plan = run(build_verify_prompt.main, ["plan", rs, str(ledger)])
    green = run(build_verify_prompt.main, green_args)[1]
    refactor = run(build_verify_prompt.main, ["--fast-cmd", "make unit", "refactor", s, testpath, "0123abc"])[1]
    replaces_green = run(build_verify_prompt.main, ["--step", replaces_step, "--fast-cmd", "make unit", "green", s,
                                                    "tests/py/test_zorblat.py", "test_zorblat_frobs_a_nitz"])
    repair_green = run(build_verify_prompt.main, ["--step", repair_step, "--fast-cmd", "make unit", "green", s,
                                                  "skills/tdd/scripts/tests/zorblat.test.sh", "zorblat frobs a nitz"])
    one_refactoring = r"REJECT[^.]{0,200}(one|a single|named) refactoring|(one|a single|named) refactoring[^.]{0,200}REJECT"
    runnable = r"REJECT[^.]{0,200}(runnable|shell)[^.]{0,40}predicate|(runnable|shell)[^.]{0,40}predicate[^.]{0,200}REJECT"
    gone = r"(gone|deleted|removed|no longer)"
    every_suite = r"(every|each|all)( of the)? (listed|red|named) suites?"
    not_reject = r"\b(not|never)\b[^.]{0,40}REJECT"
    hazard = r"shell[^.]{0,40}hazard"
    included, _ = scratch(tmp_path, "included", templates={
        "verify-red.md": b"before {{INCLUDE:_probe-outer.md}} after\n",
        "_probe-outer.md": b"outer {{INCLUDE:_probe-inner.md}} end\n",
        "_probe-inner.md": b"inner judges {{TEST_PATH}}\n"})
    dangling, dangling_prompts = scratch(tmp_path, "dangling", templates={
        "verify-red.md": b"before {{INCLUDE:_probe-absent.md}} after\n"})
    cycle, _ = scratch(tmp_path, "cycle", templates={
        "verify-red.md": b"before {{INCLUDE:_probe-cycle-a.md}} after\n",
        "_probe-cycle-a.md": b"a {{INCLUDE:_probe-cycle-b.md}}\n",
        "_probe-cycle-b.md": b"b {{INCLUDE:_probe-cycle-a.md}}\n"})
    red_args = ["red", s, testpath, "test_slugify_lowercases"]
    dangling_run = run(dangling.main, red_args)
    cycle_run = run(cycle.main, red_args)

    assert {
        "diff without fast-cmd": (diff_no_fast[0], diff_no_fast[1], diff_no_fast[2] != b""),
        "refactor plan": (rf_plan[0], has(rf_plan[1], one_refactoring), has(rf_plan[1], runnable),
                          has(plan, one_refactoring), has(plan, runnable)),
        "refactor plan unreadable": unreadable_paragraph(
            "no-refactor-plan", "_verify-plan-refactor.md", ["plan", rs, str(ledger)],
            [["red", rs, testpath, "test_slugify_lowercases"]]),
        "#679 no-op": has(rf_plan[1], r"REJECT[^.]{0,200}no-op[^.]{0,200}later step|no-op[^.]{0,200}later step[^.]{0,200}REJECT"),
        "rationale comment": {phase: [has(out, r"REJECT[^.]{0,200}rationale comment|rationale comment[^.]{0,200}REJECT"),
                                      has(out, r"contract header"), has(out, hazard)]
                              for phase, out in (("green", green), ("refactor", refactor))},
        "contract header not grounds": {
            phase: [has(out, rf"contract header[^.]{{0,200}}{not_reject}|{not_reject}[^.]{{0,200}}contract header"),
                    has(out, rf"{hazard}[^.]{{0,200}}{not_reject}|{not_reject}[^.]{{0,200}}{hazard}")]
            for phase, out in (("green", green), ("refactor", refactor))},
        "replaces-case": (replaces_green[0],
                          has(replaces_green[1], r"PASS[^.]{0,250}pytest[^.]{0,120}same behaviou?r"),
                          has(replaces_green[1], rf"PASS[^.]{{0,250}}named (bash )?case[^.]{{0,60}}{gone}"),
                          has(replaces_green[1], r"REJECT[^.]{0,200}(delet|modif)[^.]{0,80}(any|every) other (bash )?case"
                                                 r"|(delet|modif)[^.]{0,80}(any|every) other (bash )?case[^.]{0,200}REJECT"),
                          has(green, r"PASS[^.]{0,250}pytest")),
        "suite-repair": (repair_green[0],
                         has(repair_green[1], rf"PASS[^.]{{0,250}}{every_suite}[^.]{{0,80}}green"),
                         has(repair_green[1], r"run[^.]{0,120}full test command|full test command[^.]{0,120}(run|judge)"),
                         has(repair_green[1], r"(not|rather than|instead of)[^.]{0,60}fast (test )?command"),
                         has(green, r"run[^.]{0,120}full test command")),
        "replaces-case unreadable": unreadable_paragraph(
            "no-replaces-case", "_verify-green-replaces-case.md",
            ["--step", replaces_step, "--fast-cmd", "make unit", "green", s, "tests/py/test_zorblat.py",
             "test_zorblat_frobs_a_nitz"],
            [green_args]),
        "suite-repair unreadable": unreadable_paragraph(
            "no-suite-repair", "_verify-green-suite-repair.md",
            ["--step", repair_step, "--fast-cmd", "make unit", "green", s, "skills/tdd/scripts/tests/zorblat.test.sh",
             "zorblat frobs a nitz"],
            [green_args, ["--step", repair_step, "red", s, "skills/tdd/scripts/tests/zorblat.test.sh",
                          "zorblat frobs a nitz"]]),
        "#671 byte-identity": [green_sum(["--step", unmarked_step]), green_sum([])],
        "#703 include": run(included.main, red_args),
        "#703 missing partial": (dangling_run[0], dangling_run[1],
                                 str(dangling_prompts / "_probe-absent.md").encode() in dangling_run[2]),
        "#703 self-including partial": (cycle_run[0], cycle_run[1], b"_probe-cycle-a.md" in cycle_run[2]),
    } == {
        "diff without fast-cmd": (2, b"", True),
        "refactor plan": (0, True, True, False, False),
        "refactor plan unreadable": (2, b"", True, [0]),
        "#679 no-op": True,
        "rationale comment": {"green": [True] * 3, "refactor": [True] * 3},
        "contract header not grounds": {"green": [True] * 2, "refactor": [True] * 2},
        "replaces-case": (0, True, True, True, False),
        "suite-repair": (0, True, True, True, False),
        "replaces-case unreadable": (2, b"", True, [0]),
        "suite-repair unreadable": (2, b"", True, [0, 0]),
        "#671 byte-identity": [(0, "1933796141 8186"), (0, "605695461 7910")],
        "#703 include": (0, f"before outer inner judges {testpath} end after\n".encode(), b""),
        "#703 missing partial": (2, b"", True),
        "#703 self-including partial": (2, b"", True),
    }


@pytest.mark.tree_audit("the templates under prompts/")
def test_main_states_the_signal_only_processes_you_started_rule_in_every_phase_from_one_partial_the_develop_prompts_include_too_1223(
        tmp_path, capsysbinary, monkeypatch, build_verify_prompt):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec, ledger = tmp_path / "spec.md", tmp_path / "ledger.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    ledger.write_bytes("# Plan for #1223\n\n- [ ] zorblat frobs a nitz ⟦criterion 1⟧\n".encode())
    s, sha, fast = str(spec), "0123abc", ["--fast-cmd", "make unit"]
    argvs = {
        "red": ["red", s, "tests/zorblat.test.sh", "zorblat frobs a nitz"],
        "green": [*fast, "green", s, "tests/zorblat.test.sh", "zorblat frobs a nitz"],
        "refactor": [*fast, "refactor", s, "tests/zorblat.test.sh", sha],
        "pin": ["pin", s, "tests/zorblat.test.sh", "zorblat frobs a nitz"],
        "plan": ["plan", s, str(ledger)],
        "rebase": ["rebase", s, sha, "4567def"],
        "transform": ["transform", s, str(tmp_path / "predicate.md"), sha],
        "diff": ["--step", "zorblat frobs a nitz", *fast, "diff", s, sha, "4567def"],
    }

    def flat(data):
        return re.sub(rb"\s+", b" ", data).strip()

    def rendered(main, argv):
        code = main(argv)
        out, _ = capsysbinary.readouterr()
        return code, flat(out)

    spelled = sorted(p.name for p in (SCRIPTS / "prompts").glob("_*.md") if b"`pkill`" in p.read_bytes())
    partial = (spelled[0] if len(spelled) == 1 and spelled[0].startswith("_")
               and spelled[0] not in ("_shared.md", "_develop-shared.md") else None)
    rule = flat((SCRIPTS / "prompts" / partial).read_bytes()) if partial else None
    prompts = {phase: rendered(build_verify_prompt.main, argv) for phase, argv in argvs.items()}
    prompts["develop red"] = rendered(build_develop_prompt.main, ["red", s, "zorblat frobs a nitz", "make test"])

    assert {
        "spelled in one partial of its own": partial is not None,
        "carried": {phase: (code, rule is not None and rule in out) for phase, (code, out) in prompts.items()},
    } == {
        "spelled in one partial of its own": True,
        "carried": dict.fromkeys(prompts, (0, True)),
    }


def test_main_passes_a_replaces_case_green_only_when_every_case_its_step_names_is_gone_and_has_a_pytest_case_and_rejects_touching_any_case_it_does_not_name_one_or_several(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    several = ('⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz", "zorblat quuxes a frob", '
               '"zorblat refuses an empty nitz" move to tests/py/test_zorblat.py ⟦criterion 1⟧')
    one = ('⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz" moves to '
           'tests/py/test_zorblat.py ⟦criterion 1⟧')

    def rendered(step):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", "green", str(spec),
                                         "tests/py/test_zorblat.py", "test_zorblat_frobs_a_nitz"])
        out, _ = capsysbinary.readouterr()
        return re.sub(rb"\s+", b" ", out) if code == 0 else None

    prompts = {"several": rendered(several), "one": rendered(one)}

    def says(prompt, pattern):
        return prompt is not None and re.search(pattern, prompt, re.I) is not None

    rules = {
        "passes only when every named case is gone from its suite": (
            rb"PASS[^.]{0,250}(every|each|all)[^.]{0,30}(named|cases? (it|the step|its text) names)[^.]{0,60}"
            rb"(gone|deleted|removed|no longer)"),
        "and each has a pytest case asserting its behaviour": (
            rb"(each|every)[^.]{0,80}pytest case[^.]{0,40}assert[^.]{0,30}(its|their) behaviou?r"),
        "rejects deleting or modifying any case the step does not name": (
            rb"REJECT[^.]{0,200}(delet|modif)[^.]{0,80}(any|a) case (it|the step|its text) does not name"),
    }
    one_only = rb"^(?!.*(names one bash case|the named case is gone))"

    assert {key: [rule for rule, pattern in rules.items() if not says(prompt, pattern)]
            + (["never confines a several-case step to one case"]
               if key == "several" and not says(prompt, one_only) else [])
            for key, prompt in prompts.items()} == dict.fromkeys(prompts, [])


def test_main_renders_a_ci_repair_green_prompt_judged_by_ci_evidence_and_not_by_the_revert_goes_red_check_and_an_unmarked_green_prompt_carries_no_such_paragraph_1473(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')

    def rendered(step):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", "green", str(spec),
                                         "tests/py/test_zorblat.py", "test_zorblat_frobs_a_nitz"])
        out, _ = capsysbinary.readouterr()
        assert code == 0
        return re.sub(rb"\s+", b" ", out)

    marked = rendered("zorblat sorts on CI only ⟦ci-repair⟧ ⟦criterion 1⟧")
    unmarked = rendered("zorblat sorts ⟦criterion 1⟧")

    rules = {
        "evidence is the failing CI job's log before the fix": (
            rb"CI job'?s? log[^.]{0,80}before the fix|before the fix[^.]{0,80}CI job'?s? log"),
        "and a green CI run on the pushed fix": rb"green CI run[^.]{0,40}(pushed )?fix",
        "not judged by the local revert-goes-red check": (
            rb"not judged by[^.]{0,120}(local|revert|goes red|removed)"),
    }

    def says(prompt, pattern):
        return re.search(pattern, prompt, re.I) is not None

    assert ([rule for rule, pattern in rules.items() if not says(marked, pattern)],
            [rule for rule, pattern in rules.items() if says(unmarked, pattern)]) == ([], list(rules)[:0])


def test_main_renders_the_fixture_repair_paragraph_in_the_green_prompt_of_a_marked_step_only_rejecting_a_named_path_or_hunk_and_passing_only_when_confined_1021(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"The awake-clock stub must not leak wall time.\n")
    marked = ("the case passes under load: repairs the fixture 'awake-clock' in tests/zorblat.test.sh, "
              "reproduced by a case in tests/zorblat.test.sh ⟦fixture-repair⟧ ⟦criterion 1⟧")
    unmarked = "the case passes under load ⟦criterion 1⟧"

    def rendered(step, phase, third):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", phase, str(spec),
                                         "tests/zorblat.test.sh", third])
        out, _ = capsysbinary.readouterr()
        assert code == 0
        return re.sub(rb"\s+", b" ", out)

    base = "a" * 40
    prompts = {"marked green": rendered(marked, "green", "case"), "unmarked green": rendered(unmarked, "green", "case"),
               "marked red": rendered(marked, "red", "case"), "marked refactor": rendered(marked, "refactor", base)}
    reject = rb"REJECT, naming the path or hunk, any change outside the target test's file, the named fixture file"
    passes = rb"PASS only when the target case passes with every change confined to those"

    assert {key: (re.search(reject, prompt) is not None, re.search(passes, prompt) is not None)
            for key, prompt in prompts.items()} == {
        "marked green": (True, True), "unmarked green": (False, False),
        "marked red": (False, False), "marked refactor": (False, False)}


def test_main_gives_a_green_prompt_the_replaces_case_paragraph_only_to_a_step_whose_trailing_marks_include_the_mark_not_one_that_mentions_it_in_prose_or_backticks_1538(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')

    def rendered(step):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", "green", str(spec),
                                         "tests/py/test_zorblat.py", "test_zorblat_frobs_a_nitz"])
        out, _ = capsysbinary.readouterr()
        assert code == 0
        return re.sub(rb"\s+", b" ", out)

    paragraph = (rb"REJECT[^.]{0,200}(delet|modif)[^.]{0,80}(any|a) case (it|the step|its text) does not name")
    mention = "zorblat reads the ⟦replaces-case⟧ mark, quoted as `⟦replaces-case⟧` in prose"
    marked = rendered(f"{mention} ⟦replaces-case⟧ ⟦criterion 1⟧")
    mentioned = rendered(f"{mention} ⟦criterion 1⟧")

    assert ([re.search(paragraph, marked, re.I) is not None, re.search(paragraph, mentioned, re.I) is not None]
            == [True, False])


def _green_paragraph_by_trailing_marker(tmp_path, capsysbinary, build_verify_prompt, mark, paragraph):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')

    def rendered(step):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", "green", str(spec),
                                         "tests/py/test_zorblat.py", "test_zorblat_frobs_a_nitz"])
        out, _ = capsysbinary.readouterr()
        assert code == 0
        return re.sub(rb"\s+", b" ", out)

    mention = f"zorblat reads the ⟦{mark}⟧ mark mid-sentence"
    return [re.search(paragraph, rendered(f"{mention} ⟦criterion 1⟧")) is not None,
            re.search(paragraph, rendered(f"{mention} ⟦{mark}⟧ ⟦criterion 1⟧")) is not None]


def test_main_renders_no_suite_repair_green_paragraph_for_a_step_naming_the_mark_mid_sentence_without_ending_in_it_1919(
        tmp_path, capsysbinary, build_verify_prompt):
    assert _green_paragraph_by_trailing_marker(
        tmp_path, capsysbinary, build_verify_prompt, "suite-repair", rb"This step repairs the full run") == [False, True]


def test_main_renders_no_ci_repair_green_paragraph_for_a_step_naming_the_mark_mid_sentence_without_ending_in_it_1919(
        tmp_path, capsysbinary, build_verify_prompt):
    assert _green_paragraph_by_trailing_marker(
        tmp_path, capsysbinary, build_verify_prompt, "ci-repair", rb"repairs a failure that reproduces only on CI") == [False, True]


def test_main_renders_a_ci_repair_green_prompt_that_passes_on_evidence_from_before_the_push_and_leaves_the_verdict_on_the_pushed_fix_to_wait_ci_1473(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    code = build_verify_prompt.main(["--step", "zorblat sorts on CI only ⟦ci-repair⟧ ⟦criterion 1⟧",
                                     "--fast-cmd", "make unit", "green", str(spec),
                                     "tests/py/test_zorblat.py", "test_zorblat_frobs_a_nitz"])
    out, _ = capsysbinary.readouterr()
    prompt = re.sub(rb"\s+", b" ", out)
    assert code == 0

    rules = {
        "passes on the quoted CI failure, a diff touching what it names and the local suites green": (
            rb"PASS[^.]{0,200}(quote|log)[^.]{0,200}diff[^.]{0,120}touch[^.]{0,200}(local|suites?)[^.]{0,60}green"),
        "never requires a CI run on the fix": (
            rb"(never|not|no)[^.]{0,40}(require|need|expect|wait)[^.]{0,40}(CI run|run on the fix|green run)"),
        "because none exists before the push": rb"(before|until|after)[^.]{0,40}(push|PASS)[^.]{0,120}(CI run|exists?)",
        "the CI verdict on the pushed fix is wait-ci.sh's, red bailing ci-red": (
            rb"wait-ci\.sh[^.]{0,200}ci-red|ci-red[^.]{0,200}wait-ci\.sh"),
        "does not reject a step whose latest CI run is still the red one": (
            rb"^(?!.*run still red is a REJECT)"),
    }

    assert [rule for rule, pattern in rules.items() if re.search(pattern, prompt, re.I) is None] == []


def test_main_renders_an_expand_and_a_migrate_verify_prompt_stating_what_each_phase_changes_and_that_test_files_stay_frozen(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"zorblat(nitz) replaces frob(nitz, quux).\n")
    step = ("Interface change: frob(nitz, quux) becomes zorblat(nitz) "
            "⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧")

    def rendered(phase):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", phase, str(spec),
                                         "tests/py/test_zorblat.py", "0123abc"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(rb"\s+", b" ", out)

    frozen = (rb"(test files?[^.]{0,40}(stay|stays|remain|remains|are|is|left) frozen"
              rb"|(never|not|no)[^.]{0,30}(touch|modify|edit)[^.]{0,20}(a |any )?test file)")
    rules = {
        "expand": {
            "production gains the new interface": rb"(add|gains?|introduce)[^.]{0,60}the new interface",
            "the old interface becomes a proxy": rb"old (one|interface)[^.]{0,60}(becomes?|turns? into|as) a proxy",
            "test files stay frozen": frozen,
        },
        "migrate": {
            "callers move to the new interface": rb"callers?[^.]{0,60}(move|moved|migrate)[^.]{0,30}the new interface",
            "test files stay frozen": frozen,
        },
    }

    results = {}
    for phase, phase_rules in rules.items():
        code, prompt = rendered(phase)
        results[phase] = (code, [rule for rule, pattern in phase_rules.items()
                                 if re.search(pattern, prompt, re.I) is None])

    assert results == {"expand": (0, []), "migrate": (0, [])}


def test_main_refuses_an_expand_or_a_migrate_call_without_fast_cmd_with_exit_2_and_its_message_then_the_usage_line(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    results = {}
    for phase in ("expand", "migrate"):
        code = build_verify_prompt.main([phase, str(spec), "t", "0123abc"])
        results[phase] = (code, *capsysbinary.readouterr())

    assert results == {
        phase: (2, b"", f"build-verify-prompt: {phase} needs --fast-cmd '<fast-tier test command>'\n".encode() + USAGE)
        for phase in ("expand", "migrate")}


def test_main_renders_a_contract_a_and_a_contract_b_verify_prompt_stating_production_frozen_then_the_proxy_deleted_and_test_files_frozen(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"zorblat(nitz) replaces frob(nitz, quux).\n")
    step = ("Interface change: frob(nitz, quux) becomes zorblat(nitz) "
            "⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧")

    def rendered(phase):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", phase, str(spec),
                                         "tests/py/test_zorblat.py", "0123abc"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(rb"\s+", b" ", out)

    def frozen(what):
        return (rb"(" + what + rb"[^.]{0,40}(stay|stays|remain|remains|are|is|left) frozen"
                rb"|(never|not|no)[^.]{0,30}(touch|modify|edit)[^.]{0,20}(a |any )?" + what + rb")")

    rules = {
        "contract-a": {
            "production stays frozen": frozen(rb"production( files?| code)?"),
        },
        "contract-b": {
            "the proxy is deleted": rb"(proxy[^.]{0,60}(is |are )?(deleted|removed)|(delete|remove)s?[^.]{0,40}proxy)",
            "test files stay frozen": frozen(rb"test files?"),
        },
    }

    results = {}
    for phase, phase_rules in rules.items():
        code, prompt = rendered(phase)
        results[phase] = (code, [rule for rule, pattern in phase_rules.items()
                                 if re.search(pattern, prompt, re.I) is None])

    assert results == {"contract-a": (0, []), "contract-b": (0, [])}


def test_main_admits_an_expand_migrate_contract_a_or_contract_b_base_sha_only_as_7_to_40_lowercase_hex_and_refuses_any_other_with_exit_2_as_refactor_does(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    s = str(spec)
    phases = ("refactor", "expand", "migrate", "contract-a", "contract-b")

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    def bad_sha(phase, value):
        return (2, b"", b"build-verify-prompt: " + phase.encode() + b" needs <base-sha>"
                b" as 7-40 lowercase hex characters, got '" + value + b"'\n" + USAGE)

    refused = {(phase, value): run(["--fast-cmd", "m", phase, s, "t", *([value.decode()] if value else [])])
               for phase in phases for value in (b"0123ABC", b"012345", b"0123abc\n", b"")}
    assert refused == {(phase, value): bad_sha(phase, value)
                       for phase in phases for value in (b"0123ABC", b"012345", b"0123abc\n", b"")}

    admitted = {phase: run(["--fast-cmd", "m", phase, s, "t", "0123456789abcdef0123456789abcdef01234567"])[::2]
                for phase in phases}
    assert admitted == dict.fromkeys(phases, (0, b""))


def test_main_of_both_prompt_builders_refuses_an_unknown_phase_with_exit_2_naming_expand_migrate_contract_a_and_contract_b_among_the_phases_it_accepts(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    builders = {"build-develop-prompt": (importlib.import_module("veri.build_develop_prompt"),
                                         ["bogus", str(spec), "step", "make test"]),
                "build-verify-prompt": (build_verify_prompt, ["bogus", str(spec), "t"])}

    def answer(module, argv):
        code = module.main(argv)
        _, err = capsysbinary.readouterr()
        accepted = re.search(rb"unknown phase 'bogus' \(want ([^)]*)\)", err)
        named = accepted.group(1).split(b"|") if accepted else []
        return code, [phase for phase in ("expand", "migrate", "contract-a", "contract-b")
                      if phase.encode() not in named]

    assert {name: answer(*call) for name, call in builders.items()} == {
        "build-develop-prompt": (2, []), "build-verify-prompt": (2, [])}


def test_main_renders_a_check_that_every_case_the_step_asks_for_exists_and_passes_only_in_the_last_listed_phase_1495(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"zorblat(nitz) replaces frob(nitz, quux), with a case refusing a sibling start.\n")
    step = ("Interface change: frob(nitz, quux) becomes zorblat(nitz) "
            "⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧")

    def rendered(phase):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", phase, str(spec),
                                         "tests/py/test_zorblat.py", "0123abc"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(r"\s+", " ", out.decode("utf-8", "surrogateescape"))

    check = (r"(?m)(^|\s)\d+\. [^.]{0,200}(case|test)[^.]{0,200}(exists?|present)[^.]{0,60}HEAD"
             r"[^.]{0,200}pass[^.]{0,200}\.[^.]{0,200}REJECT[^.]{0,100}(missing|absent)")
    carries = {phase: (lambda result: (result[0], re.search(check, result[1], re.I) is not None))(rendered(phase))
               for phase in ("expand", "contract-a")}

    assert carries == {"expand": (0, False), "contract-a": (0, True)}


def test_main_renders_no_every_case_exists_check_in_the_expand_or_migrate_prompt_of_a_step_listing_expand_migrate_contract_a_1495(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"zorblat(nitz) replaces frob(nitz, quux), with a case refusing a sibling start.\n")
    step = ("Interface change: frob(nitz, quux) becomes zorblat(nitz) "
            "⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧")

    def rendered(phase):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", phase, str(spec),
                                         "tests/py/test_zorblat.py", "0123abc"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(r"\s+", " ", out.decode("utf-8", "surrogateescape"))

    carries = {phase: (lambda result: (result[0], "Every case the step asks for exists" in result[1]))(rendered(phase))
               for phase in ("expand", "migrate")}

    assert carries == {"expand": (0, False), "migrate": (0, False)}


def test_main_renders_a_red_prompt_for_a_replaces_case_step_saying_one_replacement_case_per_named_case_judged_each_and_not_one_new_failing_test_while_one_without_the_mark_still_says_it_1537(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    marked = ('⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz", "zorblat quuxes a frob" '
              'move to tests/py/test_zorblat.py ⟦criterion 1⟧')
    plain = "zorblat frobs a nitz ⟦criterion 1⟧"

    def rendered(step):
        code = build_verify_prompt.main(["--step", step, "red", str(spec), "tests/py/test_zorblat.py", "test_zorblat"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(r"\s+", " ", out.decode("utf-8", "surrogateescape"))

    one_failing = "**one new failing test**"
    per_case = r"one replacement (test )?case per named case"
    code, prompt = rendered(marked)
    marked_result = (code, one_failing in prompt, re.search(per_case, prompt, re.I) is not None,
                     re.search(r"judge each", prompt, re.I) is not None)
    code, prompt = rendered(plain)
    plain_result = (code, one_failing in prompt, re.search(per_case, prompt, re.I) is not None)

    assert (marked_result, plain_result) == ((0, False, True, True), (0, True, False))


def test_main_renders_the_per_case_red_prompt_for_a_step_whose_text_ends_with_the_replaces_case_mark_not_at_its_start_1882(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    step = "tests/zorblat.test.sh: 'zorblat frobs a nitz' moves to tests/py/test_zorblat.py ⟦replaces-case⟧"

    code = build_verify_prompt.main(["--step", step, "red", str(spec), "tests/py/test_zorblat.py", "test_zorblat"])
    out, _ = capsysbinary.readouterr()
    prompt = re.sub(r"\s+", " ", out.decode("utf-8", "surrogateescape"))

    assert (code, "judge each of them" in prompt) == (0, True)


SPEC_TEXT = 'slugify("Hello & World/Foo") must return "hello-world-foo" — see {ref}\\n done.\n'
TESTPATH = "tests/test_slugify.py"


def test_carries_issue_spec_verbatim(tmp_path, run_cli, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(SPEC_TEXT.encode())

    code, out, _ = run_cli(build_verify_prompt, ["red", str(spec), TESTPATH, "test_slugify_lowercases"])

    assert (code, 'slugify("Hello & World/Foo")' in out) == (0, True)


def test_unknown_phase_exits_non_zero(tmp_path, run_cli, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(SPEC_TEXT.encode())

    code, out, _ = run_cli(build_verify_prompt, ["bogus", str(spec), TESTPATH])

    assert (code, out) == (2, "")


def folded_bytes(text):
    return text.replace("\n", " ").encode("utf-8", "surrogateescape")


@pytest.fixture
def spec(tmp_path):
    path = tmp_path / "spec.md"
    path.write_bytes(SPEC_TEXT.encode())
    return str(path)


def test_verify_plan_carries_the_issue_spec_and_the_ledger_named_as_its_third_argument(
        tmp_path, spec, run_cli, build_verify_prompt):
    ledger = tmp_path / "ledger.md"
    ledger.write_text("# Plan for #426\n\n- [ ] A verdict launcher script runs verify.sh with the step title as an "
                      "argument ⟦criterion 1⟧\n")

    code, out, _ = run_cli(build_verify_prompt, ["plan", spec, str(ledger)])

    assert code == 0
    assert 'slugify("Hello & World/Foo")' in out
    assert "A verdict launcher script runs verify.sh with the step title as an argument ⟦criterion 1⟧" in out


def test_verify_plan_carries_only_the_issue_spec_and_the_ledger_and_no_cycle_phase_prompt_carries_a_ledger(
        tmp_path, spec, run_cli, build_verify_prompt):
    ledger = tmp_path / "rationale-ledger.md"
    ledger.write_text("# Plan for #439\n\n- [ ] LEDGER-BODY-MARKER a plan step no cycle verifier may be shown "
                      "⟦criterion 1⟧\n")
    leak_step = "RATIONALE-LEAK the developer chose a launcher script because bash -c broke the quoting"
    problems = []

    code, plan_only, _ = run_cli(build_verify_prompt, ["--step", leak_step, "plan", spec, str(ledger),
                                                        "test_rationale_leak"])
    if code != 0:
        problems.append(f"the plan call exited {code}")
    if 'slugify("Hello & World/Foo")' not in plan_only:
        problems.append("the plan prompt drops the issue spec")
    if "LEDGER-BODY-MARKER" not in plan_only:
        problems.append("the plan prompt drops the ledger")
    if "RATIONALE-LEAK" in plan_only:
        problems.append("the plan prompt carries the --step text")
    if "test_rationale_leak" in plan_only:
        problems.append("the plan prompt carries the fourth positional")
    for phase in ("red", "green", "refactor", "pin"):
        fast = ["--fast-cmd", "make unit"] if phase in ("green", "refactor") else []
        slot = "0123abc" if phase == "refactor" else "test_slugify_lowercases"
        _, cycle, _ = run_cli(build_verify_prompt, [*fast, phase, spec, str(ledger), slot])
        if str(ledger) not in cycle:
            problems.append(f"verify-{phase} drops the path it was given")
        if "LEDGER-BODY-MARKER" in cycle:
            problems.append(f"verify-{phase} carries the ledger's text")

    assert problems == []


def test_verify_red_requires_a_bugs_observed_failure_to_match_what_happened_and_nothing_of_the_kind_without_a_bug_section(
        tmp_path, spec, run_cli, build_verify_prompt):
    bug_spec = tmp_path / "bug-spec.md"
    bug_spec.write_bytes(SPEC_TEXT.encode() + (
        '\n## Bug\n\n### What happened\n\nslugify returned "HELLO_WORLD" on the ampersanded seed.\n\n'
        '### Expected\n\nslugify returns "hello-world-foo".\n\n### Steps to reproduce\n\n'
        'Call slugify("Hello & World/Foo").\n\n### Environment\n\nveri on bash 5.2, macOS 15.\n').encode())
    observed_matches_reported = (rb"(match|matches|matching|same as)[^.]{0,80}what happened"
                                 rb"|what happened[^.]{0,80}(match|matches|matching|same as)")
    problems = []

    code, bug_red, _ = run_cli(build_verify_prompt, ["red", str(bug_spec), TESTPATH, "test_slugify_lowercases"])
    _, red, _ = run_cli(build_verify_prompt, ["red", spec, TESTPATH, "test_slugify_lowercases"])
    if code != 0:
        problems.append(f"with a bug spec and red's own four positionals exited {code}, want 0")
    if 'slugify returned "HELLO_WORLD" on the ampersanded seed.' not in bug_red:
        problems.append("does not carry the bug report from the spec")
    if not re.search(observed_matches_reported, folded_bytes(bug_red), re.I):
        problems.append("never requires the failure it observes to match What happened")
    if re.search(observed_matches_reported, folded_bytes(red), re.I):
        problems.append("a spec with no Bug section still requires the failure to match What happened")

    assert problems == []


DIFF_STEP = "the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧"
DIFF_BASE = "0123abcdef"
STEP_BASE = "4567abcdef"


def hex_message(label, value):
    return f"build-verify-prompt: diff needs {label} as 7-40 lowercase hex characters, got '{value}'"


def diff_refusal_problems(run_cli, module, label, want, argv):
    code, out, err = run_cli(module, argv)
    first = err.split("\n")[0]
    problems = []
    if code != 2:
        problems.append(f"{label} exited {code}, want 2")
    if out != "":
        problems.append(f"{label} printed {len(out.encode('utf-8', 'surrogateescape'))} bytes, want none")
    if first != want:
        problems.append(f"{label}'s first stderr line is '{first}', want '{want}'")
    return problems


def test_995_diff_with_fast_cmd_refuses_a_non_hex_base_a_missing_step_and_a_bad_step_base_each_with_exit_2_and_its_own_message(
        tmp_path, spec, run_cli, build_verify_prompt):
    fc = ["--fast-cmd", "make unit"]
    step = ["--step", DIFF_STEP]
    problems = []
    for label, want, argv in (
            ("diff with a non-hex base", hex_message("<base-sha>", "tidied the helper"),
             [*step, *fc, "diff", spec, "tidied the helper", DIFF_BASE]),
            ("diff with no --step", "build-verify-prompt: diff needs --step '<STEP>'",
             [*fc, "diff", spec, DIFF_BASE, DIFF_BASE]),
            ("diff with no step base", hex_message("<step-base-sha>", ""),
             [*step, *fc, "diff", spec, DIFF_BASE]),
            ("diff with a non-hex step base", hex_message("<step-base-sha>", "tidied the helper"),
             [*step, *fc, "diff", spec, DIFF_BASE, "tidied the helper"]),
            ("diff with an uppercase step base", hex_message("<step-base-sha>", "4567ABCDEF"),
             [*step, *fc, "diff", spec, DIFF_BASE, "4567ABCDEF"]),
            ("diff with a 6-character step base", hex_message("<step-base-sha>", "4567ab"),
             [*step, *fc, "diff", spec, DIFF_BASE, "4567ab"])):
        problems += diff_refusal_problems(run_cli, build_verify_prompt, label, want, argv)

    assert problems == []


def test_1041_diff_with_fast_cmd_refuses_an_extra_positional_argument_with_exit_2_and_the_extra_argument_message(
        tmp_path, spec, run_cli, build_verify_prompt):

    problems = diff_refusal_problems(
        run_cli, build_verify_prompt, "diff with an extra positional", "build-verify-prompt: too many arguments",
        ["--step", DIFF_STEP, "--fast-cmd", "make unit", "diff", spec, DIFF_BASE, DIFF_BASE, "extra"])

    assert problems == []


def test_a_diff_prompt_tells_the_verifier_the_wrapper_hands_the_test_commands_exit_status_straight_back(
        tmp_path, spec, run_cli, build_verify_prompt):
    problems = []

    code, prompt, _ = run_cli(build_verify_prompt, ["--step", DIFF_STEP, "--fast-cmd", "make unit", "diff", spec,
                                                    DIFF_BASE, STEP_BASE])
    if code != 0:
        problems.append(f"exited {code}, want 0")
    if ("The wrapper hands the command's own exit status straight back, so a red run stays red."
            not in prompt.replace("\n", " ")):
        problems.append("never says the wrapper hands the exit status straight back")

    assert problems == []


def test_main_renders_the_ordinary_red_prompt_for_a_step_mentioning_the_replaces_case_mark_only_in_its_prose_or_backticks_1538(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    prose = "the guard reads ⟦replaces-case⟧ only among trailing marks: replaces 'zorblat frobs a nitz' in tests/zorblat.test.sh ⟦criterion 1⟧"
    ticks = "a step that only quotes `⟦replaces-case⟧` as text ⟦criterion 1⟧"

    def rendered(step):
        code = build_verify_prompt.main(["--step", step, "red", str(spec), "tests/py/test_zorblat.py", "test_zorblat"])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(r"\s+", " ", out.decode("utf-8", "surrogateescape"))

    results = []
    for step in (prose, ticks):
        code, prompt = rendered(step)
        results.append((code, "**one new failing test**" in prompt,
                        re.search(r"one replacement (test )?case per named case", prompt, re.I) is not None))

    assert results == [(0, True, False)] * 2


def refactor_and_plain_plan_renders(tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n\n## Refactor\n\nRun kind: refactor.\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes("# Plan for #1527\n\n- [ ] Extract Function ⟦criterion 1⟧\n".encode())

    plain_spec = tmp_path / "plain-spec.md"
    plain_spec.write_bytes(b"# spec\n\nbehaviour\n")

    def render(spec_path):
        code = build_verify_prompt.main(["plan", str(spec_path), str(ledger)])
        return code, capsysbinary.readouterr()[0].replace(b"\n", b" ")

    return render(spec), render(plain_spec)


@pytest.mark.tree_audit("the templates under prompts/")
def test_main_tells_the_refactor_plan_verifier_to_reject_a_phases_step_1527(tmp_path, capsysbinary, build_verify_prompt):
    phases = (r"REJECT[^.]{0,200}refactor[^.]{0,200}⟦phases|refactor[^.]{0,200}⟦phases[^.]{0,200}REJECT"
              r"|REJECT[^.]{0,200}⟦phases[^.]{0,200}refactor").encode()
    refactor, plain = refactor_and_plain_plan_renders(tmp_path, capsysbinary, build_verify_prompt)

    assert (refactor[0], re.search(phases, refactor[1]) is not None, re.search(phases, plain[1]) is not None) == (0, True, False)


@pytest.mark.tree_audit("the templates under prompts/")
def test_main_tells_the_refactor_plan_verifier_to_reject_a_step_that_only_edits_tests_1527(tmp_path, capsysbinary, build_verify_prompt):
    test_only = (r"REJECT[^.]{0,200}refactor[^.]{0,200}(only edits|edits only|only changes|changes only)[^.]{0,40}tests?"
                 r"|refactor-kind plan[^.]{0,200}(only edits|edits only|only changes|changes only)[^.]{0,40}tests?[^.]{0,200}REJECT").encode()
    refactor, plain = refactor_and_plain_plan_renders(tmp_path, capsysbinary, build_verify_prompt)

    assert (refactor[0], re.search(test_only, refactor[1]) is not None, re.search(test_only, plain[1]) is not None) == (0, True, False)


def test_main_exits_2_naming_the_fixture_repair_partial_when_it_is_missing_for_a_marked_green_step_1021(
        tmp_path, capsysbinary):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    (scripts / "prompts").mkdir()
    (scripts / "veri" / "build_verify_prompt.py").write_bytes((SCRIPTS / "veri" / "build_verify_prompt.py").read_bytes())
    for name in ("verify-green.md", "_shared.md"):
        (scripts / "prompts" / name).write_bytes(b"x\n")
    loader = importlib.util.spec_from_file_location("build_verify_prompt_no_fixture_partial",
                                                    scripts / "veri" / "build_verify_prompt.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    step = ("the case passes under load: repairs the fixture 'awake-clock' in tests/zorblat.test.sh, "
            "reproduced by a case in tests/zorblat.test.sh ⟦fixture-repair⟧ ⟦criterion 1⟧")

    code = module.main(["--step", step, "--fast-cmd", "make unit", "green", str(spec), "t.py", "test_x"])

    assert (code, *capsysbinary.readouterr()) == (
        2, b"", f"build-verify-prompt: cannot read '{scripts / 'prompts' / '_verify-green-fixture-repair.md'}'\n".encode())


def test_main_renders_a_plan_prompt_for_a_refactor_spec_limiting_its_refactor_checks_to_steps_that_are_not_diff_checked_or_pin_and_rejecting_a_test_only_step_only_when_planned_otherwise_1915(
        tmp_path, capsysbinary, build_verify_prompt):
    ledger = tmp_path / "plan.md"
    ledger.write_text("# Plan for #1417\n\n- [ ] a step ⟦criterion 1⟧\n", encoding="utf-8")

    def plan_prompt(name, spec_bytes):
        spec = tmp_path / name
        spec.write_bytes(spec_bytes)
        assert build_verify_prompt.main(["plan", str(spec), str(ledger)]) == 0
        out, _ = capsysbinary.readouterr()
        return " ".join(out.decode("utf-8", "surrogateescape").replace("`", "").split())

    with_refactor = plan_prompt("refactor.md", b"# spec\n\n## Refactor\n\ntidy it\n")
    without = plan_prompt("plain.md", b"# spec\n\n1. A case pins behaviour.\n")

    limit = "the first three only to a step that is neither ⟦diff-checked⟧ nor a pin step"
    test_only = "holds a step that only edits tests, unless that step is planned as ⟦diff-checked⟧ or a pin step"
    assert ((limit in with_refactor, test_only in with_refactor),
            (limit in without, test_only in without)) == ((True, True), (False, False))


def test_the_green_prompt_requires_a_coverage_judgement_to_run_the_fast_command_and_the_affected_suites_never_one_file_and_a_reject_to_name_the_command_run_2477(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    assert build_verify_prompt.main(
        ["--fast-cmd", "make unit", "green", str(spec), "tests/test_slugify.py", "test_slugify_lowercases"]) == 0
    prompt = " ".join(capsysbinary.readouterr()[0].decode("utf-8", "surrogateescape").split())

    assert {
        "fast command and affected suites": re.search(
            r"covered by a case is made by running the fast command you were given, `make unit`, and the affected suites",
            prompt, re.I) is not None,
        "never one file": re.search(r"never one test file alone", prompt, re.I) is not None,
        "REJECT names the command": re.search(
            r"A REJECT on that ground names the exact command that was run", prompt) is not None,
    } == {"fast command and affected suites": True, "never one file": True, "REJECT names the command": True}


def test_the_refactor_and_diff_prompts_each_require_a_coverage_judgement_to_run_the_fast_command_and_the_affected_suites_never_one_file_2477(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    found = {}
    for phase, rest in (("refactor", ["t", "0123abc"]), ("diff", ["0123abc", "0123abc"])):
        assert build_verify_prompt.main(["--fast-cmd", "make unit", "--step", "s", phase, str(spec), *rest]) == 0
        prompt = " ".join(capsysbinary.readouterr()[0].decode("utf-8", "surrogateescape").split())
        found[phase] = (
            re.search(r"covered by a case is made by running the fast command you were given, `make unit`, "
                      r"and the affected suites, never one test file alone", prompt, re.I) is not None,
            re.search(r"A REJECT on that ground names the exact command that was run", prompt) is not None)

    assert found == {"refactor": (True, True), "diff": (True, True)}


def test_main_renders_a_red_prompt_with_fast_cmd_that_runs_it_once_and_rejects_a_red_failing_it_for_any_reason_but_the_targets_expected_failure_naming_the_file_and_the_error_2569(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n\nthe criteria\n")
    argv = ["red", str(spec), "tests/a.test.sh", "case one"]

    def run(args):
        code = build_verify_prompt.main(args)
        return (code, *capsysbinary.readouterr())

    code, out, err = run(["--fast-cmd", "npm run lint && npm test", *argv])
    prompt = " ".join(out.decode("utf-8", "surrogateescape").split())
    assert (code, err) == (0, b"")
    assert re.search(r"Run `npm run lint && npm test` once\b.*other than the target test's expected failure.*"
                     r"\bREJECT\b.*naming the file and the error",
                     prompt) is not None


def test_main_renders_a_red_prompt_without_fast_cmd_byte_identical_to_the_template_without_the_fast_check_and_unchanged_by_veri_test_cmd_2569(
        tmp_path, capsysbinary, monkeypatch, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n\nthe criteria\n")
    argv = ["--step", "the step", "red", str(spec), "tests/a.test.sh", "case one"]
    template = (SCRIPTS / "prompts" / "verify-red.md").read_bytes()
    assert b"{{RED_FAST_CHECK}}" in template
    real_read = build_verify_prompt._read

    def read_without_check(path, *rest):
        data = real_read(path, *rest)
        return data.replace(b"{{RED_FAST_CHECK}}", b"") if str(path).endswith("verify-red.md") else data

    with monkeypatch.context() as patched:
        patched.setattr(build_verify_prompt, "_read", read_without_check)
        assert build_verify_prompt.main(argv) == 0
    expected, _ = capsysbinary.readouterr()

    assert build_verify_prompt.main(argv) == 0
    plain, _ = capsysbinary.readouterr()
    monkeypatch.setenv("VERI_TEST_CMD", "pytest -k leaked_channel")
    assert build_verify_prompt.main(argv) == 0
    with_env, _ = capsysbinary.readouterr()

    assert (plain, with_env) == (expected, expected)
