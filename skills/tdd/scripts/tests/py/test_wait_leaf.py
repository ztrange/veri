"""In-process cases for veri/wait_leaf.py, the module wait-leaf.sh is a shim over."""
import importlib
import re
import subprocess

import pytest

from conftest import INTERPRETER_VENV, SCRIPTS

USAGE = "usage: wait-leaf.sh <name> [max-seconds]\n"


@pytest.fixture
def wait_leaf():
    return importlib.import_module("veri.wait_leaf")


def test_main_refuses_a_missing_name_answers_a_recorded_code_and_times_out_with_3(
        monkeypatch, capsys, tmp_path, wait_leaf, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(lambda line, **_: (0, "1000\n", "") if line == "date +%s" else (0, "", ""))

    refusals = []
    for argv in ([], [""]):
        code = wait_leaf.main(argv)
        captured = capsys.readouterr()
        refusals.append((code, captured.out, captured.err))
    assert refusals == [(2, "", USAGE), (2, "", USAGE)]
    assert calls == []

    (tmp_path / ".tdd").mkdir()
    recorded = []
    for text in ("0\n", "1\n", "2\n", "3\n", "5\n"):
        (tmp_path / ".tdd" / "x.exit").write_text(text)
        recorded.append(wait_leaf.main(["x"]))
    assert recorded == [0, 1, 2, 3, 2]

    (tmp_path / ".tdd" / "x.exit").unlink()
    assert wait_leaf.main(["x", "0"]) == 3


def test_main_refusal_touches_no_file_maps_a_recorded_code_as_text_and_waits_out_a_code_that_is_not_one(
        monkeypatch, capsys, tmp_path, wait_leaf, fake_processes):
    monkeypatch.chdir(tmp_path)
    readings = []

    def answer(line, **_):
        if line == "date +%s":
            readings.append(1000 + len(readings))
            return (0, f"{readings[-1]}\n", "")
        return (0, "", "")

    fake_processes(answer)

    for argv in ([], [""]):
        assert wait_leaf.main(argv) == 2
    assert list(tmp_path.iterdir()) == []

    (tmp_path / ".tdd").mkdir()
    exit_file = tmp_path / ".tdd" / "x.exit"
    mapped = []
    for text in ("3\n", "4\n", "00\n", "01\n", "12345678901234567890\n"):
        exit_file.write_text(text)
        mapped.append((wait_leaf.main(["x"]), capsys.readouterr().out))
    assert mapped == [(3, ""), (2, ""), (2, ""), (2, ""), (2, "")]

    waited = []
    for text in ("-1\n", "7x\n", "", None):
        exit_file.unlink(missing_ok=True)
        if text is None:
            exit_file.mkdir()
        else:
            exit_file.write_text(text)
        readings.clear()
        waited.append((wait_leaf.main(["x", "5"]), readings[-1] >= readings[0] + 5))
    assert waited == [(3, True)] * 4


def test_main_reads_the_clock_once_then_per_round_checks_the_pid_rechecks_after_a_dead_supervisor_and_sleeps_between_rounds(
        monkeypatch, capsys, tmp_path, wait_leaf, fake_processes):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_POLL", "0.5")
    (tmp_path / ".tdd").mkdir()
    readings = []

    def answer(line, **_):
        if line == "date +%s":
            if len(readings) > 20:
                raise RuntimeError("runaway wait: more than 20 clock readings")
            readings.append(next(clock))
            return (0, f"{readings[-1]}\n", "")
        if line == "ps -p 42 -o args=":
            if len(calls) > 6:
                (tmp_path / ".tdd" / "x.exit").write_text("1\n")
                return (1, "", "")
            return (0, "bash supervise.sh x develop-red\n", "")
        return (0, "", "")

    calls = fake_processes(answer)

    (tmp_path / ".tdd" / "y.pid").write_text("abc\n")
    clock = iter([1000, 1000, 1001] + [1001] * 20)
    timed_out = wait_leaf.main(["y", "1"])
    assert (timed_out, calls) == (3, ["date +%s", "date +%s", "sleep 0.5", "date +%s"])

    calls.clear()
    readings.clear()
    (tmp_path / ".tdd" / "x.pid").write_text("42\n")
    clock = iter([1000] * 21)
    answered = wait_leaf.main(["x"])
    assert (answered, calls) == (1, [
        "date +%s",
        "ps -p 42 -o args=", "date +%s", "sleep 0.5",
        "ps -p 42 -o args=", "date +%s", "sleep 0.5",
        "ps -p 42 -o args=",
    ])
    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("", "")


def test_main_reads_max_as_bash_arithmetic_defaulting_to_540_and_ignores_arguments_past_it(
        monkeypatch, capsys, tmp_path, wait_leaf, fake_processes):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "x.pid").write_text("42\n")
    readings = []

    def answer(line, **_):
        if line == "date +%s":
            if len(readings) > 600:
                raise RuntimeError("runaway wait: more than 600 clock readings")
            readings.append(1000 + len(readings))
            return (0, f"{readings[-1]}\n", "")
        if line == "ps -p 42 -o args=":
            return (0, "bash supervise.sh x develop-red\n", "")
        return (0, "", "")

    calls = fake_processes(answer)

    rounds = {}
    for argv in (["x"], ["x", ""], ["x", "0"], ["x", "-5"], ["x", "010"], ["x", "0x10"], ["x", "3", "9"]):
        calls.clear()
        readings.clear()
        code = wait_leaf.main(argv)
        rounds[tuple(argv[1:])] = (code, calls.count("ps -p 42 -o args="), readings[-1] - readings[0])
    assert rounds == {
        (): (3, 590, 590),
        ("",): (3, 590, 590),
        ("0",): (3, 1, 1),
        ("-5",): (3, 1, 1),
        ("010",): (3, 8, 8),
        ("0x10",): (3, 16, 16),
        ("3", "9"): (3, 3, 3),
    }
    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("", "")


def test_main_answers_a_max_that_is_not_an_integer_form_with_1_as_bash_did(
        monkeypatch, capsys, tmp_path, wait_leaf, fake_processes):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "x.pid").write_text("42\n")
    readings = []

    def answer(line, **_):
        if line == "date +%s":
            if len(readings) > 20:
                raise RuntimeError("runaway wait: more than 20 clock readings")
            readings.append(1000 + len(readings))
            return (0, f"{readings[-1]}\n", "")
        if line == "ps -p 42 -o args=":
            return (0, "bash supervise.sh x develop-red\n", "")
        return (0, "", "")

    calls = fake_processes(answer)

    answers = {}
    for text in ("abc", "08", "1.5", "10+5"):
        calls.clear()
        readings.clear()
        code = wait_leaf.main(["x", text])
        captured = capsys.readouterr()
        answers[text] = (code, list(calls), captured.out, captured.err.count("\n"), text in captured.err)
    assert answers == {
        "abc": (1, ["date +%s"], "", 1, True),
        "08": (1, ["date +%s", "ps -p 42 -o args=", "date +%s"], "", 1, True),
        "1.5": (1, ["date +%s", "ps -p 42 -o args=", "date +%s"], "", 1, True),
        "10+5": (1, ["date +%s", "ps -p 42 -o args=", "date +%s"], "", 1, True),
    }

    (tmp_path / ".tdd" / "x.exit").write_text("0\n")
    calls.clear()
    assert (wait_leaf.main(["x", "08"]), calls) == (0, ["date +%s"])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_main_hands_veri_poll_to_sleep_as_text_defaulting_to_1_and_a_failing_sleep_does_not_end_the_wait(
        monkeypatch, capsys, tmp_path, wait_leaf, fake_processes):
    monkeypatch.chdir(tmp_path)
    readings = []

    def answer(line, **_):
        if line == "date +%s":
            if len(readings) > 20:
                raise RuntimeError("runaway wait: more than 20 clock readings")
            readings.append(1000 + len(readings))
            return (0, f"{readings[-1]}\n", "")
        if line.startswith("sleep"):
            return (1, "", "sleep: invalid time interval\n")
        return (0, "", "")

    calls = fake_processes(answer)

    waits = {}
    for poll in (None, "", "0.02"):
        if poll is None:
            monkeypatch.delenv("VERI_POLL", raising=False)
        else:
            monkeypatch.setenv("VERI_POLL", poll)
        calls.clear()
        readings.clear()
        waits[poll] = (wait_leaf.main(["x", "2"]), list(calls))
    assert waits == {
        None: (3, ["date +%s", "date +%s", "sleep 1", "date +%s"]),
        "": (3, ["date +%s", "date +%s", "sleep 1", "date +%s"]),
        "0.02": (3, ["date +%s", "date +%s", "sleep 0.02", "date +%s"]),
    }
    captured = capsys.readouterr()
    assert captured.out == ""


def test_main_never_calls_a_pid_file_with_no_number_dead_and_names_a_dead_supervisor_by_the_pid_digits_as_read(
        monkeypatch, capsys, tmp_path, wait_leaf, fake_processes):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    readings = []

    def answer(line, **_):
        if line == "date +%s":
            if len(readings) > 20:
                raise RuntimeError("runaway wait: more than 20 clock readings")
            readings.append(1000 + len(readings))
            return (0, f"{readings[-1]}\n", "")
        if line.startswith("ps "):
            return (1, "", "")
        return (0, "", "")

    calls = fake_processes(answer)

    pid_file = tmp_path / ".tdd" / "x.pid"
    no_verdict = {}
    for text in (None, "", "abc\n", "-7\n"):
        pid_file.unlink(missing_ok=True)
        if text is not None:
            pid_file.write_text(text)
        calls.clear()
        readings.clear()
        code = wait_leaf.main(["x", "2"])
        no_verdict[text] = (code, [c for c in calls if c.startswith("ps ")])
    assert no_verdict == {None: (3, []), "": (3, []), "abc\n": (3, []), "-7\n": (3, [])}
    capsys.readouterr()

    pid_file.write_text("007\n")
    calls.clear()
    code = wait_leaf.main(["x"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err, [c for c in calls if c.startswith("ps ")]) == (
        2, "",
        "wait-leaf.sh: supervisor for leaf 'x' (pid 007) exited without recording a status\n",
        ["ps -p 007 -o args="],
    )


def test_main_counts_an_empty_date_reading_as_0_before_the_loop_and_never_as_the_deadline_in_a_round(
        monkeypatch, capsys, tmp_path, wait_leaf, fake_processes):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_POLL", "0")

    def answer(line, **_):
        if line == "date +%s":
            if not readings:
                raise RuntimeError("runaway wait: no clock reading left")
            reading = readings.pop(0)
            if reading is None:
                return empty()
            return (0, f"{reading}\n", "")
        return (0, "", "")

    calls = fake_processes(answer)

    def missing():
        raise FileNotFoundError(2, "No such file or directory", "date")

    waits = {}
    for how, empty in (("prints nothing", lambda: (0, "", "")),
                       ("fails", lambda: (1, "", "date: illegal option\n")),
                       ("missing", missing)):
        calls.clear()
        readings = [None, None, None, 4, 5]
        waits[how] = (wait_leaf.main(["x", "5"]), list(calls))
    rounds = ["date +%s", "date +%s", "sleep 0", "date +%s", "sleep 0",
              "date +%s", "sleep 0", "date +%s"]
    assert waits == {"prints nothing": (3, rounds), "fails": (3, rounds), "missing": (3, rounds)}
    assert capsys.readouterr().out == ""


@pytest.mark.process("wait-leaf.sh run through a symlink to the skills directory")
def test_a_run_through_a_symlink_to_the_skills_directory_reads_the_working_directorys_exit_file_and_answers_a_recorded_1(
        tmp_path):
    (tmp_path / "linked").symlink_to(SCRIPTS.parents[1], target_is_directory=True)
    (tmp_path / "caller" / ".tdd").mkdir(parents=True)
    (tmp_path / "caller" / ".tdd" / "via-link.exit").write_text("1\n")

    ran = subprocess.run([str(tmp_path / "linked" / "tdd" / "scripts" / "wait-leaf.sh"), "via-link", "0"],
                         cwd=tmp_path / "caller", stdin=subprocess.DEVNULL, capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin", "VERI_VENV": INTERPRETER_VENV, "VERI_POLL": "0"})

    assert (ran.returncode, ran.stdout, ran.stderr) == (1, "", "")
    assert not (SCRIPTS / ".tdd" / "via-link.exit").exists()


def stepping_clock(fake_processes, ps=None, land=None):
    readings = []

    def answer(line, **_):
        if line == "date +%s":
            if len(readings) > 600:
                raise RuntimeError("runaway wait: more than 600 clock readings")
            readings.append(len(readings))
            if land is not None and readings[-1] >= land[0] and not land[1].exists():
                land[1].write_text(land[2])
            return (0, f"{readings[-1]}\n", "")
        if line.startswith("ps ") and ps is not None:
            return ps
        return (0, "", "")

    fake_processes(answer)
    return readings


def test_cli_answers_a_code_recorded_a_couple_of_seconds_into_the_wait_as_soon_as_it_lands(
        tmp_path, run_cli, wait_leaf, fake_processes):
    (tmp_path / ".tdd").mkdir()
    answers = {}
    for code in ("0", "1", "2"):
        exit_file = tmp_path / ".tdd" / f"late-{code}.exit"
        readings = stepping_clock(fake_processes, land=(2, exit_file, f"{code}\n"))
        answer = run_cli(wait_leaf, [f"late-{code}", "20"], env={"VERI_POLL": "0"}, cwd=tmp_path)
        answers[code] = (answer, 2 <= readings[-1] - readings[0] <= 10)
    assert answers == {"0": ((0, "", ""), True), "1": ((1, "", ""), True), "2": ((2, "", ""), True)}


def test_cli_exits_2_promptly_naming_the_leaf_and_the_pid_when_the_recorded_pid_runs_something_other_than_its_supervisor(
        tmp_path, run_cli, wait_leaf, fake_processes):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "reused-sup.pid").write_text("4242\n")
    readings = stepping_clock(fake_processes, ps=(0, "sleep 60\n", ""))

    answer = run_cli(wait_leaf, ["reused-sup", "20"], env={"VERI_POLL": "0"}, cwd=tmp_path)

    assert answer == (2, "", "wait-leaf.sh: supervisor for leaf 'reused-sup' (pid 4242) exited without recording a status\n")
    assert readings[-1] - readings[0] <= 10


def test_cli_exits_3_at_budget_0_with_nothing_on_stderr_while_a_supervisor_spelled_veri_supervise_py_is_alive(
        tmp_path, run_cli, wait_leaf, fake_processes):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "live-py.pid").write_text("4242\n")
    stepping_clock(fake_processes, ps=(0, "python3 /x/veri/supervise.py live-py develop-red\n", ""))

    assert run_cli(wait_leaf, ["live-py", "0"], env={"VERI_POLL": "0"}, cwd=tmp_path) == (3, "", "")


def test_cli_exits_2_promptly_naming_a_verifier_leaf_whose_supervisor_died(
        tmp_path, run_cli, wait_leaf, fake_processes):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-red.pid").write_text("4242\n")
    readings = stepping_clock(fake_processes, ps=(1, "", ""))

    code, out, err = run_cli(wait_leaf, ["verdict-red", "20"], env={"VERI_POLL": "0"}, cwd=tmp_path)

    assert (code, out, "'verdict-red'" in err, "4242" in err) == (2, "", True, True)
    assert readings[-1] - readings[0] <= 10


def test_cli_with_its_default_budget_answers_0_1_or_2_as_soon_as_recorded_and_2_once_the_supervisor_dies_never_3_1708(
        tmp_path, run_cli, wait_leaf, fake_processes):
    (tmp_path / ".tdd").mkdir()
    answers = {}
    for code in ("0", "1", "2"):
        exit_file = tmp_path / ".tdd" / f"long-{code}.exit"
        readings = stepping_clock(fake_processes, land=(300, exit_file, f"{code}\n"))
        answer = run_cli(wait_leaf, [f"long-{code}"], env={"VERI_POLL": "0"}, cwd=tmp_path)
        answers[code] = (answer, 300 <= readings[-1] - readings[0] <= 310)

    (tmp_path / ".tdd" / "long-dead.pid").write_text("4242\n")
    readings = []

    def answer(line, **_):
        if line == "date +%s":
            if len(readings) > 600:
                raise RuntimeError("runaway wait: more than 600 clock readings")
            readings.append(len(readings))
            return (0, f"{readings[-1]}\n", "")
        if line.startswith("ps "):
            if readings[-1] >= 300:
                return (1, "", "")
            return (0, "bash supervise.sh long-dead develop-red\n", "")
        return (0, "", "")

    fake_processes(answer)
    died = run_cli(wait_leaf, ["long-dead"], env={"VERI_POLL": "0"}, cwd=tmp_path)
    answers["dead"] = ((died[0], died[1], "'long-dead'" in died[2]), 300 <= readings[-1] - readings[0] <= 310)

    assert answers == {"0": ((0, "", ""), True), "1": ((1, "", ""), True), "2": ((2, "", ""), True),
                       "dead": ((2, "", True), True)}


def skill_paragraphs():
    return re.split(r"\n[ \t]*\n", (SCRIPTS.parent / "SKILL.md").read_text())


def test_skill_md_launches_every_leaf_detached_and_waits_for_it_with_wait_leaf_sh_in_the_foreground():
    lines = (SCRIPTS.parent / "SKILL.md").read_text().split("\n")
    sites = [i for i, line in enumerate(lines)
             if ("$S/supervise.sh" in line or "$S/verify.sh" in line) and ".tdd/" in line]
    misses = [i + 1 for i in sites
              if "detach-leaf.sh" not in lines[i] or "wait-leaf.sh" not in "\n".join(lines[i:i + 7])]
    assert (len(sites) >= 5, misses) == (True, [])


def test_skill_md_warns_that_a_background_call_awaiting_a_notification_never_completes_in_print_mode():
    assert [p for p in skill_paragraphs()
            if "background" in p.lower() and "notification" in p.lower() and re.search(r"print[ -]mode", p.lower())]


def test_skill_md_reports_a_verifier_whose_supervisor_died_the_way_it_reports_a_killed_developer_leaf():
    text = (SCRIPTS.parent / "SKILL.md").read_text()
    section = re.search(r"^## Launching a leaf — detach, then wait in the foreground\n(.*?)(?=^## )",
                        text, re.S | re.M).group(1)
    assert [p for p in re.split(r"\n[ \t]*\n", section)
            if "verdict-<phase>" in p and "killed-stuck" in p.lower() and "bail" in p.lower()
            and ("without recording a status" in p.lower()
                 or re.search(r"supervisor[^.]*(died|dies|exited|is gone)", p.lower()))]


def test_skill_md_tells_the_conductor_to_call_wait_leaf_sh_with_the_bash_maximum_timeout_and_names_the_600_s_cap_1708():
    assert [p for p in skill_paragraphs()
            if "wait-leaf.sh" in p and "600000" in p and "590" in p
            and re.search(r"no (max-seconds|second)s? argument|without a max-seconds", p.lower())
            and re.search(r"600 ?s[^.]*cap|cap[^.]*600 ?s", p.lower())]


def test_skill_md_tells_the_conductor_to_call_detach_command_sh_wait_with_no_max_seconds_and_the_bash_maximum_timeout_never_a_fixed_500_1708():
    text = (SCRIPTS.parent / "SKILL.md").read_text()
    assert not re.search(r"detach-command\.sh wait <name> 500", text)
    assert [p for p in skill_paragraphs()
            if "detach-command.sh wait" in p and "600000" in p
            and re.search(r"no (max-seconds|second)s? argument|without a max-seconds", p.lower())]
