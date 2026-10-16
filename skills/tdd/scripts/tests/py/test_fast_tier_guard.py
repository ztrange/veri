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
