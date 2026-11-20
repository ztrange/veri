"""In-process cases for veri/mutation_probe.py, the module mutation-probe.sh is a shim over."""
import importlib
import shlex

import pytest

from veri.mutation_record import records


@pytest.fixture
def mutation_probe():
    return importlib.import_module("veri.mutation_probe")


def red_under_mutation(fake_processes, target, seen=None):
    """Every command exits 0 while <target> holds its original bytes and 1 once it is mutated; <seen> gets the text it held."""
    original = target.read_bytes()

    def exit_code(line, **kwargs):
        if seen is not None:
            seen.append(target.read_text())
        return (0 if target.read_bytes() == original else 1, "", "")

    return fake_processes.answers({}, default=exit_code)


def test_main_with_no_argument_prints_the_usage_line_and_exits_2(run_cli, mutation_probe):
    code, out, err = run_cli(mutation_probe, [])
    assert code == 2
    assert out == ""
    assert "mutation-probe.sh <file> <old> <new> -- <command…>" in err


@pytest.mark.parametrize(
    "args",
    [[], ["alpha"], ["alpha", "beta"], ["alpha", "beta", "true"], ["alpha", "beta", "--"]],
    ids=["no args", "two args", "three args", "four args without --", "-- with no command"],
)
def test_main_refuses_a_malformed_call_with_the_usage_line_and_exit_2_leaving_the_file_alone(
    run_cli, mutation_probe, monkeypatch, tmp_path, args
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    writes = []
    monkeypatch.setattr(mutation_probe.Path, "write_bytes", lambda self, data: writes.append(self))
    argv = [str(target)] + args if args else []
    code, out, err = run_cli(mutation_probe, argv)
    assert code == 2
    assert out == ""
    assert "usage: mutation-probe.sh <file> <old> <new> -- <command…>" in err
    assert writes == []
    assert target.read_text() == "alpha\n"


def test_main_exits_2_without_running_the_command_when_the_edit_leaves_the_file_unchanged(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    fake = fake_processes.answers({})
    code, out, err = run_cli(mutation_probe, [str(target), "absent", "new", "--", "true"])
    assert code == 2
    assert fake.calls == []
    assert target.read_text() == "alpha\n"
    assert "not mutated" in err


def test_main_exits_1_naming_the_green_suite_when_the_command_still_passes_under_the_mutation(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    fake_processes.answers({}, default=(0, "", ""))
    code, out, err = run_cli(mutation_probe, [str(target), "alpha", "beta", "--", "true"])
    assert code == 1
    assert "stayed green under the mutation" in err


def test_main_leaves_the_file_byte_identical_and_no_copy_beside_it_when_the_suite_goes_red(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_bytes(b"alpha\r\nbeta\n")
    red_under_mutation(fake_processes, target)
    code, out, err = run_cli(mutation_probe, [str(target), "alpha", "gamma", "--", "false"])
    assert code == 0
    assert target.read_bytes() == b"alpha\r\nbeta\n"
    assert [p.name for p in tmp_path.iterdir()] == ["target.txt"]


def test_main_appends_file_old_new_and_command_with_their_newlines_to_the_record_when_it_exits_0_2506(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("head\nalpha\nbeta\ntail\n")
    record = tmp_path / "mutations.md"
    red_under_mutation(fake_processes, target)
    old, new, command = "alpha\nbeta", "gamma\ndelta\n", "check one\ntwo"
    code, out, err = run_cli(
        mutation_probe,
        [str(target), old, new, "--", command],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 0
    [fields] = records(record.read_text())
    assert (fields["file"], fields["old"], fields["new"], fields["command"]) == (str(target), old, new, shlex.quote(command))


def test_main_appends_nothing_to_the_record_when_the_command_stays_green_and_exits_1_2506(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    fake_processes.answers({}, default=(0, "", ""))
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "alpha", "beta", "--", "true"],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 1
    assert not record.exists() or record.read_text() == ""


def test_main_appends_nothing_to_the_record_when_the_file_was_not_mutated_and_exits_2_2506(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    red_under_mutation(fake_processes, target)
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "absent", "beta", "--", "true"],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 2
    assert not record.exists() or record.read_text() == ""


def test_main_records_a_bash_c_probe_with_its_script_as_one_quoted_word_2877(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    import shlex

    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    red_under_mutation(fake_processes, target)
    script = "pytest -k 'that shell's own job'"
    argv = ["bash", "-c", script]
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "alpha", "beta", "--", *argv],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 0
    lines = record.read_text().split("\n")
    command = lines[lines.index("command %d" % len(shlex.join(argv))) + 1]
    assert shlex.split(command) == argv


def test_main_records_only_the_test_command_when_the_probe_runs_through_timed_test_run_2877(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    import shlex
    from pathlib import Path

    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    red_under_mutation(fake_processes, target)
    wrapper = str(Path(mutation_probe.__file__).resolve().parent.parent / "timed-test-run.sh")
    test_command = ["make", "test", "TESTS=tests/py/unit/test_a.py tests/py/unit/test_b.py"]
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "alpha", "beta", "--", wrapper, "affected", "a suite", *test_command],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 0
    lines = record.read_text().split("\n")
    expected = shlex.join(test_command)
    assert lines[lines.index("command %d" % len(expected)) + 1] == expected


def test_main_recognises_the_wrapper_when_the_module_itself_is_reached_through_a_symlink_2919(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    import importlib.util
    import shlex
    from pathlib import Path

    link = tmp_path / "veri-link"
    link.symlink_to(Path(mutation_probe.__file__).resolve().parent)
    spec = importlib.util.spec_from_file_location("mutation_probe_via_symlink", link / "mutation_probe.py")
    via_link = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(via_link)
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    red_under_mutation(fake_processes, target)
    wrapper = str(Path(mutation_probe.__file__).resolve().parent.parent / "timed-test-run.sh")
    test_command = ["make", "test", "TESTS=tests/py/unit/test_a.py"]
    code, out, err = run_cli(
        via_link,
        [str(target), "alpha", "beta", "--", wrapper, "affected", "a suite", *test_command],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 0
    expected = shlex.join(test_command)
    lines = record.read_text().split("\n")
    assert lines[lines.index("command %d" % len(expected)) + 1] == expected


@pytest.mark.parametrize(
    "args",
    [
        ["--before", "abc1234", "--keep", "t.py", "--"],
        ["--before", "abc1234", "--nokeep", "t.py", "--", "true"],
        ["--before", "abc1234", "--keep", "t.py", "x", "true"],
    ],
    ids=["fewer than 6 arguments", "argv[2] not --keep", "argv[4] not --"],
)
def test_main_before_refuses_a_malformed_call_with_the_usage_line_and_exit_2_without_running_the_command_2900(
    run_cli, fake_processes, mutation_probe, monkeypatch, args
):
    fake = fake_processes.answers({})
    code, out, err = run_cli(mutation_probe, args)
    assert code == 2
    assert out == ""
    assert "usage: mutation-probe.sh --before <sha> --keep <test-path> -- <command…>" in err
    assert fake.calls == []


@pytest.mark.parametrize("env", [{}, {"VERI_MUTATION_ADDRESS_DOMAIN": ""}], ids=["unset", "empty"])
def test_main_accepts_and_records_an_outside_address_when_the_address_domain_is_unset_or_empty_3330(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path, env
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    calls = []
    red_under_mutation(fake_processes, target, seen=calls)
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "alpha", "x@outside.invalid", "--", "false"],
        env={"VERI_MUTATION_RECORD": str(record), **env},
    )
    assert code == 0
    assert calls[-1] == "x@outside.invalid\n"
    assert target.read_text() == "alpha\n"
    [fields] = records(record.read_text())
    assert fields["new"] == "x@outside.invalid"


@pytest.mark.parametrize("new", ["x@corp.invalid", "plain"], ids=["on-domain", "no-address"])
def test_main_accepts_and_records_an_on_domain_or_addressless_new_when_the_address_domain_is_set_3330(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path, new
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    calls = []
    red_under_mutation(fake_processes, target, seen=calls)
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "alpha", new, "--", "false"],
        env={"VERI_MUTATION_RECORD": str(record), "VERI_MUTATION_ADDRESS_DOMAIN": "corp.invalid"},
    )
    assert code == 0
    assert calls[-1] == new + "\n"
    assert target.read_text() == "alpha\n"
    [fields] = records(record.read_text())
    assert fields["new"] == new


def test_main_refuses_a_new_with_an_outside_address_when_the_address_domain_is_set_3330(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    record.write_text("before\n")
    fake = fake_processes.answers({}, default=(1, "", ""))
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "alpha", "x@outside.invalid", "--", "false"],
        env={"VERI_MUTATION_RECORD": str(record), "VERI_MUTATION_ADDRESS_DOMAIN": "corp.invalid"},
    )
    assert code == 2
    assert fake.calls == []
    assert target.read_bytes() == b"alpha\n"
    assert record.read_bytes() == b"before\n"
    assert "x@outside.invalid" in err
    assert "corp.invalid" in err


def test_main_refuses_an_old_with_an_outside_address_when_the_address_domain_is_set_3330(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("mail x@outside.invalid now\n")
    record = tmp_path / "mutations.md"
    record.write_text("before\n")
    fake = fake_processes.answers({}, default=(1, "", ""))
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "x@outside.invalid", "beta", "--", "false"],
        env={"VERI_MUTATION_RECORD": str(record), "VERI_MUTATION_ADDRESS_DOMAIN": "corp.invalid"},
    )
    assert code == 2
    assert fake.calls == []
    assert target.read_bytes() == b"mail x@outside.invalid now\n"
    assert record.read_bytes() == b"before\n"
    assert "x@outside.invalid" in err
    assert "corp.invalid" in err


def test_main_before_behaves_the_same_with_the_address_domain_set_and_unset_on_an_outside_address_3330(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    """Criterion 5: with VERI_MUTATION_ADDRESS_DOMAIN=corp.invalid the --before form behaves as with the key unset."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "f.txt").write_text("new\n")

    fake_processes.answers({
        "git rev-parse HEAD": (0, "cafe123\n", ""),
        "git rev-parse": (0, b"", ""),
        "git diff": (0, b"f.txt\0", ""),
        "git ls-files": (0, b"", ""),
        "git show": (0, b"old\n", ""),
        "echo x@outside.invalid": lambda line, **kwargs: (0 if (tmp_path / "f.txt").read_bytes() == b"new\n" else 1, "", ""),
    }, default=(1, "", ""))
    args = ["--before", "abc1234", "--keep", "t.py", "--", "echo", "x@outside.invalid"]
    outcomes = []
    for env in ({}, {"VERI_MUTATION_ADDRESS_DOMAIN": "corp.invalid"}):
        record = tmp_path / "mutations.md"
        record.write_text("")
        code, out, err = run_cli(mutation_probe, args, env={"VERI_MUTATION_RECORD": str(record), **env})
        outcomes.append((code, out, err, record.read_bytes(), (tmp_path / "f.txt").read_bytes()))
    assert outcomes[0][0] == 0
    assert b"x@outside.invalid" in outcomes[0][3]
    assert outcomes[0] == outcomes[1]


def test_main_records_the_full_source_line_holding_the_old_text_as_context_3331(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("head\n    if done: break  # stop\ntail\n")
    record = tmp_path / "mutations.md"
    red_under_mutation(fake_processes, target)
    line = "    if done: break  # stop"
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "break", "continue", "--", "check"],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 0
    [fields] = records(record.read_text())
    assert fields["context"] == line


def test_main_records_neither_the_old_nor_the_new_text_verbatim_context_included_3471(
    run_cli, fake_processes, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("head\nsee OLDMARKER3471 here\ntail\n")
    record = tmp_path / "mutations.md"
    red_under_mutation(fake_processes, target)
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "OLDMARKER3471", "NEWMARKER3471", "--", "check"],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 0
    data = record.read_bytes()
    assert b"OLDMARKER3471" not in data
    assert b"NEWMARKER3471" not in data
