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
