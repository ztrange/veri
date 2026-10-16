"""In-process cases for veri/fast_tier_guard.py, the fast tier's admission-bar guard."""
import importlib


def test_a_planted_test_file_starting_a_process_through_subprocess_is_named_by_file_and_line_and_a_clean_one_is_not(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "import subprocess\n"
        "\n"
        "def test_runs_a_process():\n"
        "    subprocess.run(['true'])\n"
    )
    clean = tmp_path / "test_clean.py"
    clean.write_text("def test_adds():\n    assert 1 + 1 == 2\n")

    found = guard.offences(tmp_path)

    assert [line.split(": ")[0] for line in found] == [f"{offender}:4"]


def test_a_planted_test_file_starting_a_process_through_an_imported_name_or_an_aliased_module_is_named_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    imported = tmp_path / "test_imported_name.py"
    imported.write_text(
        "from subprocess import run\n"
        "\n"
        "def test_runs_a_process():\n"
        "    run(['true'])\n"
    )
    aliased = tmp_path / "test_aliased_module.py"
    aliased.write_text(
        "import subprocess as sp\n"
        "\n"
        "def test_runs_a_process():\n"
        "    sp.run(['true'])\n"
    )

    found = guard.offences(tmp_path)

    assert sorted(line.split(": ")[0] for line in found) == [f"{aliased}:4", f"{imported}:4"]


def test_a_planted_test_file_starting_a_process_through_os_system_os_exec_os_spawn_or_pty_is_named_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    forms = {
        "test_os_system.py": ("os", "os.system('true')"),
        "test_os_exec.py": ("os", "os.execv('/bin/true', ['true'])"),
        "test_os_spawn.py": ("os", "os.spawnl(os.P_WAIT, '/bin/true', 'true')"),
        "test_pty.py": ("pty", "pty.spawn(['true'])"),
    }
    planted = []
    for name, (module, call) in forms.items():
        path = tmp_path / name
        path.write_text(
            f"import {module}\n"
            "\n"
            "def test_runs_a_process():\n"
            f"    {call}\n"
        )
        planted.append(f"{path}:4")

    found = guard.offences(tmp_path)

    assert sorted(line.split(": ")[0] for line in found) == sorted(planted)


def test_a_planted_test_file_calling_time_sleep_is_reported_as_a_sleep_offence_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_sleeper.py"
    offender.write_text(
        "import time\n"
        "\n"
        "def test_waits():\n"
        "    time.sleep(1)\n"
    )

    found = guard.offences(tmp_path)

    assert [line.split(": ")[0] for line in found] == [f"{offender}:4"]
    assert "sleep" in found[0].split(": ", 1)[1]
