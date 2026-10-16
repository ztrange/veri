"""The one check that every top-level skills/tdd/scripts/*.sh is the canonical shim over a module under veri/."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS, shim_problems

EXEMPT = {
    "build-develop-prompt.sh": "a spelling difference; canonicalising it is a change of its own",
    "build-verify-prompt.sh": "a spelling difference; canonicalising it is a change of its own",
    "render-leaf-log.sh": "adding \"$@\" changes what a stray argument does, a behaviour change",
    "run-leaf.sh": "the locale preamble must act before the interpreter starts, so it cannot move into the module",
    "run-verdict.sh": "the locale preamble must act before the interpreter starts, so it cannot move into the module",
    "stop-run.sh": "records the caller's directory before anything can change it",
}


def shim(path, *lines):
    path.write_text("#!/bin/sh\n# %s — a shim.\n%s\n" % (path.name, "\n".join(lines)))


def test_shim_problems_names_each_script_with_logic_in_it_or_a_missing_module_and_passes_a_canonical_shim(tmp_path):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "kept.py").write_text("")
    shim(tmp_path / "canonical.sh", 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')
    shim(tmp_path / "logic.sh", 'export EXP_SHIM_WORD=1', 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')
    shim(tmp_path / "orphaned.sh", 'exec python3 "$(dirname "$0")/veri/gone.py" "$@"')

    problems = shim_problems(tmp_path)

    assert [line.split(":")[0] for line in problems] == ["logic.sh", "orphaned.sh"]
    assert "not the canonical shim" in problems[0]
    assert "veri/gone.py" in problems[1] and "does not exist" in problems[1]


@pytest.mark.tree_audit("every scripts/*.sh against the shim exemption table")
def test_the_exemption_table_lists_the_six_non_canonical_shims_with_a_reason_each_and_a_stale_row_fails_naming_the_script(tmp_path):
    assert shim_problems(SCRIPTS, EXEMPT) == []
    assert len(EXEMPT) == 6 and all(reason.strip() for reason in EXEMPT.values())

    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "kept.py").write_text("")
    shim(tmp_path / "canonical.sh", 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')
    shim(tmp_path / "preamble.sh", 'export EXP_SHIM_WORD=1', 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')

    problems = shim_problems(tmp_path, {"canonical.sh": "a reason", "preamble.sh": "a reason", "gone.sh": "a reason"})

    assert sorted(line.split(":")[0] for line in problems) == ["canonical.sh", "gone.sh"]
    assert all("stale exemption" in line for line in problems)


@pytest.mark.process("leaf-role.sh run through a symlink to the skills directory")
def test_a_shim_run_through_a_symlink_to_the_skills_directory_from_another_cwd_gives_its_modules_exit_code_and_stdout(
        run_cli, tmp_path):
    (tmp_path / "skills").symlink_to(SCRIPTS.parents[1], target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()

    ran = subprocess.run([str(tmp_path / "skills" / "tdd" / "scripts" / "leaf-role.sh"), "verify-green-2"],
                         cwd=tmp_path / "elsewhere", stdin=subprocess.DEVNULL, capture_output=True, text=True)
    code, out, _ = run_cli(importlib.import_module("veri.leaf_role"), ["verify-green-2"])

    assert (ran.returncode, ran.stdout) == (code, out) == (0, "VERI_ACTOR=verifier VERI_PHASE=green VERI_ATTEMPT=2\n")


def test_entry_bypass_problems_names_the_module_whose_main_block_exits_bare_as_module_and_line_and_passes_one_calling_entry_run(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "bare.sh", 'exec python3 "$(dirname "$0")/veri/bare.py" "$@"')
    shim(tmp_path / "wrapped.sh", 'exec python3 "$(dirname "$0")/veri/wrapped.py" "$@"')
    (tmp_path / "veri" / "bare.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main(sys.argv[1:]))\n")
    (tmp_path / "veri" / "wrapped.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    import entry\n    entry.run(main, sys.argv[1:])\n")

    problems = entry_bypass_problems(tmp_path)

    assert [line.split(" ")[0] for line in problems] == ["bare.py:8"]


def test_entry_bypass_problems_names_the_module_whose_single_quoted_main_test_block_exits_bare_as_module_and_line(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "quoted.sh", 'exec python3 "$(dirname "$0")/veri/quoted.py" "$@"')
    (tmp_path / "veri" / "quoted.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == '__main__':\n    sys.exit(main(sys.argv[1:]))\n")

    problems = entry_bypass_problems(tmp_path)

    assert [line.split(" ")[0] for line in problems] == ["quoted.py:8"]


def test_entry_bypass_problems_names_the_module_whose_only_entry_run_in_its_main_block_is_a_comment_as_module_and_line(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "commented.sh", 'exec python3 "$(dirname "$0")/veri/commented.py" "$@"')
    (tmp_path / "veri" / "commented.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    # entry.run(main)\n    sys.exit(main(sys.argv[1:]))\n")

    problems = entry_bypass_problems(tmp_path)

    assert [line.split(" ")[0] for line in problems] == ["commented.py:8"]


def test_entry_bypass_problems_reports_a_problem_for_a_scripts_tree_holding_no_shim(tmp_path):
    """Its subject is source text: a planted scripts tree with no shim in it, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    (tmp_path / "plain.txt").write_text("not a shim\n")

    problems = entry_bypass_problems(tmp_path)

    assert problems


def test_entry_bypass_problems_names_the_planted_bare_module_as_module_and_line_leaves_the_entry_run_one_alone_and_passes_once_the_offender_is_removed(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "probe-bare.sh", 'exec python3 "$(dirname "$0")/veri/probe_bare.py" "$@"')
    shim(tmp_path / "probe-entry.sh", 'exec python3 "$(dirname "$0")/veri/probe_entry.py" "$@"')
    (tmp_path / "veri" / "probe_bare.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main(sys.argv[1:]))\n")
    (tmp_path / "veri" / "probe_entry.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    import entry\n    entry.run(main, sys.argv[1:])\n")

    planted = entry_bypass_problems(tmp_path)
    (tmp_path / "probe-bare.sh").unlink()
    (tmp_path / "veri" / "probe_bare.py").unlink()
    removed = entry_bypass_problems(tmp_path)

    assert ([line.split(" ")[0] for line in planted], removed) == (["probe_bare.py:8"], [])
