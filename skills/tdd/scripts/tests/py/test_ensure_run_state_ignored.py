"""In-process cases for veri/ensure_run_state_ignored.py, the module ensure-run-state-ignored.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

RULE = ".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md\n"


@pytest.fixture
def ensure_run_state_ignored():
    return importlib.import_module("veri.ensure_run_state_ignored")


def fake_rev_parse(monkeypatch, code, stdout):
    """subprocess.run answering `git -C <root> rev-parse --git-common-dir` with <code> and <stdout>."""
    def fake_run(args, **kwargs):
        if list(args[:2]) != ["git", "-C"] or list(args[3:]) != ["rev-parse", "--git-common-dir"]:
            raise AssertionError("unexpected command: %r" % (args,))
        captured = stdout if kwargs.get("stdout") == subprocess.PIPE else None
        if captured is not None and not kwargs.get("text"):
            captured = captured.encode()
        return subprocess.CompletedProcess(args, code, captured, None)

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_main_adds_the_rule_to_both_files_and_returns_2_when_rev_parse_fails(tmp_path, monkeypatch, capsys,
                                                                              ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    fake_rev_parse(monkeypatch, 0, ".git\n")

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (0, ("added\n", ""))
    assert (root / ".gitignore").read_text() == RULE
    assert (root / ".git" / "info" / "exclude").read_text() == RULE

    broken = tmp_path / "broken"
    (broken / ".git").mkdir(parents=True)
    fake_rev_parse(monkeypatch, 128, "")

    assert ensure_run_state_ignored.main([str(broken)]) == 2
    assert not (broken / ".gitignore").exists()
    assert not (broken / ".git" / "info" / "exclude").exists()


def test_main_does_not_refuse_a_gitignore_holding_other_lines_but_not_the_spec_line(tmp_path, monkeypatch, capsys,
                                                                                     ensure_run_state_ignored):
    fake_rev_parse(monkeypatch, 0, ".git\n")
    for name, original in (("node_modules", b"node_modules/\n"), ("non_utf8", b"\xff\xfe\n")):
        root = tmp_path / name
        (root / ".git").mkdir(parents=True)
        (root / ".gitignore").write_bytes(original)

        code = ensure_run_state_ignored.main([str(root)])

        assert (code, capsys.readouterr()[:]) == (0, ("added\n", ""))
        assert (root / ".gitignore").read_bytes() == original + RULE.encode()


def test_main_refuses_a_gitignore_holding_only_the_spec_line(tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git" / "info").mkdir(parents=True)
    (root / ".gitignore").write_bytes(b".tdd/issue-*-spec.md\n")
    (root / ".git" / "info" / "exclude").write_bytes(b"")
    fake_rev_parse(monkeypatch, 0, ".git\n")

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (2, ("", "ensure-run-state-ignored: %s/.gitignore carries veri's run-state "
                                                      "rule only in part, or with its lines out of order — fix it by "
                                                      "hand\n" % root))
    assert (root / ".gitignore").read_bytes() == b".tdd/issue-*-spec.md\n"
    assert (root / ".git" / "info" / "exclude").read_bytes() == b""


def test_main_reports_already_present_from_the_gitignore_alone_and_leaves_both_files_on_a_second_run(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    fake_rev_parse(monkeypatch, 0, ".git\n")
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    assert ensure_run_state_ignored.main([str(root)]) == 0
    capsys.readouterr()

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (0, ("already present\n", ""))
    assert (root / ".gitignore").read_text() == RULE
    assert (root / ".git" / "info" / "exclude").read_text() == RULE

    carried = tmp_path / "carried"
    (carried / ".git" / "info").mkdir(parents=True)
    (carried / ".gitignore").write_text(RULE)
    (carried / ".git" / "info" / "exclude").write_text("")

    code = ensure_run_state_ignored.main([str(carried)])

    assert (code, capsys.readouterr()[:]) == (0, ("already present\n", ""))
    assert (carried / ".gitignore").read_text() == RULE
    assert (carried / ".git" / "info" / "exclude").read_text() == RULE
