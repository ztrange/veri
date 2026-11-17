"""In-process cases for veri/pr_ready_wait.py, the module pr-ready-wait.sh is a shim over (PRD 027.10, #4032)."""
import importlib
import os

import pytest

URL = "https://github.com/o/r/pull/42"
HEAD = "a" * 40


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout) or (code, stdout, {redirected path: its text})."""

    def __init__(self, answers=None):
        self.answers, self.calls = dict(answers or {}), []

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), answer in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                for path, text in (answer[2] if len(answer) > 2 else {}).items():
                    with open(os.path.join(cwd, path), "w") as f:
                        f.write(text)
                return answer[0], answer[1], ""
        if base == "gh":
            return 0, URL + "\n", ""
        if base == "git" and args[:1] == ("branch",):
            return 0, "tdd/12-thing\n", ""
        if base == "git" and args[:1] == ("rev-parse",):
            return 0, HEAD + "\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def made(self, base):
        return [c for c in self.calls if c[0] == base]


@pytest.fixture
def ready(monkeypatch, run_cli, tmp_path):
    """ready(answers=None, fake=None, missing=(), argv=None) runs pr-ready-wait for issue 12 from the main tree, the
    run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    pr_ready_wait = importlib.import_module("veri.pr_ready_wait")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=None):
        if "preflight" not in missing:
            (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(pr_ready_wait, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4032_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(ready):
    code, out, err, fake = ready(argv=())

    assert (code, "pr-ready-wait.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.pr_ready_wait").__file__)
    assert os.path.exists(os.path.join(here, "..", "pr-ready-wait.sh"))


def test_4032_a_missing_preflight_is_exit_2_before_any_inner_call_named_on_stderr(ready):
    code, out, err, fake = ready(missing=("preflight",))

    assert (code, fake.calls) == (2, [])
    assert ".tdd/issue-12-preflight" in err
