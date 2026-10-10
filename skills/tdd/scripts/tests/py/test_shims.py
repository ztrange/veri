"""The one check that every top-level skills/tdd/scripts/*.sh is the canonical shim over a module under veri/."""
from conftest import shim_problems


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
