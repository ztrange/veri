"""Baseline smoke test.

Keeps the suite green at baseline so `/solve-issue` can confirm a clean starting
point before writing its first failing test. veri will add the real test for the
seeded acceptance criterion alongside this one.
"""
import unittest


class SmokeTest(unittest.TestCase):
    def test_baseline_is_green(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
