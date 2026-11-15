"""A ratchet: test files defining their own subprocess fake do not grow in number; new cases use fake_processes."""
import ast

import pytest

# Test files that still define a local fake_run or fake_git (at any depth). Lower this number when you migrate a
# file to conftest's fake_processes (see its docstring); never raise it. A new case answers its processes with
# fake_processes.answers(...), which matches a command line, records the call and fails an unexpected one loudly.
FILES_WITH_A_LOCAL_PROCESS_FAKE = 29

LOCAL_FAKES = ("fake_run", "fake_git")


def _files_defining_a_local_process_fake():
    from conftest import SCRIPTS

    found = []
    for source in sorted((SCRIPTS / "tests" / "py").rglob("*.py")):
        tree = ast.parse(source.read_text())
        if any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in LOCAL_FAKES
               for node in ast.walk(tree)):
            found.append(str(source.relative_to(SCRIPTS / "tests" / "py")))
    return found


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_no_more_test_files_define_a_local_fake_run_or_fake_git_than_the_ratchet_allows():
    found = _files_defining_a_local_process_fake()

    assert len(found) <= FILES_WITH_A_LOCAL_PROCESS_FAKE, (
        f"{len(found)} test files define their own {' or '.join(LOCAL_FAKES)}, the ratchet allows "
        f"{FILES_WITH_A_LOCAL_PROCESS_FAKE}: answer processes with fake_processes.answers instead: {found}")


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_the_ratchet_is_lowered_to_the_number_of_files_still_defining_a_local_fake():
    found = _files_defining_a_local_process_fake()

    assert len(found) >= FILES_WITH_A_LOCAL_PROCESS_FAKE, (
        f"only {len(found)} test files still define a local fake, below the ratchet's "
        f"{FILES_WITH_A_LOCAL_PROCESS_FAKE}: lower FILES_WITH_A_LOCAL_PROCESS_FAKE to {len(found)}")
