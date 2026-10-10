"""The one check that every top-level skills/tdd/scripts/*.sh is the canonical shim over a module under veri/."""
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
