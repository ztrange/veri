"""In-process cases for veri/go_red_step.py, the module go-red-step.sh is a shim over (#4443)."""
import importlib
import os

import pytest

FILE = "src/run.py"
CASE = "tests/test_run.py::test_refuses_stacked"
STEP = ("Go-red guard: the stacked refusal, probe `%s` `if stacked:` → `if False:` on `%s` ⟦go-red⟧ ⟦criterion 3⟧"
        % (FILE, CASE))
LEDGER = "# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n"
SOURCE = "if stacked:\n    raise SystemExit(2)\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout); <during_probe>, when given, runs as mutation-probe.sh."""

    def __init__(self, answers=None, during_probe=None):
        self.answers, self.calls, self.during_probe = dict(answers or {}), [], during_probe

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        if base == "mutation-probe.sh" and self.during_probe:
            self.during_probe()
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "detect-test-command.sh":
            return 0, "make test TESTS=\"$1\"\n", ""
        if base == "step-tick.sh":
            return 0, "tick-ledger.sh .tdd/issue-12.md exit 0\nnext=cycle\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def go_red(monkeypatch, run_cli, tmp_path):
    """go_red(answers=None, fake=None, step=STEP, argv=("12",), during_probe=None) runs go-red-step for issue 12 from
    the main tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    module = importlib.import_module("veri.go_red_step")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / "src").mkdir()

    def go(answers=None, fake=None, step=STEP, argv=("12",), during_probe=None, ledger=True, source=True):
        files = {(wt / ".tdd" / "issue-12-preflight"): "worktree=%s\nfast_cmd=make unit\n" % wt,
                 (wt / FILE): SOURCE}
        if not source:
            del files[wt / FILE]
        if ledger:
            files[wt / ".tdd" / "issue-12.md"] = LEDGER % step
        for path, text in files.items():
            if not path.exists():
                path.write_text(text)
        fake = fake or Fake(answers, during_probe)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(module, list(argv), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4443_a_go_red_step_probes_its_named_case_into_the_runs_mutation_record_then_ticks_through_step_tick(go_red):
    code, out, err, fake = go_red()

    assert code == 0, err
    assert fake.names() == ["detect-test-command.sh", "mutation-probe.sh", "step-tick.sh"]
    assert fake.call("detect-test-command.sh")[1] == ("--tier", "one test file")
    probe = fake.call("mutation-probe.sh")
    assert probe[1] == (FILE, "if stacked:", "if False:", "--", "sh", "-c", 'make test TESTS="$1"', "sh", CASE)
    assert probe[2] == str(go_red.wt)
    assert probe[3]["VERI_MUTATION_RECORD"] == ".tdd/issue-12-mutations.md"
    assert fake.call("step-tick.sh")[1] == ("12",)
    assert out.splitlines()[-1] == "next=cycle"


def test_4443_bad_arguments_a_missing_ledger_no_open_go_red_step_or_a_step_naming_no_probe_exit_2_probing_nothing(
        go_red):
    usage = "usage: go-red-step.sh <n>\n"
    cases = [({"argv": ()}, usage), ({"argv": ("x",)}, usage),
             ({"ledger": False}, "go-red-step.sh: no .tdd/issue-12.md\n"),
             ({"step": STEP.replace(" ⟦go-red⟧", "")}, "go-red-step.sh: no open ⟦go-red⟧ step in .tdd/issue-12.md\n"),
             ({"step": "Go-red guard: probe `src/run.py` on nothing ⟦go-red⟧ ⟦criterion 3⟧"},
              "go-red-step.sh: the open ⟦go-red⟧ step names no probe `<file>` `<old>` → `<new>` on `<case>`\n")]
    results = []
    for kw, _ in cases:
        ledger = go_red.wt / ".tdd" / "issue-12.md"
        if ledger.exists():
            ledger.unlink()
        code, out, err, fake = go_red(**kw)
        results.append((code, err, fake.names()))

    assert results == [(2, said, []) for _, said in cases]


def test_4443_with_no_one_test_file_command_or_a_detect_2_it_stops_with_exit_2_probing_and_ticking_nothing(go_red):
    results = []
    for detected in (3, 2):
        code, out, err, fake = go_red(answers={("detect-test-command.sh", "--tier"): (detected, "")})
        results.append((code, fake.names(), out.splitlines()[-1].split(" ")[:3]))

    assert results == [(2, ["detect-test-command.sh"], ["stopped", "at", "probe"])] * 2
    code, out, err, fake = go_red(answers={("detect-test-command.sh", "--tier"): (3, "")})
    assert "go-red-step.sh: no `veri: one test file:` line" in err


def test_4443_a_probe_that_sees_no_red_stops_with_exit_1_and_ticks_nothing(go_red):
    code, out, err, fake = go_red(answers={("mutation-probe.sh", None): (1, "")})

    assert (code, "step-tick.sh" in fake.names()) == (1, False)
    assert out.splitlines()[-1].startswith("stopped at probe ")


def test_4480_a_missing_named_file_is_left_to_the_probes_exit_2_and_stops_at_probe_with_exit_2(go_red):
    code, out, err, fake = go_red(answers={("mutation-probe.sh", None): (2, "")}, source=False)

    assert (code, "step-tick.sh" in fake.names(), out.splitlines()[-1]) == (
        2, False, "stopped at probe mutation-probe.sh exit 2")


def test_4443_a_probe_exit_2_or_a_named_file_left_unrestored_stops_with_exit_2_and_ticks_nothing(go_red):
    results = []
    code, out, err, fake = go_red(answers={("mutation-probe.sh", None): (2, "")})
    results.append((code, "step-tick.sh" in fake.names(), out.splitlines()[-1]))
    left = go_red.wt / FILE
    code, out, err, fake = go_red(during_probe=lambda: left.write_text("if False:\n    raise SystemExit(2)\n"))
    results.append((code, "step-tick.sh" in fake.names(), out.splitlines()[-1].split(" ")[:3]))

    assert results == [
        (2, False, "stopped at probe mutation-probe.sh exit 2"),
        (2, False, ["stopped", "at", "restore"]),
    ]


def test_4443_a_failing_step_tick_is_never_exit_0_and_leaves_the_step_unticked(go_red):
    code, out, err, fake = go_red(answers={("step-tick.sh", None): (2, "")})

    assert (code, out.splitlines()[-1].split(" ")[:3]) == (2, ["stopped", "at", "tick"])
    assert (go_red.wt / ".tdd" / "issue-12.md").read_text() == LEDGER % STEP


@pytest.mark.parametrize("ticked", [1, 3])
def test_4443_any_step_tick_exit_but_0_is_exit_2_never_1_which_only_a_green_case_answers(go_red, ticked):
    code, out, err, fake = go_red(answers={("step-tick.sh", None): (ticked, "")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at tick step-tick.sh 12 exit %d" % ticked)


def test_4443_an_empty_new_text_parses_and_is_probed_as_a_deletion(go_red):
    code, out, err, fake = go_red(step=STEP.replace("→ `if False:`", "→ ``"))

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][:4] == (FILE, "if stacked:", "", "--")


def test_4443_the_probes_stdout_goes_to_go_red_probe_out_under_the_worktree(go_red):
    code, out, err, fake = go_red()

    probe = fake.call("mutation-probe.sh")
    assert (probe[2], probe[4].get("out")) == (str(go_red.wt), ".tdd/go-red-probe.out")


def test_4480_a_probe_whose_old_text_is_gone_is_named_as_stale_not_plumbing(go_red):
    (go_red.wt / FILE).write_text("if not waiting and stacked_now:\n    raise SystemExit(2)\n")

    code, out, err, fake = go_red(answers={("mutation-probe.sh", None): (2, "")})

    assert code == 1, out
    assert "mutation-probe.sh" not in fake.names() and "step-tick.sh" not in fake.names()
    assert out.splitlines()[-1] == "stopped at probe src/run.py no longer holds `if stacked:`"


def test_4628_a_case_the_test_file_holds_only_under_the_red_leafs_issue_number_prefix_is_the_one_probed(go_red):
    (go_red.wt / "tests").mkdir()
    (go_red.wt / "tests" / "test_run.py").write_text("def test_4605_refuses_stacked():\n    pass\n")

    code, out, err, fake = go_red()

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "tests/test_run.py::test_4605_refuses_stacked"


def test_4628_a_case_the_test_file_defines_itself_is_probed_unchanged_beside_a_prefixed_twin(go_red):
    (go_red.wt / "tests").mkdir()
    (go_red.wt / "tests" / "test_run.py").write_text(
        "def test_refuses_stacked():\n    pass\n\n\ndef test_4605_refuses_stacked():\n    pass\n")

    code, out, err, fake = go_red()

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == CASE


def test_4628_a_case_the_test_file_holds_under_two_issue_number_prefixes_is_probed_unchanged_never_guessed(go_red):
    (go_red.wt / "tests").mkdir()
    (go_red.wt / "tests" / "test_run.py").write_text(
        "def test_4605_refuses_stacked():\n    pass\n\n\ndef test_4606_refuses_stacked():\n    pass\n")

    code, out, err, fake = go_red()

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == CASE


def test_4628_a_committed_case_that_only_extends_the_ledgers_name_is_not_taken_as_its_renamed_case(go_red):
    (go_red.wt / "tests").mkdir()
    (go_red.wt / "tests" / "test_run.py").write_text("def test_4605_refuses_stacked_extra():\n    pass\n")

    code, out, err, fake = go_red()

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == CASE


def test_4626_a_bare_test_function_name_is_probed_through_the_test_file_that_defines_it(go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "foo_test.go").write_text("package pkg\n\nfunc TestFoo(t *testing.T) {\n}\n")
    step = STEP.replace(CASE, "TestFoo")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "pkg/foo_test.go"


def test_4626_a_case_id_with_a_double_colon_is_passed_unchanged_even_when_another_file_defines_the_name(go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "other_test.go").write_text("package pkg\n\nfunc test_refuses_stacked(t *testing.T) {\n}\n")

    code, out, err, fake = go_red()

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == CASE


def test_4626_a_case_naming_an_existing_path_is_passed_unchanged_never_sent_through_the_defining_file_lookup(go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "foo_test.go").write_text("package pkg\n")
    (go_red.wt / "notes_test.go").write_text("func pkg/foo_test.go\n")
    step = STEP.replace(CASE, "pkg/foo_test.go")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "pkg/foo_test.go"


@pytest.mark.parametrize("hidden", [".git", ".tdd"])
def test_4626_a_copy_defining_the_bare_name_under_git_or_tdd_is_not_a_defining_file_so_the_real_test_file_resolves(
        go_red, hidden):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "foo_test.go").write_text("package pkg\n\nfunc TestFoo(t *testing.T) {\n}\n")
    (go_red.wt / hidden).mkdir(exist_ok=True)
    (go_red.wt / hidden / "foo_test.go").write_text("package pkg\n\nfunc TestFoo(t *testing.T) {\n}\n")
    step = STEP.replace(CASE, "TestFoo")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "pkg/foo_test.go"


def test_4626_a_bare_name_only_a_longer_function_starts_with_is_defined_by_no_test_file_and_stops_at_probe_with_exit_2(
        go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "foo_test.go").write_text("package pkg\n\nfunc TestFooBar(t *testing.T) {\n}\n")
    step = STEP.replace(CASE, "TestFoo")

    code, out, err, fake = go_red(step=step)

    assert code == 2, out
    assert "no test file under the worktree defines the case TestFoo" in err
    assert "mutation-probe.sh" not in fake.names()


def test_4626_a_bare_name_resolves_to_the_file_defining_it_never_to_one_defining_only_a_longer_function(go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "a_test.go").write_text("package pkg\n\nfunc TestFoo(t *testing.T) {\n}\n")
    (go_red.wt / "pkg" / "b_test.go").write_text("package pkg\n\nfunc TestFooBar(t *testing.T) {\n}\n")
    step = STEP.replace(CASE, "TestFoo")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "pkg/a_test.go"


def test_4626_a_non_test_go_file_defining_the_bare_name_is_not_a_defining_file(go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "foo_test.go").write_text("package pkg\n\nfunc TestFoo(t *testing.T) {\n}\n")
    (go_red.wt / "pkg" / "helpers.go").write_text("package pkg\n\nfunc TestFoo(t *testing.T) {\n}\n")
    step = STEP.replace(CASE, "TestFoo")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "pkg/foo_test.go"


def test_4626_a_test_file_that_is_not_utf_8_is_skipped_never_raised_on_so_the_defining_file_resolves(go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "foo_test.go").write_text("package pkg\n\nfunc TestFoo(t *testing.T) {\n}\n")
    (go_red.wt / "pkg" / "x_test.go").write_bytes(b"package pkg\n\xff\xfe\x80 // not utf-8\n")
    step = STEP.replace(CASE, "TestFoo")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "pkg/foo_test.go"


def test_4626_a_bare_test_function_name_defined_by_no_test_file_stops_at_probe_with_exit_2_naming_the_case_probing_nothing(
        go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "foo_test.go").write_text("package pkg\n\nfunc TestOther(t *testing.T) {\n}\n")
    step = STEP.replace(CASE, "TestMissing")

    code, out, err, fake = go_red(step=step)

    assert code == 2, out
    assert "TestMissing" in err
    assert "mutation-probe.sh" not in fake.names()
    assert out.splitlines()[-1].startswith("stopped at probe ")


def test_4626_a_bare_test_function_name_defined_by_more_than_one_test_file_stops_at_probe_with_exit_2_naming_the_case_and_files(
        go_red):
    (go_red.wt / "pkg").mkdir()
    for name in ("a_test.go", "b_test.go"):
        (go_red.wt / "pkg" / name).write_text("package pkg\n\nfunc TestDup(t *testing.T) {\n}\n")
    step = STEP.replace(CASE, "TestDup")

    code, out, err, fake = go_red(step=step)

    assert code == 2, out
    assert "TestDup" in err
    assert "pkg/a_test.go" in err and "pkg/b_test.go" in err
    assert "mutation-probe.sh" not in fake.names()
    assert out.splitlines()[-1].startswith("stopped at probe ")


def test_4626_a_dangling_test_file_symlink_is_skipped_never_raised_on_so_the_defining_file_resolves(go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "foo_test.go").write_text("package pkg\n\nfunc TestFoo(t *testing.T) {\n}\n")
    (go_red.wt / "pkg" / "x_test.go").symlink_to(go_red.wt / "pkg" / "gone_test.go")
    step = STEP.replace(CASE, "TestFoo")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "pkg/foo_test.go"


def test_4626_a_test_file_that_only_calls_runs_or_mentions_the_case_is_not_a_defining_file(go_red):
    (go_red.wt / "pkg").mkdir()
    (go_red.wt / "pkg" / "foo_test.go").write_text("package pkg\n\nfunc TestFoo(t *testing.T) {\n}\n")
    (go_red.wt / "pkg" / "bar_test.go").write_text(
        "package pkg\n\n// TestFoo covers the same path.\nfunc TestBar(t *testing.T) {\n"
        "\tTestFoo(t)\n\tt.Run(\"TestFoo\", func(t *testing.T) {})\n}\n")
    step = STEP.replace(CASE, "TestFoo")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "pkg/foo_test.go"


def test_4719_a_node_test_case_title_is_probed_through_the_test_mjs_file_whose_test_call_names_it(go_red):
    title = "no component inlines the label-thinning formula"
    (go_red.wt / "site" / "test").mkdir(parents=True)
    (go_red.wt / "site" / "test" / "chart-geometry.test.mjs").write_text(
        "import { test } from \"node:test\";\n\ntest(\"%s\", () => {\n});\n" % title)
    step = STEP.replace(CASE, title)

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "site/test/chart-geometry.test.mjs"


def test_4719_a_bare_pytest_case_name_is_probed_through_the_test_py_file_whose_def_names_it(go_red):
    (go_red.wt / "tests").mkdir()
    (go_red.wt / "tests" / "test_chart.py").write_text("def test_thins_labels():\n    pass\n")
    step = STEP.replace(CASE, "test_thins_labels")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "tests/test_chart.py"


def test_4719_a_node_test_case_title_is_not_probed_through_a_test_mjs_file_whose_test_title_only_starts_with_it(go_red):
    title = "no component inlines the label-thinning formula"
    (go_red.wt / "site" / "test").mkdir(parents=True)
    (go_red.wt / "site" / "test" / "axis.test.mjs").write_text(
        "import { test } from \"node:test\";\n\ntest(\"%s and more\", () => {\n});\n" % title)
    (go_red.wt / "site" / "test" / "chart-geometry.test.mjs").write_text(
        "import { test } from \"node:test\";\n\ntest(\"%s\", () => {\n});\n" % title)
    step = STEP.replace(CASE, title)

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "site/test/chart-geometry.test.mjs"


def test_4719_a_bare_pytest_case_name_is_not_probed_through_a_test_py_file_defining_only_a_longer_name(go_red):
    (go_red.wt / "tests").mkdir()
    (go_red.wt / "tests" / "test_axis.py").write_text("def test_thins_labels_twice():\n    pass\n")
    (go_red.wt / "tests" / "test_chart.py").write_text("def test_thins_labels():\n    pass\n")
    step = STEP.replace(CASE, "test_thins_labels")

    code, out, err, fake = go_red(step=step)

    assert code == 0, err
    assert fake.call("mutation-probe.sh")[1][-1] == "tests/test_chart.py"
