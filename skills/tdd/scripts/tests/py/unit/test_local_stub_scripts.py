"""A ratchet: test files writing their own `#!/bin/sh` stub script only shrink in number; new cases use stub_script.

What counts is a string literal that starts `#!/bin/sh` anywhere in the file, read with `ast` (the leading piece of an
f-string included), never a mention in a comment. `stub_script.py` holds the one header and is exempt.
"""
import pytest
from stub_script import holds_an_inline_stub

# The test files (paths under tests/py, sorted, ONE per line) that still hold a string literal starting `#!/bin/sh`.
# Migrate a file's stubs to stub_script.write_stub(path, body) and delete its line: a listed file that no longer holds
# one fails the second case below. Entries may be removed, NEVER added; a file not listed that holds one fails the
# first. One line per file keeps parallel migrations from conflicting.
FILES_WITH_AN_INLINE_STUB = {
    "test_add_ledger_step_process.py": "inline stubs, not yet on write_stub",
    "test_bash_version_guard_process.py": "inline stubs, not yet on write_stub",
    "test_capture_spec_process.py": "inline stubs, not yet on write_stub",    "test_coverage_blocker_process.py": "inline stubs, not yet on write_stub",
    "test_detach_command_process.py": "inline stubs, not yet on write_stub",
    "test_emitted_text_process.py": "inline stubs, not yet on write_stub",
    "test_event.py": "inline stubs, not yet on write_stub",
    "test_grade_prose_process.py": "inline stubs, not yet on write_stub",
    "test_graded_rebase_conflict_process.py": "inline stubs, not yet on write_stub",
    "test_install_links_process.py": "inline stubs, not yet on write_stub",
    "test_issue_worktree_process.py": "inline stubs, not yet on write_stub",
    "test_leaf_launchable_process.py": "inline stubs, not yet on write_stub",
    "test_mutation_parity_process.py": "inline stubs, not yet on write_stub",
    "test_no_product_caller_process.py": "inline stubs, not yet on write_stub",
    "test_parallel_conductors.py": "inline stubs, not yet on write_stub",
    "test_park_issue_process.py": "inline stubs, not yet on write_stub",
    "test_parked_issues_process.py": "inline stubs, not yet on write_stub",
    "test_pin_fast_tier_process.py": "inline stubs, not yet on write_stub",
    "test_pinned_scripts_process.py": "inline stubs, not yet on write_stub",
    "test_pr_ready_process.py": "inline stubs, not yet on write_stub",
    "test_profile.py": "inline stubs, not yet on write_stub",
    "test_pytest_leg_process.py": "inline stubs, not yet on write_stub",
    "test_queued_merge_process.py": "inline stubs, not yet on write_stub",
    "test_ready_check_process.py": "inline stubs, not yet on write_stub",
    "test_rebase_graded_only_process.py": "inline stubs, not yet on write_stub",
    "test_rebase_onto_default_process.py": "inline stubs, not yet on write_stub",
    "test_recipe_one_pytest_process.py": "inline stubs, not yet on write_stub",
    "test_report_process.py": "inline stubs, not yet on write_stub",
    "test_restore_production_process.py": "inline stubs, not yet on write_stub",
    "test_run_conductor_process.py": "inline stubs, not yet on write_stub",
    "test_run_finished_process.py": "inline stubs, not yet on write_stub",
    "test_run_leaf_process.py": "inline stubs, not yet on write_stub",
    "test_shim_interpreter_floor_process.py": "inline stubs, not yet on write_stub",
    "test_shim_interpreter_guard_process.py": "inline stubs, not yet on write_stub",
    "test_shims_process.py": "inline stubs, not yet on write_stub",
    "test_skill_ci_conflict.py": "inline stubs, not yet on write_stub",
    "test_skill_ci_conflict_graded_process.py": "inline stubs, not yet on write_stub",
    "test_skill_draft_pr_refused_repair_process.py": "inline stubs, not yet on write_stub",
    "test_skill_edit_step_process.py": "inline stubs, not yet on write_stub",
    "test_skill_leaf_env.py": "inline stubs, not yet on write_stub",
    "test_stale_bytecode_process.py": "inline stubs, not yet on write_stub",
    "test_status_refresh_scope_process.py": "inline stubs, not yet on write_stub",
    "test_status_report_refresh_process.py": "inline stubs, not yet on write_stub",
    "test_stop_run_process.py": "inline stubs, not yet on write_stub",
    "test_suite_red_resume_process.py": "inline stubs, not yet on write_stub",
    "test_suite_reported_process.py": "inline stubs, not yet on write_stub",
    "test_supervise_process.py": "inline stubs, not yet on write_stub",
    "test_tick_issue_criterion_process.py": "inline stubs, not yet on write_stub",
    "test_venv_python.py": "inline stubs, not yet on write_stub",
    "test_verdict_chain.py": "inline stubs, not yet on write_stub",
    "test_verify_process.py": "inline stubs, not yet on write_stub",
    "test_watch_process.py": "inline stubs, not yet on write_stub",
    "test_watch_runs_process.py": "inline stubs, not yet on write_stub",
    "unit/test_affected_suites.py": "inline stubs, not yet on write_stub",
    "unit/test_comment.py": "inline stubs, not yet on write_stub",
    "unit/test_issue_worktree.py": "inline stubs, not yet on write_stub",
    "unit/test_launch_floor.py": "inline stubs, not yet on write_stub",
    "unit/test_missing_argument_cli.py": "inline stubs, not yet on write_stub",
    "unit/test_prompt_test_tiers.py": "inline stubs, not yet on write_stub",
    "unit/test_scripts_md_rows.py": "inline stubs, not yet on write_stub",
    "unit/test_session_env.py": "inline stubs, not yet on write_stub",
    "unit/test_shims.py": "inline stubs, not yet on write_stub",
    "unit/test_skill_reference_usage.py": "inline stubs, not yet on write_stub",
    "unit/test_unreachable.py": "inline stubs, not yet on write_stub",
}

EXEMPT = ("stub_script.py",)


def _files_holding_an_inline_stub(tests_py_index):
    return sorted(path for path, entry in (
        ("/".join(entry.path.parts[entry.path.parts.index("py") + 1:]), entry) for entry in tests_py_index)
        if path not in EXEMPT and holds_an_inline_stub(entry.text))


def test_the_list_is_sorted():
    paths = list(FILES_WITH_AN_INLINE_STUB)

    assert paths == sorted(paths)


@pytest.mark.parametrize("source, holds", [
    ('STUB = "#!/bin/sh\\nexit 0\\n"\n', True),
    ('def f(p):\n    p.write_text(f"#!/bin/sh\\necho {p}\\n")\n', True),
    ('# a stub starts "#!/bin/sh"\nX = 1\n', False),
    ('X = "a #!/bin/sh in the middle"\n', False),
    ('X = "#!/usr/bin/env bash\\n"\n', False),
], ids=["literal", "f-string", "comment", "mid-string", "bash"])
def test_4052_a_string_literal_starting_the_sh_header_counts_and_a_comment_or_another_header_does_not(source, holds):
    assert holds_an_inline_stub(source) is holds


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_4052_no_test_file_outside_the_list_holds_an_inline_stub(tests_py_index):
    unlisted = [path for path in _files_holding_an_inline_stub(tests_py_index) if path not in FILES_WITH_AN_INLINE_STUB]

    assert not unlisted, (
        f"{unlisted} write their own #!/bin/sh stub: use stub_script.write_stub(path, body) instead. "
        f"FILES_WITH_AN_INLINE_STUB only shrinks, never add to it")


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_4052_a_listed_file_that_no_longer_holds_an_inline_stub_is_removed_from_the_list(tests_py_index):
    found = _files_holding_an_inline_stub(tests_py_index)
    gone = [path for path in FILES_WITH_AN_INLINE_STUB if path not in found]

    assert not gone, f"{gone} no longer hold an inline #!/bin/sh stub: remove them from FILES_WITH_AN_INLINE_STUB"
