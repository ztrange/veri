"""Cases for veri/rerun_alone.py, the logic behind rerun-alone.sh."""
import importlib


def test_main_with_no_argument_prints_a_usage_line_naming_rerun_alone_sh_on_stderr_and_exits_2_2905(run_cli):
    rerun_alone = importlib.import_module("veri.rerun_alone")

    code, out, err = run_cli(rerun_alone, [])

    assert (code, out) == (2, "")
    assert "usage: rerun-alone.sh" in err


def test_main_with_a_red_file_holding_an_invalid_utf8_fragment_answers_exit_1_not_a_decode_error_2936(run_cli, tmp_path):
    rerun_alone = importlib.import_module("veri.rerun_alone")
    red = tmp_path / "red.txt"
    red.write_bytes(b"x" * 10 + "€".encode()[:2])

    code, out, err = run_cli(rerun_alone, ["true", str(red)])

    assert (code, out) == (1, "")
    assert "UnicodeDecodeError" not in err


def test_rerun_answers_0_and_records_a_suite_flake_when_every_named_file_passes_alone_and_1_when_one_stays_red(
        monkeypatch, capsys, tmp_path, fake_processes):
    rerun_alone = importlib.import_module("veri.rerun_alone")
    red = tmp_path / "red.txt"
    red.write_text("FAILED tests/a.py::t1 - boom\nFAILED tests/b.py::t2\n")
    recorded = []
    one_fails = fake_processes.answers(
        {"sh ": lambda line, **kw: (int(one_fails.argvs[-1][-1].startswith("tests/b")), "", "")})
    monkeypatch.setattr(rerun_alone.event, "append", lambda *a: recorded.append(a) or 0)

    still_red = rerun_alone.rerun("alone-cmd", str(red))
    all_pass = fake_processes.answers({"sh ": (0, "", "")})
    flaked = rerun_alone.rerun("alone-cmd", str(red))

    assert [argv[-1] for argv in one_fails.argvs] == ["tests/a.py::t1", "tests/b.py::t2"]
    assert [argv[-1] for argv in all_pass.argvs] == ["tests/a.py::t1", "tests/b.py::t2"]
    assert (still_red, flaked) == (1, 0)
    assert recorded == [("", {}, "suite-flake", ["files=tests/a.py::t1,tests/b.py::t2"])]
    assert capsys.readouterr() == ("", "")


# main through run_cli as `rerun-alone.sh <alone-cmd> <red-output-file>`, run from tmp_path. The alone command is faked at
# `sh`: each target it is handed arrives as `sh -c <cmd> sh <target>`, and red_when(target) is its exit status.

def alone(fake_processes, red_when=lambda target: False):
    fake = fake_processes.answers({"sh ": lambda line, **kw: (int(red_when(fake.argvs[-1][-1])), "", "")})
    return fake


def targets(fake):
    return [argv[-1] for argv in fake.argvs]


def rerun_in(run_cli, tmp_path, alone_cmd, red_text):
    rerun_alone = importlib.import_module("veri.rerun_alone")
    red = tmp_path / "red-output.txt"
    red.write_text(red_text)
    return run_cli(rerun_alone, [alone_cmd, str(red)], cwd=tmp_path)


def flake_events(tmp_path):
    return [e for e in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines() if "suite-flake" in e]


def test_red_output_naming_no_test_file_exits_1_and_runs_no_alone_command_2905(run_cli, tmp_path, fake_processes):
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone"), "Error: connection refused\n2 failed\n")

    assert code == 1
    assert targets(fake) == []


def test_a_file_still_red_alone_exits_1_and_writes_no_suite_flake_event_2905(run_cli, tmp_path, fake_processes):
    fake = alone(fake_processes, red_when=lambda t: t.endswith("b.test.ts"))

    code, out, err = rerun_in(run_cli, tmp_path, f'{tmp_path / "alone-cmd.sh"} "$1"',
                              "FAIL src/a.test.ts\nFAIL src/b.test.ts\n2 failed\n")

    assert code == 1
    assert sorted(targets(fake)) == ["src/a.test.ts", "src/b.test.ts"]
    assert not list(tmp_path.rglob("*events*"))


def test_every_file_passing_alone_exits_0_and_writes_a_suite_flake_event_naming_each_2905(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"), "FAIL src/a.test.ts\nFAIL src/b.test.ts\n2 failed\n")

    assert code == 0
    flakes = flake_events(tmp_path)
    assert len(flakes) == 1
    assert "src/a.test.ts" in flakes[0] and "src/b.test.ts" in flakes[0]


def test_alone_command_placing_its_own_file_argument_receives_the_file_once_as_written_2905(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)
    runner = tmp_path / "runner.sh"

    code, out, err = rerun_in(run_cli, tmp_path, f'{runner} TESTS="$1"', "FAIL src/a.test.ts\n1 failed\n")
    usage = run_cli(importlib.import_module("veri.rerun_alone"), [], cwd=tmp_path)

    assert code == 0
    assert fake.argvs == [["sh", "-c", f'{runner} TESTS="$1"', "sh", "src/a.test.ts"]]
    assert "<alone-cmd> <red-output-file>" in usage[2]


def test_pytest_failed_summary_file_passing_alone_exits_0_and_writes_a_suite_flake_event_naming_it_2883(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_bar - Failed: Timeout >30.0s\n1 failed\n")

    assert code == 0
    assert targets(fake) == ["skills/tdd/scripts/tests/py/test_foo.py::test_bar"]
    flakes = flake_events(tmp_path)
    assert len(flakes) == 1
    assert "skills/tdd/scripts/tests/py/test_foo.py::test_bar" in flakes[0]


def test_pytest_error_summary_file_passing_alone_exits_0_and_writes_a_suite_flake_event_naming_it_2883(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "ERROR skills/tdd/scripts/tests/py/test_foo.py::test_bar - Failed: Timeout >30.0s\n1 error\n")

    assert code == 0
    assert targets(fake) == ["skills/tdd/scripts/tests/py/test_foo.py::test_bar"]
    flakes = flake_events(tmp_path)
    assert len(flakes) == 1
    assert "skills/tdd/scripts/tests/py/test_foo.py::test_bar" in flakes[0]


def test_several_summary_lines_naming_one_file_run_it_alone_once_and_name_it_once_2883(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_a - Failed: Timeout >30.0s\n"
                              "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_b - Failed: Timeout >30.0s\n"
                              "ERROR skills/tdd/scripts/tests/py/test_foo.py::test_c - Failed: Timeout >30.0s\n"
                              "3 failed\n")

    assert code == 0
    assert targets(fake) == ["skills/tdd/scripts/tests/py/test_foo.py::test_a", "skills/tdd/scripts/tests/py/test_foo.py::test_b", "skills/tdd/scripts/tests/py/test_foo.py::test_c"]
    flakes = flake_events(tmp_path)
    assert len(flakes) == 1
    for t in ("test_a", "test_b", "test_c"):
        assert flakes[0].count("skills/tdd/scripts/tests/py/test_foo.py::" + t) == 1


def test_pytest_red_output_naming_no_file_on_a_summary_line_exits_1_runs_no_alone_command_and_writes_no_event_2883(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "skills/tdd/scripts/tests/py/test_foo.py ....                [ 50%]\n"
                              "skills/tdd/scripts/tests/py/test_bar.py ....                [100%]\n"
                              "!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!\n"
                              "no tests ran in 3.21s\n")

    assert code == 1
    assert targets(fake) == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_pytest_red_output_naming_two_files_one_still_red_alone_exits_1_and_writes_no_suite_flake_event_2883(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes, red_when=lambda t: t.endswith("test_bar.py::test_b"))

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_a - Failed: Timeout >30.0s\n"
                              "FAILED skills/tdd/scripts/tests/py/test_bar.py::test_b - AssertionError\n"
                              "2 failed\n")

    assert code == 1
    assert targets(fake) == [
        "skills/tdd/scripts/tests/py/test_foo.py::test_a",
        "skills/tdd/scripts/tests/py/test_bar.py::test_b",
    ]
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_pytest_failed_line_naming_a_unit_file_reruns_it_alone_once_and_writes_one_suite_flake_event_2933(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "FAILED skills/tdd/scripts/tests/py/unit/test_x.py::test_a - assert 0\n")

    assert code == 0
    assert targets(fake) == ["skills/tdd/scripts/tests/py/unit/test_x.py::test_a"]
    flakes = flake_events(tmp_path)
    assert len(flakes) == 1
    assert "skills/tdd/scripts/tests/py/unit/test_x.py::test_a" in flakes[0]


def test_bare_test_py_path_without_a_pytest_summary_line_reruns_it_alone_once_and_writes_one_suite_flake_event_2933(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "timed out waiting in\nskills/tdd/scripts/tests/py/unit/test_x.py\n1 failed\n")

    assert code == 0
    assert targets(fake) == ["skills/tdd/scripts/tests/py/unit/test_x.py"]
    flakes = flake_events(tmp_path)
    assert len(flakes) == 1
    assert "skills/tdd/scripts/tests/py/unit/test_x.py" in flakes[0]


def test_bare_test_py_path_still_red_alone_exits_1_and_writes_no_suite_flake_event_2933(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes, red_when=lambda t: True)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "timed out waiting in\nskills/tdd/scripts/tests/py/unit/test_x.py\n1 failed\n")

    assert code == 1
    assert targets(fake) == ["skills/tdd/scripts/tests/py/unit/test_x.py"]
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_several_failed_lines_naming_one_unit_file_rerun_it_alone_once_and_list_it_once_in_the_event_2933(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "FAILED skills/tdd/scripts/tests/py/unit/test_x.py::test_a - assert 0\n"
                              "FAILED skills/tdd/scripts/tests/py/unit/test_x.py::test_b - assert 0\n"
                              "FAILED skills/tdd/scripts/tests/py/unit/test_x.py::test_c - assert 0\n"
                              "3 failed\n")

    assert code == 0
    assert targets(fake) == ["skills/tdd/scripts/tests/py/unit/test_x.py::test_a", "skills/tdd/scripts/tests/py/unit/test_x.py::test_b", "skills/tdd/scripts/tests/py/unit/test_x.py::test_c"]
    flakes = flake_events(tmp_path)
    assert len(flakes) == 1
    for t in ("test_a", "test_b", "test_c"):
        assert flakes[0].count("skills/tdd/scripts/tests/py/unit/test_x.py::" + t) == 1


def test_a_test_ext_file_listed_twice_reruns_alone_once_and_is_listed_once_in_the_event_2933(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"), "FAIL src/a.test.ts\nFAIL src/a.test.ts\n2 failed\n")

    assert code == 0
    assert targets(fake) == ["src/a.test.ts"]
    flakes = flake_events(tmp_path)
    assert len(flakes) == 1
    assert flakes[0].count("src/a.test.ts") == 1


def test_pytest_failed_line_wins_over_a_test_path_in_the_output_body_3537(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "assert 'foo.test.ts::x' in out\n"
                              "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_bar - Failed: Timeout >30.0s\n"
                              "1 failed\n")

    assert code == 0
    assert targets(fake) == ["skills/tdd/scripts/tests/py/test_foo.py::test_bar"]


def test_pytest_failed_node_id_reruns_alone_exactly_that_node_id_and_writes_one_suite_flake_event_3537(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)
    node = "skills/tdd/scripts/tests/py/test_foo.py::test_bar"

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "assert 'foo.test.ts::x' in out\n"
                              f"FAILED {node} - Failed: Timeout >30.0s\n"
                              "1 failed\n")

    assert code == 0
    assert targets(fake) == [node]
    flakes = flake_events(tmp_path)
    assert len(flakes) == 1
    assert node in flakes[0]


def test_node_id_still_red_alone_with_a_test_string_in_the_body_exits_1_and_writes_no_suite_flake_event_3537(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes, red_when=lambda t: t.endswith("test_foo.py::test_bar"))

    code, out, err = rerun_in(run_cli, tmp_path, str(tmp_path / "alone-cmd.sh"),
                              "E   AssertionError: foo.test.ts::rejects an empty name\n"
                              "FAILED skills/tdd/scripts/tests/py/test_foo.py::test_bar - Failed: Timeout >30.0s\n"
                              "1 failed\n")

    assert code == 1
    assert targets(fake) == ["skills/tdd/scripts/tests/py/test_foo.py::test_bar"]
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_pytest_failed_node_id_with_a_space_reruns_alone_whole_as_one_argument_and_names_it_in_the_event_3537(run_cli, tmp_path, fake_processes):
    (tmp_path / ".git").mkdir()
    fake = alone(fake_processes)
    alone_cmd = f'{tmp_path / "alone-cmd.sh"} "$1"'

    code, out, err = rerun_in(run_cli, tmp_path, alone_cmd, "FAILED tests/test_x.py::test_y[a b] - assert 0\n1 failed\n")

    assert code == 0
    assert fake.argvs == [["sh", "-c", alone_cmd, "sh", "tests/test_x.py::test_y[a b]"]]
    event = (tmp_path / ".tdd" / "events.jsonl").read_text()
    assert '"files": "tests/test_x.py::test_y[a b]"' in event
