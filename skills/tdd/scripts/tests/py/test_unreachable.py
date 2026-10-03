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


def test_main_does_not_list_scripts_reached_from_a_procedure_file_a_recipe_or_a_hook_and_needs_no_hooks_or_lib_directory(tmp_path, capsys):
    unreachable = importlib.import_module("veri.unreachable")
    kinds = tmp_path / "kinds"
    scripts = fixture_root(kinds)
    (scripts / "lib").mkdir()
    script(scripts / "helper.sh", "echo helped")
    with (kinds / "skills" / "tdd" / "SKILL.md").open("a") as f:
        f.write("\nEach leaf follows `WORKER.md`.\n")
    (kinds / "skills" / "tdd" / "WORKER.md").write_text("# worker\n\nRun `$S/by-procedure.sh`.\n")
    (kinds / "Makefile").write_text("test:\n\t@echo ok\n\ncheck:\n\tskills/tdd/scripts/by-make.sh\n")
    script(scripts / "by-make.sh", '"$(dirname "$0")/chained-make.sh" "$@"')
    script(scripts / "chained-make.sh", "echo chained")
    (kinds / "docs" / "hooks" / "reference-transaction").write_text("#!/bin/sh\nskills/tdd/scripts/by-hook.sh\n")
    script(scripts / "by-hook.sh", 'source "$(dirname "$0")/lib/via-lib.sh"')
    (scripts / "lib" / "via-lib.sh").write_text('via_lib() { "$S/by-lib.sh"; }\n')
    script(scripts / "by-procedure.sh", "echo procedure")
    script(scripts / "by-lib.sh", "echo lib")
    script(scripts / "orphan.sh", "echo alone")
    no_hooks = tmp_path / "no-hooks"
    scripts = fixture_root(no_hooks)
    hook = no_hooks / "docs" / "hooks" / "reference-transaction"
    hook.unlink()
    hook.parent.rmdir()
    script(scripts / "helper.sh", "echo helped")
    script(scripts / "orphan.sh", "echo alone")
    no_lib = tmp_path / "no-lib"
    scripts = fixture_root(no_lib)
    script(scripts / "helper.sh", '"$(dirname "$0")/lib.sh" "$@"')
    script(scripts / "lib.sh", "echo lib")
    script(scripts / "orphan.sh", "echo alone")

    answers = []
    for root in (kinds, no_hooks, no_lib):
        code = unreachable.main([str(root)])
        listing = capsys.readouterr()
        answers.append((code, listing.out, listing.err))

    assert answers == [(0, "orphan.sh\n", "")] * 3


def test_main_does_not_list_a_script_or_procedure_file_named_only_through_a_built_path(tmp_path, capsys):
    unreachable = importlib.import_module("veri.unreachable")
    plain = tmp_path / "plain"
    scripts = fixture_root(plain)
    script(scripts / "helper.sh", 'for kind in red green; do\n  "$(dirname "$0")/build-$kind-prompt.sh" "$@"\ndone')
    script(scripts / "build-red-prompt.sh", "echo red")
    script(scripts / "build-green-prompt.sh", "echo green")
    script(scripts / "orphan.sh", "echo alone")
    braced = tmp_path / "braced"
    scripts = fixture_root(braced)
    script(scripts / "helper.sh", 'for kind in red green; do\n  "$(dirname "$0")/build-${kind}-prompt.sh" "$@"\ndone')
    script(scripts / "build-red-prompt.sh", "echo red")
    script(scripts / "orphan.sh", "echo alone")
    procedure = tmp_path / "procedure"
    scripts = fixture_root(procedure)
    (procedure / "skills" / "tdd" / "SKILL.md").write_text(
        "# skill\n\nRun `$S/entry.sh <n>`, then read `prompts/develop-$phase.md`.\n")
    (procedure / "skills" / "tdd" / "develop-red.md").write_text("Run `$S/target.sh`.\n")
    script(scripts / "helper.sh", "echo helped")
    script(scripts / "target.sh", "echo target")
    script(scripts / "orphan.sh", "echo alone")

    answers = []
    for root in (plain, braced, procedure):
        code = unreachable.main([str(root)])
        listing = capsys.readouterr()
        answers.append((code, listing.out, listing.err))

    assert answers == [(0, "orphan.sh\n", "")] * 3
