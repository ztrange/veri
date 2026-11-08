"""Guard: every script an operator skill names answers --help with exit 0 and its usage on stdout."""
import importlib
import re

import pytest

from conftest import ROOT, SCRIPTS

NAME = re.compile(r"[A-Za-z0-9_-]+\.sh\b")
MODULE = re.compile(r"veri/([a-z0-9_]+)\.py")


def named_scripts():
    sources = [ROOT / "operator" / "PRINCIPLES.md"]
    sources += [skill for skill in sorted((ROOT / "skills").glob("*/SKILL.md"))
                if "operator/PRINCIPLES.md" in skill.read_text()]
    names = set()
    for source in sources:
        names.update(NAME.findall(source.read_text()))
    return sorted(name for name in names if (SCRIPTS / name).is_file())


@pytest.mark.tree_audit("reads operator/PRINCIPLES.md and every skills/*/SKILL.md, and globs skills")
def test_every_script_an_operator_skill_names_answers_help_with_exit_0_and_usage_on_stdout(run_cli):
    failures = []
    names = named_scripts()
    assert names
    for name in names:
        found = MODULE.search((SCRIPTS / name).read_text())
        if found is None:
            failures.append("%s: no veri module behind the shim" % name)
            continue
        code, out, _ = run_cli(importlib.import_module("veri." + found.group(1)), ["--help"])
        if code != 0 or "usage" not in out.lower():
            failures.append("%s: exit %s, stdout %r" % (name, code, out[:60]))
    assert failures == []
