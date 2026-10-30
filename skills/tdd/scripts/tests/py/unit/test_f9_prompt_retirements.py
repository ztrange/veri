"""F9 prompt retirements: what the cover and over-budget renders keep mechanical."""
import importlib
import pathlib
import re

import pytest


def test_the_cover_render_has_covered_unreachable_type_only_and_proof_report_lines_and_over_budget_ignores_a_reason_file_past_budget(
        tmp_path, run_cli):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_text("# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_text("zxqv-unreadable-rejection-reason\n")
    step, cmd = "extract the frobnicator", "make test"

    code, cover, _ = run_cli(build_develop_prompt, ["cover", str(spec), step, cmd])
    assert code == 0
    assert re.search(r"^COVERED:.*unreachable", cover, re.M)
    assert re.search(r"^COVERED:.*type-only", cover, re.M)
    assert re.search(r"^PROOF:", cover, re.M)

    argv = ["over-budget", str(spec), step, cmd, "3.47", "2.50"]
    code, plain, _ = run_cli(build_develop_prompt, argv)
    code_extra, extra, _ = run_cli(build_develop_prompt, argv + [str(reason)])
    assert (code, code_extra) == (0, 0)
    assert extra == plain
    assert "zxqv-unreadable-rejection-reason" not in extra


@pytest.mark.tree_audit("checks that unit/test_commit_suffix.py is gone")
def test_report_formats_keeps_parse_and_drops_the_stop_prose_lint_and_the_commit_suffix_suite_is_gone():
    report_formats = importlib.import_module("veri.report_formats")
    assert [n for n in ("EXEMPT", "_STOP_WORDS", "stop_prose_offenders")
            if hasattr(report_formats, n)] == []
    assert hasattr(report_formats, "parse")
    assert not (pathlib.Path(__file__).parent / "test_commit_suffix.py").exists()
