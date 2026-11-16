"""Every shim-fronted module declares `USAGE`, so `--help` is answered by entry and never runs the script."""
import ast
import importlib
import os
import re
import socket
import subprocess

import pytest

from conftest import SCRIPTS

SHIM_EXEC = re.compile(r'^exec (?:python3|"\$py") .*/veri/([\w-]+)\.py"', re.MULTILINE)

# Shims whose module is owned by an open PR and so cannot be edited here; none today. A ratchet: it may shrink, never grow.
EXEMPT = {}


def fronted():
    """(shim name, module name) of every shim that execs a veri/ module, in shim order."""
    return [(shim.name, match.group(1)) for shim in sorted(SCRIPTS.glob("*.sh"))
            if (match := SHIM_EXEC.search(shim.read_text()))]


def declared_usage(module):
    """The module's top-level `USAGE` as text: the literal, or "" when it is built at import; None when it declares none."""
    for node in ast.parse((SCRIPTS / "veri" / (module + ".py")).read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "USAGE" for t in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                return ""
            return value.decode() if isinstance(value, bytes) else str(value)
    return None


@pytest.mark.tree_audit("every shim of skills/tdd/scripts")
def test_every_shim_fronted_module_declares_a_usage_that_opens_with_its_shims_name():
    assert len(fronted()) >= 60
    # entry prints from the first `usage: `, so a `<name>: ` lead-in (refactor-owed: usage: …) is allowed before it.
    form = {shim: re.compile(rf"(?:[\w.-]+: )?usage: {re.escape(shim)}") for shim, _ in fronted()}
    wrong = [f"{shim}: {module}.py USAGE does not start with `usage: {shim}`" for shim, module in fronted()
             if shim not in EXEMPT and (usage := declared_usage(module)) is not None
             and usage != "" and not form[shim].match(usage.lstrip())]
    wrong += [f"{shim}: {module}.py declares no USAGE" for shim, module in fronted()
              if shim not in EXEMPT and declared_usage(module) is None]

    assert not wrong, "\n".join(wrong)


@pytest.fixture
def no_work(monkeypatch):
    """Any process launch or network access during the case is recorded, and the case fails on it.

    The tier's own guards are not enough to rely on: small_case_guard refuses only git and a python3 outside veri/, and
    network_guard only gh, curl and a non-loopback connect, so `claude`, `sh` or a loopback socket would pass them. This
    refuses every Popen (subprocess.run and call go through it), os.system, fork, exec and spawn, and every connect.
    """
    attempts = []

    def forbid(what):
        def refused(*args, **kwargs):
            attempts.append(what)
            raise AssertionError(f"--help started work: {what}")
        return refused

    monkeypatch.setattr(subprocess.Popen, "__init__", forbid("subprocess.Popen"))
    monkeypatch.setattr(socket.socket, "connect", forbid("socket.connect"))
    monkeypatch.setattr(socket, "create_connection", forbid("socket.create_connection"))
    for name in ("system", "fork", "execv", "execve", "execvp", "execvpe", "posix_spawn", "posix_spawnp", "spawnv", "spawnve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, forbid("os." + name))
    return attempts


@pytest.mark.parametrize("shim,module", fronted(), ids=[shim for shim, _ in fronted()])
def test_help_prints_the_usage_on_stdout_exits_0_and_starts_no_process_and_no_connection(
        shim, module, run_cli, no_work):
    imported = importlib.import_module("veri." + module)
    code, out, err = run_cli(imported, ["--help"])

    assert (code, err, no_work) == (0, "", [])
    declared = imported.USAGE.decode() if isinstance(imported.USAGE, bytes) else imported.USAGE
    assert out.startswith("usage: ") and out.startswith(f"usage: {shim}")
    assert out.rstrip("\n") == declared[declared.index("usage: "):].rstrip("\n")


# Scripts that take no arguments and refuse one; unit/test_zero_argument_modules_refuse_an_argument.py fails for any module that should be here and is not.
NO_ARGUMENTS = ["branch_suite", "cover_outcome", "exhausted_outcome", "extract_result", "invisible_work",
                "leaf_launchable", "next_pending_refactor", "next_unchecked", "parse_verdict",
                "rebased_tip_suite", "refactor_triage", "resume_clean", "skill_drift", "time_budget"]


@pytest.mark.parametrize("module", NO_ARGUMENTS)
def test_a_script_that_takes_no_arguments_refuses_one_naming_it_and_starts_no_process(module, run_cli, no_work):
    imported = importlib.import_module("veri." + module)
    shim = module.replace("_", "-") + ".sh"
    code, out, err = run_cli(imported, ["bogus"])

    assert (code, out, no_work) == (2, "", [])
    assert err == f"{shim}: unexpected argument 'bogus'\n{imported.USAGE}\n"
