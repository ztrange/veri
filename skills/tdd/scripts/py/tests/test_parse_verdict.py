"""Unit tests for py/parse_verdict.py — in-process, no subprocess. Every case the bash
integration suite (tests/parse-verdict.test.sh) holds the CLI to, plus the byte-level
edges the bash script's `read` loop and trims imply."""
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import parse_verdict as pv  # noqa: E402


class ParseTests(unittest.TestCase):
    def check(self, text, code, reason):
        got = pv.parse(text)
        self.assertEqual((got[0], got[1]), (code, reason))

    def test_pass_with_reason(self):
        self.check(
            "I ran the test and it failed as expected.\nVERDICT: PASS\n"
            "REASON: The test fails because slugify is undefined, which is the missing behavior.",
            0, "The test fails because slugify is undefined, which is the missing behavior.")

    def test_reject_with_reason(self):
        self.check("VERDICT: REJECT\nREASON: The test asserts on an internal helper, not observable behavior.",
                   1, "The test asserts on an internal helper, not observable behavior.")

    def test_no_verdict_is_malformed(self):
        code, reason, diag = pv.parse("I could not make up my mind about this test.")
        self.assertEqual((code, reason, diag), (2, "", "parse-verdict: no VERDICT: line found"))

    def test_last_verdict_wins(self):
        self.check("My first instinct was VERDICT: PASS but on reflection:\nVERDICT: REJECT\n"
                   "REASON: The failure is an ImportError from a typo, not the missing behavior.",
                   1, "The failure is an ImportError from a typo, not the missing behavior.")

    def test_case_insensitive(self):
        self.check("verdict: pass\nreason: Genuine pass — target test and full suite are green.",
                   0, "Genuine pass — target test and full suite are green.")

    def test_indented_verdict_line(self):
        self.check("   VERDICT: PASS\n   REASON: All good.", 0, "All good.")

    def test_multiline_reason_preserved(self):
        self.check("VERDICT: REJECT\nREASON: Two problems:\n- the test is over-coupled to the implementation\n"
                   "- it is also far too complex for one criterion",
                   1, "Two problems:\n- the test is over-coupled to the implementation\n"
                      "- it is also far too complex for one criterion")

    def test_reason_inline_after_verdict(self):
        self.check("VERDICT: REJECT — the test never actually runs the code under test",
                   1, "the test never actually runs the code under test")

    def test_unknown_verdict_word_is_malformed(self):
        code, reason, diag = pv.parse("VERDICT: MAYBE\nREASON: unsure")
        self.assertEqual((code, reason, diag), (2, "", "parse-verdict: unrecognised verdict word 'MAYBE'"))

    def test_fenced_verdict_block(self):
        self.check("I ran the test myself.\n```\nVERDICT: REJECT\n"
                   "REASON: The test asserts a constant and never calls slugify().\n```",
                   1, "The test asserts a constant and never calls slugify().")

    def test_multiline_reason_then_fence(self):
        self.check("VERDICT: REJECT\nREASON: Two problems:\n- vacuous assertion\n- no call to the function\n```",
                   1, "Two problems:\n- vacuous assertion\n- no call to the function")

    def test_new_step_lines_change_nothing(self):
        plain = ("I read the diff against the base sha.\nVERDICT: PASS\n"
                 "REASON: The transform is behaviour-preserving and the suite is green.")
        proposing = plain.replace("VERDICT:", "NEW_STEP: slugify returns an empty string for input "
                                              "that is all separators\nVERDICT:", 1)
        self.assertEqual(pv.parse(plain), pv.parse(proposing))

    # Edges of the bash `read` loop and its trims, not covered by the integration suite.
    def test_split_lines_matches_read_loop(self):
        self.assertEqual(pv.split_lines(""), [])
        self.assertEqual(pv.split_lines("\n"), [""])
        self.assertEqual(pv.split_lines("a\nb"), ["a", "b"])
        self.assertEqual(pv.split_lines("a\nb\n"), ["a", "b"])

    def test_empty_verdict_word_is_malformed(self):
        self.assertEqual(pv.parse("VERDICT:")[0], 2)
        self.assertEqual(pv.parse("VERDICT:")[2], "parse-verdict: unrecognised verdict word ''")

    def test_only_one_separator_is_stripped(self):
        self.check("VERDICT: PASS - - twice", 0, "- twice")

    def test_fence_alone_as_reason_is_empty(self):
        self.check("VERDICT: PASS\n~~~", 0, "")

    def test_unicode_case_fold_is_ascii_only(self):
        # U+017F folds to 's' under Unicode rules; bash's [Ss] never matched it.
        self.assertEqual(pv.parse("VERDICT: PAſſ")[0], 2)


class MainTests(unittest.TestCase):
    """main() writes bytes and returns the exit code; no process is started."""

    def run_main(self, data):
        stdin = io.TextIOWrapper(io.BytesIO(data))
        out, err = io.TextIOWrapper(io.BytesIO()), io.TextIOWrapper(io.BytesIO())
        code = pv.main(stdin, out, err)
        return code, out.buffer.getvalue(), err.buffer.getvalue()

    def test_pass_writes_reason_and_newline_to_stdout(self):
        self.assertEqual(self.run_main(b"VERDICT: PASS\nREASON: ok"), (0, b"ok\n", b""))

    def test_malformed_writes_diagnostic_to_stderr_only(self):
        self.assertEqual(self.run_main(b"nothing"), (2, b"", b"parse-verdict: no VERDICT: line found\n"))

    def test_invalid_utf8_round_trips(self):
        self.assertEqual(self.run_main(b"VERDICT: REJECT\nREASON: bad \xff byte"), (1, b"bad \xff byte\n", b""))


if __name__ == "__main__":
    unittest.main()
