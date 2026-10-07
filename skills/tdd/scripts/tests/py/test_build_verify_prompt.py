"""In-process cases for veri/build_verify_prompt.py, the module build-verify-prompt.sh is a shim over."""
import importlib
import importlib.util
import pathlib
import re
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = b"usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]\n"


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
                                    b"(want red|green|refactor|pin|plan|rebase|transform|diff)\n" + USAGE),
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
            b"       " + real_timed + b" affected '<the suites affected-suites.sh printed>' <the command that runs them>\n"
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
        "blindness contract": has("red", r"have not (been told|received).*(reason|rationale)|never.*(reason|rationale)"),
        "verdict format": has("red", r"VERDICT:", 0) and has("red", "pass") and has("red", "reject"),
        "red audit": has("red", "right reason") and has("red", "trivial|coupled|complex"),
        "green full suite": has("green", "full") and has("green", "suite")
                            and has("green", r"full[^0-9A-Za-z]*test[^0-9A-Za-z]*suite"),
        "refactor standard and green": has("refactor", "standard|convention|typing|robust") and has("refactor", "green"),
        "pin checks": "slugify(\"Hello & World/Foo\")" in prompts["pin"]
                      and has("pin", r"pass(es)? (now|today|already|against|on the (current|unmodified))")
                      and has("pin", "mutation") and has("pin", r"behaviou?r-level|trivial"),
        "foreground": all(has(p, "foreground") and has(p, r"end(ing)?[^0-9A-Za-z]+(your|the|its)[^0-9A-Za-z]+turn")
                          for p in every),
        "git stash": all(has(p, r"(never|do not|don't|no)[^.]{0,60}stash") and has(p, r"git show HEAD:|git worktree add", 0)
                         for p in every),
        "no prediction": all(prediction not in prompts[p] and not has(p, "PREDICTED_FAILURE|PREDICTION")
                             for p in every),
        "fifth positional": {phase: (code, out) for phase, (code, out, _) in fifth.items()},
        "unknown phase": bogus[0] != 0,
    } == {
        "exits": {p: (0, b"") for p in every},
        "ambient reaches nothing": True,
        "test path": True,
        "blindness contract": True,
        "verdict format": True,
        "red audit": True,
        "green full suite": True,
        "refactor standard and green": True,
        "pin checks": True,
        "foreground": True,
        "git stash": True,
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
    red, green = prompts["red"], prompts["green"]
    with_base = run(["--fast-cmd", "make unit", "refactor", s, testpath, base_sha])
    refusals = {label: run(["--fast-cmd", "make unit", "refactor", s, testpath, *sha])[::2]
                for label, sha in (("missing", []), ("short", ["abc123"]), ("uppercase", ["3F9A1C07E2B4"]),
                                   ("with-text", ["3f9a1c07e2b4 because it tidies"]),
                                   ("too-long", ["3f9a1c07e2b43f9a1c07e2b43f9a1c07e2b43f9a1"]))}
    stepped = {phase: run(call(phase, ["--step", step])) for phase in every}
    scoped_refactor = run(["--step", step, "--fast-cmd", "make unit", "refactor", s, testpath, base_sha])[1]
    monkeypatch.setenv("VERI_STEP", ambient_step)
    ambient = {phase: run(call(phase))[1] for phase in every}
    fast_green = run(["--fast-cmd", fast_cmd, "green", s, testpath, "test_slugify_lowercases"])
    no_fast = run(["green", s, testpath, "test_slugify_lowercases"])

    refactor = with_base[1]
    assert {
        "base sha carried": (with_base[0], base_sha.encode() in refactor),
        "base sha refusals": {label: (code, bool(err)) for label, (code, err) in refusals.items()},
        "diff range": (f"git diff {base_sha}..HEAD".encode() in refactor,
                       has(refactor, r"(never|not|don't|no)[^.]{0,80}commit messages")),
        "weakened assertion": [has(refactor, p) for p in (
            r"(removed|weakened)[^.]{0,80}assertion[^.]{0,120}REJECT|REJECT[^.]{0,120}(removed|weakened)[^.]{0,80}assertion",
            r"REJECT[^.]{0,120}nam(e|es|ing)[^.]{0,40}assertion",
            r"cosmetic[^.]{0,160}REASON:",
            r"cosmetic[^.]{0,200}(not|never|no)[^.]{0,60}REJECT",
            r"empty (range|diff)[^.]{0,160}(not|never|no)[^.]{0,60}REJECT")],
        "step scoping": {phase: (code, step.encode() in out, has(
            out, r"verdict[^.]{0,160}(criterion|step)[^.]{0,40}only|verdict[^.]{0,160}only[^.]{0,40}(criterion|step)"))
            for phase, (code, out, _) in stepped.items()},
        "VERI_STEP reaches nothing": {phase: ambient[phase] == prompts[phase]
                                      and ambient_step.encode() not in ambient[phase] for phase in every},
        "out of scope": (has(scoped_refactor, r"out of scope[^.]{0,200}REASON:|REASON:[^.]{0,200}out of scope"),
                         has(scoped_refactor, r"outside[^.]{0,240}(not|never|no)[^.]{0,80}REJECT"
                                              r"|out of scope[^.]{0,240}(not|never|no)[^.]{0,80}REJECT")),
        "configuration": {phase: (has(out, r"(never|do not|don't|not)[^.]{0,80}(global|user-level)[^.]{0,60}config"),
                                  has(out, r"environment variables?"),
                                  has(out, r"(throwaway|temporary|scratch)[^.]{0,20}director(y|ies)"))
                          for phase, out in {**prompts, "refactor": refactor}.items()},
        "mechanism": {phase: [has(prompts[phase], p) for p in (
            r"(process|fork)[^.]{0,20}count|timing",
            r"in-process spy",
            r"PATH[^.]{0,60}shim|shim[^.]{0,60}(count|real process)",
            r"(runs?|running)[^.]{0,40}(another|other)[^.]{0,20}suite|re-runs?[^.]{0,30}suite")]
            for phase in ("red", "pin")},
        "fast-cmd": (fast_green[0], fast_cmd.encode() in fast_green[1], no_fast[0], bool(no_fast[2])),
        "red name error": [has(red, p) for p in (
            r"error[^.]{0,160}(exactly the name|the exact name)[^.]{0,200}(valid|legitimate) red"
            r"|(valid|legitimate) red[^.]{0,200}error[^.]{0,160}(exactly the name|the exact name)",
            r"(missing|absent)[^.]{0,120}(script|file)[^.]{0,120}(route|field)",
            r"any [^.]{0,20}other[^.]{0,20} error[^.]{0,60}before[^.]{0,40}assertion[^.]{0,80}REJECT",
            r"typo", r"wrong path|incorrect path|path that does not exist",
            r"(missing|absent) fixture", r"syntax error")],
        "red reaching assertions": [has(red, p) for p in (
            r"(must|has to|should)[^.]{0,100}not error before[^.]{0,60}assertion",
            r"(must|has to|should)[^.]{0,100}reach(es)? its assertions")],
        "green unrequired code": [has(green, p) for p in (
            r"REJECT[^.]{0,200}code[^.]{0,80}no test requires|code[^.]{0,80}no test requires[^.]{0,200}REJECT",
            r"branch[^.]{0,80}option[^.]{0,80}flag[^.]{0,80}parameter",
            r"remov(e|ed|ing|al)[^.]{0,140}(leaves?|leaving)[^.]{0,60}tests? green"
            r"|remov(e|ed|ing|al)[^.]{0,140}(every|all) tests? [^.]{0,40}green",
            r"REASON:?[^.]{0,160}nam(e|es|ing)[^.]{0,60}code|nam(e|es|ing)[^.]{0,60}code[^.]{0,160}REASON")],
        "green restore": [has(green, p) for p in (
            r"remov(e|ing)[^.]{0,120}run[^.]{0,80}suite",
            r"restor(e|ing)[^.]{0,80}(tree|code|file)",
            r"before[^.]{0,60}report")],
        "checkout rule": (has(red, r"(never|do not|don't|not)[^.]{0,120}git checkout -- <file>"),
                          has(red, r"(never|do not|don't|not)[^.]{0,160}git restore"),
                          has(red, r"(undo|restor)[^.]{0,60}(probe|mutat)"),
                          b"cp <file> <file>.orig" in red, b"mv <file>.orig <file>" in red),
    } == {
        "base sha carried": (0, True),
        "base sha refusals": {label: (2, True) for label in refusals},
        "diff range": (True, True),
        "weakened assertion": [True] * 5,
        "step scoping": {phase: (0, True, True) for phase in every},
        "VERI_STEP reaches nothing": {phase: True for phase in every},
        "out of scope": (True, True),
        "configuration": {phase: (True, True, True) for phase in every},
        "mechanism": {"red": [True] * 4, "pin": [True] * 4},
        "fast-cmd": (0, True, 2, True),
        "red name error": [True] * 7,
        "red reaching assertions": [False, False],
        "green unrequired code": [True] * 4,
        "green restore": [True] * 3,
        "checkout rule": (True, True, True, True, True),
    }


def test_main_scopes_refactor_to_the_cycles_files_with_flags_lines_checks_plan_refusals_and_criteria_rebase_transform_and_diff_rendering_test_adding_and_fast_cmd_rules(
        tmp_path, monkeypatch, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'slugify("Hello & World/Foo") must return "hello-world-foo" \xe2\x80\x94 see {ref}\\n done.\n')
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes("# Plan for #426\n\n- [ ] A verdict launcher script runs verify.sh with the step title"
                       " as an argument ⟦criterion 1⟧\n".encode())
    predicate = tmp_path / "predicate.md"
    predicate.write_bytes(b'grep -q "extract_helper" lib/foo.sh\n')
    s, testpath, base_sha = str(spec), "tests/test_slugify.py", "3f9a1c07e2b4"
    diff_step = "the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧"
    diff_fast = 'make unit ZORBLAT=diff -- --only "frob & nitz/quux"'
    every = ("red", "green", "refactor", "pin")

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    def call(phase):
        fast = ["--fast-cmd", "make unit"] if phase in ("green", "refactor") else []
        slot4 = "0123abc" if phase == "refactor" else "test_slugify_lowercases"
        return [*fast, phase, s, testpath, slot4]

    def has(out, pattern, flags=re.I):
        return re.search(pattern.encode(), out.replace(b"\n", b" "), flags) is not None

    def diff(base, step_base, fast="make unit"):
        return run(["--step", diff_step, "--fast-cmd", fast, "diff", s, base, step_base])

    monkeypatch.delenv("VERI_STEP", raising=False)
    monkeypatch.delenv("VERI_RATIONALE", raising=False)
    prompts = {phase: run(call(phase))[1] for phase in every}
    refactor = prompts["refactor"]
    with_base = run(["--fast-cmd", "make unit", "refactor", s, testpath, base_sha])[1]
    plan = run(["plan", s, str(ledger)])[1]
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
    deliver = r"deliver(s|ed|ing)?[^a-z]"
    red_word = r"(red|fails?|failing|not green)[^0-9A-Za-z]"
    gap_step = r"gap step|untagged|no[^.]{0,20}criterion[^.]{0,20}tag"

    def rejects_shape(marker, ere):
        return [f"⟦{marker}⟧".encode() in plan, has(plan, rf"REJECT[^.]{{0,200}}{ere}|{ere}[^.]{{0,200}}REJECT"),
                has(plan, rf"Red[^.]{{0,40}}Green[^.]{{0,200}}{marker}|{marker}[^.]{{0,200}}Red[^.]{{0,40}}Green")]

    assert {
        "refactor file scope": (f"git diff --name-only {base_sha}^ {base_sha}".encode() in with_base,
                                has(with_base, r"outside[^.]{0,80}list[^.]{0,160}REJECT|REJECT[^.]{0,160}outside[^.]{0,80}list"),
                                has(with_base, r"(unless|except)[^.]{0,160}duplication|duplication[^.]{0,160}(unless|except)")),
        "refactor edge case flag": [has(refactor, p) for p in (
            r"unhandled edge case[^.]{0,200}FLAGS|FLAGS[^.]{0,200}unhandled edge case",
            r"FLAGS[^.]{0,120}before[^.]{0,120}VERDICT",
            r"(edge case|robust)[^.]{0,200}not( by itself)? a REJECT|not( by itself)? a REJECT[^.]{0,200}(edge case|robust)")],
        "FLAGS allowed": {phase: [has(out, p) for p in (
            r"FLAGS[^.]{0,200}(may|can|allow|permit)|(may|can|allow|permit)[^.]{0,200}FLAGS",
            r"FLAGS[^.]{0,160}before[^.]{0,160}(VERDICT|(final|last)[^.]{0,40}two lines)")]
            for phase, out in prompts.items()},
        "plan ledger refusals": (no_ledger, missing_ledger),
        "plan together": [has(plan, p) for p in (
            r"together[^.]{0,200}deliver|deliver[^.]{0,200}together",
            r"as written|in its own terms|the criterion.{0,20}own (words|terms|wording)",
            r"REJECT[^.]{0,120}(name|identif|say|state)[^.]{0,200}criterion[^.]{0,200}(no step|nothing[^.]{0,40}cover|uncovered)",
            r"PASS[^.]{0,200}every criterion[^.]{0,200}(deliver|cover)|every criterion[^.]{0,200}(deliver|cover)[^.]{0,200}PASS")],
        "plan too big": [has(plan, p) for p in (
            r"(too (big|large)|too much|does not fit|not fit)[^.]{0,150}cycle",
            r"(name|names|say so|state)[^.]{0,100}(REASON:|reason\b)",
            r"(whether|either way|regardless)[^.]{0,100}(PASS|REJECT|verdict)")],
        "plan untagged step": [has(plan, p) for p in (
            rf"{gap_step}|(carries|carrying|with|without|has) no[^.]{{0,40}}criterion",
            rf"({gap_step})[^.]{{0,200}}(not|never|no)[^.]{{0,80}}REJECT",
            r"(by itself|on its own|alone|in itself)[^.]{0,100}REJECT|REJECT[^.]{0,100}(by itself|on its own|alone|in itself)")],
        "plan mechanism": [has(plan, p) for p in (
            r"mechanism[^.]{0,200}(sufficient|suffices|enough)|(sufficient|suffices|enough)[^.]{0,200}mechanism",
            r"REJECT[^.]{0,200}(no step|nothing)[^.]{0,150}(establish|deliver)|(no step|nothing)[^.]{0,150}(establish|deliver)[^.]{0,200}REJECT")],
        "refactor flag classes": (b"FLAGS:" in refactor, [c in refactor for c in (b"overfit", b"uncovered-spec", b"beyond-spec")],
                                  b"NEW_STEP" in refactor),
        "rebase": (rebase[0], b'slugify("Hello & World/Foo")' in rebase[1], rb_onto.encode() in rebase[1],
                   rb_pre.encode() in rebase[1], b"{{" in rebase[1],
                   has(rebase[1], r"full[^.]{0,80}(test|suite)"), b"HEAD" in rebase[1], has(rebase[1], r"default branch"),
                   has(rebase[1], r"both[^.]{0,200}(surviv|preserv|intact|kept)|(surviv|preserv|intact|kept)[^.]{0,200}both")),
        "rebase sha refusals": rebase_refusals,
        "plan full-suite": rejects_shape("full-suite", r"(test command|suites?)[^.]{0,120}pass"),
        "plan human-owed": rejects_shape("human-owed", r"(manual|human)[^.]{0,120}(check|record)"),
        "plan marker delivers": [has(plan, rf"⟦{m}⟧[^.]{{0,200}}{deliver}|{deliver}[^.]{{0,200}}⟦{m}⟧")
                                 for m in ("full-suite", "human-owed", "diff-checked")],
        "plan diff-checked": rejects_shape("diff-checked", r"diff[- ]property"),
        "plan forbidden reads": [has(plan, rf"REJECT[^.]{{0,200}}{r}|{r}[^.]{{0,200}}REJECT")
                                 for r in ("another suite's source text", "git history")],
        "plan ordering": [has(plan, p) for p in (
            r"REJECT[^.]{0,200}branch[^.]{0,200}later step|branch[^.]{0,200}later step[^.]{0,200}REJECT",
            r"nam(e|es|ing)[^.]{0,40}both[^.]{0,200}introduc[^.]{0,200}pin|nam(e|es|ing)[^.]{0,40}both[^.]{0,200}pin[^.]{0,200}introduc",
            r"after[^.]{0,80}pin[^.]{0,200}not[^.]{0,40}REJECT|not[^.]{0,40}REJECT[^.]{0,200}after[^.]{0,80}pin",
            r"only[^.]{0,40}branch[^.]{0,80}own test[^.]{0,200}not[^.]{0,40}REJECT"
            r"|not[^.]{0,40}REJECT[^.]{0,200}only[^.]{0,40}branch[^.]{0,80}own test")],
        "transform": (transform[0], b'slugify("Hello & World/Foo")' in transform[1],
                      b"git diff 0123abcdef..HEAD" in transform[1], has(transform[1], r"green commit"),
                      transform_bad_base, transforms),
        "diff rendering": (dp[0], diff_step.encode() in dp[1], b"git diff 0123abcdef..HEAD" in dp[1],
                           has(dp[1], r"git diff 0123abcdef\.\.HEAD[^.]{0,200}alone|alone[^.]{0,200}git diff 0123abcdef\.\.HEAD"),
                           b"VERDICT: PASS" in dp[1] and b"VERDICT: REJECT" in dp[1]),
        "diff blind": (has(dp[1], r"(never|not|don't|no)[^.]{0,80}commit messages"), b"{{" in dp[1],
                       b"the target test" in dp[1], dp_ambient == dp[1],
                       dp_other.replace(b"fedcba9876", b"0123abcdef") == dp[1]),
        "diff adds a test": has(dp[1], r"REJECT[^.]{0,160}(add|adds|added)[^.]{0,40}test|(add|adds|added)[^.]{0,40}test[^.]{0,160}REJECT"),
        "diff step base": (ds[0], b"git diff 0123abcdef..HEAD" in ds[1],
                           has(ds[1], r"(add|adds|added)[^.]{0,40}test[^.]{0,200}git diff 4567abcdef\.\.HEAD"
                                      r"|git diff 4567abcdef\.\.HEAD[^.]{0,200}(add|adds|added)[^.]{0,40}test")),
        "diff fast-cmd": (df[0], bool(found), b"affected-suites.sh" in after_fast,
                          has(df[1], rf"(fast|affected)[^.]{{0,200}}{red_word}[^.]{{0,200}}REJECT"
                                     rf"|REJECT[^.]{{0,200}}(fast|affected)[^.]{{0,200}}{red_word}")),
    } == {
        "refactor file scope": (True, True, True),
        "refactor edge case flag": [True] * 3,
        "FLAGS allowed": {phase: [True, True] for phase in every},
        "plan ledger refusals": ((2, b""), (2, b"")),
        "plan together": [True] * 4,
        "plan too big": [True] * 3,
        "plan untagged step": [True] * 3,
        "plan mechanism": [True] * 2,
        "refactor flag classes": (True, [True] * 3, False),
        "rebase": (0, True, True, True, False, True, True, True, True),
        "rebase sha refusals": {label: (2, b"") for label in rebase_refusals},
        "plan full-suite": [True] * 3,
        "plan human-owed": [True] * 3,
        "plan marker delivers": [True] * 3,
        "plan diff-checked": [True] * 3,
        "plan forbidden reads": [True] * 2,
        "plan ordering": [True] * 4,
        "transform": (0, True, True, False, 2, 2),
        "diff rendering": (0, True, True, True, True),
        "diff blind": (True, False, False, True, True),
        "diff adds a test": True,
        "diff step base": (0, True, True),
        "diff fast-cmd": (0, True, True, True),
    }
