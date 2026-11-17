"""In-process cases for veri/run_done.py, the module run-done.sh is a shim over (PRD 027.12, #4034)."""
import importlib
import os

import pytest


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout). stop-requested.sh exits 3 (no request) unless answered."""

    def __init__(self, answers=None):
        self.answers, self.calls = dict(answers or {}), []

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "stop-requested.sh" and not args:
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]


@pytest.fixture
def done(monkeypatch, run_cli, tmp_path):
    """done(answers=None, fake=None, missing=(), argv=None) runs run-done for issue 12 from the main tree, the run's
    worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    run_done = importlib.import_module("veri.run_done")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=None):
        if "preflight" not in missing:
            (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(run_done, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4034_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(done):
    code, out, err, fake = done(argv=())

    assert (code, "run-done.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.run_done").__file__)
    assert os.path.exists(os.path.join(here, "..", "run-done.sh"))


def test_4034_a_missing_preflight_is_exit_2_before_any_inner_call_named_on_stderr(done):
    code, out, err, fake = done(missing=("preflight",))

    assert (code, fake.calls) == (2, [])
    assert ".tdd/issue-12-preflight" in err


TREE = ("git", ("status", "--porcelain", "--untracked-files=all"))


@pytest.mark.parametrize("asked, said, cleared", [(3, "", "0"), (0, "now\n", "1"), (2, "", "1")],
                         ids=["no stop request", "a stop request", "a malformed request"])
def test_4034_it_asks_for_a_stop_posts_the_done_comment_clears_a_reported_request_and_settles(done, asked, said,
                                                                                               cleared):
    code, out, err, fake = done(answers={("stop-requested.sh", "--clear"): (0, ""),
                                         ("stop-requested.sh", None): (asked, said)})

    clear = [("stop-requested.sh", ("--clear",))] if cleared == "1" else []
    assert [(c[0], c[1]) for c in fake.calls] == [("stop-requested.sh", ()), TREE, ("comment.sh", ("12", "done"))] + clear
    lines = ["stop_requested=%d" % asked, "cleared=" + cleared]
    assert (code, out.splitlines()[-2:]) == (0, lines)
    assert (done.wt / ".tdd" / "issue-12-run-done").read_text() == "".join(line + "\n" for line in lines)
    assert all(c[2] == str(done.wt) for c in fake.calls)


def test_4034_a_dirty_tree_just_before_the_comment_stops_it_with_exit_1_and_no_comment(done):
    code, out, err, fake = done(answers={("git", "status"): (0, " M x.py\n")})

    assert (code, out.splitlines()[-1]) == (1, "stopped at 4 tree-check")
    assert "comment.sh" not in fake.names()


def test_4034_a_comment_with_no_answer_stops_it_with_exit_2_before_any_clear(done):
    code, out, err, fake = done(answers={("stop-requested.sh", None): (0, "now\n"), ("comment.sh", None): (2, "")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at 4 comment.sh 12 done exit 2")
    assert fake.calls[-1][0] == "comment.sh"
    assert not (done.wt / ".tdd" / "issue-12-run-done").exists()


def test_4034_a_clear_that_fails_stops_it_with_its_code(done):
    code, out, err, fake = done(answers={("stop-requested.sh", "--clear"): (2, ""),
                                         ("stop-requested.sh", None): (0, "now\n")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at 4 stop-requested.sh --clear exit 2")


def test_4034_it_never_merges_and_handles_no_refusal(done):
    import inspect
    module = importlib.import_module("veri.run_done")
    done(answers={("comment.sh", None): (2, "")})
    code, out, err, fake = done()

    assert code == 0 and fake.names() == ["stop-requested.sh", "git", "comment.sh"]
    assert "merge" not in inspect.getsource(module).replace("never merges", "")
    assert not {"event.sh", "classify-bail.sh", "preflight-refused.sh", "detach-leaf.sh", "gh"} & set(fake.names())


def test_4034_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr(done):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) == "git":
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, "ERR<%d>\n" % len(self.calls)

    code, out, err, fake = done(fake=Marked({("stop-requested.sh", None): (0, "now\n")}))

    lines = out.splitlines()
    assert code == 0
    for i, c in enumerate(fake.calls, 1):
        if c[0] == "git":
            continue
        named = lines[lines.index("OUT<%d>" % i) - 1]
        assert named.startswith(c[0]) and named.endswith(" exit 0") and "ERR<%d>" % i in err
