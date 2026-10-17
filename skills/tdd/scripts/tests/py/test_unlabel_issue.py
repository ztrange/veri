"""In-process case for veri/unlabel_issue.py, the module unlabel-issue.sh is a shim over."""
import importlib
import subprocess


def test_main_1656_removes_the_opt_in_label_so_the_issue_is_unlisted_and_a_label_already_absent_exits_0(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    labels = {"7": {"ready-for-agent", "bug"}, "8": {"bug"}}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        joined = " ".join(args)
        if args[:3] == ["gh", "api", "-X"] and args[3] == "DELETE":
            number, _, name = args[4].partition("/issues/")[2].partition("/labels/")
            if name not in labels[number]:
                return subprocess.CompletedProcess(args, 1, "", "gh: Label does not exist (HTTP 404)\n")
            labels[number].discard(name)
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:3] == ["gh", "issue", "edit"] and "--remove-label" in args:
            labels[args[3]].discard(args[args.index("--remove-label") + 1])
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected call: %s" % joined)

    monkeypatch.setattr(subprocess, "run", fake_run)

    carrying = unlabel_issue.main(["7"])
    carrying_left = set(labels["7"])
    bare = unlabel_issue.main(["8"])

    assert (carrying, carrying_left, bare, labels["8"], capsys.readouterr().err) == (0, {"bug"}, 0, {"bug"}, "")
