"""In-process cases for veri/claude_md_counts.py, the check that CLAUDE.md states no count of its tree."""
import importlib
from pathlib import Path


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


def test_the_committed_claude_md_states_no_count_of_the_tree_1508(run_cli):
    claude_md_counts = importlib.import_module("veri.claude_md_counts")
    claude_md = Path(__file__).resolve().parents[6] / "CLAUDE.md"

    code, out, err = run_cli(claude_md_counts, [str(claude_md)])

    assert (code, out + err) == (0, "")


def test_a_digit_count_with_no_word_count_beside_it_fails_naming_its_line_and_passes_with_the_line_removed_1508(tmp_path, run_cli):
    claude_md_counts = importlib.import_module("veri.claude_md_counts")
    planted = tmp_path / "planted.md"
    planted.write_text("# notes\n\nThe fixtures are 130 files under tests/.\n")
    removed = tmp_path / "removed.md"
    removed.write_text("# notes\n\n")

    code, out, err = run_cli(claude_md_counts, [str(planted)])
    removed_code, removed_out, removed_err = run_cli(claude_md_counts, [str(removed)])

    flagged = [line.split(":")[1] for line in (out + err).splitlines() if line.startswith(f"{planted}:")]
    assert (code, flagged, removed_code, removed_out + removed_err) == (1, ["3"], 0, "")


def test_a_count_of_files_alone_in_words_fails_naming_its_line_and_passes_with_the_line_removed_1508(tmp_path, run_cli):
    claude_md_counts = importlib.import_module("veri.claude_md_counts")
    planted = tmp_path / "planted.md"
    planted.write_text("# notes\n\nTwelve files hold the fixtures.\n")
    removed = tmp_path / "removed.md"
    removed.write_text("# notes\n\n")

    code, out, err = run_cli(claude_md_counts, [str(planted)])
    removed_code, removed_out, removed_err = run_cli(claude_md_counts, [str(removed)])

    flagged = [line.split(":")[1] for line in (out + err).splitlines() if line.startswith(f"{planted}:")]
    assert (code, flagged, removed_code, removed_out + removed_err) == (1, ["3"], 0, "")


def test_a_count_split_from_its_noun_by_a_backticked_or_path_like_word_fails_naming_its_line_each_planted_alone_1508(tmp_path, run_cli):
    claude_md_counts = importlib.import_module("veri.claude_md_counts")
    plants = {
        "backticked": "The four `-recorded` suites count through the harness.\n",
        "path_like": "The three tests/unit/ suites are fast.\n",
    }
    results = {}
    for name, text in plants.items():
        planted = tmp_path / f"{name}.md"
        planted.write_text("# notes\n\n" + text)
        code, out, err = run_cli(claude_md_counts, [str(planted)])
        results[name] = (code, [line.split(":")[1] for line in (out + err).splitlines() if line.startswith(f"{planted}:")])

    assert results == {"backticked": (1, ["3"]), "path_like": (1, ["3"])}


def test_claude_mds_prose_names_invisible_work_sh_the_script_the_procedure_does_not_call():
    root = Path(__file__).resolve().parents[6]
    problems = []
    if not (root / "skills/tdd/scripts/invisible-work.sh").is_file():
        problems.append("skills/tdd/scripts/invisible-work.sh is not in the tree whose count CLAUDE.md states")
    if not problems:
        preamble = []
        for line in (root / "CLAUDE.md").read_text(encoding="utf-8", errors="surrogateescape").splitlines():
            if line.startswith("## "):
                break
            preamble.append(line)
        intro = " ".join(preamble) + " "
        if intro.replace(" ", "") and "invisible-work.sh" not in intro:
            problems.append("CLAUDE.md's opening paragraph counts '<n> bash scripts it calls' without naming invisible-work.sh, a script the procedure never calls")

    assert problems == []
