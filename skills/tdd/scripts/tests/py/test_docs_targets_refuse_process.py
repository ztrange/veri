"""Medium cases for the Makefile's docs targets inside a development run: make started for real over a scratch tree of tripwires."""
import os
import shutil
import subprocess

import pytest

from conftest import SCRIPTS

ROOT = SCRIPTS.parents[2]
TARGETS = ["docs", "docs-test", "docs-check", "docs-fresh"]
PYTHON_TRIPWIRE = 'import os\nwith open(os.environ["VERI_TRIPWIRE_LOG"], "a") as log:\n    log.write("%s\\n")\n'
SHELL_TRIPWIRE = '#!/bin/sh\nprintf "ran a documentation suite\\n" >> "$VERI_TRIPWIRE_LOG"\necho "1 passed, 0 failed"\n'


def tree_with_tripwires(tmp_path):
    tree = tmp_path / "tree"
    (tree / "docs" / "tests").mkdir(parents=True)
    shutil.copy(ROOT / "Makefile", tree / "Makefile")
    (tree / "docs" / "build-walkthrough.py").write_text(PYTHON_TRIPWIRE % "built the page")
    (tree / "docs" / "check-walkthrough.py").write_text(PYTHON_TRIPWIRE % "checked the page is fresh")
    suite = tree / "docs" / "tests" / "tripwire.test.sh"
    suite.write_text(SHELL_TRIPWIRE)
    suite.chmod(0o755)
    return tree


def run_target(tree, log, target, test_cmd):
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if k != "VERI_TEST_CMD"}
    env["VERI_TRIPWIRE_LOG"] = str(log)
    if test_cmd is not None:
        env["VERI_TEST_CMD"] = test_cmd
    ran = subprocess.run(["make", "-C", str(tree), target], env=env, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    return ran.returncode, log.read_text(), ran.stdout, ran.stderr


@pytest.mark.process("make started for each docs target over a scratch tree of tripwires")
def test_with_veri_test_cmd_make_test_make_docs_docs_test_docs_check_and_docs_fresh_each_exit_2_without_running_anything_and_say_why_on_stderr(tmp_path):
    tree, log = tree_with_tripwires(tmp_path), tmp_path / "ran.log"
    refused = {}
    for target in TARGETS:
        premise = run_target(tree, log, target, None)
        assert premise[0] == 0 and premise[1], "premise broke: 'make %s' with VERI_TEST_CMD unset: %r" % (target, premise)
        code, ran, out, err = run_target(tree, log, target, "make test")
        refused[target] = (code, ran, "VERI_TEST_CMD" in err)
    assert refused == {target: (2, "", True) for target in TARGETS}


@pytest.mark.process("make started for each docs target over a scratch tree of tripwires")
def test_with_veri_test_cmd_unset_or_set_to_make_docs_test_make_docs_docs_test_docs_check_and_docs_fresh_each_run_as_before(tmp_path):
    tree, log = tree_with_tripwires(tmp_path), tmp_path / "ran.log"
    results = {}
    for test_cmd in (None, "make docs-test"):
        for target in TARGETS:
            code, ran, out, err = run_target(tree, log, target, test_cmd)
            results[(test_cmd, target)] = (code, bool(ran))
    assert results == {(c, t): (0, True) for c in (None, "make docs-test") for t in TARGETS}
