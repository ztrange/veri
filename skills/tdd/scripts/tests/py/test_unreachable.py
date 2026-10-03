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


def test_main_lists_orphans_chained_orphans_and_tail_names_and_takes_only_bounded_names_as_mentions(tmp_path, capsys):
    unreachable = importlib.import_module("veri.unreachable")
    orphans = tmp_path / "orphans"
    scripts = fixture_root(orphans)
    script(scripts / "helper.sh", "echo helped")
    script(scripts / "orphan-top.sh", '"$(dirname "$0")/orphan-leaf.sh" "$@"')
    script(scripts / "orphan-leaf.sh", '"$(dirname "$0")/orphan-top.sh" --again')
    tail = tmp_path / "tail"
    scripts = fixture_root(tail)
    script(scripts / "helper.sh", '"$(dirname "$0")/run-leaf.sh" "$@"')
    script(scripts / "run-leaf.sh", "echo ran")
    script(scripts / "leaf.sh", "echo alone")
    bounds = tmp_path / "bounds"
    scripts = fixture_root(bounds)
    script(scripts / "helper.sh",
           "kept.sh\n# xleaf.sh 2leaf.sh my_leaf.sh v2.leaf.sh leaf.shx leaf.sh2 leaf.sh_old leaf.sh-old")
    script(scripts / "kept.sh", "echo kept")
    script(scripts / "leaf.sh", "echo alone")

    answers = []
    for root in (orphans, tail, bounds):
        code = unreachable.main([str(root)])
        answers.append((code, capsys.readouterr().out))

    assert answers == [(0, "orphan-leaf.sh\norphan-top.sh\n"), (0, "leaf.sh\n"), (0, "leaf.sh\n")]
