"""In-process cases for veri/unreachable.py, the module unreachable.sh is a shim over."""
import importlib
import pathlib
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def script(path, body):
    path.write_text("#!/usr/bin/env bash\n%s\n" % body)
    path.chmod(0o755)


def fixture_root(root):
    """<root> holding a Makefile, one git hook, a SKILL.md naming entry.sh, and entry.sh calling helper.sh."""
    scripts = root / "skills" / "tdd" / "scripts"
    hooks = root / "docs" / "hooks"
    scripts.mkdir(parents=True)
    hooks.mkdir(parents=True)
    (root / "Makefile").write_text("test:\n\t@echo ok\n")
    (hooks / "reference-transaction").write_text("#!/bin/sh\nexit 0\n")
    (root / "skills" / "tdd" / "SKILL.md").write_text("# skill\n\nRun `$S/entry.sh <n>` to start.\n")
    script(scripts / "entry.sh", '"$(dirname "$0")/helper.sh" "$@"')
    return scripts


def test_main_lists_an_orphan_and_returns_0_and_with_no_argument_returns_2_naming_its_usage(tmp_path, capsys):
    unreachable = importlib.import_module("veri.unreachable")
    scripts = fixture_root(tmp_path)
    script(scripts / "helper.sh", "echo helped")
    script(scripts / "orphan.sh", "echo alone")

    listed = unreachable.main([str(tmp_path)])
    listing = capsys.readouterr()
    refused = unreachable.main([])
    refusal = capsys.readouterr()

    assert (listed, listing.out, listing.err, refused, refusal.out, refusal.err) == (
        0, "orphan.sh\n", "", 2, "", "usage: unreachable.sh <repo-root>\n")


def test_main_with_an_empty_argument_returns_2_naming_its_usage(capsys):
    unreachable = importlib.import_module("veri.unreachable")

    refused = unreachable.main([""])
    refusal = capsys.readouterr()

    assert (refused, refusal.out, refusal.err) == (2, "", "usage: unreachable.sh <repo-root>\n")
