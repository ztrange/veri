"""Unit tests for py/push_branch.py — in-process: `run`, `run_stdout`, `sleep_for` and
`record` are replaced by spies, so no git, sleep or event.sh process starts. Covers what
tests/unit/push-branch.test.sh covered (bad tunable, the failed-push path end to end) and
the rest of the integration suite's contract (retries, backoff doubling, rejection,
second-attempt success, an event write that fails)."""
import io
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import push_branch as pb  # noqa: E402


class Harness:
    """Spies for every process the script would start, scripted per test."""

    def __init__(self, push_results, ls_remote="", branch="tdd/1-x"):
        self.calls = []
        self.push_results = list(push_results)
        self.ls_remote = ls_remote
        self.branch = branch

    def run(self, argv):
        self.calls.append(argv)
        return self.push_results.pop(0)

    def run_stdout(self, argv):
        self.calls.append(argv)
        return self.branch if argv[1] == "rev-parse" else self.ls_remote

    def sleep_for(self, seconds):
        self.calls.append(["sleep", seconds])

    def record(self, event, *pairs):
        self.calls.append(["record", event, *pairs])

    def main(self, environ):
        err = io.StringIO()
        with mock.patch.multiple(pb, run=self.run, run_stdout=self.run_stdout,
                                 sleep_for=self.sleep_for, record=self.record):
            code = pb.main(environ, err)
        return code, err.getvalue()


UNREACHABLE = (128, "fatal: unable to access origin")


class TunableTests(unittest.TestCase):
    def test_bad_retries_exits_2_before_any_push(self):
        h = Harness([])
        code, err = h.main({"VERI_PUSH_RETRIES": "x", "VERI_PUSH_BACKOFF": "0"})
        self.assertEqual(code, 2)
        self.assertEqual(err, "push-branch.sh: VERI_PUSH_RETRIES must be a non-negative integer, got 'x'\n")
        self.assertEqual(h.calls, [])

    def test_fractional_backoff_exits_2(self):
        h = Harness([])
        code, err = h.main({"VERI_PUSH_BACKOFF": "1.5"})
        self.assertEqual(code, 2)
        self.assertEqual(err, "push-branch.sh: VERI_PUSH_BACKOFF must be a non-negative integer, got '1.5'\n")

    def test_set_but_empty_tunable_takes_the_default(self):
        # bash `${VERI_PUSH_RETRIES:-3}`: empty is unset.
        self.assertEqual(pb.read_tunables({"VERI_PUSH_RETRIES": "", "VERI_PUSH_BACKOFF": ""}, io.StringIO()), (3, 2))


class FailedPushTests(unittest.TestCase):
    def test_one_retry_runs_two_pushes_one_wait_one_event_exit_0(self):
        # the bash unit suite's case 3, in-process
        h = Harness([UNREACHABLE, UNREACHABLE])
        code, err = h.main({"VERI_PUSH_RETRIES": "1"})
        self.assertEqual(code, 0)
        self.assertEqual(err, "push-branch.sh: push failed after 2 attempts; the branch is not on the remote\n")
        self.assertEqual(h.calls, [
            ["git", "push", "--set-upstream", "origin", "HEAD"],
            ["sleep", 2],
            ["git", "push", "--set-upstream", "origin", "HEAD"],
            ["record", "push-failed", "error=fatal: unable to access origin", "attempts=2"],
        ])

    def test_default_retries_is_four_attempts(self):
        h = Harness([UNREACHABLE] * 4)
        code, _ = h.main({"VERI_PUSH_BACKOFF": "0"})
        self.assertEqual(code, 0)
        self.assertEqual(sum(1 for c in h.calls if c[:2] == ["git", "push"]), 4)

    def test_backoff_doubles_per_wait_and_none_after_the_last(self):
        h = Harness([UNREACHABLE] * 4)
        h.main({"VERI_PUSH_RETRIES": "3", "VERI_PUSH_BACKOFF": "1"})
        self.assertEqual([c[1] for c in h.calls if c[0] == "sleep"], [1, 2, 4])

    def test_zero_retries_pushes_once_and_never_sleeps(self):
        h = Harness([UNREACHABLE])
        code, err = h.main({"VERI_PUSH_RETRIES": "0"})
        self.assertEqual(code, 0)
        self.assertNotIn(["sleep", 2], h.calls)
        self.assertIn("after 1 attempts", err)


class SuccessTests(unittest.TestCase):
    def test_landing_push_exits_0_quietly_with_no_event(self):
        h = Harness([(0, "")])
        code, err = h.main({})
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(h.calls, [["git", "push", "--set-upstream", "origin", "HEAD"]])

    def test_second_attempt_landing_exits_0_with_no_event(self):
        h = Harness([UNREACHABLE, (0, "")])
        code, err = h.main({"VERI_PUSH_BACKOFF": "0"})
        self.assertEqual((code, err), (0, ""))
        self.assertFalse([c for c in h.calls if c[0] == "record"])


class RejectionTests(unittest.TestCase):
    REJECTED = (1, " ! [rejected]        HEAD -> tdd/1-x (non-fast-forward)\nerror: failed to push some refs")

    def test_non_fast_forward_exits_1_after_one_attempt_naming_the_remote_sha(self):
        h = Harness([self.REJECTED], ls_remote="abc123\trefs/heads/tdd/1-x")
        code, err = h.main({"VERI_PUSH_RETRIES": "3"})
        self.assertEqual(code, 1)
        self.assertEqual(err, "push rejected (non-fast-forward): origin/tdd/1-x is at abc123\n")
        self.assertEqual(sum(1 for c in h.calls if c[:2] == ["git", "push"]), 1)
        self.assertFalse([c for c in h.calls if c[0] == "sleep"])
        self.assertEqual(h.calls[-1], ["record", "push-rejected", "remote_sha=abc123", "error=" + self.REJECTED[1]])

    def test_rejected_without_a_known_cause_is_retried(self):
        h = Harness([(1, " ! [rejected] something else"), (0, "")])
        code, _ = h.main({"VERI_PUSH_BACKOFF": "0"})
        self.assertEqual(code, 0)

    def test_is_rejection_needs_both_halves(self):
        self.assertTrue(pb.is_rejection("[rejected] x fetch first"))
        self.assertTrue(pb.is_rejection("[rejected] stale info"))
        self.assertFalse(pb.is_rejection("non-fast-forward alone"))
        self.assertFalse(pb.is_rejection("[rejected] alone"))


class RecordTests(unittest.TestCase):
    def test_failing_event_write_exits_2(self):
        with mock.patch.object(pb.subprocess, "run", return_value=mock.Mock(returncode=1)):
            with self.assertRaises(SystemExit) as cm:
                pb.record("push-failed", "error=x")
        self.assertEqual(cm.exception.code, 2)

    def test_record_calls_event_sh_beside_the_scripts(self):
        with mock.patch.object(pb.subprocess, "run", return_value=mock.Mock(returncode=0)) as run:
            pb.record("push-failed", "error=x", "attempts=2")
        argv = run.call_args.args[0]
        self.assertEqual(argv[1:], ["push-failed", "error=x", "attempts=2"])
        self.assertEqual(os.path.basename(argv[0]), "event.sh")
        self.assertEqual(os.path.basename(os.path.dirname(argv[0])), "scripts")


if __name__ == "__main__":
    unittest.main()
