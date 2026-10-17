"""In-process cases for veri/claude_md_counts.py, the check that CLAUDE.md states no count of its tree."""
import importlib


def test_a_stated_count_of_the_trees_files_fails_naming_its_line_and_a_dated_measurement_passes_1508(tmp_path, run_cli):
    claude_md_counts = importlib.import_module("veri.claude_md_counts")
    planted = tmp_path / "planted.md"
    planted.write_text(
        "# notes\n"
        "\n"
        "a procedure plus eighty bash scripts it calls.\n"
        "It measured 393 s on 2026-09-18 (the same 76 suites).\n"
        "Plain-shell asserts, 130 files for eighty scripts,\n"
        "plus thirteen suites under `unit/`, all run by `make test`.\n"
    )
    clean = tmp_path / "clean.md"
    clean.write_text("# notes\n\nThe scripts live under `skills/tdd/scripts/`.\nOn 2026-09-18 (the same 76 suites) it took 154 s.\n")

    code, out, err = run_cli(claude_md_counts, [str(planted)])
    clean_code, clean_out, clean_err = run_cli(claude_md_counts, [str(clean)])

    flagged = sorted({line for line in (out + err).splitlines() if line.startswith(f"{planted}:")})
    assert (code, [line.split(":")[1] for line in flagged], clean_code, clean_out + clean_err) == (1, ["3", "5", "6"], 0, "")
