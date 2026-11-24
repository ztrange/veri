"""The ratchet over a leaf's allow-list (PRD 022.5): every environment variable a script a leaf may run reads by
literal name passes `run_leaf.leaf_passes`, or is named in NOT_A_LEAFS_INPUT with the reason it needs not.

How the reads are found: a leaf runs veri's modules (its scripts are shims onto them) and the Makefile's `test` and
`unit` recipes, so the sweep reads every module under `veri/` for `environ`/`env`/`environment()` subscripts and
`.get`/`.pop`/`.setdefault` calls, `tunables.<reader>("NAME")` calls and `"NAME" in os.environ` tests, each keyed by a
string literal, and the Makefile for `$${NAME}`/`$$NAME`. A read keyed by a variable is the tunables reader's, whose
names are all `VERI_*` or `REVISE_BUDGET` (`tunables.TUNABLES`)."""
import importlib
import re

import pytest

from conftest import ROOT

READS = re.compile(r'(?:\benviron|\benv|environment\(\))(?:\.get|\.pop|\.setdefault)?[\[(]"([A-Z][A-Za-z0-9_]*)"'
                   r'|\btunables\.[a-z_]+\("([A-Z][A-Za-z0-9_]*)"'
                   r'|"([A-Z][A-Za-z0-9_]*)" (?:not )?in os\.environ')
MAKE_READS = re.compile(r"\$\$\{?([A-Z][A-Z0-9_]*)")

NOT_A_LEAFS_INPUT = {
    "CLAUDE_CODE_SESSION_ID": "the conductor's session id, stripped from a leaf on purpose (session_env)",
    "PYTEST_LEG_SERIAL_SEEN": "set by pytest_leg for the pytest it starts, never read from its caller",
    "PYTEST_PLUGINS": "set by pytest_leg for the pytest it starts",
    "PYTEST_XDIST_WORKER": "set by pytest-xdist in its own workers",
    "GIT_SSH_COMMAND": "read by ready_check, which only the conductor runs before a push",
    "GIT_SSH": "read by ready_check, which only the conductor runs before a push",
    "PYTEST_LEG_FULL_LOCK_HOLDER": "set by a full run for the runs nested in it; no leaf is launched inside one",
    "OFFLINE_REAL_GIT": "set by the Makefile for the make it nests; unset, the recipe finds git itself",
    "BASH_VERSION": "a shell variable bash sets, not an environment input",
    "BASH_VERSINFO": "a shell variable bash sets, not an environment input",
    "CLAUDE_CODE_REMOTE": "read by cloud_setup, which only a cloud session's SessionStart hook runs, never a leaf",
    "CLAUDE_ENV_FILE": "read by cloud_setup, which only a cloud session's SessionStart hook runs, never a leaf",
}


def unpassed(names, run_leaf):
    return sorted(name for name in set(names) if not run_leaf.leaf_passes(name) and name not in NOT_A_LEAFS_INPUT)


@pytest.mark.tree_audit("every module under veri/ and the Makefile")
def test_3976_every_environment_variable_a_leafs_scripts_read_by_name_passes_the_allow_list_or_is_exempt_by_reason(
        veri_modules_index):
    run_leaf = importlib.import_module("veri.run_leaf")
    names = [match for name in veri_modules_index.names for found in READS.findall(veri_modules_index.text(name))
             for match in found if match]
    names += MAKE_READS.findall((ROOT / "Makefile").read_text())
    assert unpassed(names, run_leaf) == []


def test_3976_the_ratchet_names_a_read_the_allow_list_does_not_pass():
    run_leaf = importlib.import_module("veri.run_leaf")
    source = 'os.environ.get("GH_TOKEN"); tunables.read("JAVA_HOME"); env["PATH"]; "AWS_X" in os.environ'
    names = [match for found in READS.findall(source) for match in found if match]
    assert unpassed(names, run_leaf) == ["AWS_X", "GH_TOKEN", "JAVA_HOME"]
