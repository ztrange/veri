"""In-process cases for veri/mutation_probe.py, the module mutation-probe.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def mutation_probe():
    return importlib.import_module("veri.mutation_probe")


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
    run_cli, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    calls = []
    monkeypatch.setattr(mutation_probe.subprocess, "run", lambda *a, **k: calls.append(a))
    code, out, err = run_cli(mutation_probe, [str(target), "absent", "new", "--", "true"])
    assert code == 2
    assert calls == []
    assert target.read_text() == "alpha\n"
    assert "not mutated" in err


def test_main_exits_1_naming_the_green_suite_when_the_command_still_passes_under_the_mutation(
    run_cli, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    monkeypatch.setattr(
        mutation_probe.subprocess, "run", lambda *a, **k: mutation_probe.subprocess.CompletedProcess(a, 0)
    )
    code, out, err = run_cli(mutation_probe, [str(target), "alpha", "beta", "--", "true"])
    assert code == 1
    assert "stayed green under the mutation" in err


def test_main_leaves_the_file_byte_identical_and_no_copy_beside_it_when_the_suite_goes_red(
    run_cli, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_bytes(b"alpha\r\nbeta\n")
    monkeypatch.setattr(
        mutation_probe.subprocess, "run", lambda *a, **k: mutation_probe.subprocess.CompletedProcess(a, 1)
    )
    code, out, err = run_cli(mutation_probe, [str(target), "alpha", "gamma", "--", "false"])
    assert code == 0
    assert target.read_bytes() == b"alpha\r\nbeta\n"
    assert [p.name for p in tmp_path.iterdir()] == ["target.txt"]


def test_main_appends_file_old_new_and_command_with_their_newlines_to_the_record_when_it_exits_0_2506(
    run_cli, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("head\nalpha\nbeta\ntail\n")
    record = tmp_path / "mutations.md"
    monkeypatch.setattr(
        mutation_probe.subprocess, "run", lambda *a, **k: mutation_probe.subprocess.CompletedProcess(a, 1)
    )
    old, new, command = "alpha\nbeta", "gamma\ndelta\n", "check one\ntwo"
    code, out, err = run_cli(
        mutation_probe,
        [str(target), old, new, "--", command],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 0
    text = record.read_text()
    for piece in (str(target), old, new, command):
        assert piece in text


def test_main_appends_nothing_to_the_record_when_the_command_stays_green_and_exits_1_2506(
    run_cli, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    monkeypatch.setattr(
        mutation_probe.subprocess, "run", lambda *a, **k: mutation_probe.subprocess.CompletedProcess(a, 0)
    )
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "alpha", "beta", "--", "true"],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 1
    assert not record.exists() or record.read_text() == ""


def test_main_appends_nothing_to_the_record_when_the_file_was_not_mutated_and_exits_2_2506(
    run_cli, mutation_probe, monkeypatch, tmp_path
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    monkeypatch.setattr(
        mutation_probe.subprocess, "run", lambda *a, **k: mutation_probe.subprocess.CompletedProcess(a, 1)
    )
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "absent", "beta", "--", "true"],
        env={"VERI_MUTATION_RECORD": str(record)},
    )
    assert code == 2
    assert not record.exists() or record.read_text() == ""


def test_main_records_a_bash_c_probe_with_its_script_as_one_quoted_word_2877(
    run_cli, mutation_probe, monkeypatch, tmp_path
):
    import shlex

    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    monkeypatch.setattr(
        mutation_probe.subprocess, "run", lambda *a, **k: mutation_probe.subprocess.CompletedProcess(a, 1)
    )
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
    run_cli, mutation_probe, monkeypatch, tmp_path
):
    import shlex
    from pathlib import Path

    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    monkeypatch.setattr(
        mutation_probe.subprocess, "run", lambda *a, **k: mutation_probe.subprocess.CompletedProcess(a, 1)
    )
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
    run_cli, mutation_probe, monkeypatch, tmp_path
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
    monkeypatch.setattr(via_link.subprocess, "run", lambda *a, **k: via_link.subprocess.CompletedProcess(a, 1))
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
    run_cli, mutation_probe, monkeypatch, args
):
    calls = []
    monkeypatch.setattr(mutation_probe.subprocess, "run", lambda *a, **k: calls.append(a))
    code, out, err = run_cli(mutation_probe, args)
    assert code == 2
    assert out == ""
    assert "usage: mutation-probe.sh --before <sha> --keep <test-path> -- <command…>" in err
    assert calls == []


@pytest.mark.parametrize("env", [{}, {"VERI_MUTATION_ADDRESS_DOMAIN": ""}], ids=["unset", "empty"])
def test_main_accepts_and_records_an_outside_address_when_the_address_domain_is_unset_or_empty_3330(
    run_cli, mutation_probe, monkeypatch, tmp_path, env
):
    target = tmp_path / "target.txt"
    target.write_text("alpha\n")
    record = tmp_path / "mutations.md"
    calls = []

    def fake_run(*a, **k):
        calls.append(target.read_text())
        return mutation_probe.subprocess.CompletedProcess(a, 1)

    monkeypatch.setattr(mutation_probe.subprocess, "run", fake_run)
    code, out, err = run_cli(
        mutation_probe,
        [str(target), "alpha", "x@outside.invalid", "--", "false"],
        env={"VERI_MUTATION_RECORD": str(record), **env},
    )
    assert code == 0
    assert calls == ["x@outside.invalid\n"]
    assert target.read_text() == "alpha\n"
    assert "x@outside.invalid" in record.read_text()
