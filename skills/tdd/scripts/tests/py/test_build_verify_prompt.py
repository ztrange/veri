"""In-process cases for veri/build_verify_prompt.py, the module build-verify-prompt.sh is a shim over."""
import importlib
import importlib.util
import pathlib
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
