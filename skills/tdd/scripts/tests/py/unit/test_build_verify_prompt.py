"""In-process cases for veri/build_verify_prompt.py, the module build-verify-prompt.sh is a shim over."""
import importlib
import importlib.util
import os
import re
import shutil

import pytest

from conftest import SCRIPTS

USAGE = b"usage: build-verify-prompt.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] [--supersede-base <sha>] <phase> <issue-spec-file> <test-path> [<target-test-id>]\n"


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


def every_file_tracked(line, cwd=None, **_):
    """A `git ls-files -z` answer naming every file under the current directory, as if all were tracked."""
    root = cwd or os.getcwd()
    names = [os.path.relpath(os.path.join(top, name), root) for top, _, files in os.walk(root) for name in files]
    return 0, "".join(name + "\0" for name in sorted(names)), ""


@pytest.fixture(autouse=True)
def tracked_tree(fake_processes):
    """The plan phase lists the test files git tracks (#3919); here git answers that every file is tracked."""
    return fake_processes.answers({"git ls-files": every_file_tracked})


@pytest.fixture
def build_verify_prompt():
    return importlib.import_module("veri.build_verify_prompt")


CLOSING = b"STUB-CLOSING-CONTRACT\n"


def split_closing(out, fragment=CLOSING):
    tail = fragment.rstrip(b"\n")
    text = out.rstrip(b"\n")
    if text.endswith(tail) and out.count(tail) == 1:
        return text.removesuffix(tail).rstrip(b"\n") + b"\n", True
    return out, False


EMPTY_TOUCHING_SECTION = (b"\n\n### Test cases touching the files the plan names\n\n"
                          b"No test case touches a file the plan names.")


def without_touching_cases(body):
    """The render with exactly the plan phase's empty touching-cases section (#3919) cut out, as it renders where no
    test file touches a file the plan names; anything else added to the render still shows."""
    return body.replace(EMPTY_TOUCHING_SECTION, b"", 1)


def test_main_refuses_a_missing_argument_an_option_with_no_value_an_unknown_phase_and_a_green_or_diff_call_without_fast_cmd_with_exit_2_and_its_message_then_the_usage_line(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    results = {}
    for argv in ([], ["red", "", "t"], ["--fast-cmd"], ["bogus", str(spec), "t"],
                 ["green", str(spec), "t", "x"],
                 ["--step", "s", "--branch-base", "0123abc", "diff", str(spec), "0123abc"]):
        code = build_verify_prompt.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("red", "", "t"): (2, b"", USAGE),
        ("--fast-cmd",): (2, b"", b"build-verify-prompt: --fast-cmd needs a value\n" + USAGE),
        ("bogus", str(spec), "t"): (2, b"", b"build-verify-prompt: unknown phase 'bogus' "
                                    b"(want red|green|refactor|pin|plan|rebase|transform|diff|surround|break|expand|cover-new|migrate|contract-a|contract-b)\n"
                                    + USAGE),
        ("green", str(spec), "t", "x"): (
            2, b"", b"build-verify-prompt: green needs --fast-cmd '<fast-tier test command>'\n" + USAGE),
        ("--step", "s", "--branch-base", "0123abc", "diff", str(spec), "0123abc"): (
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
    ten = ("red", "green", "refactor", "pin", "plan", "rebase", "transform", "diff", "surround", "break")
    assert all(p in build_verify_prompt.PHASES for p in ten)
    assert [p for p in build_verify_prompt.PHASES if p in ten] == list(ten)


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
        ["--fast-cmd", "m", "transform", s, "t", "012345"],
        ["--fast-cmd", "m", "--branch-base", "0123abc", "diff", s, "zz"],
        ["--step", "s", "--fast-cmd", "m", "--branch-base", "0123abc", "diff", s, "0123abG"],
        ["--step", "s", "--fast-cmd", "m", "--branch-base", "xyz", "diff", s, "0123abc"],
        ["rebase", s, "nothex", "0123abc"],
        ["rebase", s, "0123abc", "bad"],
        ["rebase", s, "0123abc"],
        ["--step", "s", "--branch-base", "0123abc", "diff", s, "bad"],
        ["--branch-base", "0123abc", "diff", s, "bad"],
        ["transform", s, "t", "0123abc"],
    )}
    assert refused == {
        ("--fast-cmd", "m", "refactor", s, "t", "0123ABC"): bad_sha(b"refactor", b"<base-sha>", b"0123ABC"),
        ("--fast-cmd", "m", "refactor", s, "t", "0123abc\n"): bad_sha(b"refactor", b"<base-sha>", b"0123abc\n"),
        ("--fast-cmd", "m", "transform", s, "t", "012345"): bad_sha(b"transform", b"<base-sha>", b"012345"),
        ("--fast-cmd", "m", "--branch-base", "0123abc", "diff", s, "zz"): refusal(b"build-verify-prompt: diff needs --step '<STEP>'"),
        ("--step", "s", "--fast-cmd", "m", "--branch-base", "0123abc", "diff", s, "0123abG"): bad_sha(
            b"diff", b"<step-base-sha>", b"0123abG"),
        ("--step", "s", "--fast-cmd", "m", "--branch-base", "xyz", "diff", s, "0123abc"): refusal(
            b"build-verify-prompt: --branch-base needs 7-40 lowercase hex characters, got 'xyz'"),
        ("rebase", s, "nothex", "0123abc"): bad_sha(b"rebase", b"<onto-sha> <pre-rebase-sha>", b"nothex"),
        ("rebase", s, "0123abc", "bad"): bad_sha(b"rebase", b"<onto-sha> <pre-rebase-sha>", b"bad"),
        ("rebase", s, "0123abc"): bad_sha(b"rebase", b"<onto-sha> <pre-rebase-sha>", b""),
        ("--step", "s", "--branch-base", "0123abc", "diff", s, "bad"): refusal(
            b"build-verify-prompt: diff needs --fast-cmd '<fast-tier test command>'"),
        ("--branch-base", "0123abc", "diff", s, "bad"): refusal(
            b"build-verify-prompt: diff needs --fast-cmd '<fast-tier test command>'"),
        ("transform", s, "t", "0123abc"): refusal(
            b"build-verify-prompt: transform needs --fast-cmd '<fast-tier test command>'"),
    }

    admitted = [run(argv)[::2] for argv in (
        ["--fast-cmd", "m", "refactor", s, "t", "0123456789abcdef0123456789abcdef01234567"],
        ["--fast-cmd", "m", "transform", s, "t", "0123abc"],
        ["rebase", s, "0123abc", "0123abd"],
        ["--step", "s", "--fast-cmd", "m", "--branch-base", "0123abc", "diff", s, "0123abd"],
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
    (prompts / "_verify-output-contract.md").write_bytes(CLOSING)
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

    transform = run(["--fast-cmd", "m", "transform", str(spec), str(missing), "0123abc"])
    assert (transform[0], transform[2], split_closing(transform[1])) == (0, b"", (b"verify-transform.md\n", True))

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
    (scripts / "prompts" / "_verify-output-contract.md").write_bytes(CLOSING)
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

    closed = []

    def run(argv):
        code = module.main(argv)
        out, err = capsysbinary.readouterr()
        body, ok = split_closing(out)
        closed.append(ok)
        return (code, body, err)

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
    assert closed == [True, True]


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
        "_verify-output-contract.md": CLOSING,
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
    closed = []

    def run(argv):
        code = module.main(argv)
        out, err = capsysbinary.readouterr()
        body, ok = split_closing(out)
        if code == 0:
            closed.append(ok)
        return (code, without_touching_cases(body), err)

    assert [
        run(["--step", "step {{INCLUDE:_b.md}}", "red", str(bug_spec), "tp", "tid"]),
        run(["--step", "⟦replaces-case⟧ ⟦suite-repair⟧", "--fast-cmd", "m", "green", str(spec), "tp", "tid"]),
        run(["--fast-cmd", "m", "green", str(spec), "tp", "tid"]),
        run(["plan", str(refactor_spec), str(ledger)]),
        run(["--branch-base", "3f9a1c0", "pin", str(spec), "t"]),
        run(["rebase", str(spec), "0123abc", "0123abd"]),
        run(["--fast-cmd", "m", "transform", str(spec), "rec", "0123abc"]),
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
    assert closed == [True] * 5
    no_base = run(["pin", str(spec), "t"])
    assert (no_base[0], no_base[1], b"--branch-base" in no_base[2]) == (2, b"", True)

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
    (tmp_path / "skills/tdd/scripts/tests/py").mkdir(parents=True)  # veri's own tree: today's run line (#4105)
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
    (prompts / "_verify-output-contract.md").write_bytes(CLOSING)
    (prompts / "_verify-green-replaces-case.md").write_bytes(b"rc\n")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"spec {{TEST_PATH}} {{STEP}} {{SHARED}} {{BASE_SHA}} & \\1\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(b"ledger & \\1 {{STEP}}\n\n")
    timed = str(scripts / "timed-test-run.sh").encode()

    closed = []

    def run(main, argv):
        code = main(argv)
        out, err = capsysbinary.readouterr()
        if main is not module.main:
            return (code, out, err)
        body, ok = split_closing(out)
        closed.append(ok)
        return (code, without_touching_cases(body), err)

    def block(step):
        return (b"### The step under judgement\n\n" + step + b"\n\n"
                b"Your verdict is about this criterion only: the spec below is the whole issue, and its other\n"
                b"criteria belong to other steps of the plan.\n\n")

    def rendered(*fields):
        return b"|".join(fields) + b"|" + timed + b"\n"

    assert [
        run(module.main, ["--step", "st & \\0", "--fast-cmd", "a & b \\1 /x", "--branch-base", "0123abc", "diff", str(spec), "4567def"]),
        run(module.main, ["rebase", str(spec), "89abcde", "fedcba9"]),
        run(module.main, ["plan", str(spec), str(ledger)]),
        run(module.main, ["red", str(spec), "tp"]),
        run(module.main, ["--step", "⟦replaces-case⟧", "--fast-cmd", "m", "green", str(spec), "tp", "tid"]),
    ] == [
        (0, rendered(b"sh", block(b"st & \\0"), b"spec 4567def {{STEP}} {{SHARED}} 0123abc & \\1", b"", b"", b"", b"",
                     b"", b"4567def", b"the target test", b"0123abc", b"4567def", b"a & b \\1 /x", b"", b""), b""),
        (0, rendered(b"sh", b"", b"spec 89abcde {{STEP}} {{SHARED}} fedcba9 & \\1", b"", b"", b"", b"",
                     b"", b"89abcde", b"fedcba9", b"fedcba9", b"", b"", b"89abcde", b"fedcba9"), b""),
        (0, rendered(b"sh", b"", b"spec " + str(ledger).encode() + b" {{STEP}} {{SHARED}}  & \\1", b"", b"", b"", b"",
                     b"ledger & \\1 {{STEP}}", str(ledger).encode(), b"the target test", b"", b"", b"", b"", b""), b""),
        (0, rendered(b"sh", b"", b"spec tp {{STEP}} {{SHARED}}  & \\1", b"", b"", b"", b"",
                     b"", b"tp", b"the target test", b"", b"", b"", b"", b""), b""),
        (0, rendered(b"sh", block("⟦replaces-case⟧".encode()), b"spec tp {{STEP}} {{SHARED}} tid & \\1", b"", b"",
                     b"\n\nrc", b"", b"", b"tp", b"tid", b"tid", b"", b"m", b"", b""), b""),
    ]
    assert closed == [True] * 5

    code, out, err = run(build_verify_prompt.main, ["--step", "s", "--fast-cmd", "make unit && a/b", "--branch-base", "0123abc", "diff",
                                                    str(spec), "4567def"])
    real_timed = f"{build_verify_prompt.HERE}/timed-test-run.sh".encode()
    assert (code, err, b"git diff 0123abc..HEAD" in out, b"git diff 4567def..HEAD" in out,
            b"       " + real_timed + b" fast '' make unit && a/b\n"
            b"       " + real_timed + b" changed '<the test files you ran>' make test TESTS=\"<those paths>\"\n"
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
    (scripts / "prompts" / "_verify-output-contract.md").write_bytes(CLOSING)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"spec \xff\xfe end\n")

    code = module.main(["--step", "step \udcff end", "red", str(spec), "tp"])
    out, err = capsysbinary.readouterr()
    body, ok = split_closing(out)

    assert (code, body, err, ok) == (
        0,
        b"### The step under judgement\n\nstep \xff end\n\n"
        b"Your verdict is about this criterion only: the spec below is the whole issue, and its other\n"
        b"criteria belong to other steps of the plan.\n\n"
        b"spec:spec \xff\xfe end\n",
        b"",
        True,
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
        "pin": ["--branch-base", "3f9a1c0", "pin", s, testpath, "test_slugify_lowercases"],
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
    no_base = run(["pin", s, testpath, "test_slugify_lowercases"])
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
        "pin without a branch base": (no_base[0], no_base[1], b"--branch-base" in no_base[2]),
    } == {
        "exits": {p: (0, b"") for p in every},
        "ambient reaches nothing": True,
        "test path": True,
        "verdict format": True,
        "pin checks": True,
        "no prediction": True,
        "fifth positional": {p: (2, b"") for p in every},
        "unknown phase": True,
        "pin without a branch base": (2, b"", True),
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
        base = ["--branch-base", "3f9a1c0"] if phase == "pin" else []
        return [*step_args, *fast, *base, phase, s, testpath, slot4]

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
        return run(["--step", diff_step, "--fast-cmd", fast, "--branch-base", base, "diff", s, step_base])

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
    transform = run(["--fast-cmd", diff_fast, "transform", s, str(predicate), "0123abcdef"])
    _, transform_fast, transform_after_fast = transform[1].partition(f"timed-test-run.sh fast '' {diff_fast}".encode())
    transform_bad_base = run(["--fast-cmd", "m", "transform", s, str(predicate), "tidied the helper"])[0]
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
                      bool(transform_fast), b"changed '<the test files you ran>'" in transform_after_fast,
                      transform_bad_base, transforms),
        "diff rendering": (dp[0], diff_step.encode() in dp[1], b"git diff 0123abcdef..HEAD" in dp[1]),
        "diff blind": (b"{{" in dp[1],
                       b"the target test" in dp[1], dp_ambient == dp[1],
                       dp_other.replace(b"fedcba9876", b"0123abcdef") == dp[1]),
        "diff step base": (ds[0], b"git diff 0123abcdef..HEAD" in ds[1]),
        "diff fast-cmd": (df[0], bool(found), b"changed '<the test files you ran>'" in after_fast),
    } == {
        "refactor file scope": True,
        "plan ledger refusals": ((2, b""), (2, b"")),
        "rebase": (0, True, True, True, False),
        "rebase sha refusals": {label: (2, b"") for label in rebase_refusals},
        "transform": (0, True, True, True, True, 2, 2),
        "diff rendering": (0, True, True),
        "diff blind": (False, False, True, True),
        "diff step base": (0, True),
        "diff fast-cmd": (0, True, True),
    }


@pytest.mark.tree_audit("the templates under prompts/")
def test_main_refuses_diff_without_fast_cmd_reads_the_refactor_plan_replaces_case_and_suite_repair_paragraphs_for_their_phase_alone_renders_the_comment_rules_byte_identical_unmarked_green_and_resolves_or_refuses_includes(
        tmp_path, capsysbinary, build_verify_prompt):
    (tmp_path / "skills/tdd/scripts/tests/py").mkdir(parents=True)  # veri's own tree: today's run line (#4105)
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

    def fragment_line(name):
        lines = (SCRIPTS / "prompts" / name).read_bytes().splitlines()
        return next(line for line in lines[1:] if line and b"{{" not in line)

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
        contract = open(f"{build_verify_prompt.HERE}/prompts/_verify-output-contract.md", "rb").read().rstrip(b"\n")
        out = out.rstrip(b"\n")
        out = out.removesuffix(contract).rstrip(b"\n") if contract else out
        body = out.replace(build_verify_prompt.HERE.encode(), b"@SCRIPTS@") + b"\n"
        return code, cksum(body)

    def unreadable_paragraph(name, paragraph, marked, unmarked):
        module, _ = scratch(tmp_path, name, drop=[paragraph])
        refused = run(module.main, marked)
        return (refused[0], refused[1], paragraph.encode() in refused[2],
                [run(module.main, argv)[0] for argv in unmarked])

    diff_no_fast = run(build_verify_prompt.main, ["--step", "s", "--branch-base", "0123abcdef", "diff", s, "4567abcdef"])
    plan = run(build_verify_prompt.main, ["plan", s, str(ledger)])[1]
    rf_plan = run(build_verify_prompt.main, ["plan", rs, str(ledger)])
    green = run(build_verify_prompt.main, green_args)[1]
    replaces_green = run(build_verify_prompt.main, ["--step", replaces_step, "--fast-cmd", "make unit", "green", s,
                                                    "tests/py/test_zorblat.py", "test_zorblat_frobs_a_nitz"])
    repair_green = run(build_verify_prompt.main, ["--step", repair_step, "--fast-cmd", "make unit", "green", s,
                                                  "skills/tdd/scripts/tests/zorblat.test.sh", "zorblat frobs a nitz"])
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
    include_run = run(included.main, red_args)
    real_contract = (SCRIPTS / "prompts" / "_verify-output-contract.md").read_bytes()
    include_body, include_ok = split_closing(include_run[1], real_contract)
    include_closed = (include_run[0], include_body, include_run[2], include_ok)
    dangling_run = run(dangling.main, red_args)
    cycle_run = run(cycle.main, red_args)

    assert {
        "diff without fast-cmd": (diff_no_fast[0], diff_no_fast[1], diff_no_fast[2] != b""),
        "refactor plan": (rf_plan[0], fragment_line("_verify-plan-refactor.md") in rf_plan[1],
                          fragment_line("_verify-plan-refactor.md") in plan),
        "refactor plan unreadable": unreadable_paragraph(
            "no-refactor-plan", "_verify-plan-refactor.md", ["plan", rs, str(ledger)],
            [["red", rs, testpath, "test_slugify_lowercases"]]),
        "replaces-case": (replaces_green[0], fragment_line("_verify-green-replaces-case.md") in replaces_green[1],
                          fragment_line("_verify-green-replaces-case.md") in green),
        "suite-repair": (repair_green[0], fragment_line("_verify-green-suite-repair.md") in repair_green[1],
                         fragment_line("_verify-green-suite-repair.md") in green),
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
        "#703 include": include_closed,
        "#703 missing partial": (dangling_run[0], dangling_run[1],
                                 str(dangling_prompts / "_probe-absent.md").encode() in dangling_run[2]),
        "#703 self-including partial": (cycle_run[0], cycle_run[1], b"_probe-cycle-a.md" in cycle_run[2]),
    } == {
        "diff without fast-cmd": (2, b"", True),
        "refactor plan": (0, True, False),
        "refactor plan unreadable": (2, b"", True, [0]),
        "replaces-case": (0, True, False),
        "suite-repair": (0, True, False),
        "replaces-case unreadable": (2, b"", True, [0]),
        "suite-repair unreadable": (2, b"", True, [0, 0]),
        "#671 byte-identity": [(0, "3946582125 11091"), (0, "16492697 10815")],
        "#703 include": (0, f"before outer inner judges {testpath} end after\n".encode(), b"", True),
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
        "pin": ["--branch-base", "3f9a1c0", "pin", s, "tests/zorblat.test.sh", "zorblat frobs a nitz"],
        "plan": ["plan", s, str(ledger)],
        "rebase": ["rebase", s, sha, "4567def"],
        "transform": ["--fast-cmd", "m", "transform", s, str(tmp_path / "predicate.md"), sha],
        "diff": ["--step", "zorblat frobs a nitz", *fast, "--branch-base", sha, "diff", s, "4567def"],
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


def test_a_develop_and_a_verify_prompt_carry_the_third_paragraph_of_leaf_safety_the_untrusted_text_rule_above_the_issue_text_3958(
        tmp_path, capsysbinary, build_verify_prompt):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    s = str(spec)

    def flat(data):
        return re.sub(rb"\s+", b" ", data).strip()

    def rendered(main, argv):
        code = main(argv)
        out, _ = capsysbinary.readouterr()
        return code, flat(out)

    blocks = (SCRIPTS / "prompts" / "_leaf-safety.md").read_bytes().split(b"\n\n")
    paragraph = flat(blocks[2]) if len(blocks) > 3 and b"{{INCLUDE:" not in blocks[2] else None
    prompts = {
        "develop red": rendered(build_develop_prompt.main, ["red", s, "zorblat frobs a nitz", "make test"]),
        "verify red": rendered(build_verify_prompt.main, ["red", s, "tests/zorblat.test.sh", "zorblat frobs a nitz"]),
    }

    def above_the_issue_text(out):
        return paragraph is not None and -1 < out.find(paragraph) < out.find(b'zorblat("Frob & Nitz/Quux")')

    assert {
        "a prose third paragraph before the include line": paragraph is not None,
        "carried above the issue text": {kind: (code, above_the_issue_text(out)) for kind, (code, out) in prompts.items()},
    } == {
        "a prose third paragraph before the include line": True,
        "carried above the issue text": dict.fromkeys(prompts, (0, True)),
    }


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

    line = next(l for l in (SCRIPTS / "prompts" / "_verify-green-ci-repair.md").read_bytes().splitlines()
                if l and b"{{" not in l)
    line = re.sub(rb"\s+", b" ", line)

    assert (line in marked, line in unmarked) == (True, False)


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
    line = next(l for l in (SCRIPTS / "prompts" / "_verify-green-fixture-repair.md").read_bytes().splitlines()
                if l and b"{{" not in l)
    line = re.sub(rb"\s+", b" ", line)

    assert {key: line in prompt for key, prompt in prompts.items()} == {
        "marked green": True, "unmarked green": False, "marked red": False, "marked refactor": False}


def _fragment_line(name):
    line = next(l for l in (SCRIPTS / "prompts" / name).read_bytes().splitlines() if l.strip() and b"{{" not in l)
    return re.sub(rb"\s+", b" ", line).strip()


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

    paragraph = _fragment_line("_verify-green-replaces-case.md")
    mention = "zorblat reads the ⟦replaces-case⟧ mark, quoted as `⟦replaces-case⟧` in prose"
    marked = rendered(f"{mention} ⟦replaces-case⟧ ⟦criterion 1⟧")
    mentioned = rendered(f"{mention} ⟦criterion 1⟧")

    assert [paragraph in marked, paragraph in mentioned] == [True, False]


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
    return [paragraph in rendered(f"{mention} ⟦criterion 1⟧"),
            paragraph in rendered(f"{mention} ⟦{mark}⟧ ⟦criterion 1⟧")]


def test_main_renders_no_suite_repair_green_paragraph_for_a_step_naming_the_mark_mid_sentence_without_ending_in_it_1919(
        tmp_path, capsysbinary, build_verify_prompt):
    assert _green_paragraph_by_trailing_marker(
        tmp_path, capsysbinary, build_verify_prompt, "suite-repair", _fragment_line("_verify-green-suite-repair.md")) == [False, True]


def test_main_renders_no_ci_repair_green_paragraph_for_a_step_naming_the_mark_mid_sentence_without_ending_in_it_1919(
        tmp_path, capsysbinary, build_verify_prompt):
    assert _green_paragraph_by_trailing_marker(
        tmp_path, capsysbinary, build_verify_prompt, "ci-repair", _fragment_line("_verify-green-ci-repair.md")) == [False, True]


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


def test_main_renders_the_expand_migrate_contract_a_and_contract_b_verify_prompts_with_exit_0_no_stderr_and_each_its_own_phase_heading(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"zorblat(nitz) replaces frob(nitz, quux).\n")
    step = ("Interface change: frob(nitz, quux) becomes zorblat(nitz) "
            "⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 2⟧")

    def rendered(phase):
        code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", phase, str(spec),
                                         "tests/py/test_zorblat.py", "0123abc"])
        out, err = capsysbinary.readouterr()
        return code, err, "## Phase: verify-%s" % phase in out.decode("utf-8", "surrogateescape")

    phases = ("expand", "migrate", "contract-a", "contract-b")
    assert {phase: rendered(phase) for phase in phases} == {phase: (0, b"", True) for phase in phases}


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
        fast += ["--branch-base", "3f9a1c0"] if phase == "pin" else []
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
    bug_line = " ".join(next(line for line in (SCRIPTS / "prompts" / "_verify-red-bug.md").read_text().splitlines()
                             if line.strip() and "{{" not in line).split())
    problems = []

    code, bug_red, _ = run_cli(build_verify_prompt, ["red", str(bug_spec), TESTPATH, "test_slugify_lowercases"])
    _, red, _ = run_cli(build_verify_prompt, ["red", spec, TESTPATH, "test_slugify_lowercases"])
    if code != 0:
        problems.append(f"with a bug spec and red's own four positionals exited {code}, want 0")
    if 'slugify returned "HELLO_WORLD" on the ampersanded seed.' not in bug_red:
        problems.append("does not carry the bug report from the spec")
    if bug_line not in " ".join(bug_red.split()):
        problems.append("the bug render does not carry the bug fragment")
    if bug_line in " ".join(red.split()):
        problems.append("a spec with no Bug section still carries the bug fragment")

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
            ("diff with a non-hex base",
             "build-verify-prompt: --branch-base needs 7-40 lowercase hex characters, got 'tidied the helper'",
             [*step, *fc, "--branch-base", "tidied the helper", "diff", spec, STEP_BASE]),
            ("diff with no --step", "build-verify-prompt: diff needs --step '<STEP>'",
             [*fc, "--branch-base", DIFF_BASE, "diff", spec, DIFF_BASE]),
            ("diff with no step base", USAGE.decode().rstrip("\n"),
             [*step, *fc, "--branch-base", DIFF_BASE, "diff", spec]),
            ("diff with a non-hex step base", hex_message("<step-base-sha>", "tidied the helper"),
             [*step, *fc, "--branch-base", DIFF_BASE, "diff", spec, "tidied the helper"]),
            ("diff with an uppercase step base", hex_message("<step-base-sha>", "4567ABCDEF"),
             [*step, *fc, "--branch-base", DIFF_BASE, "diff", spec, "4567ABCDEF"]),
            ("diff with a 6-character step base", hex_message("<step-base-sha>", "4567ab"),
             [*step, *fc, "--branch-base", DIFF_BASE, "diff", spec, "4567ab"])):
        problems += diff_refusal_problems(run_cli, build_verify_prompt, label, want, argv)

    assert problems == []


def test_1041_diff_with_fast_cmd_refuses_an_extra_positional_argument_with_exit_2_and_the_extra_argument_message(
        tmp_path, spec, run_cli, build_verify_prompt):

    problems = diff_refusal_problems(
        run_cli, build_verify_prompt, "diff with an extra positional", "build-verify-prompt: too many arguments",
        ["--step", DIFF_STEP, "--fast-cmd", "make unit", "--branch-base", DIFF_BASE, "diff", spec, DIFF_BASE, DIFF_BASE,
         "extra"])

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


def test_the_green_prompt_requires_a_coverage_judgement_to_run_the_fast_command_and_the_affected_suites_never_one_file_and_a_reject_to_name_the_command_run_2477(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    assert build_verify_prompt.main(
        ["--fast-cmd", "make unit", "green", str(spec), "tests/test_slugify.py", "test_slugify_lowercases"]) == 0
    prompt = " ".join(capsysbinary.readouterr()[0].decode("utf-8", "surrogateescape").split())

    probe = " ".join((SCRIPTS / "prompts" / "_verify-coverage-probe.md").read_text().replace("{{FAST_CMD}}", "make unit").split())
    assert probe in prompt


def test_the_refactor_and_diff_prompts_each_require_a_coverage_judgement_to_run_the_fast_command_and_the_affected_suites_never_one_file_2477(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    probe = " ".join((SCRIPTS / "prompts" / "_verify-coverage-probe.md").read_text().replace("{{FAST_CMD}}", "make unit").split())
    found = {}
    for phase, flags, rest in (("refactor", [], ["t", "0123abc"]), ("diff", ["--branch-base", "0123abc"], ["0123abc"])):
        assert build_verify_prompt.main(["--fast-cmd", "make unit", "--step", "s", *flags, phase, str(spec), *rest]) == 0
        found[phase] = probe in " ".join(capsysbinary.readouterr()[0].decode("utf-8", "surrogateescape").split())

    assert found == {"refactor": True, "diff": True}


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
    fast = " ".join((SCRIPTS / "prompts" / "_verify-red-fast.md").read_text()
                    .replace("{{FAST_CMD}}", "npm run lint && npm test").split())
    assert fast in prompt


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


def test_main_renders_a_verify_beside_prompt_telling_the_blind_verifier_to_reject_a_diff_that_changes_the_old_interfaces_behaviour_or_makes_it_a_proxy_2826(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"zorblat(nitz) is added beside frob(nitz, quux).\n")
    step = "Interface change: add zorblat(nitz) beside frob ⟦phases: beside, cover-new, migrate⟧ ⟦criterion 2⟧"

    code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", "beside", str(spec),
                                     "tests/py/test_zorblat.py", "0123abc"])
    out, err = capsysbinary.readouterr()
    prompt = re.sub(rb"\s+", b" ", out)

    assert (code, err) == (0, b""), err
    assert (b"## Phase: verify-beside" in prompt, b"git diff 0123abc..HEAD" in prompt) == (True,) * 2, out


def test_main_refuses_a_beside_call_without_fast_cmd_or_without_a_base_sha_with_exit_2_as_the_other_interface_phases_do_2826(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    s = str(spec)

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    assert run(["beside", s, "t", "0123abc"]) == (
        2, b"", b"build-verify-prompt: beside needs --fast-cmd '<fast-tier test command>'\n" + USAGE)
    assert run(["--fast-cmd", "m", "beside", s, "t"]) == (
        2, b"", b"build-verify-prompt: beside needs <base-sha> as 7-40 lowercase hex characters, got ''\n" + USAGE)


def test_main_renders_a_verify_dual_stub_prompt_telling_the_blind_verifier_to_reject_a_diff_in_which_an_edited_case_does_not_stub_both_transports_or_fails_against_unmoved_production_or_weakens_an_assertion_2826(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"zorblat(nitz) is added beside frob(nitz, quux).\n")
    step = "Interface change: add zorblat(nitz) beside frob ⟦phases: beside, cover-new, dual-stub, migrate⟧ ⟦criterion 3⟧"

    code = build_verify_prompt.main(["--step", step, "--fast-cmd", "make unit", "dual-stub", str(spec),
                                     "tests/py/test_zorblat.py", "0123abc"])
    out, err = capsysbinary.readouterr()
    prompt = re.sub(rb"\s+", b" ", out)

    assert (code, err) == (0, b""), err
    assert (b"## Phase: verify-dual-stub" in prompt, b"git diff 0123abc..HEAD" in prompt) == (True,) * 2, out


def test_main_fills_the_pin_prompts_branch_base_slot_from_branch_base_with_only_that_hex_commit_name_2900(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"slugify must lowercase.\n")
    base = "3f9a1c07e2b4"

    def run(argv):
        code = build_verify_prompt.main(argv)
        return (code, *capsysbinary.readouterr())

    pin = ["pin", str(spec), "tests/test_slugify.py", "test_slugify_lowercases"]
    filled = run(["--branch-base", base, *pin])
    prompt = filled[1].decode("utf-8", "surrogateescape")
    refused = {value: run(["--branch-base", value, *pin])[::2] for value in ("nothex", "3f9a1C0", "3f9a1c0\n")}
    assert {
        "exit": filled[0],
        "before-state probe names the base": f"--before {base} --keep 'tests/test_slugify.py'" in prompt,
        "no slot left": "{{BRANCH_BASE}}" not in prompt,
        "non-hex refusals": {value: (code, bool(err)) for value, (code, err) in refused.items()},
    } == {
        "exit": 0,
        "before-state probe names the base": True,
        "no slot left": True,
        "non-hex refusals": {value: (2, True) for value in refused},
    }


def test_main_refuses_a_pin_call_whose_branch_base_is_absent_with_exit_2_and_its_message_and_no_prompt_2900(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"slugify must lowercase.\n")

    code = build_verify_prompt.main(["pin", str(spec), "tests/test_slugify.py", "test_slugify_lowercases"])
    out, err = capsysbinary.readouterr()

    assert {"exit": code, "names --branch-base": b"--branch-base" in err, "prompt": out} == {
        "exit": 2, "names --branch-base": True, "prompt": b""}


def test_main_lists_the_ledgers_later_unchecked_steps_in_a_green_prompt_given_ledger_and_leaves_it_unchanged_without_2916(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"zorblat frobs.\n")
    ledger = tmp_path / "issue-7.md"
    ledger.write_bytes("- [ ] zorblat frobs ⟦criterion 1⟧\n- [ ] quuxlet nitzes ⟦criterion 2⟧\n"
                       "- [ ] wibblet sorts ⟦criterion 3⟧\n".encode())

    def rendered(*extra):
        code = build_verify_prompt.main(["--step", "zorblat frobs ⟦criterion 1⟧", *extra, "--fast-cmd", "make unit",
                                         "green", str(spec), "tests/py/test_zorblat.py", "test_zorblat_frobs"])
        out, _ = capsysbinary.readouterr()
        return code, out.decode()

    code, with_ledger = rendered("--ledger", str(ledger))
    plain_code, plain = rendered()

    assert (code, plain_code) == (0, 0)
    assert ("quuxlet nitzes" in with_ledger, "wibblet sorts" in with_ledger, "quuxlet nitzes" in plain) == (True, True, False)
    assert with_ledger.count("zorblat frobs ⟦criterion 1⟧") == plain.count("zorblat frobs ⟦criterion 1⟧")


def test_main_omits_a_checked_later_step_from_a_green_prompts_later_steps_and_renders_none_for_a_red_prompt_given_ledger_2916(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"zorblat frobs.\n")
    ledger = tmp_path / "issue-7.md"
    ledger.write_bytes("- [ ] zorblat frobs ⟦criterion 1⟧\n- [x] quuxlet nitzes ⟦criterion 2⟧\n"
                       "- [ ] wibblet sorts ⟦criterion 3⟧\n".encode())

    def rendered(phase):
        code = build_verify_prompt.main(["--step", "zorblat frobs ⟦criterion 1⟧", "--ledger", str(ledger),
                                         "--fast-cmd", "make unit", phase, str(spec), "tests/py/test_zorblat.py",
                                         "test_zorblat_frobs"])
        out, _ = capsysbinary.readouterr()
        return code, out.decode()

    green_code, green = rendered("green")
    red_code, red = rendered("red")

    assert (green_code, red_code) == (0, 0)
    assert ("wibblet sorts" in green, "quuxlet nitzes" in green, "wibblet sorts" in red) == (True, False, False)


def test_the_green_prompts_mutation_probe_line_names_the_fast_command_and_the_affected_suites_together_not_a_bare_suites_command_3041(
        tmp_path, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    assert build_verify_prompt.main(
        ["--fast-cmd", "make unit-3041", "green", str(spec), "tests/test_slugify.py", "test_slugify_lowercases"]) == 0
    prompt = " ".join(capsysbinary.readouterr()[0].decode("utf-8", "surrogateescape").split())

    probe_lines = re.findall(r"mutation-probe\.sh <file> <old> <new> -- [^`]*`", prompt)
    assert len(probe_lines) == 1
    assert "make unit-3041" in probe_lines[0]


def test_3104_supersede_base_that_is_not_lowercase_hex_exits_2_and_prints_no_prompt(
        tmp_path, run_cli, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")

    for value in ("zz", "0123ABC", "012345", "0123abc\nrationale", "0123abc" + "0" * 34):
        code, out, err = run_cli(build_verify_prompt, [
            "--step", "s", "--fast-cmd", "m", "--supersede-base", value,
            "--branch-base", "0123abc", "diff", str(spec), "0123abd"])

        assert (code, out) == (2, "")
        assert "--supersede-base" in err
        assert "7-40 lowercase hex characters" in err


def test_3104_supersede_base_diff_prompt_judges_git_diff_of_that_sha_and_keeps_own_red_case_out_of_scope(
        tmp_path, run_cli, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    sha = "abcdef1234567"

    code, out, _ = run_cli(build_verify_prompt, [
        "--step", "s", "--fast-cmd", "m", "--supersede-base", sha,
        "--branch-base", "0123abc", "diff", str(spec), "0123abd"])
    flat = " ".join(out.split())

    assert code == 0
    assert f"git diff {sha}" in flat


def test_main_renders_a_diff_prompt_naming_a_unit_whose_skill_edit_step_ran_author_less_as_already_present_3404(
        tmp_path, capsysbinary, monkeypatch, build_verify_prompt):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"ts": 1, "awake": 1, "issue": "3404", "actor": "", "phase": "", "step": "", '
        '"event": "skill-edit-no-author", "attempt": "", "skill_commit": "", "unit": "skills/tdd/SCRIPTS.md"}\n')
    spec = tmp_path / "spec.md"
    spec.write_text("spec\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_ISSUE", "3404")

    code = build_verify_prompt.main(["--step", "s", "--fast-cmd", "make unit", "--branch-base", "0123abc", "diff", str(spec), "4567def"])
    out, _ = capsysbinary.readouterr()
    prompt = re.sub(r"\s+", " ", out.decode("utf-8", "surrogateescape"))

    assert (code, "skills/tdd/SCRIPTS.md" in prompt, "already present" in prompt) == (0, True, True)


def test_main_lists_only_this_issues_named_author_less_units_sorted_past_an_unreadable_log_line_and_only_in_a_diff_prompt_3404(
        tmp_path, capsysbinary, monkeypatch, build_verify_prompt):
    def event(issue, unit):
        unit_field = f', "unit": "{unit}"' if unit is not None else ""
        return ('{"ts": 1, "awake": 1, "issue": "%s", "actor": "", "phase": "", "step": "", '
                '"event": "skill-edit-no-author", "attempt": "", "skill_commit": ""%s}\n' % (issue, unit_field))

    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        event("3404", "skills/tdd/b-unit.md") + "not json at all\n" + event("9999", "skills/tdd/foreign-unit.md")
        + event("3404", None) + event("3404", "skills/tdd/a-unit.md"))
    spec = tmp_path / "spec.md"
    spec.write_text("spec\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_ISSUE", "3404")

    def rendered(*phase_args):
        code = build_verify_prompt.main(["--step", "s", "--fast-cmd", "make unit", *phase_args])
        out, _ = capsysbinary.readouterr()
        return code, re.sub(r"\s+", " ", out.decode("utf-8", "surrogateescape"))

    code, diff = rendered("--branch-base", "0123abc", "diff", str(spec), "4567def")
    green_code, green = rendered("green", str(spec), "tests/py/test_x.py", "test_x")

    assert (code, green_code) == (0, 0)
    assert (
        "- skills/tdd/a-unit.md - skills/tdd/b-unit.md" in diff,
        "foreign-unit" in diff,
        "already present" in green,
        "a-unit" in green,
    ) == (True, False, False, False)


def test_main_renders_a_diff_prompt_without_the_author_less_block_when_the_log_holds_no_event_for_this_issue_3404(
        tmp_path, capsysbinary, monkeypatch, build_verify_prompt):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"ts": 1, "awake": 1, "issue": "9999", "actor": "", "phase": "", "step": "", '
        '"event": "skill-edit-no-author", "attempt": "", "skill_commit": "", "unit": "skills/tdd/SCRIPTS.md"}\n')
    spec = tmp_path / "spec.md"
    spec.write_text("spec\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_ISSUE", "3404")

    code = build_verify_prompt.main(["--step", "s", "--fast-cmd", "make unit", "--branch-base", "0123abc", "diff", str(spec), "4567def"])
    out, _ = capsysbinary.readouterr()
    prompt = re.sub(r"\s+", " ", out.decode("utf-8", "surrogateescape"))

    assert (code, "already present" in prompt, "skills/tdd/SCRIPTS.md" in prompt) == (0, False, False)


def test_main_keeps_leaf_output_and_reason_files_out_of_a_diff_prompt_that_carries_the_author_less_block_3404(
        tmp_path, capsysbinary, monkeypatch, build_verify_prompt):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "events.jsonl").write_text(
        '{"ts": 1, "awake": 1, "issue": "3404", "actor": "", "phase": "", "step": "", '
        '"event": "skill-edit-no-author", "attempt": "", "skill_commit": "", "unit": "skills/tdd/SCRIPTS.md"}\n')
    (tdd / "issue-3404-step3-develop.out").write_text("ZEBRA-RATIONALE-OUT the developer reasoned thus\n")
    (tdd / "issue-3404-step3-develop.reason").write_text("ZEBRA-RATIONALE-REASON because it was upstream\n")
    spec = tmp_path / "spec.md"
    spec.write_text("spec\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_ISSUE", "3404")

    code = build_verify_prompt.main(["--step", "s", "--fast-cmd", "make unit", "--branch-base", "0123abc", "diff", str(spec), "4567def"])
    out, _ = capsysbinary.readouterr()
    prompt = out.decode("utf-8", "surrogateescape")

    assert (code, "already present" in " ".join(prompt.split()), "ZEBRA-RATIONALE" in prompt) == (0, True, False)


def test_main_ends_every_phases_verify_prompt_with_the_output_contract_fragment_exactly_once_3621(
        tmp_path, capsysbinary, build_verify_prompt):
    spec, ledger = tmp_path / "spec.md", tmp_path / "ledger.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    ledger.write_bytes("# Plan for #3621\n\n- [ ] zorblat frobs a nitz ⟦criterion 1⟧\n".encode())
    s, sha, fast, test = str(spec), "0123abc", ["--fast-cmd", "make unit"], "tests/py/test_zorblat.py"
    argvs = {
        "red": ["red", s, test, "zorblat frobs a nitz"],
        "green": [*fast, "green", s, test, "zorblat frobs a nitz"],
        "refactor": [*fast, "refactor", s, test, sha],
        "pin": ["--branch-base", "3f9a1c0", "pin", s, test, "zorblat frobs a nitz"],
        "plan": ["plan", s, str(ledger)],
        "rebase": ["rebase", s, sha, "4567def"],
        "transform": ["--fast-cmd", "m", "transform", s, str(tmp_path / "predicate.md"), sha],
        "diff": ["--step", "zorblat frobs a nitz", *fast, "--branch-base", sha, "diff", s, "4567def"],
        **{phase: [*fast, phase, s, test, sha]
           for phase in ("expand", "cover-new", "migrate", "contract-a", "contract-b", "beside", "dual-stub")},
    }
    fragment = (SCRIPTS / "prompts" / "_verify-output-contract.md").read_bytes().rstrip(b"\n")

    def verdict(argv):
        code = build_verify_prompt.main(argv)
        out, _ = capsysbinary.readouterr()
        return code, out.rstrip(b"\n").endswith(fragment), out.count(fragment)

    assert {phase: verdict(argv) for phase, argv in argvs.items()} == dict.fromkeys(argvs, (0, True, 1))


TOUCHING = "### Test cases touching the files the plan names"


def touching_section(out):
    if TOUCHING not in out:
        return None
    return out.split(TOUCHING, 1)[1].split("\n### ", 1)[0]


def plan_in_tree(tmp_path, run_cli, module, files, steps, env=None):
    for rel, text in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(SPEC_TEXT)
    ledger = tmp_path / ".tdd" / "issue-1.md"
    ledger.parent.mkdir(exist_ok=True)
    ledger.write_text("# Plan for #1\n\n" + "".join(f"- [ ] {step} ⟦criterion 1⟧\n" for step in steps))
    return run_cli(module, ["plan", str(spec_file), str(ledger)], env=env, cwd=tmp_path)


ROUTE_TREE = {
    "scripts/route.py": "def route():\n    return None\n",
    "tests/test_route.py": ("import route\n\n\ndef test_route_answers():\n    assert route.route() is None\n\n\n"
                            "def test_route_refuses():\n    CASE_BODY_MARKER = 1\n"),
}


def test_3919_plan_lists_after_the_ledger_the_case_names_of_a_test_file_holding_the_stem_of_a_path_a_step_names(
        tmp_path, run_cli, build_verify_prompt):
    code, out, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, ROUTE_TREE,
                                ["the router answers through scripts/route.py"])
    section = touching_section(out)

    assert (code, section is not None) == (0, True)
    assert out.index("scripts/route.py ⟦criterion 1⟧") < out.index(TOUCHING)
    assert ("tests/test_route.py" in section, "test_route_answers" in section, "test_route_refuses" in section,
            "CASE_BODY_MARKER" in section) == (True, True, True, False)


def test_3919_plan_lists_the_cases_touching_a_file_a_step_names_by_its_basename_alone(
        tmp_path, run_cli, build_verify_prompt):
    code, out, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, ROUTE_TREE,
                                ["the router answers through `route.py`."])
    section = touching_section(out) or ""

    assert (code, "tests/test_route.py" in section, "test_route_answers" in section) == (0, True, True)


def test_3919_plan_counts_dash_and_underscore_alike_so_a_step_naming_wrong_test_route_sh_lists_a_file_mentioning_wrong_test_route(
        tmp_path, run_cli, build_verify_prompt):
    tree = {"scripts/wrong-test-route.sh": "exit 0\n",
            "tests/test_reroute.py": "from veri import wrong_test_route\n\n\ndef test_reroutes_once():\n    pass\n"}
    code, out, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, tree,
                                ["wrong-test-route.sh answers prep after the free reroute"])
    section = touching_section(out) or ""

    assert (code, "tests/test_reroute.py" in section, "test_reroutes_once" in section) == (0, True, True)


def test_3919_plan_lists_no_case_of_a_test_file_holding_the_stem_only_inside_a_longer_word(
        tmp_path, run_cli, build_verify_prompt):
    tree = {"scripts/route.py": "def route():\n    return None\n",
            "tests/test_router.py": "import router\n\n\ndef test_router_routes():\n    assert router.routes\n"}
    code, out, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, tree, ["route.py answers"])
    section = touching_section(out)

    assert (code, section is not None, "test_router_routes" in (section or "")) == (0, True, False)


NO_TOUCHING = "No test case touches a file the plan names."


def test_3919_plan_section_is_the_one_no_case_line_when_no_step_names_a_file_or_no_test_file_touches_one(
        tmp_path, run_cli, build_verify_prompt):
    renders = {}
    for name, steps in (("names-none", ["the router answers"]), ("touched-by-none", ["helper.py answers"])):
        files = dict(ROUTE_TREE, **{"scripts/helper.py": "pass\n"})
        code, out, _ = plan_in_tree(tmp_path / name, run_cli, build_verify_prompt, files, steps)
        renders[name] = (code, (touching_section(out) or "").strip())

    assert renders == dict.fromkeys(renders, (0, NO_TOUCHING))


def route_cases(*names):
    return "import route\n" + "".join(f"\n\ndef {name}():\n    pass\n" for name in names)


def test_3919_plan_lists_at_most_veri_plan_touching_cases_names_default_100_then_one_more_cases_line_per_file_left_over(
        tmp_path, run_cli, build_verify_prompt):
    small = {"scripts/route.py": "pass\n",
             "tests/test_a.py": route_cases("test_a1", "test_a2"),
             "tests/test_b.py": route_cases("test_b1", "test_b2", "test_b3"),
             "tests/test_c.py": route_cases("test_c1")}
    big = {"scripts/route.py": "pass\n", "tests/test_many.py": route_cases(*(f"test_n{i}" for i in range(101)))}
    _, default, _ = plan_in_tree(tmp_path / "default", run_cli, build_verify_prompt, big, ["route.py answers"])
    _, capped, _ = plan_in_tree(tmp_path / "capped", run_cli, build_verify_prompt, small, ["route.py answers"],
                                env={"VERI_PLAN_TOUCHING_CASES": "3"})

    def listed(out):
        section = touching_section(out) or ""
        return (sorted(set(re.findall(r"\btest_[abc]\d\b|\btest_n\d+\b", section))),
                [line for line in section.splitlines() if "more cases" in line])

    assert listed(capped) == (["test_a1", "test_a2", "test_b1"],
                              ["tests/test_b.py: 2 more cases", "tests/test_c.py: 1 more cases"])
    assert (len(listed(default)[0]), listed(default)[1]) == (100, ["tests/test_many.py: 1 more cases"])


def test_3919_plan_refuses_a_veri_plan_touching_cases_that_is_not_a_whole_number_free_text_included_with_exit_2_one_line_naming_it_and_no_prompt(
        tmp_path, run_cli, build_verify_prompt):
    smuggled = "100 RATIONALE-LEAK the developer chose a launcher because bash -c broke the quoting"
    results = {}
    for value in ("abc", "-1", "1.5", " 7", smuggled):
        code, out, err = plan_in_tree(tmp_path / str(len(results)), run_cli, build_verify_prompt, ROUTE_TREE,
                                      ["route.py answers"], env={"VERI_PLAN_TOUCHING_CASES": value})
        results[value] = (code, out, len(err.splitlines()), "VERI_PLAN_TOUCHING_CASES" in err)

    assert results == dict.fromkeys(results, (2, "", 1, True))


def test_3919_plan_lists_no_case_of_a_touching_test_file_under_dot_git_dot_tdd_dot_venv_or_node_modules(
        tmp_path, run_cli, build_verify_prompt):
    hidden = {f"{where}/tests/test_route.py": route_cases(f"test_hidden_in_{where.strip('.').replace('/', '_')}")
              for where in (".git", ".tdd", ".venv", "node_modules", "pkg/node_modules")}
    tree = dict(hidden, **{"scripts/route.py": "pass\n", "tests/test_route.py": route_cases("test_listed")})
    code, out, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, tree, ["route.py answers"])
    section = touching_section(out) or ""

    assert (code, "test_listed" in section, re.findall(r"test_hidden_in_\w+", section)) == (0, True, [])


def test_3919_verify_plan_carries_no_tdd_file_naming_a_steps_file_no_step_text_and_no_fourth_positional_through_the_touching_cases(
        tmp_path, run_cli, build_verify_prompt):
    files = dict(ROUTE_TREE, **{".tdd/tests/test_route_reason.py": (
        "import route\n\n\ndef test_RATIONALE_LEAK_route_was_kept_because_bash_c_broke_the_quoting():\n"
        "    'RATIONALE-LEAK-MARKER the developer chose a launcher script'\n")})
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    ledger = tmp_path / ".tdd" / "issue-1.md"
    ledger.write_text("# Plan for #1\n\n- [ ] route.py answers ⟦criterion 1⟧\n")
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(SPEC_TEXT)

    code, out, _ = run_cli(build_verify_prompt, ["--step", "STEP-LEAK the developer reasoned about quoting", "plan",
                                                 str(spec_file), str(ledger), "test_positional_leak"], cwd=tmp_path)
    section = touching_section(out) or ""

    assert (code, "test_route_answers" in section) == (0, True)
    assert [leak for leak in ("RATIONALE", "STEP-LEAK", "test_positional_leak") if leak in out] == []


def test_3919_plan_still_renders_when_a_touching_test_file_cannot_be_read_or_holds_a_case_call_that_never_closes(
        tmp_path, run_cli, build_verify_prompt):
    tree = dict(ROUTE_TREE, **{"tests/route.test.js": "const route = require('route')\nit('never closes', () => {\n"})
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_gone.py").symlink_to(tmp_path / "nowhere.py")
    code, out, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, tree, ["route.py answers"])
    section = touching_section(out) or ""

    assert (code, "test_route_answers" in section, "never closes" in section) == (0, True, False)


def test_3919_plan_lists_only_test_files_git_tracks_not_an_untracked_one_nor_one_in_a_gitignored_directory(
        tmp_path, run_cli, build_verify_prompt, fake_processes):
    tree = dict(ROUTE_TREE, **{"tests/test_untracked.py": route_cases("test_untracked_case"),
                               "build/tests/test_ignored.py": route_cases("test_ignored_case"),
                               ".gitignore": "build/\n"})
    fake_processes.answers({"git ls-files": (0, "scripts/route.py\0tests/test_route.py\0.gitignore\0", "")})
    code, out, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, tree, ["route.py answers"])
    section = touching_section(out) or ""

    assert (code, "test_route_answers" in section, re.findall(r"test_(?:untracked|ignored)_case", section)) == (
        0, True, [])


def test_3919_plan_exits_2_with_one_stderr_line_naming_git_ls_files_and_no_prompt_when_git_ls_files_fails(
        tmp_path, run_cli, build_verify_prompt, fake_processes):
    fake_processes.answers({"git ls-files": (128, "", "fatal: not a git repository\n")})
    code, out, err = plan_in_tree(tmp_path, run_cli, build_verify_prompt, ROUTE_TREE, ["route.py answers"])

    assert (code, out, len(err.splitlines()), "build-verify-prompt:" in err, "git ls-files" in err,
            "not a git repository" in err) == (2, "", 1, True, True, True)


def test_3919_plan_never_follows_a_test_file_that_is_a_symbolic_link_to_a_file_outside_the_repository(
        tmp_path, run_cli, build_verify_prompt):
    outside = tmp_path / "outside" / "test_elsewhere.py"
    outside.parent.mkdir()
    outside.write_text(route_cases("test_outside_case"))
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_linked.py").symlink_to(outside)
    code, out, _ = plan_in_tree(repo, run_cli, build_verify_prompt, ROUTE_TREE, ["route.py answers"])
    section = touching_section(out) or ""

    assert (code, "test_route_answers" in section, "test_outside_case" in section) == (0, True, False)


def test_3919_plan_states_each_touching_test_file_whose_cases_it_cannot_read_within_the_cap_and_never_then_says_no_case_touches(
        tmp_path, run_cli, build_verify_prompt, fake_processes):
    tree = {"scripts/route.py": "pass\n",
            "tests/route_test.rs": "use route;\n\n#[test]\nfn routes() {}\n",
            "tests/route.test.js": "const route = require('route')\nit('never closes', () => {\n",
            "tests/conftest.py": "import route\n"}
    tracked = "scripts/route.py\0tests/route_test.rs\0tests/route.test.js\0tests/conftest.py\0tests/test_gone.py\0"
    fake_processes.answers({"git ls-files": (0, tracked, "")})
    _, whole, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, tree, ["route.py answers"])
    _, capped, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, tree, ["route.py answers"],
                                env={"VERI_PLAN_TOUCHING_CASES": "1"})

    def stated(out):
        section = touching_section(out) or ""
        return [line for line in section.splitlines() if "not readable" in line], NO_TOUCHING in section

    assert stated(whole) == (["tests/route.test.js: cases not readable", "tests/route_test.rs: cases not readable",
                              "tests/test_gone.py: cases not readable"], False)
    assert stated(capped) == (["tests/route.test.js: cases not readable",
                               "2 more test files whose cases are not readable"], False)


def test_3919_plan_lists_first_the_files_touching_a_path_a_step_gives_in_full_then_by_hits_then_alphabetically(
        tmp_path, run_cli, build_verify_prompt):
    tree = {"skills/tdd/SCRIPTS.md": "# scripts\n", "scripts/build-verify-prompt.sh": "exit 0\n",
            "skills/x/route.py": "pass\n",
            "tests/test_y_bvp.py": ("from veri import build_verify_prompt\n" + "build_verify_prompt.main\n" * 4
                                    + "\n\ndef test_bvp_case():\n    pass\n"),
            "tests/test_z_route.py": "import route\n\n\ndef test_route_case():\n    pass\n",
            **{f"tests/test_a{i}_process.py": f"SCRIPTS = 1\n\n\ndef test_a{i}_case():\n    pass\n" for i in range(10)}}
    code, out, _ = plan_in_tree(tmp_path, run_cli, build_verify_prompt, tree,
                                ["SCRIPTS.md's build-verify-prompt.sh entry names skills/x/route.py"],
                                env={"VERI_PLAN_TOUCHING_CASES": "3"})
    section = touching_section(out) or ""

    assert (code, re.findall(r"^tests/\S+\.py$", section, re.M)) == (
        0, ["tests/test_z_route.py", "tests/test_y_bvp.py", "tests/test_a0_process.py"])


def test_4106_plan_fills_the_legacy_slot_with_the_legacy_fragment_for_a_legacy_spec_alone_and_with_no_new_input(
        tmp_path, spec, run_cli, build_verify_prompt):
    ledger = tmp_path / "ledger.md"
    ledger.write_text("# Plan for #4106\n\n- [ ] wrap the parser ⟦phases: seam,surround⟧ ⟦criterion 1⟧\n")
    legacy_spec = tmp_path / "legacy-spec.md"
    legacy_spec.write_text(open(spec).read() + "\n## Legacy\n\nRun kind: legacy.\n")
    refactor_spec = tmp_path / "refactor-spec.md"
    refactor_spec.write_text(open(spec).read() + "\n## Refactor\n\nRun kind: refactor.\n")
    fragment = (SCRIPTS / "prompts" / "_verify-plan-legacy.md").read_text().strip()

    outs = {name: run_cli(build_verify_prompt, ["plan", str(path), str(ledger)])
            for name, path in (("legacy", legacy_spec), ("plain", spec), ("refactor", refactor_spec))}

    assert {name: (code, fragment in out, "{{LEGACY_PLAN}}" in out) for name, (code, out, _) in outs.items()} == {
        "legacy": (0, True, False), "plain": (0, False, False), "refactor": (0, False, False)}


def test_4107_surround_renders_verify_surround_md_from_the_pin_phase_s_inputs_alone_and_refuses_any_other_with_exit_2(
        tmp_path, spec, run_cli, build_verify_prompt):
    step = "wrap parse() in src/parse.py:10-80 through bin/parse \u27e6phases: seam,surround\u27e7 \u27e6criterion 1\u27e7"
    pin_inputs = ["--branch-base", "3f9a1c0", "surround", str(spec), "tests/test_parse_cli.py"]

    def render(argv):
        code, out, err = run_cli(build_verify_prompt, argv)
        return code, "## Phase: verify-surround" in out, "3f9a1c0" in out, err

    rendered = {"pin's inputs": render(pin_inputs),
                "pin's inputs and a target": render(pin_inputs + ["test_parse_prints_the_tree"]),
                "pin's inputs and its step": render(["--step", step] + pin_inputs)}
    refused = {name: run_cli(build_verify_prompt, argv)[::2] for name, argv in {
        "no branch base": ["surround", str(spec), "tests/test_parse_cli.py"],
        "a fast command": ["--fast-cmd", "make unit"] + pin_inputs,
        "a supersede base": ["--supersede-base", "3f9a1c0"] + pin_inputs,
        "a ledger": ["--ledger", str(tmp_path / "ledger.md")] + pin_inputs,
        "an extra positional": pin_inputs + ["test_parse_prints_the_tree", "extra"],
    }.items()}

    assert rendered == {name: (0, True, True, "") for name in rendered}
    assert {name: (code, "surround" in err or "too many" in err) for name, (code, err) in refused.items()} == {
        name: (2, True) for name in refused}


LINT_STEP = "make `ruff check .` pass: E501 line too long ⟦diff-checked⟧ ⟦lint-repair⟧ ⟦added⟧ ⟦criterion 2⟧"


def lint_render(tmp_path, monkeypatch, run_cli, build_verify_prompt, step, claude_md=b"veri: lint: `ruff check --quiet .`\n", env=None):
    repo = tmp_path / "repo"
    repo.mkdir(exist_ok=True)
    if claude_md is not None:
        (repo / "CLAUDE.md").write_bytes(claude_md)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"the spec\n")
    monkeypatch.chdir(repo)
    return run_cli(build_verify_prompt, ["--step", step, "--fast-cmd", "make unit", "--branch-base", "0123abc", "diff", str(spec), "4567def"],
                   env=env)


def test_4123_a_lint_repair_diff_prompt_names_the_declared_lint_command_and_tells_the_verifier_to_run_it(
        tmp_path, monkeypatch, run_cli, build_verify_prompt):
    code, out, err = lint_render(tmp_path, monkeypatch, run_cli, build_verify_prompt, LINT_STEP)

    words = " ".join(out.split())
    assert (code, err) == (0, "")
    assert "Run the repo's declared lint command, `ruff check --quiet .`," in words
    assert "REJECT, naming its first finding, while it exits non-zero" in words
    assert "{{" not in out


def test_4123_a_diff_prompt_for_a_step_without_the_lint_repair_mark_names_no_lint_command(
        tmp_path, monkeypatch, run_cli, build_verify_prompt):
    for step in ("the dead line is gone ⟦diff-checked⟧ ⟦criterion 2⟧",
                 "explain why ⟦lint-repair⟧ ends a lint repair step ⟦diff-checked⟧ ⟦criterion 2⟧"):
        code, out, err = lint_render(tmp_path, monkeypatch, run_cli, build_verify_prompt, step)

        assert (code, err, "ruff check --quiet ." in out, "declared lint command" in out, "{{" in out) == (
            0, "", False, False, False), step


def test_4123_a_lint_repair_diff_prompt_with_no_declared_lint_command_exits_2_printing_nothing(
        tmp_path, monkeypatch, run_cli, build_verify_prompt):
    for claude_md in (None, b"veri: all tests: make test\n"):
        code, out, err = lint_render(tmp_path, monkeypatch, run_cli, build_verify_prompt, LINT_STEP, claude_md=claude_md)

        assert (code, out) == (2, ""), claude_md
        assert err == ("build-verify-prompt: a lint-repair step needs the repo's declared lint command, and its CLAUDE.md"
                       " declares no `veri: lint:` line\n")


def test_4123_build_verify_prompt_keeps_its_usage_line_and_options_and_reads_the_lint_command_from_no_environment(
        tmp_path, monkeypatch, run_cli, build_verify_prompt):
    assert build_verify_prompt.USAGE.encode() + b"\n" == USAGE
    _, plain, _ = lint_render(tmp_path, monkeypatch, run_cli, build_verify_prompt, LINT_STEP)
    ambient = {name: "echo injected" for name in ("VERI_LINT", "VERI_LINT_CMD", "LINT", "LINT_CMD", "VERI_LINT_COMMAND")}
    _, with_env, _ = lint_render(tmp_path, monkeypatch, run_cli, build_verify_prompt, LINT_STEP, env=ambient)
    code, out, err = run_cli(build_verify_prompt, ["--lint", "echo injected", "--step", LINT_STEP, "--fast-cmd", "m",
                                                   "--branch-base", "0123abc", "diff", str(tmp_path / "spec.md"), "4567def"])

    assert (with_env == plain, "injected" in with_env, code, out) == (True, False, 2, "")


def test_4111_break_renders_verify_break_md_given_a_hex_base_sha_and_exits_2_for_any_other_value(
        spec, run_cli, build_verify_prompt):
    step = "wrap parse() in src/parse.py:10-80 through bin/parse \u27e6phases: seam,surround\u27e7 \u27e6criterion 1\u27e7"

    def run(*argv):
        code, out, err = run_cli(build_verify_prompt, ["--step", step, "--fast-cmd", "make unit", *argv])
        return code, "## Phase: verify-break" in out, argv[-1] in out if code == 0 else argv[-1] in err

    rendered = {sha: run("break", str(spec), "src/parse.py", sha) for sha in ("3f9a1c0", "3f9a1c0" * 5 + "abcde")}
    refused = {sha: run("break", str(spec), "src/parse.py", sha)[0]
               for sha in ("3f9a1c", "3F9A1C0", "3f9a1c0g", "HEAD", "3f9a1c0 ", "a" * 41)}
    no_sha = run_cli(build_verify_prompt, ["--fast-cmd", "make unit", "break", str(spec), "src/parse.py"])[0]

    assert rendered == {sha: (0, True, True) for sha in rendered}
    assert (refused, no_sha) == ({sha: 2 for sha in refused}, 2)
    assert ("break" in build_verify_prompt.PHASES, build_verify_prompt.NEEDS.get("break")) == (True, {"fast-cmd", "base-sha"})


def test_main_renders_the_branch_prompt_with_exit_0_from_the_branch_diff_the_spec_and_the_fast_command_and_no_ambient_input(
        tmp_path, monkeypatch, capsysbinary, build_verify_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b'zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux".\n')
    fast = 'make unit ZORBLAT=branch -- --only "frob & nitz/quux"'
    monkeypatch.setenv("VERI_STEP", "I tidied the helper because it was ugly")
    monkeypatch.setenv("VERI_RATIONALE", "the author meant well")

    code = build_verify_prompt.main(["--fast-cmd", fast, "--branch-base", "0123abcdef", "branch", str(spec)])
    out, err = capsysbinary.readouterr()
    assert (code, err) == (0, b"")
    assert (b"git diff 0123abcdef..HEAD" in out, b'zorblat("Frob & Nitz/Quux")' in out, fast.encode() in out,
            b"{{" in out, b"tidied the helper" in out, b"the author meant well" in out) == (
        True, True, True, False, False, False)


def test_main_reads_the_branch_prompts_named_spec_rows_at_the_branch_base_not_at_head(
        tmp_path, monkeypatch, capsysbinary, fake_processes, build_verify_prompt):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "specs").mkdir()
    (tmp_path / "specs" / "prd-zz.md").write_bytes(b"| ZZ1 | the HEAD wording leaf-edited-it |\n")
    spec = tmp_path / "issue.md"
    spec.write_bytes(b"Frob must nitz.\n\nSpec: specs/prd-zz.md , rows ZZ1\n")
    at_base = b"| ZZ1 | the base wording predates the run |\n"

    def show(line, **_):
        return (0, at_base.decode(), "") if line.endswith(":specs/prd-zz.md") or line.endswith(":./specs/prd-zz.md") else (1, "", "")

    fake_processes.answers({"git ls-files": every_file_tracked, "git show": show}, default=(0, "", ""))
    code = build_verify_prompt.main(["--fast-cmd", "make unit", "--branch-base", "0123abcdef", "branch", str(spec)])
    out, _ = capsysbinary.readouterr()

    assert (code, b"the base wording predates the run" in out, b"leaf-edited-it" in out) == (0, True, False)
